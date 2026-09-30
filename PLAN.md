# PLAN.md — CrumpCV

A CV as code. Structured data in `data/`, rendered by Quarto to PDF (Typst), Word, HTML, and a `cv.json` feed for the website. Updated by describing new items in chat.

**Status (2026-09-30): Milestones 0 to 6 are implemented.** Content is current to March 2024. Milestone 7 (refresh to 2026) needs items only the user can supply; see the end of this file. Milestone 8 (website) is still to do.

Written 2026-09-30 after reviewing `IDEA.md`, the three `vitae` projects in `CV Examples/rvitae/`, and the two 2024 documents `CV Examples/Crump_CV_2024_BC.docx` and `CV Examples/Crump_CV_24_formatted.pdf`.

## Goal

One source of truth for the CV that:

1. renders the academic CV to PDF, Word, and HTML in a style chosen from a few side-by-side variants,
2. renders the Brooklyn College personnel-form CV (the sections I to VIII layout) as Word from the same data, so it never has to be hand-synced again,
3. exports a single `cv.json` containing every section for the website,
4. can be updated by a one-line description in chat, with validation and automatic re-rendering so nothing drifts.

## What the examples tell us

### The two 2024 documents are the content source

| File | Date | What it is |
|---|---|---|
| `Crump_CV_2024_BC.docx` | Feb 14, 2024 | Brooklyn College personnel form: sections I Personal Data, II Higher Education, III Teaching Career, IV Experience and Educational Philosophy, V Scholarly and Creative Activity, VI Grants, VII Professional Awards, VIII Service. Arial headings, 30 tables, instruction text kept from the template. |
| `Crump_CV_24_formatted.pdf` | Mar 5, 2024 | The same content re-laid-out as a standard academic CV, 18 pages, Letter. Sections: Positions Held, Education, Publications, Invited Talks, Abstracts and Papers at Meetings, Grants (Funded), Grants (Submitted), Professional Awards, Service, Mentorship, Dissertation Committees, Teaching Experience. |

They agree almost everywhere. Where they differ the PDF is newer (Honors Academy Reader runs to 2024, Psychology Club liaison ends 2015, SCiP DEI committee ends 2021, funded grants carry a PI marker). The PDF wins on conflicts; the docx supplies the prose sections and the form structure.

Content inventory (2024):

- 4 positions, 2 degrees plus postdoc, dissertation title, appointment and tenure dates.
- 53 publications, numbered, reverse chronological, with an `R.` marker for refereed, `Invited.` for invited, asterisks marking postdoc, doctoral, and undergraduate co-authors, and OER textbooks listed as publications. The form splits them into Recent (2016 onward), Accepted, In Progress (2 preprints), and Previous.
- 15 invited talks, 44 conference presentations, 6 funded grants, 8 submitted proposals, 4 awards, 8 software packages and websites.
- Mentorship: 1 postdoc, 4 doctoral, 5 master's, 26 undergraduates, 12 dissertation committees.
- Teaching: 10 undergraduate, 7 master's, 9 doctoral courses, 8 OER course resources with URLs.
- Service: about 45 entries across college, division, department, student activities, other, doctoral program, professional and editorial, grant reviewing, and a list of 23 journals reviewed for.
- Prose: educational philosophy, other experience, curriculum development, web tutorials, teaching certificate.

Plain-text extractions of both files are in `CV Examples/extracted/` so any session can harvest from them without PDF or Word tooling. Tables from the docx are kept as pipe-delimited rows.

### The vitae projects supply structured publications and three style references

`CV Examples/rvitae/` holds three R `vitae` projects with identical 2019 content and three looks:

| Folder | Look | Build |
|---|---|---|
| `awesome/` | Awesome-CV: Roboto, red accent on the first letters of headings, institution left and location right, tiny small-caps roles | Rendered `Crump_CV.pdf` present |
| `modern/` | moderncv "casual": blue `#3873B3` accent, dates in a left column | Built once, PDF not kept |
| `Untitled/` | hyndman: maroon accent, boxed header with icons, left date column, compact | Rendered `Untitled.pdf` present |

