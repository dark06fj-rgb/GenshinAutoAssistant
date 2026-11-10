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

The current merged catalogs contain **1,922 quest records** across the Archon and World Quest files:

| Catalog | Node type | Records |
|---|---|---:|
| Archon | Act | 51 |
| Archon | Individual main quest | 208 |
| World | Chapter | 67 |
| World | Series | 90 |
| World | Individual main quest | 1,506 |
| **Total** | | **1,922** |

Source filtering results:

- 3,905 English quest files scanned.
- 272 AQ and 2,673 WQ source candidates identified.
- The latest per-ID sync fetched 208 AQ and 1,230 WQ player-facing records. The current World Quest catalog contains 1,506 individual quest nodes, including 276 retained legacy records from the earlier catalog.
- 960 non-AQ/WQ records excluded.
- 1,428 hidden or repeatable AQ/WQ records excluded.
- The 79 IDs previously held back for empty English titles were cross-checked against the pinned Chinese quest records: **78 are internal, test, obsolete, or explicitly unreleased placeholders** and are now excluded from the player-facing catalog; **ID `74173` remains unresolved** because no usable title is present. No Arabic labels were invented for these records. The released World Quest **The Farmer's Treasure** is source ID `72199` and is already translated as `كنز المزارع`; `72109` is an unreleased duplicate.
- The merged catalog has 51 Archon acts, 67 World Quest chapter nodes, and 90 World Quest series nodes. All 67 World Quest chapter titles and all 90 series titles have Arabic draft translations.

All catalog IDs are unique. Parent references and the retained prerequisite graph resolve within their respective catalogs, and the validator reports no hierarchy or prerequisite cycles.

## Arabic editorial status

All 259 Archon nodes have Arabic draft titles. In the current World Quest catalog, all 67 chapter nodes, all 90 series nodes, and all 1,506 individual quest nodes have Arabic draft titles (1,663 World Quest entries total). Only 344 individual World Quest entries currently have a non-empty Arabic summary; 1,162 still lack `description_ar`. Of the 314 individual quests marked `needs_translation` at commit `3faf9c1`, 276 remain in the current catalog and now have Arabic titles, while 38 are absent from the current source roster. The 276 retained legacy records have no corresponding per-ID English quest file in the pinned GI-OnlineQuest snapshot, so their description hashes require a TextMap lookup before faithful summaries can be written. No summaries should be inferred from titles alone.

The quest schema and validator now permit an empty Arabic name **only** when `translation_status` is `needs_translation`. Any other status still requires a non-empty Arabic name. No imported English title is presented as an Arabic translation, and no record is marked reviewed or approved automatically.

## Automation and verification

- Importer: `scripts/sync_quest_source_metadata.py`.
- Workflow: `.github/workflows/quest-source-metadata-sync.yml`.
- Machine-readable results: `localization/quest-import-report.json`.
- Regression suite: **42 tests passed**.
- Full localization validation: **9 Arabic JSON catalogs and 2,796 records checked; PASS**.
- The successful workflow ran the importer, regression tests, and full catalog validator before committing the expanded data.

## Remaining work

1. Revisit the single unresolved source ID `74173` only if a later source snapshot provides a real title; the other 78 IDs have been correctly classified as internal/unreleased placeholders.
2. Continue resolving chapter/series source metadata gaps (2 Archon act titles and 31 World Quest series titles) where a verified English source title becomes available; do not invent nodes or labels.
3. Translate the 1,452 missing World Quest Arabic summaries in reviewable batches, using verified English source descriptions and preserving null when a source description is unavailable. Of the 276 retained legacy records from the 314-item backlog, 274 now have Arabic summaries based on verified English descriptions extracted from the pinned TextMap source. Two descriptions remain unresolved because their source hashes (`2625786622` for quest `77115` and `3439185798` for quest `77307`) were not found; keep their summaries null until a verified source text becomes available. Review all Arabic draft titles for terminology and in-game context.
4. Review the four omitted prerequisite edges against the in-game quest log and versioned source tables.
5. Cross-check region, Adventure Rank, chapter membership, and prerequisites against the Travel Log and current game data.
6. Add coverage assertions for the full source roster so future source updates reveal additions/removals without silently accepting partial imports.

**Status:** all 1,922 AQ/WQ catalog nodes have Arabic draft titles. The current World Quest catalog has 344 Arabic summaries and 1,162 missing summaries. All 67 World Quest chapter titles are Arabic. Within the original 314-item backlog, 274 of the 276 retained records now have source-backed Arabic summaries; two remain unresolved, and 38 records are no longer present in the current source roster. Arabic summary work and editorial review remain incomplete.
