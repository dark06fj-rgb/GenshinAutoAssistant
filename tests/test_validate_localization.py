"""Regression tests for the Arabic localization catalog validator."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_localization  # noqa: E402


def entity(entity_id: str, category: str, source_name: str, arabic_name: str, **extra):
    return {
        "id": entity_id,
        "category": category,
        "source_name": source_name,
        "arabic_name": arabic_name,
        "translation_status": "draft",
        "source": [{"name": "fixture", "url": "https://example.org/source"}],
        **extra,
    }


def fixture_catalogs():
    return {
        "glossary.json": {"entries": [
            {"id": "term.sword", "source_term": "Sword", "translation": "سيف", "status": "draft"},
            {"id": "term.currency", "source_term": "Currency", "translation": "عملة", "status": "draft"},
        ]},
        "characters.json": {"entries": [
            entity("character.test", "character", "Test", "اختبار",
                   element=None, weapon_type="Sword")
        ]},
        "talents.json": {"entries": [
            entity(f"character.test.talent.{talent_type}", "term",
                   f"Test {talent_type} talent", "موهبة تجريبية",
                   character_id="character.test", character_name_ar="اختبار",
                   talent_type=talent_type)
            for talent_type in ("normal", "skill", "burst")
        ]},
        "weapons.json": {"entries": [
            entity("weapon.test", "weapon", "Test Sword", "سيف تجريبي",
                   weapon_type="WEAPON_SWORD_ONE_HAND")
        ]},
        "materials.json": {"entries": [
            entity("material.test", "material", "Currency", "عملة",
                   item_type="Currency")
        ]},
        "resources.json": {"entries": [
            entity("resource.test", "resource", "Test Plant", "نبات تجريبي",
                   item_type="Currency")
        ]},
        "artifacts.json": {"entries": [
            entity("artifact.test", "artifact", "Test Set", "مجموعة تجريبية")
        ]},
        "quests_archon.json": {"entries": [
            entity(
                "quest.archon.chapter.prologue", "quest", "Prologue",
                "المقدمة", quest_type="archon", node_type="chapter",
                source_quest_id="1001", parent_id=None, prerequisite_ids=[],
            ),
            entity(
                "quest.archon.act.prologue.i", "quest", "Act I",
                "الفصل الأول", quest_type="archon", node_type="act",
                source_quest_id="1001-1", parent_id="quest.archon.chapter.prologue",
                prerequisite_ids=[], sequence=1,
            ),
            entity(
                "quest.archon.quest.wanderers_trail", "quest", "Wanderer's Trail",
                "أثر المتجول", quest_type="archon", node_type="quest",
                source_quest_id="100101", parent_id="quest.archon.act.prologue.i",
                prerequisite_ids=[], sequence=1,
            ),
        ]},
        "quests_world.json": {"entries": [
            entity(
                "quest.world.series.chi_of_yore", "quest", "The Chi of Yore",
                "تشي العصور", quest_type="world", node_type="series",
                source_quest_id="series-chi-of-yore", parent_id=None,
                prerequisite_ids=[],
            ),
            entity(
                "quest.world.quest.the_chi_of_yore", "quest", "The Chi of Yore",
                "تشي العصور", quest_type="world", node_type="quest",
                source_quest_id="quest-chi-of-yore", parent_id="quest.world.series.chi_of_yore",
                prerequisite_ids=[], sequence=1,
            ),
        ]},
    }


def add_traveler_talent_matrix(catalogs):
    catalogs["characters.json"]["entries"].append(
        entity("character.aether", "character", "Aether", "إيثر",
               element=None, weapon_type="Sword")
    )
    for element in ("Anemo", "Geo", "Electro", "Dendro", "Hydro", "Pyro", "Cryo"):
        for talent_type in ("normal", "skill", "burst"):
            catalogs["talents.json"]["entries"].append(
                entity(
                    f"character.aether.talent.{element.lower()}.{talent_type}",
                    "term",
                    f"Aether {element} {talent_type}",
                    "موهبة المسافر",
                    character_id="character.aether",
                    character_name_ar="إيثر (المسافر)",
                    element=element,
                    talent_type=talent_type,
                )
            )
    return catalogs


class ValidatorRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.catalog_dir = Path(self.temp.name)
        self.write_catalogs(fixture_catalogs())

    def tearDown(self):
        self.temp.cleanup()

    def write_catalogs(self, catalogs):
        for path in self.catalog_dir.glob("*.json"):
            path.unlink()
        for name, data in catalogs.items():
            (self.catalog_dir / name).write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )

    def run_validator(self):
        validator = validate_localization.Validator()
        output = io.StringIO()
        with patch.object(validate_localization, "AR_DIR", self.catalog_dir):
            with contextlib.redirect_stdout(output):
                exit_code = validator.run()
        return exit_code, output.getvalue(), validator

    def test_valid_catalogs_pass(self):
        exit_code, output, validator = self.run_validator()
        self.assertEqual(exit_code, 0, output)
        self.assertFalse(validator.errors)

    def test_duplicate_ids_across_catalogs_fail(self):
        catalogs = fixture_catalogs()
        catalogs["weapons.json"]["entries"][0]["id"] = "character.test"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("shared by", output)

    def test_material_glossary_mismatch_fails(self):
        catalogs = fixture_catalogs()
        catalogs["materials.json"]["entries"][0]["arabic_name"] = "نقود"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("disagrees with glossary", output)

    def test_unknown_talent_character_fails(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"][0]["character_id"] = "character.missing"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unknown character_id", output)

    def test_invalid_source_url_fails(self):
        catalogs = fixture_catalogs()
        catalogs["materials.json"]["entries"][0]["source"][0]["url"] = "javascript:alert(1)"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("invalid HTTP(S) URL", output)

    def test_unsupported_category_fails(self):
        catalogs = fixture_catalogs()
        catalogs["artifacts.json"]["entries"][0]["category"] = "unknown"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported category", output)

    def test_missing_expected_catalog_fails(self):
        catalogs = fixture_catalogs()
        del catalogs["artifacts.json"]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("Missing expected catalog", output)

    def test_quest_type_must_match_catalog(self):
        catalogs = fixture_catalogs()
        catalogs["quests_world.json"]["entries"][0]["quest_type"] = "archon"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("does not match catalog type", output)

    def test_needs_translation_allows_blank_arabic_name(self):
        catalogs = fixture_catalogs()
        entry = catalogs["quests_world.json"]["entries"][0]
        entry["arabic_name"] = ""
        entry["translation_status"] = "needs_translation"
        self.write_catalogs(catalogs)
        exit_code, output, validator = self.run_validator()
        self.assertEqual(exit_code, 0, output)
        self.assertFalse(validator.errors)

    def test_blank_arabic_name_requires_needs_translation_status(self):
        catalogs = fixture_catalogs()
        entry = catalogs["quests_world.json"]["entries"][0]
        entry["arabic_name"] = ""
        entry["translation_status"] = "draft"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("empty/invalid arabic_name", output)

    def test_quest_parent_reference_must_exist(self):
        catalogs = fixture_catalogs()
        catalogs["quests_archon.json"]["entries"][2]["parent_id"] = "quest.archon.act.missing"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("references missing parent_id", output)

    def test_quest_prerequisite_reference_must_exist(self):
        catalogs = fixture_catalogs()
        catalogs["quests_world.json"]["entries"][1]["prerequisite_ids"] = [
            "quest.world.quest.missing"
        ]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("references missing prerequisite_id", output)

    def test_quest_parent_cycle_fails(self):
        catalogs = fixture_catalogs()
        catalogs["quests_archon.json"]["entries"][0]["parent_id"] = (
            "quest.archon.act.prologue.i"
        )
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("parent hierarchy cycle", output)

    def test_quest_prerequisite_cycle_fails(self):
        catalogs = fixture_catalogs()
        catalogs["quests_archon.json"]["entries"][1]["prerequisite_ids"] = [
            "quest.archon.quest.wanderers_trail"
        ]
        catalogs["quests_archon.json"]["entries"][2]["prerequisite_ids"] = [
            "quest.archon.act.prologue.i"
        ]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("prerequisite cycle", output)

    def test_duplicate_quest_source_id_for_same_node_type_fails(self):
        catalogs = fixture_catalogs()
        duplicate = dict(catalogs["quests_archon.json"]["entries"][2])
        duplicate["id"] = "quest.archon.quest.another"
        catalogs["quests_archon.json"]["entries"].append(duplicate)
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("duplicates source_quest_id", output)

    def test_quest_catalog_rejects_invalid_node_type(self):
        catalogs = fixture_catalogs()
        catalogs["quests_world.json"]["entries"][0]["node_type"] = "chapter"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported node_type", output)

    def test_quest_validator_handles_malformed_hierarchy_values(self):
        catalogs = fixture_catalogs()
        catalogs["quests_archon.json"]["entries"][0]["node_type"] = ["chapter"]
        catalogs["quests_archon.json"]["entries"][1]["parent_id"] = ["not-an-id"]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported node_type", output)
        self.assertIn("parent_id must be a non-empty string or null", output)


    def test_complete_traveler_seven_element_matrix_passes(self):
        catalogs = add_traveler_talent_matrix(fixture_catalogs())
        self.write_catalogs(catalogs)
        exit_code, output, validator = self.run_validator()
        self.assertEqual(exit_code, 0, output)
        self.assertFalse(validator.errors)

    def test_missing_traveler_talent_slot_fails(self):
        catalogs = add_traveler_talent_matrix(fixture_catalogs())
        catalogs["talents.json"]["entries"] = [
            item for item in catalogs["talents.json"]["entries"]
            if item.get("id") != "character.aether.talent.cryo.burst"
        ]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("Traveler is missing talent slot Cryo/burst", output)

    def test_traveler_talent_must_reference_aether(self):
        catalogs = add_traveler_talent_matrix(fixture_catalogs())
        target = next(
            item for item in catalogs["talents.json"]["entries"]
            if item.get("id") == "character.aether.talent.anemo.skill"
        )
        target["character_id"] = "character.test"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("must reference character.aether", output)

    def test_traveler_talent_rejects_unknown_element(self):
        catalogs = add_traveler_talent_matrix(fixture_catalogs())
        target = next(
            item for item in catalogs["talents.json"]["entries"]
            if item.get("id") == "character.aether.talent.anemo.normal"
        )
        target["element"] = "Quantum"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported element 'Quantum'", output)

    def test_traveler_talent_rejects_duplicate_slot(self):
        catalogs = add_traveler_talent_matrix(fixture_catalogs())
        target = next(
            item for item in catalogs["talents.json"]["entries"]
            if item.get("id") == "character.aether.talent.cryo.burst"
        )
        target["element"] = "Anemo"
        target["talent_type"] = "normal"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("duplicate talent slot Anemo/normal", output)

    def test_complete_regular_character_talent_matrix_passes(self):
        catalogs = fixture_catalogs()
        self.write_catalogs(catalogs)
        exit_code, output, validator = self.run_validator()
        self.assertEqual(exit_code, 0, output)
        self.assertFalse(validator.errors)

    def test_missing_regular_character_talent_slot_fails(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"] = [
            item for item in catalogs["talents.json"]["entries"]
            if item.get("talent_type") != "burst"
        ]
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("Character character.test is missing talent slot burst", output)

    def test_regular_talent_must_reference_matching_character(self):
        catalogs = fixture_catalogs()
        catalogs["characters.json"]["entries"].append(
            entity("character.other", "character", "Other", "آخر",
                   element=None, weapon_type="Sword")
        )
        catalogs["talents.json"]["entries"][0]["character_id"] = "character.other"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("talent ID prefix 'character.test' is already assigned", output)
        self.assertIn("Character character.test is missing talent slot normal", output)
        self.assertIn("Character character.other is missing talent slot", output)

    def test_regular_talent_rejects_unknown_type(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"][0]["talent_type"] = "passive"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("unsupported regular-character talent_type 'passive'", output)

    def test_regular_talent_rejects_duplicate_slot(self):
        catalogs = fixture_catalogs()
        duplicate = dict(catalogs["talents.json"]["entries"][0])
        duplicate["id"] = "character.test.talent.normal.copy"
        catalogs["talents.json"]["entries"].append(duplicate)
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("duplicate talent slot normal", output)

    def test_regular_talent_id_must_match_talent_type(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"][0]["talent_type"] = "skill"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("ID does not match a supported character/talent slot", output)

    def test_stale_review_note_conflicts_with_populated_summary(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"][0]["description_ar"] = (
            "ملخص عربي موجود."
        )
        catalogs["talents.json"]["entries"][0]["review_notes"] = (
            "الوصف لم يُترجم بعد."
        )
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("stale review note", output)

    def test_malformed_json_fails(self):
        (self.catalog_dir / "resources.json").write_text("{broken", encoding="utf-8")
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("invalid/unreadable JSON", output)

    def test_noncanonical_elemental_talent_terms_fail(self):
        for phrase in (
            "ضرر هايدرو",
            "ضرر كريو",
            "موجة ديندرو",
            "تحويل ضررها إلى هوائي",
        ):
            with self.subTest(phrase=phrase):
                catalogs = fixture_catalogs()
                catalogs["talents.json"]["entries"][0]["description_ar"] = phrase
                self.write_catalogs(catalogs)
                exit_code, output, _ = self.run_validator()
                self.assertEqual(exit_code, 1, output)
                self.assertIn("non-canonical elemental term", output)

    def test_descriptive_air_current_is_not_an_element_label(self):
        catalogs = fixture_catalogs()
        catalogs["talents.json"]["entries"][0]["description_ar"] = (
            "ينشئ تياراً هوائياً يرفع الشخصية في الهواء."
        )
        self.write_catalogs(catalogs)
        exit_code, output, validator = self.run_validator()
        self.assertEqual(exit_code, 0, output)
        self.assertFalse(validator.errors)


    def test_source_backed_talent_summary_corrections_remain_draft(self):
        root = Path(__file__).resolve().parents[1]
        catalog_path = root / "localization" / "ar" / "talents.json"
        entries = json.loads(catalog_path.read_text(encoding="utf-8"))["entries"]
        by_id = {entry["id"]: entry for entry in entries}
        expected = {
            "character.beidou.talent.skill": (
                ("عدد مرات تعرضها للهجوم",),
                ("الضرر الذي امتصته",),
            ),
            "character.beidou.talent.burst": (
                ("مقاومة المقاطعة", "تفريغات برق متسلسلة"),
                ("درعاً كهربائياً",),
            ),
            "character.hutao.talent.skill": (
                ("علامة زهر الدم", "ضرر بايرو دورياً"),
                ("تضعف الأعداء",),
            ),
            "character.razor.talent.burst": (
                ("مقاومته للمقاطعة", "مناعة من ضرر حالة الشحن الكهربائي"),
                ("مقاومته الكهربائية ومقاطعة الأعداء له",),
            ),
            "character.noelle.talent.skill": (
                ("فرصة لاستعادة صحة جميع أعضاء الفريق",),
                (),
            ),
            "character.noelle.talent.burst": (
                ("تزيد هجومها بحسب دفاعها",),
                (),
            ),
            "character.ganyu.talent.normal": (
                ("سهماً إكليلياً", "ضرر كرايو واسعاً"),
                ("انفجار جليدي واسع",),
            ),
            "character.ganyu.talent.burst": (
                ("ضرر كرايو", "باستمرار"),
                ("لؤلؤة جليدية",),
            ),
            "character.nahida.talent.normal": (
                ("هجمات دندرو",),
                ("هجمات نباتية",),
            ),
            "character.prune.talent.normal": (
                ("ضربات أنيمو",),
                ("ضربات هوائية",),
            ),
            "character.wanderer.talent.skill": (
                ("ضربات أنيمو",),
                ("ضربات هوائية",),
            ),
            "character.gorou.talent.normal": (
                ("سهم جيو",),
                ("سهم جغرافي",),
            ),
            "character.illuga.talent.burst": (
                ("إنشاءات جيو", "تراكمات إضافية"),
                ("المنشآت الجغرافية",),
            ),
            "character.linnea.talent.normal": (
                ("سهم جيو",),
                ("سهم جغرافي",),
            ),
            "character.navia.talent.skill": (
                ("ضرر جيو", "تخترق الأعداء"),
                ("روسولا الجغرافية",),
            ),
            "character.navia.talent.burst": (
                ("ضرر جيو", "الأعداء القريبين"),
                ("قصفاً مدفعياً جغرافياً",),
            ),
            "character.chiori.talent.skill": (
                ("إنشاءات جيو",),
                ("إنشاءات جغرافية",),
            ),
        }
        for talent_id, (required, forbidden) in expected.items():
            with self.subTest(talent_id=talent_id):
                self.assertIn(talent_id, by_id)
                entry = by_id[talent_id]
                summary = entry["description_ar"]
                for phrase in required:
                    self.assertIn(phrase, summary)
                for phrase in forbidden:
                    self.assertNotIn(phrase, summary)
                self.assertEqual(entry["translation_status"], "draft")



if __name__ == "__main__":
    unittest.main()
