# hkdata Strategy Registry

Rendered from `data/experiences.jsonl` — **positive** experiences (what worked).
Do not edit by hand; record an experience and run `hkdata.py log-render`.


### HKKF ETA API (`www.hkkfeta.com`)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| HKKF API trailing slash 問題 | - 所有 HKKF API call 必須加 `-L` flag（跟隨 redirect）或者直接喺 URL 加 trailing slash - `curl -s -L "https://www.hkkfeta.com/opendata/route/"` → 正常返回 JSON | - | 2026-06-22 | failure-log |

### SWD CSV 下載端點

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| SWD 長者中心 CSV 格式問題 | 1. 讀取 raw bytes，detect BOM → `utf-16-le` decode 2. Strip BOM character (`\ufeff`) 3. 用 `delimiter='\t'` parse 4. DE/DCU 跳過首 2 行標題/備註 | - | 2026-06-22 | failure-log |

### Tourism

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Tourism — visitor arrivals / hotel occupancy | Web search: site:data.gov.hk hotel occupancy rate Hong Kong monthly → inspect hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate + hk-censtatd-tablechart-650-80001 | hk-censtatd-tablechart-650-80001, hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate | 2026-09-27 | strategy-registry |

### Uncategorised

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| HK monthly/daily temperature history (HKO) | CLMTEMP CSV from HKO open data API. Filter rows: 5 cols, digit year, target month, numeric value (skip '***'). HQ station code HKO. 2021-2025 Oct means: 26.0/26.2/26.5/27.3/27.4 — 5yr avg 26.7 vs 1991-2020 normal 26.4. | hk-hko-rss-daily-temperature-info-hko | 2026-09-27 | references/weather-oct-climate.md |

### `package_search` (CKAN Solr index) vs `package_list` / `package_show` (DB)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| CKAN package_search 覆蓋率不足（0 結果問題的真正根源） | 建立完整線下 catalog：`catalog-sync` 用 `package_list` 做 seed（1 request），`catalog-sync --full --lang en,tc` 用 `package_show` 逐個抓取（en+tc，~2 小時、可中斷續跑），存成 `.cache/catalog/raw/catalog-NNN.jsonl`（每 500 個一個 shard），再由 `catalog-embed` 建 ChromaDB 向量庫，`catalog-search` 做 dense + 關鍵字混合搜尋。（後續已完全移除 SQLite/FTS5 同 CKAN `search`。） | - | 2026-09-27 | failure-log |

### `search` (CKAN) / `catalog.py` FTS5 / `vectors.py` ChromaDB

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| CKAN package_search 退役，SQLite/FTS5 移除，改用 ChromaDB | 1. 移除 `search` (CKAN) 同 `hkdata-find.sh`、`scripts/hkdata/search.py` 2. 移除 `catalog-reindex` 同 `.cache/catalog/index.db` (FTS5) 3. `catalog-search` 改用 ChromaDB：dense KNN (Ollama `qwen3-embedding:0.6b`, 1024d) + 關鍵字 `$contains`，用 RRF 融合 4. `catalog-embed` 由 JSONL shards 建向量庫；文檔用 `text_hash` 增量更新 5. 爬取加入 `--lang en,tc`，將 tc metadata（例如 `康樂及文化事務署`）寫入 shards 再嵌入 | - | 2026-09-27 | failure-log |

### city

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Hong Kong Public Holidays Data | Official Hong Kong public holidays data for 2024-2026, provided by the 1823 Contact Centre. Contains dates and names of all statutory holidays in Hong Kong. | hk-dpo-statistic-cal | 2026-09-27 | references/city-holidays.md |

