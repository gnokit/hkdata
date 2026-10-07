"""Offline catalog: seed, crawl, and shard storage.

``package_search`` (Solr) only sees ~631 of the ~3,822 datasets that
``package_list`` (DB-backed) returns, so it cannot be used as the catalog.
This module builds a complete local catalog from the reliable endpoints:

  * ``package_list``  -> seed of dataset IDs (1 request, no auth)
  * ``package_show``  -> full metadata per dataset (crawl)

Storage layout::

    references/catalog-names.json     committed seed, sorted IDs
    data/catalog/catalog-NNN.jsonl    sanitized records, 500/shard (committed)
    data/catalog/manifest.json        sync bookkeeping

Search lives in :mod:`hkdata.vectors` (ChromaDB, under ``.cache/``). Shards are
chunked by *sorted* ID so the ID -> shard mapping is deterministic.

Each line is a **sanitized projection** of a ``package_show`` result — only the
fields the search/embed layer needs (see :data:`STORE_FIELDS`). Personal contact
details (author/maintainer emails and phones, ``creator_user_id``) and other CKAN
bookkeeping are stripped by :func:`sanitize` on write, so shards are safe to
commit and the vector store can be rebuilt without re-crawling.
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .common import USER_AGENT

ROOT = Path(__file__).parent.parent.parent
REFERENCES_DIR = ROOT / "references"
# Shards are a sanitized projection of package_show, so they can be committed.
RAW_DIR = ROOT / "data" / "catalog"
# Derived, regenerable artifacts (the ChromaDB store) stay local.
CACHE_DIR = ROOT / ".cache" / "catalog"

NAMES_PATH = REFERENCES_DIR / "catalog-names.json"

RSS_FEED_URL = "https://data.gov.hk/filestore/feeds/data_rss_en.xml"
SHARD_SIZE = 500
DEFAULT_RATE = 2.0  # requests per second
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# data.gov.hk serves the same dataset IDs with localized metadata per locale.
LOCALE_HOSTS = {"en": "en-data", "tc": "tc-data", "sc": "sc-data"}
DEFAULT_LANGS = ("en",)

# Locale fields kept from non-English package_show responses (the text-bearing
# fields; the rest is redundant with the English record).
_LOCALE_KEEP = ("title", "notes", "organization", "groups", "tags")

# Allowlist for stored shards. Everything the search/embed layer needs, and
# nothing that carries personal contact details (author/maintainer emails and
# phones, creator_user_id) or other non-essential CKAN bookkeeping.
STORE_FIELDS = (
    "name", "title", "notes", "url", "organization", "groups", "tags",
    "resources", "update_frequency", "isopen", "metadata_modified",
    "license_title", "locales", "data_dictionary",
)
_ORG_FIELDS = ("title", "name")
_RESOURCE_FIELDS = ("format", "name", "url", "is_api")

_RSS_DATASET_RE = re.compile(r"/(?:en|tc|sc)-data/dataset/([^/]+)/resource/")


@dataclass(frozen=True)
class CatalogPaths:
    """Filesystem locations used by the catalog commands."""

    names_path: Path
    raw_dir: Path


def default_paths() -> CatalogPaths:
    return CatalogPaths(names_path=NAMES_PATH, raw_dir=RAW_DIR)


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------


def parse_langs(value: str) -> List[str]:
    """Parse a ``--lang`` value (e.g. ``en,tc``) into a validated locale list."""
    langs = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not langs:
        raise ValueError("No locales given")
    unknown = [lang for lang in langs if lang not in LOCALE_HOSTS]
    if unknown:
        raise ValueError(f"Unknown locale(s): {', '.join(unknown)} "
                         f"(supported: {', '.join(LOCALE_HOSTS)})")
    if "en" not in langs:
        langs.insert(0, "en")
    return list(dict.fromkeys(langs))


def _api_base(locale: str) -> str:
    return f"https://data.gov.hk/{LOCALE_HOSTS[locale]}/api/3/action/"


def _api_get(action: str, params: Optional[Dict[str, str]] = None,
             locale: str = "en") -> dict:
    """GET a CKAN action endpoint and return the parsed JSON body."""
    url = _api_base(locale) + action
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_package_list(locale: str = "en") -> List[str]:
    """Return the full DB-backed list of dataset IDs, sorted."""
    data = _api_get("package_list", locale=locale)
    names = data.get("result", [])
    if not isinstance(names, list):
        raise RuntimeError("Unexpected package_list response")
    return sorted(names)


def fetch_package_show(name: str, locale: str = "en") -> dict:
    """Return one dataset's raw metadata (the ``result`` object)."""
    data = _api_get("package_show", {"id": name}, locale=locale)
    result = data.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected package_show response for {name}")
    return result