`Crump_pr.bib` (39 entries, 2006 to 2019, Zotero export with `url` removed) is the structured seed for publications. `works2.bib` is an ORCID export of the same period with 3 books added and messier fields. `curie.bib` is vitae sample data.

### The 2024 formatted CV is itself the fourth style reference

It is the user's own current taste: Aptos, bold small-caps section titles with a rule beneath, a two-column contact header, a left date column for positions and education, numbered publications with the user's name in bold, and mentee stars. Replicating this look in Typst is the baseline style; the others are alternatives.

## Decisions on the open questions

| Question | Decision |
|---|---|
| Current CV format | Answered. The 2024 docx and PDF are the source. Harvest them into `data/` in Milestone 1. The remaining gap is 2024 to 2026. |
| Which example CVs drive style | Four references: the 2024 formatted CV (baseline, "classic"), Awesome-CV, moderncv, hyndman. Build classic first, then two alternates. |
| Website and JSON shape | crumplab.com is a Quarto site. It will read `cv.json` published by this repo. Shape drafted below; website spike is Milestone 8. |
| Academic only, or short versions too | Two documents from one dataset: the academic CV and the Brooklyn College form. Entries carry optional `tags` so a two-page CV or biosketch is a filter later. |
| Publications source | BibTeX in `data/publications.bib`, seeded from `Crump_pr.bib` and topped up to 2024 from the PDF list (DOI lookups where possible). Zotero remains the editor of record; ORCID is a discovery source. |
| Typst or LaTeX | Typst. Quarto bundles it, styling is plain functions, no TeX Live in CI. The awesome-cv LaTeX build in the examples failed on fonts. |
| Engine for data to document | **Python pre-render scripts** (`scripts/build.py`), no R or Jupyter. Changed from the original R plan on 2026-09-30 because Quarto and Python were available in the build session while R was not, and because CI then needs only Quarto and pip. The generated sections are plain Markdown plus raw Typst, so the choice of language is invisible to the documents. |

## Scope

In scope for v1:

- `data/` files with a documented schema and a validation script.
- `cv.qmd` (academic CV) rendering to PDF, Word, and HTML from the same data.
- `cv-bc.qmd` (Brooklyn College form) rendering to Word that matches the 2024 docx layout.
- Three Typst style variants rendered side by side, one chosen as default.
- `cv.json` export on every render.
- GitHub Action that validates, renders, and publishes outputs to `gh-pages`.
- A Claude skill and `CLAUDE.md` conventions for chat updates.
- Content harvested from the 2024 documents, then refreshed to 2026.

Out of scope for v1 (possible later):

- Biosketch or NSF/NIH formats, two-page CV.
- Automatic ORCID or Google Scholar sync.
- Website integration beyond publishing `cv.json` and a documented fetch pattern.
- JSON Resume compatibility (a mapping on top of `cv.json`).

## Architecture

