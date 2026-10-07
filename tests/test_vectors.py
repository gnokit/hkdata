import pytest

from hkdata import catalog, vectors

chromadb = pytest.importorskip("chromadb")

RECORD = {
    "name": "hk-lcsd-facility-facility-bmtc",
    "title": "Badminton Courts (Free Outdoor Pitches/Courts)",
    "notes": "Location of Badminton Courts (Free Outdoor Pitches/Courts)",
    "organization": {"title": "Leisure and Cultural Services Department"},
    "groups": [{"name": "recreation-and-culture",
                "title": "Recreation, Sports and Culture"}],
    "resources": [{"format": "JSON", "is_api": True}],
    "tags": [{"name": "badminton"}],
    "isopen": False,
    "metadata_modified": "2021-07-02T06:06:01.403354",
    "locales": {
        "tc": {
            "title": "羽毛球場(戶外免費球場)",
            "notes": "羽毛球場(戶外免費球場) 位置",
            "organization": {"title": "康樂及文化事務署"},
        }
    },
}

VESSEL = {
    "name": "hk-md-mardep-vessel-arrivals-and-departures",
    "title": "Vessel arrivals and departures",
    "notes": "Real-time vessel movements",
    "organization": {"title": "Marine Department"},
    "resources": [{"format": "XML", "is_api": False}],
}


@pytest.fixture
def paths(tmp_path):
    return catalog.CatalogPaths(
        names_path=tmp_path / "references" / "catalog-names.json",
        raw_dir=tmp_path / ".cache" / "catalog" / "raw",
    )


def _fake_embed(texts):
    vectors_out = []
    for text in texts:
        low = text.lower()
        vectors_out.append([
            1.0 if ("badminton" in low or "羽毛球" in low) else 0.0,
            1.0 if ("vessel" in low or "船" in low) else 0.0,
            1.0 if "instruct" in low else 0.0,
            1.0,
        ])
    return vectors_out


def _ephemeral():
    return chromadb.EphemeralClient()


# ---------------------------------------------------------------------------
# Document / metadata construction
# ---------------------------------------------------------------------------


def test_build_document_includes_both_languages():
    doc = vectors.build_document(RECORD)
    assert "Badminton Courts (Free Outdoor Pitches/Courts)" in doc
    assert "羽毛球場(戶外免費球場)" in doc
    assert "康樂及文化事務署" in doc
    assert "Leisure and Cultural Services Department" in doc
    assert "Formats: JSON" in doc


def test_build_document_english_only():
    doc = vectors.build_document(VESSEL)
    assert doc.startswith("Vessel arrivals and departures")
    assert "Marine Department" in doc
    assert "Formats: XML" in doc


def test_build_metadata_fields():
    digest = vectors.text_hash("x")
    meta = vectors.build_metadata(RECORD, "qwen3-embedding:0.6b", digest)
    assert meta["name"] == RECORD["name"]
    assert meta["title_tc"] == "羽毛球場(戶外免費球場)"
    assert meta["org_tc"] == "康樂及文化事務署"
    assert meta["formats"] == "JSON"
    assert meta["is_api"] is True
    assert meta["is_open"] is False
    assert meta["locales"] == "en,tc"
    assert meta["text_hash"] == digest
    # Chroma metadata values must be scalar.
    assert all(isinstance(v, (str, int, float, bool)) for v in meta.values())


def test_text_hash_is_stable_and_content_sensitive():
    assert vectors.text_hash("abc") == vectors.text_hash("abc")
    assert vectors.text_hash("abc") != vectors.text_hash("abd")


def test_rrf_rank_keeps_first_rank_on_duplicates():
    # "a" appears at rank 0 (best) and rank 3; the later, worse rank must not win.
    scores = vectors._rrf_rank(["a", "b", "c", "a"])
    assert scores["a"] == 1.0 / (60 + 0 + 1)
    assert scores["b"] == 1.0 / (60 + 1 + 1)
    assert scores["c"] == 1.0 / (60 + 2 + 1)
    # Sanity: first rank strictly beats any later rank.
    assert scores["a"] > 1.0 / (60 + 3 + 1)


def test_rrf_rank_skips_empty_names():
    scores = vectors._rrf_rank(["a", "", "b"])
    assert set(scores) == {"a", "b"}


def test_expand_query_aliases():
    aliases = {"康文署": ["康樂及文化事務署", "LCSD"]}
    assert vectors.expand_query("康文署羽毛球場", aliases) == [
        "康樂及文化事務署", "LCSD"]
    assert vectors.expand_query("badminton", aliases) == []
    # Already-present expansions are not duplicated.
    assert vectors.expand_query("康文署 LCSD", aliases) == ["康樂及文化事務署"]


