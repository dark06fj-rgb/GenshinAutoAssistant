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
            entity("character.test.talent.normal", "term", "Test talent", "موهبة تجريبية",
                   character_id="character.test", character_name_ar="اختبار")
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
                    type=talent_type,
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
        target["type"] = "normal"
        self.write_catalogs(catalogs)
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("duplicate talent slot Anemo/normal", output)

    def test_malformed_json_fails(self):
        (self.catalog_dir / "resources.json").write_text("{broken", encoding="utf-8")
        exit_code, output, _ = self.run_validator()
        self.assertEqual(exit_code, 1)
        self.assertIn("invalid/unreadable JSON", output)


if __name__ == "__main__":
    unittest.main()
