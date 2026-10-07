# hkdata Failure Log

Rendered from `data/experiences.jsonl` — **negative** experiences (dead ends).
Do not edit by hand; record an experience and run `hkdata.py log-render`.


### 2026-10-07 | geodata.gov.hk retired portal

- **Kind:** negative
- **Category:** location
- **Method:** geodata.gov.hk has been retired; its geo-spatial endpoints moved to the CSDI Portal — use www.map.gov.hk/gs/api/... (see the CSDI API docs) instead.
- **Outcome:** pitfall
- **Caveats:** Any reference to a geodata.gov.hk URL is a dead path — re-route to map.gov.hk/gs/api
- **Source:** manual

---

### 2026-10-07 | Endpoint 403 without User-Agent

- **Kind:** negative
- **Category:** 通用模式
- **Method:** Some department APIs (Censtatd, LandsD, map APIs) return 403 to the bare Python urllib agent; the hkdata CLI already sends a browser-like User-Agent on every fetch — reuse that header in any ad-hoc fetch instead of assuming the endpoint is down.
- **Outcome:** pitfall
- **Caveats:** curl works because it sends a User-Agent by default; urllib without headers does not
- **Source:** manual

---

### 2026-10-07 | Procedural / application-form questions

- **Kind:** negative
- **Category:** 通用模式
- **Method:** data.gov.hk carries statistics and fee tables, not application steps or forms. Redirect procedural questions to the department's website and say so, rather than logging a 'dataset miss'.
- **Outcome:** pitfall
- **Caveats:** Do not treat a procedural question as a missing dataset
- **Source:** manual

---

### 2026-09-27 | 交通 — 渡輪 (Transport — Ferry) — TD licensed ferry

- **Kind:** negative
- **Category:** 交通 — 渡輪 (Transport — Ferry)
- **Method:** `hkdata-find.sh "outlying"`
- **Outcome:** ❌ 0 相關結果
- **Source:** strategy-registry

---

### 2026-09-27 | 交通 — 渡輪 (Transport — Ferry) — Sun Ferry ETA

- **Kind:** negative
- **Category:** 交通 — 渡輪 (Transport — Ferry)
- **Method:** `hkdata-find.sh "ETA"`
- **Outcome:** ❌ 0 results
- **Source:** strategy-registry

---

### 2026-09-27 | 交通 — 渡輪 (Transport — Ferry) — HKKF pier

- **Kind:** negative
- **Category:** 交通 — 渡輪 (Transport — Ferry)
- **Method:** `curl -L hkkfeta.com/opendata/pier/`
- **Outcome:** ⚠️ 422 Incorrect Parameter（需要額外參數）
- **Source:** strategy-registry

---

### 2026-09-27 | 就業與勞動力 (Employment & Labour) — unemployment by district

- **Kind:** negative
- **Category:** 就業與勞動力 (Employment & Labour)
- **Method:** `hkdata-find.sh "district"`
- **Outcome:** ❌ 只返回地產/藥物/土地註冊
- **Source:** strategy-registry

---

### 2026-09-27 | 就業與勞動力 (Employment & Labour) — unemployment rate by district

- **Kind:** negative
- **Category:** 就業與勞動力 (Employment & Labour)
- **Method:** 確認
- **Outcome:** ❌ data.gov.hk 無此數據（GHS 樣本太小）
- **Source:** strategy-registry

---

### 2026-09-27 | 房屋 (Housing) — 區名 join

- **Kind:** negative
- **Category:** 房屋 (Housing)
- **Method:** Housing Authority 用 `&`，Censtatd 用 `and`
- **Outcome:** ⚠️ 需要標準化（replace `&` → `and`）
- **Source:** strategy-registry

---

### 2026-09-27 | 環境與空氣質素 (Environment & Air Quality) — pollution

- **Kind:** negative
- **Category:** 環境與空氣質素 (Environment & Air Quality)
- **Method:** `hkdata-find.sh "pollution"`
- **Outcome:** ❌ 0 results
- **Source:** strategy-registry

---

### 2026-09-27 | 環境與空氣質素 (Environment & Air Quality) — air quality (multi-word)

