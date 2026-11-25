"""Tests for archetype inheritance resolved by `load_bank` (B-archetype-inheritance).

Contract: every archetype `load_bank` returns has every field set; `bullets` and `signals` are
plain lists (no ListDelta); `extends` stays set. A field left out takes the parent's value, a
plain list replaces it, a ListDelta edits the parent's resolved list (remove first, then append
the `add` items not already present). Chains resolve parent-first; a cycle raises BankLoadError
naming a file of the cycle.
"""

from pathlib import Path

import pytest

from autoresume.bank.loader import BankLoadError, load_bank
from autoresume.bank.schema import Archetype, ListDelta
from autoresume.render.render import _build_data

BANK_YAML = """\
skills:
  - id: pytorch
    label: {fr: PyTorch, en: PyTorch}
    category: ml
education: []
experiences:
  - id: acme-2022
    org: Acme Labs
    role: {fr: Ingénieur, en: Engineer}
    start: 2022-03-01
    end: 2024-08-01
    bullets:
      - id: b1
        tags: [pytorch]
        text: {fr: Un., en: One.}
      - id: b2
        tags: [pytorch]
        text: {fr: Deux., en: Two.}
      - id: b3
        tags: [pytorch]
        text: {fr: Trois., en: Three.}
      - id: b4
        tags: [pytorch]
        text: {fr: Quatre., en: Four.}
projects:
  - id: toy-synth
    name: Toy Synth
    bullets:
      - id: p1
        tags: [pytorch]
        text: {fr: Synthé., en: Synth.}
"""

ROOT = """\
id: root
description: Root archetype
headline: {fr: Racine, en: Root}
skills_order: [pytorch]
bullets: [b1, b2, b3]
projects: [toy-synth]
signals: [s1, s2, s3]
"""


def make_bank(tmp_path: Path, **archetypes: str) -> Path:
    """Write the bank and one archetype file per keyword (file name = key, `_` -> `-`)."""
    (tmp_path / "bank.yaml").write_text(BANK_YAML, encoding="utf-8")
    (tmp_path / "archetypes").mkdir()
    for name, content in archetypes.items():
        (tmp_path / "archetypes" / f"{name.replace('_', '-')}.yaml").write_text(
            content, encoding="utf-8"
        )
    return tmp_path


def variant(id_: str, extends: str, body: str = "") -> str:
    """YAML of a variant archetype with `body` appended."""
    return f"id: {id_}\nextends: {extends}\n{body}"


def test_omitted_fields_inherit_the_parents_value(tmp_path):
    make_bank(tmp_path, root=ROOT, child=variant("child", "root"))
    _, archetypes = load_bank(tmp_path)
    child, root = archetypes["child"], archetypes["root"]
    assert child.description == root.description
    assert child.headline == root.headline
    assert child.skills_order == ["pytorch"]
    assert child.bullets == ["b1", "b2", "b3"]
    assert child.projects == ["toy-synth"]
    assert child.signals == ["s1", "s2", "s3"]


def test_own_scalar_fields_win_over_the_parent(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        child=variant("child", "root", "description: Mine\nprojects: []\nskills_order: []\n"),
    )
    child = load_bank(tmp_path)[1]["child"]
    assert child.description == "Mine"
    assert child.projects == []
    assert child.skills_order == []


def test_plain_list_replaces_the_parents_list(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        child=variant("child", "root", "bullets: [b4]\nsignals: [other]\n"),
    )
    child = load_bank(tmp_path)[1]["child"]
    assert child.bullets == ["b4"]
    assert child.signals == ["other"]


def test_delta_removes_then_appends_keeping_parent_order(tmp_path):
    body = "bullets: {remove: [b2], add: [b4]}\nsignals: {add: [s9]}\n"
    make_bank(tmp_path, root=ROOT, child=variant("child", "root", body))
    child = load_bank(tmp_path)[1]["child"]
    assert child.bullets == ["b1", "b3", "b4"]
    assert child.signals == ["s1", "s2", "s3", "s9"]


