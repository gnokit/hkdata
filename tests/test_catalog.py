import json

import pytest

from hkdata import catalog


@pytest.fixture
def paths(tmp_path):
    return catalog.CatalogPaths(
        names_path=tmp_path / "references" / "catalog-names.json",
        raw_dir=tmp_path / ".cache" / "catalog" / "raw",
    )


def _record(name, title="", notes="", org=""):
    payload = {"name": name, "title": title, "notes": notes}
    if org:
        payload["organization"] = {"title": org}
    return payload


def _write_seed(paths, names):
    catalog.save_seed(names, paths)


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def test_save_seed_is_sorted_and_hashed(paths):
    payload = catalog.save_seed(["b", "a", "c", "a"], paths)
    assert payload["names"] == ["a", "b", "c"]
    assert payload["count"] == 3
    assert payload["sha256"]
    assert catalog.load_seed(paths) == ["a", "b", "c"]


def test_sync_seed_uses_package_list(paths, monkeypatch):
    monkeypatch.setattr(catalog, "fetch_package_list", lambda: ["z", "a", "m"])
    catalog.sync_seed(paths, verbose=False)
    assert catalog.load_seed(paths) == ["a", "m", "z"]


def test_parse_langs():
    assert catalog.parse_langs("tc") == ["en", "tc"]
    assert catalog.parse_langs("en,tc,sc") == ["en", "tc", "sc"]
    assert catalog.parse_langs(" tc , en ") == ["tc", "en"]
    with pytest.raises(ValueError):
        catalog.parse_langs("jp")
    with pytest.raises(ValueError):
        catalog.parse_langs(" , ")


# ---------------------------------------------------------------------------
# Shards
# ---------------------------------------------------------------------------


def test_shard_count_and_paths(paths):
    assert catalog.shard_count([]) == 0
    assert catalog.shard_count(["a"] * 500) == 1
    assert catalog.shard_count(["a"] * 501) == 2
    assert catalog.shard_path(paths.raw_dir, 3).name == "catalog-003.jsonl"


def test_write_then_load_roundtrip(paths):
    names = ["ds-a", "ds-b", "ds-c"]
    records = {n: _record(n, title=f"Title {n}") for n in names}
    catalog.write_shards(records, names, paths, shard_size=2)

    assert sorted(p.name for p in paths.raw_dir.glob("*.jsonl")) == [
        "catalog-000.jsonl", "catalog-001.jsonl"]
    loaded = catalog.load_records(paths)
    assert set(loaded) == set(names)
    assert loaded["ds-b"]["title"] == "Title ds-b"


def test_write_shards_prunes_stale(paths):
    catalog.write_shards({n: _record(n) for n in ["a", "b", "c"]}, ["a", "b", "c"],
                         paths, shard_size=2)
    assert len(list(paths.raw_dir.glob("*.jsonl"))) == 2

    catalog.write_shards({"a": _record("a")}, ["a"], paths, shard_size=2)
    assert [p.name for p in paths.raw_dir.glob("*.jsonl")] == ["catalog-000.jsonl"]


def test_load_records_skips_torn_line(paths):
    paths.raw_dir.mkdir(parents=True)
    good = json.dumps(_record("ds-a"))
    (paths.raw_dir / "catalog-000.jsonl").write_text(good + "\n{\"name\": \"ds-b\"",
                                                     encoding="utf-8")
    loaded = catalog.load_records(paths)
    assert set(loaded) == {"ds-a"}


# ---------------------------------------------------------------------------
# Sync / crawl
# ---------------------------------------------------------------------------


def test_sync_full_fetches_and_resumes(paths, monkeypatch):
    _write_seed(paths, ["ds-a", "ds-b", "ds-c"])
    calls = []

    def fake_show(name, locale="en"):
        calls.append(name)
        return _record(name, title=f"Title {name}")

    monkeypatch.setattr(catalog, "fetch_package_show", fake_show)
    result = catalog.sync_full(paths, rate=0, verbose=False)
    assert result["fetched"] == 3
    assert sorted(calls) == ["ds-a", "ds-b", "ds-c"]

    calls.clear()
    result = catalog.sync_full(paths, rate=0, verbose=False)
    assert result["fetched"] == 0
    assert calls == []


def test_sync_full_limit(paths, monkeypatch):
    _write_seed(paths, ["ds-a", "ds-b", "ds-c"])
    monkeypatch.setattr(catalog, "fetch_package_show",
                        lambda name, locale="en": _record(name))
    result = catalog.sync_full(paths, rate=0, limit=2, verbose=False)
    assert result["fetched"] == 2
    assert len(catalog.load_records(paths)) == 2


