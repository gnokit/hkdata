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

### 2026-06-22 | Task: 港口貨櫃船舶統計搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `vessel` 返回 0 結果
- 搜尋 `arrival` 只返回訪客/航空旅客統計，無船舶到港數據
- 搜尋 `ship` 只返回 Censtatd 貨運吞吐量統計，無船舶計數

**根本原因:** data.gov.hk CKAN `package_search` 對 Marine Department 嘅 vessel arrivals dataset 嘅 metadata 索引不完整，關鍵字 `vessel` / `arrival` / `ship` 都搵唔到 `hk-md-mardep-vessel-arrivals-and-departures`

**解決方案:** 
1. 用 web search 搜尋 `site:data.gov.hk vessel arrival port call Hong Kong marine department`
2. 直接搵到 dataset ID: `hk-md-mardep-vessel-arrivals-and-departures`
3. 用 `package_show` API 取得 XML endpoint URLs
4. 測試 XML endpoint 確認可用

**驗證:** ✅ 成功發現 dataset，XML endpoint 正常返回 78 筆船舶記錄（36 筆貨櫃船）

---

### 2026-06-22 | Task: Censtatd 航運統計報告 CSV 下載

**失敗組件:** Censtatd `wbr.html` CSV 下載端點

**錯誤現象:** 
- Dataset `hk-censtatd-tablechart-b1020008` (Hong Kong Shipping Statistics Report) 嘅 CSV 資源 URL `https://www.censtatd.gov.hk/en/wbr.html?ecode=B10200082026QQ01&download_csv=1` 返回 HTML 頁面（JavaScript 渲染嘅網頁報告），唔係實際 CSV 數據
- `curl -s -L` 跟隨重定向後仍然係 HTML，唔係 CSV

**根本原因:** Censtatd 嘅 `wbr.html` 係一個網頁報告查看器，`download_csv=1` 參數係由 JavaScript 觸發嘅客戶端動作，唔係伺服器端直接文件下載。程式化存取無法取得 CSV。

**解決方案:** 
- 改用同類嘅 Censtatd JSON API（`api/get.php?id=410-55110`）取得貨運吞吐量數據
- 船舶計數方面，改用 Marine Department 嘅實時 XML feed（`RP05005i.XML`）
- 歷史月度船舶到港計數目前無可用嘅程式化 API

**驗證:** ✅ JSON API 正常返回 2036 筆記錄；XML feed 正常返回 78 筆船舶記錄

---

### 2026-06-22 | Task: 區議會分區失業率搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `unemployment` 返回 72 個結果，全部按年齡/性別/教育/行業/職業劃分，無按區議會分區劃分
- 搜尋 `district` 只返回 3 個結果（地產、藥物、土地註冊），無勞動力數據
- 搜尋 `unemployment district` / `labour force district` / `employment district` / `public housing` 全部因為多字關鍵字含空格而 crash（URL encoding bug）
- 探測 table ID 210-06820 至 210-06840 全部返回 Fail

**根本原因:** 
1. data.gov.hk CKAN `package_search` 對多字關鍵字無 URL encoding，空格導致 API 請求失敗
2. Censtatd 嘅 General Household Survey 樣本太小，不支持區議會分區級別嘅失業率估計
3. 區議會分區級別只提供勞動力（LF）同勞動力參與率（LFPR），唔提供失業率（UR）

**解決方案:** 
1. 用單字關鍵字搜尋（`unemployment` 而唔係 `unemployment district`）
2. 用 web search 搜尋 `site:data.gov.hk "unemployment" "district council" censtatd` 搵到 `210-06821`（LFPR by district）
3. 用 Censtatd API `api/get.php?id=210-06821` 取得 LFPR 數據
4. 明確指出 LFPR ≠ 失業率，以 LFPR 作為最接近嘅替代指標

**驗證:** ✅ 找到 210-06821（年度 LFPR by district），但失業率 by district 確認不存在於 data.gov.hk

---

### 2026-06-22 | Task: hkdata-find.sh 多字關鍵字 URL encoding bug

**失敗組件:** `hkdata-find.sh`

**錯誤現象:** 
- 搜尋含空格嘅關鍵字（如 `unemployment district`, `public housing`, `labour force district`）全部 crash，報 `json.decoder.JSONDecodeError: Expecting value`
- 因為 CKAN API 返回非 JSON 響應（空內容或錯誤頁面）

**根本原因:** `hkdata-find.sh` 第 44 行 `q=${KEYWORD}` 無做 URL encoding，空格直接放入 URL 導致 API 請求失敗

**解決方案:** 
- 暫時改用單字關鍵字搜尋
- 永久修復：喺 `hkdata-find.sh` 中加入 URL encoding（如 `python3 -c "import urllib.parse; print(urllib.parse.quote('${KEYWORD}'))"` 或 bash `sed` 替換空格為 `%20`）

**驗證:** ⚠️ 暫時用單字繞過，永久修復尚未實施

---

### 2026-06-22 | Task: 長者服務中文關鍵字搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `長者` 直接 crash（`json.decoder.JSONDecodeError`），因為腳本無 URL encoding
- 手動 URL encode 後搜尋 `%E9%95%B7%E8%80%85`（長者）→ 0 results
- 手動 URL encode 後搜尋 `%E8%80%81%E4%BA%BA`（老人）→ 0 results

**根本原因:** 
1. `hkdata-find.sh` 無 URL encoding，非 ASCII 字元直接放入 URL 导致 400 Bad Request
2. data.gov.hk CKAN `package_search` 對中文關鍵字嘅 metadata 索引不完整，即使正確 URL encode 亦返回 0 結果