```
CrumpCV/
├── _quarto.yml                  formats, pre-render and post-render scripts
├── cv.qmd                       academic CV: headings + one R chunk per section
├── cv-bc.qmd                    Brooklyn College form: same chunks, form order, form prose
├── data/
│   ├── profile.yml              name, title, affiliation, links, interests, appointment dates
│   ├── positions.yml
│   ├── education.yml            degrees, dissertation, advisors, postdoc
│   ├── publications.bib         Zotero / Better BibTeX export; keywords drive categories
│   ├── talks.yml                invited talks and conference presentations
│   ├── grants.yml               funded and submitted, with role
│   ├── awards.yml
│   ├── software.yml             packages, websites, other creative work
│   ├── teaching.yml             courses with level, notes, OER URL
│   ├── students.yml             mentees by level, and dissertation committees
│   ├── service.yml              categorised to match the BC form subsections
│   ├── reviewing.yml            journals reviewed for, grant panels
│   └── narratives/*.md          educational philosophy, other experience, curriculum development
├── schema/*.json                JSON Schema per section
├── scripts/
│   ├── validate.py              schema, ordering, privacy lint, bib checks
│   ├── build.py + cvlib.py      pre-render: data → _generated/*.md (Markdown + raw Typst), meta.yml, cv.json
│   ├── build_bc.py              the Brooklyn College form sections
│   ├── render_styles.py         render every Typst style and write previews
│   ├── make_reference_docx.py   build the Word reference documents
│   └── harvest/                 one-off parsers used in M1, kept for reference
├── csl/apa-cv.csl               APA 7 sorted by descending date
├── _extensions/
│   ├── cv-classic/              Typst format matching the 2024 formatted CV
│   ├── cv-modern/               moderncv-like
│   └── cv-awesome/              Awesome-CV-like, bundled Roboto + FontAwesome
├── templates/
│   ├── reference.docx           Word styles for the academic CV
│   └── reference-bc.docx        Word styles cloned from Crump_CV_2024_BC.docx
├── styles/README.md             gallery of page-1 previews, decision log
├── _output/                     rendered files, published by CI
├── .github/workflows/render.yml
├── .claude/skills/add-entry/SKILL.md
└── CV Examples/                 the source documents and vitae projects (pruned in M0)
```

Data flow:

```
data/*.yml + publications.bib + narratives/*.md
        │  validate.R, build_pubs.R  (pre-render)
        ▼
cv.qmd, cv-bc.qmd ── R/cv.R ──► Markdown + raw Typst blocks
        │
        ├─► typst ──► _output/cv.pdf            (cv-classic, cv-modern, cv-awesome while comparing)
        ├─► docx  ──► _output/cv.docx, _output/cv-bc.docx
        ├─► html  ──► _output/cv.html
        └─► build_json.R (post-render) ──► _output/cv.json
```

Each helper emits two representations of an entry: a raw ```` ```{=typst} ```` block calling the style's `#cv-entry()` function, and a Markdown fallback wrapped in `::: {.content-visible unless-format="typst"}` for Word and HTML. Typst gets full layout control; Word and HTML get a clean, plainer rendering from the same call. The BC form is Word-first and uses tables, so its helpers emit Markdown tables that `reference-bc.docx` styles.

### Publications are rendered as data, not by in-document citeproc

The 2024 CV needs things citeproc alone cannot do: numbering that restarts per subsection, the user's name in bold, mentee stars derived from `students.yml`, an `R.` refereed marker, and the form's Recent / Accepted / In Progress / Previous split by date and status. So publications are pre-rendered once and then treated like any other section:

1. `build_pubs.R` runs `quarto pandoc data/publications.bib -t csljson` for structured data, and a citeproc run with `csl/apa-cv.csl` to get one formatted Markdown string per entry.
2. It joins the two by citation key and adds `refereed`, `category`, `status`, and `mentees` from the bib fields (`keywords`, `note`, custom `status = {inpress|inprogress}`), writing `_data/publications.json`.
3. `cv_pubs()` in `R/cv.R` filters, sorts, numbers, bolds the user's name, marks mentee co-authors by matching surnames and initials against `students.yml`, and emits the list.

Categories via `keywords`: `article`, `chapter`, `proceedings`, `book`, `oer`, `preprint`, `review`, `other`. The mentee-star logic is a lookup, so a new student in `students.yml` automatically stars their future papers.

### Data model

Conventions: one YAML list per file, newest first, years as integers, `end: null` for ongoing, optional `tags` list, optional `note` free text, optional `when` free text that renders verbatim when a date does not fit (for example `Summer 2013`). Sorting uses `start` or `year`.

