"""Pydantic models for the bank and archetypes.

Scheme A, see docs/decisions/2026-11-23-bank-schema.md.

Where each rule lives, from cheapest to most specific:
- type: what the annotation alone says (required, `date`, `list[str]`, optional `| None`);
- field: a `Field(...)` constraint on one value (e.g. non-empty string);
- model: a `model_validator` looking at several fields of one model;
- Bank-level: rules that need the whole bank (unique ids, tags that exist).
"""

from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Field level: a string that cannot be empty. Reused for every translatable string.
NonEmptyStr = Annotated[str, Field(min_length=1)]


class Strict(BaseModel):
    """Base of every model: unknown keys are errors (catches typos like `levl`)."""

    model_config = ConfigDict(extra="forbid")


class Text(Strict):
    """A translatable string: both `fr` and `en` are required and non-empty."""

    fr: NonEmptyStr
    en: NonEmptyStr


class Skill(Strict):
    """A skill: plain `id`, a `label` and a `category` used to group skills. No levels."""

    id: NonEmptyStr
    label: Text
    category: NonEmptyStr


class Bullet(Strict):
    """One verified claim: `id`, `tags` (skill ids) and `text` (FR and EN)."""

    id: NonEmptyStr
    tags: list[str]
    text: Text


class Experience(Strict):
    """A job with its nested bullets. Dates are full YYYY-MM-DD."""

    id: NonEmptyStr
    org: NonEmptyStr
    role: Text
    start: date  # type level: `date` rejects "2022-03"; required because no default
    end: date | None = None  # `| None = None`: omitted for an ongoing role
    bullets: list[Bullet]


class Project(Strict):
    """A project with its nested bullets (a bullet belongs to a job or a project, never both)."""

    id: NonEmptyStr
    name: NonEmptyStr
    bullets: list[Bullet]


class Bank(Strict):
    """The whole `bank.yaml`."""

    skills: list[Skill]
    experiences: list[Experience]
    projects: list[Project]

    def bullets(self) -> list[Bullet]:
        """Return every bullet of every job, then every project, in file order."""
        owners: list[Experience | Project] = [*self.experiences, *self.projects]
        return [b for owner in owners for b in owner.bullets]

    @model_validator(mode="after")
    def _check_ids_and_tags(self) -> Self:
        # Bank-level rules: they compare entries with each other, so no single field or
        # nested model can enforce them.
        # Rule 1: skill ids are unique.
        skill_ids = [s.id for s in self.skills]
        _reject_duplicates(skill_ids, "skill")
        # Rule 2: bullet ids are unique across all jobs and projects (not only within one).
        _reject_duplicates([b.id for b in self.bullets()], "bullet")
        # Rule 3: every bullet tag is an existing skill id.
        known = set(skill_ids)
        for bullet in self.bullets():
            unknown = [t for t in bullet.tags if t not in known]
            if unknown:
                raise ValueError(f"bullet {bullet.id!r} has unknown skill tag(s): {unknown}")
        return self

    def check_archetype(self, archetype: "Archetype") -> None:
        """Raise ValueError naming the id if `archetype` references an id missing from this bank.

        Ids inside `{add}` deltas count too. Done here, not in Archetype, because an archetype
        alone cannot know which ids exist.
        """
        bullet_ids = {b.id for b in self.bullets()}
        skill_ids = {s.id for s in self.skills}
        project_ids = {p.id for p in self.projects}
        checks = [
            ("bullet", _referenced_ids(archetype.bullets), bullet_ids),
            ("skill", archetype.skills_order or [], skill_ids),
            ("project", archetype.projects or [], project_ids),
        ]
        for kind, referenced, known in checks:
            for ref in referenced:
                if ref not in known:
                    raise ValueError(
                        f"archetype {archetype.id!r} references unknown {kind} id {ref!r}"
                    )


def _reject_duplicates(ids: list[str], kind: str) -> None:
    """Raise ValueError naming the first id that appears twice."""
    seen: set[str] = set()
    for id_ in ids:
        if id_ in seen:
            raise ValueError(f"duplicate {kind} id: {id_!r}")
        seen.add(id_)


class ListDelta(Strict):
    """An edit of an inherited list: optional `add` and `remove` lists."""

    add: list[str] = []  # pydantic copies mutable defaults, so [] is safe here
    remove: list[str] = []


def _referenced_ids(value: "list[str] | ListDelta | None") -> list[str]:
    """Ids a plain list or a delta points to (`add` only: `remove` may name inherited ids)."""
    if value is None:
        return []
    if isinstance(value, ListDelta):
        return value.add
    return value


class Archetype(Strict):
    """A resume preset.

    `bullets` and `signals` accept a plain list (replaces the parent's) or a ListDelta (edits
    it). Inheritance is resolved by the loader, not here.
    """

    id: NonEmptyStr
    extends: str | None = None
    # Every field below defaults to None ("not set") so a variant can omit what it inherits;
    # the model validator then demands them for a root archetype.
    description: str | None = None
    headline: Text | None = None
    skills_order: list[str] | None = None
    bullets: list[str] | ListDelta | None = None
    projects: list[str] | None = None
    signals: list[str] | ListDelta | None = None

    @model_validator(mode="after")
    def _root_sets_every_field(self) -> Self:
        # Rule: a root archetype (no `extends`) has no parent to inherit from, so it must
        # set every field. A variant may set only the differences.
        if self.extends is None:
            missing = [
                name
                for name in (
                    "description",
                    "headline",
                    "skills_order",
                    "bullets",
                    "projects",
                    "signals",
                )
                if getattr(self, name) is None
            ]
            if missing:
                raise ValueError(f"root archetype {self.id!r} must set: {missing}")
        return self
