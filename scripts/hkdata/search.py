"""CKAN package_search client for data.gov.hk."""

import json
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Tuple

from .common import API_BASE_URL, USER_AGENT


def _build_search_url(keyword: str, page: int = 1, rows: int = 50) -> str:
    offset = (page - 1) * rows
    params = urllib.parse.urlencode({
        "q": keyword,
        "rows": rows,
        "start": offset,
    })
    return f"{API_BASE_URL}package_search?{params}"


def _fetch_search(keyword: str, page: int = 1, rows: int = 50) -> Tuple[str, dict]:
    """Fetch search results for a single keyword.

    Returns a tuple of (keyword, result_dict) where result_dict contains:
      - datasets: list of dataset dicts with keys id, title, notes
      - count: total matching count
      - page: page number
      - error: error message string, or None
    """
    url = _build_search_url(keyword, page=page, rows=rows)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return keyword, {"datasets": [], "count": 0, "page": page, "error": f"HTTP {exc.code}: {exc.reason}"}
    except urllib.error.URLError as exc:
        return keyword, {"datasets": [], "count": 0, "page": page, "error": f"Network error: {exc.reason}"}
    except json.JSONDecodeError as exc:
        return keyword, {"datasets": [], "count": 0, "page": page, "error": f"Invalid JSON: {exc}"}

    result = data.get("result", {})
    datasets = []
    for ds in result.get("results", []):
        datasets.append({
            "id": ds.get("name", "N/A"),
            "title": ds.get("title", "N/A"),
            "notes": ds.get("notes", "N/A"),
        })
    return keyword, {
        "datasets": datasets,
        "count": result.get("count", 0),
        "page": page,
        "error": None,
    }


def search(keyword: str, page: int = 1, rows: int = 50) -> dict:
    """Search data.gov.hk for a single keyword."""
    _, result = _fetch_search(keyword, page=page, rows=rows)
    return result


def search_multiple(
    keywords: Iterable[str],
    page: int = 1,
    rows: int = 50,
    parallel: bool = True,
) -> List[Tuple[str, dict]]:
    """Search data.gov.hk for multiple keywords.

    Returns a list of (keyword, result_dict) tuples in the original keyword
    order if sequential, or completion order if parallel.
    """
    keywords = list(keywords)
    if not keywords:
        return []

    if parallel and len(keywords) > 1:
        results = {}
        with ThreadPoolExecutor(max_workers=min(len(keywords), 5)) as executor:
            futures = {
                executor.submit(_fetch_search, kw, page, rows): kw
                for kw in keywords
            }
            for future in as_completed(futures):
                kw, result = future.result()
                results[kw] = result
        return [(kw, results[kw]) for kw in keywords]

    return [_fetch_search(kw, page=page, rows=rows) for kw in keywords]
