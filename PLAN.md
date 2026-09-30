# PLAN.md — CrumpCV

A CV as code. Structured data in `data/`, rendered by Quarto to PDF (Typst), Word, HTML, and a `cv.json` feed for the website. Updated by describing new items in chat.

Written 2026-09-30 after reviewing `IDEA.md` and the three `vitae` projects in `CV Examples/`.

## Goal

One source of truth for the CV that:

1. renders to PDF, Word, and HTML in a style chosen from a few side-by-side variants,
2. exports a single `cv.json` containing every section (profile, positions, education, grants, publications, talks, teaching, students, service) for the website,
3. can be updated by a one-line description in chat, with validation and automatic re-rendering so nothing drifts.

## What the examples tell us

`CV Examples/rvitae/` holds three R `vitae` projects (`awesome`, `modern`, `Untitled`) that share identical content and differ only in the output style:

| Folder | vitae output | Look | Build state |
|---|---|---|---|
| `awesome/` | `vitae::awesomecv` | Awesome-CV: Roboto, coloured accent, bold section rules, bundled fonts | Failed (fontspec, TeX Live 2019) |
| `modern/` | `vitae::moderncv` | moderncv "casual": blue accent `#3873B3`, dates in a left column | Built, 7 pages |
| `Untitled/` | `vitae::hyndman` | Plain, compact, serif; the classic academic CV | Built, 7 pages |

Content in the `.Rmd` files is a **2019 snapshot** of the whole CV, already semi-structured:

- Positions and education as `tribble()` data frames rendered by `detailed_entries()`.
- Funding (4 grants), invited talks (13), conference presentations (37), mentorship (postdocs, doctoral, master's, undergraduate, dissertation committees), teaching (undergrad, master's, doctoral courses), and service (college, department, doctoral program, professional, reviewing) as Markdown lists.
- Publications from `Crump_pr.bib` (39 entries, 2006–2019, 37 articles + 2 chapters), sorted by descending date. `Crump.bib` is the same list with Zotero `url`/`urldate` fields still present. `works2.bib` (40 entries, 2006–2019, includes 3 books and 1 misc) looks like an ORCID export with different keys and messier journal names. `curie.bib` is the vitae sample file and can be ignored.
- Header data: name, title, affiliation, office phone, email, website, Twitter, GitHub.

Takeaways that shape the plan:

- The `tribble` + `detailed_entries` pattern is exactly the data-to-layout split we want. We keep the idea, move the data out of the document into YAML, and swap LaTeX for Typst.
- The three styles map directly onto the three style variants to build.
- The 2019 snapshot is the seed for `data/`. Everything from 2019 to 2026 still has to be added (see Milestone 6 and the open questions).
- The bib needs cleaning on import: drop `file`, `abstract`, `urldate`, keep `doi`. The office phone should not go into the public repo unless approved.
- LaTeX font trouble is why the awesome build failed. Typst avoids the TeX toolchain entirely.

## Decisions on the open questions

| Question | Decision |
|---|---|
| Current CV format | Unknown. Seed `data/` from the 2019 `.Rmd` snapshot now; the user shares the current CV (Word or PDF) to fill 2019–2026 in Milestone 6. |
| Which example CVs drive style | The three vitae styles: awesome, modern, classic (hyndman). Each becomes a Typst format. |
| Website and JSON shape | crumplab.com is a Quarto site. It will read `cv.json` published by this repo (stable URL on `gh-pages`). Shape is drafted below; the website spike is Milestone 7. |
| Academic only, or short versions too | Academic CV only for v1. Entries carry optional `tags` so a two-page CV or biosketch is a filter later, not a new data model. |
| Publications source | BibTeX in `data/publications.bib`, exported from Zotero (Better BibTeX). ORCID is the top-up source for the 2019–2026 gap. |
| Typst or LaTeX | Typst. Quarto bundles it, it renders in under a second, styling is plain functions, no TeX Live in CI. |
| Engine for data → document | R (knitr) chunks in `cv.qmd`, with helpers in `R/cv.R`. Matches the vitae code and the user's tooling. Python would work equally well and the helper layer is about 100 lines, so switching later is cheap. |

## Scope

In scope for v1:

- `data/` files with a documented schema and a validation script.
- `cv.qmd` rendering to `cv.pdf` (Typst), `cv.docx`, `cv.html` from the same data.
- Three Typst style variants rendered side by side, one chosen as default.
- `cv.json` export on every render.
- GitHub Action that validates, renders, and publishes outputs to `gh-pages`.
- A Claude skill and `CLAUDE.md` conventions for chat updates.
- Seed content from the 2019 snapshot, then a refresh to 2026.

Out of scope for v1 (possible later):

- Short CV, biosketch, or NSF/NIH formats.
- Automatic ORCID or Google Scholar sync.
- Website integration beyond publishing `cv.json` and a documented fetch pattern.
- JSON Resume compatibility (a mapping can be added on top of `cv.json`).

## Architecture

```
CrumpCV/
├── _quarto.yml                  project config: formats, pre/post-render scripts
├── cv.qmd                       the document: headings + one R chunk per section
├── data/
│   ├── profile.yml              name, title, affiliation, email, links, interests
│   ├── positions.yml
│   ├── education.yml
│   ├── grants.yml
│   ├── publications.bib         Zotero / Better BibTeX export
│   ├── talks.yml                invited talks and conference presentations
│   ├── teaching.yml
│   ├── students.yml             mentees and dissertation committees
│   └── service.yml
├── schema/*.json                JSON Schema per section, used by validate + CI
├── R/cv.R                       read_section(), cv_entries(), cv_list(), cv_bib()
├── scripts/
│   ├── validate.R               schema checks, ordering, privacy lint
│   └── build_json.R             post-render: data + bib → _output/cv.json
├── csl/apa-cv.csl               APA 7 sorted by descending date (from the CSL repo)
├── _extensions/
│   ├── cv-classic/              Typst format, hyndman-like
│   ├── cv-modern/               Typst format, moderncv-like
│   └── cv-awesome/              Typst format, Awesome-CV-like, bundled fonts
├── templates/reference.docx     Word styles
├── styles/README.md             gallery of page-1 previews, decision log
├── _output/                     rendered files (ignored, published by CI)
├── .github/workflows/render.yml
├── .claude/skills/add-entry/SKILL.md
└── examples/vitae/              the pruned CV Examples (see Milestone 0)
```

Data flow:

```
data/*.yml + publications.bib
        │  (validate.R, pre-render)
        ▼
cv.qmd ── R/cv.R ──► Markdown + raw Typst blocks
        │
        ├─► typst  ──► _output/cv.pdf         (one per style while comparing)
        ├─► docx   ──► _output/cv.docx        (reference.docx styles)
        ├─► html   ──► _output/cv.html
        └─► build_json.R (post-render) ──► _output/cv.json
```

Each helper emits two representations of an entry: a raw ```` ```{=typst} ```` block calling the style's `#cv-entry()` function, and a Markdown fallback wrapped in `::: {.content-visible unless-format="typst"}` for Word and HTML. Typst gets full layout control; Word and HTML get a clean, plainer rendering from the same call.

### Data model

Conventions: one YAML list per file, newest first, years as integers, `end: null` for ongoing, optional `tags` list on any entry, optional `note` free text. IDs are only needed where another file refers to an entry.

```yaml
# data/profile.yml
name: Matthew J. C. Crump
title: Professor of Psychology
affiliation: Brooklyn College of CUNY
department: Department of Psychology
email: mcrump@brooklyn.cuny.edu
website: https://crumplab.com
github: CrumpLab
orcid: null            # add if wanted
interests:
  - Learning, memory, attention, and performance
  - Computational modeling of semantic cognition
  - Pattern learning and recognition

# data/positions.yml
- title: Professor
  institution: Brooklyn College of CUNY
  location: Brooklyn, NY
  start: 2022
  end: null
- title: Visiting Research Professor
  institution: University of Manitoba
  location: Winnipeg, MB
  start: 2019-10
  end: 2019-10

# data/education.yml
- degree: Ph.D.
  field: Psychology
  institution: McMaster University
  location: Hamilton, ON
  year: 2007

# data/grants.yml
- title: Acquisition of hierarchical control in skilled action sequencing
  funder: National Science Foundation
  program: null
  number: "1353360"
  amount: 356073
  currency: USD
  role: PI
  start: 2014-07
  end: 2017-06

# data/talks.yml
- type: invited            # invited | conference | workshop
  year: 2018
  authors: [Crump, M. J. C.]
  title: "Betrayed by your fingertips: Keystroke dynamics in typing as cognitive fingerprints"
  venue: ConCats seminar, New York University
  location: New York, NY

# data/teaching.yml
- level: undergraduate     # undergraduate | masters | doctoral
  code: PSYC 3400
  title: Statistics
  note: Large sections, OER

# data/students.yml
- level: doctoral          # postdoc | doctoral | masters | undergraduate
  name: Nicholaus Brosowsky
  start: 2014
  end: 2019
  program: Cognition, Language, and Development
  note: null
- level: committee
  role: Chair
  student: Nicholaus Brosowsky
  institution: Graduate Center of CUNY
  year: 2019

# data/service.yml
- category: department     # college | department | doctoral-program | professional | reviewing
  role: Director of Experimental Psychology Graduate Program
  organization: Brooklyn College of CUNY
  start: 2019
  end: null
- category: reviewing
  role: Ad hoc reviewer
  organization: Psychonomic Bulletin & Review
```

