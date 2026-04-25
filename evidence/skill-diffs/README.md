# Skill Diff Evidence

Use this folder for before/after records that explain how PR Sentinel improved from a real run failure.

Do not add the first skill diff until the baseline run has been scored and the feedback is recorded. The improvement should be one concrete, reusable rule that would have prevented the observed failure.

## Recommended Format

````markdown
# Skill Diff: <failure-mode>

## Baseline Failure

Task / PR:

Result:

Main failure mode:

## Recorded Feedback

```text
SkillRunEntry(
    run_id="team:practice-1:pr-sentinel",
    selected_skill_id="pr-sentinel",
    task_text="...",
    result_summary="...",
    success_score=...,
    feedback=...,
    error_type="...",
    error_message="...",
)
```

## Skill Before

```markdown
<exact relevant snippet before the change>
```

## Skill After

```markdown
<exact relevant snippet after the change>
```

## Why This Rule Is Reusable

- Based on the real baseline failure.
- Specific enough to change future review behavior.
- General enough to apply to hidden PRs.
- Short enough to keep `SKILL.md` usable.

## Improved Run Result

Task / PR:

Result:

Score change:
````

## Notes

- Use [examples/before-after-skill-diff.md](../../examples/before-after-skill-diff.md) as the model.
- Do not hard-code practice PR file names, line numbers, or answers into `SKILL.md`.
- Redact secrets before pasting command output or logs.