def test_delta_add_skips_items_already_present(tmp_path):
    body = "bullets: {add: [b2, b4, b4]}\n"
    make_bank(tmp_path, root=ROOT, child=variant("child", "root", body))
    assert load_bank(tmp_path)[1]["child"].bullets == ["b1", "b2", "b3", "b4"]


def test_delta_removing_and_adding_the_same_id_moves_it_to_the_end(tmp_path):
    body = "bullets: {remove: [b1], add: [b1]}\n"
    make_bank(tmp_path, root=ROOT, child=variant("child", "root", body))
    assert load_bank(tmp_path)[1]["child"].bullets == ["b2", "b3", "b1"]


def test_delta_removing_an_id_the_parent_lacks_is_ignored(tmp_path):
    make_bank(tmp_path, root=ROOT, child=variant("child", "root", "bullets: {remove: [b4]}\n"))
    assert load_bank(tmp_path)[1]["child"].bullets == ["b1", "b2", "b3"]


def test_empty_delta_inherits_the_parents_list(tmp_path):
    make_bank(tmp_path, root=ROOT, child=variant("child", "root", "bullets: {}\nsignals: {}\n"))
    child = load_bank(tmp_path)[1]["child"]
    assert child.bullets == ["b1", "b2", "b3"]
    assert child.signals == ["s1", "s2", "s3"]


def test_chain_resolves_parent_first_whatever_the_file_order(tmp_path):
    # "a-leaf" sorts before its ancestors, so a naive file-order pass would see unresolved parents.
    make_bank(
        tmp_path,
        a_leaf=variant("a-leaf", "mid", "bullets: {add: [b4]}\n"),
        mid=variant("mid", "root", "bullets: {remove: [b1]}\nprojects: []\n"),
        root=ROOT,
    )
    _, archetypes = load_bank(tmp_path)
    assert archetypes["mid"].bullets == ["b2", "b3"]
    leaf = archetypes["a-leaf"]
    assert leaf.bullets == ["b2", "b3", "b4"]
    assert leaf.projects == []
    assert leaf.signals == ["s1", "s2", "s3"]
    assert leaf.headline == archetypes["root"].headline


def test_chain_with_a_plain_list_in_the_middle_then_a_delta(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        mid=variant("mid", "root", "bullets: [b4, b1]\n"),
        leaf=variant("leaf", "mid", "bullets: {remove: [b4], add: [b2]}\n"),
    )
    archetypes = load_bank(tmp_path)[1]
    assert archetypes["mid"].bullets == ["b4", "b1"]
    assert archetypes["leaf"].bullets == ["b1", "b2"]


@pytest.mark.parametrize("name", ["root", "mid", "leaf"])
def test_every_returned_archetype_is_fully_resolved(tmp_path, name):
    make_bank(
        tmp_path,
        root=ROOT,
        mid=variant("mid", "root", "bullets: {add: [b4]}\nsignals: {remove: [s1]}\n"),
        leaf=variant("leaf", "mid"),
    )
    archetype = load_bank(tmp_path)[1][name]
    assert isinstance(archetype, Archetype)
    assert isinstance(archetype.bullets, list)
    assert isinstance(archetype.signals, list)
    assert not isinstance(archetype.bullets, ListDelta)
    for field in ("description", "headline", "skills_order", "projects"):
        assert getattr(archetype, field) is not None


def test_extends_stays_set_on_the_result(tmp_path):
    make_bank(tmp_path, root=ROOT, child=variant("child", "root"))
    archetypes = load_bank(tmp_path)[1]
    assert archetypes["child"].extends == "root"
    assert archetypes["root"].extends is None


