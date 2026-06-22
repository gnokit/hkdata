"""Normalization helpers for districts, categories, and keywords."""

from typing import Dict, List, Optional

# Canonical District Council districts with common variants.
DISTRICTS = [
    {
        "canonical_en": "Central and Western",
        "ha_variant": "Central & Western",
        "zh": "中西區",
        "code": "A",
    },
    {
        "canonical_en": "Wan Chai",
        "ha_variant": "Wan Chai",
        "zh": "灣仔",
        "code": "B",
    },
    {
        "canonical_en": "Eastern",
        "ha_variant": "Eastern",
        "zh": "東區",
        "code": "C",
    },
    {
        "canonical_en": "Southern",
        "ha_variant": "Southern",
        "zh": "南區",
        "code": "D",
    },
    {
        "canonical_en": "Yau Tsim Mong",
        "ha_variant": "Yau Tsim Mong",
        "zh": "油尖旺",
        "code": "E",
    },
    {
        "canonical_en": "Sham Shui Po",
        "ha_variant": "Sham Shui Po",
        "zh": "深水埗",
        "code": "F",
    },
    {
        "canonical_en": "Kowloon City",
        "ha_variant": "Kowloon City",
        "zh": "九龍城",
        "code": "G",
    },
    {
        "canonical_en": "Wong Tai Sin",
        "ha_variant": "Wong Tai Sin",
        "zh": "黃大仙",
        "code": "H",
    },
    {
        "canonical_en": "Kwun Tong",
        "ha_variant": "Kwun Tong",
        "zh": "觀塘",
        "code": "J",
    },
    {
        "canonical_en": "Kwai Tsing",
        "ha_variant": "Kwai Tsing",
        "zh": "葵青",
        "code": "S",
    },
    {
        "canonical_en": "Tsuen Wan",
        "ha_variant": "Tsuen Wan",
        "zh": "荃灣",
        "code": "T",
    },
    {
        "canonical_en": "Tuen Mun",
        "ha_variant": "Tuen Mun",
        "zh": "屯門",
        "code": "L",
    },
    {
        "canonical_en": "Yuen Long",
        "ha_variant": "Yuen Long",
        "zh": "元朗",
        "code": "M",
    },
    {
        "canonical_en": "North",
        "ha_variant": "North",
        "zh": "北區",
        "code": "N",
    },
    {
        "canonical_en": "Tai Po",
        "ha_variant": "Tai Po",
        "zh": "大埔",
        "code": "P",
    },
    {
        "canonical_en": "Sha Tin",
        "ha_variant": "Sha Tin",
        "zh": "沙田",
        "code": "Q",
    },
    {
        "canonical_en": "Sai Kung",
        "ha_variant": "Sai Kung",
        "zh": "西貢",
        "code": "R",
    },
    {
        "canonical_en": "Islands",
        "ha_variant": "Islands",
        "zh": "離島",
        "code": "Y",
    },
]

CATEGORY_MAP: Dict[str, str] = {
    "climate-and-weather": "weather",
    "transport": "transport",
    "development": "location",
    "housing": "housing",
    "health": "health",
    "education": "education",
    "environment": "environment",
    "city-management": "city",
    "commerce-and-industry": "commerce",
    "employment-and-labour": "employment",
    "finance": "finance",
    "food": "food",
    "law-and-security": "security",
    "population": "population",
    "recreation-and-culture": "recreation",
    "tourism": "tourism",
    "legislature": "legislature",
    "social-welfare": "welfare",
    "information-technology-and-broadcasting": "it",
    "miscellaneous": "misc",
}

KEYWORD_SYNONYMS: Dict[str, List[str]] = {
    "elderly": ["elderly", "aged", "senior", "長者", "老人"],
    "vessel": ["vessel", "arrival", "ship", "marine", "arrivals", "departures"],
    "ferry": ["ferry", "pier", "harbour", "outlying", "eta"],
    "air": ["air", "aqhi", "pollution", "monitoring", "epd"],
}


def normalize_district(name: str) -> Optional[str]:
    """Return the canonical English district name for a given variant."""
    if not name:
        return None
    cleaned = name.strip().lower().replace("&", "and")
    for district in DISTRICTS:
        variants = [
            district["canonical_en"].lower().replace("&", "and"),
            district["ha_variant"].lower().replace("&", "and"),
            district["zh"],
            district["code"].lower(),
        ]
        if cleaned in variants:
            return district["canonical_en"]
    return None


def category_to_prefix(category: str) -> str:
    """Map a data.gov.hk category to the reference-file prefix."""
    return CATEGORY_MAP.get(category.lower(), category.split("-")[0])


def expand_synonyms(keyword: str) -> List[str]:
    """Expand a keyword to a list of related search terms if known."""
    keyword_lower = keyword.lower().strip()
    for root, synonyms in KEYWORD_SYNONYMS.items():
        if keyword_lower in [s.lower() for s in synonyms] or keyword_lower == root:
            return synonyms
    return [keyword]
