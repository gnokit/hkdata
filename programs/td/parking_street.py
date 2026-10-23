"""Transport Department — on-street metered and non-metered parking spaces."""


def metered_parking_spaces(include_occupancy: bool = True,
                           vehicle_type: str = "A") -> list:
    """On-street metered parking spaces with optional live occupancy.

    Provides:
        - inventory: ParkingSpaceId, street (en/tc), section, lat/lng,
          VehicleType, LPP (max stay min), OperatingPeriod, TimeUnit,
          PaymentUnit (fee)
        - when include_occupancy: ParkingMeterStatus (N/NU), OccupancyStatus
          (V vacant / O occupied), OccupancyDateChanged

    Coverage:
        - Geography: HK-wide sensor-equipped metered spaces
        - Time:      occupancy refresh every few minutes; inventory rare

    Datasets:   hk-td-msd_1-metered-parking-spaces-data
    Department: Transport Department
    Endpoint:   https://resource.data.one.gov.hk/td/psiparkingspaces/spaceinfo/parkingspaces.csv
                https://resource.data.one.gov.hk/td/psiparkingspaces/occupancystatus/occupancystatus.csv
    Format:     CSV

    Usage:
        >>> spaces = metered_parking_spaces()
        >>> vacant = [s for s in spaces if s.get("OccupancyStatus") == "V"][:5]

    Questions:
        - "有冇街邊咪錶位空"
        - "metered parking vacancy near Island Road"
        - "on-street parking meter occupancy"

    Quirks:
        - inventory CSV: line 1 = file date, line 2 blank/commas, header on line 3
        - ParkingMeterStatus NU = not for use (excluded); PoleId > 90000 = TD test
        - VehicleType A = private cars (normalise case); G goods; C coaches
        - OccupancyDateChanged is MM/DD/YYYY hh:mm:ss AM/PM (when status changed)
        - OperatingPeriod letter codes (A/B/D/…) — see TD dataspec PDF table
        - send User-Agent; vacancy changes in minutes
    """
    import csv
    import io
    import urllib.request

    def _get(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8-sig")

    inv_url = ("https://resource.data.one.gov.hk/td/psiparkingspaces/"
               "spaceinfo/parkingspaces.csv")
    lines = _get(inv_url).splitlines()
    # skip file-date + blank row; header is line 3 (index 2)
    body = "\n".join(lines[2:])
    rows = list(csv.DictReader(io.StringIO(body)))

    vt = (vehicle_type or "").strip().upper()
    out = []
    for r in rows:
        try:
            pole = int(float(r.get("PoleId") or 0))
        except ValueError:
            pole = 0
        if pole > 90000:
            continue
        if (r.get("District") or "").upper() == "INTERNAL TEST":
            continue
        if vt and (r.get("VehicleType") or "").strip().upper() != vt:
            continue
        out.append(r)

    if not include_occupancy:
        return out

    occ_url = ("https://resource.data.one.gov.hk/td/psiparkingspaces/"
               "occupancystatus/occupancystatus.csv")
    occ = {o["ParkingSpaceId"]: o
           for o in csv.DictReader(io.StringIO(_get(occ_url)))}
    joined = []
    for r in out:
        o = occ.get(r.get("ParkingSpaceId") or "")
        if not o:
            continue
        if (o.get("ParkingMeterStatus") or "").upper() == "NU":
            continue
        row = dict(r)
        row["ParkingMeterStatus"] = o.get("ParkingMeterStatus")
        row["OccupancyStatus"] = o.get("OccupancyStatus")
        row["OccupancyDateChanged"] = o.get("OccupancyDateChanged")
        joined.append(row)
    return joined


def non_metered_parking_spaces(include_occupancy: bool = True,
                               vehicle_type: str = "A") -> list:
    """Sensor-equipped non-metered on-street parking spaces + occupancy.

    Provides:
        - inventory: ParkingSpaceId, region/district/street (en/tc), lat/lng,
          VehicleType
        - when include_occupancy: OccupancyStatus (V/O/NU), OccupancyDateChanged

    Coverage:
        - Geography: ~145 spaces, mostly country-park roads in North / Tai Po /
          Sha Tin / Yuen Long / Sai Kung (urban core often empty)
        - Time:      occupancy refresh every few minutes

    Datasets:   hk-td-msd_2-non-metered-parking-spaces-data
    Department: Transport Department
    Endpoint:   https://data.nmospiot.gov.hk/api/pvds/Download/parkingspace
                https://data.nmospiot.gov.hk/api/pvds/Download/occupancystatus
    Format:     CSV

    Usage:
        >>> spaces = non_metered_parking_spaces()
        >>> vacant = [s for s in spaces if s.get("OccupancyStatus") == "V"]

    Questions:
        - "非咪錶路旁車位"
        - "non-metered on-street parking sensors"
        - "新娘潭路泊車位有冇空"

    Quirks:
        - inventory: line 1 file date (YYYY-MM-DD or DD-MM-YYYY), line 2 blank,
          header line 3
        - OccupancyStatus NU = not for use (excluded); VehicleType D = disabled
        - OccupancyDateChanged is D/M/YYYY H:M:S 24h without zero-padding
        - sparse urban coverage — expect few/no hits downtown
    """
    import csv
    import io
    import urllib.request

    def _get(url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8-sig")

    inv_url = "https://data.nmospiot.gov.hk/api/pvds/Download/parkingspace"
    lines = _get(inv_url).splitlines()
    body = "\n".join(lines[2:])
    rows = list(csv.DictReader(io.StringIO(body)))

    vt = (vehicle_type or "").strip().upper()
    out = []
    for r in rows:
        rvt = (r.get("VehicleType") or "").strip().upper()
        if vt and rvt != vt:
            continue
        if rvt == "D":
            continue
        out.append(r)

    if not include_occupancy:
        return out

    occ_url = "https://data.nmospiot.gov.hk/api/pvds/Download/occupancystatus"
    occ = {o["ParkingSpaceId"]: o
           for o in csv.DictReader(io.StringIO(_get(occ_url)))}
    joined = []
    for r in out:
        o = occ.get(r.get("ParkingSpaceId") or "")
        if not o:
            continue
        status = (o.get("OccupancyStatus") or "").upper()
        if status == "NU":
            continue
        row = dict(r)
        row["OccupancyStatus"] = o.get("OccupancyStatus")
        row["OccupancyDateChanged"] = o.get("OccupancyDateChanged")
        joined.append(row)
    return joined
