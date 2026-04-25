# Hour 3 Agent Team Evidence

This artifact defines the intended five-role PR Sentinel evidence team for the judge-visible improvement loop. It is a readiness artifact, not proof that the live team has executed.

Current live role evidence is not observed until the Dockerized Hour 2 run succeeds. The recorded baseline failed at Daytona shared volume setup with `401 Unauthorized` before repository checkout, Moss retrieval, Cognee `SkillRunEntry` write, Daytona workspace creation, or any PR review agent ran.

## Role Model

| Role | Platform Ownership | Evidence Output |
|---|---|---|
| Scout | Reads the PR diff, changed files, affected workflows, and likely risk zones. | Compact risk map covering correctness, permissions, destructive/write paths, and missing tests. |
| Fixer | Proposes the smallest practical patch and the targeted test that would prove it. | Patch summary, files expected to change, test proposal, and any implementation blockers. |
| Critic | Scores the result against the challenge rubric and labels the primary failure mode. | Scorecard, `SkillRunEntry` fields, error type, feedback, and residual risk. |
| Editor | Converts a real scored failure into one reusable skill rule or records that no skill edit is justified. | Skill diff note, no-skill-edit rationale, and link to the failure that motivated the rule. |
| Verifier | Runs or specifies the narrowest meaningful verification command and records cleanup evidence. | Command output, blocked command reason, targeted test plan, Daytona workspace notes, and cleanup status. |

## Platform Notes

- Cognee is the intended storage layer for scored `SkillRunEntry` feedback, but no Cognee write is currently observed.
- Moss is the intended retrieval layer for prior failure memory, but no retrieved or stored Moss memory IDs are currently observed.
- Daytona is the intended isolated verification workspace, but the baseline attempt did not create a workspace because credentials failed during shared volume setup.
- Docker is the required runtime path for the next Hour 2 rerun; future role evidence should cite Docker output before making platform claims.

## Final-Round Freeze Behavior

Before the final hidden round, `skills/pr-sentinel/SKILL.md` should be treated as frozen. The team may use the improved skill as-is, collect evidence, score the run, and record outcomes, but should not manually edit the skill during the hidden evaluation. Any later skill edit must be tied to a completed, scored run outside the frozen final-round window.