### city management
- **update frequency:** as and when there are changes to data

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Government Car Parks Open for Public Use (data.gov.hk) | Location, address, and number of car parking spaces by type for all Government car parks open for public use under the purview of the Government Property Agency. Includes EV charger counts and parking fee information. | hk-gpa-msd-gpa-psi-t-cp`
- **URL:** https://data.gov.hk/en-data/dataset/hk-gpa-msd-gpa-psi-t-cp
- **Provider:** Government Property Agency (GPA)
- **Category:** City Management
- **Update Frequency:** As and when there are changes to data | 2026-09-27 | references/city-parking.md |

### commerce and industry

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Dataset: Consumer Price Index (CPI) - Seasonally Adjusted | This dataset provides monthly seasonally adjusted Consumer Price Index (CPI) figures for Hong Kong. The CPI measures changes in the price level of a market basket of consumer goods and services purchased by households over time. It is the primary indicator of inflation in Hong Kong.  Key indices included: - **Composite CPI**: Overall consumer price index covering all households - **Underlying inflation rate**: CPI excluding effects of government one-off relief measures - **Seasonally adjusted CPI**: Adjusted for seasonal patterns | hk-censtatd-tablechart-510-60004 | 2026-09-27 | references/commerce-cpi.md |

### education

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| School Figures — Day Schools, Enrolment and Classes (EDB) | Territory-wide annual time series used to track the number of schools, student enrolment and operating classes by level (kindergarten / primary / secondary / special) and sector (government / aided / DSS / private / international). These are the tables that show the effect of Hong Kong's falling birth rate on the school system. They do **not** enumerate individual school closures. | education-school-figures | 2026-09-27 | references/education-school-figures.md |
| Education - Number of Day Schools by Type and Region | Provides the number of day schools in Hong Kong by school type/sector and region. Includes data on: - Kindergartens (KG) - Primary schools (PS) - government, aided, private, Direct Subsidy Scheme - Secondary schools (SS) - day schools by sector  Data is available annually from 2013 onwards, broken down by: - School type (kindergarten, primary, secondary) - Sector (public sector, private, Direct Subsidy Scheme) - Region (Hong Kong Island, Kowloon, New Territories) | hk-censtatd-tablechart-925-92023 | 2026-09-27 | references/education-schools.md |

### education
- **update frequency:** yearly
- **description:** student enrolment in primary schools by district council district and grade (p1–p6).

### operating classes, accommodation, enrolment and repeaters by grade
- **dataset id:** `hk-edb-figustat-ope-acc-stu-rep-pri-gra`
- **provider:** education bureau
- **category:** education
- **update frequency:** yearly
- **description:** territory-wide operating classes, accommodation (capacity/places), enrolment and repeaters in primary schools by grade.

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Primary School Enrolment and Accommodation (EDB) | # Primary School Enrolment and Accommodation (EDB) | hk-edb-figustat-stu-pri-dis-gra`
- **Provider:** Education Bureau
- **Category:** Education
- **Update Frequency:** Yearly
- **Description:** Student enrolment in primary schools by District Council district and grade (P1–P6).

### Operating Classes, Accommodation, Enrolment and Repeaters by Grade
- **Dataset ID:** `hk-edb-figustat-ope-acc-stu-rep-pri-gra`
- **Provider:** Education Bureau
- **Category:** Education
- **Update Frequency:** Yearly
- **Description:** Territory-wide operating classes, accommodation (capacity/places), enrolment and repeaters in primary schools by grade. | 2026-09-27 | references/education-primary-enrolment.md |

### employment

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| District-Level Labour Force Statistics | # District-Level Labour Force Statistics | hk-censtatd-tablechart-210-06821 | 2026-09-27 | references/employment-district-lf.md |

### employment and labour

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Dataset: Hong Kong Unemployment Rate | Statistics on Labour Force, Unemployment and Underemployment - Table 210-06401: Unemployed persons and unemployment rate by age and sex.  This dataset provides monthly and annual unemployment statistics for Hong Kong, broken down by age groups and sex.  ### Key Metrics - **Unemployment Rate**: Proportion of unemployed persons in the labour force - **Unemployed Persons**: Number of unemployed individuals (in thousands)  ### Update Frequency Monthly | hk-censtatd-tablechart-210-06401 | 2026-09-27 | references/employment-unemployment.md |

### environment

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Air Quality Data | # Air Quality Data | environment-air-quality | 2026-09-27 | references/environment-air-quality.md |