Publications stay in BibTeX because Quarto's citeproc formats them for free in every output format. `csl/apa-cv.csl` sorts by descending date, and `nocite: '@*'` prints the whole file. Sub-sections (peer-reviewed, chapters, books, preprints) are driven by the `keywords` field in each entry; `cv_bib(section = "peer-reviewed")` filters on it. If Pandoc's single-bibliography limit gets in the way, the `multibib` Lua filter or one `.bib` per subsection is the fallback.

### JSON shape

`_output/cv.json` is the data files merged, plus publications as CSL-JSON with a preformatted APA string, plus metadata. The website never re-formats anything it does not want to.

```json
{
  "meta": { "generated": "2026-09-30T12:00:00Z", "commit": "abc1234", "schema": 1 },
  "profile": { "name": "…", "title": "…", "affiliation": "…", "email": "…", "website": "…", "interests": ["…"] },
  "positions": [ { "title": "…", "institution": "…", "location": "…", "start": 2022, "end": null } ],
  "education": [ … ],
  "grants": [ … ],
  "publications": [
    { "id": "crumpEvaluatingAmazonMechanical2013", "type": "article-journal", "title": "…",
      "author": [ { "family": "Crump", "given": "M. J. C." } ], "issued": { "date-parts": [[2013]] },
      "container-title": "PLoS ONE", "DOI": "10.1371/journal.pone.0057410",
      "keywords": ["peer-reviewed"], "formatted": "Crump, M. J. C., McDonnell, J. V., & Gureckis, T. M. (2013). …" }
  ],
  "talks": [ … ], "teaching": [ … ], "students": [ … ], "service": [ … ]
}
```

CSL-JSON comes from `quarto pandoc data/publications.bib -t csljson`; the `formatted` strings come from a plain-text citeproc run over the same bib with the same CSL. Both are already in Quarto, so no extra bib parser is needed.

### Style variants

All three render from the same `cv.qmd` by listing three Typst formats in `_quarto.yml`. `quarto render` produces `cv-classic.pdf`, `cv-modern.pdf`, `cv-awesome.pdf` in one go. Each extension defines the same small API so the document does not care which style is active:

- `#cv-header(profile)`: name block and contact line.
- `#cv-section(title)`: section heading.
- `#cv-entry(what, when, with, where, details)`: the `detailed_entries` equivalent.
- `#cv-item(when, text)`: the `brief_entries` equivalent, used for talks, service, students.
- Bibliography styling: numbering, hanging indent, spacing.

Starting points, so nothing is written from scratch:

- classic: hand-written, roughly 80 lines of Typst. Serif, small caps section titles, dates flush right. Closest to the hyndman look and the safest for Word parity.
- modern: adapt `moderner-cv` from Typst Universe or hand-write with the `#3873B3` accent and left date column from `modern.tex`.
- awesome: adapt `modern-cv` (Typst Universe, based on Awesome-CV) or `quarto-awesomecv-typst`; ship the Roboto and FontAwesome files already in `CV Examples/rvitae/awesome/fonts/`.

Comparison workflow: `styles/README.md` shows page-1 PNGs of each variant (made with `pdftoppm -png -r 80 -f 1 -l 1`) and a short notes column. One round of tweaks per style, then the user picks. The chosen style becomes the default `format`; the other two stay in `_extensions/` as cheap options unless the user wants them removed. Style options that should be easy to flip after the choice: accent colour, font family, page size (Letter), date column width, whether publications are numbered.

### Update workflow