**解決方案:** 
1. 用英文關鍵字 `elderly` 搜尋 → 成功搵到 3 個 Censtatd 統計表
2. 用 web search `site:data.gov.hk elderly centre social welfare department` → 搵到 4 個 SWD 中心名單 dataset
3. 中文關鍵字暫時唔可靠 — 必須用英文同義詞或 web search fallback

**驗證:** ✅ 英文關鍵字 + web search 成功發現全部相關 dataset

---

### 2026-06-22 | Task: SWD 長者中心 CSV 格式問題

**失敗組件:** SWD CSV 下載端點

**錯誤現象:** 
- 4 個 SWD 長者中心 CSV 檔案全部用 UTF-16-LE 編碼（BOM `FF FE`），非 UTF-8
- 副檔名係 `.csv` 但實際用 tab 分隔，唔係 comma
- DE/DCU CSV 開頭有標題行同備註行，實際數據由第 3 行開始
- SCE CSV 只有 1 筆資料（已過時，已遷移至 CSDI Portal）

**根本原因:** SWD 用 Excel 匯出格式（UTF-16-LE + tab），唔係標準 CSV

**解決方案:** 
1. 讀取 raw bytes，detect BOM → `utf-16-le` decode
2. Strip BOM character (`\ufeff`)
3. 用 `delimiter='\t'` parse
4. DE/DCU 跳過首 2 行標題/備註

**驗證:** ✅ 成功 parse 全部 4 個 CSV，NEC 172 + DE/DCU 96 + STE 64 = 332 個中心/隊

---

### 2026-06-22 | Task: 空氣質素健康指數 AQHI 搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `AQHI` → 0 results
- 搜尋 `pollution` → 0 results
- 搜尋 `air quality` → crash（多字關鍵字 URL encoding bug）
- 搜尋 `air` → 只找到 Smart Lampposts + 航空運輸統計，無 AQHI

**根本原因:** data.gov.hk CKAN `package_search` 對 EPD airteam 嘅 AQHI dataset 嘅 metadata 索引不完整，關鍵字 `AQHI` / `pollution` / `air quality` 都搵唔到

**解決方案:** 
1. 用 web search 搜尋 `site:data.gov.hk AQHI air quality health index EPD monitoring station Hong Kong`
2. 搵到 4 個相關 dataset：
   - `hk-epd-airteam-current-aqhi-of-individual-air-quality-monitoring-stations` (RSS)
   - `hk-epd-airteam-past24hr-pc-of-individual-air-quality-monitoring-stations` (XML)
   - `hk-dpo-datagovhk2-city-dashboard-aqhi` (JSON/CSV/XML)
   - `hk-epd-lamppost-air-quality-lamppost` (ZIP)
3. 全部 endpoint 測試成功，無死鏈

**驗證:** ✅ 全部 4 個 endpoint 正常返回數據。AQHI=2 (Low)，PM2.5=7.8 µg/m³ for Causeway Bay

**備註:** 此問題原本預期可能遇到「broken endpoint」情況，但實際全部 endpoint 都正常。EPD air quality API 嘅穩定性比預期好。

---

### 2026-06-22 | Task: 離島渡輪航線搜尋

**失敗組件:** `hkdata-find.sh` (CKAN package_search API)

**錯誤現象:** 
- 搜尋 `ferry` → 只找到 Star Ferry（天星小輪），搵唔到 Transport Department 嘅持牌渡輪服務、Sun Ferry ETA、HKKF ETA
- 搜尋 `pier` → 0 相關結果
- 搜尋 `harbour` → 0 相關結果
- 搜尋 `outlying` → 0 相關結果
- 搜尋 `ETA` → 0 results

**根本原因:** data.gov.hk CKAN `package_search` 對渡輪類 dataset 嘅索引不完整。Star Ferry 被索引（因為 dataset name 含 "ferry"），但 TD licensed ferry（dataset name `hk-td-wcms_8-ferry-services-tt-ft` 不含 "ferry" keyword in indexed metadata）、Sun Ferry ETA、HKKF ETA 都唔被索引

**解決方案:** 
1. 用 web search `site:data.gov.hk ferry timetable Cheung Chau outlying island Central pier`
2. 搵到 TD licensed ferry dataset + Sun Ferry ETA + HKKF ETA 共 3 個 dataset
3. 用 `package_show` 取得 endpoint URLs
4. 測試全部 endpoint 確認可用

**驗證:** ✅ 全部 endpoint 正常。Sun Ferry ETA `?route=CECC` 返回 Central→Cheung Chau 實時到達時間。TD CSV 返回 165 行時刻表。

---

### 2026-06-22 | Task: HKKF API trailing slash 問題

**失敗組件:** HKKF ETA API (`www.hkkfeta.com`)

**錯誤現象:** 
- `curl https://www.hkkfeta.com/opendata/pier` 返回空內容（HTTP 301 redirect）
- `curl https://www.hkkfeta.com/opendata/route` 同樣返回空內容

**根本原因:** HKKF API 所有 endpoint 需要 trailing slash（`/opendata/route/` 而唔係 `/opendata/route`）。無 trailing slash 會返回 301 redirect 到加咗 slash 嘅 URL，但 redirect 響應 body 係空嘅

**解決方案:** 
- 所有 HKKF API call 必須加 `-L` flag（跟隨 redirect）或者直接喺 URL 加 trailing slash
- `curl -s -L "https://www.hkkfeta.com/opendata/route/"` → 正常返回 JSON

**驗證:** ✅ 加 trailing slash 後正常返回 routes JSON

---

<!-- 新記錄請加喺上面 -->

