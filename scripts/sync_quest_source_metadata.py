#!/usr/bin/env python3
"""Resolve quest source hashes by stable IDs without fetching TextMapEN.json."""
from __future__ import annotations

import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGS = {
    ROOT / "localization/ar/quests_archon.json": "archon",
    ROOT / "localization/ar/quests_world.json": "world",
}
ANIME_COMMIT = "d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1"
CHAPTER_URL = (
    "https://raw.githubusercontent.com/DimbreathBot/AnimeGameData/"
    f"{ANIME_COMMIT}/ExcelBinOutput/ChapterExcelConfigData.json"
)
GI_QUEST_BASE = (
    "https://raw.githubusercontent.com/lzray-universe/GI-OnlineQuest/"
    "9651f89b8b4af8815cb193e147c84e3fb43ede63/EN/quests"
)
USER_AGENT = "GenshinArabicQuestCatalog/1.0"


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_chapters() -> dict[str, dict]:
    rows = fetch_json(CHAPTER_URL)
    if not isinstance(rows, list):
        raise ValueError("ChapterExcelConfigData response is not an array")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("id") is None:
            continue
        key = str(row["id"])
        if key in result:
            raise ValueError(f"Duplicate chapter ID in pinned source: {key}")
        result[key] = row
    return result


def fetch_individual_quest(quest_id: str) -> dict:
    payload = fetch_json(f"{GI_QUEST_BASE}/{quest_id}.json")
    if not isinstance(payload, dict) or str(payload.get("mainQuestId")) != quest_id:
        raise ValueError(f"Quest {quest_id}: source returned a mismatched record")
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
    raw = excel.get("mainQuestRaw") if isinstance(excel, dict) else None
    if not isinstance(raw, dict):
        raw = {}
    metadata_source = dict(raw)
    if isinstance(excel, dict):
        metadata_source.update(excel)
    metadata = {}
    for key in (
        "chapterId", "series", "type", "mainQuestTag",
        "recommendLevel", "suggestTrackMainQuestList",
    ):
        value = metadata_source.get(key)
        if value is not None and value != 0 and value != []:
            metadata[key] = value
    quest_tag = str(metadata.get("mainQuestTag", metadata.get("type", "")))
    return {
        "title": title.strip(),
        "hashes": {"title": title_hash, "description": desc_hash},
        "metadata": metadata,
        "quest_tag": quest_tag,
    }


def chapter_hashes(row: dict) -> dict:
    hashes = {}
    for name, source_key in (
        ("title", "chapterTitleTextMapHash"),
        ("number", "chapterNumTextMapHash"),
        ("image_title", "chapterImageTitleTextMapHash"),
    ):
        value = row.get(source_key)
        if isinstance(value, int):
            hashes[name] = value
    if not hashes.get("title"):
        raise ValueError(f"Chapter {row.get('id')}: chapter title hash is missing")
    return hashes