The point of the data layer is that an update is a diff to one YAML file.

1. User says, for example, "Add a talk: invited colloquium at NYU, October 2026, title X".
2. The `add-entry` skill maps it to `data/talks.yml`, inserts at the top in the existing shape, runs `Rscript scripts/validate.R`, and commits with `Add talk: X`.
3. Push triggers the Action: validate, render all formats, build `cv.json`, publish to `gh-pages`, attach outputs to the run.
4. `https://crumplab.github.io/CrumpCV/cv.pdf` and `cv.json` are always current.

Because CI renders, chat updates never depend on Quarto or R being installed in the session. A session that does have them can run `quarto render` for a local check. New publications: export from Zotero to `data/publications.bib` (Better BibTeX auto-export keeps it current) or paste a BibTeX entry in chat.

Validation (`scripts/validate.R`) checks: every file parses; each entry matches its JSON Schema; lists are in reverse chronological order; no phone numbers or street addresses anywhere; every bib entry has `author`, `title`, `year` or `date`, and a `keywords` category; no duplicate bib keys.

## Milestones

Each milestone ends in a pushed commit and something the user can look at.

### M0 Housekeeping (this branch, small)

- Commit `PLAN.md`; point `README.md` and `CLAUDE.md` at it.
- Fix `.gitignore`: keep ignoring rendered `*.pdf` and `*.docx`, but un-ignore `templates/reference.docx` and rendered previews in `styles/previews/`. Add `_output/`.
- Propose pruning `CV Examples/` to the useful files (`*.Rmd`, `*.bib`, `awesome-cv.cls`, `moderncv*.sty`, `fonts/`) and moving them to `examples/vitae/` without the space in the path. Ask before deleting the `.log`, `.aux`, `.bcf`, `.bbl`, `.blg`, `.out`, `.run.xml`, `.Rproj` build files.

### M1 Data model and seed

- Write `schema/*.json` and the YAML files above.
- Convert the 2019 snapshot from `Untitled.Rmd` into `data/*.yml`: 4 positions, 2 degrees, 4 grants, 13 invited talks, 37 conference presentations, 1 postdoc, 3 doctoral, 4 master's, and 21 undergraduate mentees, 9 committees, 19 courses, about 30 service items, and the reviewing journal list.
- Import `Crump_pr.bib` as `data/publications.bib`: strip `file`, `abstract`, `urldate`; keep `doi`; add `keywords = {peer-reviewed}` or `{chapter}`; cross-check against `works2.bib` for the 3 books (textbook, course website, lab manual) and add them tagged `book` or `oer`.
- `scripts/validate.R` passing on the seed data.
- Deliverable: `data/` complete for 2019, validated. Commit `Seed data from 2019 vitae snapshot`.

### M2 Render pipeline with the classic style

- `_quarto.yml` with `cv-classic-typst`, `docx`, and `html` formats, `output-dir: _output`, `pre-render: Rscript scripts/validate.R`.
- `R/cv.R` helpers and `cv.qmd` with one chunk per section.
- `_extensions/cv-classic/` Typst format (template, show rules, the five functions).
- `csl/apa-cv.csl`, `nocite: '@*'`, publications subsections via keywords.
- `templates/reference.docx` with Heading 1/2, body, and a two-column entry table style.
- Deliverable: `quarto render` produces `cv.pdf`, `cv.docx`, `cv.html` from the seed data. Commit `Render pipeline: classic Typst, Word, HTML`.

### M3 Style exploration

- Add `_extensions/cv-modern/` and `_extensions/cv-awesome/` implementing the same five functions.
- Render all three, generate `styles/previews/*.png`, write `styles/README.md` with the gallery and notes.
- User reviews; one tweak round each; user picks. Record the decision in `styles/README.md` and set the default format.
- Deliverable: three PDFs plus gallery, then a chosen default. Commits `Add modern and awesome Typst styles`, `Choose <style> as default CV style`.

### M4 JSON export and CI

- `scripts/build_json.R` as a `post-render` step producing `_output/cv.json` (shape above), including CSL-JSON and formatted strings.
- `.github/workflows/render.yml`: on push to `main` and on PRs, set up Quarto (pinned version) and R (r-lib/actions, packages: yaml, jsonlite, knitr, rmarkdown), validate, render, upload `_output/` as an artifact; on `main` also publish `_output/` to `gh-pages`.
- README documents the stable URLs.
- Deliverable: green Action, `cv.pdf`, `cv.docx`, `cv.json` reachable at `https://crumplab.github.io/CrumpCV/`. Commit `Export cv.json and render in CI`.