def test_sync_full_multilang_stores_and_resumes(paths, monkeypatch):
    _write_seed(paths, ["ds-a", "ds-b"])
    calls = []

    def fake_show(name, locale="en"):
        calls.append((name, locale))
        if locale == "en":
            return _record(name, title=f"English {name}")
        return {"title": f"中文 {name}", "notes": "備註",
                "organization": {"title": "康樂及文化事務署"}}

    monkeypatch.setattr(catalog, "fetch_package_show", fake_show)
    result = catalog.sync_full(paths, rate=0, langs=("en", "tc"), verbose=False)
    assert result["langs"] == ["en", "tc"]
    assert sorted(calls) == [("ds-a", "en"), ("ds-a", "tc"),
                             ("ds-b", "en"), ("ds-b", "tc")]

    loaded = catalog.load_records(paths)
    assert loaded["ds-a"]["locales"]["tc"]["title"] == "中文 ds-a"
    assert loaded["ds-a"]["locales"]["tc"]["organization"]["title"] == "康樂及文化事務署"

    calls.clear()
    again = catalog.sync_full(paths, rate=0, langs=("en", "tc"), verbose=False)
    assert again["fetched"] == 0
    assert calls == []


def test_sync_full_adds_missing_locale_only(paths, monkeypatch):
    _write_seed(paths, ["ds-a"])
    monkeypatch.setattr(catalog, "fetch_package_show",
                        lambda name, locale="en": _record(name, title="EN"))
    catalog.sync_full(paths, rate=0, langs=("en",), verbose=False)

    calls = []

    def fake_show(name, locale="en"):
        calls.append(locale)
        return {"title": "中文"}

    monkeypatch.setattr(catalog, "fetch_package_show", fake_show)
    catalog.sync_full(paths, rate=0, langs=("en", "tc"), verbose=False)
    assert calls == ["tc"]


def test_sync_full_records_failures(paths, monkeypatch):
    _write_seed(paths, ["ds-a", "ds-b"])

    def fake_show(name, locale="en"):
        if name == "ds-b":
            raise RuntimeError("boom")
        return _record(name)

    monkeypatch.setattr(catalog, "fetch_package_show", fake_show)
    monkeypatch.setattr(catalog.time, "sleep", lambda _: None)
    result = catalog.sync_full(paths, rate=0, verbose=False)
    assert result["failed"] == ["ds-b"]
    assert set(catalog.load_records(paths)) == {"ds-a"}


def test_sync_refresh_merges_new_ids(paths, monkeypatch):
    _write_seed(paths, ["ds-a"])
    catalog.write_shards({"ds-a": _record("ds-a", title="Old")}, ["ds-a"], paths)
    monkeypatch.setattr(catalog, "fetch_changed_ids", lambda: ["ds-a", "ds-new"])
    monkeypatch.setattr(catalog, "fetch_package_show",
                        lambda name, locale="en": _record(
                            name, title="New" if name == "ds-a" else "Fresh"))

    result = catalog.sync_refresh(paths, rate=0, verbose=False)
    assert result["new"] == ["ds-new"]
    assert catalog.load_seed(paths) == ["ds-a", "ds-new"]
    loaded = catalog.load_records(paths)
    assert loaded["ds-a"]["title"] == "New"
    assert loaded["ds-new"]["title"] == "Fresh"


def test_fetch_changed_ids_parses_rss(paths, monkeypatch):
    rss = b"""<?xml version="1.0"?><rss version="2.0"><channel>
      <item><link>https://data.gov.hk/en-data/dataset/ds-one/resource/abc</link></item>
      <item><link>https://data.gov.hk/en-data/dataset/ds-two/resource/def</link></item>
      <item><link>https://data.gov.hk/en-data/dataset/ds-one/resource/ghi</link></item>
      <item><link>https://example.com/not-a-dataset</link></item>
    </channel></rss>"""

    class _Resp:
        def read(self):
            return rss

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(catalog.urllib.request, "urlopen", lambda *a, **k: _Resp())
    assert catalog.fetch_changed_ids() == ["ds-one", "ds-two"]


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def test_status_reports_coverage(paths, monkeypatch):
    _write_seed(paths, ["ds-a", "ds-b", "ds-c"])
    monkeypatch.setattr(catalog, "fetch_package_show",
                        lambda name, locale="en": _record(name))
    catalog.sync_full(paths, rate=0, limit=2, verbose=False)
    data = catalog.status(paths)
    assert data["seed_count"] == 3
    assert data["fetched_count"] == 2
    assert data["missing_count"] == 1
    assert data["shards"] == 1