def _org_title(record: dict) -> str:
    org = record.get("organization")
    if isinstance(org, dict):
        return org.get("title") or org.get("name") or ""
    return ""


def _trim_locale(result: dict) -> dict:
    """Keep only the text-bearing fields of a localized package_show result."""
    trimmed = {key: result[key] for key in _LOCALE_KEEP if key in result}
    org = trimmed.get("organization")
    if isinstance(org, dict):
        trimmed["organization"] = {"title": org.get("title") or org.get("name") or ""}
    return trimmed


def fetch_changed_ids(feed_url: str = RSS_FEED_URL) -> List[str]:
    """Parse the data.gov.hk RSS change feed into a sorted list of dataset IDs."""
    request = urllib.request.Request(feed_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
        raw = response.read()
    root = ET.fromstring(raw)
    names = set()
    for item in root.findall(".//item"):
        link = item.findtext("link") or ""
        match = _RSS_DATASET_RE.search(link)
        if match:
            names.add(match.group(1))
    return sorted(names)


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def load_seed(paths: CatalogPaths) -> List[str]:
    if not paths.names_path.exists():
        return []
    with paths.names_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return list(data.get("names", []))


def save_seed(names: Iterable[str], paths: CatalogPaths) -> dict:
    names = sorted(set(names))
    payload = {
        "version": 1,
        "count": len(names),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sha256": hashlib.sha256("\n".join(names).encode("utf-8")).hexdigest(),
        "names": names,
    }
    paths.names_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(
        paths.names_path,
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
    )
    return payload


# ---------------------------------------------------------------------------
# Shards
# ---------------------------------------------------------------------------


def shard_count(names: Iterable[str], shard_size: int = SHARD_SIZE) -> int:
    total = len(list(names))
    if total == 0:
        return 0
    return (total + shard_size - 1) // shard_size


def shard_path(raw_dir: Path, index: int) -> Path:
    return raw_dir / f"catalog-{index:03d}.jsonl"


def _chunk(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _sanitize_locale(view: dict) -> dict:
    out = {k: view[k] for k in _LOCALE_KEEP if k in view}
    org = out.get("organization")
    if isinstance(org, dict):
        out["organization"] = {k: org.get(k) for k in _ORG_FIELDS if org.get(k)}
    return out


def sanitize(record: dict) -> dict:
    """Reduce a raw ``package_show`` result to the storable, PII-free fields."""
    out = {k: record[k] for k in STORE_FIELDS if k in record}
    org = out.get("organization")
    if isinstance(org, dict):
        out["organization"] = {k: org.get(k) for k in _ORG_FIELDS if org.get(k)}
    if "resources" in out:
        out["resources"] = [
            {k: r.get(k) for k in _RESOURCE_FIELDS if r.get(k) is not None}
            for r in record.get("resources") or []
        ]
    locales = out.get("locales")
    if isinstance(locales, dict):
        out["locales"] = {loc: _sanitize_locale(view)
                          for loc, view in locales.items() if isinstance(view, dict)}
    return out


def load_records(paths: CatalogPaths) -> Dict[str, dict]:
    """Load every shard into a ``name -> result`` mapping (last line wins)."""
    records: Dict[str, dict] = {}
    for path in sorted(paths.raw_dir.glob("catalog-*.jsonl")):
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    # Torn trailing line from an interrupted crawl: skip it.
                    continue
                name = record.get("name")
                if name:
                    records[name] = record
    return records


def write_shards(records: Dict[str, dict], names: List[str], paths: CatalogPaths,
                 shard_size: int = SHARD_SIZE) -> int:
    """Atomically rewrite shards so they reflect ``names`` sorted and chunked."""
    ordered = sorted(set(names) | set(records))
    paths.raw_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    chunks = _chunk(ordered, shard_size)
    for index, chunk in enumerate(chunks):
        lines = []
        for name in chunk:
            record = records.get(name)
            if record is not None:
                lines.append(json.dumps(sanitize(record), ensure_ascii=False))
        _atomic_write_text(shard_path(paths.raw_dir, index), "".join(
            line + "\n" for line in lines
        ))
        written += len(lines)
    # Remove stale shards left over from a larger previous catalog.
    for path in sorted(paths.raw_dir.glob("catalog-*.jsonl")):
        match = re.search(r"catalog-(\d+)\.jsonl$", path.name)
        if match and int(match.group(1)) >= len(chunks):
            path.unlink()
    return written


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def _write_manifest(paths: CatalogPaths, records: Dict[str, dict], seed: List[str],
                    last_sync: str, last_full_sync: Optional[str],
                    langs: Tuple[str, ...] = DEFAULT_LANGS) -> None:
    manifest = {
        "seed_count": len(seed),
        "fetched_count": len(records),
        "missing_count": max(0, len(set(seed) - set(records))),
        "fetched_at": last_sync,
        "last_full_sync": last_full_sync,
        "shards": shard_count(seed),
        "shard_size": SHARD_SIZE,
        "langs": list(langs),
    }
    _atomic_write_text(
        paths.raw_dir / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
    )


def read_manifest(paths: CatalogPaths) -> dict:
    path = paths.raw_dir / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


def sync_seed(paths: CatalogPaths, verbose: bool = True) -> dict:
    """Refresh the committed seed from ``package_list``."""
    names = fetch_package_list()
    previous = set(load_seed(paths))
    payload = save_seed(names, paths)
    if verbose:
        added = len(set(names) - previous) if previous else len(names)
        removed = len(previous - set(names)) if previous else 0
        print(f"Seed: {payload['count']} ids (+{added} new, -{removed} removed)",
              file=sys.stderr)
    return payload


def _pace(last_call: float, rate: float) -> float:
    interval = 1.0 / rate if rate > 0 else 0.0
    elapsed = time.time() - last_call
    if elapsed < interval:
        time.sleep(interval - elapsed)
    return time.time()


def _fetch_with_retry(name: str, locale: str, rate: float,
                      last_call: float,
                      verbose: bool = True) -> Tuple[Optional[dict], float]:
    for attempt in range(MAX_RETRIES):
        last_call = _pace(last_call, rate)
        try:
            return fetch_package_show(name, locale=locale), last_call
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            if verbose:
                print(f"  failed {name} [{locale}]: HTTP {exc.code}", file=sys.stderr)
            return None, last_call
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                RuntimeError) as exc:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            if verbose:
                print(f"  failed {name} [{locale}]: {exc}", file=sys.stderr)
            return None, last_call
    return None, last_call


def _missing_locales(record: Optional[dict], langs: Tuple[str, ...]) -> List[str]:
    """Return the locales still to fetch for a dataset (non-English)."""
    needed = []
    for locale in langs:
        if locale == "en":
            continue
        view = (record or {}).get("locales") or {}
        if locale not in view:
            needed.append(locale)
    return needed


def sync_full(paths: CatalogPaths, rate: float = DEFAULT_RATE,
              limit: Optional[int] = None, langs: Tuple[str, ...] = DEFAULT_LANGS,
              verbose: bool = True) -> dict:
    """Crawl every seed ID missing from the shards. Resumable.

    ``langs`` selects which locale endpoints to fetch (``en`` is always
    fetched); extra locales are stored under ``record["locales"][locale]``.
    Writes shards atomically every ``SHARD_SIZE`` datasets, so an interrupted
    run loses at most one batch.
    """
    langs = tuple(dict.fromkeys(("en",) + tuple(langs)))
    seed = load_seed(paths)
    if not seed:
        sync_seed(paths, verbose=verbose)
        seed = load_seed(paths)

    records = load_records(paths)
    missing = [name for name in seed
               if name not in records or _missing_locales(records.get(name), langs)]
    if limit is not None:
        missing = missing[:limit]

    if verbose:
        print(f"Catalog: {len(records)}/{len(seed)} fetched, "
              f"{len(missing)} to crawl ({','.join(langs)}) at {rate}/s",
              file=sys.stderr)

    last_call = 0.0
    fetched = 0
    failed: List[str] = []
    for i, name in enumerate(missing, 1):
        record = records.get(name)
        if record is None:
            record, last_call = _fetch_with_retry(name, "en", rate, last_call,
                                                  verbose=verbose)
            if record is None:
                failed.append(name)
                continue
            records[name] = record
        for locale in _missing_locales(record, langs):
            view, last_call = _fetch_with_retry(name, locale, rate, last_call,
                                               verbose=verbose)
            if view is None:
                failed.append(name)
                continue
            record.setdefault("locales", {})[locale] = _trim_locale(view)
        fetched += 1
        if fetched % SHARD_SIZE == 0:
            write_shards(records, seed, paths)
            if verbose:
                print(f"  {i}/{len(missing)} (checkpoint)", file=sys.stderr)

    write_shards(records, seed, paths)
    previous_full = read_manifest(paths).get("last_full_sync")
    incomplete = [n for n in seed if _missing_locales(records.get(n), langs)]
    complete = not failed and not incomplete
    _write_manifest(paths, records, seed, _now(),
                    _now() if complete else previous_full, langs=langs)

    if verbose:
        print(f"Crawl done: +{fetched} datasets, {len(failed)} failed, "
              f"{len(records)}/{len(seed)} total", file=sys.stderr)
    return {"fetched": fetched, "failed": failed, "total": len(records),
            "seed": len(seed), "langs": list(langs)}


def sync_refresh(paths: CatalogPaths, rate: float = DEFAULT_RATE,
                 langs: Optional[Tuple[str, ...]] = None,
                 verbose: bool = True) -> dict:
    """Re-fetch datasets listed in the 14-day RSS feed, then rewrite shards."""
    if langs is None:
        langs = tuple(read_manifest(paths).get("langs") or DEFAULT_LANGS)
    langs = tuple(dict.fromkeys(("en",) + tuple(langs)))

    changed = fetch_changed_ids()
    seed = load_seed(paths)
    known = set(seed)
    new = [name for name in changed if name not in known]
    if new:
        seed = sorted(known | set(new))
        save_seed(seed, paths)

    records = load_records(paths)
    targets = [name for name in changed if name in set(seed)]
    if verbose:
        print(f"Refresh: {len(targets)} changed ids ({len(new)} new to the seed)",
              file=sys.stderr)

    last_call = 0.0
    refreshed = 0
    failed: List[str] = []
    for name in targets:
        record, last_call = _fetch_with_retry(name, "en", rate, last_call,
                                              verbose=verbose)
        if record is None:
            failed.append(name)
            continue
        record.pop("locales", None)
        for locale in langs:
            if locale == "en":
                continue
            view, last_call = _fetch_with_retry(name, locale, rate, last_call,
                                               verbose=verbose)
            if view is None:
                failed.append(name)
                continue
            record.setdefault("locales", {})[locale] = _trim_locale(view)
        records[name] = record
        refreshed += 1

    write_shards(records, seed, paths)
    _write_manifest(paths, records, seed, _now(),
                    read_manifest(paths).get("last_full_sync"), langs=langs)
    if verbose:
        print(f"Refresh done: {refreshed} refreshed, {len(failed)} failed",
              file=sys.stderr)
    return {"refreshed": refreshed, "failed": failed, "new": new}


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def status(paths: CatalogPaths) -> dict:
    seed = load_seed(paths)
    records = load_records(paths)
    manifest = read_manifest(paths)
    shards = sorted(paths.raw_dir.glob("catalog-*.jsonl"))
    return {
        "seed_count": len(seed),
        "fetched_count": len(records),
        "missing_count": max(0, len(set(seed) - set(records))),
        "shards": len(shards),
        "shard_bytes": sum(path.stat().st_size for path in shards),
        "langs": manifest.get("langs", []),
        "last_full_sync": manifest.get("last_full_sync"),
        "fetched_at": manifest.get("fetched_at"),
        "names_path": str(paths.names_path),
    }