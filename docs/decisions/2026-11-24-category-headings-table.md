# Skill category headings come from a table in the render code
- Date: 2026-11-24
- Area: render, bank
- Status: accepted
- Source: /compose 2026-11-24, P0.S12

## Context
The template groups skills under one heading per `category` and reads the headings from an optional `category_titles` in its data (P0.S11, #19). A bank `category` is a plain id (`ml`, `mlops`), with no FR/EN label, so something has to turn ids into headings, or raw ids reach the page.

## Decision
`src/autoresume/render/headings.py` holds a FR/EN table from category id to heading. The render step fills `category_titles` from it for every category it passes to the template. A category missing from the table gets a tidied id ("soft-skills" gives "Soft skills") and a warning; the render never fails on it.

## Rejected options
- A `categories` list with FR/EN labels in the bank: cleaner, and no code change per new category, but a schema change in a co-designed area. Worth revisiting if categories change often.
- Stop the render on an unknown category: a new category in the bank would break the resume until the code catches up.

## Consequences
A new category in a bank needs a table entry to get a proper heading; until then the tidied id shows and a warning is logged. The table lives in public code, so it holds only generic category names.
