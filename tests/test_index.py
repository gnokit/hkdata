from pathlib import Path

from hkdata.index import (
    REFERENCES_DIR,
    build_index,
    parse_reference_file,
    render_index_md,
    score_dataset,
    search_local,
)


def test_parse_reference_file_kmb():
    path = REFERENCES_DIR / "transport-kmb.md"
    record = parse_reference_file(path)
    assert record["id"] == "hk-td-tis_21-etakmb"
    assert record["title"] == "KMB/LWB Bus Real-time ETA"
    assert record["category"] == "transport"
    assert "kmb" in record["keywords"]


def test_build_index_includes_datasets():
    index = build_index()
    assert index["count"] > 0
    ids = {r["id"] for r in index["datasets"]}
    assert "hk-td-tis_21-etakmb" in ids


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


def test_search_local_returns_results():
    results = search_local("kmb bus", top_n=5)
    assert len(results) > 0
    assert results[0][0] == "dataset"


def test_build_index_excludes_method_docs():
    """Method docs (workflow-guides/template/category-mapping/index) are not datasets."""
    index = build_index()
    banned = {"workflow-guides.md", "template.md", "category-mapping.md", "index.md"}
    for record in index["datasets"]:
        assert record["filename"] not in banned
        assert record["title"] != "Workflow Guides"


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