```yaml
# data/profile.yml
name: Matthew J. C. Crump
short_name: Crump, M. J. C.          # used to bold the user's name in author lists
title: Professor of Psychology
department: Department of Psychology
affiliation: Brooklyn College of CUNY
address: 2900 Bedford Avenue, Brooklyn, NY 11210    # institutional, already public
phone: null                          # office line is in the public CV; include only if approved
email: mcrump@brooklyn.cuny.edu
website: https://crumplab.com
github: CrumpLab
orcid: null
interests:
  - Learning, memory, attention, and performance
  - Computational modeling of semantic cognition
  - Pattern learning and recognition
appointment:                         # BC form section I
  initial_appointment: 2011-01-28
  tenure_date: 2018-09-01
  present_rank: Full Professor
  present_rank_since: 2022-09-01
  promotions: [2016-09-01, 2022-09-01]

# data/positions.yml
- title: Full Professor
  institution: Brooklyn College of CUNY
  department: Department of Psychology
  location: Brooklyn, NY
  start: 2022-09
  end: null
- title: Postdoctoral Researcher
  institution: Vanderbilt University
  department: Department of Psychology
  location: Nashville, TN
  start: 2007
  end: 2011
  advisor: Gordon D. Logan

# data/education.yml
- degree: Ph.D.
  field: Psychology
  institution: McMaster University
  location: Hamilton, ON, Canada
  start: 2002
  end: 2007
  conferred: 2007-11-16
  dissertation: "Context-specific learning and control: An instance based view of flexible online control"
  advisor: Bruce Milliken
- degree: B.Sc. (Hon.)
  field: Psychology
  institution: University of Lethbridge
  location: Lethbridge, AB, Canada
  start: 1999
  end: 2002
  advisor: John Vokey

# data/grants.yml
- title: Remembering and forgetting pictures: Testing a computational instance-based account
  funder: PSC-CUNY
  program: Traditional B
  number: null
  amount: 6000
  currency: USD
  role: PI
  status: funded            # funded | submitted | declined
  start: 2023
  end: 2024
- title: Answering questions with data: Teaching computational skills in introductory statistics to psychology undergraduates
  funder: NSF
  amount: 299470
  role: PI
  status: submitted
  submitted: 2021-02

# data/talks.yml
- type: invited            # invited | conference | workshop
  year: 2022
  authors: [Crump, M. J. C.]
  title: Instance theory as a domain-general intuition pump for cognition
  venue: CCP colloquium, The Graduate Center of CUNY
  location: New York, NY
- type: conference
  year: 2022
  authors: [Shives, D. W., Ihejirika, P., Crump, M. J. C.]
  title: The role of stimulus duration in directed forgetting for natural scenes
  venue: Psychonomic Society Annual Meeting
  location: Boston, MA

# data/awards.yml
- title: Doctoral Thesis Award, Certificate of Academic Excellence
  organization: Canadian Psychological Association
  year: 2008

# data/software.yml
- name: Vertical
  description: R-studio project template and workflow for sharing psychological research projects as a website
  type: r-package
  url: https://www.crumplab.com/vertical/

# data/teaching.yml
- level: undergraduate     # undergraduate | masters | doctoral | other
  code: PSYC 2530
  title: Introduction to Cognitive Psychology
  note: In-person, async, sync, large sections
  oer: https://www.crumplab.com/cognition/
  institution: Brooklyn College of CUNY

# data/students.yml
- level: doctoral          # postdoc | doctoral | masters | undergraduate
  name: Drew Shives
  surname: Shives
  initials: D. W.
  start: 2021
  end: null
  program: Cognitive and Comparative Psychology training area
- level: undergraduate
  name: Patrick Ihejirika
  surname: Ihejirika
  initials: P.
  note: MARC; honors thesis; Goldwater scholarship winner
- level: committee
  role: Committee member
  student: Janani Rajagopalan
  institution: Graduate Center of CUNY
  year: 2023

# data/service.yml
- category: department     # college | division | department | student-activities | other-college
                           # | doctoral-program | university | professional | community
  role: Appointments Committee (elected)
  organization: Department of Psychology, Brooklyn College
  when: "May 2018 – June 2021; May 2022 – present"
  start: 2018
  end: null

# data/reviewing.yml
grant_panels:
  - organization: PSC-CUNY
    role: Grant Review Panel, Cycle 55
    year: 2024
journals:
  - Acta Psychologica
  - Attention, Perception, and Psychophysics
```