### environment
- **update frequency:** every mid of month

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Recent River Water Quality Data (data.gov.hk) | Recent Dissolved Oxygen (DO) and 5-day Biochemical Oxygen Demand (BOD5) data at downstream monitoring stations of major rivers in Hong Kong. Data covers 04/2024 to 03/2026. | hk-epd-riverteam-river-water-quality-recent-data`
- **URL:** https://data.gov.hk/en-data/dataset/hk-epd-riverteam-river-water-quality-recent-data
- **Provider:** Environmental Protection Department (EPD)
- **Category:** Environment
- **Update Frequency:** Every mid of month | 2026-09-27 | references/environment-river-water.md |

### finance

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Hong Kong GDP Data | Gross Domestic Product (GDP), implicit price deflator of GDP and per capita GDP. This dataset provides: - GDP at current market prices (名義本地生產總值) - GDP in chained (2023) dollars (以環比物量計算的實質本地生產總值) - GDP implicit price deflator (本地生產總值內含平減物價指數) - Per capita GDP (人均本地生產總值) - Year-on-year percentage changes (按年變動百分率) | hk-censtatd-tablechart-310-31001 | 2026-09-27 | references/finance-gdp.md |

### health

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Hong Kong Birth Statistics | Birth Statistics from Department of Health: - (i) Number of Known Births for Different Sexes and Crude Birth Rate for the Period from 1981 to 2024 - (ii) Percentage Distribution of Live Births by Birth Weight for the Period from 2012 to 2024 | hk-dh-dh_ncddhss-ncdd-dataset-2 | 2026-09-27 | references/health-births.md |

### hkdata.py search + Censtatd/CSTB datasets

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Mainland visitor arrivals and hotel occupancy rate for last month | 1. Use web search fallback: site:data.gov.hk hotel occupancy rate Hong Kong monthly 2. Use Censtatd JSON API for visitor arrivals (650-80001) 3. Use CSTB CSV for hotel occupancy rate 4. Report the latest available month and state the data lag | - | 2026-06-22 | failure-log |

### hkdata.py search + EDB/Censtatd datasets

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Primary school places per 5-year-old child by district | 1. Use web search fallback to find EDB tab0307 (enrolment by district and grade) and Censtatd 110-06811 (population by district and age group) 2. Use P1 enrolment as proxy for P1 places and 0-14 population as proxy for child population 3. Normalize district names (& vs and) before joining 4. State both proxies explicitly in the answer | - | 2026-06-22 | failure-log |

### housing

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Public Housing Estates Inventory | # Public Housing Estates Inventory | hk-housing-eslocator-eslocator | 2026-09-27 | references/housing-estates.md |

### housing
- **update frequency:** annually

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Public Rental Housing Income & Asset Limits (data.gov.hk) | Monthly income and asset limits for Public Rental Housing (PRH) application, broken down by household type and household size. This is the official eligibility criteria used by the Housing Authority to assess PRH applications. | hk-housing-aas-prhicaslmt`
- **URL:** https://data.gov.hk/en-data/dataset/hk-housing-aas-prhicaslmt
- **Provider:** Hong Kong Housing Authority
- **Category:** Housing
- **Update Frequency:** Annually | 2026-09-27 | references/housing-prh.md |

### law and security
- **update frequency:** annual

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Crime Statistics — Persons Arrested (data.gov.hk) | Persons arrested for crime by type of offence, age group and sex. Annual statistics compiled from Hong Kong Police Force records. | hk-censtatd-tablechart-940-92031`
- **URL:** https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-940-92031
- **Provider:** Census and Statistics Department (sourced from Police)
- **Category:** Law and Security
- **Update Frequency:** Annual | 2026-09-27 | references/security-crime.md |

### law and security (`law-and-security` → `security-`)
- **update frequency:** as and when necessary

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| HKPF Crime Statistics in Detail | Hong Kong Police Force crime statistics. The dataset contains two CSV resources:  1. **Crime Statistics in Detail** (`crime_details.csv`) — annual territory-wide crime counts by offence type, in Traditional Chinese + English (Big5 encoded). 2. **Overall Crime and Violent Crime Situation** (`crime_details_overall.csv`) — monthly territory-wide overall and violent crime counts (UTF-8 encoded).  **Important limitation:** Neither resource provides District Council district-level breakdowns. Data is territory-wide only. | hk-hkpf-stat-crm-stat-detail`
- **URL:** https://data.gov.hk/en-data/dataset/hk-hkpf-stat-crm-stat-detail
- **Provider:** Hong Kong Police Force
- **Category:** Law and Security (`law-and-security` → `security-`)
- **Update Frequency:** As and when necessary | 2026-09-27 | references/security-crime-hkpf.md |

### location

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Address Lookup Service (ALS) | # Address Lookup Service (ALS) | hk-dpo-als_01-als | 2026-09-27 | references/location-address.md |

### population

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Hong Kong Population Statistics | Land area, land population, and population density by District Council district. Updated annually with mid-year population estimates. | hk-censtatd-tablechart-110-02001 | 2026-09-27 | references/population-census.md |

