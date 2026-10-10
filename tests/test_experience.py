import json

import pytest

from hkdata import catalog, experience, vectors

chromadb = pytest.importorskip("chromadb")


POSITIVE = {
    "kind": "positive",
    "topic": "Government gym rooms near Cheung Sha Wan",
    "query_patterns": ["gym room in Cheung Sha Wan", "長沙灣 健身室"],
    "category": "recreation-and-culture",
    "datasets": ["hk-lcsd-facility-facility-fit"],
    "method": "call facility-fitrm.json and filter by address",
    "endpoint": "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json",
    "outcome": "located",
    "caveats": ["no real-time availability"],
    "source": "references/recreation-fitness-rooms.md",
    "date": "2026-09-27",
}

NEGATIVE = {
    "kind": "negative",
    "topic": "HKPF smart CCTV figures",
    "query_patterns": ["police smart camera", "閉路電視 數目"],
    "category": "law-and-security",
    "datasets": [],
    "method": "searched catalog for CCTV/camera; HKPF datasets are personnel only",
    "outcome": "not_on_data_gov_hk",
    "source": "logs/failure-log.jsonl",
    "date": "2026-09-27",
}


@pytest.fixture
def exp_path(tmp_path):
    return tmp_path / "experiences.jsonl"


def _fake_embed(texts):
    out = []
    for text in texts:
        low = text.lower()
        out.append([
            1.0 if ("gym" in low or "健身" in low or "badminton" in low) else 0.0,
            1.0 if ("cctv" in low or "camera" in low or "閉路電視" in low) else 0.0,
            1.0 if "instruct" in low else 0.0,
            1.0,
        ])
    return out


def _orth_embed(texts):
    """Orthogonal one-hot embeddings — real (non-baseline) similarities."""
    out = []
    for text in texts:
        low = text.lower()
        if "gym" in low or "健身" in low:
            out.append([1.0, 0.0, 0.0])
        elif "cctv" in low or "camera" in low or "閉路電視" in low:
            out.append([0.0, 1.0, 0.0])
        else:
            out.append([0.0, 0.0, 1.0])
    return out


def _ephemeral():
    return chromadb.EphemeralClient()


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------


def test_normalize_defaults_and_scrubs():
    rec = experience.normalize({"topic": "x", "kind": "weird",
                                "method": "contact a@b.gov.hk"})
    assert rec["kind"] == "positive"
    assert "a@b.gov.hk" not in rec["method"]
    assert "[email]" in rec["method"]
    assert rec["id"].startswith("exp-")


def test_build_document_has_no_answer_prose():
    doc = experience.build_document(POSITIVE)
    assert "Government gym rooms near Cheung Sha Wan" in doc
    assert "hk-lcsd-facility-facility-fit" in doc
    assert "facility-fitrm.json" in doc
    assert "Kind: positive" in doc


def test_build_metadata_is_scalar():
    meta = experience.build_metadata(NEGATIVE)
    assert meta["kind"] == "negative"
    assert meta["outcome"] == "not_on_data_gov_hk"
    assert meta["model"] == vectors.DEFAULT_MODEL
    assert all(isinstance(v, (str, int, float, bool)) for v in meta.values())
    assert meta["text_hash"]


# ---------------------------------------------------------------------------
# Store + index
# ---------------------------------------------------------------------------


def test_append_writes_jsonl_and_upserts(exp_path):
    client = _ephemeral()
    record = experience.append_experience(
        POSITIVE, path=exp_path, embed_fn=_fake_embed, client=client,
        collection_name="exp_append", upsert=True, verbose=False)
    assert exp_path.exists()
    lines = [json.loads(l) for l in exp_path.read_text().splitlines() if l.strip()]
    assert len(lines) == 1 and lines[0]["id"] == record["id"]
    assert experience.count.__module__  # sanity


def test_embed_and_search_with_kind_filter(exp_path):
    records = [experience.normalize(POSITIVE), experience.normalize(NEGATIVE)]
    experience.save_experiences(records, exp_path)
    client = _ephemeral()
    # embed_experiences reads the default path; call upsert directly on our records.
    experience.upsert_experiences(records, embed_fn=_fake_embed, client=client,
                                  collection_name="exp_search", verbose=False)

    hits = experience.search("健身室", embed_fn=_fake_embed, client=client,
                             collection_name="exp_search", top_n=2, verbose=False)
    assert hits and hits[0]["topic"] == POSITIVE["topic"]

    hits = experience.search("camera", kind="negative", embed_fn=_fake_embed,
                             client=client, collection_name="exp_search",
                             top_n=2, verbose=False)
    assert hits and hits[0]["topic"] == NEGATIVE["topic"]

    hits = experience.search("camera", kind="positive", embed_fn=_fake_embed,
                             client=client, collection_name="exp_search",
                             top_n=2, verbose=False)
    assert all(h["kind"] == "positive" for h in hits)