def test_siblings_do_not_affect_each_other_or_the_parent(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        one=variant("one", "root", "bullets: {remove: [b1]}\n"),
        two=variant("two", "root", "bullets: {add: [b4]}\n"),
    )
    archetypes = load_bank(tmp_path)[1]
    assert archetypes["root"].bullets == ["b1", "b2", "b3"]
    assert archetypes["one"].bullets == ["b2", "b3"]
    assert archetypes["two"].bullets == ["b1", "b2", "b3", "b4"]


def test_cycle_raises_naming_a_file_of_the_cycle(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        a=variant("a", "b", "description: A\n"),
        b=variant("b", "a", "description: B\n"),
    )
    with pytest.raises(BankLoadError, match=r"[ab]\.yaml") as exc:
        load_bank(tmp_path)
    assert "cycle" in str(exc.value).lower()


def test_three_cycle_raises_naming_a_file_of_the_cycle(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        a=variant("a", "b", "description: A\n"),
        b=variant("b", "c", "description: B\n"),
        c=variant("c", "a", "description: C\n"),
    )
    with pytest.raises(BankLoadError, match=r"[abc]\.yaml") as exc:
        load_bank(tmp_path)
    assert "cycle" in str(exc.value).lower()


@pytest.mark.parametrize("field", ["bullets", "signals"])
def test_root_archetype_with_a_delta_is_rejected_naming_file(tmp_path, field):
    root = "\n".join(
        f"{field}: {{add: [b1]}}" if line.startswith(f"{field}:") else line
        for line in ROOT.splitlines()
    )
    make_bank(tmp_path, root=root + "\n")
    with pytest.raises(BankLoadError, match=r"root\.yaml") as exc:
        load_bank(tmp_path)
    assert field in str(exc.value)
    assert "root archetype cannot use a delta" in str(exc.value)


def test_root_with_a_delta_is_rejected_even_when_a_child_extends_it(tmp_path):
    root = ROOT.replace("bullets: [b1, b2, b3]", "bullets: {add: [b1]}")
    make_bank(tmp_path, root=root, child=variant("child", "root"))
    with pytest.raises(BankLoadError, match=r"root\.yaml"):
        load_bank(tmp_path)


def test_lists_are_owned_by_each_archetype(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        one=variant("one", "root"),
        two=variant("two", "root", "bullets: [b4]\n"),
        three=variant("three", "root", "bullets: {add: [b4]}\n"),
    )
    archetypes = load_bank(tmp_path)[1]
    archetypes["one"].skills_order.append("mutated")
    archetypes["one"].projects.append("mutated")
    archetypes["one"].bullets.append("mutated")
    archetypes["one"].signals.append("mutated")
    archetypes["two"].bullets.append("mutated")
    archetypes["three"].bullets.append("mutated")
    for other in ("root", "two", "three"):
        assert "mutated" not in archetypes[other].skills_order
        assert "mutated" not in archetypes[other].projects
        assert "mutated" not in archetypes[other].signals
    assert archetypes["root"].bullets == ["b1", "b2", "b3"]
    assert archetypes["two"].bullets == ["b4", "mutated"]
    assert archetypes["three"].bullets == ["b1", "b2", "b3", "b4", "mutated"]


def test_archetype_extending_itself_is_a_cycle(tmp_path):
    make_bank(tmp_path, me=variant("me", "me", "description: Me\n"))
    with pytest.raises(BankLoadError, match=r"me\.yaml") as exc:
        load_bank(tmp_path)
    assert "cycle" in str(exc.value).lower()


def test_render_of_a_delta_variant_has_a_work_section_and_projects(tmp_path):
    make_bank(
        tmp_path,
        root=ROOT,
        child=variant("child", "root", "bullets: {remove: [b1], add: [b4]}\n"),
    )
    bank, archetypes = load_bank(tmp_path)
    data = _build_data(bank, archetypes["child"], "en")
    assert [e["bullets"] for e in data["experiences"]] == [["Two.", "Three.", "Four."]]
    assert [p["name"] for p in data["projects"]] == ["Toy Synth"]
