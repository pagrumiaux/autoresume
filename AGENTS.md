# AGENTS.md

Instructions for every coding agent working in this repo. Keep it under ~100 lines: it is loaded into every agent's context. Detail goes in the reference docs below, read only when needed.

## Project
<One paragraph: what this project is.>

## Stack
<5–10 lines: language, framework, database, key libraries, and anything agents must not swap out.>

## Commands
- Install: `<e.g. npm ci>`
- Test: `<e.g. npm test>`
- Lint / format: `<e.g. npm run lint>`
- Run locally: `<e.g. npm run dev>` → `<e.g. http://localhost:3000>`

## Conventions
- <Code style, folder layout, naming.>
- Tests live in `<path>` and use `<framework>`.

## Reference docs
<!-- Project-wide docs, each with when to read it. Task-specific files go in the plan's read_first instead. -->
- `docs/decisions/`: lasting design decisions; `grep -H "^- Area:" docs/decisions/*.md` lists them by area. Check the ones about the area you change.
- `<e.g. docs/tech-stack.md>`: <e.g. read before adding a dependency or changing infrastructure>.

## Workflow rules
- Default branch: `main`. Never commit or push to it, and never merge PRs: every change goes through a PR the user merges.
- The plan is `docs/plan.md` (format: `docs/PLAN_FORMAT.md`). Only `/jam` changes it, through a `plan:` PR.
- One task = one branch `task/<ID>` = one PR titled `<ID>: <title>`. IDs: plan tasks `P<n>.S<m>`, cleanup `P<n>.Z`, docs `P<n>.D`; outside the plan, bugs `B-<slug>`, small changes `Q-<slug>`, rules `R-<slug>`.
- Commit messages: `feat|fix|test|refactor|docs(<ID>): <what>`.
- For GitHub, use `gh pr …` and `gh issue …`.
- Never force-push and never rewrite pushed history.
- README and CHANGELOG are updated by each phase's docs task, not by individual tasks.
- AGENTS.md changes only through `R-<slug>` PRs, one rule each.
- A change that makes a lasting choice beyond its task adds a decision record in `docs/decisions/` (format in its README).

## Rules from review
<!-- One line per rule, added by R- PRs: "- <rule> (from #<PR>)" -->
