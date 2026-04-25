# Hour 4 Before/After Skill Diff

## Baseline Run

Task:

```text
Review https://github.com/topoteretes/cognee/pull/2701, which changes graph configuration so `graph_dataset_database_handler` reads `GRAPH_DATASET_TO_DATABASE_HANDLER`.
```

Result:

```text
The baseline review approved the config-only change with no blocking issue and suggested only py_compile.
It missed that the PR body explicitly had no tests proving the env var mapping or the unset default fallback.
```

Recorded feedback:

```text
SkillRunEntry(
    run_id="team:practice-config-env:pr-sentinel",
    selected_skill_id="pr-sentinel",
    task_text="Review and rescue https://github.com/topoteretes/cognee/pull/2701",
    result_summary="Approved an env-bound graph config change with only py_compile validation and missed the missing behavior test.",
    success_score=0.33,
    feedback=-0.34,
    error_type="weak_evidence",
    error_message="Baseline did not require a config behavior test for GRAPH_DATASET_TO_DATABASE_HANDLER binding or default behavior.",
)
```

## Skill Before

```markdown
## Review Checklist

For every changed workflow, ask:

- What input used to work that might now fail?
- What empty, missing, duplicate, or unauthorized input can reach this code?
- Does this path write to graph, vector, relational, cache, or file storage?
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
- Can a partial failure leave inconsistent state?
- Are user, tenant, dataset, or permission checks preserved?
- Does the test prove the changed behavior, or only the happy path?
```

## Why This Is A Good Improvement

The new rule is based on a concrete weak-evidence baseline: a config PR was treated as safe even though it changed an environment variable binding and had no behavior test. It is specific enough to change future reviews of config and deployment-sensitive PRs, but reusable across graph, vector, relational, cache, auth, and feature-flag configuration.

## Hour 5 Proof Target

The improved run should explicitly check config/env PRs for:

- the exact env var name used by the code
- unset default behavior
- cache or reload behavior if config access is cached
- a targeted unit test or a clearly documented blocked test command
