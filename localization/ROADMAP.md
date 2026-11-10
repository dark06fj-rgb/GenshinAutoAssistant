# Localization roadmap

1. Establish stable IDs, JSON schema, provenance, and review states. (started)
2. Expand character, weapon, artifact, and material indexes from permitted reference data.
3. Add original Arabic names and descriptions in small reviewable batches.
4. Add resource taxonomy (local specialties, ores, enemy drops, boss drops) and source-backed locations.
5. Establish separate Archon Quest and World Quest catalogs with stable source IDs, chapter/act/series hierarchy, region, prerequisites, Adventure Rank gates, and version provenance. (structure started; data population pending)
6. Import quest metadata in verifiable batches; translate titles and write original short Arabic summaries without copying dialogue or long quest text.
7. Add automated JSON/schema validation and duplicate-ID checks.
8. Build an offline searchable Arabic glossary/catalog viewer.
9. Keep any future game integration separate; this catalog alone does not alter the game client.

## Quality gates

- No invented IDs or unverified locations.
- No copied bulk text unless redistribution rights are confirmed.
- All new translations start as `draft`.
- Keep placeholders and markup intact.
- A reviewer must approve terminology consistency before a release.
