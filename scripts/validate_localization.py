#!/usr/bin/env python3
"""Validate JSON catalogs, Arabic coverage, glossary consistency, and cross-catalog references."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / "localization"
AR_DIR = ROOT / "ar"
ALLOWED_STATUSES = {"draft", "reviewed", "approved", "needs_context", "needs_translation"}
ALLOWED_CATEGORIES = {"character", "weapon", "artifact", "material", "resource", "region", "enemy", "food", "quest", "term"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
ENTITY_REQUIRED = {"id", "category", "source_name", "arabic_name", "translation_status", "source"}
GLOSSARY_REQUIRED = {"id", "source_term", "translation", "status"}
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
ELEMENT_TERMS = {
    "Anemo": "Anemo", "Geo": "Geo", "Electro": "Electro",
    "Dendro": "Dendro", "Hydro": "Hydro", "Pyro": "Pyro", "Cryo": "Cryo",
}
CHARACTER_WEAPON_TERMS = {
    "Sword": "Sword", "Claymore": "Claymore", "Polearm": "Polearm",
    "Bow": "Bow", "Catalyst": "Catalyst",
}
WEAPON_TYPE_TERMS = {
    "WEAPON_SWORD_ONE_HAND": "Sword",
    "WEAPON_CLAYMORE": "Claymore",
    "WEAPON_POLE": "Polearm",
    "WEAPON_BOW": "Bow",
    "WEAPON_CATALYST": "Catalyst",
}
NONCANONICAL_TALENT_TERMS = {
    "هايدرو": re.compile(r"هايدرو"),
    "كريو": re.compile(r"كريو"),
    "ديندرو": re.compile(r"ديندرو"),
    # Keep visual descriptions such as "تيار هوائي"; flag only this damage-label phrase.
    "هوائي (damage label)": re.compile(r"ضررها\s+إلى\s+هوائي"),
}
EXPECTED_CATALOGS = {
    "characters.json", "talents.json", "weapons.json",
    "materials.json", "resources.json", "artifacts.json",
    "quests_archon.json", "quests_world.json", "glossary.json",
}

QUEST_CATALOG_TYPES = {
    "quests_archon.json": "archon",
    "quests_world.json": "world",
}
QUEST_NODE_TYPES = {
    "archon": {"chapter", "act", "quest"},
    "world": {"chapter", "series", "quest"},
}


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.data: dict[str, dict] = {}
        self.entry_count = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def load_catalogs(self) -> None:
        for path in sorted(AR_DIR.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                self.error(f"{path.name}: invalid/unreadable JSON: {exc}")
                continue
            if not isinstance(data, dict):
                self.error(f"{path.name}: top-level JSON value must be an object")
                continue
            entries = data.get("entries")
            if not isinstance(entries, list):
                self.error(f"{path.name}: 'entries' must be an array")
                continue
            self.data[path.name] = data
            self.entry_count += len(entries)
            self.validate_entries(path.name, entries)

        missing = EXPECTED_CATALOGS - self.data.keys()
        for name in sorted(missing):
            self.error(f"Missing expected catalog: ar/{name}")

    def validate_source(self, label: str, sources: object) -> None:
        if not isinstance(sources, list) or not sources:
            self.error(f"{label}: source must be a non-empty array")
            return
        for index, source in enumerate(sources):
            item = f"{label}: source[{index}]"
            if not isinstance(source, dict):
                self.error(f"{item} must be an object")
                continue
            if not isinstance(source.get("name"), str) or not source["name"].strip():
                self.error(f"{item} has no source name")
            url = source.get("url")
            parsed = urlparse(url) if isinstance(url, str) else None
            if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
                self.error(f"{item} has an invalid HTTP(S) URL")

    def validate_entries(self, filename: str, entries: list) -> None:
        seen_ids: set[str] = set()
        is_glossary = filename == "glossary.json"
        required = GLOSSARY_REQUIRED if is_glossary else ENTITY_REQUIRED
        for index, entry in enumerate(entries):
            label = f"ar/{filename}: entry {index + 1}"
            if not isinstance(entry, dict):
                self.error(f"{label} must be an object")
                continue
            missing = required - entry.keys()
            if missing:
                self.error(f"{label} missing fields: {', '.join(sorted(missing))}")
            entity_id = entry.get("id")
            if not isinstance(entity_id, str) or not entity_id.strip():
                self.error(f"{label} has an empty/invalid id")
            elif not ID_RE.fullmatch(entity_id):
                self.error(f"{label} has an id outside the stable lowercase format")
            elif entity_id in seen_ids:
                self.error(f"{label} duplicates id {entity_id}")
            else:
                seen_ids.add(entity_id)

            if is_glossary:
                if not isinstance(entry.get("source_term"), str) or not entry["source_term"].strip():
                    self.error(f"{label} has an empty source_term")
                if not isinstance(entry.get("translation"), str) or not entry["translation"].strip():
                    self.error(f"{label} has an empty translation")
                if entry.get("status") not in ALLOWED_STATUSES:
                    self.error(f"{label} has unsupported glossary status")
                continue

            if not isinstance(entry.get("source_name"), str) or not entry["source_name"].strip():
                self.error(f"{label} has an empty/invalid source_name")
            status = entry.get("translation_status")
            arabic_name = entry.get("arabic_name")
            if status == "needs_translation":
                if not isinstance(arabic_name, str) or arabic_name.strip():
                    self.error(f"{label} needs_translation entries must have an empty arabic_name")
            elif not isinstance(arabic_name, str) or not arabic_name.strip():
                self.error(f"{label} has an empty/invalid arabic_name")
            if entry.get("category") not in ALLOWED_CATEGORIES:
                self.error(f"{label} has an unsupported category")
            if status not in ALLOWED_STATUSES:
                self.error(f"{label} has unsupported translation_status")
            self.validate_source(label, entry.get("source"))
            if isinstance(entry.get("arabic_name"), str) and entry["arabic_name"].strip():
                if not ARABIC_RE.search(entry["arabic_name"]):
                    self.warning(f"{label} Arabic name contains no Arabic-script character")
            if "description_ar" in entry and entry["description_ar"] is not None:
                if not isinstance(entry["description_ar"], str):
                    self.error(f"{label} description_ar must be a string or null")
                elif not entry["description_ar"].strip():
                    self.warning(f"{label} has an empty description_ar")

    def glossary_index(self) -> dict[str, str]:
        glossary = self.data.get("glossary.json", {}).get("entries", [])
        by_source: dict[str, str] = {}
        seen_ids: set[str] = set()
        for index, term in enumerate(glossary):
            if not isinstance(term, dict):
                continue
            source = term.get("source_term")
            translation = term.get("translation")
            if not isinstance(source, str) or not isinstance(translation, str):
                continue
            if source in by_source and by_source[source] != translation:
                self.error(f"Glossary has conflicting translations for source term: {source}")
            elif source in by_source:
                self.error(f"Glossary repeats source term: {source}")
            by_source[source] = translation
        return by_source

    def check_glossary_links(self) -> None:
        terms = self.glossary_index()
        for filename in ("materials.json", "resources.json"):
            for entry in self.data.get(filename, {}).get("entries", []):
                if not isinstance(entry, dict):
                    continue
                source = entry.get("source_name")
                if source in terms and entry.get("arabic_name") != terms[source]:
                    self.error(
                        f"ar/{filename}: {entry.get('id')} disagrees with glossary "
                        f"for {source!r}: {entry.get('arabic_name')!r} != {terms[source]!r}"
                    )
                item_type = entry.get("item_type")
                if item_type and item_type not in terms:
                    self.warning(
                        f"ar/{filename}: item_type {item_type!r} has no glossary entry"
                    )

        for entry in self.data.get("characters.json", {}).get("entries", []):
            if not isinstance(entry, dict):
                continue
            for field, mapping in (
                ("element", ELEMENT_TERMS),
                ("weapon_type", CHARACTER_WEAPON_TERMS),
            ):
                value = entry.get(field)
                if not value:
                    continue
                source_term = mapping.get(value)
                if source_term and source_term not in terms:
                    self.error(f"characters.json: missing glossary term {source_term!r} for {field}")

        for entry in self.data.get("weapons.json", {}).get("entries", []):
            if not isinstance(entry, dict):
                continue
            source_term = WEAPON_TYPE_TERMS.get(entry.get("weapon_type"))
            if source_term and source_term not in terms:
                self.error(f"weapons.json: missing glossary term {source_term!r} for weapon_type")

    def check_talent_elemental_terminology(self) -> None:
        """Reject known non-canonical elemental labels in talent summaries."""
        talents = self.data.get("talents.json", {}).get("entries", [])
        for talent in talents:
            if not isinstance(talent, dict):
                continue
            description = talent.get("description_ar")
            if not isinstance(description, str):
                continue
            for term, pattern in NONCANONICAL_TALENT_TERMS.items():
                if pattern.search(description):
                    self.error(
                        f"talents.json: {talent.get('id', 'no id')} uses non-canonical "
                        f"elemental term {term!r} in description_ar"
                    )

    def check_talent_review_notes(self) -> None:
        """Reject stale editorial notes that contradict populated Arabic summaries."""
        talents = self.data.get("talents.json", {}).get("entries", [])
        stale_marker = "الوصف لم يُترجم بعد"
        for talent in talents:
            if not isinstance(talent, dict):
                continue
            notes = talent.get("review_notes")
            summary = talent.get("description_ar")
            if (
                isinstance(notes, str) and stale_marker in notes
                and isinstance(summary, str) and summary.strip()
            ):
                self.error(
                    f"talents.json: {talent.get('id', 'no id')} has a stale review note "
                    "claiming its populated Arabic summary is not translated"
                )

    def check_talent_references(self) -> None:
        characters = self.data.get("characters.json", {}).get("entries", [])
        talents = self.data.get("talents.json", {}).get("entries", [])
        character_by_id = {
            item.get("id"): item for item in characters
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        for index, talent in enumerate(talents):
            if not isinstance(talent, dict):
                continue
            label = f"talents.json: entry {index + 1} ({talent.get('id', 'no id')})"
            character_id = talent.get("character_id")
            character = character_by_id.get(character_id)
            if character is None:
                self.error(f"{label} references unknown character_id {character_id!r}")
                continue
            expected_name = character.get("arabic_name")
            actual_name = talent.get("character_name_ar")
            # Traveler talent records carry a display suffix not present on the
            # identity record; retain that explicit, documented presentation.
            allowed_names = {expected_name}
            if character_id in {"character.aether", "character.lumine"} and expected_name:
                allowed_names.add(f"{expected_name} (المسافر)")
            if actual_name not in allowed_names:
                self.error(
                    f"{label} character_name_ar does not match characters.json "
                    f"for {character_id}: {actual_name!r}"
                )

    def check_traveler_talent_sets(self) -> None:
        """Require the seven known Traveler elements to have all three talent slots."""
        traveler_id = "character.aether"
        expected_elements = {"Anemo", "Geo", "Electro", "Dendro", "Hydro", "Pyro", "Cryo"}
        expected_types = {"normal", "skill", "burst"}
        expected_slots = {
            (element, talent_type)
            for element in expected_elements
            for talent_type in expected_types
        }
        talents = self.data.get("talents.json", {}).get("entries", [])
        characters = self.data.get("characters.json", {}).get("entries", [])
        traveler_exists = any(
            isinstance(item, dict) and item.get("id") == traveler_id
            for item in characters
        )
        traveler_talents = [
            item for item in talents
            if isinstance(item, dict) and (
                item.get("character_id") == traveler_id
                or (
                    isinstance(item.get("id"), str)
                    and item["id"].startswith(f"{traveler_id}.talent.")
                )
            )
        ]
        # Generic fixtures may omit Traveler; enforce the full matrix whenever
        # the real Traveler record or any Traveler talent exists.
        if not traveler_exists and not traveler_talents:
            return

        found_slots: set[tuple[str, str]] = set()
        for talent in traveler_talents:
            talent_id = talent.get("id", "no id")
            if talent.get("character_id") != traveler_id:
                self.error(
                    f"Traveler talent {talent_id} must reference {traveler_id}"
                )

            element = talent.get("element")
            talent_type = talent.get("talent_type")
            if element not in expected_elements:
                self.error(
                    f"Traveler talent {talent_id} has unsupported element {element!r}"
                )
                continue
            if talent_type not in expected_types:
                self.error(
                    f"Traveler talent {talent_id} has unsupported type {talent_type!r}"
                )
                continue

            slot = (element, talent_type)
            expected_id = (
                f"{traveler_id}.talent.{element.lower()}.{talent_type}"
            )
            if talent_id != expected_id:
                self.error(
                    f"Traveler talent ID {talent_id!r} does not match slot "
                    f"{element}/{talent_type}; expected {expected_id!r}"
                )
            if slot in found_slots:
                self.error(
                    f"Traveler has duplicate talent slot {element}/{talent_type}"
                )
            found_slots.add(slot)

        missing_slots = expected_slots - found_slots
        for element, talent_type in sorted(missing_slots):
            self.error(
                f"Traveler is missing talent slot {element}/{talent_type}"
            )

    def check_character_talent_sets(self) -> None:
        """Require normal, skill, and burst talents for every non-Traveler character."""
        expected_types = {"normal", "skill", "burst"}
        characters = self.data.get("characters.json", {}).get("entries", [])
        talents = self.data.get("talents.json", {}).get("entries", [])
        character_ids = {
            item.get("id") for item in characters
            if isinstance(item, dict) and isinstance(item.get("id"), str)
            and item.get("id") != "character.aether"
        }
        found_slots: dict[str, set[str]] = {
            character_id: set() for character_id in character_ids
        }
        prefix_owner: dict[str, str] = {}
        prefix_by_character: dict[str, str] = {}

        for index, talent in enumerate(talents):
            if not isinstance(talent, dict):
                continue
            character_id = talent.get("character_id")
            talent_id = talent.get("id", "no id")

            # Traveler kits have element-specific IDs and are validated separately.
            if character_id == "character.aether" or (
                isinstance(talent_id, str)
                and talent_id.startswith("character.aether.talent.")
            ):
                continue
            if character_id not in character_ids:
                continue

            label = f"talents.json: entry {index + 1} ({talent_id})"
            talent_type = talent.get("talent_type")
            if talent_type not in expected_types:
                self.error(
                    f"{label} has unsupported regular-character talent_type "
                    f"{talent_type!r}; expected normal, skill, or burst"
                )
                continue

            # Character catalog IDs are upstream numeric IDs (e.g. character.10000083),
            # while talent IDs use stable name slugs (e.g. character.lynette.talent.skill).
            # Validate the talent slug independently and enforce one-to-one consistency.
            match = re.fullmatch(
                r"(character\.[a-z0-9][a-z0-9._-]*)\.talent\.(normal|skill|burst)",
                talent_id if isinstance(talent_id, str) else "",
            )
            if not match or match.group(2) != talent_type:
                self.error(
                    f"{label} ID does not match a supported character/talent slot "
                    f"for {talent_type!r}"
                )
            else:
                talent_prefix = match.group(1)
                previous_owner = prefix_owner.get(talent_prefix)
                if previous_owner is not None and previous_owner != character_id:
                    self.error(
                        f"{label} talent ID prefix {talent_prefix!r} is already "
                        f"assigned to {previous_owner}, not {character_id}"
                    )
                else:
                    prefix_owner[talent_prefix] = character_id

                previous_prefix = prefix_by_character.get(character_id)
                if previous_prefix is not None and previous_prefix != talent_prefix:
                    self.error(
                        f"{label} uses inconsistent talent ID prefix for {character_id}; "
                        f"expected {previous_prefix!r}"
                    )
                else:
                    prefix_by_character[character_id] = talent_prefix

            slots = found_slots[character_id]
            if talent_type in slots:
                self.error(
                    f"Character {character_id} has duplicate talent slot {talent_type}"
                )
            slots.add(talent_type)

        for character_id in sorted(character_ids):
            missing = expected_types - found_slots[character_id]
            for talent_type in sorted(missing):
                self.error(
                    f"Character {character_id} is missing talent slot {talent_type}"
                )

    def check_quest_catalogs(self) -> None:
        """Validate quest-specific types, stable IDs, hierarchy, and prerequisites."""
        for filename, expected_type in QUEST_CATALOG_TYPES.items():
            entries = self.data.get(filename, {}).get("entries", [])
            by_id: dict[str, dict] = {}
            source_ids: dict[tuple[str, str], str] = {}
            parent_graph: dict[str, list[str]] = {}
            prerequisite_graph: dict[str, list[str]] = {}

            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    continue
                label = f"ar/{filename}: entry {index + 1}"
                entity_id = entry.get("id")
                node_type = entry.get("node_type")
                source_id = entry.get("source_quest_id")

                if entry.get("category") != "quest":
                    self.error(f"{label} category must be 'quest'")
                if entry.get("quest_type") != expected_type:
                    self.error(
                        f"{label} quest_type {entry.get('quest_type')!r} "
                        f"does not match catalog type {expected_type!r}"
                    )
                if not isinstance(node_type, str) or node_type not in QUEST_NODE_TYPES[expected_type]:
                    self.error(
                        f"{label} has unsupported node_type {node_type!r} "
                        f"for {expected_type} catalog"
                    )
                if not isinstance(entity_id, str) or not re.fullmatch(
                    rf"quest\.{expected_type}\.[a-z0-9][a-z0-9._-]*", entity_id
                ):
                    self.error(f"{label} has an invalid quest ID for {expected_type}")
                else:
                    by_id[entity_id] = entry

                if not isinstance(source_id, str) or not source_id.strip():
                    self.error(f"{label} has no source_quest_id")
                elif isinstance(node_type, str):
                    key = (node_type, source_id)
                    if key in source_ids:
                        self.error(
                            f"{label} duplicates source_quest_id {source_id!r} "
                            f"for node_type {node_type!r}"
                        )
                    elif isinstance(entity_id, str):
                        source_ids[key] = entity_id

                parent_id = entry.get("parent_id")
                if parent_id is not None:
                    if not isinstance(parent_id, str) or not parent_id:
                        self.error(f"{label} parent_id must be a non-empty string or null")
                    elif isinstance(entity_id, str):
                        parent_graph[entity_id] = [parent_id]

                prerequisites = entry.get("prerequisite_ids", [])
                if not isinstance(prerequisites, list):
                    self.error(f"{label} prerequisite_ids must be an array")
                else:
                    valid_prerequisites = [
                        value for value in prerequisites
                        if isinstance(value, str) and value
                    ]
                    if len(valid_prerequisites) != len(prerequisites):
                        self.error(f"{label} prerequisite_ids contains an invalid ID")
                    if len(set(valid_prerequisites)) != len(valid_prerequisites):
                        self.error(f"{label} prerequisite_ids contains duplicates")
                    if isinstance(entity_id, str):
                        prerequisite_graph[entity_id] = valid_prerequisites

                sequence = entry.get("sequence")
                if sequence is not None and (
                    isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0
                ):
                    self.error(f"{label} sequence must be a non-negative integer or null")
                rank = entry.get("adventure_rank")
                if rank is not None and (
                    isinstance(rank, bool) or not isinstance(rank, int) or rank < 1
                ):
                    self.error(f"{label} adventure_rank must be a positive integer or null")

            for entity_id, entry in by_id.items():
                label = f"ar/{filename}: {entity_id}"
                parent_id = entry.get("parent_id")
                if isinstance(parent_id, str) and parent_id not in by_id:
                    self.error(f"{label} references missing parent_id {parent_id!r}")
                prerequisites = entry.get("prerequisite_ids", [])
                if isinstance(prerequisites, list):
                    for prerequisite_id in prerequisites:
                        if isinstance(prerequisite_id, str) and prerequisite_id not in by_id:
                            self.error(
                                f"{label} references missing prerequisite_id {prerequisite_id!r}"
                            )

            def has_cycle(graph: dict[str, list[str]]) -> bool:
                state: dict[str, int] = {}

                def visit(node: str) -> bool:
                    if state.get(node) == 1:
                        return True
                    if state.get(node) == 2:
                        return False
                    state[node] = 1
                    for neighbor in graph.get(node, []):
                        if neighbor in by_id and visit(neighbor):
                            return True
                    state[node] = 2
                    return False

                return any(visit(node) for node in by_id if state.get(node, 0) == 0)

            if has_cycle(parent_graph):
                self.error(f"ar/{filename} contains a parent hierarchy cycle")
            if has_cycle(prerequisite_graph):
                self.error(f"ar/{filename} contains a prerequisite cycle")

    def check_global_ids(self) -> None:
        owners: dict[str, str] = {}
        for filename, data in self.data.items():
            for entry in data.get("entries", []):
                if not isinstance(entry, dict):
                    continue
                entity_id = entry.get("id")
                if not isinstance(entity_id, str):
                    continue
                if entity_id in owners:
                    self.error(
                        f"ID {entity_id!r} is shared by {owners[entity_id]} and ar/{filename}"
                    )
                else:
                    owners[entity_id] = f"ar/{filename}"

    def run(self) -> int:
        self.load_catalogs()
        if "glossary.json" in self.data:
            self.check_glossary_links()
        if "characters.json" in self.data and "talents.json" in self.data:
            self.check_talent_references()
            self.check_talent_elemental_terminology()
            self.check_talent_review_notes()
            self.check_traveler_talent_sets()
            self.check_character_talent_sets()
        self.check_quest_catalogs()
        self.check_global_ids()

        print(
            f"Checked {len(self.data)} Arabic JSON catalogs and "
            f"{self.entry_count} records."
        )
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for message in self.warnings:
                print(f"  WARN: {message}")
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for message in self.errors:
                print(f"  ERROR: {message}")
            return 1
        print("PASS: JSON structure, IDs, source metadata, glossary links, and talent references.")
        return 0


if __name__ == "__main__":
    sys.exit(Validator().run())
