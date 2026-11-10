# Automated Localization Validator

## Purpose

`scripts/validate_localization.py` is the repository's offline quality gate for the Arabic reference catalogs. It uses only the Python standard library and does not download game data or alter catalog entries.

## Checks performed

- Parse every JSON catalog under `localization/ar/` and require the six expected catalogs.
- Validate required fields, non-empty source and Arabic labels, supported translation statuses, and HTTP(S) source URLs.
- Detect duplicate IDs within a catalog and across all catalogs.
- Validate glossary record fields and detect repeated or conflicting source terms.
- Compare material/resource labels with exact glossary terms when a shared source term exists.
- Require glossary coverage for material/resource item types.
- Require canonical glossary entries for the seven elements and five character weapon classes used by the character catalog.
- Map upstream weapon type identifiers to the corresponding shared glossary terms.
- Verify every talent's `character_id` exists and its Arabic character label matches the character catalog.
- Report Arabic-script coverage and empty optional Arabic descriptions as warnings rather than silently rewriting content.

## Exit behavior

- Exit code `0`: no structural or cross-reference errors.
- Exit code `1`: one or more errors were found.
- Warnings are visible but do not fail the run.

## Run locally

```bash
python scripts/validate_localization.py
```

The existing GitHub Actions localization validation workflows invoke this same script, so the expanded checks run automatically on their configured push and pull-request events.

## Safety and editorial policy

The validator never changes translations and never promotes a record from `draft` to `reviewed` or `approved`. It checks consistency, not linguistic correctness. A clean run is not proof that Arabic wording is official or professionally reviewed.