### recreation and culture

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Fitness Rooms | Locations of LCSD sports centres that provide a fitness room (健身房 / 健身室), plus the fitness equipment installed in each room. Covers 87 fitness rooms across all 18 districts, with English/Chinese venue names, addresses, room sizes, phone numbers and coordinates.  There is **no real-time fitness-room availability dataset** on data.gov.hk. The "Available Session of … by Venue" family exists only for tennis, badminton, basketball and volleyball courts. | hk-lcsd-facility-facility-fit | 2026-09-27 | references/recreation-fitness-rooms.md |

### recreation and culture
- **update frequency:** quarterly

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Hong Kong Cinemas (data.gov.hk) | Complete inventory of cinemas in Hong Kong including name, address, number of screens, number of seats, website, contact information, and geographical coordinates (longitude/latitude and HK1980 grid coordinates). | hk-cstb-cstb_ccida-hkcinemas`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-hkcinemas
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY | 2026-09-27 | references/recreation-cinema.md |
| Hong Kong Box Office for FDF Projects (data.gov.hk) | Hong Kong box office revenue for film production projects funded under the Film Development Fund (FDF). Tracks commercial performance of government-supported films. | hk-cstb-cstb_ccida-hkboxoffice-for-fdf-projects`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-hkboxoffice-for-fdf-projects
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY | 2026-09-27 | references/recreation-film-boxoffice.md |
| Film Development Fund Approved Projects (data.gov.hk) | List of approved projects funded under the Film Development Fund (FDF) since June 2009. Covers two funding schemes: Film Production Financing (FPF) / Film Production Grant (FPG) and other schemes. | hk-cstb-cstb_ccida-approved-projects-funded-under-fdf`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-approved-projects-funded-under-fdf
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY | 2026-09-27 | references/recreation-film-fund.md |

### recreation, sports and culture

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Badminton Courts (Free Outdoor Pitches/Courts) | Location data for free outdoor badminton courts managed by LCSD. Covers 14 venues across Hong Kong, including district, address, opening hours, ancillary facilities, and contact information. | hk-lcsd-facility-facility-bmtc | 2026-09-27 | references/recreation-badminton-outdoor.md |
| Badminton Court Sessions (Available by Venue) | Real-time availability of badminton court sessions across all LCSD sports centres. Covers 105 venues across 18 districts, with session times, fees, and booking status. Updates every 5 minutes. | hk-lcsd-facility-facility-bmtcvenue | 2026-09-27 | references/recreation-badminton-sessions.md |

### tourism
- **update frequency:** monthly

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Visitor Arrivals by Nationality/Region | Monthly visitor arrivals to Hong Kong by nationality/region. Includes total arrivals and breakdowns such as Chinese Mainland, The Americas, Europe, Africa, Australia/New Zealand/South Pacific, etc. | hk-censtatd-tablechart-650-80001`
- **URL:** https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-650-80001
- **Provider:** Census and Statistics Department
- **Category:** Tourism
- **Update Frequency:** Monthly | 2026-09-27 | references/tourism-arrivals.md |
| Hotel Room Occupancy Rate | Monthly and annual hotel room occupancy rate (%) in Hong Kong. Data covers the past five years and is provided by the Hong Kong Tourism Board. | hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate
- **Provider:** Culture, Sports and Tourism Bureau (data from Hong Kong Tourism Board)
- **Category:** Tourism
- **Update Frequency:** Monthly | 2026-09-27 | references/tourism-hotel-occupancy.md |

### transport

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Ferry Services — Timetables and Real-time ETA | # Ferry Services — Timetables and Real-time ETA | transport-ferry | 2026-09-27 | references/transport-ferry.md |
| KMB/LWB Bus Real-time ETA | # KMB/LWB Bus Real-time ETA | hk-td-tis_21-etakmb | 2026-09-27 | references/transport-kmb.md |
| Port Cargo Throughput | # Port Cargo Throughput | hk-censtatd-tablechart-410-55110 | 2026-09-27 | references/transport-port-cargo.md |
| Vessel Arrivals and Departures | # Vessel Arrivals and Departures | hk-md-mardep-vessel-arrivals-and-departures | 2026-09-27 | references/transport-vessel-arrivals.md |

