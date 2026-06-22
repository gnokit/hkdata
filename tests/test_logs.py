from hkdata.logs import (
    _extract_field,
    parse_failure_markdown,
    parse_strategy_markdown,
    render_failure_log,
    render_strategy_registry,
)


FAILURE_MD = """# Failure Log

## Format

```
## [日期] Task: <任務描述>

**失敗組件:** <script/API/tool 名稱>
```

---

## 記錄

### 2026-06-22 | Task: 測試失敗

**失敗組件:** `test-component`

**錯誤現象:** 
- Error 1
- Error 2

**根本原因:** Root cause

**解決方案:** Fix it

**驗證:** ✅ 成功

---

<!-- 新記錄請加喺上面 -->
"""

STRATEGY_MD = """# Strategy Registry

## 成功策略記錄

### Category A

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| topic1 | method1 | ✅ result1 |
| topic2 | method2 | ❌ result2 |

<!-- 新記錄請加喺上面 -->
"""


def test_extract_field():
    body = "**失敗組件:** `comp`\n\n**錯誤現象:** symptom"
    assert _extract_field(body, "失敗組件") == "`comp`"
    assert _extract_field(body, "錯誤現象") == "symptom"


def test_parse_failure_markdown():
    records = parse_failure_markdown(FAILURE_MD)
    assert len(records) == 1
    rec = records[0]
    assert rec["date"] == "2026-06-22"
    assert rec["task"] == "測試失敗"
    assert "test-component" in rec["component"]
    assert "Error 1" in rec["symptom"]
    assert "Root cause" in rec["root_cause"]
    assert "Fix it" in rec["solution"]
    assert "成功" in rec["verification"]


def test_parse_strategy_markdown():
    records = parse_strategy_markdown(STRATEGY_MD)
    assert len(records) == 2
    assert records[0]["category"] == "Category A"
    assert records[0]["topic"] == "topic1"
    assert records[1]["topic"] == "topic2"


def test_render_failure_log_roundtrip():
    records = parse_failure_markdown(FAILURE_MD)
    rendered = render_failure_log(records)
    assert "### 2026-06-22 | Task: 測試失敗" in rendered
    assert "**失敗組件:**" in rendered


def test_render_strategy_registry_roundtrip():
    records = parse_strategy_markdown(STRATEGY_MD)
    rendered = render_strategy_registry(records)
    assert "### Category A" in rendered
    assert "| topic1 | method1 | ✅ result1 |" in rendered
