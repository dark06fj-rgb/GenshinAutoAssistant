# Materials and Resources Terminology Audit

Audit date: 2026-11-10  
Branch: `arabic-localization-catalog`

## Scope

Reviewed all entries in `ar/materials.json` and `ar/resources.json`, compared shared material names with `ar/glossary.json`, and checked identifiers, Arabic-name coverage, source metadata, and translation status.

## Catalog inventory

| Catalog | Records | Coverage |
|---|---:|---|
| Materials | 5 | Common currencies and wish items |
| Resources | 8 | Gatherable plants, fruits, and ores |
| **Total** | **13** | |

## Name review

### Materials

| Source name | Current Arabic draft | Review |
|---|---|---|
| Mora | مورا | Kept; matches glossary and remains an unverified draft |
| Primogem | الجوهرة الأولية | Kept; matches glossary and remains an unverified draft |
| Original Resin | الريزن الأصلي | Kept; matches glossary and remains an unverified draft |
| Intertwined Fate | القدر المتشابك | Kept; matches glossary and remains an unverified draft |
| Acquaint Fate | قدر التعارف | Kept; matches glossary and remains an unverified draft |

The five material names were checked individually. The shared terms for Mora, Primogem, Original Resin, Intertwined Fate, and Acquaint Fate match the corresponding glossary entries. No name change was justified by this consistency review.

### Resources

| Source name | Current Arabic draft | Review |
|---|---|---|
| Sweet Flower | زهرة حلوة | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Mint | نعناع | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Berry | توت | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Sunsettia | فاكهة الغروب | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Apple | تفاحة | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Crystal Chunk | قطعة كريستالية | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| Iron Chunk | قطعة حديد | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |
| White Iron Chunk | قطعة حديد أبيض | Kept as a concise draft; no authoritative Arabic in-game equivalent was established in this audit |

Resource names are short labels, not verified official translations. In particular, the fictional item label "Sunsettia" is rendered descriptively as "فاكهة الغروب"; this is a proposal rather than an official localized name.

## Shared item-type terminology

Added the following reusable draft terms to `ar/glossary.json` for future catalog viewers, filters, and documentation:

| Source type | Arabic draft |
|---|---|
| Currency | عملة |
| Wish Item | عنصر أمنية |
| Gatherable plant | نبات قابل للجمع |
| Gatherable fruit | ثمرة قابلة للجمع |
| Ore | خام |

The source `item_type` values in the entity records remain unchanged, preserving their machine-readable source labels. A future interface can resolve them through the glossary.

## Structural checks

- Materials: 5; resources: 8; combined: 13.
- Duplicate IDs across these two catalogs: 0.
- Duplicate Arabic names across these two catalogs: 0.
- Missing Arabic names: 0.
- Missing source names or source records: 0.
- All 13 entries remain `draft`.
- All five material names match their existing glossary entries.
- No entries were promoted to `reviewed` or `approved`.

## Limitations

This is a terminology and structural consistency audit, not a professional linguistic review or official HoYoverse localization. The catalog uses genshin-db 7.2 and GenshinData provenance as recorded in the entries. Names remain community proposals and should be compared with Arabic community usage and in-game context before approval. No claim is made that this catalog displays Arabic inside the live game.
