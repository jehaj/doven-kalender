"""
This script converts an ODF XML file (like content.xml from an ODT document) into a CSV format.

An example of the use of this script is downloading an ODT file (e.g., from Google Docs), extracting the content.xml file from the ODT archive, and then running this script to convert the table data into a CSV file. Hopefully, this would be done automatically in a workflow that handles the ODT file extraction and processing.

It is written by Gemini 3.0 Flash (05/02-2026). It has been tested on a single content.xml file, and may require adjustments for different ODF structures or namespaces.
"""

import csv
import xml.etree.ElementTree as ET

# Define all relevant ODF namespaces
namespaces = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}


def get_full_text(element):
    """Recursively collects all text from an element and its children."""
    return "".join(element.itertext()).strip()


def convert_odt_xml_to_csv(xml_path, csv_path, table_name="Table1"):
    # If parsing a string snippet, use ET.fromstring(xml_string)
    # If parsing the file, use ET.parse(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    table = root.find(f".//table:table[@table:name='{table_name}']", namespaces)

    if table is None:
        print(f"Table '{table_name}' not found.")
        return

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in table.findall(".//table:table-row", namespaces):
            row_data = []
            for cell in row.findall(".//table:table-cell", namespaces):
                # Handle repeated columns (if any)
                repeat = cell.get(f"{{{namespaces['table']}}}number-columns-repeated")
                count = int(repeat) if repeat else 1

                # Extract text from all paragraphs within the cell
                paragraphs = cell.findall(".//text:p", namespaces)
                # Join multiple paragraphs with a newline to preserve cell structure
                cell_content = "\n".join([get_full_text(p) for p in paragraphs])

                for _ in range(count):
                    row_data.append(cell_content)

            # Write row if it contains any data
            if any(row_data):
                writer.writerow(row_data)


if __name__ == "__main__":
    convert_odt_xml_to_csv("content.xml", "output.csv")
