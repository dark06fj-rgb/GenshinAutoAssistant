# Quest catalog audit — version 7.2 source snapshot

## Scope

This catalog covers player-facing **Archon Quests (AQ)** and **World Quests (WQ)** at the MainQuest level:

- Archon act nodes and individual Archon main quests.
- World Quest series nodes and individual World Quest main quests.

It does not treat every `QuestExcelConfigData` step/objective as a separate player-facing quest. Story Quests, Hangout Events, Commissions, and Event Quests remain outside this catalog and require separate scope decisions.

## Pinned sources and extraction method

- [DimbreathBot/AnimeGameData](https://github.com/DimbreathBot/AnimeGameData), snapshot commit `d54f6f0d423ded9d055bb740a3e5f3aa8f2667f1` (7.2.0), provides `MainQuestExcelConfigData.json` (4,543 rows) and `ChapterExcelConfigData.json` (436 rows).
- [GI-OnlineQuest](https://github.com/lzray-universe/GI-OnlineQuest), commit `9651f89b8b4af8815cb193e147c84e3fb43ede63`, provides 3,905 per-ID English quest records. The importer scans these records and uses their explicit `meta.questType` rather than guessing from ID ranges or the main-quest tag.
- Only records whose source type is AQ/WQ, whose display type is `QUEST_SHOW`, and which are not repeatable are eligible for the player-facing quest catalog.
- Individual titles, description hashes, chapter/series IDs, region, Adventure Rank metadata, and prerequisite IDs are read per quest ID. Dialogue, voice data, and long narrative text are not copied.
- Chapter/series titles are taken from verified chapter records or the English chapter title attached to a matching quest. A chapter node is not invented when no source title is available.
- The importer does **not** request or download the 57.7 MB `TextMapEN.json`. Records with an empty English display title are held back and listed in `quest-import-report.json`, even if a text-map hash exists.
- Four prerequisite edges in the source graph formed cycles. The importer deterministically omits those four edges from the navigable prerequisite graph; the raw prerequisite IDs remain in source metadata for later review.

## Current verified catalog

The latest successful import produced **1,590 records**:

| Catalog | Node type | Records |
|---|---|---:|
| Archon | Act | 51 |
| Archon | Individual main quest | 208 |
| World | Series | 101 |
| World | Individual main quest | 1,230 |
| **Total** | | **1,590** |

Source filtering results:

- 3,905 English quest files scanned.
- 272 AQ and 2,673 WQ source candidates identified.
- 208 AQ and 1,230 WQ displayable quests imported.
- 960 non-AQ/WQ records excluded.
- 1,428 hidden or repeatable AQ/WQ records excluded.
- 79 displayable AQ/WQ records held back because their English title is empty; their source IDs are recorded in `quest-import-report.json`.
- The source chapter table has 53 Archon act rows and 132 World Quest series rows. The current catalogs contain 51 and 101 respectively because the remaining chapter/series rows do not yet have a verified English title in the per-ID data used by this importer.

All catalog IDs are unique. Parent references and the retained prerequisite graph resolve within their respective catalogs, and the validator reports no hierarchy or prerequisite cycles.

## Arabic editorial status

The previous 148 curated records were preserved, including their Arabic titles and summaries. The newly discovered records are explicitly marked `needs_translation` with an empty `arabic_name` and null `description_ar`; this is a deliberate, machine-readable distinction from an Arabic translation draft.

The quest schema and validator now permit an empty Arabic name **only** when `translation_status` is `needs_translation`. Any other status still requires a non-empty Arabic name. No imported English title is presented as an Arabic translation, and no record is marked reviewed or approved automatically.

## Automation and verification

- Importer: `scripts/sync_quest_source_metadata.py`.
- Workflow: `.github/workflows/quest-source-metadata-sync.yml`.
- Machine-readable results: `localization/quest-import-report.json`.
- Regression suite: **32 tests passed**.
- Full localization validation: **9 Arabic JSON catalogs and 2,418 records checked; PASS**.
- The successful workflow ran the importer, regression tests, and full catalog validator before committing the expanded data.

## Remaining work

1. Resolve the 79 held-back quest titles using a bounded per-hash lookup source rather than downloading the entire TextMapEN file.
2. Resolve the 2 Archon act titles and 31 World Quest series titles missing from the current per-ID chapter metadata, then add those nodes.
3. Translate the 1,442 newly added records in reviewable batches, including Arabic titles and concise original summaries. Preserve `needs_translation` until each record has actual Arabic text.
4. Review the four omitted prerequisite edges against the in-game quest log and versioned source tables.
5. Cross-check region, Adventure Rank, chapter membership, and prerequisites against the Travel Log and current game data.
6. Add coverage assertions for the full source roster so future source updates reveal additions/removals without silently accepting partial imports.

**Status:** the source roster has been substantially expanded and passes automated validation, but this is not yet a complete quest catalog or a completed Arabic translation. Hidden/repeatable records, unresolved English titles, missing chapter titles, and editorial translation/review remain explicitly tracked.
