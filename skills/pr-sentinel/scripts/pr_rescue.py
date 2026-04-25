#!/usr/bin/env python3
"""Deterministic PR rescue helpers for the PR Sentinel skill.

This script is intentionally stdlib-only. It gives the agent compact facts
about a checkout so LLM tokens are spent on judgment instead of mechanical
diff and test discovery.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


RISK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("auth", re.compile(r"(auth|login|logout|token|jwt|oauth|session)", re.I)),
    ("permission", re.compile(r"(permission|role|tenant|owner|access|acl|policy)", re.I)),
    ("storage", re.compile(r"(graph|vector|database|db|sql|postgres|kuzu|neo4j|cache|redis|file|s3|storage)", re.I)),
    ("api", re.compile(r"(api|route|router|endpoint|request|response|schema|serializer)", re.I)),
    ("cli", re.compile(r"(cli|command|argparse|click|flag|option)", re.I)),
    ("migration", re.compile(r"(migration|alembic|schema|model|table|column|index)", re.I)),
    ("config", re.compile(r"(config|settings|env|default|feature|toggle)", re.I)),
    ("destructive", re.compile(r"(delete|remove|drop|truncate|purge|reset|overwrite)", re.I)),
    ("async", re.compile(r"(async|await|queue|worker|task|concurrent|parallel)", re.I)),
]

TEST_PATH_RE = re.compile(r"(^|/)(tests?|specs?)(/|$)|(_test|test_|\.spec\.|\.test\.)", re.I)
SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".rb"}
TEXT_EXTENSIONS = SOURCE_EXTENSIONS | {".md", ".yaml", ".yml", ".toml", ".json", ".ini", ".cfg", ".txt"}


@dataclass
class ChangedFile:
    path: str
    status: str
    extension: str
    risk_tags: list[str] = field(default_factory=list)
    is_test: bool = False
    symbols: list[str] = field(default_factory=list)
    added_lines: int = 0
    removed_lines: int = 0
    hunk_headers: list[str] = field(default_factory=list)


@dataclass
class ProbeReport:
    repo: str
    base_ref: str
    head_ref: str
    merge_base: str
    changed_files: list[ChangedFile]
    risk_summary: dict[str, list[str]]
    test_candidates: list[str]
    suggested_commands: list[str]
    notes: list[str]


def run_git(repo: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = ["git", "-C", str(repo), *args]
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def git_stdout(repo: Path, args: list[str]) -> str:
    result = run_git(repo, args)
    return result.stdout.strip() if result.returncode == 0 else ""


def resolve_ref(repo: Path, ref: str) -> str:
    if ref:
        return ref
    for candidate in ("origin/main", "origin/master", "main", "master"):
        if run_git(repo, ["rev-parse", "--verify", candidate]).returncode == 0:
            return candidate
    return "HEAD~1"


def merge_base(repo: Path, base_ref: str, head_ref: str) -> str:
    base = git_stdout(repo, ["merge-base", base_ref, head_ref])
    return base or base_ref


def parse_name_status(text: str) -> list[tuple[str, str]]:
    files: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        path = parts[-1]
        files.append((status, path))
    return files


def diff_range(base: str, head: str) -> list[str]:
    return [base] if head == "WORKTREE" else [base, head]


def classify_path(path: str) -> list[str]:
    haystack = path.replace("\\", "/")
    tags = [name for name, pattern in RISK_PATTERNS if pattern.search(haystack)]
    if TEST_PATH_RE.search(haystack):
        tags.append("test")
    return sorted(set(tags))


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def extract_python_symbols(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    symbols: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(node.name)
    return symbols[:40]


def extract_regex_symbols(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    patterns = [
        r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=",
        r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
    ]
    found: list[str] = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text))
    return list(dict.fromkeys(found))[:40]


def extract_symbols(repo: Path, rel_path: str) -> list[str]:
    path = repo / rel_path
    if not path.exists() or not is_text_file(path):
        return []
    if path.suffix.lower() == ".py":
        return extract_python_symbols(path)
    return extract_regex_symbols(path)


def parse_numstat(repo: Path, base: str, head: str) -> dict[str, tuple[int, int]]:
    out = git_stdout(repo, ["diff", "--numstat", *diff_range(base, head)])
    stats: dict[str, tuple[int, int]] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added = int(parts[0]) if parts[0].isdigit() else 0
        removed = int(parts[1]) if parts[1].isdigit() else 0
        stats[parts[-1]] = (added, removed)
    return stats


def parse_hunk_headers(repo: Path, base: str, head: str, rel_path: str, limit: int) -> list[str]:
    out = git_stdout(repo, ["diff", "--unified=0", *diff_range(base, head), "--", rel_path])
    headers = [line for line in out.splitlines() if line.startswith("@@ ")]
    return headers[:limit]


def changed_files(repo: Path, base: str, head: str, max_hunks: int) -> list[ChangedFile]:
    raw = git_stdout(repo, ["diff", "--name-status", *diff_range(base, head)])
    stats = parse_numstat(repo, base, head)
    files: list[ChangedFile] = []
    for status, path in parse_name_status(raw):
        added, removed = stats.get(path, (0, 0))
        files.append(
            ChangedFile(
                path=path,
                status=status,
                extension=Path(path).suffix.lower(),
                risk_tags=classify_path(path),
                is_test=bool(TEST_PATH_RE.search(path.replace("\\", "/"))),
                symbols=extract_symbols(repo, path),
                added_lines=added,
                removed_lines=removed,
                hunk_headers=parse_hunk_headers(repo, base, head, path, max_hunks),
            )
        )
    return files


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except Exception:
        return 0


def untracked_files(repo: Path) -> list[str]:
    out = git_stdout(repo, ["ls-files", "--others", "--exclude-standard"])
    return [line for line in out.splitlines() if line.strip()]


def append_untracked(repo: Path, files: list[ChangedFile]) -> list[ChangedFile]:
    seen = {item.path for item in files}
    for path in untracked_files(repo):
        if path in seen:
            continue
        full_path = repo / path
        files.append(
            ChangedFile(
                path=path,
                status="??",
                extension=Path(path).suffix.lower(),
                risk_tags=classify_path(path),
                is_test=bool(TEST_PATH_RE.search(path.replace("\\", "/"))),
                symbols=extract_symbols(repo, path),
                added_lines=line_count(full_path),
                removed_lines=0,
                hunk_headers=[],
            )
        )
    return files


def git_files(repo: Path) -> list[str]:
    out = git_stdout(repo, ["ls-files"])
    return [line for line in out.splitlines() if line.strip()]


def test_candidates_for(changed: Iterable[ChangedFile], files: list[str], limit: int) -> list[str]:
    tests = [f for f in files if TEST_PATH_RE.search(f.replace("\\", "/"))]
    selected: list[str] = []
    for item in changed:
        stem = Path(item.path).stem
        parent_parts = Path(item.path).parts[:-1]
        parent_key = "/".join(parent_parts[-2:]) if parent_parts else ""
        patterns = [
            re.compile(rf"(^|/)(test_)?{re.escape(stem)}(_test)?\.", re.I),
            re.compile(re.escape(stem), re.I),
            re.compile(re.escape(parent_key), re.I) if parent_key else None,
        ]
        for test in tests:
            if test in selected:
                continue
            if any(pattern and pattern.search(test) for pattern in patterns):
                selected.append(test)
                if len(selected) >= limit:
                    return selected
    if len(selected) < limit:
        for test in tests:
            if test not in selected:
                selected.append(test)
                if len(selected) >= limit:
                    break
    return selected


def risk_summary(changed: Iterable[ChangedFile]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for item in changed:
        for tag in item.risk_tags:
            summary.setdefault(tag, []).append(item.path)
    return {tag: paths for tag, paths in sorted(summary.items())}


def suggested_commands(repo: Path, candidates: list[str]) -> list[str]:
    commands: list[str] = []
    if candidates:
        py_tests = [p for p in candidates if p.endswith(".py")]
        if py_tests:
            commands.append("python -m pytest " + " ".join(py_tests[:5]))
    if (repo / "pyproject.toml").exists() and not commands:
        commands.append("python -m pytest")
    if (repo / "package.json").exists():
        commands.append("npm test")
    if (repo / "go.mod").exists():
        commands.append("go test ./...")
    if (repo / "Cargo.toml").exists():
        commands.append("cargo test")
    return commands[:6]


def build_report(args: argparse.Namespace) -> ProbeReport:
    repo = Path(args.repo).resolve()
    base_ref = resolve_ref(repo, args.base_ref)
    head_ref = "WORKTREE" if args.worktree else args.head_ref or "HEAD"
    merge_head = "HEAD" if args.worktree else head_ref
    base = merge_base(repo, base_ref, merge_head) if args.use_merge_base else base_ref
    changed = changed_files(repo, base, head_ref, args.max_hunks)
    if args.worktree and args.include_untracked:
        changed = append_untracked(repo, changed)
    all_files = git_files(repo)
    candidates = test_candidates_for(changed, all_files, args.max_tests)
    notes: list[str] = []
    if not changed:
        notes.append("No changed files found for the selected refs.")
    if not candidates:
        notes.append("No likely test files were found by path heuristics.")
    return ProbeReport(
        repo=str(repo),
        base_ref=base_ref,
        head_ref=head_ref,
        merge_base=base,
        changed_files=changed,
        risk_summary=risk_summary(changed),
        test_candidates=candidates,
        suggested_commands=suggested_commands(repo, candidates),
        notes=notes,
    )


def report_to_json(report: ProbeReport) -> str:
    return json.dumps(asdict(report), indent=2, sort_keys=True)


def compact_list(items: list[str], limit: int) -> str:
    if not items:
        return "-"
    visible = items[:limit]
    suffix = f" (+{len(items) - limit} more)" if len(items) > limit else ""
    return ", ".join(visible) + suffix


def report_to_markdown(report: ProbeReport, max_files: int, max_symbols: int) -> str:
    lines: list[str] = [
        "# PR Rescue Probe",
        "",
        f"- Repo: `{report.repo}`",
        f"- Base ref: `{report.base_ref}`",
        f"- Head ref: `{report.head_ref}`",
        f"- Diff base: `{report.merge_base}`",
        f"- Changed files: `{len(report.changed_files)}`",
        "",
        "## Changed Files",
        "",
        "| Status | File | Risk | Lines | Symbols |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report.changed_files[:max_files]:
        lines.append(
            f"| {item.status} | `{item.path}` | {compact_list(item.risk_tags, 8)} | "
            f"+{item.added_lines}/-{item.removed_lines} | {compact_list(item.symbols, max_symbols)} |"
        )
    if len(report.changed_files) > max_files:
        lines.append(f"| ... | {len(report.changed_files) - max_files} more files omitted | | | |")

    lines.extend(["", "## Risk Summary", ""])
    if report.risk_summary:
        for tag, paths in report.risk_summary.items():
            lines.append(f"- `{tag}`: {compact_list(paths, 8)}")
    else:
        lines.append("- No risk tags matched.")

    lines.extend(["", "## Hunk Headers", ""])
    for item in report.changed_files[:max_files]:
        if item.hunk_headers:
            lines.append(f"- `{item.path}`")
            for header in item.hunk_headers:
                lines.append(f"  - `{header}`")

    lines.extend(["", "## Likely Tests", ""])
    if report.test_candidates:
        lines.extend(f"- `{path}`" for path in report.test_candidates)
    else:
        lines.append("- No likely tests found.")

    lines.extend(["", "## Suggested Commands", ""])
    if report.suggested_commands:
        lines.extend(f"- `{cmd}`" for cmd in report.suggested_commands)
    else:
        lines.append("- No command inferred.")

    if report.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in report.notes)

    return "\n".join(lines) + "\n"


def write_outputs(args: argparse.Namespace, report: ProbeReport) -> None:
    if args.json_out:
        Path(args.json_out).write_text(report_to_json(report) + "\n", encoding="utf-8")
    if args.md_out:
        Path(args.md_out).write_text(
            report_to_markdown(report, args.max_files, args.max_symbols),
            encoding="utf-8",
        )


def score_output(text: str) -> dict[str, object]:
    lower = text.lower()
    checks = {
        "severity": bool(re.search(r"\b(critical|high|medium|low)\b", lower)),
        "file_reference": bool(re.search(r"\b[\w./-]+\.(py|ts|tsx|js|jsx|md|yaml|yml)(:\d+)?\b", text)),
        "test": "test" in lower or "pytest" in lower,
        "fix": "fix" in lower or "recommend" in lower or "change" in lower or "patch" in lower,
        "impact": "impact" in lower or "because" in lower or "risk" in lower or "breaks" in lower,
        "evidence": "evidence" in lower or "reproduce" in lower or "confirmed" in lower,
    }
    score = round(sum(1 for ok in checks.values() if ok) / len(checks), 2)
    error_type = "" if score >= 0.67 else "weak_evidence"
    return {
        "score": score,
        "feedback": max(-1.0, min(1.0, round((score - 0.5) * 2, 2))),
        "error_type": error_type,
        "error_message": "" if not error_type else "Output lacks enough severity, file, test, fix, impact, and evidence signal.",
        "checks": checks,
    }


def add_probe_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=os.getcwd(), help="Repository checkout to inspect.")
    parser.add_argument(
        "--base-ref",
        default="",
        help="Base git ref. Defaults to origin/main, origin/master, main, master, then HEAD~1.",
    )
    parser.add_argument("--head-ref", default="HEAD", help="Head git ref. Defaults to HEAD.")
    parser.add_argument("--worktree", action="store_true", help="Diff the merge base against the current working tree.")
    parser.add_argument(
        "--no-untracked",
        dest="include_untracked",
        action="store_false",
        help="In --worktree mode, do not include untracked files.",
    )
    parser.add_argument("--no-merge-base", dest="use_merge_base", action="store_false", help="Diff directly against --base-ref.")
    parser.add_argument("--max-files", type=int, default=30, help="Maximum changed files to include in markdown output.")
    parser.add_argument("--max-hunks", type=int, default=8, help="Maximum hunk headers per changed file.")
    parser.add_argument("--max-symbols", type=int, default=8, help="Maximum symbols per file in markdown output.")
    parser.add_argument("--max-tests", type=int, default=12, help="Maximum likely test files to report.")
    parser.add_argument("--json-out", default="", help="Write full JSON report to this path.")
    parser.add_argument("--md-out", default="", help="Write compact markdown report to this path.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PR Sentinel deterministic helper commands.")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="Generate a full compact PR rescue report.")
    add_probe_args(probe)

    changed = sub.add_parser("changed", help="Print changed file records as JSON.")
    add_probe_args(changed)

    risks = sub.add_parser("risks", help="Print risk summary as JSON.")
    add_probe_args(risks)

    tests = sub.add_parser("tests", help="Print likely test candidates as JSON.")
    add_probe_args(tests)

    score = sub.add_parser("score-output", help="Score a review output for structure and evidence.")
    score.add_argument("--input", required=True, help="Path to review output text.")
    score.add_argument("--json-out", default="", help="Optional path for JSON score output.")

    args = parser.parse_args(argv)

    if args.command in {"probe", "changed", "risks", "tests"}:
        report = build_report(args)
        write_outputs(args, report)
        if args.command == "probe":
            print(report_to_markdown(report, args.max_files, args.max_symbols), end="")
        elif args.command == "changed":
            print(json.dumps([asdict(item) for item in report.changed_files], indent=2))
        elif args.command == "risks":
            print(json.dumps(report.risk_summary, indent=2, sort_keys=True))
        elif args.command == "tests":
            print(json.dumps(report.test_candidates, indent=2))
        return 0

    if args.command == "score-output":
        text = Path(args.input).read_text(encoding="utf-8", errors="replace")
        result = score_output(text)
        output = json.dumps(result, indent=2, sort_keys=True)
        if args.json_out:
            Path(args.json_out).write_text(output + "\n", encoding="utf-8")
        print(output)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
