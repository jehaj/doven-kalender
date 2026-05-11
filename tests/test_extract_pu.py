import csv
import io
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

from doven_kalender.extractor.pu import content_xml_to_rows, extract_csv_from_odt, odt_bytes_to_rows


class _FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


def _build_odt_bytes(content_xml: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("content.xml", content_xml)
    return buffer.getvalue()


def test_content_xml_to_rows_reads_table_rows() -> None:
    content_xml = Path("assets/content.xml").read_text(encoding="utf-8")

    rows = content_xml_to_rows(content_xml)

    assert rows[0][:3] == ["Dato", "Titel", "Emne/aktivitet"]
    assert rows[1][:3] == ["8. januar", "Nytårskur", "Fællesspisning v. Fred"]


def test_odt_bytes_to_rows_reads_content_xml() -> None:
    content_xml = Path("assets/content.xml").read_text(encoding="utf-8")
    rows = odt_bytes_to_rows(_build_odt_bytes(content_xml))

    assert rows[0][:3] == ["Dato", "Titel", "Emne/aktivitet"]
    assert rows[1][:3] == ["8. januar", "Nytårskur", "Fællesspisning v. Fred"]


@patch("doven_kalender.extractor.pu.urllib.request.urlopen")
def test_extract_csv_from_odt_writes_csv(mock_urlopen, tmp_path) -> None:
    content_xml = Path("assets/content.xml").read_text(encoding="utf-8")
    mock_urlopen.return_value = _FakeResponse(_build_odt_bytes(content_xml))

    old_cookie = os.environ.get("DOCS_COOKIE")
    os.environ["DOCS_COOKIE"] = "sessionid=abc123"

    csv_path = tmp_path / "output.csv"
    try:
        written_path = extract_csv_from_odt("https://example.com/document.odt", csv_path)
    finally:
        if old_cookie is None:
            os.environ.pop("DOCS_COOKIE", None)
        else:
            os.environ["DOCS_COOKIE"] = old_cookie

    assert written_path == csv_path
    request = mock_urlopen.call_args.args[0]
    assert request.get_header("Cookie") == "sessionid=abc123"
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    assert rows[0][:3] == ["Dato", "Titel", "Emne/aktivitet"]
    assert rows[1][:3] == ["8. januar", "Nytårskur", "Fællesspisning v. Fred"]