- **Kind:** negative
- **Category:** 環境與空氣質素 (Environment & Air Quality)
- **Method:** `hkdata-find.sh "air quality"`
- **Outcome:** ❌ crash (URL encoding bug)
- **Source:** strategy-registry

---

### 2026-09-27 | 社會福利與長者服務 (Social Welfare & Elderly) — elderly services

- **Kind:** negative
- **Category:** 社會福利與長者服務 (Social Welfare & Elderly)
- **Method:** `curl ...q=%E9%95%B7%E8%80%85...` (手動 encode)
- **Outcome:** ❌ 0 results (中文索引不全)
- **Source:** strategy-registry

---

### 2026-09-27 | 航運與港口 (Shipping & Port) — Censtatd 報告 CSV 下載

- **Kind:** negative
- **Category:** 航運與港口 (Shipping & Port)
- **Method:** `curl wbr.html?download_csv=1`
- **Outcome:** ❌ 返回 HTML，非 CSV
- **Source:** strategy-registry

---

### 2026-09-27 | 通用模式 — Censtatd `wbr.html?download_csv=1`

- **Kind:** negative
- **Category:** 通用模式
- **Method:** 報告 CSV
- **Outcome:** ❌ 唔好用，返回 HTML
- **Source:** strategy-registry

---

### 2026-09-27 | 通用模式 — SWD CSV 下載

- **Kind:** negative
- **Category:** 通用模式
- **Method:** 長者中心名單
- **Outcome:** ⚠️ UTF-16-LE + tab 分隔，非標準 CSV
- **Source:** strategy-registry

---

### 2026-09-27 | 通用模式 — 單字關鍵字搜尋

- **Kind:** negative
- **Category:** 通用模式
- **Method:** 多字關鍵字
- **Outcome:** ⚠️ `hkdata-find.sh` 不支援空格，用單字或 web search 代替
- **Source:** strategy-registry

---

### 2026-09-27 | 通用模式 — 中文關鍵字搜尋

- **Kind:** negative
- **Category:** 通用模式
- **Method:** 中文 topic
- **Outcome:** ❌ `hkdata-find.sh` 無 URL encoding + CKAN 中文索引不全；改用英文同義詞
- **Source:** strategy-registry

---

### 2026-09-27 | Law and Security — crime / violent crime

- **Kind:** negative
- **Category:** Law and Security
- **Datasets:** hk-hkpf-stat-crm-stat-detail
- **Method:** Web search: site:data.gov.hk crime police → inspect hk-hkpf-stat-crm-stat-detail → test CSV endpoints
- **Outcome:** ✅ Found HKPF crime CSVs; district-level data NOT available on data.gov.hk
- **Caveats:** data.gov.hk CKAN package_search does not index "crime" or "violent crime" keywords. Hong Kong Police Force does not publish District Council district-level violent crime statistics on data.gov.hk.
- **Details:** （較早記錄）District-level violent crime trend by district: 1. Use web search fallback: site:data.gov.hk crime police to find hk-hkpf-stat-crm-stat-detail
2. Use HKPF CSV endpoints for territory-wide trends
3. Report honestly that district-level data is unavailable; use territory-wide proxy with explicit caveat
- **Source:** strategy-registry

---

### 2026-09-27 | Education — primary school places / enrolment by district

- **Kind:** negative
- **Category:** Education
- **Method:** Web search: site:data.gov.hk primary school places district EDB → tab0307_en.csv + 110-06811 JSON API
- **Outcome:** ✅ Found EDB enrolment by district and Censtatd population by district/age group; exact 5-year-old and district-level places unavailable, use proxies
- **Source:** strategy-registry

---

### 2026-09-27 | 警方智慧閉路電視（smart CCTV）數目查詢