`data/narratives/` holds `educational-philosophy.md`, `other-experience.md`, `curriculum-development.md`, `web-tutorials.md`, and `certificates.md`, used only by the BC form and included with `{{< include >}}`.

### JSON shape

`_output/cv.json` is the data files merged, with publications as CSL-JSON plus the formatted string, plus metadata.

```json
{
  "meta": { "generated": "2026-09-30T12:00:00Z", "commit": "abc1234", "schema": 1 },
  "profile": { "name": "…", "title": "…", "affiliation": "…", "email": "…", "website": "…", "interests": ["…"] },
  "positions": [ { "title": "…", "institution": "…", "start": "2022-09", "end": null } ],
  "education": [ … ],
  "publications": [
    { "id": "crumpEvaluatingAmazonMechanical2013", "type": "article-journal", "title": "…",
      "author": [ { "family": "Crump", "given": "M. J. C." } ], "issued": { "date-parts": [[2013]] },
      "container-title": "PLoS ONE", "DOI": "10.1371/journal.pone.0057410",
      "category": "article", "refereed": true, "mentee_coauthors": [],
      "formatted": "Crump, M. J. C., McDonnell, J. V., & Gureckis, T. M. (2013). …" }
  ],
  "talks": [ … ], "grants": [ … ], "awards": [ … ], "software": [ … ],
  "teaching": [ … ], "students": [ … ], "service": [ … ], "reviewing": { … }
}
```

Narratives are not exported by default.

### Style variants

All three Typst styles render from `cv.qmd` by listing three formats in `_quarto.yml`; one `quarto render` yields `cv-classic.pdf`, `cv-modern.pdf`, `cv-awesome.pdf`. Each extension implements the same small API:

- `#cv-header(profile)`: name block and contact lines.
- `#cv-section(title)`: section heading.
- `#cv-entry(what, when, with, where, details)`: positions, education, committees.
- `#cv-item(when, text)` and `#cv-numbered(items)`: talks, service, publications.
- `#cv-table(rows)`: grants.

Starting points:

- classic: hand-written Typst matching the 2024 formatted CV. Letter size, bold small-caps headings with a rule, two-column header, left date column, numbered publications with bold self-name and mentee stars. Aptos is proprietary, so use an open metric-compatible substitute (Source Sans 3 or Inter) shipped in the extension.
- modern: adapt `moderner-cv` from Typst Universe or hand-write with the `#3873B3` accent and left date column from `modern.tex`.
- awesome: adapt `modern-cv` from Typst Universe (based on Awesome-CV) or `quarto-awesomecv-typst`, shipping the Roboto and FontAwesome files from `CV Examples/rvitae/awesome/fonts/`.

Comparison workflow: `styles/README.md` shows page-1 PNGs of each variant beside the 2024 PDF's page 1, with a notes column. One tweak round per style, then the user picks. The chosen style becomes the default; the others stay as cheap options unless removed. Easy-to-flip options after the choice: accent colour, font, page size, date column width, whether publications are numbered, whether mentee stars show.

### The Brooklyn College form

`cv-bc.qmd` reproduces sections I to VIII in the form's order, keeps the form's instruction sentences as static text, and fills every table from data. `reference-bc.docx` is derived from the 2024 docx so headings, fonts, and table styles match. Parameters at the top of the file: `recent_since` (the cutoff for Recent vs Previous publications, 2016 in the 2024 version) and `as_of` date. The Word output is the deliverable; a PDF of it is a bonus.

