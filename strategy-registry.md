# hkdata Strategy Registry

記錄邊個關鍵字/方法喺邊個 category 成功過，避免重複試失敗的方法。

## 格式

```
## [Category/Topic]
- **關鍵字:** "xxx" → 結果 ✅/❌
- **方法:** "web search: site:data.gov.hk xxx" → 結果
```

---

## 成功策略記錄

### 休閒設施 (Recreation & Sports)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| badminton | `hkdata-find.sh "badminton"` | ❌ 0 results |
| badminton | `hkdata-find.sh "sport"` | ❌ 0 results |
| badminton | `hkdata-find.sh "court"` | ❌ 0 results |
| badminton | `hkdata-find.sh "facility"` | ❌ 0 results |
| badminton | Web search: `site:data.gov.hk badminton lcsd` | ✅ 找到 2 個 datasets |
| badminton | 直接用已知 ID 測試 | ✅ 成功 |

### 通用模式

| Pattern | 適用場景 | 備註 |
|---------|---------|------|
| `site:data.gov.hk <topic> lcsd` | 休閒設施、體育場地 | LCSD 管的設施常用 |
| `site:data.gov.hk <topic> transport` | 交通相關 | |
| `site:data.gov.hk <topic> census` | 人口統計 | |

---

<!-- 新記錄請加喺上面 -->

