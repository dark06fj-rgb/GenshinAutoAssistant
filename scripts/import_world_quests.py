#!/usr/bin/env python3
"""Import the complete World Quest index from a pinned AnimeGameData snapshot.

This imports quest metadata and English source labels only. It deliberately does
not copy dialogue, voice assets, or long in-game scripts, and it does not invent
Arabic translations. Untranslated entries are marked needs_translation.
"""
from __future__ import annotations

import json
import os
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

SNAPSHOT = "d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1"
BASE = f"https://raw.githubusercontent.com/DimbreathBot/AnimeGameData/{SNAPSHOT}"
MAIN_URL = f"{BASE}/ExcelBinOutput/MainQuestExcelConfigData.json"
CHAPTER_URL = f"{BASE}/ExcelBinOutput/ChapterExcelConfigData.json"
TEXT_URL = f"{BASE}/TextMap/TextMapEN.json"
MEDIUM_TEXT_URL = f"{BASE}/TextMap/TextMap_MediumEN.json"
OUT = Path("localization/ar/quests_world.json")
REPORT = Path("localization/WORLD_QUEST_IMPORT_REPORT.md")


def download_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "Teyvat-Arabic-Catalog/1.0"})
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
        os.unlink(name)


def text_for(text_map, medium_text_map, value):
    if value is None:
        return ""
    key = str(value)
    return str(text_map.get(key) or medium_text_map.get(key) or "").strip()


