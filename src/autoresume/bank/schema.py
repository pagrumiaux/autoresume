"""Pydantic models for the bank and archetypes.

Scheme A, see docs/decisions/2026-11-23-bank-schema.md. Stubs only: the user writes the fields
and validators.
"""

from pydantic import BaseModel


class Text(BaseModel):
    """A translatable string.

    TODO(PA): fields `fr: str` and `en: str`, both required and non-empty.
    """


class Skill(BaseModel):
    """A skill: plain `id`, a `label` (Text) and a `category` used to group skills. No levels.

    TODO(PA): fields and validation (unknown keys such as `level` are rejected).
    """


class Bullet(BaseModel):
    """One verified claim: `id`, `tags` (skill ids) and `text` (Text with FR and EN).

    TODO(PA): fields and validation.
    """


class Experience(BaseModel):
    """A job: `id`, `org`, `role` (Text), `start` (date), optional `end` (date, omitted if
    ongoing) and its nested `bullets`.

    TODO(PA): fields and validation. Dates are full YYYY-MM-DD.
    """


class Project(BaseModel):
    """A project: `id`, `name` and its nested `bullets`.

    A bullet belongs to a job or a project, never both.

    TODO(PA): fields and validation.
    """


class Bank(BaseModel):
    """The whole `bank.yaml`: `skills`, `experiences`, `projects`.

    Expected behaviour: skill ids and bullet ids are unique (bullet ids across jobs and projects),
    every bullet tag is an existing skill id, `bullets()` flattens jobs then projects, and
    `check_archetype` rejects an archetype that references an unknown bullet, skill or project id.

    TODO(PA): fields, model validators, `bullets()` and `check_archetype()`.
    """

    def bullets(self) -> list[Bullet]:
        """Return every bullet of every job, then every project, in file order.

        TODO(PA): implement.
        """
        raise NotImplementedError

    def check_archetype(self, archetype: "Archetype") -> None:
        """Raise ValueError naming the id if `archetype` references an id missing from this bank.

        Ids inside `{add}` deltas count too.

        TODO(PA): implement.
        """
        raise NotImplementedError


class ListDelta(BaseModel):
    """An edit of an inherited list: optional `add` and `remove` lists.

    TODO(PA): fields.
    """


class Archetype(BaseModel):
    """A resume preset.

    Fields: `id`, optional `extends`, `description`, `headline` (Text), `skills_order`, `bullets`,
    `projects`, free-text `signals`. `bullets` and `signals` accept a plain list (replaces the
    parent's) or a ListDelta (edits it). A root archetype (no `extends`) must set every field; a
    variant may set only the differences. Inheritance is resolved by the loader, not here.

    TODO(PA): fields and validation.
    """
