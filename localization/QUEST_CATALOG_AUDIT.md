# Quest catalog audit — version 7.2 baseline

## Scope
This audit establishes the missing quest-data work as two independent catalogs:

- **Archon Quests**: chapter, act, and individual quest nodes, with stable IDs and prerequisite relationships.
- **World Quests**: quest-series and individual quest nodes, with region and prerequisite relationships.

Story Quests, Hangout Events, Commissions, and Event Quests are not silently mixed into either catalog. They require separate scope decisions and files.

## Source assessment

- The current `genshin-db` data-folder index documents characters, talents, weapons, artifacts, materials, and other categories, but does not expose a dedicated quest catalog in its documented query functions. It is therefore not sufficient by itself for quest coverage.
- The maintained technical source is [DimbreathBot/AnimeGameData](https://github.com/DimbreathBot/AnimeGameData), the GitHub mirror of `Dimbreath/animegamedata2`. The documented 7.2.0 snapshot is commit `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1` (2026-11-04).
- `ExcelBinOutput/MainQuestExcelConfigData.json` contains 4,075 main-quest definitions in that snapshot. This is a mixed pool, not a count of Archon or World Quests; it must be filtered against chapter metadata.
- `ExcelBinOutput/ChapterExcelConfigData.json` contains 436 chapter rows in this snapshot. `CHAPTER_STYLE_TYPE_AQ` identifies Archon chapter/act rows and `questType: WQ` identifies World Quest series rows. These are group metadata, not individual player-visible quests.
- `ExcelBinOutput/QuestExcelConfigData.json` stores individual quest steps linked by `mainId`; these steps must not be mistaken for separate main quests.
- Quest title hashes are resolved through `TextMapEN` and `TextMap_MediumEN`; the upstream source audit documents separate, non-overlapping hash spaces. Missing hashes must be counted and reported, not silently replaced with empty strings.
- Community parsers and the Genshin Impact Wiki are cross-check leads for extraction logic and hierarchy, not translation authorities.

## Data model

Each record preserves the upstream identifier and identifies its node type (`chapter`, `act`, `series`, or `quest`). Where supported by the source, record parent, chapter/act/series IDs, sequence, region, prerequisite quest IDs, Adventure Rank gate, and version introduced. Unknown values must remain absent or null rather than guessed.

Arabic titles and concise summaries are original community drafts. Do not copy dialogue, long narrative descriptions, voice files, or artwork into this catalog.

## Current state

- `ar/quests_archon.json`: **51 Archon act records**. Every source ID was matched to an Archon row in the pinned 436-row `ChapterExcelConfigData` snapshot.
- `ar/quests_world.json`: **63 World Quest series records**. Every source ID was matched to a `questType: WQ` row in the same pinned snapshot. The records were normalized from the incorrect `quest` node type/ID prefix to `series`.
- All 114 records now include source text-map hash identifiers and compact chapter metadata.
- The new `scripts/sync_quest_source_metadata.py` reads the 202 KB chapter table and resolves only the 114 requested IDs. It does **not** request or download the 57.7 MB `TextMapEN.json` file.
- The first per-quest lookup experiment against `GI-OnlineQuest/EN/quests/{id}.json` was rejected safely because these catalog IDs are chapter/series IDs, not individual quest IDs. No partial writes were made by that failed run.
- No individual player-visible quest records have been imported by this metadata sync yet. The 4,075-row main-quest table is not a valid coverage denominator.
- No quest has been marked reviewed or approved.

## Remaining work

1. Resolve the stored text-map hashes to English titles only where the catalog lacks reliable source titles; use a bounded lookup method and report unresolved hashes.
2. Build a reproducible importer pinned to AnimeGameData snapshot `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1`; filter main quests using the validated chapter metadata and preserve original numeric IDs.
3. Populate Archon chapter/act/individual quest nodes and World Quest series/individual quest nodes in reviewable batches.
4. Cross-check prerequisite graphs and Adventure Rank gates against versioned source tables and the Travel Log.
5. Write original Arabic titles and short summaries; leave ambiguous translations as `needs_context`.
6. Extend integration tests to compare imported chapter/act membership and individual quest references against the pinned source tables, then publish coverage counts only after reconciling the complete roster.

**This is verified source metadata scaffolding, not a completed quest translation.** The current 51 + 63 records are partial chapter/series catalogs; individual quest coverage and editorial review remain outstanding.
