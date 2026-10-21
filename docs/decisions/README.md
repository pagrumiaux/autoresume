# Decision records

One short file per lasting decision: a library, a data format, an architecture choice, a pattern others should reuse. Not for choices that only matter inside one PR (those go in the PR's "Decisions" section).

- File name: `YYYY-MM-DD-<slug>.md`. Dates instead of numbers, so parallel PRs never pick the same name.
- Written by `/jam` (with plan changes) and by task-runners (when a PR makes a choice beyond its task).
- `Area:` is the category. `grep -H "^- Area:" docs/decisions/*.md` gives a one-line index of all records; agents use it to find the ones about the code they change, and read only those.
- To change a decision, add a new record that supersedes the old one, and set the old one's status to `superseded by <file>`.

## Format (keep it under ~20 lines)

```markdown
# <Decision, as a short statement>
- Date: YYYY-MM-DD
- Area: <comma-separated areas, e.g. storage, api>
- Status: accepted | superseded by <file>
- Source: <PR #n, /jam, task ID>

## Context
<What problem forced a choice.>

## Decision
<What we do, in one or two sentences.>

## Rejected options
- <Option>: <why not>

## Consequences
<What this makes easier or harder; what future work must respect.>
```
