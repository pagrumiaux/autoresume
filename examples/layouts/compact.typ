#set page(paper: "a4", margin: (x: 1.4cm, y: 1.2cm))
#set text(font: "Libertinus Serif", size: 9.5pt)
#set par(leading: 0.5em)
#let rule(title) = block(above: 0.8em, below: 0.4em)[
  #grid(
    columns: (2.6cm, 1fr),
    text(weight: "bold", size: 9.5pt, upper(title)),
    align(horizon, line(length: 100%, stroke: 0.4pt + gray)),
  )
]
#let job(dates, title, bullets) = grid(
  columns: (2.6cm, 1fr), row-gutter: 0.3em,
  text(fill: gray.darken(30%))[#dates],
  [*#title* #for b in bullets [- #b]],
)

#text(size: 18pt, weight: "bold")[Jane Doe] #h(0.5em) #text(size: 11pt)[Data Engineer] \
Lyon, France | jane.doe\@example.com | +33 6 00 00 00 00 | github.com/janedoe

#rule("Profile")
Data engineer with six years of experience building reliable batch and streaming pipelines, improving data quality and mentoring junior colleagues in small product teams.

#rule("Experience")
#job("2021 - Present", "Senior Data Engineer, Acme Analytics", (
  "Designed an event pipeline processing 40 million records per day with Kafka and Spark.",
  "Reduced nightly batch runtime from five hours to ninety minutes by repartitioning large tables.",
  "Introduced automated data quality checks that caught schema drift before reaching dashboards.",
))
#v(0.4em)
#job("2018 - 2021", "Data Engineer, Globex Logistics", (
  "Built an Airflow platform orchestrating more than two hundred daily jobs for finance and operations.",
  "Migrated an on-premise warehouse to a cloud warehouse with no reporting downtime.",
  "Mentored three junior engineers and ran weekly code review sessions.",
))
#v(0.4em)
#job("2017", "Software Intern, Initech", (
  "Wrote Python tools to validate customer exports and documented them for the support team.",
))

#rule("Education")
#grid(
  columns: (2.6cm, 1fr), row-gutter: 0.3em,
  [2015 - 2017], [*MSc Computer Science*, Université Example],
  [2012 - 2015], [*BSc Mathematics*, Université Example],
)

#rule("Skills")
#grid(
  columns: (2.6cm, 1fr), row-gutter: 0.3em,
  [Languages], [Python, SQL, Scala, Bash],
  [Tools], [Spark, Kafka, Airflow, dbt, Docker, Terraform],
  [Spoken], [French (native), English (fluent), German (basic)],
)