- **Kind:** negative
- **Category:** catalog-search / data.gov.hk（HKPF 數據集）
- **Method:** 用最接近嘅代用數據並加註明：(1) 運輸署衝紅燈攝影機路口 230 個、偵速攝影機機箱 164 個；(2) 食環署非法棄置黑點 IP 攝影機（CSDI）；(3) SCIOCS 2024 年度報告 — 截取通訊及監察授權（非鏡頭）：發出 25、續期 13。清楚標明三者都唔等於警方智慧閉路電視。
- **Outcome:** unavailable
- **Caveats:** 警方智慧閉路電視（及公共地方 CCTV）部署數目並非 data.gov.hk 開放數據；屬保安／執法運作資料，只在立法會文件／新聞公報公布。
- **Details:** - 搜尋 `CCTV`/`camera`/`surveillance camera`/`閉路電視`/`監控`/`智慧燈柱`/`天眼` 均無 HKPF 閉路電視數據
- 33 個 `hk-hkpf-*` 數據集全部同鏡頭無關（Personnel、Arrested、Traffic Prosecutions、Complaints、Marine Police Bases 等）
- 全 catalog 無任何 dataset 提及警方公共地方 CCTV／智慧閉路電視數目 警方智慧閉路電視（及公共地方 CCTV）部署數目並非 data.gov.hk 開放數據；屬保安／執法運作資料，只在立法會文件／新聞公報公布。 ✅ 確認 data.gov.hk 無此數據；已用 catalog-search 全 catalog 掃描（3,822 個 dataset）
- **Source:** failure-log

---

### 2026-09-27 | 休閒設施 (Recreation & Sports) — badminton

- **Kind:** negative
- **Category:** 休閒設施 (Recreation & Sports)
- **Method:** `hkdata-find.sh "facility"`
- **Outcome:** ❌ 0 results
- **Source:** strategy-registry

---

### 2026-09-27 | 環境與空氣質素 (Environment & Air Quality) — AQHI

- **Kind:** negative
- **Category:** 環境與空氣質素 (Environment & Air Quality)
- **Method:** `hkdata-find.sh "AQHI"`
- **Outcome:** ❌ 0 results
- **Source:** strategy-registry

---

### 2026-09-27 | 社會福利與長者服務 (Social Welfare & Elderly) — elderly centres

- **Kind:** negative
- **Category:** 社會福利與長者服務 (Social Welfare & Elderly)
- **Method:** `hkdata-find.sh "centre"`
- **Outcome:** ❌ 只返回家庭服務中心、幼兒中心
- **Source:** strategy-registry

---

### 2026-09-27 | 航運與港口 (Shipping & Port) — vessel arrivals

- **Kind:** negative
- **Category:** 航運與港口 (Shipping & Port)
- **Method:** `hkdata-find.sh "ship"`
- **Outcome:** ❌ 只返回 Censtatd 貨運
- **Source:** strategy-registry

---

### 2026-06-22 | Censtatd 航運統計報告 CSV 下載

- **Kind:** negative
- **Category:** Censtatd `wbr.html` CSV 下載端點
- **Method:** - 改用同類嘅 Censtatd JSON API（`api/get.php?id=410-55110`）取得貨運吞吐量數據
- 船舶計數方面，改用 Marine Department 嘅實時 XML feed（`RP05005i.XML`）
- 歷史月度船舶到港計數目前無可用嘅程式化 API
- **Outcome:** unavailable
- **Caveats:** Censtatd 嘅 `wbr.html` 係一個網頁報告查看器，`download_csv=1` 參數係由 JavaScript 觸發嘅客戶端動作，唔係伺服器端直接文件下載。程式化存取無法取得 CSV。
- **Details:** - Dataset `hk-censtatd-tablechart-b1020008` (Hong Kong Shipping Statistics Report) 嘅 CSV 資源 URL `https://www.censtatd.gov.hk/en/wbr.html?ecode=B10200082026QQ01&download_csv=1` 返回 HTML 頁面（JavaScript 渲染嘅網頁報告），唔係實際 CSV 數據
- `curl -s -L` 跟隨重定向後仍然係 HTML，唔係 CSV Censtatd 嘅 `wbr.html` 係一個網頁報告查看器，`download_csv=1` 參數係由 JavaScript 觸發嘅客戶端動作，唔係伺服器端直接文件下載。程式化存取無法取得 CSV。 ✅ JSON API 正常返回 2036 筆記錄；XML feed 正常返回 78 筆船舶記錄
- **Source:** failure-log

---

### 2026-06-22 | 區議會分區失業率搜尋