### M5 Chat update workflow

- `.claude/skills/add-entry/SKILL.md`: intake questions (which section, required fields), insertion rules, validate, commit message format, when to ask (removals, rewording, ambiguous section).
- Expand `CLAUDE.md`: file map, schema summary, ordering rules, privacy rules, how to render locally, how to add a publication.
- Dry run: add three real items by chat (a talk, a service role, a bib entry) and confirm CI publishes them.
- Deliverable: a working end-to-end update by chat. Commit `Add add-entry skill and conventions`.

### M6 Content refresh to 2026

- User shares the current CV (any format). Diff it against `data/` section by section and add the missing 2019–2026 entries: positions (Professor 2022, chair role), grants, talks, students, teaching, service.
- Top up `publications.bib` from Zotero or an ORCID export; dedupe against existing keys.
- Fold in the Chair Activities Inventory as service entries once that list exists.
- Deliverable: a current CV. Several commits, one per section.

### M7 Website integration spike (after v1)

- In the crumplab.com Quarto project, try the two candidate patterns: an OJS cell fetching `cv.json`, or a Quarto custom listing with an EJS template over a copy of the section data. Pick one and document the fetch URL and shape in this repo's README.

## Risks

| Risk | Mitigation |
|---|---|
| Rendering cannot be verified in Claude web sessions (no Quarto or R in the container today). | CI is the render check. Optionally add a SessionStart setup script that installs Quarto and R so sessions can render locally. |
| Word output looks plain next to the Typst PDF. | Accept it as the editable format. Invest in `reference.docx` styles once, after the Typst style is chosen. |
| Typst font embedding and licensing for the awesome style. | Ship fonts inside the extension; Roboto and FontAwesome are already in the examples under open licences. |
| Publications gap 2019–2026 and messy exports (ORCID keys, journal names). | Zotero is the source; ORCID only for discovery. Validation rejects entries without a category keyword. |
| Pandoc supports one bibliography per document. | Keywords plus filtering in `cv_bib()` first; `multibib` filter or per-section bib files as fallback. |
| Public repo privacy. | Validation lints for phone numbers and addresses. Office phone from the examples is not carried over unless approved. `CLAUDE.md` already forbids private data. |
| Style exploration expands without end. | Three variants, one tweak round each, then a decision recorded in `styles/README.md`. |
| Quarto or Typst version drift breaks the build. | Pin the Quarto version in the Action and note it in README. |
| Chat updates introduce malformed data. | Schema validation in the skill and in CI; commits are small and reviewable. |
| Dates in mixed formats (`2019-10`, `Summer 2013`, `Spring 2019`). | Schema allows year, year-month, or a `when` free-text override that renders verbatim; sorting uses `start`/`year`. |

## First steps

In order, starting on this branch:

1. Commit `PLAN.md` and the README and CLAUDE.md pointers.
2. Fix `.gitignore` (un-ignore `templates/reference.docx`, ignore `_output/`).
3. Get approval to prune and move `CV Examples/` to `examples/vitae/`.
4. Write `schema/` and `data/profile.yml`, `positions.yml`, `education.yml` by hand from the snapshot; write `scripts/validate.R`; run it.
5. Convert talks, grants, teaching, students, and service from `Untitled.Rmd` into YAML.
6. Clean and import `Crump_pr.bib` with keywords.
7. Build `_quarto.yml`, `R/cv.R`, `cv.qmd`, and the classic Typst extension; render locally or via the Action; open the PDF.
8. Add the modern and awesome styles, generate previews, and hand the gallery to the user for the style decision.

## Environment notes

- Local: Quarto 1.6 or later (Typst bundled), R 4.3 or later with `yaml`, `jsonlite`, `knitr`, `rmarkdown`, and `jsonvalidate` for schema checks. No TeX installation needed. `poppler-utils` for `pdftoppm` previews.
- CI: `quarto-dev/quarto-actions/setup`, `r-lib/actions/setup-r` and `setup-r-dependencies`, `peaceiris/actions-gh-pages` or `actions/deploy-pages` for publishing.
- This cloud session has Python only. Data and schema work is possible here; rendering waits for CI or a local machine.
