from pathlib import Path

from hkdata.index import (
    REFERENCES_DIR,
    build_index,
    parse_reference_file,
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
