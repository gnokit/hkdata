from hkdata.normalize import (
    DISTRICTS,
    category_to_prefix,
    expand_synonyms,
    normalize_district,
)


def test_normalize_district_english():
    assert normalize_district("Kwun Tong") == "Kwun Tong"


def test_normalize_district_ampersand_variant():
    assert normalize_district("Central & Western") == "Central and Western"


def test_normalize_district_chinese():
    assert normalize_district("觀塘") == "Kwun Tong"


def test_normalize_district_code():
    assert normalize_district("S") == "Kwai Tsing"


def test_normalize_district_unknown():
    assert normalize_district("Mars") is None


def test_category_to_prefix_known():
    assert category_to_prefix("commerce-and-industry") == "commerce"
    assert category_to_prefix("law-and-security") == "security"
    assert category_to_prefix("city-management") == "city"


def test_category_to_prefix_unknown():
    assert category_to_prefix("some-new-category") == "some"


def test_expand_synonyms_elderly():
    expanded = expand_synonyms("elderly")
    assert "elderly" in expanded
    assert "長者" in expanded


def test_expand_synonyms_no_match():
    assert expand_synonyms("weather") == ["weather"]


def test_all_districts_have_required_fields():
    for district in DISTRICTS:
        assert district["canonical_en"]
        assert district["zh"]
        assert district["code"]
