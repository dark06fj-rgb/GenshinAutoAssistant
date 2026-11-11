import tempfile
import unittest
from pathlib import Path

from tools.text_asset_probe import inspect_text, probe


class TextAssetProbeTests(unittest.TestCase):
    def test_counts_json_strings_without_exposing_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sample = root / "strings.json"
            sample.write_text('{"menu":"Settings","items":["Start","Exit"]}', encoding="utf-8")
            report = probe(root)
            self.assertEqual(report["readable_file_count"], 1)
            self.assertEqual(report["files"][0]["format"], "json")
            self.assertEqual(report["files"][0]["string_value_count"], 4)
            self.assertNotIn("Settings", str(report))

    def test_skips_binary_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "data.bin"
            binary.write_bytes(b"\x00\x01\x02")
            large = root / "large.txt"
            large.write_text("x" * 20, encoding="utf-8")
            self.assertEqual(inspect_text(binary)["status"], "skipped")
            self.assertEqual(inspect_text(large, max_bytes=10)["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
