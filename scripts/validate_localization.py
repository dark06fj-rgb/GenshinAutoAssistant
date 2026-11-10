#!/usr/bin/env python3
"""Validate localization JSON syntax, record shape, and stable IDs."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / "localization"
files = sorted(ROOT.rglob("*.json"))
errors = []
checked = 0
allowed_statuses = {"draft", "reviewed", "approved", "needs_context"}
required_fields = {"id", "category", "source_name", "arabic_name", "translation_status", "source"}

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
        label = f"{path.relative_to(ROOT.parent)}: entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{label} is not an object")
            continue

        entity_id = entry.get("id")
        if entity_id is not None:
            if not isinstance(entity_id, str) or not entity_id:
                errors.append(f"{label} has an invalid id")
            elif entity_id in seen:
                errors.append(f"{label} duplicates id {entity_id}")
            else:
                seen.add(entity_id)

        # The glossary has its own compact term/value record format.
        if path.name == "glossary.json":
            continue

        missing = required_fields - entry.keys()
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(sorted(missing))}")
            continue

        if not isinstance(entry["translation_status"], str) or entry["translation_status"] not in allowed_statuses:
            errors.append(f"{label} has unsupported translation_status")
        if not isinstance(entry["source"], list) or not entry["source"]:
            errors.append(f"{label} must include at least one source record")
        if not isinstance(entry["arabic_name"], str):
            errors.append(f"{label} arabic_name must be a string")

if errors:
    print("\n".join(errors))
    sys.exit(1)

print(f"Validated JSON syntax and catalog records in {checked} files.")
