# Skills of category `soft` are never rendered on the resume
- Date: 2026-11-24
- Area: render, bank
- Status: accepted
- Source: P0.S11, user decision 2026-11-24

## Context
The bank holds soft skills (teamwork, mentoring, ...). They help select bullets by tag, but listing them on the page adds little for a recruiter or an ATS.

## Decision
The Typst template drops every skill whose `category` is `soft`. Such skills only serve as tags for bullet selection.

## Rejected options
- Render them in a separate "Soft skills" block: takes sidebar space on a one-page resume.

## Consequences
The filter is on the exact category name `soft`. The fake banks (`examples/bank`, `tests/fixtures/bank`) still name it `soft-skills`, so they are not filtered yet; they are renamed to `soft` in issue #20. Bank authors must use `soft` for skills that should stay off the page.
 P0.S12 should also drop `soft` skills when it builds the template data; the template filter is a second safety net.\n