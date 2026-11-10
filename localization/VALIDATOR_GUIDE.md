# Automated Localization Validator

## Purpose

`scripts/validate_localization.py` is the repository's offline quality gate for the Arabic reference catalogs. It uses only the Python standard library and does not download game data or alter catalog entries.

## Checks performed

- Parse every JSON catalog under `localization/ar/` and require the six expected catalogs.
- Validate required fields, stable lowercase IDs, supported catalog categories and translation statuses, non-empty source and Arabic labels, and HTTP(S) source URLs.
- Detect duplicate IDs within a catalog and across all catalogs.
- Validate glossary record fields and detect repeated or conflicting source terms.
- Compare material/resource labels with exact glossary terms when a shared source term exists.
- Require glossary coverage for material/resource item types.
- Require canonical glossary entries for the seven elements and five character weapon classes used by the character catalog.
- Map upstream weapon type identifiers to the corresponding shared glossary terms.
- Verify every talent's `character_id` exists and its Arabic character label matches the character catalog.
- Reject stale editorial notes that claim a populated Arabic talent summary has not yet been translated.
- Enforce a complete three-slot talent matrix (`normal`, `skill`, `burst`) for every non-Traveler character; validate each talent ID's stable name-based slug and slot type, ensure each slug belongs to only one upstream character ID, and reject missing, duplicate, or unsupported slots.
- Enforce the Traveler (Aether) talent matrix: all seven known elements (Anemo, Geo, Electro, Dendro, Hydro, Pyro, Cryo), each with exactly one normal, skill, and burst slot; validate slot IDs and require every Traveler talent to reference `character.aether`.
- Report Arabic-script coverage and empty optional Arabic descriptions as warnings rather than silently rewriting content.

## Exit behavior

- Exit code `0`: no structural or cross-reference errors.
- Exit code `1`: one or more errors were found.
- Warnings are visible but do not fail the run.

## Regression tests

Run the regression suite before changing validator behavior:

```bash
python -m unittest discover -s tests -v
python scripts/validate_localization.py
```

The suite covers a valid fixture and deliberate failures for duplicate cross-catalog IDs, glossary mismatches, dangling talent references, unsafe source URLs, unsupported categories, missing catalogs, malformed JSON, incomplete Traveler element kits, incorrect Traveler character links, unsupported Traveler elements, duplicate Traveler talent slots, incomplete regular-character kits, mismatched regular talent IDs/references, unsupported regular talent types, and duplicate regular talent slots. It also verifies that a complete seven-element/21-slot Traveler fixture passes and that stale review notes cannot contradict populated Arabic summaries. GitHub Actions runs both the tests and the live-catalog validator on relevant changes.

## Run locally

```bash
python scripts/validate_localization.py
```

The existing GitHub Actions localization validation workflows invoke this same script, so the expanded checks run automatically on their configured push and pull-request events.

## Safety and editorial policy

The validator never changes translations and never promotes a record from `draft` to `reviewed` or `approved`. It checks consistency, not linguistic correctness. A clean run is not proof that Arabic wording is official or professionally reviewed.
