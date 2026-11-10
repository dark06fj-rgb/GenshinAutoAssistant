# Character Roster Audit — Version 7.2

Audit date: 2026-11-10  
Catalog: `ar/characters.json`  
Target game version: `7.2`

## Result

The character catalog was compared with a current Version 7.2 playable-character list and the official HoYoverse Version 7.2 update announcement.

- Previous catalog size: 118 records.
- Added missing playable characters: 5.
- Current catalog size: 123 records.
- Catalog metadata `game_version` is now `7.2`.
- All Arabic names remain `draft`; none are official HoYoverse Arabic localizations.
- Existing records were preserved; no character record was deleted.

## Added in this audit

| Source name | Catalog ID | Arabic draft | Element | Weapon | Rarity |
|---|---|---|---|---|---:|
| Kamisato Ayato | `character.10000066` | كاميساتو أياتو | Hydro | Sword | 5 |
| Kaeya | `character.10000015` | كايا | Cryo | Sword | 4 |
| Shenhe | `character.10000063` | شينهي | Cryo | Polearm | 5 |
| Skirk | `character.10000114` | سكيرك | Cryo | Sword | 5 |
| Varesa | `character.10000111` | فاريسا | Electro | Catalyst | 5 |

Metadata and stable numeric IDs were checked against the corresponding individual records in [genshin-db](https://github.com/theBowja/genshin-db).

## Previously questioned records

The following names were retained. The current Version 7.2 playable-character list includes them as playable characters, so their presence is not evidence of an NPC or unreleased record:

- Alyosha
- Odette
- Vesna
- Vodyanitsa
- Sandrone
- Lohen
- Nicole
- Prune

## Traveler handling

The catalog retains the existing Aether record as the Traveler's catalog identity. Lumine is the alternate selectable protagonist identity, not an additional independent character entry in this catalog. Elemental alignments/forms (including the Cryo form listed for Version 7.0) are treated as Traveler variants, not separate character records. This avoids multiplying one character into multiple catalog entities.

## Not added

Names listed by the current reference as unreleased, including Danica, Noy, and Anastasya, were not added to the playable roster.

## Sources and confidence

1. [HoYoverse — Version 7.2 Update Details, posted 2026-11-04](https://genshin.hoyoverse.com/en/news/detail/167187): primary source confirming the 7.2 update and the playable debuts of Mitya and Valeriy.
2. [GameWith — All Character List for 7.2, updated 2026-11-09](https://gamewith.net/genshin-impact/article/show/22357): community-maintained current playable roster used to cross-check the full list, Traveler variants, and unreleased names.
3. [genshin-db](https://github.com/theBowja/genshin-db): individual character metadata and IDs for the five added records.

This is a roster completeness audit, not a claim that the Arabic translations have been linguistically approved. Review names and descriptions separately before changing any record to `reviewed` or `approved`.