def test_load_aliases_ignores_comments(tmp_path):
    path = tmp_path / "aliases.json"
    path.write_text('{"_comment": "x", "天文台": ["香港天文台"]}', encoding="utf-8")
    assert vectors.load_aliases(path) == {"天文台": ["香港天文台"]}


# ---------------------------------------------------------------------------
# Build + search
# ---------------------------------------------------------------------------


def test_build_vectors_and_search(paths):
    catalog.write_shards({RECORD["name"]: RECORD, VESSEL["name"]: VESSEL},
                         [RECORD["name"], VESSEL["name"]], paths)
    client = _ephemeral()
    result = vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                                   collection_name="t_build", verbose=False)
    assert result["total"] == 2
    assert result["embedded"] == 2

    hits = vectors.vector_search("羽毛球場", paths, top_n=1,
                                 embed_fn=_fake_embed, client=client,
                                 collection_name="t_build", verbose=False)
    assert hits[0]["name"] == RECORD["name"]
    assert hits[0]["score"] > 0

    hits = vectors.vector_search("vessel", paths, top_n=1,
                                 embed_fn=_fake_embed, client=client,
                                 collection_name="t_build", verbose=False)
    assert hits[0]["name"] == VESSEL["name"]


def test_build_vectors_skips_unchanged(paths):
    catalog.write_shards({RECORD["name"]: RECORD}, [RECORD["name"]], paths)
    client = _ephemeral()
    first = vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                                  collection_name="t_inc", verbose=False)
    assert first["embedded"] == 1

    second = vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                                   collection_name="t_inc", verbose=False)
    assert second["embedded"] == 0
    assert second["total"] == 1


def test_build_vectors_removes_stale(paths):
    catalog.write_shards({RECORD["name"]: RECORD, VESSEL["name"]: VESSEL},
                         [RECORD["name"], VESSEL["name"]], paths)
    client = _ephemeral()
    vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                          collection_name="t_stale", verbose=False)

    # VESSEL disappears from the catalog -> its vector must be deleted.
    catalog.write_shards({RECORD["name"]: RECORD}, [RECORD["name"]], paths)
    result = vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                                   collection_name="t_stale", verbose=False)
    assert result["removed"] == 1
    assert result["total"] == 1


def test_hybrid_search_dense_and_keyword(paths):
    catalog.write_shards({RECORD["name"]: RECORD, VESSEL["name"]: VESSEL},
                         [RECORD["name"], VESSEL["name"]], paths)
    client = _ephemeral()
    vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                          collection_name="t_hybrid", verbose=False)

    # Semantic hit (no exact substring needed).
    hits = vectors.hybrid_search("羽毛球場", paths, top_n=2, embed_fn=_fake_embed,
                                 client=client, collection_name="t_hybrid",
                                 verbose=False)
    assert hits[0]["name"] == RECORD["name"]

    # Keyword pass: exact substring present in the stored document.
    hits = vectors.hybrid_search("Badminton", paths, top_n=2, embed_fn=_fake_embed,
                                 client=client, collection_name="t_hybrid",
                                 verbose=False)
    names = [h["name"] for h in hits]
    assert RECORD["name"] in names
    assert all(h["score"] > 0 for h in hits)


def test_hybrid_search_applies_aliases(paths):
    catalog.write_shards({RECORD["name"]: RECORD, VESSEL["name"]: VESSEL},
                         [RECORD["name"], VESSEL["name"]], paths)
    client = _ephemeral()
    vectors.build_vectors(paths, embed_fn=_fake_embed, client=client,
                          collection_name="t_alias", verbose=False)

    # "康文署" alone has no lexical overlap; the alias maps it to "Badminton".
    hits = vectors.hybrid_search("康文署", paths, top_n=1, embed_fn=_fake_embed,
                                 client=client, collection_name="t_alias",
                                 aliases={"康文署": ["Badminton"]}, verbose=False)
    assert hits[0]["name"] == RECORD["name"]


def test_hybrid_search_empty_store(paths):
    hits = vectors.hybrid_search("anything", paths, embed_fn=_fake_embed,
                                 client=_ephemeral(), collection_name="t_hempty",
                                 verbose=False)
    assert hits == []


def test_vector_search_empty_store(paths):
    hits = vectors.vector_search("anything", paths, embed_fn=_fake_embed,
                                 client=_ephemeral(), collection_name="t_empty",
                                 verbose=False)
    assert hits == []


def test_build_vectors_requires_records(paths):
    with pytest.raises(RuntimeError):
        vectors.build_vectors(paths, embed_fn=_fake_embed, client=_ephemeral(),
                              collection_name="t_none", verbose=False)