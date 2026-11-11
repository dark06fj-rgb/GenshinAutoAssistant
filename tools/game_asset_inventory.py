#!/usr/bin/env python3
"""Safely inventory user-provided game export files without unpacking or modifying them.

This is a reconnaissance tool, not a Genshin asset decryptor. It never writes to
the input directory, executes files, or attempts to bypass encryption/DRM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SIGNATURES = (
    (b"UnityFS", "Unity AssetBundle (UnityFS)"),
    (b"PK\x03\x04", "ZIP archive"),
    (b"\x1f\x8b", "GZIP stream"),
    (b"SQLite format 3\x00", "SQLite database"),
    (b"\x89PNG\r\n\x1a\n", "PNG image"),
    (b"\xff\xd8\xff", "JPEG image"),
    (b"\x7fELF", "ELF executable"),
    (b"MZ", "Windows PE/DOS executable"),
)

TEXT_SUFFIXES = {".json", ".txt", ".csv", ".xml", ".yaml", ".yml", ".ini", ".po", ".tsv"}


def identify(path: Path) -> str:
    try:
        with path.open("rb") as stream:
            head = stream.read(32)
    except OSError:
        return "unreadable"
    for signature, label in SIGNATURES:
        if head.startswith(signature):
            return label
    if path.suffix.lower() in TEXT_SUFFIXES:
        return "text candidate (content not parsed)"
    return "unknown/binary"


def inventory(root: Path) -> dict:
    records = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        try:
            stat = path.stat()
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            records.append({
                "path": path.relative_to(root).as_posix(),
                "size_bytes": stat.st_size,
                "sha256": digest.hexdigest(),
                "detected_type": identify(path),
            })
        except OSError as exc:
            records.append({
                "path": path.relative_to(root).as_posix(),
                "detected_type": "unreadable",
                "error": str(exc),
            })
    return {
        "format": "game-asset-inventory-v1",
        "root": root.name,
        "file_count": len(records),
        "files": records,
        "limitations": [
            "Inventory only: files are not extracted, decrypted, modified, or executed.",
            "A detected signature is a clue, not proof that a format is supported.",
            "Encrypted or proprietary game containers require a lawful, documented export path.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing files you are authorized to inspect")
    parser.add_argument("--output", type=Path, help="Write JSON report here (outside the input directory)")
    args = parser.parse_args()
    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    report = json.dumps(inventory(root), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        if output == root or root in output.parents:
            parser.error("output must be outside the scanned input directory")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
