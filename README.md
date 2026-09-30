# CrumpCV

A CV maintained as a Quarto project. The content lives in structured data files, and Quarto renders it to:

- **PDF** for sending and posting
- **Word** for institutions that want an editable file
- **JSON** for the personal website

New entries can be added by describing them to Claude in chat.

## Status

Just seeded. See `IDEA.md` for the idea and its open questions. The next step is to settle those questions and write `PLAN.md`.

## Layout (planned)

```
data/           structured CV content, one file per section
IDEA.md         the originating idea, snapshot from the Idea Console
idea/idea.json  the same idea as JSON
CLAUDE.md       conventions for Claude sessions in this repo
```
