# CrumpCV

A CV as code. The content lives in structured data files and Quarto renders it to:

- **PDF** in a choice of Typst styles (`cv.pdf`, plus `cv-classic.pdf`, `cv-modern.pdf`, `cv-awesome.pdf`)
- **Word** (`cv.docx`) for institutions that want an editable file
- **HTML** (`cv.html`)
- **The Brooklyn College personnel form** (`cv-bc.docx`), sections I to VIII, filled from the same data
- **JSON** (`cv.json`) with every section, for the personal website

New entries are added by describing them in chat (the `add-entry` skill) or by editing a YAML file. Every push to `main` re-renders everything and publishes it.

## Outputs

After the first successful Action run on `main`, the current files are at:

- https://crumplab.github.io/CrumpCV/ (index)
- https://crumplab.github.io/CrumpCV/cv.pdf
- https://crumplab.github.io/CrumpCV/cv.docx
- https://crumplab.github.io/CrumpCV/cv-bc.docx
- https://crumplab.github.io/CrumpCV/cv.json

(Enable GitHub Pages for the `gh-pages` branch once in the repository settings.) Each Action run also attaches the outputs as an artifact.

## Layout

```
data/            the source of truth: one YAML file per section, publications.bib, narratives/
schema/          JSON Schema per section
scripts/         validate.py, build.py (data -> generated sections + cv.json), render_styles.py, make_reference_docx.py
cv.qmd           the academic CV (headings + includes)
cv-bc.qmd        the Brooklyn College form (Word)
cv-config.yml    content options: refereed marker, mentee stars, numbering, form cutoff year
_extensions/     Typst styles: cv-classic (default), cv-modern, cv-awesome
templates/       Word reference documents
styles/          style gallery with previews
CV Examples/     the 2024 CV documents and earlier vitae projects the data was harvested from
PLAN.md          decisions, milestones, what is left
```

## Rendering locally

Requirements: [Quarto](https://quarto.org) 1.6 or later (it bundles Pandoc and Typst) and Python 3 with `pyyaml`, `jsonschema`, and optionally `pymupdf` for previews. No R, LaTeX, or Jupyter.

On a Mac, `pip` may not exist on its own; `python3 -m pip` always works. If it refuses with "externally-managed-environment" (Homebrew Python), use a virtual environment and activate it in every terminal where you run `quarto render`, because Quarto calls `python3` for the pre-render step:

```
python3 -m venv .venv && source .venv/bin/activate   # optional, see above
python3 -m pip install pyyaml jsonschema pymupdf
python3 scripts/validate.py       # check the data
quarto render                     # -> _output/: cv.pdf, cv.docx, cv.html, cv-bc.docx, cv.json
python3 scripts/render_styles.py  # -> _output/cv-<style>.pdf and styles/previews/
```

## Updating the CV

1. Edit the right file in `data/` (newest first) or describe the item in a Claude session.
2. `python3 scripts/validate.py`
3. Commit and push. CI renders and publishes.

Publications live in `data/publications.bib`. Each entry carries `keywords = {category}` (article, chapter, proceedings, book, oer, commentary, book-review, preprint, ...). Mentee co-authors are starred automatically from `data/students.yml`, and the owner's name is bolded, so the bib needs no markup.

## Styles

See `styles/README.md` for previews and how to switch the default.
