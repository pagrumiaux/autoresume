#set page(paper: "a4", margin: (x: 1.5cm, y: 1.5cm))
#set text(font: "Libertinus Serif", size: 10pt)
#set par(leading: 0.55em)
#let accent = rgb("#1f4e79")
#show heading.where(level: 1): it => block(above: 0.9em, below: 0.4em)[
  #set text(size: 11pt, weight: "bold", fill: accent)
  #it.body
]

#text(size: 22pt, weight: "bold", fill: accent)[Jane Doe] \
#text(size: 12pt)[Data Engineer]
#v(0.3em)

#grid(
  columns: (5.2cm, 1fr), column-gutter: 0.8cm,
  [
    = Contact
    Lyon, France \
    jane.doe\@example.com \
    +33 6 00 00 00 00 \
    github.com/janedoe

    = Skills
    *Languages* \ Python, SQL, Scala, Bash

    *Tools* \ Spark, Kafka, Airflow, dbt, Docker, Terraform

    = Languages
    French (native) \ English (fluent) \ German (basic)

    = Education
    *MSc Computer Science* \ Université Example, 2017

    *BSc Mathematics* \ Université Example, 2015
  ],
  [
    = Summary
    Data engineer with six years of experience building reliable batch and streaming pipelines, improving data quality and mentoring junior colleagues.

    = Experience
    *Senior Data Engineer*, Acme Analytics #h(1fr) 2021 - Present
    - Designed an event pipeline processing 40 million records per day with Kafka and Spark.
    - Reduced nightly batch runtime from five hours to ninety minutes by repartitioning large tables.
    - Introduced automated data quality checks that caught schema drift before reaching dashboards.

    *Data Engineer*, Globex Logistics #h(1fr) 2018 - 2021
    - Built an Airflow platform orchestrating more than two hundred daily jobs for finance and operations.
    - Migrated an on-premise warehouse to a cloud warehouse with no reporting downtime.
    - Mentored three junior engineers and ran weekly code review sessions.

    *Software Intern*, Initech #h(1fr) 2017
    - Wrote Python tools to validate customer exports and documented them for the support team.
  ],
)
