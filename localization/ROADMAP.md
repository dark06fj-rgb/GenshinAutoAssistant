# Localization roadmap

1. Establish stable IDs, JSON schema, provenance, and review states. (established)
2. Expand character, weapon, artifact, and material indexes from permitted reference data. (ongoing editorial review)
3. Add original Arabic names and descriptions in small reviewable batches; preserve explicit draft/review states. (ongoing)
4. Maintain resource taxonomy (local specialties, ores, enemy drops, boss drops) and source-backed locations. (ongoing)
5. Maintain separate **Main Story / Archon Quest** and **World Quest** catalogs with stable source IDs, chapter/act/series hierarchy, region, prerequisites, Adventure Rank gates, and version provenance. The current verified catalog contains **1,922 nodes**: 51 Archon acts, 208 Archon quests, 67 World Quest chapters, 90 World Quest series, and 1,506 individual World Quests. All 1,922 nodes have Arabic draft titles.
6. Keep unresolved source records out of the player-facing catalog. Of 79 previously held-back AQ/WQ candidates, 78 were classified from pinned source evidence as internal, test, obsolete, or unreleased placeholders; source ID `74173` remains unresolved. Review the four prerequisite edges omitted to prevent cycles, and restore only verified, acyclic relationships. Never download the 57.7 MB TextMapEN file wholesale.
7. Continue Arabic quest-summary work in reviewable batches. The current catalog has 62 Archon Quest summaries and 481 individual World Quest summaries; **1,025 of the 1,506 individual World Quests still lack Arabic summaries**. Preserve existing editorial text, keep unavailable source descriptions null, and mark new translations as `draft` pending human review. Within the earlier 314-record legacy backlog, 274 retained records have source-backed Arabic summaries; two source hashes remain unresolved and 38 IDs are no longer in the current player-facing roster.
8. Cross-check quest region, Adventure Rank, chapter/series membership, and prerequisites against versioned source data and the in-game Travel Log; do not invent missing metadata or dialogue.
9. Add source-roster coverage assertions and regression tests so future updates expose additions/removals instead of silently accepting partial imports.
10. Offline searchable Archon and World Quest progress lists are integrated into the Android assistant with local completion tracking and series grouping; continue the glossary and broader catalog viewer.
11. Keep any future game integration separate; this catalog alone does not alter the game client.

## Quest scope (required)

- **Main story:** Archon Quest chapters, acts, and individual player-facing main quests.
- **World content:** World Quest series and individual player-facing World Quests, including multi-part chains.
- Track Story Quests (character quests), Hangout Events, Commissions, and Event Quests separately; do not silently mix them into the Archon/World Quest totals.
- Dialogue, voice data, and long narrative text are outside the current catalog scope. Quest titles and short original summaries are in scope.

## Quality gates

- No invented IDs, source text, translations, or unverified locations.
- No copied bulk text unless redistribution rights are confirmed.
- All new translations start as `draft`; untranslated records remain `needs_translation`.
- Keep placeholders and markup intact.
- A reviewer must approve terminology consistency before a release.
- Run the regression suite and full localization validator after each import or translation batch.
