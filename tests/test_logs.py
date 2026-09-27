from hkdata import experience
from hkdata.logs import (
    log_search,
    render_failure_log,
    render_strategy_registry,
)


def _neg(topic="police smart camera", category="law-and-security"):
    return experience.normalize({
        "kind": "negative", "topic": topic, "category": category,
        "method": "searched catalog; not published", "outcome": "unavailable",
        "caveats": ["no dataset on data.gov.hk"], "details": "Symptom: none available",
        "source": "failure-log", "date": "2026-09-27",
    })


def _pos(topic="Cheung Sha Wan gym", category="recreation"):
    return experience.normalize({
        "kind": "positive", "topic": topic, "category": category,
        "datasets": ["hk-lcsd-facility-facility-fit"],
        "method": "call facility-fitrm.json", "outcome": "located",
        "source": "references/recreation-fitness-rooms.md", "date": "2026-09-27",
    })


def test_render_failure_log_from_negative_experiences():
    md = render_failure_log([_neg(), _pos()])
    assert "police smart camera" in md
    assert "**Kind:** negative" in md
    assert "**Details:** Symptom: none available" in md
    # positive experiences are not part of the failure view
    assert "Cheung Sha Wan gym" not in md


def test_render_strategy_registry_groups_by_category():
    md = render_strategy_registry([_pos(), _neg()])
    assert "### recreation" in md
    assert "Cheung Sha Wan gym" in md
    assert "hk-lcsd-facility-facility-fit" in md
    # negative experiences are not part of the strategy view
    assert "police smart camera" not in md


def test_log_search_filters_by_kind(monkeypatch):
    records = [_neg(), _pos()]
    monkeypatch.setattr(experience, "load_experiences", lambda *a, **k: records)

    both = log_search(None, ["cheung"])
    assert {r["kind"] for r in both} == {"positive"}

    negative = log_search(["failure-log"], ["police"])
    assert len(negative) == 1 and negative[0]["kind"] == "negative"

    positive = log_search(["strategy-registry"], ["gym"])
    assert len(positive) == 1 and positive[0]["kind"] == "positive"
