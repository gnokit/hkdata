import json
import urllib.error
from unittest.mock import patch

from hkdata.search import _build_search_url, _fetch_search, search_multiple


def test_build_search_url_encodes_keyword():
    url = _build_search_url("unemployment district", page=1, rows=50)
    assert ("q=unemployment%20district" in url) or ("q=unemployment+district" in url)
    assert "rows=50" in url
    assert "start=0" in url


def test_build_search_url_encodes_unicode():
    url = _build_search_url("長者", page=2, rows=20)
    assert "%E9%95%B7%E8%80%85" in url
    assert "start=20" in url


class _MockResponse:
    def __init__(self, payload, status=200):
        self._payload = json.dumps(payload).encode("utf-8")
        self.code = status
        self.headers = {"Content-Type": "application/json"}

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def _mock_response(payload, status=200):
    return _MockResponse(payload, status)


def test_fetch_search_parses_results():
    payload = {
        "result": {
            "count": 2,
            "results": [
                {"name": "ds-one", "title": "One", "notes": "First"},
                {"name": "ds-two", "title": "Two", "notes": "Second"},
            ],
        }
    }
    with patch("hkdata.search.urllib.request.urlopen", return_value=_mock_response(payload)):
        keyword, result = _fetch_search("transport")
    assert keyword == "transport"
    assert result["count"] == 2
    assert len(result["datasets"]) == 2
    assert result["datasets"][0]["id"] == "ds-one"


def test_fetch_search_empty_results():
    payload = {"result": {"count": 0, "results": []}}
    with patch("hkdata.search.urllib.request.urlopen", return_value=_mock_response(payload)):
        keyword, result = _fetch_search("nonsense")
    assert result["count"] == 0
    assert result["datasets"] == []


def test_fetch_search_http_error():
    def raise_error(*args, **kwargs):
        raise urllib.error.HTTPError("url", 400, "Bad Request", {}, None)

    with patch("hkdata.search.urllib.request.urlopen", side_effect=raise_error):
        keyword, result = _fetch_search("bad query")
    assert result["error"].startswith("HTTP 400")


def test_search_multiple_deduplicates():
    payload = {
        "result": {
            "count": 1,
            "results": [{"name": "ds-one", "title": "One", "notes": "First"}],
        }
    }
    with patch("hkdata.search.urllib.request.urlopen", return_value=_mock_response(payload)):
        results = search_multiple(["vessel", "ship"], parallel=False)
    assert len(results) == 2
    assert results[0][0] == "vessel"
    assert results[1][0] == "ship"
