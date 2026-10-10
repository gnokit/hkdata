import pytest

from hkdata import index as index_mod
from hkdata.index import (
    parse_reference_file,
    render_index_md,
    score_dataset,
    search_local,
)

KMB_MD = """# KMB/LWB Bus Real-time ETA

**Dataset ID:** `hk-td-tis_21-etakmb`
**Provider:** Transport Department
**Category:** transport

## Description

Real-time KMB/LWB bus arrival times.

## API

**Endpoint:** `https://data.etabus.gov.hk/v1/transport/kmb/eta`

**Date Added:** 2026-09-27
"""


@pytest.fixture
def refs(tmp_path, monkeypatch):
    """A hermetic references/ dir — the public repo has no dataset docs."""
    d = tmp_path / "references"
    d.mkdir()
    (d / "transport-kmb.md").write_text(KMB_MD, encoding="utf-8")
    (d / "workflow-guides.md").write_text(
        "# Workflow Guides\n\nA method doc, not a dataset.\n", encoding="utf-8")
    (d / "index.md").write_text("# Registry\n", encoding="utf-8")
    (d / "template.md").write_text("# Dataset Template\n", encoding="utf-8")
    (d / "category-mapping.md").write_text("# Category Mapping\n", encoding="utf-8")
    monkeypatch.setattr(index_mod, "REFERENCES_DIR", d)
    monkeypatch.setattr(index_mod, "INDEX_PATH", d / "search-index.json")
    monkeypatch.setattr(index_mod, "INDEX_MD_PATH", d / "generated-index.md")
    return d


def test_parse_reference_file_kmb(refs):
    record = parse_reference_file(refs / "transport-kmb.md")
    assert record["id"] == "hk-td-tis_21-etakmb"
    assert record["title"] == "KMB/LWB Bus Real-time ETA"
    assert record["category"] == "transport"
    assert "kmb" in record["keywords"]


def test_build_index_includes_datasets(refs):
    index = index_mod.build_index()
    assert index["count"] == 1
    ids = {r["id"] for r in index["datasets"]}
    assert "hk-td-tis_21-etakmb" in ids


def test_build_index_excludes_method_docs(refs):
    """Method docs (workflow-guides/template/category-mapping/index) are not datasets."""
    index = index_mod.build_index()
    banned = {"workflow-guides.md", "template.md", "category-mapping.md", "index.md"}
    for record in index["datasets"]:
        assert record["filename"] not in banned
        assert record["title"] != "Workflow Guides"


def test_score_dataset_zero_for_unrelated():
    record = {
        "title": "Weather",
        "description": "Sunny",
        "category": "weather",
        "keywords": ["weather", "sun"],
    }
    assert score_dataset("unemployment district", record) == 0.0


def test_score_dataset_positive_for_match():
    record = {
        "title": "KMB Bus ETA",
        "description": "Bus arrival times",
        "category": "transport",
        "keywords": ["kmb", "bus", "eta"],
    }
    assert score_dataset("bus eta", record) > 0


def test_search_local_returns_results(refs):
    index_mod.save_index(index_mod.build_index())
    results = search_local("kmb bus", top_n=5, include_logs=False)
    assert len(results) > 0
    assert results[0][0] == "dataset"


def test_render_index_md_generates_registry(tmp_path):
    index = {
        "version": 1,
        "count": 1,
        "datasets": [{
            "id": "hk-x",
            "title": "X | Y",
            "category": "transport",
            "filename": "transport-x.md",
            "description": "desc | with pipe",
        }],
    }
    out = tmp_path / "index.md"
    render_index_md(index, out)
    text = out.read_text(encoding="utf-8")
    assert "transport-x.md" in text
    assert "X \\| Y" in text          # pipe escaped for the markdown table
    assert "## By Category" in text
    assert "### transport" in text
