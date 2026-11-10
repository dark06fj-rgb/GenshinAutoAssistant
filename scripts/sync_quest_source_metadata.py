#!/usr/bin/env python3
"""Expand Archon and World Quest catalogs from pinned, per-ID source records.

The importer downloads small structured quest/chapter tables and only the
individual English quest records selected as AQ/WQ. It never downloads TextMapEN.
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
CATALOGS = {
    "archon": ROOT / "localization/ar/quests_archon.json",
    "world": ROOT / "localization/ar/quests_world.json",
}
ANIME_COMMIT = "d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1"
GI_COMMIT = "9651f89b8b4af8815cb193e147c84e3fb43ede63"
ANIME_BASE = (
    "https://raw.githubusercontent.com/DimbreathBot/AnimeGameData/"
    f"{ANIME_COMMIT}/ExcelBinOutput"
)
GI_BASE = (
    "https://raw.githubusercontent.com/lzray-universe/GI-OnlineQuest/"
    f"{GI_COMMIT}"
)
GI_TREE_URL = (
    "https://api.github.com/repos/lzray-universe/GI-OnlineQuest/"
    f"git/trees/{GI_COMMIT}?recursive=1"
)
USER_AGENT = "GenshinArabicQuestCatalog/2.0"
REGIONS = {
    1: "Mondstadt",
    2: "Liyue",
    3: "Inazuma",
    4: "Sumeru",
    5: "Fontaine",
    6: "Natlan",
    7: "Nod-Krai",
}


def fetch_json(url: str, attempts: int = 4):
    last_error = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.github+json, application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 404:
                raise
            if exc.code not in (403, 429, 500, 502, 503, 504):
                raise
        except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(min(2 ** attempt, 12))
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def fetch_source_tables():
    chapters = fetch_json(
        f"{ANIME_BASE}/ChapterExcelConfigData.json"
    )
    main_quests = fetch_json(
        f"{ANIME_BASE}/MainQuestExcelConfigData.json"
    )
    tree = fetch_json(GI_TREE_URL)
    if not isinstance(chapters, list) or len(chapters) < 100:
        raise ValueError("Pinned ChapterExcelConfigData is incomplete")
    if not isinstance(main_quests, list) or len(main_quests) < 1000:
        raise ValueError("Pinned MainQuestExcelConfigData is incomplete")
    if tree.get("truncated"):
        raise ValueError("GI-OnlineQuest source tree is truncated")
    available_ids = set()
    for item in tree.get("tree", []):
        prefix = "EN/quests/"
        path = item.get("path", "")
        if path.startswith(prefix) and path.endswith(".json"):
            quest_id = path[len(prefix):-5]
            if quest_id.isdigit():
                available_ids.add(quest_id)
    if len(available_ids) < 1000:
        raise ValueError("Pinned GI-OnlineQuest English quest roster is incomplete")
    return chapters, main_quests, available_ids


def quest_type(row: dict) -> str | None:
    value = row.get("type")
    if value in ("AQ", "WQ"):
        return value
    raw = row.get("mainQuestRaw")
    if isinstance(raw, dict) and raw.get("type") in ("AQ", "WQ"):
        return raw["type"]
    return None


def classify_unresolved_title(chs_title: str | None, title_hash: int | None) -> str:
    """Separate internal/unreleased placeholders from genuinely unresolved titles."""
    title = chs_title.strip() if isinstance(chs_title, str) else ""
    folded = title.casefold()
    if "$unreleased" in folded:
        return "unreleased_or_internal"
    if "test" in folded or "测试" in title or "測試" in title:
        return "internal_test"
    if not title and (not isinstance(title_hash, int) or title_hash <= 0):
        return "no_source_title"
    return "missing_english_title"


def fetch_quest(quest_id: str) -> dict | None:
    payload = fetch_json(f"{GI_BASE}/EN/quests/{quest_id}.json")
    if not isinstance(payload, dict) or str(payload.get("mainQuestId")) != quest_id:
        raise ValueError(f"Quest {quest_id}: source ID mismatch")
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    excel = payload.get("mainQuestExcel")
    if not isinstance(excel, dict):
        excel = {}
    raw = excel.get("mainQuestRaw")
    if not isinstance(raw, dict):
        raw = {}
    actual_type = meta.get("questType") or quest_type(raw) or quest_type(excel)
    if actual_type not in ("AQ", "WQ"):
        return {"_skip_reason": "not_aq_or_wq"}
    show_type = meta.get("showType") or excel.get("showType") or raw.get("showType")
    repeatable = meta.get("repeatable", raw.get("repeatable", False))
    title = payload.get("title") or excel.get("title")
    title_hash = payload.get("titleTextMapHash") or excel.get("titleTextMapHash")
    desc_hash = payload.get("descTextMapHash") or excel.get("descTextMapHash")
    if show_type != "QUEST_SHOW" or repeatable is True:
        return {"_skip_reason": "hidden_or_repeatable", "type": actual_type}
    if not isinstance(title, str) or not title.strip():
        try:
            chs_payload = fetch_json(f"{GI_BASE}/CHS/quests/{quest_id}.json")
            chs_title = chs_payload.get("title") if isinstance(chs_payload, dict) else None
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            chs_title = None
        reason = classify_unresolved_title(chs_title, title_hash)
        return {"_skip_reason": reason, "type": actual_type}
    if not isinstance(title_hash, int):
        raise ValueError(f"Quest {quest_id}: title text-map hash missing")
    if desc_hash is not None and not isinstance(desc_hash, int):
        raise ValueError(f"Quest {quest_id}: invalid description text-map hash")

    def positive_int(value):
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None

    chapter_id = positive_int(meta.get("chapterId") or raw.get("chapterId"))
    series_id = positive_int(meta.get("series") or raw.get("series"))
    city_id = positive_int(meta.get("cityId"))
    need_level = positive_int(meta.get("needPlayerLevel"))
    recommend_level = positive_int(meta.get("recommendLevel") or raw.get("recommendLevel"))
    prerequisites = meta.get("preMainQuestIds", [])
    if not isinstance(prerequisites, list):
        prerequisites = []
    prerequisites = sorted({
        str(value) for value in prerequisites
        if isinstance(value, int) and not isinstance(value, bool) and value > 0
    })
    next_ids = meta.get("nextMainQuestIds", [])
    if not isinstance(next_ids, list):
        next_ids = []
    next_ids = sorted({
        str(value) for value in next_ids
        if isinstance(value, int) and not isinstance(value, bool) and value > 0
    })
    return {
        "id": quest_id,
        "type": actual_type,
        "title": title.strip(),
        "hashes": {
            "title": title_hash,
            **({"description": desc_hash} if isinstance(desc_hash, int) else {}),
        },
        "chapter_id": str(chapter_id) if chapter_id else None,
        "series_id": str(series_id) if series_id else None,
        "region": meta.get("cityName") or REGIONS.get(city_id),
        "chapter_title": meta.get("chapterTitle") if isinstance(meta.get("chapterTitle"), str) else None,
        "city_id": city_id,
        "adventure_rank": need_level or recommend_level,
        "prerequisites": prerequisites,
        "next_ids": next_ids,
        "meta": {
            key: value for key, value in {
                "chapterId": chapter_id,
                "series": series_id,
                "type": actual_type,
                "mainQuestTag": meta.get("mainQuestTag") or raw.get("mainQuestTag"),
                "recommendLevel": recommend_level,
                "needPlayerLevel": need_level,
                "cityId": city_id,
                "cityName": meta.get("cityName"),
                "preMainQuestIds": [int(x) for x in prerequisites],
                "nextMainQuestIds": [int(x) for x in next_ids],
            }.items() if value is not None
        },
    }

def existing_index(data: dict, expected_type: str) -> dict[str, dict]:
    result = {}
    for entry in data.get("entries", []):
        if not isinstance(entry, dict):
            continue
        if entry.get("quest_type") != expected_type:
            continue
        source_id = entry.get("source_quest_id")
        if source_id is not None:
            key = (entry.get("node_type"), str(source_id))
            result[key] = entry
    return result


def node_id(kind: str, node_type: str, source_id: str) -> str:
    return f"quest.{kind}.{node_type}.{source_id}"


def new_node(kind: str, node_type: str, source_id: str, title: str, source_url: str,
             hashes: dict, region: str | None, metadata: dict) -> dict:
    return {
        "id": node_id(kind, node_type, source_id),
        "category": "quest",
        "quest_type": kind,
        "node_type": node_type,
        "source_quest_id": source_id,
        "source_name": title,
        "arabic_name": "",
        "description_ar": None,
        "chapter_id": None,
        "act_id": None,
        "series_id": None,
        "region": region,
        "sequence": None,
        "prerequisite_ids": [],
        "adventure_rank": None,
        "version_added": None,
        "source": [{
            "name": "Pinned AnimeGameData / GI-OnlineQuest source records",
            "url": source_url,
            "version": "7.2.0 / pinned English index",
        }],
        "translation_status": "needs_translation",
        "review_notes": "لم يُنجز الاسم أو الملخص العربي بعد؛ أُدرج السجل لتغطية المصدر فقط ويحتاج إلى ترجمة ومراجعة.",
        "source_text_map_hashes": hashes,
        **metadata,
    }


def merge_source(existing: dict | None, generated: dict) -> dict:
    if existing is None:
        return generated
    merged = dict(existing)
    for key, value in generated.items():
        if key in ("arabic_name", "description_ar", "translation_status", "review_notes"):
            continue
        if key == "source":
            old_sources = merged.get("source", [])
            if not isinstance(old_sources, list):
                old_sources = []
            by_url = {item.get("url"): item for item in old_sources if isinstance(item, dict)}
            for item in value:
                by_url[item["url"]] = item
            merged[key] = list(by_url.values())
        else:
            merged[key] = value
    if not str(merged.get("arabic_name", "")).strip():
        merged["arabic_name"] = ""
        merged["translation_status"] = "needs_translation"
        merged["review_notes"] = (
            "لم يُنجز الاسم أو الملخص العربي بعد؛ أُدرج السجل لتغطية المصدر فقط ويحتاج إلى ترجمة ومراجعة."
        )
    return merged


def main() -> int:
    chapters, main_rows, available_ids = fetch_source_tables()
    chapter_by_id = {
        str(row["id"]): row for row in chapters
        if isinstance(row, dict) and row.get("id") is not None
    }

    selected_ids = sorted(available_ids)
    fetched = {}
    skipped_non_target = 0
    skipped_hidden_or_repeatable = 0
    skipped_unresolved_title = 0
    skipped_internal_or_unreleased = 0
    skipped_no_source_title = 0
    unresolved_title_ids = []
    excluded_internal_ids = []
    excluded_no_source_title_ids = []
    candidate_type_counts = {"AQ": 0, "WQ": 0}
    errors = []
    with ThreadPoolExecutor(max_workers=24) as pool:
        futures = {
            pool.submit(fetch_quest, quest_id): quest_id
            for quest_id in selected_ids
        }
        for future in as_completed(futures):
            quest_id = futures[future]
            try:
                result = future.result()
                if result is None or result.get("_skip_reason") == "not_aq_or_wq":
                    skipped_non_target += 1
                else:
                    if result.get("type") in candidate_type_counts:
                        candidate_type_counts[result["type"]] += 1
                    if result.get("_skip_reason") == "hidden_or_repeatable":
                        skipped_hidden_or_repeatable += 1
                    elif result.get("_skip_reason") in ("unreleased_or_internal", "internal_test"):
                        skipped_internal_or_unreleased += 1
                        excluded_internal_ids.append(quest_id)
                    elif result.get("_skip_reason") == "no_source_title":
                        skipped_no_source_title += 1
                        excluded_no_source_title_ids.append(quest_id)
                    elif result.get("_skip_reason") == "missing_english_title":
                        skipped_unresolved_title += 1
                        unresolved_title_ids.append(quest_id)
                    else:
                        fetched[quest_id] = result
            except Exception as exc:
                errors.append(f"{quest_id}: {exc}")
    if errors:
        raise RuntimeError(
            f"Failed to verify {len(errors)} of {len(selected_ids)} English quest files; "
            "refusing all catalog writes. First errors: " + "; ".join(errors[:20])
        )
    if len(fetched) < 100:
        raise ValueError("Verified player-facing AQ/WQ roster unexpectedly small")

    data_by_kind = {}
    existing_by_kind = {}
    for kind, path in CATALOGS.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise ValueError(f"{path}: invalid catalog structure")
        data_by_kind[kind] = data
        existing_by_kind[kind] = existing_index(data, kind)

    # Create/update chapter and series nodes using verified chapter IDs.
    chapter_titles = {}
    chapter_regions = {}
    for quest in fetched.values():
        if quest["chapter_id"]:
            if quest.get("chapter_title"):
                chapter_titles.setdefault(quest["chapter_id"], quest["chapter_title"])
            if quest["region"]:
                chapter_regions.setdefault(quest["chapter_id"], quest["region"])

    for row in chapters:
        if not isinstance(row, dict) or row.get("id") is None:
            continue
        source_id = str(row["id"])
        style = row.get("FOGHOPGBDML")
        quest_type_value = row.get("questType")
        if style == "CHAPTER_STYLE_TYPE_AQ":
            kind, node_type = "archon", "act"
        elif quest_type_value == "WQ":
            kind, node_type = "world", "series"
        else:
            continue

        existing = existing_by_kind[kind].get((node_type, source_id))
        source_title = (
            (existing or {}).get("source_name")
            or chapter_titles.get(source_id)
        )
        # Keep the chapter roster source-complete without inventing a localized title.
        if not isinstance(source_title, str) or not source_title.strip():
            continue
        hashes = {}
        for name, source_key in (
            ("title", "chapterTitleTextMapHash"),
            ("number", "chapterNumTextMapHash"),
            ("image_title", "chapterImageTitleTextMapHash"),
        ):
            value = row.get(source_key)
            if isinstance(value, int):
                hashes[name] = value
        metadata = {
            "source_chapter_metadata": {
                key: row[key] for key in (
                    "id", "groupId", "beginQuestId", "endQuestId",
                    "cityId", "needPlayerLevel", "chapterSerialNumberIcon",
                    "questType",
                ) if key in row
            },
            "source_text_map_hashes": hashes,
        }
        region = chapter_regions.get(source_id) or REGIONS.get(row.get("cityId"))
        url = (
            f"https://github.com/DimbreathBot/AnimeGameData/blob/{ANIME_COMMIT}/"
            "ExcelBinOutput/ChapterExcelConfigData.json"
        )
        generated = new_node(kind, node_type, source_id, source_title, url,
                             hashes, region, metadata)
        generated["id"] = (
            existing.get("id") if existing else node_id(kind, node_type, source_id)
        )
        generated["region"] = region
        merged = merge_source(existing, generated)
        existing_by_kind[kind][(node_type, source_id)] = merged

    # Generate individual quest nodes; preserve existing Arabic editorial work.
    for quest_id, quest in fetched.items():
        kind = "archon" if quest["type"] == "AQ" else "world"
        old = existing_by_kind[kind].get(("quest", quest_id))
        source_url = f"{GI_BASE}/blob/{GI_COMMIT}/EN/quests/{quest_id}.json"
        metadata = {
            "source_main_quest_metadata": quest["meta"],
        }
        generated = new_node(
            kind, "quest", quest_id, quest["title"], source_url,
            quest["hashes"], quest["region"], metadata,
        )
        generated["id"] = old.get("id") if old else node_id(kind, "quest", quest_id)
        generated["chapter_id"] = quest["chapter_id"]
        generated["series_id"] = quest["series_id"]
        generated["act_id"] = (
            quest["chapter_id"] if kind == "archon" else None
        )
        generated["adventure_rank"] = quest["adventure_rank"]
        generated["parent_id"] = None
        if kind == "archon" and quest["chapter_id"]:
            parent = node_id("archon", "act", quest["chapter_id"])
            if ("act", quest["chapter_id"]) in existing_by_kind[kind]:
                generated["parent_id"] = parent
        elif kind == "world" and quest["chapter_id"]:
            parent = node_id("world", "series", quest["chapter_id"])
            if ("series", quest["chapter_id"]) in existing_by_kind[kind]:
                generated["parent_id"] = parent
        merged = merge_source(old, generated)
        existing_by_kind[kind][("quest", quest_id)] = merged

    translation_path = ROOT / "localization/quest-title-translations.json"
    translation_data = json.loads(translation_path.read_text(encoding="utf-8"))
    if not isinstance(translation_data, dict):
        raise ValueError("Quest title translation map must be an object")
    translation_targets = {
        "archon": ("archon", "quest"),
        "world": ("world", "quest"),
        "world_series": ("world", "series"),
    }
    applied_translations = {group: 0 for group in translation_targets}
    for group, mapping in translation_data.items():
        if group in ("archon_summaries", "world_summaries"):
            continue
        target = translation_targets.get(group)
        if target is None or not isinstance(mapping, dict):
            raise ValueError(f"Invalid quest title translation group: {group!r}")
        kind, node_type = target
        known_source_ids = {
            source_id for (current_type, source_id) in existing_by_kind[kind]
            if current_type == node_type
        }
        for source_id, arabic_title in mapping.items():
            if source_id not in known_source_ids:
                raise ValueError(
                    f"Translation map references unknown {kind}/{node_type} ID {source_id}"
                )
            if not isinstance(arabic_title, str) or not arabic_title.strip():
                raise ValueError(f"Translation for {group} ID {source_id} is empty")
            if not any("\u0600" <= char <= "\u06FF" for char in arabic_title):
                raise ValueError(f"Translation for {group} ID {source_id} contains no Arabic text")
            entry = existing_by_kind[kind][(node_type, source_id)]
            if not str(entry.get("arabic_name", "")).strip():
                entry["arabic_name"] = arabic_title.strip()
                entry["translation_status"] = "draft"
                entry["review_notes"] = (
                    "ترجمة عربية أولية لاسم مجموعة المهام؛ تحتاج إلى تدقيق المصطلحات والسياق قبل اعتمادها."
                    if node_type == "series"
                    else "ترجمة عربية أولية لاسم المهمة؛ تحتاج إلى تدقيق المصطلحات والسياق قبل اعتمادها."
                )
                applied_translations[group] += 1

    summary_targets = {
        "archon_summaries": ("archon", "quest"),
        "world_summaries": ("world", "quest"),
    }
    applied_summaries = {group: 0 for group in summary_targets}
    for group, mapping in translation_data.items():
        if group not in summary_targets:
            continue
        if not isinstance(mapping, dict):
            raise ValueError(f"Invalid quest summary translation group: {group!r}")
        kind, node_type = summary_targets[group]
        known_source_ids = {
            source_id for (current_type, source_id) in existing_by_kind[kind]
            if current_type == node_type
        }
        for source_id, arabic_summary in mapping.items():
            if source_id not in known_source_ids:
                raise ValueError(
                    f"Summary map references unknown {kind}/{node_type} ID {source_id}"
                )
            if not isinstance(arabic_summary, str) or not arabic_summary.strip():
                raise ValueError(f"Summary for {group} ID {source_id} is empty")
            if not any("\u0600" <= char <= "\u06FF" for char in arabic_summary):
                raise ValueError(f"Summary for {group} ID {source_id} contains no Arabic text")
            entry = existing_by_kind[kind][(node_type, source_id)]
            if not str(entry.get("description_ar") or "").strip():
                entry["description_ar"] = arabic_summary.strip()
                if entry.get("arabic_name"):
                    entry["translation_status"] = "draft"
                entry["review_notes"] = (
                    "ملخص عربي موجز بصياغة أصلية اعتماداً على وصف المصدر؛ يحتاج إلى مراجعة تحريرية."
                )
                applied_summaries[group] += 1
    # Resolve only prerequisites that are present in the matching catalog.
    for kind in ("archon", "world"):
        source_to_catalog_id = {
            source_id: entry["id"]
            for (node_type, source_id), entry in existing_by_kind[kind].items()
            if node_type == "quest"
        }
        for quest_id, quest in fetched.items():
            expected_kind = "archon" if quest["type"] == "AQ" else "world"
            if expected_kind != kind:
                continue
            entry = existing_by_kind[kind][("quest", quest_id)]
            resolved = [
                source_to_catalog_id[source_id]
                for source_id in quest["prerequisites"]
                if source_id in source_to_catalog_id and source_id != quest_id
            ]
            entry["prerequisite_ids"] = sorted(set(resolved))

    cycle_edges_dropped = 0
    for kind in ("archon", "world"):
        graph = {}
        quest_entries = [
            entry for (node_type, _), entry in existing_by_kind[kind].items()
            if node_type == "quest"
        ]
        for entry in sorted(quest_entries, key=lambda item: item["id"]):
            kept = []
            for prerequisite in sorted(set(entry.get("prerequisite_ids", []))):
                stack = [prerequisite]
                visited = set()
                creates_cycle = False
                while stack:
                    current = stack.pop()
                    if current == entry["id"]:
                        creates_cycle = True
                        break
                    if current in visited:
                        continue
                    visited.add(current)
                    stack.extend(graph.get(current, []))
                if creates_cycle:
                    cycle_edges_dropped += 1
                else:
                    kept.append(prerequisite)
                    graph.setdefault(entry["id"], []).append(prerequisite)
            entry["prerequisite_ids"] = kept

    # Retain only catalog records whose source IDs are represented in this
    # pinned source, while preserving hand-authored chapter/series entries.
    for kind, path in CATALOGS.items():
        entries = list(existing_by_kind[kind].values())
        entries.sort(key=lambda item: (
            {"chapter": 0, "act": 1, "series": 1, "quest": 2}.get(item.get("node_type"), 9),
            int(item.get("source_quest_id", "0")) if str(item.get("source_quest_id", "")).isdigit() else 0,
            item.get("id", ""),
        ))
        data = data_by_kind[kind]
        data["entries"] = entries
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    counts = {}
    for kind, data in data_by_kind.items():
        for entry in data["entries"]:
            key = f"{kind}_{entry.get('node_type')}"
            counts[key] = counts.get(key, 0) + 1
    fetched_counts = {
        kind: sum(1 for value in fetched.values() if value["type"] == kind)
        for kind in ("AQ", "WQ")
    }
    arabic_title_coverage = {}
    for kind, data in data_by_kind.items():
        for entry in data["entries"]:
            if isinstance(entry.get("arabic_name"), str) and entry["arabic_name"].strip():
                key = f"{kind}_{entry.get('node_type')}"
                arabic_title_coverage[key] = arabic_title_coverage.get(key, 0) + 1

    report = {
        "animegamedata_commit": ANIME_COMMIT,
        "gi_onlinequest_commit": GI_COMMIT,
        "main_quest_rows": len(main_rows),
        "english_quest_files": len(available_ids),
        "player_facing_candidates": candidate_type_counts,
        "player_facing_imported": fetched_counts,
        "skipped_non_target": skipped_non_target,
        "skipped_hidden_or_repeatable": skipped_hidden_or_repeatable,
        "held_back_unresolved_title_count": skipped_unresolved_title,
        "excluded_internal_or_unreleased_count": skipped_internal_or_unreleased,
        "excluded_internal_or_unreleased_source_ids": sorted(excluded_internal_ids),
        "excluded_no_source_title_count": skipped_no_source_title,
        "excluded_no_source_title_source_ids": sorted(excluded_no_source_title_ids),
        "arabic_title_coverage": arabic_title_coverage,
        "cycle_prerequisite_edges_dropped": cycle_edges_dropped,
        "catalog_counts": counts,
        "unresolved_title_source_ids": unresolved_title_ids,
    }
    report_path = ROOT / "localization/quest-import-report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Source roster: {len(main_rows)} MainQuest rows, "
        f"{len(available_ids)} English quest files scanned, "
        f"{len(fetched)} player-facing AQ/WQ quests, "
        f"{skipped_non_target} non-AQ/WQ records skipped, "
        f"{skipped_hidden_or_repeatable} hidden/repeatable AQ/WQ records skipped, "
        f"{skipped_unresolved_title} AQ/WQ records held back for unresolved English titles, "
        f"{skipped_internal_or_unreleased} internal/unreleased placeholders excluded, "
        f"{skipped_no_source_title} records excluded because the source has no title hash."
    )
    print(f"Player-facing candidates: AQ={candidate_type_counts['AQ']}, WQ={candidate_type_counts['WQ']}")
    print(f"Imported displayable types: AQ={fetched_counts['AQ']}, WQ={fetched_counts['WQ']}")
    print(f"Unresolved-title IDs held back: {len(unresolved_title_ids)}")
    print(f"Internal/unreleased IDs excluded: {len(excluded_internal_ids)}")
    print(f"No-source-title IDs excluded: {len(excluded_no_source_title_ids)}")
    print(
        "Arabic draft titles applied: "
        f"AQ={applied_translations['archon']}, "
        f"WQ={applied_translations['world']}, "
        f"WQ series={applied_translations['world_series']}"
    )
    print(f"Prerequisite cycle edges safely omitted: {cycle_edges_dropped}")
    print(f"Arabic original summaries applied: AQ={applied_summaries['archon_summaries']}, WQ={applied_summaries['world_summaries']}")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    print(
        "Arabic names/summaries not yet translated are explicitly marked "
        "needs_translation; existing Arabic editorial text is preserved."
    )
    print("TextMapEN.json was not requested or downloaded.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Quest catalog import failed safely: {exc}", file=sys.stderr)
        raise SystemExit(1)