- **Kind:** negative
- **Category:** `hkdata-find.sh` (CKAN package_search API)
- **Method:** 1. 用單字關鍵字搜尋（`unemployment` 而唔係 `unemployment district`）
2. 用 web search 搜尋 `site:data.gov.hk "unemployment" "district council" censtatd` 搵到 `210-06821`（LFPR by district）
3. 用 Censtatd API `api/get.php?id=210-06821` 取得 LFPR 數據
4. 明確指出 LFPR ≠ 失業率，以 LFPR 作為最接近嘅替代指標
- **Outcome:** unavailable
- **Caveats:** 1. data.gov.hk CKAN `package_search` 對多字關鍵字無 URL encoding，空格導致 API 請求失敗
2. Censtatd 嘅 General Household Survey 樣本太小，不支持區議會分區級別嘅失業率估計
3. 區議會分區級別只提供勞動力（LF）同勞動力參與率（LFPR），唔提供失業率（UR）
- **Details:** - 搜尋 `unemployment` 返回 72 個結果，全部按年齡/性別/教育/行業/職業劃分，無按區議會分區劃分
- 搜尋 `district` 只返回 3 個結果（地產、藥物、土地註冊），無勞動力數據
- 搜尋 `unemployment district` / `labour force district` / `employment district` / `public housing` 全部因為多字關鍵字含空格而 crash（URL encoding bug）
- 探測 table ID 210-06820 至 210-06840 全部返回 Fail 1. data.gov.hk CKAN `package_search` 對多字關鍵字無 URL encoding，空格導致 API 請求失敗
2. Censtatd 嘅 General Household Survey 樣本太小，不支持區議會分區級別嘅失業率估計
3. 區議會分區級別只提供勞動力（LF）同勞動力參與率（LFPR），唔提供失業率（UR） ✅ 找到 210-06821（年度 LFPR by district），但失業率 by district 確認不存在於 data.gov.hk
- **Source:** failure-log

---

### 2026-06-22 | hkdata-find.sh 多字關鍵字 URL encoding bug

- **Kind:** negative
- **Category:** `hkdata-find.sh`
- **Method:** - 暫時改用單字關鍵字搜尋
- 永久修復：喺 `hkdata-find.sh` 中加入 URL encoding（如 `python3 -c "import urllib.parse; print(urllib.parse.quote('${KEYWORD}'))"` 或 bash `sed` 替換空格為 `%20`）
- **Outcome:** unavailable
- **Caveats:** `hkdata-find.sh` 第 44 行 `q=${KEYWORD}` 無做 URL encoding，空格直接放入 URL 導致 API 請求失敗
- **Details:** - 搜尋含空格嘅關鍵字（如 `unemployment district`, `public housing`, `labour force district`）全部 crash，報 `json.decoder.JSONDecodeError: Expecting value`
- 因為 CKAN API 返回非 JSON 響應（空內容或錯誤頁面） `hkdata-find.sh` 第 44 行 `q=${KEYWORD}` 無做 URL encoding，空格直接放入 URL 導致 API 請求失敗 ⚠️ 暫時用單字繞過，永久修復尚未實施
- **Source:** failure-log

---

### 2026-06-22 | 長者服務中文關鍵字搜尋

- **Kind:** negative
- **Category:** `hkdata-find.sh` (CKAN package_search API)
- **Method:** 1. 用英文關鍵字 `elderly` 搜尋 → 成功搵到 3 個 Censtatd 統計表
2. 用 web search `site:data.gov.hk elderly centre social welfare department` → 搵到 4 個 SWD 中心名單 dataset
3. 中文關鍵字暫時唔可靠 — 必須用英文同義詞或 web search fallback
- **Outcome:** unavailable
- **Caveats:** 1. `hkdata-find.sh` 無 URL encoding，非 ASCII 字元直接放入 URL 导致 400 Bad Request
2. data.gov.hk CKAN `package_search` 對中文關鍵字嘅 metadata 索引不完整，即使正確 URL encode 亦返回 0 結果
- **Details:** - 搜尋 `長者` 直接 crash（`json.decoder.JSONDecodeError`），因為腳本無 URL encoding
- 手動 URL encode 後搜尋 `%E9%95%B7%E8%80%85`（長者）→ 0 results
- 手動 URL encode 後搜尋 `%E8%80%81%E4%BA%BA`（老人）→ 0 results 1. `hkdata-find.sh` 無 URL encoding，非 ASCII 字元直接放入 URL 导致 400 Bad Request
2. data.gov.hk CKAN `package_search` 對中文關鍵字嘅 metadata 索引不完整，即使正確 URL encode 亦返回 0 結果 ✅ 英文關鍵字 + web search 成功發現全部相關 dataset
- **Source:** failure-log

