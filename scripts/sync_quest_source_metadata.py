#!/usr/bin/env python3
"""Resolve quest chapter/series metadata by stable IDs, without TextMapEN.json."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGS = {
    ROOT / "localization/ar/quests_archon.json": "archon",
    ROOT / "localization/ar/quests_world.json": "world",
}
SOURCE_COMMIT = "d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1"
CHAPTER_URL = (
    "https://raw.githubusercontent.com/DimbreathBot/AnimeGameData/"
    f"{SOURCE_COMMIT}/ExcelBinOutput/ChapterExcelConfigData.json"
)


def fetch_chapters() -> dict[str, dict]:
    request = urllib.request.Request(
        CHAPTER_URL,
        headers={"User-Agent": "GenshinArabicQuestCatalog/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        rows = json.loads(response.read().decode("utf-8"))
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


def main() -> int:
    chapters = fetch_chapters()
    loaded = []
    errors = []
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
            if source_id is None:
                errors.append(f"{path.name}[{index}]: source_quest_id is missing")
                continue
            key = str(source_id)
            row = chapters.get(key)
            if row is None:
                errors.append(f"{path.name}: chapter ID {key} is absent from pinned source")
                continue

            if catalog_type == "archon":
                style = row.get("FOGHOPGBDML")
                if style != "CHAPTER_STYLE_TYPE_AQ":
                    errors.append(
                        f"{path.name}: ID {key} is not an Archon chapter (style={style!r})"
                    )
                    continue
                if entry.get("node_type") != "act":
                    entry["node_type"] = "act"
                entry["source_chapter_metadata"] = {
                    name: row[name]
                    for name in (
                        "id", "groupId", "beginQuestId", "endQuestId",
                        "cityId", "needPlayerLevel", "chapterSerialNumberIcon",
                    )
                    if name in row
                }
                hashes = {}
                for name, source_key in (
                    ("title", "chapterTitleTextMapHash"),
                    ("number", "chapterNumTextMapHash"),
                    ("image_title", "chapterImageTitleTextMapHash"),
                ):
                    value = row.get(source_key)
                    if isinstance(value, int):
                        hashes[name] = value
                entry["source_text_map_hashes"] = hashes
            else:
                quest_type = row.get("questType")
                if quest_type != "WQ":
                    errors.append(
                        f"{path.name}: ID {key} is not a World Quest series (questType={quest_type!r})"
                    )
                    continue
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
                hashes = {}
                for name, source_key in (
                    ("title", "chapterTitleTextMapHash"),
                    ("number", "chapterNumTextMapHash"),
                    ("image_title", "chapterImageTitleTextMapHash"),
                ):
                    value = row.get(source_key)
                    if isinstance(value, int):
                        hashes[name] = value
                entry["source_text_map_hashes"] = hashes
                world_series_ids.add((str(old_id), new_id))
        loaded.append((path, data, catalog_type))

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

    archon_count = sum(len(data["entries"]) for _, data, kind in loaded if kind == "archon")
    world_count = sum(len(data["entries"]) for _, data, kind in loaded if kind == "world")
    print(f"Resolved {archon_count} Archon chapter records and {world_count} World Quest series records.")
    print(f"Source: AnimeGameData snapshot {SOURCE_COMMIT}")
    print("Extracted only IDs and text-map hashes from ChapterExcelConfigData; TextMapEN.json was not requested.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Quest source sync failed safely: {exc}", file=sys.stderr)
        raise SystemExit(1)
