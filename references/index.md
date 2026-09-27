# Dataset Registry

Master index of all verified Hong Kong open data APIs.

## Verified Datasets

| Dataset | Category | Description | File |
|---------|----------|-------------|------|
| KMB Bus ETA | transport | Real-time bus arrival times | [transport-kmb.md](transport-kmb.md) |
| Sunrise/Sunset | weather | Daily sunrise and sunset times | [weather-sunrise.md](weather-sunrise.md) |
| Current Weather | weather | Real-time weather and forecasts | [weather-current.md](weather-current.md) |
| Address Lookup | location | Hong Kong address geocoding | [location-address.md](location-address.md) |
| Population Statistics | population | HK population by district (mid-year estimates) | [population-census.md](population-census.md) |
| GDP Statistics | finance | GDP, price deflator, per capita GDP | [finance-gdp.md](finance-gdp.md) |
| Birth Statistics | health | Live births by sex and crude birth rate (1981-2024) | [health-births.md](health-births.md) |
| Unemployment Rate | employment | Monthly unemployment rate by age and sex | [employment-unemployment.md](employment-unemployment.md) |
| Consumer Price Index | commerce | Monthly CPI and inflation rate (Jan 2026: 1.1%) | [commerce-cpi.md](commerce-cpi.md) |
| Badminton Courts (Free Outdoor) | recreation | Free outdoor badminton court locations (14 venues) | [recreation-badminton-outdoor.md](recreation-badminton-outdoor.md) |
| Badminton Court Sessions | recreation | Real-time session availability across 105 LCSD venues (5-min updates) | [recreation-badminton-sessions.md](recreation-badminton-sessions.md) |
| School Statistics | education | Number of schools by type/sector and region (2024: 590 primary schools) | [education-schools.md](education-schools.md) |
| Primary School Enrolment | education | Primary school enrolment by district and grade; territory-wide accommodation | [education-primary-enrolment.md](education-primary-enrolment.md) |
| School Figures (day schools/enrolment/classes) | education | EDB annual series: schools, enrolment, classes by level/sector (2015–2025) | [education-school-figures.md](education-school-figures.md) |
| Public Holidays | city | Hong Kong public holidays 2024-2026 (official 1823 data) | [city-holidays.md](city-holidays.md) |
| PRH Income & Asset Limits | housing | Monthly income/asset limits for public rental housing application | [housing-prh.md](housing-prh.md) |
| River Water Quality | environment | Recent DO and BOD5 data at downstream river monitoring stations | [environment-river-water.md](environment-river-water.md) |
| Monthly Transport Digest | transport | Monthly CSV stats: passenger journeys, accidents, tunnel flows, licences | [transport-digest.md](transport-digest.md) |
| Government Car Parks | city | Government car parks open for public use: locations, spaces, fees | [city-parking.md](city-parking.md) |
| Crime Statistics (Persons Arrested) | security | Persons arrested for crime by offence type, age group and sex (Censtatd) | [security-crime.md](security-crime.md) |
| HKPF Crime Statistics in Detail | security | Territory-wide overall and violent crime CSVs from HKPF (no district breakdown) | [security-crime-hkpf.md](security-crime-hkpf.md) |
| Fitness Rooms | recreation | LCSD sports centres with fitness rooms (87) + equipment (1,925 rows) | [recreation-fitness-rooms.md](recreation-fitness-rooms.md) |
| Cinemas | recreation | HK cinema inventory: locations, screens, seats, coordinates | [recreation-cinema.md](recreation-cinema.md) |
| Film Development Fund | recreation | Approved FDF film projects since 2009: titles, funding, dates | [recreation-film-fund.md](recreation-film-fund.md) |
| Film Box Office (FDF) | recreation | HK box office revenue for FDF-funded films | [recreation-film-boxoffice.md](recreation-film-boxoffice.md) |
| Port Cargo Throughput | transport | Quarterly port cargo tonnage + YoY % change (Censtatd JSON API) | [transport-port-cargo.md](transport-port-cargo.md) |
| Vessel Arrivals & Departures | transport | Real-time ocean-going vessel arrivals/departures (Marine Dept XML, 20-min) | [transport-vessel-arrivals.md](transport-vessel-arrivals.md) |
| PRH Estates Inventory | housing | All HA public rental housing estates with district, coordinates, block counts (197 PRH estates) | [housing-estates.md](housing-estates.md) |
| District-Level Labour Force | employment | Annual LF count and LFPR by District Council district (2025; NOT unemployment rate) | [employment-district-lf.md](employment-district-lf.md) |
| Elderly Centres Inventory | welfare | SWD elderly centres: NEC (172), DE/DCU (96), STE (64) — CSV, UTF-16-LE tab-delimited | [welfare-elderly-centres.md](welfare-elderly-centres.md) |
| Elderly Service Statistics | welfare | Annual recipient counts for community support, community care, residential care (2024) | [welfare-elderly-services.md](welfare-elderly-services.md) |
| Air Quality (AQHI + Pollutants) | environment | Real-time AQHI + PM2.5/PM10/NO2/SO2/O3/CO at 18 stations (EPD RSS/XML + DPO JSON, hourly) | [environment-air-quality.md](environment-air-quality.md) |
| Ferry Services (Timetables + ETA) | transport | Static timetables (TD, all routes) + real-time ETA (Sun Ferry, HKKF — 1-min, vessel GPS) | [transport-ferry.md](transport-ferry.md) |
| Visitor Arrivals | tourism | Monthly visitor arrivals by nationality/region (e.g., Chinese Mainland) | [tourism-arrivals.md](tourism-arrivals.md) |
| Hotel Room Occupancy Rate | tourism | Monthly hotel room occupancy rate (%) | [tourism-hotel-occupancy.md](tourism-hotel-occupancy.md) |

