"""Regression tests for source-backed quest summary selection."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import translate_quest_summaries as translator  # noqa: E402


class WorldQuestSourceTests(unittest.TestCase):
    def write_artifact(self, folder: str, entries: list[dict]) -> Path:
        path = Path(folder) / "world_sources.json"
        path.write_text(json.dumps({"entries": entries}), encoding="utf-8")
        return path

    def test_loads_source_descriptions_by_exact_entry_id(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_artifact(folder, [
                {
                    "id": "quest.world.quest.70001",
                    "description_en": "A sufficiently long English quest summary.",
                }
            ])
            sources = translator.load_world_source_descriptions(path)
        self.assertEqual(
            sources["quest.world.quest.70001"],
            "A sufficiently long English quest summary.",
        )

    def test_ignores_title_only_source_strings(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_artifact(folder, [
                {"id": "quest.world.quest.1", "description_en": "Short title"}
            ])
            sources = translator.load_world_source_descriptions(path)
        self.assertEqual(sources, {})

    def test_world_quest_uses_exact_id_match(self):
        sources = {"quest.world.quest.1": "A source-backed World Quest description."}
        entry = {
            "id": "quest.world.quest.1",
            "quest_type": "world",
            "node_type": "quest",
        }
        self.assertEqual(
            translator.source_text(entry, sources),
            "A source-backed World Quest description.",
        )

    def test_archon_quest_does_not_borrow_world_source(self):
        sources = {"quest.world.quest.1": "A source-backed World Quest description."}
        entry = {
            "id": "quest.archon.quest.1",
            "quest_type": "archon",
            "node_type": "quest",
        }
        self.assertIsNone(translator.source_text(entry, sources))

    def test_inline_source_fields_take_precedence(self):
        sources = {"quest.world.quest.1": "Artifact source description is long enough."}
        entry = {
            "id": "quest.world.quest.1",
            "quest_type": "world",
            "node_type": "quest",
            "source_description_en": "Inline source description is long enough.",
        }
        self.assertEqual(
            translator.source_text(entry, sources),
            "Inline source description is long enough.",
        )

    def test_conflicting_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.write_artifact(folder, [
                {"id": "quest.world.quest.1", "description_en": "First source description is long."},
                {"id": "quest.world.quest.1", "description_en": "Different source description is long."},
            ])
            with self.assertRaises(RuntimeError):
                translator.load_world_source_descriptions(path)


if __name__ == "__main__":
    unittest.main()