def main():
    old_text = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    old = json.loads(old_text) if old_text.strip() else {}
    old_by_id = {item["id"]: item for item in old.get("entries", [])}

    main_quests = download_json(MAIN_URL)
    chapters = download_json(CHAPTER_URL)
    text_map = download_json(TEXT_URL)
    medium_text_map = download_json(MEDIUM_TEXT_URL)

    world_chapters = {
        int(ch["id"]): ch for ch in chapters
        if ch.get("FOGHOPGBDML") == "CHAPTER_STYLE_TYPE_WORLD_QUEST_RANK_ZERO"
    }
    source_world = [q for q in main_quests if q.get("type") == "WQ"]
    world_ids = {int(q["id"]) for q in source_world if q.get("id") is not None}

    entries = []
    unresolved_titles = []
    chapter_linked = 0
    hidden_count = 0
    for ch_id, ch in sorted(world_chapters.items()):
        title = text_for(text_map, medium_text_map, ch.get("chapterTitleTextMapHash"))
        if not title:
            unresolved_titles.append(f"chapter:{ch_id}")
            continue
        record_id = f"quest.world.chapter.{ch_id}"
        previous = old_by_id.get(record_id, {})
        entries.append({
            "id": record_id,
            "category": "quest",
            "quest_type": "world",
            "node_type": "chapter",
            "source_quest_id": str(ch_id),
            "source_name": title,
            "arabic_name": previous.get("arabic_name", ""),
            "description_ar": previous.get("description_ar"),
            "chapter_id": str(ch_id),
            "act_id": None,
            "series_id": str(ch.get("groupId")) if ch.get("groupId") is not None else None,
            "region": None,
            "sequence": None,
            "prerequisite_ids": [],
            "adventure_rank": None,
            "version_added": None,
            "source": [{
                "name": "AnimeGameData 7.2.0 pinned ChapterExcelConfigData",
                "url": f"https://github.com/DimbreathBot/AnimeGameData/blob/{SNAPSHOT}/ExcelBinOutput/ChapterExcelConfigData.json",
                "version": "7.2.0"
            }],
            "translation_status": previous.get("translation_status", "needs_translation"),
            "review_notes": previous.get("review_notes", "عنوان فصل مستورد من فهرس اللعبة؛ لا توجد ترجمة عربية معتمدة بعد."),
            "source_chapter_metadata": {
                "id": ch_id,
                "groupId": ch.get("groupId"),
                "beginQuestId": ch.get("beginQuestId"),
                "endQuestId": ch.get("endQuestId"),
                "cityId": ch.get("cityId"),
                "style": ch.get("FOGHOPGBDML")
            },
            "source_text_map_hashes": {"title": ch.get("chapterTitleTextMapHash")}
        })

    chapter_ids_included = {
        int(item["source_quest_id"]) for item in entries if item["node_type"] == "chapter"
    }
    quest_records = []
    for q in source_world:
        qid = int(q["id"])
        title = text_for(text_map, medium_text_map, q.get("titleTextMapHash"))
        if not title:
            unresolved_titles.append(f"quest:{qid}")
            continue
        chapter_id = q.get("chapterId")
        chapter_id_int = int(chapter_id) if chapter_id not in (None, 0, "0") else None
        parent_id = (
            f"quest.world.chapter.{chapter_id_int}"
            if chapter_id_int in chapter_ids_included else None
        )
        if parent_id:
            chapter_linked += 1
        if q.get("showType") == "QUEST_HIDDEN":
            hidden_count += 1
        record_id = f"quest.world.quest.{qid}"
        previous = old_by_id.get(record_id, {})
        prerequisites = q.get("preMainQuestIds") or []
        prerequisite_ids = [
            f"quest.world.quest.{int(pid)}" for pid in prerequisites
            if str(pid).isdigit() and int(pid) in world_ids
        ]
        rank = q.get("recommendLevel")
        quest_records.append({
            "id": record_id,
            "category": "quest",
            "quest_type": "world",
            "node_type": "quest",
            "source_quest_id": str(qid),
            "source_name": title,
            "arabic_name": previous.get("arabic_name", ""),
            "description_ar": previous.get("description_ar"),
            "chapter_id": str(chapter_id_int) if chapter_id_int else None,
            "act_id": None,
            "series_id": str(q.get("series")) if q.get("series") is not None else None,
            "region": None,
            "sequence": None,
            "prerequisite_ids": prerequisite_ids,
            "adventure_rank": int(rank) if isinstance(rank, (int, float)) and rank > 0 else None,
            "version_added": None,
            "source": [{
                "name": "AnimeGameData 7.2.0 pinned MainQuestExcelConfigData",
                "url": f"https://github.com/DimbreathBot/AnimeGameData/blob/{SNAPSHOT}/ExcelBinOutput/MainQuestExcelConfigData.json",
                "version": "7.2.0"
            }],
            "translation_status": previous.get("translation_status", "needs_translation"),
            "review_notes": previous.get("review_notes", "سجل مهمة عالم مستورد آلياً؛ الاسم الإنجليزي موثق والترجمة العربية لم تُنجز بعد."),
            "source_main_quest_metadata": {
                "chapterId": chapter_id_int,
                "series": q.get("series"),
                "type": q.get("type"),
                "mainQuestTag": q.get("mainQuestTag"),
                "showType": q.get("showType"),
                "activeMode": q.get("activeMode"),
                "repeatable": q.get("repeatable"),
                "recommendLevel": q.get("recommendLevel"),
                "cityId": q.get("cityId"),
                "luaPath": q.get("luaPath")
            },
            "source_text_map_hashes": {
                "title": q.get("titleTextMapHash"),
                "description": q.get("descTextMapHash")
            },
            "parent_id": parent_id
        })

    entries.extend(quest_records)
    entries.sort(key=lambda item: (item["node_type"] != "chapter", int(item["source_quest_id"])))
    result = {
        "schema_version": "1.0.0",
        "language": "ar",
        "language_name": "Arabic",
        "locale": "ar",
        "game": "Genshin Impact",
        "game_version": "7.2.0",
        "catalog_type": "world_quests",
        "disclaimer": "فهرس مجتمعي غير رسمي. الأسماء العربية التي لم تُترجم بعد موسومة needs_translation. لا يتضمن هذا الملف حوارات المهام أو الأصول الصوتية.",
        "source_sync": {
            "repository": "DimbreathBot/AnimeGameData",
            "commit": SNAPSHOT,
            "main_quest_source_records": len(source_world),
            "world_chapter_source_records": len(world_chapters),
            "imported_world_quest_records": len(quest_records),
            "imported_chapter_records": len([e for e in entries if e["node_type"] == "chapter"]),
            "unresolved_title_records": len(unresolved_titles)
        },
        "entries": entries
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status_counts = Counter(item["translation_status"] for item in entries)
    report = [
        "# World Quest Import Report",
        "",
        f"- Source snapshot: `DimbreathBot/AnimeGameData@{SNAPSHOT}` (7.2.0)",
        f"- Source WQ records: {len(source_world)}",
        f"- Imported quest records with resolved English title: {len(quest_records)}",
        f"- Imported world-quest chapter groups: {len([e for e in entries if e['node_type'] == 'chapter'])}",
        f"- Quest records linked to an imported chapter: {chapter_linked}",
        f"- Source records flagged hidden: {hidden_count}",
        f"- Unresolved title hashes after TextMapEN + TextMap_MediumEN: {len(unresolved_titles)}",
        f"- Translation statuses: {dict(status_counts)}",
        "",
        "Arabic translations are intentionally left empty and marked `needs_translation`; no machine-generated or guessed Arabic labels are presented as completed work.",
        "The source type `WQ` is retained verbatim in metadata. Some records are internal/hidden quest nodes, so the app should label visibility from source metadata rather than imply every record is a player-facing quest.",
        "",
    ]
    if unresolved_titles:
        report += ["## Unresolved source titles", ""] + [f"- `{value}`" for value in unresolved_titles[:500]]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(result["source_sync"], ensure_ascii=False))


if __name__ == "__main__":
    main()
