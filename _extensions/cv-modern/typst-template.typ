// CV modern: a Typst take on moderncv "casual". Blue accent, name large and light with the
// position beneath, contact block at the right, section titles preceded by a short accent rule
// in the date column, dates in grey. Uses Source Sans Pro from the classic extension.

// ---------------------------------------------------------------------------
// Shared entry functions. Every style defines the same names so cv.qmd does
// not care which style is active.

// One row with a narrow left column (dates, names) and a wide right column.
#let cv-row(left, right, left-width: 1.15in) = {
  grid(columns: (left-width, 1fr), column-gutter: 0.8em, row-gutter: 0.35em, left, right)
}

// Several rows sharing one left-column width.
#let cv-rows(rows, left-width: 1.15in) = {
  grid(columns: (left-width, 1fr), column-gutter: 0.8em, row-gutter: 0.4em, ..rows.flatten())
}

// Numbered list with hanging indent; `start` continues numbering across chunks.
#let cv-numbered(items, start: 1) = {
  set enum(numbering: "1", indent: 0em, body-indent: 0.7em, spacing: 0.55em, start: start)
  enum(..items)
}

// Bulleted list.
#let cv-bullets(items) = {
  set list(indent: 0em, body-indent: 0.6em, spacing: 0.5em)
  list(..items)
}

// Simple table with a header row.
#let cv-table(header, rows, widths: auto) = {
  set text(size: 9.5pt)
  table(
    columns: widths,
    stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (bottom: 0.3pt + luma(200)) },
    inset: (x: 0.4em, y: 0.35em),
    align: left + top,
    table.header(..header.map(h => text(weight: "bold", h))),
    ..rows.flatten(),
  )
}

// Content -> plain string (for styling parts of a heading).
#let to-string(c) = {
  if type(c) == str { c }
  else if c.has("text") { c.text }
  else if c.has("children") { c.children.map(to-string).join() }
  else if c.has("body") { to-string(c.body) }
  else if c == [ ] { " " }
  else { "" }
}

// ---------------------------------------------------------------------------
// Page and heading style

#let cv(
  title: [Curriculum Vitae],
  first-name: [],
  last-name: [],
  position: none,
  affiliation: none,
  contact-left: (),
  contact-right: (),
  date: none,
  accent: rgb("#3873B3"),
  font: "Source Sans Pro",
  fontsize: 10.5pt,
  body,
) = {
  set document(title: title)
  set page(
    paper: "us-letter",
    margin: (x: 0.9in, top: 0.8in, bottom: 0.8in),
    footer: context {
      set text(size: 8.5pt, fill: luma(110))
      grid(columns: (1fr, 1fr), align(left, first-name + [ ] + last-name + [ — Curriculum Vitae]), align(right, counter(page).display("1")))
    },
  )
  set text(font: font, size: fontsize, lang: "en")
  set par(justify: false, leading: 0.5em, spacing: 0.7em)

  show heading.where(level: 1): it => {
    block(width: 100%, above: 1.3em, below: 0.6em, breakable: false,
      grid(columns: (1.15in, 1fr), column-gutter: 0.8em, align: (right + horizon, left + horizon),
        line(length: 100%, stroke: 2pt + accent),
        text(size: fontsize + 5pt, weight: "bold", fill: accent, it.body)))
  }
  show heading.where(level: 2): it => {
    block(above: 0.9em, below: 0.4em, text(size: fontsize + 1pt, weight: "bold", fill: accent.darken(30%), it.body))
  }
  show heading.where(level: 3): it => {
    block(above: 0.7em, below: 0.3em, text(size: fontsize, weight: "semibold", style: "italic", it.body))
  }
  show link: it => text(fill: accent, it)

  // Header: name and position left, contact right, rule below
  block(below: 1.2em, width: 100%, {
    grid(columns: (1fr, auto), column-gutter: 1em, align: (left + bottom, right + bottom),
      {
        text(size: 30pt, weight: "light", fill: luma(50), first-name + [ ] + text(weight: "bold", fill: accent, last-name))
        if position != none { linebreak(); text(size: 12pt, style: "italic", fill: luma(90), position) }
      },
      text(size: 9pt, fill: luma(80), (contact-left + contact-right).join(linebreak())))
    v(0.5em)
    line(length: 100%, stroke: 0.5pt + luma(150))
  })
  body
}
