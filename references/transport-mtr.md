# MTR Real-time Train Data (data.gov.hk)

## Dataset Info
- **URL:** https://data.gov.hk/en-data/dataset/mtr-data2-nexttrain-data
- **Provider:** MTR Corporation Limited
- **Category:** Transportation
- **Update Frequency:** Every 10 seconds

## Description
Provide the arrival time information for up to the next four trains of:
- Airport Express (機場快線)
- Tung Chung Line (東涌線)
- Tuen Ma Line (屯馬線)
- Tseung Kwan O Line (將軍澳線)
- East Rail Line (東鐵線)
- South Island Line (南島線)
- Tsuen Wan Line (荃灣線)
- Island Line (港島線)
- Kwun Tong Line (觀塘線)
- Disneyland Resort Line (迪士尼線)

## API Documentation
- **Data Dictionary:** https://opendata.mtr.com.hk/doc/Next_Train_DataDictionary_v1.7.pdf
- **API Specification:** https://opendata.mtr.com.hk/doc/Next_Train_API_Spec_v1.7.pdf

## Contact
- **Email:** opendata@mtr.com.hk
- **Phone:** 2993 2642 (Mon - Fri: 9:00am - 12:00noon, 2:00pm - 5:30pm)

## Usage Notes
- Real-time data, updates every 10 seconds
- Provides up to 4 next train arrival times per station
- Use the API spec to query by line and station

---

## Related MTR Datasets (from data.gov.hk)

| Dataset ID | Description |
|------------|-------------|
| `mtr-data2-nexttrain-data` | Real-time MTR train information (this page) |
| `mtr-data-routes-fares-barrier-free-facilities` | MTR Routes, Fares, Barrier Free Facilities |
| `mtr-lrnt_data-light-rail-nexttrain-data` | Light Rail Next Train Data |
| `mtr-mtr_bus-mtr-bus-eta-data` | MTR Bus ETA Data |

---

## Quick Search
```bash
hkdata-find.sh mtr
hkdata-find.sh light rail
hkdata-find.sh bus
```
