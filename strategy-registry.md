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

### 航運與港口 (Shipping & Port)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| port cargo throughput | `hkdata-find.sh "port"` | ✅ 找到 Censtatd 410-55110 等 |
| port cargo throughput | `hkdata-find.sh "cargo"` | ✅ 找到 14 個 datasets |
| container throughput | `hkdata-find.sh "container"` | ✅ 找到 410-55290 等 |
| vessel arrivals | `hkdata-find.sh "vessel"` | ❌ 0 results |
| vessel arrivals | `hkdata-find.sh "arrival"` | ❌ 只返回訪客/航空 |
| vessel arrivals | `hkdata-find.sh "ship"` | ❌ 只返回 Censtatd 貨運 |
| vessel arrivals | Web search: `site:data.gov.hk vessel arrival port call Hong Kong marine department` | ✅ 找到 `hk-md-mardep-vessel-arrivals-and-departures` |
| Censtatd 報告 CSV 下載 | `curl wbr.html?download_csv=1` | ❌ 返回 HTML，非 CSV |
| Censtatd 表格 JSON API | `api/get.php?id=410-55110` | ✅ JSON API 正常 |
| Marine Dept XML feed | `curl RP05005i.XML` + ElementTree 解析 | ✅ XML 正常，78 筆記錄 |

### 就業與勞動力 (Employment & Labour)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| unemployment by age/sex | `hkdata-find.sh "unemployment"` | ✅ 找到 210-06401 等 72 個表 |
| unemployment by district | `hkdata-find.sh "unemployment district"` | ❌ crash (URL encoding bug) |
| unemployment by district | `hkdata-find.sh "district"` | ❌ 只返回地產/藥物/土地註冊 |
| LFPR by district | Web search: `site:data.gov.hk "unemployment" "district council" censtatd` | ✅ 找到 210-06821 (LF + LFPR by district) |
| LFPR by district | `api/get.php?id=210-06821` | ✅ JSON API 正常，18 區 + Total |
| unemployment rate by district | 探測 210-06820 至 210-06840 | ❌ 全部不存在 |
| unemployment rate by district | 確認 | ❌ data.gov.hk 無此數據（GHS 樣本太小） |

### 房屋 (Housing)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| PRH estate inventory | `hkdata-find.sh "estate"` | ✅ 找到 `hk-housing-eslocator-eslocator` |
| PRH estate inventory | `hkdata-find.sh "housing"` | ✅ 同上 |
| PRH estate inventory | `curl data.housingauthority.gov.hk/psi/rest/export/prh-estates` | ✅ JSON API，197 個 PRH 屋邨 |
| PRH estate by district | API 回傳 `District_Name` 欄位 | ✅ 可按區計數 |
| 區名 join | Housing Authority 用 `&`，Censtatd 用 `and` | ⚠️ 需要標準化（replace `&` → `and`） |

### 社會福利與長者服務 (Social Welfare & Elderly)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| elderly services | `hkdata-find.sh "elderly"` | ✅ 找到 3 個 Censtatd 表 (935-88004/5/6) |
| elderly services | `hkdata-find.sh "welfare"` | ✅ 找到同上 + 社會保障表 |
| elderly services | `hkdata-find.sh "長者"` | ❌ crash (無 URL encoding) |
| elderly services | `curl ...q=%E9%95%B7%E8%80%85...` (手動 encode) | ❌ 0 results (中文索引不全) |
| elderly centres | `hkdata-find.sh "centre"` | ❌ 只返回家庭服務中心、幼兒中心 |
| elderly centres | Web search: `site:data.gov.hk elderly centre social welfare department` | ✅ 找到 4 個 SWD dataset |
| SWD CSV parse | `curl + utf-16-le decode + tab delimiter` | ✅ NEC 172 + DE/DCU 96 + STE 64 |
| Censtatd 服務統計 | `api/get.php?id=935-88005` | ✅ JSON API，但係受助人數唔係中心數 |

### 環境與空氣質素 (Environment & Air Quality)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| air quality | `hkdata-find.sh "air"` | ✅ 找到 Smart Lampposts（但非 AQHI） |
| AQHI | `hkdata-find.sh "AQHI"` | ❌ 0 results |
| pollution | `hkdata-find.sh "pollution"` | ❌ 0 results |
| air quality (multi-word) | `hkdata-find.sh "air quality"` | ❌ crash (URL encoding bug) |
| AQHI | Web search: `site:data.gov.hk AQHI air quality health index EPD monitoring station` | ✅ 找到 4 個 dataset |
| AQHI by station (RSS) | `curl aqhi_ind_rss_Eng.xml` + ElementTree | ✅ 18 站，Causeway Bay AQHI=2 Low |
| PM2.5 by station (XML) | `curl 24pc_Eng.xml` + ElementTree | ✅ 24h hourly data，PM2.5=7.8 µg/m³ |
| AQHI (City Dashboard JSON) | `curl dashboard.data.gov.hk/api/aqhi-individual?format=json` | ✅ JSON array，18 站（比 RSS 慢 ~1h） |