def main() -> int:
    chapters = fetch_chapters()
    loaded = []
    errors = []
    quest_requests: dict[str, list[tuple[str, dict]]] = {}
    world_series_ids = set()

    for path, catalog_type in CATALOGS.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise ValueError(f"{path}: invalid catalog structure")
        for index, entry in enumerate(data["entries"]):
            if not isinstance(entry, dict):
                errors.append(f"{path.name}[{index}]: entry is not an object")
                continue
            source_id = entry.get("source_quest_id")
            if source_id is None or not str(source_id).isdigit():
                errors.append(f"{path.name}[{index}]: invalid source_quest_id")
                continue
            key = str(source_id)
            node_type = entry.get("node_type")
            row = chapters.get(key)

            if catalog_type == "archon" and node_type == "quest":
                quest_requests.setdefault(key, []).append((catalog_type, entry))
                continue

            if catalog_type == "world":
                if row is not None and row.get("questType") == "WQ":
                    old_id = entry.get("id")
                    new_id = f"quest.world.series.{key}"
                    entry["id"] = new_id
                    entry["node_type"] = "series"
                    entry["series_id"] = key
                    entry["chapter_id"] = key
                    entry["source_chapter_metadata"] = {
                        name: row[name]
                        for name in (
                            "id", "groupId", "beginQuestId", "endQuestId",
                            "cityId", "needPlayerLevel", "questType",
                        )
                        if name in row
                    }
                    entry["source_text_map_hashes"] = chapter_hashes(row)
                    world_series_ids.add((str(old_id), new_id))
                    continue
                if row is None:
                    quest_requests.setdefault(key, []).append((catalog_type, entry))
                    continue
                errors.append(f"{path.name}: ID {key} is neither a WQ series nor a resolvable quest")
                continue

            if catalog_type == "archon" and node_type == "act":
                if row is None or row.get("FOGHOPGBDML") != "CHAPTER_STYLE_TYPE_AQ":
                    errors.append(f"{path.name}: ID {key} is not an Archon act row")
                    continue
                entry["source_chapter_metadata"] = {
                    name: row[name]
                    for name in (
                        "id", "groupId", "beginQuestId", "endQuestId",
                        "cityId", "needPlayerLevel", "chapterSerialNumberIcon",
                    )
                    if name in row
                }
                entry["source_text_map_hashes"] = chapter_hashes(row)
                continue

            errors.append(
                f"{path.name}: unsupported node_type {node_type!r} for source ID {key}"
            )
        loaded.append((path, data, catalog_type))

    quest_results = {}
    if quest_requests:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {
                pool.submit(fetch_individual_quest, quest_id): quest_id
                for quest_id in quest_requests
            }
            for future in as_completed(futures):
                quest_id = futures[future]
                try:
                    quest_results[quest_id] = future.result()
                except Exception as exc:
                    errors.append(f"Individual quest {quest_id}: {exc}")

    for quest_id, targets in quest_requests.items():
        source = quest_results.get(quest_id)
        if source is None:
            continue
        for catalog_type, entry in targets:
            normalize_title = lambda value: str(value).strip().strip("\"'“”‘’").casefold()
            if normalize_title(entry.get("source_name", "")) != normalize_title(source["title"]):
                errors.append(
                    f"Quest {quest_id}: English title mismatch "
                    f"({entry.get('source_name')!r} != {source['title']!r})"
                )
                continue
            if catalog_type == "world":
                old_id = entry.get("id")
                entry["id"] = f"quest.world.quest.{quest_id}"
                entry["node_type"] = "quest"
                metadata = source["metadata"]
                chapter_id = metadata.get("chapterId")
                series_id = metadata.get("series")
                if chapter_id:
                    entry["chapter_id"] = str(chapter_id)
                if series_id:
                    entry["series_id"] = str(series_id)
            else:
                old_id = entry.get("id")
            entry["source_text_map_hashes"] = source["hashes"]
            entry["source_main_quest_metadata"] = source["metadata"]

    if errors:
        raise RuntimeError(
            "Source reconciliation failed; refusing partial writes:\n"
            + "\n".join(errors)
        )

    rename_map = dict(world_series_ids)
    for path, data, catalog_type in loaded:
        if catalog_type != "world":
            continue
        for entry in data["entries"]:
            parent = entry.get("parent_id")
            if parent in rename_map:
                entry["parent_id"] = rename_map[parent]
            prerequisites = entry.get("prerequisite_ids")
            if isinstance(prerequisites, list):
                entry["prerequisite_ids"] = [
                    rename_map.get(value, value) for value in prerequisites
                ]

    for path, data, _ in loaded:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    counts = {}
    for _, data, catalog_type in loaded:
        for entry in data["entries"]:
            key = f"{catalog_type}_{entry.get('node_type')}"
            counts[key] = counts.get(key, 0) + 1
    print("Resolved quest source metadata by stable IDs:")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    print(f"Chapter source: AnimeGameData snapshot {ANIME_COMMIT}")
    print("Individual quest source: pinned GI-OnlineQuest per-ID records.")
    print("Only requested IDs and text-map hashes were extracted; TextMapEN.json was not requested.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Quest source sync failed safely: {exc}", file=sys.stderr)
        raise SystemExit(1)
