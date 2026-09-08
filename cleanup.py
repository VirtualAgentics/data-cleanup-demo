"""Bounded synthetic CSV cleanup demo. See README for the exact supported contract."""

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook

FIELDS = ["id", "name", "amount", "date"]


def transform(rows):
    candidates, exceptions, changes = [], [], []
    for number, row in enumerate(rows, 2):
        if (
            not isinstance(row, dict)
            or set(row) != set(FIELDS)
            or any(not isinstance(v, str) for v in row.values())
        ):
            raise ValueError(f"Malformed CSV record at row {number}")
        clean = {k: v.strip() for k, v in row.items()}
        reason = None
        if any(
            len(v) > 32767
            or any(
                not (
                    c in "\t\n\r"
                    or "\x20" <= c <= "\ud7ff"
                    or "\ue000" <= c <= "\ufffd"
                    or "\U00010000" <= c <= "\U0010ffff"
                )
                for c in v
            )
            for v in clean.values()
        ):
            reason = "Text exceeds Excel cell limit or contains characters unsupported by XML"
        elif not clean["id"] or not clean["name"]:
            reason = "Missing identifier or name"
        elif not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", clean["amount"]):
            reason = "Invalid amount: expected nonnegative decimal, maximum two decimal places"
        elif not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", clean["date"]):
            reason = "Ambiguous/invalid date: expected YYYY-MM-DD"
        else:
            try:
                date.fromisoformat(clean["date"])
            except ValueError:
                reason = "Invalid calendar date"
        if reason:
            exceptions.append([number, reason])
            continue
        clean["amount"] = int(Decimal(clean["amount"]) * 100)
        candidates.append((number, clean))
        for key in FIELDS:
            if row[key] != row[key].strip():
                changes.append([number, key, "Trimmed outer whitespace"])
    groups = {}
    for number, row in candidates:
        groups.setdefault(row["id"], []).append((number, row))
    accepted = []
    for entries in groups.values():
        if any(row != entries[0][1] for _, row in entries):
            exceptions.extend(
                [n, "Conflicting records for identifier: all occurrences withheld"]
                for n, _ in entries
            )
        else:
            accepted.append(entries[0])
            exceptions.extend(
                [n, f"Duplicate of source row {entries[0][0]}"] for n, _ in entries[1:]
            )
    return sorted(accepted), sorted(exceptions), changes


def deliver(source, output):
    # Parse and hash the same bounded snapshot, even if the source later changes.
    with source.open("rb") as handle:
        original = handle.read(1024 * 1024 + 1)
    if len(original) > 1024 * 1024:
        raise ValueError("Input exceeds 1 MiB demo limit")
    reader = csv.DictReader(
        io.StringIO(original.decode("utf-8-sig"), newline=""), strict=True
    )
    if reader.fieldnames != FIELDS:
        raise ValueError("Expected columns: id,name,amount,date")
    rows = []
    for row in reader:
        rows.append(row)
        if len(rows) > 10000:
            raise ValueError("Input exceeds 10000-row demo limit")
    accepted, exceptions, changes = transform(rows)
    output.mkdir(parents=True, exist_ok=False)
    try:
        book = Workbook()
        sheet = book.active
        sheet.title = "Cleaned"
        sheet.append(["source_row", "id", "name", "amount_cents", "date"])
        for number, row in accepted:
            sheet.append([number, row["id"], row["name"], row["amount"], row["date"]])
        for row in sheet:
            for cell in row:
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        with (output / "cleaned.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_row", "id", "name", "amount_cents", "date"])
            for number, row in accepted:
                values = [row["id"], row["name"], str(row["amount"]), row["date"]]
                for i, value in enumerate(values):
                    if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
                        values[i] = "'" + value
                        changes.append(
                            [
                                number,
                                FIELDS[i],
                                "CSV-only apostrophe prefix to prevent formula interpretation; XLSX retains literal original",
                            ]
                        )
                writer.writerow([number, *values])
        for title, header, entries in [
            ("Exceptions", ["source_row", "reason"], exceptions),
            ("Changes", ["source_row", "field", "change"], changes),
        ]:
            ws = book.create_sheet(title)
            ws.append(header)
            for row in entries:
                ws.append(row)
            with (output / (title.lower() + ".csv")).open(
                "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(entries)
        book.save(output / "cleaned.xlsx")
        result = dict(
            input_rows=len(rows),
            clean_rows=len(accepted),
            exception_rows=len(exceptions),
            accepted_total_cents=sum(row["amount"] for _, row in accepted),
            source_sha256=hashlib.sha256(original).hexdigest(),
            note="Total covers accepted rows only; rejected amounts are not silently treated as zero.",
        )
        if result["input_rows"] != result["clean_rows"] + result["exception_rows"]:
            raise RuntimeError("Internal reconciliation failure")
        (output / "reconciliation.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        return result
    except Exception:
        # Only this newly created directory is removed; existing destinations are refused.
        shutil.rmtree(output)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(deliver(args.source, args.output)))
