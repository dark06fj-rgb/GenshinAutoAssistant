#!/usr/bin/env python3
"""Resolve quest source text hashes by stable quest ID, without fetching TextMapEN.json.

Only compact title/description hashes and quest metadata are retained. The
large TextMapEN payload is deliberately not requested or stored.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGS = (
    ROOT / "localization/ar/quests_archon.json",
    ROOT / "localization/ar/quests_world.json",
)
SOURCE_REPO = "https://raw.githubusercontent.com/lzray-universe/GI-OnlineQuest"
SOURCE_COMMIT = "9651f89b8b4af8815cb193e147c84e3fb43ede63"
USER_AGENT = "GenshinArabicQuestCatalog/1.0"


def fetch_quest(quest_id: str) -> dict:
    url = f"{SOURCE_REPO}/{SOURCE_COMMIT}/EN/quests/{quest_id}.json"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError(f"Quest {quest_id}: response is not an object")
            returned_id = payload.get("mainQuestId")
            if str(returned_id) != quest_id:
                raise ValueError(
                    f"Quest {quest_id}: source returned mismatched ID {returned_id!r}"
                )
            title = payload.get("title")
            title_hash = payload.get("titleTextMapHash")
            desc_hash = payload.get("descTextMapHash")
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f"Quest {quest_id}: source title is missing")
            if not isinstance(title_hash, int):
                raise ValueError(f"Quest {quest_id}: titleTextMapHash is missing")
            if desc_hash is not None and not isinstance(desc_hash, int):
                raise ValueError(f"Quest {quest_id}: descTextMapHash is invalid")
            excel = payload.get("mainQuestExcel")
            if not isinstance(excel, dict):
                excel = {}
            return {
                "title": title.strip(),
                "title_hash": title_hash,
                "description_hash": desc_hash,
                "chapter_id": excel.get("chapterId"),
                "series_id": excel.get("series"),
                "quest_type": excel.get("type") or payload.get("type"),
                "recommend_level": excel.get("recommendLevel"),
                "url": url,
            }
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Quest {quest_id}: source lookup failed: {last_error}")


def main() -> int:
    loaded = []
    requested: dict[str, list[dict]] = {}
    for path in CATALOGS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise ValueError(f"{path}: invalid catalog structure")
        loaded.append((path, data))
        for entry in data["entries"]:
            if not isinstance(entry, dict) or entry.get("node_type") != "quest":
                continue
            quest_id = entry.get("source_quest_id")
            if quest_id is None:
                continue
            key = str(quest_id)
            if not key.isdigit():
                raise ValueError(f"{path}: invalid source_quest_id {quest_id!r}")
            requested.setdefault(key, []).append(entry)

    if not requested:
        print("No individual quest IDs found; no files changed.")
        return 0

    fetched: dict[str, dict] = {}
    errors = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_quest, quest_id): quest_id for quest_id in requested}
        for future in as_completed(futures):
            quest_id = futures[future]
            try:
                fetched[quest_id] = future.result()
            except Exception as exc:
                errors.append(str(exc))

    if errors:
        raise RuntimeError(
            "Source lookup incomplete; refusing partial writes:\n" + "\n".join(errors)
        )

    updated = 0
    mismatches = []
    for quest_id, entries in requested.items():
        source = fetched[quest_id]
        for entry in entries:
            existing_name = str(entry.get("source_name", "")).strip()
            if existing_name.casefold() != source["title"].casefold():
                mismatches.append(
                    f"{quest_id}: catalog={existing_name!r}, source={source['title']!r}"
                )
                continue
            entry["source_text_map_hashes"] = {
                "title": source["title_hash"],
                "description": source["description_hash"],
            }
            metadata = {}
            for key in ("chapter_id", "series_id", "quest_type", "recommend_level"):
                value = source[key]
                if value is not None:
                    metadata[key] = value
            entry["source_main_quest_metadata"] = metadata
            updated += 1

    if mismatches:
        raise RuntimeError(
            "English title mismatch; refusing all writes:\n" + "\n".join(mismatches)
        )

    for path, data in loaded:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        f"Resolved source text hashes for {updated} quest records "
        f"across {len(requested)} unique quest IDs."
    )
    print(
        "Method: one compact per-ID quest record; TextMapEN.json was not requested."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Quest source sync failed safely: {exc}", file=sys.stderr)
        raise SystemExit(1)