---

### 2026-06-22 | 空氣質素健康指數 AQHI 搜尋

- **Kind:** negative
- **Category:** `hkdata-find.sh` (CKAN package_search API)
- **Datasets:** hk-dpo-datagovhk2-city-dashboard-aqhi, hk-epd-airteam-current-aqhi-of-individual-air-quality-monitoring-stations, hk-epd-airteam-past24hr-pc-of-individual-air-quality-monitoring-stations, hk-epd-lamppost-air-quality-lamppost
- **Method:** 1. 用 web search 搜尋 `site:data.gov.hk AQHI air quality health index EPD monitoring station Hong Kong`
2. 搵到 4 個相關 dataset：
   - `hk-epd-airteam-current-aqhi-of-individual-air-quality-monitoring-stations` (RSS)
   - `hk-epd-airteam-past24hr-pc-of-individual-air-quality-monitoring-stations` (XML)
   - `hk-dpo-datagovhk2-city-dashboard-aqhi` (JSON/CSV/XML)
   - `hk-epd-lamppost-air-quality-lamppost` (ZIP)
3. 全部 endpoint 測試成功，無死鏈
- **Outcome:** unavailable
- **Caveats:** data.gov.hk CKAN `package_search` 對 EPD airteam 嘅 AQHI dataset 嘅 metadata 索引不完整，關鍵字 `AQHI` / `pollution` / `air quality` 都搵唔到
- **Details:** - 搜尋 `AQHI` → 0 results
- 搜尋 `pollution` → 0 results
- 搜尋 `air quality` → crash（多字關鍵字 URL encoding bug）
- 搜尋 `air` → 只找到 Smart Lampposts + 航空運輸統計，無 AQHI data.gov.hk CKAN `package_search` 對 EPD airteam 嘅 AQHI dataset 嘅 metadata 索引不完整，關鍵字 `AQHI` / `pollution` / `air quality` 都搵唔到 ✅ 全部 4 個 endpoint 正常返回數據。AQHI=2 (Low)，PM2.5=7.8 µg/m³ for Causeway Bay
- **Source:** failure-log

---

### 2026-06-22 | 離島渡輪航線搜尋

- **Kind:** negative
- **Category:** `hkdata-find.sh` (CKAN package_search API)
- **Method:** 1. 用 web search `site:data.gov.hk ferry timetable Cheung Chau outlying island Central pier`
2. 搵到 TD licensed ferry dataset + Sun Ferry ETA + HKKF ETA 共 3 個 dataset
3. 用 `package_show` 取得 endpoint URLs
4. 測試全部 endpoint 確認可用
- **Outcome:** unavailable
- **Caveats:** data.gov.hk CKAN `package_search` 對渡輪類 dataset 嘅索引不完整。Star Ferry 被索引（因為 dataset name 含 "ferry"），但 TD licensed ferry（dataset name `hk-td-wcms_8-ferry-services-tt-ft` 不含 "ferry" keyword in indexed metadata）、Sun Ferry ETA、HKKF ETA 都唔被索引
- **Details:** - 搜尋 `ferry` → 只找到 Star Ferry（天星小輪），搵唔到 Transport Department 嘅持牌渡輪服務、Sun Ferry ETA、HKKF ETA
- 搜尋 `pier` → 0 相關結果
- 搜尋 `harbour` → 0 相關結果
- 搜尋 `outlying` → 0 相關結果
- 搜尋 `ETA` → 0 results data.gov.hk CKAN `package_search` 對渡輪類 dataset 嘅索引不完整。Star Ferry 被索引（因為 dataset name 含 "ferry"），但 TD licensed ferry（dataset name `hk-td-wcms_8-ferry-services-tt-ft` 不含 "ferry" keyword in indexed metadata）、Sun Ferry ETA、HKKF ETA 都唔被索引 ✅ 全部 endpoint 正常。Sun Ferry ETA `?route=CECC` 返回 Central→Cheung Chau 實時到達時間。TD CSV 返回 165 行時刻表。
- **Source:** failure-log

---

