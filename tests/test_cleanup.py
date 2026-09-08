import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pytest
from openpyxl import load_workbook

import cleanup


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", ""),
        ("name", " "),
        ("amount", "-1"),
        ("amount", "NaN"),
        ("amount", "1.234"),
        ("date", "01/02/2026"),
        ("date", "2026-02-30"),
    ],
)
def test_transform_invalid_value_is_withheld(field, value):
    row = dict(id="001", name="Demo", amount="1.00", date="2026-01-01")
    row[field] = value
    good, bad, _ = cleanup.transform([row])
    assert good == []
    assert len(bad) == 1


@pytest.mark.parametrize("row", [None, {}, {"id": None}])
def test_transform_malformed_record_rejected(row):
    with pytest.raises((ValueError, TypeError)):
        cleanup.transform([row])


def test_deliver_new_input_preserves_ids_and_reconciles(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text(
        "id,name,amount,date\n009,@demo,3.14,2026-01-01\n010,Other,0.01,2026-01-02\n009,@demo,3.14,2026-01-01\n"
    )
    result = cleanup.deliver(source, tmp_path / "out")
    assert (
        result["clean_rows"],
        result["exception_rows"],
        result["accepted_total_cents"],
    ) == (2, 1, 315)
    book = load_workbook(tmp_path / "out/cleaned.xlsx")
    assert book["Cleaned"]["B2"].value == "009"
    assert book["Cleaned"]["C2"].value == "@demo"
    with ZipFile(tmp_path / "out/cleaned.xlsx") as z:
        tree = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        assert not tree.findall(
            ".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f"
        )
    assert "'@demo" in (tmp_path / "out/cleaned.csv").read_text()
    with pytest.raises(FileExistsError):
        cleanup.deliver(source, tmp_path / "out")


def test_transform_conflicting_identifiers_withholds_all():
    row = dict(id="1", name="Demo", amount="1", date="2026-01-01")
    good, bad, _ = cleanup.transform([row, {**row, "amount": "2"}])
    assert good == []
    assert len(bad) == 2


def test_deliver_wrong_header_does_not_create_output(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("wrong\nvalue\n")
    with pytest.raises(ValueError):
        cleanup.deliver(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()
