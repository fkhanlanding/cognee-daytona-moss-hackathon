# Team Submission

## Team

- Team name: PR Sentinel
- Participants: Not specified
- Skill name: PR Sentinel (`pr-sentinel`)

## Skill

- Skill path: `skills/pr-sentinel`
- Final `SKILL.md` summary: PR Sentinel is a staff-engineer PR rescue skill focused on changed workflows, correctness regressions, permission boundaries, unsafe writes, missing tests, and minimal fixes. It uses a five-role flow: Scout, Fixer, Critic, Editor, and Verifier.
- Frozen final-round skill SHA-256: `e8224dee9b9942a50461aa311c9632b35456bef9666be73f16697b23ca6f0b97`

## Runs

### Baseline Run

- Task or PR: `https://github.com/topoteretes/cognee/pull/2701`
- Score: `38 / 100`
- Main failure mode: `weak_evidence`
- `SkillRunEntry.run_id`: `team:practice-config-env:pr-sentinel`
- Log path or link: `evidence/runs/hour-4-pr-2701-baseline.md`

### Improved Run

- Task or PR: `https://github.com/topoteretes/cognee/pull/2712`
- Score: `82 / 100`
- Improvement over baseline: `+44`
- `SkillRunEntry.run_id`: `team:practice-vector-filter:pr-sentinel`
- Log path or link: `evidence/runs/hour-5-pr-2712-improved.md`

### Final Hidden Round

- Task or PR: Not provided
- Score: `42 / 100` local blocked-run score
- Main blocker: final hidden PR URL, refs, patch file, or checkout instructions were unavailable
- `SkillRunEntry.run_id`: `team:final-hidden:pr-sentinel`
- Log path or link: `evidence/runs/final-hidden-pr.md`

## Feedback Loop

What feedback did Cognee record?

```text
error_type: weak_evidence
error_message: Baseline did not require a config behavior test for GRAPH_DATASET_TO_DATABASE_HANDLER binding or default behavior.
feedback: -0.34
success_score: 0.33
```

Cognee write evidence was not observed for the local fallback baseline, so these `SkillRunEntry` fields are recorded locally in `evidence/runs/hour-4-pr-2701-baseline.scorecard.json`.

What changed in the skill because of that feedback?

```text
Before:
- Does this path write to graph, vector, relational, cache, or file storage?
- Can a partial failure leave inconsistent state?

After:
- Does this path write to graph, vector, relational, cache, or file storage?
- If this changes environment-bound configuration, does a test prove the exact env var name and default fallback behavior?
- Can a partial failure leave inconsistent state?
```

Skill diff: `evidence/skill-diffs/hour-4-config-env-rule.md`

## PR Rescue Result

- Bug or regression found: In PR `2712`, PR Sentinel found that ChromaDB node-name filtering queried `belongs_to_set` while list metadata is serialized as `belongs_to_set__list`, so the mocked tests did not prove real filter behavior.
- Fix proposed or applied: Align ChromaDB metadata serialization with filter construction by adding or querying a searchable node-membership representation, then preserve restored payload compatibility.
- Tests run or specified: Local pytest was blocked because available Python environments lacked `pytest`; Docker static verification confirmed the key mismatch. The required test is an adapter behavior test that inserts ChromaDB data points through serialization and asserts `node_name` filters return the expected IDs.
- Remaining risk: Cognee `SkillRunEntry` writes, Moss failure-memory retrieval, and Daytona final workspace evidence are not claimed unless future logs prove them. The final hidden PR itself was unavailable.

## Agent Team

```text
Scout: maps changed files, touched workflows, risk tags, hunk headers, and likely tests.
Fixer: proposes the smallest patch and the targeted test that proves it.
Critic: scores the run against the 100-point rubric and labels the failure mode.
Editor: converts a scored practice failure into one reusable skill rule; final round records notes only.
Verifier: runs or specifies the narrowest meaningful verification and records platform blockers honestly.
```

## Reproduction

Commands needed to validate the retained final-submission evidence:

```bash
# Validate canonical scorecards
python3 -m json.tool evidence/runs/hour-4-pr-2701-baseline.scorecard.json >/dev/null
python3 -m json.tool evidence/runs/hour-5-pr-2712-improved.scorecard.json >/dev/null
python3 -m json.tool evidence/runs/final-hidden-pr.scorecard.json >/dev/null

# Validate the frozen final skill hash
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path

expected = "e8224dee9b9942a50461aa311c9632b35456bef9666be73f16697b23ca6f0b97"
actual = sha256(Path("skills/pr-sentinel/SKILL.md").read_bytes()).hexdigest()
assert actual == expected, actual
PY

# Validate retained artifacts in Docker
docker run --rm --platform linux/amd64 \
  -v "$PWD:/workspace" \
  -w /workspace \
  ghcr.io/topoteretes/cognee/cognee-skills-hackathon:144a128515cc \
  sh -lc 'python3 --version; sha256sum skills/pr-sentinel/SKILL.md; python3 -m json.tool evidence/runs/final-hidden-pr.scorecard.json >/dev/null'
```

Environment assumptions:

```text
DAYTONA_API_KEY
ANTHROPIC_API_KEY
LLM_API_KEY
MOSS_PROJECT_ID
MOSS_PROJECT_KEY
```

## Evidence Index

- Baseline log: `evidence/runs/hour-4-pr-2701-baseline.md`
- Baseline scorecard: `evidence/runs/hour-4-pr-2701-baseline.scorecard.json`
- Skill diff: `evidence/skill-diffs/hour-4-config-env-rule.md`
- Improved log: `evidence/runs/hour-5-pr-2712-improved.md`
- Improved scorecard: `evidence/runs/hour-5-pr-2712-improved.scorecard.json`
- Final hidden-round blocked log: `evidence/runs/final-hidden-pr.md`
- Final hidden-round scorecard: `evidence/runs/final-hidden-pr.scorecard.json`
- Agent roles: `evidence/agent-team.md`

## Remaining Risk

The baseline-to-improved loop is documented and reproducible from local evidence. The final hidden PR was not available in the repo or task context, so the submission does not claim a completed hidden final rescue, Cognee write, Moss retrieval, or Daytona workspace for that round.
