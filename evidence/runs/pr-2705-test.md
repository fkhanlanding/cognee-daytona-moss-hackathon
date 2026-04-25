# PR 2705 Test Run

## Run Identity

- Run ID: `team:practice-agentic-graphskills:pr-sentinel`
- Skill: `pr-sentinel`
- Task / PR URL: `https://github.com/topoteretes/cognee/pull/2705`
- Started at: `2026-04-25T23:39:00Z`
- Completed at: `2026-04-25T23:42:20Z`
- Runtime command: local isolated checkout plus PR Sentinel probe and targeted pytest
- Checkout: `/tmp/cognee-pr-2705`, fetched `pull/2705/head` into `pr-sentinel-pr-2705`
- Base ref: `origin/dev`

## Scout Risk Map

- Changed files: 55 files across `remember`, search API wiring, agentic retrieval, tool execution, skill ingestion, skill amendify, engine models, deploy scripts, and new skill ingest tests.
- Affected workflows: `cognee.remember("skills/")`, skill graph/vector upsert and stale cleanup, agentic search tool calls, `SkillRunEntry` recording, self-improvement inspect/preview/amendify, cloud client search/remember parity.
- Correctness risks: high because the PR introduces new runtime surfaces and side-effectful improvement loops with only mocked/smoke coverage for the hardest paths.
- Permission or tenant risks: moderate; agentic tool execution enforces `allowed_tools` and dataset authorization when `dataset_id` is set, but callers constructing tool execution without a dataset rely on handler-level behavior.
- Missing test risks: high for `enrich=True`, `improve=True`, real graph/vector consistency, and agentic retriever routing plus `SkillRun` recording.
- Probe artifacts: `evidence/runs/pr-2705-test.probe.md` and `evidence/runs/pr-2705-test.probe.json`

## Review Finding

Severity: medium

Location: `cognee/modules/memify/skill_inspect.py`, `cognee/modules/memify/skill_improvement.py`, `cognee/modules/tools/skill_runs.py`

Problem: `improve=True` on a single `SkillRunEntry` triggers a pass over every skill in the node set, and each inspection uses `time.time()` in the inspection identity. Repeated low-scoring runs can therefore create fresh inspections and amendments for the same failure pattern instead of converging on one active proposal. That makes the improvement path costly, non-local, and hard to reason about.

Evidence: `remember_skill_run_entry` passes only `entry.node_set` into `improve_failing_skills`; `improve_failing_skills` lists all skill names in that node set; `inspect_skill` computes `inspection_id` from `skill_id`, failure count, average score, and current wall-clock time. The PR's own smoke test comments say `improve=True` end-to-end is not covered because it requires LLM and a real DB.

Fix: scope the automatic improvement pass to `entry.selected_skill_id` by default, or add an explicit flag for global improvement. Make inspection/amendment identity deterministic from the analyzed run ids and improvement content, or upsert one active inspection per skill/failure fingerprint.

Tests: add a unit test for `remember_skill_run_entry(..., improve=True)` that asserts only the selected skill is inspected by default, plus an idempotency test that two inspections for the same analyzed run ids do not create two unrelated amendment proposals.

## Secondary Gaps

- `AgenticRetriever._run_tool_safely` catches scope, permission, and invocation errors, but not `ToolNotFoundError`, even though `execute_tool` documents that lookup can raise it. Add the missing catch or normalize lookup failures in `execute_tool`.
- Search factory tests pass when `pytest-asyncio` is installed, but the current PR does not add coverage for `SearchType.AGENTIC_COMPLETION` or the graph-completion upgrade path when `skills`, `tools`, or `skills_auto_retrieve` are supplied.
- Cloud `remember` returns through `client.remember(...)` before local skill-source dispatch, so remote `cognee.remember("skills/")` does not have parity with the local skill ingestion path unless the server implements the same contract.

## Verifier Evidence

- Probe command: `python3 skills/pr-sentinel/scripts/pr_rescue.py probe --repo "/tmp/cognee-pr-2705" --base-ref origin/dev --head-ref pr-sentinel-pr-2705 --md-out evidence/runs/pr-2705-test.probe.md --json-out evidence/runs/pr-2705-test.probe.json`
- Probe result: 55 changed files, risk tags for API, migration/model, storage, async, CLI, and tests.
- Test command: `uv run --with pytest pytest cognee/tests/unit/modules/tools/test_skill_ingest.py -q`
- Test output summary: 21 passed, 8 warnings.
- Test command: `uv run --with pytest --with pytest-asyncio pytest cognee/tests/unit/modules/search/test_get_search_type_retriever_instance.py -q`
- Test output summary: 17 passed, 8 warnings.
- Note: running the search factory target with only `pytest` skipped all 17 async tests; `pytest-asyncio` was required for a meaningful result.

## Critic Scorecard

- PR rescue quality: 31 / 40
- Self-improvement evidence: 15 / 25
- Review clarity: 18 / 20
- Reproducibility: 9 / 10
- Safety: 5 / 5
- Total: 78 / 100
- Primary error type: `missing_integration_test`
- Feedback: `0.56`
- Residual risk: the highest-risk LLM and graph/vector improvement paths still need real integration coverage.

### SkillRunEntry Fields

```text
SkillRunEntry(
    run_id="team:practice-agentic-graphskills:pr-sentinel",
    selected_skill_id="pr-sentinel",
    task_text="Review and rescue https://github.com/topoteretes/cognee/pull/2705",
    result_summary="Found that improve=True can trigger a global, non-idempotent skill improvement pass and identified missing end-to-end coverage for enrich/improve/agentic retrieval paths.",
    success_score=0.78,
    feedback=0.56,
    error_type="missing_integration_test",
    error_message="The PR has useful smoke coverage, but the side-effectful improve=True and agentic retrieval paths lack integration tests proving graph/vector consistency and scoped behavior.",
)
```

## Moss / Cognee / Daytona Notes

- Moss retrieval observed: no.
- Cognee `SkillRunEntry` write observed: no; fields recorded locally only.
- Daytona workspace observed: no.
- Cleanup evidence: local checkout remains in `/tmp/cognee-pr-2705` for inspection.

## Redaction Checklist

- [x] `DAYTONA_API_KEY` redacted if present
- [x] `ANTHROPIC_API_KEY` redacted if present
- [x] `LLM_API_KEY` redacted if present
- [x] `MOSS_PROJECT_ID` redacted if present
- [x] No raw `.env` content included
