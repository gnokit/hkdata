import json

from hkdata.parse import (
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
