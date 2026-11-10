#!/usr/bin/env python3
"""Validate catalog JSON syntax and stable IDs using only Python's standard library."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / "localization"
files = sorted(ROOT.rglob("*.json"))
errors = []
checked = 0

for path in files:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        checked += 1
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT.parent)}: invalid JSON: {exc}")
        continue

    entries = data.get("entries", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        errors.append(f"{path.relative_to(ROOT.parent)}: 'entries' must be an array")
        continue
    seen = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{path.relative_to(ROOT.parent)}: entry {index} is not an object")
            continue
        entity_id = entry.get("id")
        if entity_id is None:
            continue  # Glossaries may use a different record shape.
        if not isinstance(entity_id, str) or not entity_id:
            errors.append(f"{path.relative_to(ROOT.parent)}: entry {index} has an invalid id")
        elif entity_id in seen:
            errors.append(f"{path.relative_to(ROOT.parent)}: duplicate id {entity_id}")
        else:
            seen.add(entity_id)

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"Validated JSON syntax and per-file IDs in {checked} files.")
