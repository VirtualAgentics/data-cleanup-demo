# Validation evidence

Prepublication validation on 9 September 2026:

- Clean sample-only directory; no operational repository history or customer data.
- Python 3.12.3 and 3.14.0 on Linux ARM64: full test suite passed.
- Ruff 0.16.6: lint and formatting passed.
- GitHub workflow syntax checked with actionlint 1.7.12.
- Runtime and development dependencies audited with pip-audit 2.10.1; see CI for current advisory results.

28 tests passed. The nine-record CSV reconciles to 3 accepted records, 6 exceptions and 3450 cents. Includes literal Excel strings, XML/length limits and cleanup after a simulated permission failure.

GitHub CI adds Python 3.13 and Windows validation. Consult actual run results before claiming those platforms passed. CodeQL and dependency checks are evidence, not a guarantee of defect-free software.
