# CrumpCV

A CV maintained as a Quarto project. The content lives in structured data files, and Quarto renders it to:

- **PDF** for sending and posting
- **Word** for institutions that want an editable file
- **JSON** for the personal website

New entries can be added by describing them to Claude in chat.

## Status

Planned. `PLAN.md` holds the goal, scope, milestones, risks, and first steps. `IDEA.md` is the originating idea. `CV Examples/` holds three earlier `vitae` CV projects used as style references and as the seed for the data files.

## Layout (planned)

```
data/           structured CV content, one file per section
CV Examples/    earlier vitae (R Markdown + LaTeX) CVs: style references and seed content
PLAN.md         the implementation plan
IDEA.md         the originating idea, snapshot from the Idea Console
idea/idea.json  the same idea as JSON
CLAUDE.md       conventions for Claude sessions in this repo
```
