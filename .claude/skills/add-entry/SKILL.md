---
name: add-entry
description: Add a CV item (talk, publication, grant, student, course, service role, award, software) to the right data file from a plain-language description, validate, and commit.
---

# add-entry

Turn a description like "add a talk: invited colloquium at NYU, October 2026, title X" into a data change.

## Steps

1. **Pick the file** from the item type:

   | Item | File | Notes |
   |---|---|---|
   | publication, paper, chapter, preprint, textbook/OER | `data/publications.bib` | BibTeX entry; `keywords = {category}`; see below |
   | invited talk, colloquium, workshop | `data/talks.yml` with `type: invited` or `workshop` | |
   | conference talk, poster, abstract | `data/talks.yml` with `type: conference` | |
   | grant (funded or submitted) | `data/grants.yml` | `status: funded|submitted|declined`, `role` |
   | award, fellowship, scholarship | `data/awards.yml` | |
   | software, package, website, template | `data/software.yml` | |
   | course taught | `data/teaching.yml` under `courses` | `level: undergraduate|masters|doctoral|other` |
   | student, mentee, postdoc | `data/students.yml` under `mentees` | `surname` and `initials` power the co-author stars |
   | dissertation committee | `data/students.yml` under `committees` | |
   | committee, editorial role, membership | `data/service.yml` | pick `category` (see file header) |
   | grant panel or journal reviewing | `data/reviewing.yml` | |
   | new position, promotion, chair role | `data/positions.yml` | set `end` on the previous entry |

2. **Match the existing shape.** Open the file, copy the field set of a neighbouring entry, fill it in. Quote strings that contain a colon. Use `start`/`end` (year or `YYYY-MM`) for sorting and `when` for the text that should print verbatim (`Summer 2027`, `Spring 2026 - present`). `end: null` means ongoing.

3. **Insert newest first** within the list (within its `category` for service, within `type` for talks, within `status` for grants, within `level` for mentees and courses).

4. **Publications.** Prefer a BibTeX entry from Zotero or from the DOI (`curl -LH "Accept: application/x-bibtex" https://doi.org/<doi>`); otherwise write it by hand. Always add `keywords = {article}` (or `review-article`, `chapter`, `proceedings`, `book`, `oer`, `commentary`, `book-review`, `preprint`, `other`; add `, invited` if invited). Use `status = {inpress}` or `{inprogress}` for unpublished work. Write the owner as `Crump, M. J. C.`. Titles in sentence case; wrap proper nouns and acronyms in braces (`{R}`, `{Stroop}`) because Pandoc lowercases unprotected words. Do not star mentee co-authors; that comes from `students.yml`.

5. **Validate**: `python3 scripts/validate.py`. Fix anything it reports.

6. **Render if Quarto is available** (`quarto render`); otherwise say that CI will render on push.

7. **Commit** with `Add <type>: <short title>` (for example `Add talk: Instance theory as an intuition pump`). One item per commit unless the user gave a batch.

## Ask before

- removing or rewording an existing entry,
- adding anything private (home address, personal phone, unpublished student details),
- when the section is ambiguous (a workshop could be a talk or teaching): state the choice and continue if the user is not available.

## Missing details

If the description lacks a required field (year, venue, funder, amount), ask once. If the user is not available, insert the entry with the best reading of what was given, leave the unknown field out where the schema allows it, and say what is missing in the commit message body.
