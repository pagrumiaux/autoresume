# Proposal: bank and archetype schema options

- Task: P0.S4. Status: proposal, for the user to choose from. No schema code is written here.
- Constraints from the decision records: content is YAML with FR and EN variants; agents select,
  order and lightly rephrase; every output sentence traces to a bank entry; archetypes are presets
  (headline FR/EN, skills order, default bullet ids, projects, signals) and variants can inherit.
- All examples use fake data.

## What the schema must support

| Need | Why |
| --- | --- |
| Bullets with stable ids | Archetypes list bullet ids; traceability maps output sentences to ids |
| Skill tags on bullets | The matcher maps job requirements to bullets through tags |
| FR and EN text for each user-facing string | Output language is a render-time choice |
| Dates (start, end or ongoing) | Ordering, and the template needs them |
| Projects | Selectable entries, separate from jobs |
| Archetypes with inheritance | Guard against near-duplicate archetypes |

## Option A: nested and inline bilingual

One `bank.yaml`. Bullets live inside the experience or project they belong to. Every translatable
string is a small `{fr, en}` mapping.

```yaml
# bank.yaml
skills:
  - {id: pytorch, label: {fr: PyTorch, en: PyTorch}, group: ml}
  - {id: dsp, label: {fr: Traitement du signal, en: Signal processing}, group: audio}
experiences:
  - id: acme-2022
    org: Acme Labs
    role: {fr: Ingénieur recherche, en: Research engineer}
    start: 2022-03
    end: 2024-08          # omit when ongoing
    bullets:
      - id: acme-2022-denoiser
        tags: [pytorch, dsp]
        text:
          fr: Conception d'un débruiteur temps réel, latence divisée par deux.
          en: Designed a real-time denoiser, halving latency.
projects:
  - id: toy-synth
    name: Toy Synth
    bullets:
      - {id: toy-synth-vst, tags: [dsp], text: {fr: "...", en: "..."}}
```

```python
# sketch only
class Text(BaseModel): fr: str; en: str
class Bullet(BaseModel): id: str; tags: list[str]; text: Text
class Experience(BaseModel): id: str; org: str; role: Text; start: date; end: date | None; bullets: list[Bullet]
class Bank(BaseModel): skills: list[Skill]; experiences: list[Experience]; projects: list[Project]
```

Dates: PyYAML loads `2022-03` as a string (only `2022-03-01` becomes a date). So `start` and `end`
need either a `YearMonth` type (a string with pattern `^\d{4}-\d{2}$`, or a custom type that parses
it) or full dates in the YAML. This applies to options A, B and C; see open question 4.

- Validation strength: strong at the type level (a missing `fr` fails on load). Cross-references
  (bullet tags exist in `skills`, ids are unique across the whole bank) need a model validator.
- Hand editing: one bullet's two languages sit side by side, so translations are easy to keep
  in sync. Deep nesting makes the file long, and moving a bullet between jobs means cutting text.
- Agent queries: to find a bullet by id or tag, walk experiences and projects. A `bank.bullets()`
  helper flattens it, so queries are simple but need that helper.
- Archetype inheritance: unaffected by this choice; see the shared archetype design below.

## Option B: flat registry with references

Bullets are top-level entries keyed by id. Experiences and projects only list bullet ids, in a
default order. Text is still inline `{fr, en}`.

```yaml
# bank.yaml
skills:
  pytorch: {label: {fr: PyTorch, en: PyTorch}, group: ml}
  dsp: {label: {fr: Traitement du signal, en: Signal processing}, group: audio}
bullets:
  acme-2022-denoiser:
    tags: [pytorch, dsp]
    text: {fr: "...", en: "Designed a real-time denoiser, halving latency."}
experiences:
  - id: acme-2022
    org: Acme Labs
    role: {fr: "...", en: Research engineer}
    start: 2022-03
    end: 2024-08
    bullets: [acme-2022-denoiser]
projects:
  - id: toy-synth
    name: Toy Synth
    bullets: [toy-synth-vst]
```

```python
# sketch only
class Skill(BaseModel): label: Text; group: str
class Bullet(BaseModel): tags: list[SkillId]; text: Text   # id is the dict key
class Bank(BaseModel):
    skills: dict[SkillId, Skill]
    bullets: dict[BulletId, Bullet]       # BulletId = Annotated[str, StringConstraints(pattern=...)]
    experiences: list[Experience]         # Experience.bullets: list[BulletId]
    @model_validator(mode="after")        # every referenced id and tag must exist
    def check_refs(self) -> Self: ...
```

- Validation strength: strongest. A duplicate dict key is caught at load (PyYAML silently keeps the
  last one, so the loader needs a duplicate-key check), and the validator can also flag orphan
  bullets and dangling references.
- Hand editing: bullets are one flat list, easy to grep and reorder, and the same bullet can be
  shared by a job and a project. The cost is indirection: to see a job you jump between two
  sections.
- Agent queries: the best of the three. `bank.bullets[id]` is O(1), tag filtering is a single loop,
  and traceability checks only need the id set.
- Archetype inheritance: archetypes already speak in bullet ids, so they match this layout directly.

## Option C: one file per language, shared ids

`bank.en.yaml` and `bank.fr.yaml` have the same structure and the same ids, with plain strings
instead of `{fr, en}` mappings. A loader merges them, or loads the one needed.

Ownership rule: the EN file owns all structure (ids, tags, dates, ordering); the FR file holds
only ids plus translated strings, and must not repeat tags or dates.