### transport
- **update frequency:** monthly

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Monthly Traffic and Transport Digest (CSV) (data.gov.hk) | Comprehensive monthly statistics on Hong Kong's transport system, including passenger journeys by public transport operator, vehicle registration and licensing, driving licences, vehicle inspection, road traffic accidents, tunnel traffic flows, and cross-boundary vehicular traffic. | hk-td-tis_17-monthly-traffic-and-transport-digest-csv`
- **URL:** https://data.gov.hk/en-data/dataset/hk-td-tis_17-monthly-traffic-and-transport-digest-csv
- **Provider:** Transport Department (TD)
- **Category:** Transport
- **Update Frequency:** MONTHLY | 2026-09-27 | references/transport-digest.md |

### transportation
- **update frequency:** every 10 seconds

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| MTR Real-time Train Data (data.gov.hk) | Provide the arrival time information for up to the next four trains of: - Airport Express (機場快線) - Tung Chung Line (東涌線) - Tuen Ma Line (屯馬線) - Tseung Kwan O Line (將軍澳線) - East Rail Line (東鐵線) - South Island Line (南島線) - Tsuen Wan Line (荃灣線) - Island Line (港島線) - Kwun Tong Line (觀塘線) - Disneyland Resort Line (迪士尼線) | transport-mtr | 2026-09-27 | references/transport-mtr.md |

### weather

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Current Weather | # Current Weather | weather-current | 2026-09-27 | references/weather-current.md |
| Sunrise/Sunset Times | # Sunrise/Sunset Times | hk-hko-rss-times-of-sunrise-suntransit-sunset | 2026-09-27 | references/weather-sunrise.md |

### welfare

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| Elderly Centres Inventory | # Elderly Centres Inventory | welfare-elderly-centres | 2026-09-27 | references/welfare-elderly-centres.md |
| Elderly Service Statistics | # Elderly Service Statistics | welfare-elderly-services | 2026-09-27 | references/welfare-elderly-services.md |

### 交通 — 渡輪 (Transport — Ferry)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 交通 — 渡輪 (Transport — Ferry) — Star Ferry | `hkdata-find.sh "ferry"` | - | 2026-09-27 | strategy-registry |
| 交通 — 渡輪 (Transport — Ferry) — 全部渡輪 dataset | Web search: `site:data.gov.hk ferry timetable Cheung Chau outlying island Central pier` | - | 2026-09-27 | strategy-registry |
| 交通 — 渡輪 (Transport — Ferry) — TD Central→Cheung Chau timetable | `curl ferry_central_cc_timetable_eng.csv` | - | 2026-09-27 | strategy-registry |
| 交通 — 渡輪 (Transport — Ferry) — Sun Ferry ETA (Central→Cheung Chau) | `curl -L sunferry.com.hk/eta/?route=CECC` | - | 2026-09-27 | strategy-registry |
| 交通 — 渡輪 (Transport — Ferry) — HKKF routes | `curl -L hkkfeta.com/opendata/route/` | - | 2026-09-27 | strategy-registry |

### 休閒設施 (Recreation & Sports)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 休閒設施 (Recreation & Sports) — badminton | 直接用已知 ID 測試 | - | 2026-09-27 | strategy-registry |

### 就業與勞動力 (Employment & Labour)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 就業與勞動力 (Employment & Labour) — unemployment by age/sex | `hkdata-find.sh "unemployment"` | - | 2026-09-27 | strategy-registry |
| 就業與勞動力 (Employment & Labour) — LFPR by district | `api/get.php?id=210-06821` | - | 2026-09-27 | strategy-registry |

### 房屋 (Housing)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 房屋 (Housing) — PRH estate inventory | `curl data.housingauthority.gov.hk/psi/rest/export/prh-estates` | - | 2026-09-27 | strategy-registry |
| 房屋 (Housing) — PRH estate by district | API 回傳 `District_Name` 欄位 | - | 2026-09-27 | strategy-registry |

### 環境與空氣質素 (Environment & Air Quality)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 環境與空氣質素 (Environment & Air Quality) — air quality | `hkdata-find.sh "air"` | - | 2026-09-27 | strategy-registry |
| 環境與空氣質素 (Environment & Air Quality) — AQHI | Web search: `site:data.gov.hk AQHI air quality health index EPD monitoring station` | - | 2026-09-27 | strategy-registry |
| 環境與空氣質素 (Environment & Air Quality) — AQHI by station (RSS) | `curl aqhi_ind_rss_Eng.xml` + ElementTree | - | 2026-09-27 | strategy-registry |
| 環境與空氣質素 (Environment & Air Quality) — PM2.5 by station (XML) | `curl 24pc_Eng.xml` + ElementTree | - | 2026-09-27 | strategy-registry |
| 環境與空氣質素 (Environment & Air Quality) — AQHI (City Dashboard JSON) | `curl dashboard.data.gov.hk/api/aqhi-individual?format=json` | - | 2026-09-27 | strategy-registry |

