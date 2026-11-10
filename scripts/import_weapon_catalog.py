#!/usr/bin/env python3
"""Import public weapon metadata from genshin-db into the Arabic catalog.

This importer stores names and compact metadata only. It deliberately does not
copy weapon passive descriptions or other long game text. Existing Arabic names
and review notes are preserved by stable weapon ID.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "localization/ar/weapons.json"
API = "https://genshin-db-api.vercel.app/api/v5/weapons"

def fetch(query):
    params = urllib.parse.urlencode({
        "query": query,
        "matchCategories": "true",
        "verboseCategories": "true",
        "queryLanguages": "english",
        "dumpResult": "true",
    })
    request = urllib.request.Request(
        f"{API}?{params}",
        headers={"User-Agent": "GenshinArabicLocalizationCatalog/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))

def slug(value):
    value = re.sub(r"([a-z0-9])([A-Z])", r"\\1-\\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value

def field(record, *names):
    if not isinstance(record, dict):
        return None
    normalized = {str(k).replace("_", "").lower(): v for k, v in record.items()}
    for name in names:
        value = normalized.get(name.replace("_", "").lower())
        if value is not None:
            return value
    return None

def records_from(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "result", "weapons"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return list(value.values())
        # Some API responses are a name -> record map.
        if payload and all(isinstance(v, dict) for v in payload.values()):
            return list(payload.values())
    raise ValueError("Unexpected API response shape; refusing to overwrite the catalog.")

def main():
    current = json.loads(CATALOG.read_text(encoding="utf-8"))
    old = {entry["id"]: entry for entry in current.get("entries", [])}
    payload = fetch("names")
    records = records_from(payload)
    merged = {}
    skipped = []

    for item in records:
        if isinstance(item, str):
            detail_payload = fetch(item)
            detail_records = records_from(detail_payload)
            if not detail_records:
                skipped.append(item)
                continue
            item = detail_records[0]
        name = field(item, "name", "Name")
        if not isinstance(name, str) or not name.strip():
            skipped.append(str(item)[:80])
            continue

        key = slug(name)
        if not key:
            skipped.append(name)
            continue
        entity_id = f"weapon.{key.replace('-', '_')}"
        previous = old.get(entity_id, {})
        rarity = field(item, "rarity", "Rarity")
        weapon_type = field(item, "weaponType", "weapon_type", "type", "Type")
        entry = {
            "id": entity_id,
            "category": "weapon",
            "source_name": name,
            "arabic_name": previous.get("arabic_name", ""),
            "rarity": rarity if isinstance(rarity, int) and 1 <= rarity <= 5 else previous.get("rarity"),
            "source": [{
                "name": "genshin-db",
                "url": "https://github.com/theBowja/genshin-db",
                "version": "API v5; version reported by upstream package",
            }],
            "translation_status": previous.get("translation_status", "needs_context" if not previous.get("arabic_name") else "draft"),
            "review_notes": previous.get("review_notes", "الاسم العربي يحتاج مراجعة؛ البيانات الوصفية مستوردة آلياً."),
        }
        if isinstance(weapon_type, str) and weapon_type:
            entry["weapon_type"] = weapon_type
        # Preserve any curator-added fields not managed by this importer.
        for optional in ("image_url", "item_type"):
            if optional in previous:
                entry[optional] = previous[optional]
        merged[entity_id] = entry

    if not merged:
        raise ValueError("No weapon records were recognized; original catalog left unchanged.")

    result = dict(current)
    result["entries"] = sorted(merged.values(), key=lambda x: x["source_name"].casefold())
    result["source_sync"] = {
        "provider": "genshin-db",
        "endpoint": API,
        "synced_on": date.today().isoformat(),
        "records_imported": len(result["entries"]),
        "records_skipped": len(skipped),
        "note": "Names and compact metadata only; long descriptions are not copied.",
    }
    CATALOG.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Imported {len(merged)} weapon records; skipped {len(skipped)}.")
    if skipped:
        print("Skipped records:", ", ".join(skipped[:20]))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Import failed safely: {exc}", file=sys.stderr)
        sys.exit(1)
