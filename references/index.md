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
| Public Holidays | city | Hong Kong public holidays 2024-2026 (official 1823 data) | [city-holidays.md](city-holidays.md) |
| PRH Income & Asset Limits | housing | Monthly income/asset limits for public rental housing application | [housing-prh.md](housing-prh.md) |
| River Water Quality | environment | Recent DO and BOD5 data at downstream river monitoring stations | [environment-river-water.md](environment-river-water.md) |
| Monthly Transport Digest | transport | Monthly CSV stats: passenger journeys, accidents, tunnel flows, licences | [transport-digest.md](transport-digest.md) |
| Government Car Parks | city | Government car parks open for public use: locations, spaces, fees | [city-parking.md](city-parking.md) |
| Crime Statistics | security | Persons arrested for crime by offence type, age group and sex | [security-crime.md](security-crime.md) |
| Cinemas | recreation | HK cinema inventory: locations, screens, seats, coordinates | [recreation-cinema.md](recreation-cinema.md) |
| Film Development Fund | recreation | Approved FDF film projects since 2009: titles, funding, dates | [recreation-film-fund.md](recreation-film-fund.md) |
| Film Box Office (FDF) | recreation | HK box office revenue for FDF-funded films | [recreation-film-boxoffice.md](recreation-film-boxoffice.md) |

## By Category

### Transport
- [transport-kmb.md](transport-kmb.md) - KMB/LWB bus ETA
- [transport-mtr.md](transport-mtr.md) - MTR real-time train data
- [transport-digest.md](transport-digest.md) - Monthly traffic and transport digest

### Weather
- [weather-sunrise.md](weather-sunrise.md) - Sunrise/sunset times
- [weather-current.md](weather-current.md) - Current conditions & forecasts

### Location
- [location-address.md](location-address.md) - Address lookup service

### Health
- [health-births.md](health-births.md) - Birth statistics by sex and crude birth rate

### Employment
- [employment-unemployment.md](employment-unemployment.md) - Monthly unemployment rate by age and sex



### Education
- [education-schools.md](education-schools.md) - Number of schools by type/sector and region

### City Management and Utilities
- [city-holidays.md](city-holidays.md) - Hong Kong public holidays (2024-2026)
- [city-parking.md](city-parking.md) - Government car parks open for public use

### Housing
- [housing-prh.md](housing-prh.md) - Public Rental Housing income and asset limits

### Environment
- [environment-river-water.md](environment-river-water.md) - Recent river water quality data

### Law and Security
- [security-crime.md](security-crime.md) - Crime statistics by offence type, age and sex

### Recreation & Culture
- [recreation-badminton-outdoor.md](recreation-badminton-outdoor.md) - Free outdoor badminton court locations
- [recreation-badminton-sessions.md](recreation-badminton-sessions.md) - Badminton court session availability (real-time)
- [recreation-cinema.md](recreation-cinema.md) - Hong Kong cinema inventory
- [recreation-film-fund.md](recreation-film-fund.md) - Film Development Fund approved projects
- [recreation-film-boxoffice.md](recreation-film-boxoffice.md) - Box office for FDF-funded films

## Finding New Datasets

1. Use discovery workflow in [SKILL.md](../SKILL.md)
2. Search: `bash ./bin/hkdata-find.sh "keyword"`
3. Inspect: `bash ./bin/hkdata-info.sh "dataset-id"`

## Adding New Datasets

1. Copy [template.md](template.md)
2. Rename to `{category}-{dataset}.md`
3. Update this index
4. Update SKILL.md category table
