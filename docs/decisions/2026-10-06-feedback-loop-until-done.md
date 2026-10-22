# Feedback loop until I say done, with approved lessons
- Date: 2026-10-06
- Area: feedback, agents
- Status: accepted
- Source: initial plan

## Context
Cover letters are generative and error-prone; resumes also need taste that only I can judge.

## Decision
Each application is a resumable revision loop: draft, critic check, my review. It ends only when
I say done. Every round is logged. At the end, the agent proposes up to three lessons; only
approved ones reach the lessons file read by future runs. The critic re-checks traceability on
every revision.

## Consequences
Feedback rounds per application becomes a metric. The lessons file needs periodic review to avoid
contradictions.
