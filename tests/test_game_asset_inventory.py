import tempfile
import unittest
from pathlib import Path

from tools.game_asset_inventory import identify, inventory


class GameAssetInventoryTests(unittest.TestCase):
    def test_detects_unityfs_signature(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.bundle"
            path.write_bytes(b"UnityFS" + b"\x00" * 20)
            self.assertEqual(identify(path), "Unity AssetBundle (UnityFS)")

    def test_inventory_is_read_only_and_hashes_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sample = root / "dialogue.json"
            sample.write_text('{"hello":"world"}', encoding="utf-8")
            before = sample.read_bytes()
            report = inventory(root)
            self.assertEqual(report["file_count"], 1)
            self.assertEqual(report["files"][0]["path"], "dialogue.json")
            self.assertEqual(sample.read_bytes(), before)
            self.assertEqual(len(report["files"][0]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