### 交通 — 渡輪 (Transport — Ferry)

| Topic | 嘗試方法 | 結果 |
|-------|---------|------|
| Star Ferry | `hkdata-find.sh "ferry"` | ✅ 找到 Star Ferry dataset |
| TD licensed ferry | `hkdata-find.sh "ferry"` | ❌ 同上結果，但 TD dataset 唔被索引 |
| TD licensed ferry | `hkdata-find.sh "pier"` | ❌ 0 相關結果 |
| TD licensed ferry | `hkdata-find.sh "outlying"` | ❌ 0 相關結果 |
| Sun Ferry ETA | `hkdata-find.sh "ETA"` | ❌ 0 results |
| 全部渡輪 dataset | Web search: `site:data.gov.hk ferry timetable Cheung Chau outlying island Central pier` | ✅ 找到 TD + Sun Ferry + HKKF |
| TD Central→Cheung Chau timetable | `curl ferry_central_cc_timetable_eng.csv` | ✅ CSV，165 行，UTF-8 BOM |
| Sun Ferry ETA (Central→Cheung Chau) | `curl -L sunferry.com.hk/eta/?route=CECC` | ✅ JSON，2 個班次（當前+下一班），含 GPS |
| HKKF routes | `curl -L hkkfeta.com/opendata/route/` | ✅ JSON（需要 trailing slash） |
| HKKF pier | `curl -L hkkfeta.com/opendata/pier/` | ⚠️ 422 Incorrect Parameter（需要額外參數） |

### 通用模式

| Pattern | 適用場景 | 備註 |
|---------|---------|------|
| `site:data.gov.hk <topic> lcsd` | 休閒設施、體育場地 | LCSD 管的設施常用 |
| `site:data.gov.hk <topic> transport` | 交通相關 | |
| `site:data.gov.hk <topic> census` | 人口統計 | |
| `site:data.gov.hk <topic> marine department` | 船舶、港口、海事 | Marine Dept dataset 常用 |
| `site:data.gov.hk <topic> "district council"` | 區議會分區數據 | Censtatd 068xx 系列表格 |
| `site:data.gov.hk <topic> "social welfare department"` | 長者服務、社福中心 | SWD dataset 常用 |
| `site:data.gov.hk <topic> EPD` | 空氣質素、水質、環境 | EPD airteam/marineteam/riverteam dataset |
| `site:data.gov.hk ferry timetable <route/island>` | 渡輪時刻表、ETA | TD + Sun Ferry + HKKF + Star Ferry |
| Censtatd `api/get.php?id=<table-id>` | 統計表格 | JSON API，優先於 CSV 下載；需要 User-Agent header（curl OK，urllib 403） |
| Censtatd `wbr.html?download_csv=1` | 報告 CSV | ❌ 唔好用，返回 HTML |
| Housing Authority PSI API | 房屋數據 | `data.housingauthority.gov.hk/psi/rest/export/<type>` |
| EPD AQHI endpoints | 空氣質素 | `www.aqhi.gov.hk/epd/ddata/html/out/` — RSS/XML，hourly |
| DPO City Dashboard API | 政府數據 dashboard | `dashboard.data.gov.hk/api/<type>?format=json` — JSON，比源頭慢 ~1h |
| TD ferry CSV | 渡輪時刻表 | `www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/en/` — CSV，UTF-8 BOM |
| Sun Ferry ETA API | 渡輪實時到達 | `www.sunferry.com.hk/eta/?route=<code>` — JSON，1 分鐘更新，含 GPS |
| HKKF ETA API | 渡輪實時到達 | `www.hkkfeta.com/opendata/<type>/` — JSON，需要 trailing slash |
| SWD CSV 下載 | 長者中心名單 | ⚠️ UTF-16-LE + tab 分隔，非標準 CSV |
| 單字關鍵字搜尋 | 多字關鍵字 | ⚠️ `hkdata-find.sh` 不支援空格，用單字或 web search 代替 |
| 中文關鍵字搜尋 | 中文 topic | ❌ `hkdata-find.sh` 無 URL encoding + CKAN 中文索引不全；改用英文同義詞 |

---

<!-- 新記錄請加喺上面 -->

