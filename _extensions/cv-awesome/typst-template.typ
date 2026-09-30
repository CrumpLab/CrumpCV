// CV awesome: a Typst take on Awesome-CV. Roboto, centred name with light/bold weights,
// red accent on the first letters of each section title, thin rules. Fonts bundled.

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
  accent: rgb("#DC3522"),
  font: "Roboto",
  fontsize: 10pt,
  body,
) = {
  set document(title: title)
  set page(
    paper: "us-letter",
    margin: (x: 0.85in, top: 0.75in, bottom: 0.75in),
    footer: context {
      set text(size: 8pt, fill: luma(120), tracking: 0.08em)
      grid(columns: (1fr, 1fr, 1fr),
        align(left, if date != none { upper(date) }),
        align(center, upper(first-name + [ ] + last-name + [ · Curriculum Vitae])),
        align(right, counter(page).display("1")))
    },
  )
  set text(font: font, size: fontsize, lang: "en", fill: luma(30))
  set par(justify: false, leading: 0.5em, spacing: 0.7em)

  show heading.where(level: 1): it => {
    let s = to-string(it.body)
    block(width: 100%, above: 1.3em, below: 0.6em, breakable: false,
      stack(dir: ttb, spacing: 0.3em,
        text(size: fontsize + 5pt, weight: "bold", tracking: 0.01em,
          text(fill: accent, s.slice(0, calc.min(3, s.len()))) + s.slice(calc.min(3, s.len()))),
        line(length: 100%, stroke: 0.6pt + luma(60)),
      ))
  }
  show heading.where(level: 2): it => {
    block(above: 0.9em, below: 0.4em, text(size: fontsize + 1pt, weight: "bold", fill: luma(50), it.body))
  }
  show heading.where(level: 3): it => {
    block(above: 0.7em, below: 0.3em, text(size: fontsize, weight: "medium", style: "italic", fill: luma(80), it.body))
  }
  show link: it => text(fill: luma(30), it)

  // Header: centred name, position, one-line contact
  align(center, block(below: 1.2em, {
    text(size: 28pt, weight: "light", first-name) + text(size: 28pt, weight: "bold", [ ] + last-name)
    v(0.2em)
    if position != none { text(size: 9pt, fill: accent, weight: "medium", tracking: 0.1em, upper(position)) }
    if affiliation != none { linebreak(); text(size: 9pt, style: "italic", fill: luma(90), affiliation) }
    v(0.4em)
    text(size: 8.5pt, fill: luma(70), (contact-left.slice(2) + contact-right).join([ #h(0.4em) | #h(0.4em) ]))
  }))
  body
}