```yaml
# bank.en.yaml (owner)
skills:
  - {id: pytorch, label: PyTorch, group: ml}
  - {id: dsp, label: Signal processing, group: audio}
experiences:
  - id: acme-2022
    org: Acme Labs
    role: Research engineer
    start: 2022-03
    end: 2024-08
    bullets:
      - id: acme-2022-denoiser
        tags: [pytorch, dsp]
        text: Designed a real-time denoiser, halving latency.
projects:
  - id: toy-synth
    name: Toy Synth
    bullets:
      - {id: toy-synth-vst, tags: [dsp], text: Built a VST synth plugin.}
```

```yaml
# bank.fr.yaml (translations only, same ids)
skills:
  - {id: dsp, label: Traitement du signal}     # omitted label falls back to EN
experiences:
  - id: acme-2022
    role: Ingénieur recherche
    bullets:
      - {id: acme-2022-denoiser, text: Conception d'un débruiteur temps réel, latence divisée par deux.}
projects:
  - id: toy-synth
    bullets:
      - {id: toy-synth-vst, text: Création d'un plugin de synthé VST.}
```

```python
# sketch only: two file models, merged into the same in-memory shape as option A
class BankEn(Bank): ...                      # full structure, plain-string text
class BankFr(BaseModel): ...                 # same ids, translated strings only (no tags, no dates)
def merge(en: BankEn, fr: BankFr) -> MergedBank:
    # walk by id; raise on an id in FR but not EN, and on an EN bullet with no FR text
    # (the parity check); build Text(fr=..., en=...) for each string
    ...
```

- Validation strength: weakest by default. Language parity is a cross-file check (same ids, same
  order, same dates), which a loader test must enforce. Dates and tags are duplicated, so they can
  drift apart unless only one file owns them.
- Hand editing: each file reads like a normal resume in one language, and you can fill EN first
  and translate later. Keeping two files in sync is a chore, which is the main risk for effort in
  Phase 0.
- Agent queries: querying one language is trivial and cheap in tokens (an agent never sees the
  other language). Cross-language lookup, such as rephrasing from the FR source, needs the merge.
- Archetype inheritance: unaffected, but archetype headlines then also need a per-language split,
  which doubles that file set.

## Comparison

| | A nested inline | B flat registry | C file per language |
| --- | --- | --- | --- |
| Validation strength | strong, cross-refs by validator | strongest, ids are keys | weakest, parity is a cross-file check |
| Hand editing | long file, translations adjacent | flat bullets, indirection | simple per file, sync chore |
| Agent queries | needs a flatten helper | direct lookup by id and tag | trivial per language, merge for both |
| Reuse of a bullet | copy it | reference it | copy it |

Suggestion: option B. Archetypes and traceability both work on bullet ids, so making ids the
primary keys removes a layer. A and B differ only in where bullets live, so you can start from A and
move to B later; the migration is mostly mechanical, but bullets copied in A to reuse them must be
deduplicated by hand. C is worth choosing only if you expect to write EN and
FR at different times and want to keep them apart.

## Archetypes (shared by all options)

Archetypes are small files that reference bank ids and add presentation choices.

```yaml
# archetypes/audio-ml.yaml
id: audio-ml
description: Audio ML research engineer roles.     # shown to the analyst for scoring
headline: {fr: "...", en: Audio ML research engineer}
skills_order: [pytorch, dsp]                       # skill ids, in display order
bullets: [acme-2022-denoiser]                      # default bullet ids, in display order
projects: [toy-synth]
signals: [speech enhancement, self-supervised, real-time]   # keywords for the analyst
```

```yaml
# archetypes/edge-audio.yaml
id: edge-audio
extends: audio-ml
headline: {fr: "...", en: Embedded audio AI engineer}
bullets:
  add: [acme-2022-quantization]
  remove: [acme-2022-denoiser]
signals:
  add: [embedded, quantization]
```

```python
# sketch only
class Archetype(BaseModel):
    id: str; extends: str | None = None
    headline: Text | None; skills_order: list[SkillId] | None
    bullets: list[BulletId] | ListDelta | None   # ListDelta = {add, remove}
```

Inheritance rules proposed:

- An absent field is inherited. A plain list or value replaces the parent's. An `{add, remove}`
  mapping edits the parent's list. Replacing stays the readable common case, and a small variant is
  a few lines long.
- `extends` is resolved at load time into a flat archetype, so agents never see inheritance. The
  loader rejects cycles and unknown parents, allows one level of depth at first, and checks that
  every id exists in the bank.
- A root archetype must be complete (all fields set); a variant may set only the differences.
- The "show the nearest archetype and offer a variant" step then maps onto this: a variant is the
  nearest archetype plus a diff.

Alternative, rejected for now: full copies with no inheritance. Simpler to validate and read, but
near-duplicates become cheap, which the decision record warns against.

## Proposed file layout

Matches `docs/design.md`; the loader reads `AUTORESUME_DATA_DIR`.

```
autoresume-data/
  bank.yaml              # option A or B (option C: bank.en.yaml + bank.fr.yaml)
  archetypes/
    audio-ml.yaml        # one file per archetype, file name = id
    edge-audio.yaml      # variant, extends: audio-ml
```

If `bank.yaml` grows too big, it could split into `bank/skills.yaml`, `bank/experiences.yaml`,
`bank/projects.yaml` and `bank/bullets.yaml`, with the loader reading the directory. I would not
start that way: git diffs of a single file are fine for a one-person bank.

Fake equivalents for tests and demos go in `tests/fixtures/` and `examples/`, in the same layout.

## Open questions for you

1. A, B or C? (I suggest B.)
2. Is a skill a plain id with a label, or does it need levels and categories now?
3. Are archetype `signals` free text, or tags drawn from the skills list?
4. Dates: `YYYY-MM` strings with a `YearMonth` type (PyYAML does not parse them as dates), or full
   `YYYY-MM-DD` dates? And should `end` be omitted for ongoing roles (above), or be `present`?
5. May a bullet belong to both a job and a project (only B allows it without copying)?