### Update workflow

1. User says, for example, "Add a talk: invited colloquium at NYU, October 2026, title X".
2. The `add-entry` skill maps it to `data/talks.yml`, inserts at the top in the existing shape, runs `Rscript scripts/validate.R`, and commits with `Add talk: X`.
3. Push triggers the Action: validate, build publications, render all documents, build `cv.json`, publish to `gh-pages`, attach outputs to the run.
4. `https://crumplab.github.io/CrumpCV/cv.pdf`, `cv-bc.docx`, and `cv.json` are always current.

Because CI renders, chat updates never depend on Quarto or R in the session. New publications: export from Zotero to `data/publications.bib`, or paste a BibTeX entry or DOI in chat and the skill fetches BibTeX from doi.org. New mentees added to `students.yml` automatically get stars on their papers.

Validation checks: every file parses; each entry matches its schema; lists are in reverse chronological order; no personal phone numbers or home addresses; every bib entry has `author`, `title`, a date, and a category keyword; no duplicate bib keys; every mentee co-author string in a bib `note` matches a `students.yml` entry.

## Milestones

Each milestone ends in a pushed commit and something the user can look at.

### M0 Housekeeping

- Commit this plan and the text extractions in `CV Examples/extracted/`.
- Propose pruning `CV Examples/rvitae/` to the useful files (`*.Rmd`, `*.bib`, the two rendered PDFs, `awesome-cv.cls`, `moderncv*.sty`, `fonts/`) and deleting the `.log`, `.aux`, `.bcf`, `.bbl`, `.blg`, `.out`, `.run.xml`, `.Rproj` build files. Ask before deleting. Keep the folder name.
- `.gitignore` already allows PDF and Word files; add `_output/` and `_data/` once rendering exists and decide whether rendered outputs are committed.

### M1 Harvest the 2024 documents into `data/`

- Write `schema/*.json` and `scripts/validate.R`.
- From `CV Examples/extracted/`, build every YAML file listed above. The docx tables give teaching, grants, service, committees, and mentees row by row; the PDF gives talks, awards, software, and the newer service dates.
- Publications: start from `Crump_pr.bib` (39 entries, strip `file`, `abstract`, `urldate`), add the 14 entries from 2019 to 2023 that the PDF lists (fetch BibTeX by DOI where available, hand-write the OER textbooks and proceedings), add the 2 preprints as `status = {inprogress}`, tag every entry with a category keyword and `refereed`. Record mentee co-authorship in a `note` or custom field only where the star lookup cannot infer it.
- Narratives copied into `data/narratives/*.md`.
- Resolve the small conflicts using the 2024 values (B.Sc. 2002 not 2001, postdoc from 2007 not 2008, Ph.D. conferred November 2007) and list them for the user.
- Deliverable: `data/` complete as of March 2024, validated. Commits per section, then `Harvest 2024 CV into data/`.

### M2 Render pipeline with the classic style

- `_quarto.yml` with `cv-classic-typst`, `docx`, and `html` formats, `output-dir: _output`, pre-render `validate.R` and `build_pubs.R`.
- `R/cv.R` helpers and `cv.qmd` with one chunk per section.
- `_extensions/cv-classic/` matching the 2024 formatted CV.
- `csl/apa-cv.csl`, publications via `cv_pubs()` with numbering, bold self-name, mentee stars, refereed marker.
- `templates/reference.docx` with Heading 1/2, body, and a two-column entry table style.
- Deliverable: `quarto render` produces `cv.pdf`, `cv.docx`, `cv.html` that match the 2024 CV's content page for page. Commit `Render pipeline: classic Typst, Word, HTML`.

### M3 Style exploration

