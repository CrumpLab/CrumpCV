# CrumpCV

A CV as code: structured data, rendered by Quarto to PDF, Word, and JSON for the website.

## Current stage

Planned, not yet built. `PLAN.md` records the decisions, data model, milestones, and first steps. Work through the milestones in order, starting with M0 housekeeping and M1 data seeding from the 2019 snapshot in `CV Examples/rvitae/Untitled/Untitled.Rmd`.

## Intended design

- `data/` is the single source of truth, one file per section (positions, education, publications, grants, talks, teaching, students, service). Every output format is generated from it; never edit generated output by hand.
- Publications will likely live in a BibTeX file and be formatted with a citation style such as APA.
- PDF, Word, and JSON outputs are all rendered from the same data so they never drift apart.

## Conventions

- When the user describes a new CV item in chat, add it to the right data file in the existing format, keep entries in reverse chronological order, re-render if rendering exists, and commit with a message like `Add talk: <title>`.
- Ask before removing or rewording existing entries.
- This repo is public. Do not commit private information such as home addresses, phone numbers, or anything the user has not approved for a public CV.
