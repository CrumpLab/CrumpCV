# CrumpCV

A CV as code: structured data in `data/`, rendered by Quarto to PDF (Typst), Word, HTML, the Brooklyn College personnel form, and a `cv.json` feed for the website.

## Current stage

Built through Milestone 6 of `PLAN.md`. Content is current to March 2024; Milestone 7 (2024 to 2026 refresh) needs items from the user. See `PLAN.md` for decisions and the roadmap, `styles/README.md` for the style gallery.

## Layout

- `data/*.yml`, `data/publications.bib`, `data/narratives/*.md`: the single source of truth. Never edit generated output by hand.
- `schema/*.json` and `scripts/validate.py`: what a valid entry looks like. Run `python3 scripts/validate.py` after any data change.
- `scripts/build.py` (+ `cvlib.py`, `build_bc.py`): pre-render step that writes `_generated/` (Markdown with raw Typst blocks per section, `meta.yml`, `cv.json`). Formatting rules for publications and talks (APA-like, bold owner name, mentee stars, refereed marker) live here.
- `cv.qmd`: the academic CV. `cv-bc.qmd`: the Brooklyn College form (Word). Both are just headings plus includes of generated sections.
- `_extensions/cv-classic|cv-modern|cv-awesome`: Typst styles sharing one function API. Default style is set in `_quarto.yml`. `scripts/render_styles.py` renders all three and writes `styles/previews/`.
- `templates/reference*.docx`: Word styles, produced by `scripts/make_reference_docx.py [bc]`.
- `cv-config.yml`: content options (refereed marker, mentee stars, numbering, `recent_since` for the form).
- `scripts/harvest/`: the one-off parsers that seeded the data from `CV Examples/`; keep for reference.
- `.github/workflows/render.yml`: validates, renders everything, publishes `_output/` to `gh-pages`.

## Rendering

```
python3 scripts/validate.py       # data checks
quarto render                     # cv.pdf (default style), cv.docx, cv.html, cv-bc.docx, cv.json -> _output/
python3 scripts/render_styles.py  # cv-classic.pdf, cv-modern.pdf, cv-awesome.pdf + previews
```

Needs Quarto 1.6+ (bundles Pandoc and Typst) and Python 3 with `pyyaml`, `jsonschema`, and `pymupdf` for previews. No R, LaTeX, or Jupyter. In a session without Quarto, edit and validate data; CI renders on push.

## Conventions

- When the user describes a new CV item in chat, use the `add-entry` skill: add it to the right data file in the existing shape, newest first, validate, render if possible, and commit with `Add <type>: <title>`.
- Ask before removing or rewording existing entries.
- Publications: BibTeX with a `keywords` category; owner written as `Crump, M. J. C.`; sentence-case titles with proper nouns in braces; no manual mentee stars (they come from `students.yml`).
- Dates: `start`/`end` as year or `YYYY-MM` for sorting; `when` for verbatim text; `end: null` for ongoing.
- This repo is public. Do not commit private information such as home addresses or personal phone numbers, or anything the user has not approved for a public CV. The office phone is left out of `data/profile.yml` unless the user approves it.
- Do not commit `_output/`, `_generated/`, or `cv.typ`; they are build products.
