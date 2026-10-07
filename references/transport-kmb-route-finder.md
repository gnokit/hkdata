# KMB Route Finder (A → B)

Recipe for answering *"how do I get from **A** to **B** by KMB/LWB bus?"* using
the Transport Department's KMB real-time API. This is a **three-endpoint join**:
routes are matched by their named termini, the ordered stop list gives the
stop IDs, and the ETA endpoint gives live arrival times. Build it once here
instead of re-deriving the join every time.

**Provider:** Transport Department (data from KMB/LWB)
**Category:** transport
**Related dataset:** `hk-td-tis_21-etakmb` (see [transport-kmb.md](transport-kmb.md) for the raw endpoint table)

## Endpoints (base `https://data.etabus.gov.hk/v1/transport/kmb/`)

| Endpoint | Returns |
|----------|---------|
| `GET /route/` | All routes: `route`, `bound` (`O`/`I`), `service_type`, `orig_en/tc/sc`, `dest_en/tc/sc` |
| `GET /route-stop/{route}/{direction}/{service_type}` | Ordered stops `{seq, stop}` — **stop IDs only, no names** |
| `GET /stop/{stop_id}` | One stop's `name_en/tc/sc`, `lat`, `long` |
| `GET /eta/{stop_id}/{route}/{service_type}` | Live ETAs: `eta` (ISO8601 +08:00), `rmk_en` ("Scheduled Bus"), `data_timestamp` |

`direction` is `outbound` or `inbound`; `service_type` is `1` (normal).
`bound` in `/route/` uses `O`/`I` for the same thing.

## Join workflow

1. **Match routes** — `GET /route/`, filter where `orig_en`/`orig_tc` ≈ **A** and
   `dest_en`/`dest_tc` ≈ **B** (fuzzy-match the place name; termini are estate/
   pier names, not free-text stops). No free-text stop search exists — match on
   the named termini first.
2. **Get the ordered stops** — `GET /route-stop/{route}/{direction}/{service_type}`
   returns `seq` + `stop` (ID). To resolve names call `GET /stop/{id}` per stop
   (only the boarding/alighting stops you care about, not all 20–40).
3. **Confirm direction** — boarding stop's `seq` must be `<` alighting stop's `seq`.
   If not, use the other `direction`.
4. **Get ETA** — `GET /eta/{alighting_stop_id}/{route}/{service_type}` and read
   the first `eta` (and `rmk_en` to distinguish live vs scheduled).

## Example (A = Chuk Yuen Estate, B = Star Ferry)

```bash
BASE="https://data.etabus.gov.hk/v1/transport/kmb"

# 1. Route 1 runs Chuk Yuen Estate -> Star Ferry (orig_en/dest_en)
curl -s "$BASE/route/" | python3 -c '
import sys, json
d = json.load(sys.stdin)["data"]
for r in d:
    if r["orig_en"] == "CHUK YUEN ESTATE" and r["dest_en"] == "STAR FERRY":
        print(r["route"], r["bound"], r["service_type"])
'

# 2. Ordered stops for route 1 outbound
curl -s "$BASE/route-stop/1/outbound/1" | python3 -c '
import sys, json
for s in json.load(sys.stdin)["data"]:
    print(s["seq"], s["stop"])
'

# 3. Resolve a stop's name (boarding terminal, seq 1)
curl -s "$BASE/stop/18492910339410B1" | python3 -m json.tool

# 4. Live ETA at that stop for route 1
curl -s "$BASE/eta/18492910339410B1/1/1" | python3 -m json.tool
```

## Notes

- `/route-stop/` gives **stop IDs only**; names/coordinates come from `/stop/`.
  There is no name search, so discover stops by terminus-match + sequence, not by text.
- `eta` is an ISO-8601 timestamp in `+08:00` (HKT); `rmk_en: "Scheduled Bus"`
  means no live GPS, `data_timestamp` is when the feed was generated.
- Directions: `/route/` `bound` uses `O`/`I`, but the `/route-stop/` and `/eta/`
  paths take spelled-out `outbound`/`inbound` and `service_type=1`.
- LWB routes share the same API under the KMB base path.
- Chinese termini: `orig_tc`/`dest_tc` are Traditional, `orig_sc`/`dest_sc` Simplified.

---

**Date Added:** 2026-10-07