- Add `_extensions/cv-modern/` and `_extensions/cv-awesome/` implementing the same API.
- Render all three, generate `styles/previews/*.png`, write `styles/README.md` with the gallery beside the 2024 PDF.
- User reviews; one tweak round each; user picks. Record the decision and set the default format.
- Deliverable: three PDFs plus gallery, then a chosen default.

### M4 Brooklyn College form

- `cv-bc.qmd` and `templates/reference-bc.docx` cloned from the 2024 docx.
- Render and diff against `Crump_CV_2024_BC.docx` section by section (text extraction of both, compared with `diff`).
- Deliverable: `cv-bc.docx` that a reviewer could not tell from the hand-made one, apart from newer entries. Commit `Add Brooklyn College form output`.

### M5 JSON export and CI

- `scripts/build_json.R` as a post-render step producing `_output/cv.json`.
- `.github/workflows/render.yml`: on push to `main` and on PRs, set up Quarto (pinned) and R (r-lib/actions, packages: yaml, jsonlite, knitr, rmarkdown, jsonvalidate), validate, render, upload `_output/` as an artifact; on `main` also publish to `gh-pages`.
- README documents the stable URLs.
- Deliverable: green Action, outputs reachable at `https://crumplab.github.io/CrumpCV/`.

### M6 Chat update workflow

- `.claude/skills/add-entry/SKILL.md`: section detection, required fields, insertion rules, DOI-to-BibTeX, validate, commit message format, when to ask (removals, rewording, ambiguous section).
- Expand `CLAUDE.md`: file map, schema summary, ordering and privacy rules, how to render locally, how to add a publication or a student.
- Dry run: add three real items by chat and confirm CI publishes them.

### M7 Content refresh to 2026

- Add everything since March 2024: positions or roles (including chair duties), grants, talks, students, teaching, service, publications from Zotero or ORCID.
- Fold in the Chair Activities Inventory as service entries once that list exists.
- Deliverable: a current CV in both layouts.

### M8 Website integration spike (after v1)

- In the crumplab.com Quarto project, try an OJS cell fetching `cv.json` and a custom listing with an EJS template over the section data. Pick one and document the fetch URL and shape here.

## Risks

| Risk | Mitigation |
|---|---|
| Rendering cannot be verified in Claude web sessions (no Quarto or R in the container). | CI is the render check. Optionally a SessionStart script installs Quarto and R. Data work, harvesting, and validation logic can all be developed here. |
| Harvest errors: 53 publications and about 200 other entries typed from text. | Harvest by script from the extractions where the structure allows (tables), review each YAML file against the PDF once, and keep the extractions in the repo for spot checks. |
| Publication formatting needs beyond citeproc (stars, bold name, per-section numbering). | Pre-rendered strings plus `cv_pubs()` post-processing, described above. |
| Word fidelity for the BC form. | Clone styles from the 2024 docx, compare text extractions with `diff`, accept minor layout differences. |
| Aptos is not available on Linux or in Typst. | Ship an open substitute in the classic extension; note the swap in `styles/README.md`. |
| Public repo privacy. | Validation lints for phone numbers and home addresses. Office phone stays out unless approved. Student names are already public in the 2024 CV. |
| Style exploration expands without end. | Three variants, one tweak round each, then a recorded decision. |
| Quarto or Typst version drift. | Pin the Quarto version in the Action and note it in README. |
| Chat updates introduce malformed data. | Schema validation in the skill and CI; commits are small and reviewable. |
| Mixed date formats (`Summer 2013`, `Spring 2019`, `Elected May 2018 – June 2021; May 2022 – present`). | `start`/`end` for sorting plus an optional `when` string that renders verbatim. |

## First steps

In order, on this branch:

1. Commit this plan and `CV Examples/extracted/`.
2. Get approval to prune the vitae build files.
3. Write `schema/` and `scripts/validate.R`.
4. Harvest `profile.yml`, `positions.yml`, `education.yml`, `grants.yml`, `awards.yml`, `software.yml` from the extractions and validate.
5. Harvest `teaching.yml`, `students.yml`, `service.yml`, `reviewing.yml`, `talks.yml`, then the narratives.
6. Build `publications.bib`: clean `Crump_pr.bib`, add 2019 to 2023 entries and the preprints, tag categories.
7. Build `_quarto.yml`, `R/cv.R`, `cv.qmd`, and the classic Typst extension; render via CI or locally; compare with the 2024 PDF.
8. Add the modern and awesome styles, generate previews, and hand the gallery to the user for the style decision.

## Environment notes

- Local: Quarto 1.6 or later (Typst bundled), R 4.3 or later with `yaml`, `jsonlite`, `knitr`, `rmarkdown`, `jsonvalidate`. No TeX needed. `poppler-utils` for previews.
- CI: `quarto-dev/quarto-actions/setup`, `r-lib/actions/setup-r` and `setup-r-dependencies`, `actions/deploy-pages` or `peaceiris/actions-gh-pages`.
- This cloud session has Python only. `pymupdf` can be pip-installed here for PDF text and page images; the docx is readable by unzipping its XML. Rendering waits for CI or a local machine.


## Implementation notes (2026-09-30)

What was built, and where it departs from the plan above:

- **Engine.** Python pre-render scripts instead of R chunks (see the decisions table). `cv.qmd` and `cv-bc.qmd` contain only headings and `{{< include >}}` lines.
- **Publications.** Parsed from BibTeX with Pandoc (`quarto pandoc -t csljson`) and formatted by `cvlib.fmt_pub()` rather than by citeproc, so numbering, the bold owner name, mentee stars, the `R.` marker, and the form's Recent/Accepted/In Progress/Previous split are all under our control. `csl/apa-cv.csl` was therefore not needed.
- **Styles.** Quarto cannot render two Typst formats of the same document in one project pass (they share `cv.typ`), so `_quarto.yml` lists only the default style and `scripts/render_styles.py` renders the rest. All three share one Typst function API.
- **Fonts.** Source Sans Pro (OFL) for classic and modern, Roboto (Apache 2.0) for awesome, bundled inside the extensions.
- **Word.** `templates/reference.docx` and `reference-bc.docx` are generated from Pandoc's default reference by `scripts/make_reference_docx.py`, not cloned from the 2024 file, because the 2024 file uses direct formatting rather than styles. The form uses Arial headings and an 11 pt body like the original.
- **Harvest corrections.** The 2024 documents disagree with the 2019 vitae files on three dates; the 2024 values were used: B.Sc. 2002 (not 2001), postdoc 2007-2011 (not 2008), Ph.D. conferred November 2007. One 2019 bib entry listed the first author as "Jr, L. P. Behmer"; fixed. One had "Crump, M. J." without the C; fixed. "Trends in cognitive sciences" capitalised.
- **Privacy.** The office phone number that appears in the 2024 PDF is not in `data/profile.yml` (`phone: null`); add it if a public listing is wanted.

## Milestone 7: what the user needs to supply

Nothing after March 2024 is in the data. Network access to Crossref, ORCID, and doi.org was blocked in the build session, so no automatic top-up was possible. To refresh:

1. **Publications 2024-2026.** Export from Zotero (Better BibTeX) or paste BibTeX/DOIs in chat. The `add-entry` skill adds them with categories.
2. **Positions and roles.** Any chair or administrative appointment (the Chair Activities Inventory idea), with start dates; set `end` on superseded entries.
3. **Grants** funded or submitted since 2024. **Awards.**
4. **Talks** since 2023 (invited and conference). **Students** who joined or graduated (new mentees get stars on their papers automatically). **Courses** added. **Service** roles begun or ended (set `end`).
5. **Reviewing** additions (journals, panels).
6. Whether the office phone should appear.

A chat message per section is enough; each becomes one commit.
