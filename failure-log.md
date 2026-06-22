# hkdata Failure Log

記錄每次 script/tool 失敗的原因和解決方案。Subagent 起動時自動讀取。

## 格式

```
## [日期] Task: <任務描述>

**失敗組件:** <script/API/tool 名稱>
**錯誤現象:** <實際輸出/錯誤信息>
**根本原因:** <為什麼失敗>
**解決方案:** <用咩方法搞掂>
**驗證:** <成功與否>
```

---

## 記錄

### 2026-03-18 | Task: 羽毛球場地搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `badminton`, `sport`, `court`, `facility`, `recreation`, `venue`, `leisure`, `court`, `gymnasium`, `ball`, `indoor`, `outdoor`, `booking` 等 14 個關鍵字全部返回 0 結果
- Script 本身無報錯，但 CKAN metadata indexing 有問題

**根本原因:** data.gov.hk 的 CKAN `package_search` API 對部分 dataset 嘅 metadata 索引不完整，特别是 LCSD 設施類 dataset

**解決方案:** 
1. 用 web search 搜尋 `site:data.gov.hk badminton lcsd facility`
2. 直接搵到 dataset IDs: `hk-lcsd-facility-facility-bmtc` 和 `hk-lcsd-facility-facility-bmtcvenue`
3. 用 `package_show` API 檢查 dataset metadata
4. Test API endpoint 確認可用

**驗證:** ✅ 成功發現 2 個 dataset，創建完整文檔

---

<!-- 新記錄請加喺上面 -->

