"""Format-aware parsing for data.gov.hk endpoints."""

import codecs
import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


def _canonical_encoding(name: str) -> Optional[str]:
    """Return the canonical codec name, or None if unknown."""
    try:
        return codecs.lookup(name).name
    except LookupError:
        return None


def _charset_from_content_type(content_type: Optional[str]) -> Optional[str]:
    """Extract a usable ``charset=`` value from an HTTP Content-Type header."""
    if not content_type:
        return None
    match = re.search(r"charset\s*=\s*[\"']?([\w.:+-]+)", content_type, re.IGNORECASE)
    if not match:
        return None
    return _canonical_encoding(match.group(1))


# Ordered CJK fallbacks. Big5 / Big5-HKSCS are the common HK government
# encodings and win ties; GB18030/GBK are tried too, but only when they decode
# *more plausibly* (Big5 and GB18030 overlap heavily, and GB18030 decodes almost
# any byte stream, so first-success alone would silently mis-decode one as the
# other).
_CJK_FALLBACKS = ("big5", "big5hkscs", "gb18030", "gbk")

# Non-ASCII ranges that are plausible in real HK text. Anything else (enclosed
# alphanumerics, arrows, private-use area, etc.) is treated as a mojibake signal.
_ALLOWED_RANGES = (
    (0x3400, 0x4DBF),   # CJK Extension A
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0x3000, 0x303F),   # CJK Symbols and Punctuation
    (0xFE30, 0xFE4F),   # CJK Compatibility Forms
    (0xFF00, 0xFFEF),   # Halfwidth and Fullwidth Forms
    (0x20000, 0x2FFFF),  # CJK Extensions B–F (HKSCS mappings)
)


def _plausibility(text: str) -> Tuple[int, int]:
    """Return ``(implausible, cjk)`` counts for scoring a candidate decoding."""
    implausible = cjk = 0
    for ch in text[:65536]:
        cp = ord(ch)
        if cp < 0x80:
            continue
        if any(lo <= cp <= hi for lo, hi in _ALLOWED_RANGES):
            cjk += 1
        else:
            implausible += 1
    return implausible, cjk


def _best_cjk_encoding(data: bytes) -> Optional[str]:
    """Pick the most plausible CJK decoding (fewest mojibake chars, then HK priority)."""
    best_key = None
    best_enc: Optional[str] = None
    for priority, enc in enumerate(_CJK_FALLBACKS):
        try:
            text = data.decode(enc)
        except UnicodeDecodeError:
            continue
        implausible, cjk = _plausibility(text)
        key = (implausible, -cjk, priority)
        if best_key is None or key < best_key:
            best_key, best_enc = key, enc
    return best_enc


def _bom_encoding(data: bytes) -> Optional[str]:
    for bom, enc in (
        (codecs.BOM_UTF32_LE, "utf-32-le"),
        (codecs.BOM_UTF32_BE, "utf-32-be"),
        (codecs.BOM_UTF8, "utf-8-sig"),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
    ):
        if data.startswith(bom):
            return enc
    return None


def _utf16_without_bom(data: bytes) -> Optional[str]:
    """Detect BOM-less UTF-16 from the NUL-byte distribution of ASCII-heavy text."""
    sample = data[:4096]
    if len(sample) < 8:
        return None
    even, odd = sample[0::2], sample[1::2]
    even_nul = even.count(0) / max(len(even), 1)
    odd_nul = odd.count(0) / max(len(odd), 1)
    if odd_nul > 0.6 and even_nul < 0.2:
        return "utf-16-le"
    if even_nul > 0.6 and odd_nul < 0.2:
        return "utf-16-be"
    return None


def detect_encoding(data: bytes, content_type: Optional[str] = None) -> str:
    """Best-guess the text encoding of ``data`` (never raises).

    Order: explicit ``charset=`` > BOM > BOM-less UTF-16 > strict UTF-8 >
    HK-priority CJK fallbacks (big5, big5-hkscs, gb18030, gbk) > utf-8.
    A Big5/GB18030 file cannot be told apart from bytes alone, so the HK-priority
    order (Big5 first) is the deliberate default; a ``charset=`` hint overrides it.
    """
    if not data:
        return "utf-8"
    hint = _charset_from_content_type(content_type)
    if hint:
        return hint
    bom = _bom_encoding(data)
    if bom:
        return bom
    utf16 = _utf16_without_bom(data)
    if utf16:
        return utf16
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    best = _best_cjk_encoding(data)
    return best or "utf-8"


def decode_text(data: bytes, content_type: Optional[str] = None) -> Tuple[str, str]:
    """Decode ``data`` and return ``(text, encoding_actually_used)``.

    The returned encoding is the one actually used to decode (never a guess that
    differs from reality), and the function never raises — non-decodable bytes are
    replaced and the encoding is marked ``(lossy)``.
    """
    encoding = detect_encoding(data, content_type)
    try:
        text = data.decode(encoding)
    except UnicodeDecodeError:
        return (data.decode(encoding, errors="replace").lstrip("\ufeff"),
                f"{encoding} (lossy)")
    return text.lstrip("\ufeff"), encoding


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


def _decode_text(data: bytes, content_type: Optional[str] = None) -> str:
    """Decode bytes via :func:`decode_text` (never raises)."""
    return decode_text(data, content_type)[0]


def detect_delimiter(text: str) -> str:
    """Guess CSV delimiter from the first line."""
    first_line = text.splitlines()[0] if text else ""
    tab_count = first_line.count("\t")
    comma_count = first_line.count(",")
    return "\t" if tab_count > comma_count else ","


def parse_json(data: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Parse JSON bytes into a Python object."""
    return json.loads(_decode_text(data, content_type))


def parse_xml(data: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Parse XML bytes and return a structural summary."""
    text = _decode_text(data, content_type)
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


def parse_csv(data: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Parse CSV bytes; auto-detect encoding (UTF-8/16, Big5, HKSCS, GB18030) and delimiter."""
    text, encoding = decode_text(data, content_type)
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
        ET.fromstring(decode_text(data)[0])
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
        return {"format": "json", "data": parse_json(data, content_type)}

    if fmt == "xml":
        return parse_xml(data, content_type)

    return parse_csv(data, content_type)
