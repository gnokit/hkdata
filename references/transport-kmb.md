# KMB/LWB Bus Real-time ETA

Real-time bus arrival data from Transport Department.

**Dataset ID:** `hk-td-tis_21-etakmb`
**Provider:** Transport Department (data from KMB/LWB)
**Category:** transport

## API

**Base:** `https://data.etabus.gov.hk/v1/transport/kmb/`

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /route/` | List all KMB routes |
| `GET /route/{route}` | Route details |
| `GET /route-stop/{route}/{direction}/{service_type}` | Stops for a route (direction: `outbound` or `inbound`) |
| `GET /stop/{stop_id}` | Stop details with coordinates |
| `GET /eta/{stop_id}/{route}/{service_type}` | ETA for specific stop/route |
| `GET /stop-eta/{stop_id}` | All ETAs for a stop |
| `GET /route-eta/{route}/{service_type}` | All ETAs for a route |

## Examples

```bash
# Get route 45 details
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route/45"

# Get outbound stops for route 45
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/45/outbound/1"

# Get stop details (Kowloon City Ferry)
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/stop/3241EDA71CCCF867"

# Get ETA for stop 3241EDA71CCCF867, route 45
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/eta/3241EDA71CCCF867/45/1"
```

**Added:** 2026-03-13