def test_search_empty_store(exp_path):
    hits = experience.search("anything", embed_fn=_fake_embed, client=_ephemeral(),
                             collection_name="exp_empty", verbose=False)
    assert hits == []


def test_search_no_relevant_card(exp_path):
    records = [experience.normalize(POSITIVE)]
    client = _ephemeral()
    experience.upsert_experiences(records, embed_fn=_orth_embed, client=client,
                                  collection_name="exp_norel", verbose=False)
    # Unrelated query: nothing clears the floor -> no false "match".
    assert experience.search("zzz unrelated", embed_fn=_orth_embed, client=client,
                             collection_name="exp_norel", verbose=False) == []
    # Related query clears the floor and carries a real similarity score.
    hits = experience.search("gym", embed_fn=_orth_embed, client=client,
                             collection_name="exp_norel", verbose=False)
    assert hits and hits[0]["topic"] == POSITIVE["topic"]
    assert hits[0]["similarity"] >= experience.DEFAULT_MIN_SIM


def test_search_min_sim_gates_dense(exp_path):
    records = [experience.normalize(POSITIVE)]
    client = _ephemeral()
    experience.upsert_experiences(records, embed_fn=_orth_embed, client=client,
                                  collection_name="exp_floor", verbose=False)
    # "gymming" embeds like "gym" (dense sim 1.0) but is not a literal token in
    # the doc, so only the dense gate applies: a floor above 1.0 filters it out.
    assert experience.search("gymming", embed_fn=_orth_embed, client=client,
                             collection_name="exp_floor", min_sim=1.01,
                             verbose=False) == []
    assert experience.search("gymming", embed_fn=_orth_embed, client=client,
                             collection_name="exp_floor", min_sim=0.5,
                             verbose=False)


def test_search_pagination(exp_path):
    records = [experience.normalize({**POSITIVE, "topic": f"gym room {i}"})
               for i in range(5)]
    client = _ephemeral()
    experience.upsert_experiences(records, embed_fn=_orth_embed, client=client,
                                  collection_name="exp_page", verbose=False)
    page1 = experience.search("gym", embed_fn=_orth_embed, client=client,
                              collection_name="exp_page", top_n=2, offset=0,
                              min_sim=0.0, verbose=False)
    page2 = experience.search("gym", embed_fn=_orth_embed, client=client,
                              collection_name="exp_page", top_n=2, offset=2,
                              min_sim=0.0, verbose=False)
    assert len(page1) == 2 and len(page2) == 2
    assert {h["id"] for h in page1}.isdisjoint({h["id"] for h in page2})


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------


def test_migrate_from_fixtures(tmp_path, exp_path):
    refs = tmp_path / "references"
    refs.mkdir()
    (refs / "recreation-fitness-rooms.md").write_text(
        "# Fitness Rooms\n\n**Dataset ID:** `hk-lcsd-facility-facility-fit`\n"
        "**Provider:** LCSD\n**Category:** recreation\n\n## Description\n\n"
        "Locations of LCSD fitness rooms.\n\n**Date Added:** 2026-09-27\n",
        encoding="utf-8")
    (refs / "index.md").write_text("# Registry\n", encoding="utf-8")

    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "strategy-registry.jsonl").write_text(
        json.dumps({"category": "Transport — Ferry", "topic": "TD ferry",
                    "method": "catalog-search ferry", "result": "✅ found"}) + "\n"
        + json.dumps({"category": "Recreation", "topic": "badminton",
                      "method": "catalog-search badminton", "result": "❌ 0 results"}) + "\n",
        encoding="utf-8")
    (logs / "failure-log.jsonl").write_text(
        json.dumps({"date": "2026-09-27", "task": "police cameras",
                    "component": "catalog-search", "symptom": "none",
                    "root_cause": "not published", "solution": "use proxies",
                    "verification": "❌ unavailable"}) + "\n",
        encoding="utf-8")

    result = experience.migrate(references_dir=refs, logs_dir=logs, path=exp_path,
                                verbose=False)
    assert result["total"] == 4          # 1 reference + 2 strategy + 1 failure
    assert result["positive"] == 2       # reference + the ✅ strategy row
    assert result["negative"] == 2       # the ❌ row + the failure

    kinds = {r["topic"]: r["kind"] for r in experience.load_experiences(exp_path)}
    assert kinds["Fitness Rooms"] == "positive"
    assert kinds["police cameras"] == "negative"