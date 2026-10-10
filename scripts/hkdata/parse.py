"""Format-aware parsing for data.gov.hk endpoints."""

import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


def detect_encoding(data: bytes) -> str:
    """Detect common Unicode BOMs; default to utf-8."""
    if data.startswith(b"\xff\xfe"):
        return "utf-16-le"
    if data.startswith(b"\xfe\xff"):
        return "utf-16-be"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


# Signature bytes of common binary resources. These must never be text-decoded.
_BINARY_MAGIC = (
    (b"PK\x03\x04", "zip"),               # zip (also xlsx/ods/odt)
    (b"PK\x05\x06", "zip"),               # empty zip archive
    (b"%PDF-", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "xls"),  # legacy OLE (xls/doc)
)

_XLSX_EXTS = (".xlsx", ".xlsm", ".ods", ".odt")


def detect_binary(data: bytes, url: Optional[str] = None) -> Optional[str]:
    """Return a binary format label if ``data`` carries a known magic signature.

    Returns ``None`` for text resources. ``url`` refines a zip archive into
    ``xlsx`` when the extension says it is a spreadsheet.
    """
    for magic, fmt in _BINARY_MAGIC:
        if data.startswith(magic):
            if fmt == "zip" and url and url.lower().split("?")[0].endswith(_XLSX_EXTS):
                return "xlsx"
            return fmt
    return None


def _decode_text(data: bytes) -> str:
    """Decode bytes and strip any BOM. Falls back to Big5 for HK government CSVs."""
    encoding = detect_encoding(data)
    try:
        text = data.decode(encoding)
    except UnicodeDecodeError:
        for fallback in ("big5", "big5-hkscs", "gb18030"):
            try:
                text = data.decode(fallback)
                return text.lstrip("\ufeff")
            except UnicodeDecodeError:
                continue
        raise
    return text.lstrip("\ufeff")


def detect_delimiter(text: str) -> str:
    """Guess CSV delimiter from the first line."""
    first_line = text.splitlines()[0] if text else ""
    tab_count = first_line.count("\t")
    comma_count = first_line.count(",")
    return "\t" if tab_count > comma_count else ","


def parse_json(data: bytes) -> Dict[str, Any]:
    """Parse JSON bytes into a Python object."""
    return json.loads(_decode_text(data))


def parse_xml(data: bytes) -> Dict[str, Any]:
    """Parse XML bytes and return a structural summary."""
    text = _decode_text(data)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"format": "xml", "error": f"XML parse error: {exc}"}

    children = list(root)
    sample = []
    for child in children[:3]:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        attrs = dict(child.attrib)
        text_content = (child.text or "").strip()
        sample.append({"tag": tag, "attributes": attrs, "text": text_content})

    root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    return {
        "format": "xml",
        "root_tag": root_tag,
        "child_count": len(children),
        "sample": sample,
    }


def parse_csv(data: bytes) -> Dict[str, Any]:
    """Parse CSV bytes, handling UTF-16-LE and tab-delimited files."""
    encoding = detect_encoding(data)
    text = _decode_text(data)
    delimiter = detect_delimiter(text)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    headers = rows[0] if rows else []
    preview = rows[:6]

    return {
        "format": "csv",
        "encoding": encoding,
        "delimiter": "tab" if delimiter == "\t" else "comma",
        "headers": headers,
        "row_count": max(0, len(rows) - 1),
        "preview": preview,
    }


def looks_like_html(data: bytes) -> bool:
    """Heuristic: does the response look like an HTML viewer page?"""
    text = data[:4096].decode("utf-8", errors="ignore").lower()
    return bool(re.search(r"<!doctype html|<html|<head|<body", text))


def detect_format(data: bytes, content_type: Optional[str] = None, url: Optional[str] = None) -> str:
    """Detect the data format from magic bytes, Content-Type, URL, or content sniffing."""
    # Magic bytes win: an XLSX/ZIP/PDF is binary regardless of its Content-Type
    # (an XLSX Content-Type contains "xml" via "openxmlformats"/"spreadsheetml").
    binary = detect_binary(data, url)
    if binary:
        return binary

    if content_type:
        ct = content_type.lower()
        if "json" in ct:
            return "json"
        if "spreadsheet" in ct or "excel" in ct or "officedocument" in ct:
            return "xlsx"
        if "zip" in ct:
            return "zip"
        if "pdf" in ct:
            return "pdf"
        if "xml" in ct or "rss" in ct:
            return "xml"
        if "csv" in ct or "tab-separated" in ct or "text/tab-separated-values" in ct:
            return "csv"
        if "html" in ct:
            return "html"

    if url:
        url_lower = url.lower().split("?")[0]
        if url_lower.endswith(".json"):
            return "json"
        if url_lower.endswith(".xml"):
            return "xml"
        if url_lower.endswith(".csv"):
            return "csv"
        if url_lower.endswith((".xlsx", ".xlsm", ".ods", ".odt")):
            return "xlsx"
        if url_lower.endswith((".zip", ".xls")):
            return "zip" if url_lower.endswith(".zip") else "xls"
        if url_lower.endswith(".pdf"):
            return "pdf"

    if looks_like_html(data):
        return "html"

    try:
        data.decode("utf-8")
        json.loads(data.decode("utf-8"))
        return "json"
    except Exception:
        pass

    try:
        ET.fromstring(data.decode(detect_encoding(data)))
        return "xml"
    except Exception:
        pass

    # CSV is the fallback for plain text/tabular data.
    return "csv"


_BINARY_FORMATS = frozenset({"zip", "xlsx", "xls", "pdf", "png", "jpeg", "gif"})


def parse_data(
    data: bytes,
    content_type: Optional[str] = None,
    url: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse data bytes according to detected format and return a summary."""
    fmt = detect_format(data, content_type=content_type, url=url)

    if fmt in _BINARY_FORMATS:
        return {
            "format": fmt,
            "note": "Binary resource (archive/document) — download and parse it "
                    "locally; it is not a text/JSON/CSV endpoint.",
            "bytes": len(data),
        }

    if fmt == "html":
        return {
            "format": "html",
            "note": "Response appears to be HTML, not a data endpoint (likely a viewer page).",
        }

    if fmt == "json":
        return {"format": "json", "data": parse_json(data)}

    if fmt == "xml":
        return parse_xml(data)

    return parse_csv(data)
