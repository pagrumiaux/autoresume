#set page(paper: "a4", margin: (x: 1.8cm, y: 1.5cm))
#set text(font: "Libertinus Serif", size: 10pt)
#set par(justify: false, leading: 0.55em)
#show heading.where(level: 1): it => block(above: 1em, below: 0.5em)[
  #set text(size: 11pt, weight: "bold")
  #upper(it.body)
  #v(-0.5em)
  #line(length: 100%, stroke: 0.6pt)
]
#let entry(role, org, dates, bullets) = block(below: 0.7em)[
  *#role*, #org #h(1fr) #dates
  #for b in bullets [- #b]
]

#align(center)[
  #text(size: 20pt, weight: "bold")[Jane Doe] \
  Data Engineer · Lyon, France · jane.doe\@example.com · +33 6 00 00 00 00 · github.com/janedoe
]

= Summary
Data engineer with six years of experience building reliable batch and streaming pipelines, improving data quality and mentoring junior colleagues in small product teams.

= Experience
#entry("Senior Data Engineer", "Acme Analytics", "2021 - Present", (
  "Designed an event pipeline processing 40 million records per day with Kafka and Spark.",
  "Reduced nightly batch runtime from five hours to ninety minutes by repartitioning large tables.",
  "Introduced automated data quality checks that caught schema drift before reaching dashboards.",
))
#entry("Data Engineer", "Globex Logistics", "2018 - 2021", (
  "Built an Airflow platform orchestrating more than two hundred daily jobs for finance and operations.",
  "Migrated an on-premise warehouse to a cloud warehouse with no reporting downtime.",
  "Mentored three junior engineers and ran weekly code review sessions.",
))
#entry("Software Intern", "Initech", "2017", (
  "Wrote Python tools to validate customer exports and documented them for the support team.",
))

= Education
*MSc Computer Science*, Université Example #h(1fr) 2015 - 2017 \
*BSc Mathematics*, Université Example #h(1fr) 2012 - 2015

= Skills
*Languages:* Python, SQL, Scala, Bash. *Tools:* Spark, Kafka, Airflow, dbt, Docker, Terraform. *Spoken:* French (native), English (fluent), German (basic).
