# PR 2705 Skill Diff

## Practice Run

Task:

```text
Review https://github.com/topoteretes/cognee/pull/2705, which adds graphskills, agentic retrieval, skill ingestion, SkillRunEntry recording, and self-improvement flows.
```

Result:

```text
The review found that `improve=True` on a single SkillRunEntry can trigger a global pass over every skill in the node set, while inspection ids include wall-clock time. That makes repeated low-scoring runs create fresh inspections and amendments instead of converging on one bounded proposal.
```

Recorded feedback:

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

## Skill Before

```markdown
## Review Checklist

For every changed workflow, ask:

- What input used to work that might now fail?
- What empty, missing, duplicate, or unauthorized input can reach this code?
- Does this path write to graph, vector, relational, cache, or file storage?
- If this changes environment-bound configuration, does a test prove the exact env var name and default fallback behavior?
- Can a partial failure leave inconsistent state?
- Are user, tenant, dataset, or permission checks preserved?
- Does the test prove the changed behavior, or only the happy path?
```

## Skill After

```markdown
## Review Checklist

For every changed workflow, ask:

- What input used to work that might now fail?
- What empty, missing, duplicate, or unauthorized input can reach this code?
- Does this path write to graph, vector, relational, cache, or file storage?
- If this changes environment-bound configuration, does a test prove the exact env var name and default fallback behavior?
- If this starts automatic agent, retry, or self-improvement work, does a test prove the scope is bounded and repeated runs are idempotent?
- Can a partial failure leave inconsistent state?
- Are user, tenant, dataset, or permission checks preserved?
- Does the test prove the changed behavior, or only the happy path?
```

## Why This Is A Good Improvement

The new rule is tied to a concrete finding from PR 2705: the dangerous part was not only that tests were missing, but that a single run could trigger non-local, repeated side effects across the skill graph. The rule is reusable for agent loops, retry workers, auto-remediation, self-improving skills, and any background process that writes persistent state.

## Next Proof Target

Future reviews should explicitly check automatic loops for:

- the exact object or tenant scope they are allowed to mutate
- behavior when the same failure signal is processed twice
- deterministic or deduplicated identities for generated work
- integration tests that prove graph/vector state does not grow stale or duplicate unexpectedly
