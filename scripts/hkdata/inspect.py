"""CKAN package_show client for data.gov.hk."""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Tuple, Union

from .common import API_BASE_URL, USER_AGENT


def _fetch_info(dataset_id: str) -> Tuple[str, dict]:
    """Fetch package_show for a single dataset ID.

    Returns (dataset_id, result_dict). result_dict contains:
      - data: raw CKAN package dict, or None on error
      - error: error message string, or None
    """
    params = urllib.parse.urlencode({"id": dataset_id})
    url = f"{API_BASE_URL}package_show?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return dataset_id, {"data": None, "error": f"HTTP {exc.code}: {exc.reason}"}
    except urllib.error.URLError as exc:
        return dataset_id, {"data": None, "error": f"Network error: {exc.reason}"}
    except json.JSONDecodeError as exc:
        return dataset_id, {"data": None, "error": f"Invalid JSON: {exc}"}

    return dataset_id, {"data": payload.get("result"), "error": None}


def info(dataset_id: str) -> dict:
    """Return package_show result for a single dataset ID."""
    _, result = _fetch_info(dataset_id)
    if result["error"]:
        raise RuntimeError(result["error"])
    return result["data"]


def info_multiple(dataset_ids: Iterable[str], parallel: bool = True) -> List[dict]:
    """Return package_show results for multiple dataset IDs.

    Returns a list of result dicts in the same order as the input IDs.
    """
    ids = list(dataset_ids)
    if not ids:
        return []

    if parallel and len(ids) > 1:
        results = {}
        with ThreadPoolExecutor(max_workers=min(len(ids), 5)) as executor:
            futures = {executor.submit(_fetch_info, dsid): dsid for dsid in ids}
            for future in as_completed(futures):
                dsid, result = future.result()
                results[dsid] = result
        return [results[dsid] for dsid in ids]

    return [_fetch_info(dsid)[1] for dsid in ids]