## By Category

### Transport
- [transport-kmb.md](transport-kmb.md) - KMB/LWB bus ETA
- [transport-mtr.md](transport-mtr.md) - MTR real-time train data
- [transport-digest.md](transport-digest.md) - Monthly traffic and transport digest
- [transport-port-cargo.md](transport-port-cargo.md) - Port cargo throughput (quarterly, JSON API)
- [transport-vessel-arrivals.md](transport-vessel-arrivals.md) - Real-time vessel arrivals/departures (XML)
- [transport-ferry.md](transport-ferry.md) - Ferry timetables (TD static) + real-time ETA (Sun Ferry, HKKF)

### Tourism
- [tourism-arrivals.md](tourism-arrivals.md) - Monthly visitor arrivals by nationality/region
- [tourism-hotel-occupancy.md](tourism-hotel-occupancy.md) - Monthly hotel room occupancy rate (%)

### Weather
- [weather-sunrise.md](weather-sunrise.md) - Sunrise/sunset times
- [weather-current.md](weather-current.md) - Current conditions & forecasts

### Location
- [location-address.md](location-address.md) - Address lookup service

### Health
- [health-births.md](health-births.md) - Birth statistics by sex and crude birth rate

### Employment
- [employment-unemployment.md](employment-unemployment.md) - Monthly unemployment rate by age and sex
- [employment-district-lf.md](employment-district-lf.md) - Annual labour force and LFPR by district (NOT unemployment rate)


### Education
- [education-schools.md](education-schools.md) - Number of schools by type/sector and region
- [education-primary-enrolment.md](education-primary-enrolment.md) - Primary school enrolment by district and grade
- [education-school-figures.md](education-school-figures.md) - EDB series: day schools, enrolment and operating classes by level/sector

### City Management and Utilities
- [city-holidays.md](city-holidays.md) - Hong Kong public holidays (2024-2026)
- [city-parking.md](city-parking.md) - Government car parks open for public use

### Housing
- [housing-prh.md](housing-prh.md) - Public Rental Housing income and asset limits
- [housing-estates.md](housing-estates.md) - PRH estate inventory with district locations

### Employment
- [employment-unemployment.md](employment-unemployment.md) - Monthly unemployment rate by age and sex
- [employment-district-lf.md](employment-district-lf.md) - Annual labour force and LFPR by district

### Environment
- [environment-river-water.md](environment-river-water.md) - Recent river water quality data
- [environment-air-quality.md](environment-air-quality.md) - Real-time AQHI + pollutant concentration at 18 stations

### Law and Security
- [security-crime.md](security-crime.md) - Crime statistics by offence type, age and sex (Censtatd)
- [security-crime-hkpf.md](security-crime-hkpf.md) - HKPF territory-wide overall and violent crime CSVs

### Recreation & Culture
- [recreation-badminton-outdoor.md](recreation-badminton-outdoor.md) - Free outdoor badminton court locations
- [recreation-badminton-sessions.md](recreation-badminton-sessions.md) - Badminton court session availability (real-time)
- [recreation-fitness-rooms.md](recreation-fitness-rooms.md) - LCSD fitness rooms locations + equipment (no real-time availability)
- [recreation-cinema.md](recreation-cinema.md) - Hong Kong cinema inventory
- [recreation-film-fund.md](recreation-film-fund.md) - Film Development Fund approved projects
- [recreation-film-boxoffice.md](recreation-film-boxoffice.md) - Box office for FDF-funded films

### Social Welfare
- [welfare-elderly-centres.md](welfare-elderly-centres.md) - SWD elderly centres inventory (NEC, DE/DCU, STE)
- [welfare-elderly-services.md](welfare-elderly-services.md) - Elderly service recipient statistics (Censtatd)

## Finding New Datasets

1. Use discovery workflow in [SKILL.md](../SKILL.md)
2. Search: `.venv/bin/python ./scripts/hkdata.py catalog-search "keyword"`
3. Inspect: `bash ./scripts/hkdata-info.sh "dataset-id"`

> **Maintenance note:** Keep the `Verified Datasets` table and the `By Category` section in sync. When adding a dataset, update **both**.

## Adding New Datasets

1. Copy [template.md](template.md)
2. Rename to `{category}-{dataset}.md`
3. Update this index (`Verified Datasets` table **and** `By Category` section)
4. Run `python3 ./scripts/hkdata.py reindex` to rebuild `search-index.json`
5. If fallback was used, record an experience (`experience-log`) and run `python3 ./scripts/hkdata.py log-render`
