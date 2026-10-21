# 0002: YAML content rendered with Typst

Date: 2026-10-06 · Status: accepted

## Context
The old resume lived in Canva: not diffable, not scriptable, hard to fit on one page.

## Decision
Content as YAML validated by Pydantic; layout as a Typst template compiled through the Typst
Python package. A new design is made from scratch.

## Alternatives considered
- LaTeX: mature, but slow compiles and painful templating from data.
- HTML to PDF: flexible, but page-count control is less predictable.

## Consequences
Rendering and page counting become tools an agent can call in a loop.
