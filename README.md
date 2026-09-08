# VirtualAgentics — data cleanup demonstration

Original synthetic sample, not client history. Runs on a supplied CSV with exactly `id,name,amount,date` columns (UTF-8, maximum 1 MiB / 10,000 rows).

Rules: trim outer whitespace; require an identifier and name; accept nonnegative amounts with up to two decimal places and at most nine integer digits; accept valid YYYY-MM-DD dates only. Preserve IDs as text. Remove identical normalized duplicates; withhold every occurrence of conflicting valid records sharing an ID. Invalid rows go to an exception log. Do not guess values or dates.

Deliverables: cleaned.xlsx (Cleaned, Exceptions and Changes sheets), cleaned.csv, exceptions.csv, changes.csv and reconciliation.json. Source row numbers refer to logical CSV records, with the header as row 1. Monetary values are integer cents. Totals cover accepted rows only. The XLSX stores strings literally; formula-like strings in the CSV receive a documented apostrophe prefix. Spreadsheet programs can reinterpret ordinary CSV identifiers, so use XLSX to preserve leading zeros.

Run with Python 3.12–3.14:

```sh
python -m venv .venv
# Activate .venv using the command for your shell.
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
python cleanup.py input.csv new-output
```

The output directory must not already exist. For the provided nine-row input, expect three accepted rows, six exceptions, and 3450 accepted cents. A different test input reconciles to 315 cents, showing that outputs are derived from input rather than hardcoded fixture answers.

Limits: this is a narrowly specified demonstration, not a general spreadsheet-repair service. No formula recalculation, macros, external lookups, OCR, tax/currency conversion or automatic correction of uncertain values. Customer scope and acceptance rules must be agreed after sample review. Original input is preserved and its SHA-256 recorded. The tests include duplicates, conflicts, missing identifiers, bad dates/amounts, literal formula-like text, schema rejection and preventing overwrites.


Text longer than 32,767 characters or containing characters unsupported by XML is withheld, not truncated. Amounts and dates use ASCII digits. A single bounded byte snapshot is parsed and hashed; UTF-8 errors and malformed CSV fail the run. Empty physical lines are skipped by Python's CSV reader; quoted multiline fields count as one logical record. Whitespace changes may be recorded for valid candidates subsequently withheld as duplicates or conflicts.

Ordinary write failures remove this run's new output directory. Abrupt termination or power loss can leave incomplete output: only a completed `reconciliation.json` marks successful completion. Output paths must be controlled by the caller and not concurrently modified. No crash-safe filesystem transaction is claimed. The input is never written by this program; its hash identifies the snapshot read, not a later external edit.

CSV apostrophe escaping is not universal formula protection: spreadsheet applications may reinterpret data when importing or re-saving. Prefer the XLSX, which stores supported strings as literal text; do not remove escaping from untrusted CSV data.

Contact: **bdc@virtualagentics.ai**.
