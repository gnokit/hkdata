import json

from hkdata.parse import (
    decode_text,
    detect_binary,
    detect_delimiter,
    detect_encoding,
    detect_format,
    parse_csv,
    parse_data,
    parse_json,
    parse_xml,
)


def test_detect_encoding_utf8():
    assert detect_encoding(b"hello") == "utf-8"


def test_detect_encoding_utf16_le():
    assert detect_encoding(b"\xff\xfetest") == "utf-16-le"


def test_detect_encoding_utf16_be():
    assert detect_encoding(b"\xfe\xfftest") == "utf-16-be"


def test_detect_encoding_utf8_sig():
    assert detect_encoding(b"\xef\xbb\xbftest") == "utf-8-sig"


def test_detect_delimiter_comma():
    assert detect_delimiter("a,b,c\n1,2,3") == ","


def test_detect_delimiter_tab():
    assert detect_delimiter("a\tb\tc\n1\t2\t3") == "\t"


def test_parse_json():
    data = b'{"key": "value"}'
    result = parse_json(data)
    assert result == {"key": "value"}


def test_parse_xml():
    data = b"""<?xml version="1.0"?><root><item id="1">A</item><item id="2">B</item></root>"""
    result = parse_xml(data)
    assert result["format"] == "xml"
    assert result["root_tag"] == "root"
    assert result["child_count"] == 2


def test_parse_csv_comma():
    data = b"name,value\nfoo,1\nbar,2"
    result = parse_csv(data)
    assert result["format"] == "csv"
    assert result["encoding"] == "utf-8"
    assert result["delimiter"] == "comma"
    assert result["headers"] == ["name", "value"]
    assert result["row_count"] == 2


def test_parse_csv_utf16_le_tab():
    text = "name\tvalue\nfoo\t1\nbar\t2"
    data = text.encode("utf-16-le")
    result = parse_csv(b"\xff\xfe" + data)
    assert result["encoding"] == "utf-16-le"
    assert result["delimiter"] == "tab"
    assert result["headers"] == ["name", "value"]


def test_detect_format_json():
    assert detect_format(b'{"a": 1}', content_type="application/json") == "json"


def test_detect_format_xml_by_extension():
    assert detect_format(b"<root/>", url="http://example.com/data.xml") == "xml"


def test_detect_format_html():
    data = b"<!DOCTYPE html><html><body>hi</body></html>"
    assert detect_format(data) == "html"


def test_parse_data_json():
    result = parse_data(b'{"a": 1}', content_type="application/json")
    assert result["format"] == "json"
    assert result["data"] == {"a": 1}


def test_parse_data_csv():
    result = parse_data(b"a,b\n1,2")
    assert result["format"] == "csv"
    assert result["headers"] == ["a", "b"]


# ---------------------------------------------------------------------------
# Binary resources (XLSX/ZIP/PDF) must never be text-decoded
# ---------------------------------------------------------------------------


def test_detect_binary_zip():
    assert detect_binary(b"PK\x03\x04rest") == "zip"


def test_detect_binary_xlsx_by_extension():
    assert detect_binary(b"PK\x03\x04rest", url="http://x/DC_21C.xlsx") == "xlsx"


def test_detect_binary_pdf():
    assert detect_binary(b"%PDF-1.7\nstuff") == "pdf"


def test_detect_binary_none_for_text():
    assert detect_binary(b"a,b\n1,2") is None


def test_detect_format_zip_content_type():
    assert detect_format(b"\x00\x01\x02p", content_type="application/zip") == "zip"


def test_parse_data_zip_does_not_crash():
    result = parse_data(b"PK\x03\x04\x00\x00binarydata", url="http://x/DC_21C.zip")
    assert result["format"] == "zip"
    assert "note" in result and result["bytes"] > 0


def test_parse_data_xlsx_does_not_crash():
    result = parse_data(b"PK\x03\x04\x00\x00binarydata", url="http://x/DC_21C.xlsx")
    assert result["format"] == "xlsx"


def test_parse_data_xls_by_magic():
    result = parse_data(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00")
    assert result["format"] == "xls"


def test_detect_format_xlsx_content_type_with_xml_substring():
    # The real XLSX Content-Type contains "xml" (openxmlformats/spreadsheetml)
    # but must be treated as a spreadsheet, never as XML.
    ct = ("application/vnd.openxmlformats-officedocument."
          "spreadsheetml.sheet")
    assert detect_format(b"PK\x03\x04stuff", content_type=ct,
                         url="http://x/a.xlsx") == "xlsx"


def test_detect_format_xlsx_content_type_without_magic():
    ct = ("application/vnd.openxmlformats-officedocument."
          "spreadsheetml.sheet")
    assert detect_format(b"\x00\x01binary", content_type=ct) == "xlsx"


# ---------------------------------------------------------------------------
# HK text encodings: UTF-16 (BOM-less), Big5, HKSCS, GB18030
# ---------------------------------------------------------------------------


def test_detect_encoding_utf16_le_without_bom():
    assert detect_encoding("name\tvalue\nfoo\t1".encode("utf-16-le")) == "utf-16-le"


def test_detect_encoding_utf16_be_without_bom():
    assert detect_encoding("name\tvalue\nfoo\t1".encode("utf-16-be")) == "utf-16-be"


def test_detect_encoding_charset_hint_wins():
    assert detect_encoding(b"\x80\x81\x82", "text/csv; charset=gb18030") == "gb18030"


def test_decode_text_never_raises_on_unknown_bytes():
    text, encoding = decode_text(bytes(range(256)))
    assert isinstance(text, str)          # lossy fallback, no exception
    assert "lossy" in encoding


def test_parse_csv_big5_labels_and_decodes():
    data = "地區,數目\n九龍,1".encode("big5")
    result = parse_csv(data)
    assert result["encoding"] == "big5"
    assert result["headers"] == ["地區", "數目"]


def test_parse_csv_gb18030_not_misread_as_big5():
    # A GB18030 file is also valid Big5; it must be scored as GB18030, not mojibake.
    data = "地区,数目\n九龙,1".encode("gb18030")
    result = parse_csv(data)
    assert result["encoding"] in ("gb18030", "gbk")
    assert result["headers"] == ["地区", "数目"]


def test_parse_csv_big5hkscs():
    data = "地區,數目\n鰂魚涌".encode("big5hkscs")   # 鰂 is HKSCS-only
    result = parse_csv(data)
    assert result["encoding"] == "big5hkscs"
    assert "鰂魚涌" in result["preview"][1]


def test_parse_csv_utf8_chinese_labelled_utf8():
    data = "地區,數目\n九龍,1".encode("utf-8")
    result = parse_csv(data)
    assert result["encoding"] == "utf-8"
    assert result["headers"] == ["地區", "數目"]


def test_parse_data_honours_charset_hint():
    data = "地区,数目\n九龙,1".encode("gb18030")
    result = parse_data(data, content_type="text/csv; charset=gb18030")
    assert result["format"] == "csv"
    assert result["encoding"] == "gb18030"