### 社會福利與長者服務 (Social Welfare & Elderly)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 社會福利與長者服務 (Social Welfare & Elderly) — elderly centres | Web search: `site:data.gov.hk elderly centre social welfare department` | - | 2026-09-27 | strategy-registry |
| 社會福利與長者服務 (Social Welfare & Elderly) — SWD CSV parse | `curl + utf-16-le decode + tab delimiter` | - | 2026-09-27 | strategy-registry |
| 社會福利與長者服務 (Social Welfare & Elderly) — Censtatd 服務統計 | `api/get.php?id=935-88005` | - | 2026-09-27 | strategy-registry |
| 社會福利與長者服務 (Social Welfare & Elderly) — elderly services | `hkdata-find.sh "welfare"` | - | 2026-09-27 | strategy-registry |

### 航運與港口 (Shipping & Port)

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 航運與港口 (Shipping & Port) — port cargo throughput | `hkdata-find.sh "cargo"` | - | 2026-09-27 | strategy-registry |
| 航運與港口 (Shipping & Port) — container throughput | `hkdata-find.sh "container"` | - | 2026-09-27 | strategy-registry |
| 航運與港口 (Shipping & Port) — Censtatd 表格 JSON API | `api/get.php?id=410-55110` | - | 2026-09-27 | strategy-registry |
| 航運與港口 (Shipping & Port) — Marine Dept XML feed | `curl RP05005i.XML` + ElementTree 解析 | - | 2026-09-27 | strategy-registry |

### 通用模式

| Topic | Method | Datasets | Date | Source |
|-------|--------|----------|------|--------|
| 通用模式 — Pattern | 適用場景 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> lcsd` | 休閒設施、體育場地 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> transport` | 交通相關 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> census` | 人口統計 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> marine department` | 船舶、港口、海事 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> "district council"` | 區議會分區數據 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> "social welfare department"` | 長者服務、社福中心 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk <topic> EPD` | 空氣質素、水質、環境 | - | 2026-09-27 | strategy-registry |
| 通用模式 — `site:data.gov.hk ferry timetable <route/island>` | 渡輪時刻表、ETA | - | 2026-09-27 | strategy-registry |
| 通用模式 — Censtatd `api/get.php?id=<table-id>` | 統計表格 | - | 2026-09-27 | strategy-registry |
| 通用模式 — Housing Authority PSI API | 房屋數據 | - | 2026-09-27 | strategy-registry |
| 通用模式 — EPD AQHI endpoints | 空氣質素 | - | 2026-09-27 | strategy-registry |
| 通用模式 — DPO City Dashboard API | 政府數據 dashboard | - | 2026-09-27 | strategy-registry |
| 通用模式 — TD ferry CSV | 渡輪時刻表 | - | 2026-09-27 | strategy-registry |
| 通用模式 — Sun Ferry ETA API | 渡輪實時到達 | - | 2026-09-27 | strategy-registry |
| 通用模式 — HKKF ETA API | 渡輪實時到達 | - | 2026-09-27 | strategy-registry |
| 通用模式 — 完整 catalog 搜尋（取代不可靠嘅 package_search） | `catalog-sync --full --lang en,tc` → JSONL shards → `.venv/bin/python hkdata.py catalog-embed`（ChromaDB + Ollama qwen3-embedding:0.6b）→ `catalog-search "<topic>"`（dense + 關鍵字 RRF 融合） | - | 2026-09-27 | strategy-registry |
| 通用模式 — catalog-search（ChromaDB 混合檢索） | `catalog-sync --full --lang en,tc` → JSONL shards → `.venv/bin/python hkdata.py catalog-embed`（Ollama qwen3-embedding:0.6b）→ `catalog-search "<topic>"`（dense + keyword，RRF 融合） | - | 2026-09-27 | strategy-registry |
| 通用模式 — 學校數目／學生人數／殺校 趨勢 | `catalog-search "school places" / "student numbers"` → EDB figures CSV（tab0101 學校數目、tab0103 學生人數、tab0302 班數/容量）→ 對照 `health-births`（出生人數） | - | 2026-09-27 | strategy-registry |

