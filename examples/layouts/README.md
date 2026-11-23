# Layout directions

Three one-page resume layouts with fake content, to pick a design before the real template. Each `.typ` is compiled to a `.pdf` of the same name (`uv run python -c "import typst; typst.compile('classic.typ', output='classic.pdf')"`). All use real text and no images, so they stay ATS-friendly.

- `classic`: single column, centered header, uppercase section titles with a full-width rule. The safest and most ATS-friendly reading order.
- `sidebar`: two columns, a narrow left sidebar (contact, skills, languages, education) and a main column (summary, experience). Accent color on titles; the text still reads column by column.
- `compact`: single column with a date gutter on the left and section titles inline with a thin rule. Smaller type, fits the most content.
