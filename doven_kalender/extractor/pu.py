"""Helpers for extracting the PU calendar table from an ODT document."""

from __future__ import annotations

import csv
import io
import os
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


def _cell_text(cell: ET.Element) -> str:
    paragraphs: list[str] = []
    for paragraph in cell.findall("text:p", NS):
        paragraph_text = _normalize_text("".join(paragraph.itertext()))
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n".join(paragraphs)


def content_xml_to_rows(content_xml: str) -> list[list[str]]:
    root = ET.fromstring(content_xml)
    table = root.find(".//table:table", NS)
    if table is None:
        raise ValueError("ODT document does not contain a table")

    rows: list[list[str]] = []
    for row in table.findall("table:table-row", NS):
        cells: list[str] = []
        for cell in row.findall("table:table-cell", NS):
            cell_text = _cell_text(cell)
            repeat = int(cell.attrib.get(f"{{{NS['table']}}}number-columns-repeated", "1"))
            cells.extend([cell_text] * repeat)

        if any(cells):
            rows.append(cells)

    return rows


def odt_bytes_to_rows(odt_bytes: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(odt_bytes)) as archive:
        try:
            content_xml = archive.read("content.xml").decode("utf-8")
        except KeyError as error:
            raise ValueError("ODT document does not contain content.xml") from error

    return content_xml_to_rows(content_xml)


def download_odt(document_url: str, timeout: float = 30.0) -> bytes:
    cookie = os.getenv("DOCS_COOKIE")
    if not cookie:
        raise ValueError("DOCS_COOKIE environment variable is required to download the PU document")

    request = urllib.request.Request(
        document_url,
        headers={"User-Agent": "Mozilla/5.0", "Cookie": cookie},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def extract_csv_from_odt(document_url: str, csv_file: Path, timeout: float = 30.0) -> Path:
    rows = odt_bytes_to_rows(download_odt(document_url, timeout=timeout))
    if not rows:
        raise ValueError("ODT document did not contain any table rows")

    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with csv_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    return csv_file