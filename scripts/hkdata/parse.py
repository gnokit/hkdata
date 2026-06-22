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
    """Detect the data format from Content-Type, URL, or content sniffing."""
    if content_type:
        ct = content_type.lower()
        if "json" in ct:
            return "json"
        if "xml" in ct or "rss" in ct:
            return "xml"
        if "csv" in ct or "tab-separated" in ct or "text/tab-separated-values" in ct:
            return "csv"
        if "html" in ct:
            return "html"

    if url:
        url_lower = url.lower()
        if url_lower.endswith(".json"):
            return "json"
        if url_lower.endswith(".xml"):
            return "xml"
        if url_lower.endswith(".csv"):
            return "csv"

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


def parse_data(
    data: bytes,
    content_type: Optional[str] = None,
    url: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse data bytes according to detected format and return a summary."""
    fmt = detect_format(data, content_type=content_type, url=url)

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
