# Weapon Names and Terminology Audit

Audit date: 2026-11-10  
Branch: `arabic-localization-catalog`

## Scope

Reviewed the weapon catalog structure and all 253 Arabic weapon-name records, checking source identifiers, Arabic-name presence, duplicate IDs, duplicate Arabic labels, rarity values, weapon-type identifiers, and consistency needs for weapon classification terminology.

## Catalog inventory

| Weapon type (source identifier) | Arabic catalog label | Records |
|---|---|---:|
| `WEAPON_SWORD_ONE_HAND` | سيف | 60 |
| `WEAPON_CATALYST` | محفّز | 55 |
| `WEAPON_BOW` | قوس | 50 |
| `WEAPON_CLAYMORE` | سيف عظيم | 45 |
| `WEAPON_POLE` | رمح | 43 |
| **Total** | | **253** |

Rarity distribution:

| Rarity | Records |
|---:|---:|
| 1 | 5 |
| 2 | 5 |
| 3 | 24 |
| 4 | 144 |
| 5 | 75 |

## Structural findings

- 253 weapon records were present.
- No duplicate weapon IDs were found.
- No duplicate Arabic weapon names were found after Unicode NFC normalization.
- No Arabic name or source name fields were missing.
- All records use one of the five expected weapon-type identifiers.
- All 253 translation statuses remain `draft`.
- No weapon record was promoted to `reviewed` or `approved`.

## Terminology changes

Added five shared weapon-type terms to `ar/glossary.json`:

| English source term | Arabic draft label |
|---|---|
| Sword | سيف |
| Claymore | سيف عظيم |
| Polearm | رمح |
| Bow | قوس |
| Catalyst | محفّز |

These labels are project conventions for consistent catalog display. They are not official HoYoverse Arabic terminology. The source weapon-type identifiers remain unchanged.

## Linguistic review notes

Weapon proper names include literal translations, transliterations, and mixed naming styles. A structural duplicate check cannot establish whether every individual rendering is the best Arabic equivalent or matches community usage. Names with fictional proper nouns, archaic words, puns, and culturally specific references should receive context-aware human review before any status change. No mass replacement of individual weapon names was made during this pass because no authoritative Arabic localization reference was established for those names.

## Limitations

This audit checks catalog consistency and metadata integrity; it is not a professional linguistic certification. All Arabic weapon names remain unofficial drafts pending community and human review. This catalog does not display Arabic inside the live game.
