# CV as Code

> A Quarto CV project in its own GitHub repo, driven by structured data, that renders to PDF, Word and a JSON feed for the website, and can be updated just by chatting with Claude.

Seeded from the Idea Console (slug `cv-as-code`). This file is a snapshot; the living plan will be `PLAN.md` in this repo.

## What

A GitHub repo that holds the CV as a Quarto project. The CV content lives in structured data files, and Quarto renders it into the formats needed.

- **PDF** for sending and posting.
- **Word** for institutions that ask for an editable file.
- **JSON** so the CV can easily be added to the personal website as a custom format.

Adding something new should be as easy as telling Claude about it in a chat. Claude updates the data, re-renders, and commits.

## Why

The CV needs updating, and keeping one document current across several formats is tedious. It also drifts out of sync with the website. With one structured source, every format stays consistent, and small additions such as a new paper, talk, grant, or student become quick edits rather than a formatting chore.

## How

- **One source of truth.** Store entries as YAML or JSON data by section: positions, education, publications, grants, talks, teaching, students, and service. Quarto templates render them. The JSON export for the website comes from the same data.
- **Publications from BibTeX.** Publications could live in a `.bib` file and be formatted by a citation style such as APA, which Quarto supports natively. Entries could later be pulled from ORCID or Google Scholar.
- **Style exploration.** The user shares example CVs as Word documents. Claude extracts their layouts and builds two or three style variants to compare. PDF output could use Typst or LaTeX, and Word output a styled reference document.
- **Chat updates.** The repo gets a `CLAUDE.md` and a skill for adding an entry. It takes a plain description such as a new talk, puts it in the right section in the right format, re-renders, and commits.
- **Automatic builds.** An optional GitHub Action renders the PDF, Word, and JSON files on every push so current copies are always available.

## Open questions

- What format is the current CV in, and can it be shared so it can be converted into the structured data?
- Which example CVs should drive the style exploration? Share them as Word files when ready.
- What is the personal website built with, and what JSON shape would it want?
- Is this an academic CV only, or should the same data also produce shorter versions, such as a two-page CV or a biosketch for grants?
- Should publications come from a BibTeX file, from ORCID or Google Scholar, or be entered by hand?
- Should the PDF use Typst, which renders quickly and is easy to style, or LaTeX?

## Notes

- 2026-09-30: Captured from chat. The user needs to update their CV and prefers a Quarto project so it can export to PDF and Word. They also want a JSON form that is easy to add to their website as a custom format.
- 2026-09-30: The user has several example CVs as Word documents to compare styles, and imagines a GitHub repo they can update by chatting, possibly with a hybrid Claude tool.
- 2026-09-30: Saved as a seed without a workshop round. The open questions are the workshop questions to settle before /expand-idea.
- 2026-09-30: Linked to the Chair Activities Inventory, a to-do for brainstorming chair-related activities into CV items.
