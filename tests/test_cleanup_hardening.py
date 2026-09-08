import csv

import pytest
from openpyxl import Workbook, load_workbook

import cleanup


@pytest.mark.parametrize(
    "name",
    ["x" * 32768, "a\x00b", "a\ufffeb", "a\ud800b"],
    ids=["oversized", "nul", "noncharacter", "surrogate"],
)
def test_transform_unrepresentable_excel_text_withholds_row(name):
    good, bad, _ = cleanup.transform(
        [dict(id="1", name=name, amount="1", date="2026-01-01")]
    )
    assert good == []
    assert len(bad) == 1


@pytest.mark.parametrize("amount", ["١٢", "１２", "1e2"])
def test_transform_non_ascii_amount_withholds_row(amount):
    good, bad, _ = cleanup.transform(
        [dict(id="1", name="Demo", amount=amount, date="2026-01-01")]
    )
    assert good == []
    assert len(bad) == 1


def test_deliver_unclosed_quote_rejects_without_output(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text('id,name,amount,date\n1,"Demo,1,2026-01-01')
    with pytest.raises((ValueError, csv.Error)):
        cleanup.deliver(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_deliver_save_failure_removes_own_partial_output(tmp_path, monkeypatch):
    source = tmp_path / "input.csv"
    source.write_text("id,name,amount,date\n1,Demo,1,2026-01-01\n")

    def deny_save(self, filename):
        raise PermissionError("fixture: output unavailable")

    monkeypatch.setattr(Workbook, "save", deny_save)
    with pytest.raises(PermissionError):
        cleanup.deliver(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()
    assert source.exists()


@pytest.mark.parametrize(
    "name",
    ["=1+1", "+1+1", "-1+1", "@SUM(A1)", "#N/A", "x" * 32767],
    ids=["equals", "plus", "minus", "at", "error-text", "max-length"],
)
def test_deliver_excel_preserves_literal_text(tmp_path, name):
    source = tmp_path / "input.csv"
    with source.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(cleanup.FIELDS)
        writer.writerow(["001", name, "1", "2026-01-01"])
    cleanup.deliver(source, tmp_path / "out")
    book = load_workbook(tmp_path / "out/cleaned.xlsx")
    try:
        assert book["Cleaned"]["C2"].value == name
        assert book["Cleaned"]["C2"].data_type == "s"
    finally:
        book.close()
