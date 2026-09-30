// CV classic: a Typst reproduction of the 2024 formatted CV.
// Bold small-caps section titles with a rule, two-column contact header, left date column,
// numbered lists with hanging indent. Fonts: Source Sans Pro (bundled).

#let cv(
  title: [Curriculum Vitae],
  subtitle: none,
  contact-left: (),
  contact-right: (),
  date: none,
  accent: rgb("#000000"),
  font: "Source Sans Pro",
  fontsize: 10.5pt,
  body,
) = {
  set document(title: title)
  set page(
    paper: "us-letter",
    margin: (x: 0.9in, top: 0.8in, bottom: 0.8in),
    header: context {
      if counter(page).get().first() > 1 {
        set text(size: 8.5pt, fill: luma(110))
        grid(columns: (1fr, auto), title + [ | CV], if date != none { date })
      }
    },
    footer: context {
      set text(size: 8.5pt, fill: luma(110))
      align(center, counter(page).display("1"))
    },
  )
  set text(font: font, size: fontsize, lang: "en")
  set par(justify: false, leading: 0.5em, spacing: 0.75em)

  show heading.where(level: 1): it => {
    block(width: 100%, above: 1.15em, below: 0.55em, breakable: false,
      stack(dir: ttb, spacing: 0.3em,
        text(size: fontsize + 0.5pt, weight: "bold", fill: accent, tracking: 0.04em, upper(it.body)),
        line(length: 100%, stroke: 0.6pt + accent),
      ))
  }
  show heading.where(level: 2): it => {
    block(above: 0.9em, below: 0.4em, text(size: fontsize, weight: "bold", it.body))
  }
  show heading.where(level: 3): it => {
    block(above: 0.7em, below: 0.3em, text(size: fontsize, weight: "semibold", style: "italic", it.body))
  }
  show link: it => text(fill: accent.darken(20%), it)

  // Header block
  block(below: 1.1em, {
    text(size: fontsize + 5pt, weight: "bold", title)
    if subtitle != none { text(size: fontsize + 5pt, weight: "bold", [ | ] + subtitle) }
    v(0.5em)
    grid(
      columns: (1fr, 1fr),
      gutter: 1em,
      contact-left.join(linebreak()),
      contact-right.join(linebreak()),
    )
  })
  body
}

// One row with a narrow left column (dates, names) and a wide right column.
#let cv-row(left, right, left-width: 1.15in) = {
  grid(columns: (left-width, 1fr), column-gutter: 0.8em, row-gutter: 0.35em, left, right)
}

// Several rows sharing one left-column width, kept together where possible.
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
