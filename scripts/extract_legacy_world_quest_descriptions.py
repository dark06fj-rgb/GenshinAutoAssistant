#!/usr/bin/env python3
"""Extract only source quest descriptions needed by the legacy WQ translation backlog.

No dialogue or voice assets are copied. This script produces a short-lived CI artifact;
it does not modify the Arabic catalog or mark any entry translated.
"""
from __future__ import annotations

import json
import re
import tempfile
import urllib.request
from pathlib import Path

ANIME_COMMIT = "d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1"
BACKLOG_COMMIT = "3faf9c1916e2c672593a7e1ee5709b04f314eb7a"\nGI_COMMIT = "9651f89b8b4af8815cb193e147c84e3fb43ede63"
BASE = f"https://raw.githubusercontent.com/DimbreathBot/AnimeGameData/{ANIME_COMMIT}/TextMap"
BACKLOG_URL = (
    "https://raw.githubusercontent.com/dark06fj-rgb/GenshinAutoAssistant/"
    f"{BACKLOG_COMMIT}/localization/ar/quests_world.json"
)
CURRENT_CATALOG = Path("localization/ar/quests_world.json")
OUT = Path("artifacts/world_quest_source_descriptions_en.json")
REPORT = Path("artifacts/world_quest_source_description_report.json")
INTERNAL = re.compile(r"\(test|（test|\$hidden|unreleased", re.IGNORECASE)


def load_url_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "Teyvat-Arabic-Localization/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as tmp:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            name = tmp.name
    try:
        with open(name, "r", encoding="utf-8") as handle:
            return json.load(handle)
    finally:
        Path(name).unlink(missing_ok=True)


def main() -> int:
    old = load_url_json(BACKLOG_URL)
    current = json.loads(CURRENT_CATALOG.read_text(encoding="utf-8"))
    backlog_ids = {
        str(item.get("source_quest_id"))
        for item in old.get("entries", [])
        if item.get("node_type") == "quest"
        and item.get("translation_status") == "needs_translation"
    }
    targets = [
        item for item in current.get("entries", [])
        if item.get("node_type") == "quest"
        and str(item.get("source_quest_id")) in backlog_ids
        and not INTERNAL.search(str(item.get("source_name", "")))
        and item.get("source_main_quest_metadata", {}).get("showType") != "QUEST_HIDDEN"
        and str(item.get("arabic_name", "")).strip()
    ]
    if not targets:
        raise RuntimeError("No eligible retained legacy WQ records found")

    text_map = load_url_json(f"{BASE}/TextMapEN.json")
    medium_map = load_url_json(f"{BASE}/TextMap_MediumEN.json")
    extracted = []
    missing = []
    for item in targets:
        hashes = item.get("source_text_map_hashes") or {}
        value = hashes.get("description")
        if value is None:
            missing.append({"id": item["id"], "source_quest_id": item["source_quest_id"], "reason": "missing_description_hash"})
            continue
        key = str(value)
        description = text_map.get(key) or medium_map.get(key)
        if not isinstance(description, str) or not description.strip():
            missing.append({"id": item["id"], "source_quest_id": item["source_quest_id"], "hash": key, "reason": "hash_not_found"})
            continue
        extracted.append({
            "id": item["id"],
            "source_quest_id": item["source_quest_id"],
            "source_name": item["source_name"],
            "arabic_name": item["arabic_name"],
            "description_hash": key,
            "description_en": description.strip(),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source_snapshot": f"DimbreathBot/AnimeGameData@{ANIME_COMMIT}",
        "backlog_commit": BACKLOG_COMMIT,\n        "gi_onlinequest_commit": GI_COMMIT,
        "target_count": len(targets),
        "extracted_count": len(extracted),
        "missing_count": len(missing),
        "entries": extracted,
        "missing": missing,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps({
        "backlog_target_count": len(targets),
        "source_descriptions_extracted": len(extracted),
        "description_hashes_unresolved": len(missing),
        "unresolved": missing,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Eligible retained legacy quests: {len(targets)}; "
        f"English source descriptions extracted: {len(extracted)}; "
        f"unresolved hashes: {len(missing)}."
    )
    if not extracted:
        raise RuntimeError("No English source descriptions were resolved; refusing an empty artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
