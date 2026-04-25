# Evidence Artifacts

This folder stores the judge-visible evidence for the PR Sentinel improvement loop.

## Layout

- `runs/*.md`: human-readable run logs for baseline, improved, and final PR reviews.
- `runs/*.scorecard.json`: structured scorecards with `SkillRunEntry`-compatible fields and rubric scores.
- `skill-diffs/*`: before/after skill improvement records tied to concrete run feedback.

## Evidence Rules

- Do not claim Cognee stored feedback unless the run log includes evidence from the demo output.
- Do not claim Moss retrieval influenced a run unless the retrieved memory IDs or summaries are recorded.
- Do not claim Daytona verification passed unless the workspace, command, output, and cleanup result are recorded.
- Use `null` for unknown numeric or boolean scorecard values until the run actually happens.
- Keep skill improvements tied to a real failure. Avoid generic rules like "review more carefully."

## Secret Redaction

Before saving or submitting logs, redact these values if they appear:

- `DAYTONA_API_KEY`
- `ANTHROPIC_API_KEY`
- `LLM_API_KEY`
- `MOSS_PROJECT_ID`
- `MOSS_PROJECT_KEY`
