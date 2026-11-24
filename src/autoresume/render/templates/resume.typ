// One-page resume, sidebar layout (P0.S10 direction, examples/layouts/sidebar.typ).
// Input: one JSON string in `sys.inputs.data`, already resolved to one language.
// Every key must be present; null is allowed only for phone, website, github, scholar, music,
// topic and end. Optional: category_titles {category id: heading}, used for skill headings
// (fallback: built-in languages/data titles, then the raw category id).
// The page height is fixed to A4, so overflow is not visible here: the page-count check of
// P0.S12 catches it.
// Keys: lang ("fr"|"en"), name, title, phone, website, github, scholar, music, headline,
// skills [{label, category}], education [{institution, degree, topic, start, end}],
// experiences [{org, role, start, end, bullets}], projects [{name, bullets}].
// Skills of category "soft" are never printed (they only tag bullets for selection).

#let d = json(bytes(sys.inputs.data))
#let fr = d.lang == "fr"

#let titles = if fr {
  (skills: "Compétences", education: "Formation", experience: "Expérience", projects: "Projets",
   present: "Aujourd'hui")
} else {
  (skills: "Skills", education: "Education", experience: "Experience", projects: "Projects",
   present: "Present")
}
#let category-titles = if fr {
  (languages: "Langages", data: "Données")
} else {
  (languages: "Languages", data: "Data")
}

#let accent = rgb("#1f4e79")
#let side-bg = rgb("#eef2f7")
#let muted = rgb("#555555")

#set page(paper: "a4", margin: 0pt)
#set text(font: "Libertinus Serif", size: 9.5pt)
#set par(leading: 0.5em)
#set list(spacing: 0.45em, indent: 0pt, body-indent: 0.5em)

// Sidebar section: title with a short accent bar.
#let side-section(title, body) = block(above: 1.1em, below: 0pt)[
  #text(size: 10pt, weight: "bold", fill: accent)[#upper(title)]
  #v(-0.55em)
  #line(length: 1.2cm, stroke: 1.2pt + accent)
  #v(0.1em)
  #body
]

// Main-column section: accent title with a full-width rule.
#let main-section(title, body) = block(above: 1.1em, below: 0pt)[
  #text(size: 12pt, weight: "bold", fill: accent)[#title]
  #v(-0.5em)
  #line(length: 100%, stroke: 0.5pt + accent)
  #v(0.2em)
  #body
]

#let years(start, end) = if end == none or end == start {
  str(start)
} else {
  str(start) + " – " + str(end)
}

#let link-line(value) = if value != none [#value \ ]

// Identity card: dark block at the top of the sidebar.
#let identity = block(width: 100%, fill: accent, inset: (x: 0.8cm, y: 0.9cm), {
  set text(fill: white)
  set par(leading: 0.55em)
  text(size: 15pt, weight: "bold")[#d.name]
  v(0.2em)
  text(size: 11pt)[#d.title]
  v(0.7em)
  set text(size: 9pt)
  link-line(d.phone)
  link-line(d.website)
  link-line(d.github)
  link-line(d.scholar)
  link-line(d.music)
})

#let given-titles = d.at("category_titles", default: (:))
#let heading-of(key) = given-titles.at(key, default: category-titles.at(key, default: key))
#let visible-skills = d.skills.filter(s => s.category != "soft")
#let skill-groups = {
  let order = ()
  for s in visible-skills {
    if s.category not in order { order.push(s.category) }
  }
  order.map(key => (
    title: heading-of(key),
    labels: visible-skills.filter(s => s.category == key).map(s => s.label),
  ))
}

#let sidebar = {
  identity
  block(inset: (x: 0.8cm, y: 0.2cm), width: 100%)[
    #if skill-groups.len() > 0 {
      side-section(titles.skills)[
        #for g in skill-groups [
          #text(weight: "bold")[#g.title] \
          #text(fill: muted)[#g.labels.join(", ")]
          #v(0.4em)
        ]
      ]
    }
    #if d.education.len() > 0 {
      side-section(titles.education)[
        #for e in d.education [
          #text(weight: "bold")[#e.degree] \
          #e.institution \
          #if e.topic != none [#text(style: "italic")[#e.topic] \ ]
          #text(fill: muted)[#years(e.start, e.end)]
          #v(0.5em)
        ]
      ]
    }
  ]
}

#let main = block(inset: (x: 1cm, y: 1.2cm), width: 100%)[
  #text(size: 13pt, style: "italic", fill: accent)[#d.headline]

  #main-section(titles.experience)[
    #for exp in d.experiences [
      #block(above: 0.9em, below: 0pt, breakable: false, width: 100%,
        stroke: (left: 2pt + accent), inset: (left: 0.35cm, y: 0.1cm))[
        #text(weight: "bold")[#exp.role], #exp.org #h(1fr)
        #text(fill: muted)[#years(exp.start, if exp.end == none { titles.present } else { exp.end })] \
        #for b in exp.bullets [- #b]
      ]
    ]
  ]

  #if d.projects.len() > 0 {
    main-section(titles.projects)[
      #for p in d.projects [
        #block(above: 0.8em, below: 0pt, breakable: false, width: 100%)[
          #text(weight: "bold", fill: accent)[#p.name] \
          #for b in p.bullets [- #b]
        ]
      ]
    ]
  }
]

#grid(
  columns: (6.2cm, 1fr),
  rows: (297mm,),
  grid.cell(fill: side-bg)[#sidebar],
  main,
)
