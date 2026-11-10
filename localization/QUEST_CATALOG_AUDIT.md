# Quest catalog audit — version 7.2 baseline

## Scope

This audit establishes the missing quest-data work as two independent catalogs:

- **Archon Quests**: chapter, act, and individual quest nodes, with stable IDs and prerequisite relationships.
- **World Quests**: quest-series and individual quest nodes, with region and prerequisite relationships.

Story Quests, Hangout Events, Commissions, and Event Quests are not silently mixed into either catalog. They require separate scope decisions and files.

## Source assessment

- The current `genshin-db` data-folder index documents characters, talents, weapons, artifacts, materials, and other categories, but does not expose a dedicated quest catalog in its documented query functions. It is therefore not sufficient by itself for quest coverage.
- GenshinData is the intended technical reference for stable quest/chapter identifiers and structured relationships, subject to confirming access to the relevant versioned tables.
- Community parsers such as GenshinScripts document extraction of World Quest IDs from `MainQuestExcelConfigData` and chapter structures for Archon Quests. They are leads for extraction logic, not translation authorities.
- The Genshin Impact Wiki quest index and Travel Log are useful cross-checks for titles, hierarchy, and prerequisite graphs. Individual records still need version-aware verification.

## Data model

Each record should preserve the upstream identifier and identify its node type (`chapter`, `act`, `series`, or `quest`). Where supported by the source, record parent, chapter/act/series IDs, sequence, region, prerequisite quest IDs, Adventure Rank gate, and version introduced. Unknown values must remain absent or null rather than guessed.

Arabic titles and concise summaries are original community drafts. Do not copy dialogue, long narrative descriptions, voice files, or artwork into this catalog.

## Current state

- `ar/quests_archon.json`: initialized, **0 records imported**.
- `ar/quests_world.json`: initialized, **0 records imported**.
- `schema/quest.schema.json`: quest metadata contract added.
- Automated validator now requires both catalogs to exist and validates their generic entity fields, IDs, source URLs, and translation status.
- No quest has been marked reviewed or approved.

## Remaining work

1. Obtain a stable, versioned quest index for the 7.2 baseline and record its exact commit/release provenance.
2. Build and test an importer that preserves source IDs and hierarchy without importing dialogue.
3. Populate Archon Quest chapter/act/quest nodes and World Quest series/quest nodes in reviewable batches.
4. Cross-check prerequisite graphs and Adventure Rank gates against the Travel Log and versioned source tables.
5. Write original Arabic titles and short summaries; leave ambiguous translations as `needs_context`.
6. Add validator rules for parent references, prerequisite references, cycles, and sequence consistency, plus regression tests.
7. Publish coverage counts only after reconciling the imported roster against the source index.

**This is scaffolding, not a completed quest translation.** Empty catalogs deliberately make the missing coverage visible rather than presenting a fabricated or partial list as complete.
