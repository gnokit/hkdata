"""Transport Department — KMB/LWB bus real-time data (raw endpoints)."""


def kmb_routes() -> list:
    """All KMB/LWB bus routes with named termini (raw route list).

    Provides:
        - route, bound (O=outbound/I=inbound), service_type, origin and
          destination names (en/tc/sc)

    Coverage:
        - Geography: all KMB/LWB routes
        - Time:      real-time reference data

    Datasets:   hk-td-tis_21-etakmb
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/route/
    Format:     JSON

    Usage:
        >>> routes = kmb_routes()            # list[dict] (under ["data"])
        >>> [r for r in routes if "STAR FERRY" in (r.get("dest_en") or "")]

    Questions:
        - "which KMB routes go to Star Ferry?"
        - "list KMB routes"

    Quirks:
        - response wraps records under ["data"]
        - bound is O/I; the stop/eta endpoints use outbound/inbound instead
    """
    import json
    import urllib.request

    url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def kmb_stop(stop_id: str) -> dict:
    """One KMB stop's name (en/tc/sc) and coordinates.

    Provides:
        - stop name (en/tc/sc), latitude, longitude

    Coverage:
        - Geography: all KMB/LWB stops
        - Time:      real-time reference data

    Datasets:   hk-td-tis_21-etakmb
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}
    Format:     JSON

    Usage:
        >>> stop = kmb_stop("18492910339410B1")

    Questions:
        - "what is the name of stop [id]?"

    Quirks:
        - stop IDs are alphanumeric (e.g. "18492910339410B1")
    """
    import json
    import urllib.request

    url = f"https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def kmb_eta(stop_id: str, route: str, service_type: int = 1) -> list:
    """Live KMB/LWB bus arrival times at a stop for a route.

    Provides:
        - live ETAs (ISO-8601 +08:00), remark (e.g. "Scheduled Bus"), and the
          feed's data_timestamp

    Coverage:
        - Geography: one stop × one route
        - Time:      real-time, updated continuously

    Datasets:   hk-td-tis_21-etakmb
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/{route}/{service_type}
    Format:     JSON

    Usage:
        >>> etas = kmb_eta("18492910339410B1", "1")   # list of {eta, rmk_en, ...}

    Questions:
        - "when is the next KMB bus at stop X?"
        - "live bus arrival time"

    Quirks:
        - rmk_en "Scheduled Bus" = no live GPS; data_timestamp = feed generated
        - eta is ISO-8601 in +08:00 (HKT)
    """
    import json
    import urllib.request

    url = (f"https://data.etabus.gov.hk/v1/transport/kmb/eta/"
           f"{stop_id}/{route}/{int(service_type)}")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def kmb_route_finder(origin: str, destination: str,
                     origin_radius_m: float = 400,
                     dest_radius_m: float = 400,
                     top: int = 8,
                     with_eta: bool = True) -> dict:
    """Find KMB/LWB bus routes from place A to place B (stop join + optional ETA).

    Provides:
        - origin/destination resolution (stop-name match and/or ALS geocode
          + stops within radius)
        - candidates[]: route, bound, service_type, orig→dest labels,
          board_stop / alight_stop (id, name, seq, walk_m), etas[] when with_eta
        - count of routes checked

    Coverage:
        - Geography: KMB/LWB network only (not Citybus-only routes)
        - Time:      static stop/route-stop daily; ETA real-time (~1 min)

    Datasets:   hk-td-tis_21-etakmb; hk-dpo-als_01-als (geocode fallback)
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/stop
                https://data.etabus.gov.hk/v1/transport/kmb/route-stop
                https://data.etabus.gov.hk/v1/transport/kmb/route/
                https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop}/{route}/{service_type}
                https://www.als.gov.hk/lookup?q=
    Format:     JSON

    Usage:
        >>> r = kmb_route_finder("美孚", "旺角")
        >>> r["candidates"][0]["route"], r["candidates"][0]["board_stop"]["name_tc"]

    Questions:
        - "由美孚去旺角搭邊架巴士"
        - "which KMB bus from Mei Foo to Mong Kok"
        - "KMB route finder A to B"
        - "how to go to X by KMB from Y"

    Quirks:
        - no journey planner / no transfers — single-leg only
        - pasteable: inlines stop/route-stop/route/eta fetch (no import of
          other kmb_* programs/)
        - bound is O/I in lists; seq is a string — sort numerically
        - /route/ needs trailing slash
        - special service_type ≠ 1 may be short-working / peak-only
        - Citybus-only routes absent; jointly operated may appear
        - stop names carry code suffixes like (KC298); several IDs share a name
        - ALS used when stop-name substring yields no hits
    """
    import json
    import math
    import urllib.parse
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor, as_completed

    BASE = "https://data.etabus.gov.hk/v1/transport/kmb/"
    UA = {"User-Agent": "Mozilla/5.0"}

    def _get(url):
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _haversine(lat1, lng1, lat2, lng2):
        r = 6371008.8
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = p2 - p1, math.radians(lng2 - lng1)
        a = (math.sin(dp / 2) ** 2
             + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
        return 2 * r * math.asin(math.sqrt(a))

    def _als(q):
        url = ("https://www.als.gov.hk/lookup?q="
               + urllib.parse.quote(q) + "&n=1")
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0",
                          "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8-sig"))
        sugg = data.get("SuggestedAddress") or []
        if not sugg:
            return None
        geo = sugg[0]["Address"]["PremisesAddress"]["GeospatialInformation"]
        if isinstance(geo, list):
            geo = geo[0]
        return float(geo["Latitude"]), float(geo["Longitude"])

    def _resolve(place, stops_list, radius_m):
        q = (place or "").strip()
        by_name = []
        for s in stops_list:
            tc = s.get("name_tc") or ""
            en = s.get("name_en") or ""
            if q and (q in tc or q.lower() in en.lower()):
                by_name.append(s)
        method = "stop_name"
        chosen = by_name
        centre = None
        if not chosen:
            method = "als_radius"
            coords = _als(q)
            if coords is None:
                return {"query": q, "method": "failed", "stops": [],
                        "centre": None}
            centre = {"lat": coords[0], "lng": coords[1]}
            for s in stops_list:
                try:
                    slat, slng = float(s["lat"]), float(s["long"])
                except (TypeError, ValueError, KeyError):
                    continue
                d = _haversine(coords[0], coords[1], slat, slng)
                if d <= radius_m:
                    row = dict(s)
                    row["walk_m"] = round(d)
                    chosen.append(row)
            chosen.sort(key=lambda x: x.get("walk_m", 0))
        else:
            for s in chosen:
                s.setdefault("walk_m", 0)
        return {"query": q, "method": method, "stops": chosen,
                "centre": centre, "stop_ids": {s["stop"] for s in chosen}}

    # Fetch static lists in parallel
    with ThreadPoolExecutor(max_workers=3) as ex:
        f_stop = ex.submit(_get, BASE + "stop")
        f_rs = ex.submit(_get, BASE + "route-stop")
        f_rt = ex.submit(_get, BASE + "route/")
        stops_data = f_stop.result()["data"]
        route_stops = f_rs.result()["data"]
        routes = f_rt.result()["data"]

    stops_by_id = {s["stop"]: s for s in stops_data}
    orig = _resolve(origin, stops_data, origin_radius_m)
    dest = _resolve(destination, stops_data, dest_radius_m)
    if not orig["stop_ids"] or not dest["stop_ids"]:
        return {
            "origin": orig, "destination": dest,
            "candidates": [],
            "message": "could not resolve origin and/or destination to stops",
        }

    seqs = {}
    for r in route_stops:
        key = (r["route"], r["bound"], str(r["service_type"]))
        seqs.setdefault(key, []).append((int(r["seq"]), r["stop"]))

    route_meta = {}
    for r in routes:
        key = (r["route"], r["bound"], str(r["service_type"]))
        route_meta[key] = r

    candidates = []
    for key, lst in seqs.items():
        ids = [sid for _, sid in sorted(lst)]
        a_idx = [i for i, sid in enumerate(ids) if sid in orig["stop_ids"]]
        b_idx = [i for i, sid in enumerate(ids) if sid in dest["stop_ids"]]
        if not a_idx or not b_idx:
            continue
        board_i = min(a_idx)
        # alight must be after board
        later_b = [i for i in b_idx if i > board_i]
        if not later_b:
            continue
        alight_i = min(later_b)
        board_id = ids[board_i]
        alight_id = ids[alight_i]
        bs = stops_by_id.get(board_id, {})
        als = stops_by_id.get(alight_id, {})
        meta = route_meta.get(key, {})
        board_walk = next(
            (s.get("walk_m", 0) for s in orig["stops"] if s["stop"] == board_id),
            0)
        alight_walk = next(
            (s.get("walk_m", 0) for s in dest["stops"] if s["stop"] == alight_id),
            0)
        # prefer door stops (name match) via lower walk
        candidates.append({
            "route": key[0],
            "bound": key[1],
            "service_type": key[2],
            "orig_tc": meta.get("orig_tc"),
            "dest_tc": meta.get("dest_tc"),
            "orig_en": meta.get("orig_en"),
            "dest_en": meta.get("dest_en"),
            "board_stop": {
                "stop": board_id,
                "name_tc": bs.get("name_tc"),
                "name_en": bs.get("name_en"),
                "seq": board_i + 1,
                "walk_m": board_walk,
                "lat": bs.get("lat"), "long": bs.get("long"),
            },
            "alight_stop": {
                "stop": alight_id,
                "name_tc": als.get("name_tc"),
                "name_en": als.get("name_en"),
                "seq": alight_i + 1,
                "walk_m": alight_walk,
                "lat": als.get("lat"), "long": als.get("long"),
            },
            "stops_between": alight_i - board_i,
            "directness": board_walk + alight_walk,
        })

    candidates.sort(key=lambda c: (
        c["directness"], c["stops_between"], c["route"]))
    # de-dupe same route+bound keeping best
    seen = set()
    uniq = []
    for c in candidates:
        k = (c["route"], c["bound"], c["service_type"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    uniq = uniq[: int(top)]

    if with_eta and uniq:
        def _eta(c):
            url = (f"{BASE}eta/{c['board_stop']['stop']}/"
                   f"{c['route']}/{c['service_type']}")
            try:
                data = _get(url).get("data") or []
            except Exception as exc:
                return c["route"], {"error": str(exc), "etas": []}
            etas = [{"eta": e.get("eta"), "rmk_tc": e.get("rmk_tc"),
                     "rmk_en": e.get("rmk_en")} for e in data[:3]]
            return c["route"] + "|" + c["bound"] + "|" + c["service_type"], {
                "etas": etas}

        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(_eta, c): c for c in uniq}
            eta_map = {}
            for fut in as_completed(futs):
                key, payload = fut.result()
                eta_map[key] = payload
        for c in uniq:
            k = c["route"] + "|" + c["bound"] + "|" + c["service_type"]
            c["etas"] = (eta_map.get(k) or {}).get("etas", [])

    # slim origin/dest for JSON (drop full stop lists — keep counts + sample)
    def _slim_res(res):
        return {
            "query": res["query"],
            "method": res["method"],
            "centre": res.get("centre"),
            "stop_count": len(res.get("stops") or []),
            "sample_stops": [
                {"stop": s["stop"], "name_tc": s.get("name_tc"),
                 "walk_m": s.get("walk_m", 0)}
                for s in (res.get("stops") or [])[:5]
            ],
        }

    return {
        "origin": _slim_res(orig),
        "destination": _slim_res(dest),
        "candidates": uniq,
        "routes_scanned": len(seqs),
        "matches_before_dedupe": len(candidates),
    }


def kmb_route_stops_coords(route: str, bound: str = "O",
                           service_type: int = 1) -> dict:
    """Ordered stop list with coordinates for one KMB route/direction.

    Provides:
        - route meta (orig/dest names)
        - stops[] ordered by seq: stop id, name_tc/en, lat, long, seq
        - optional google/static-friendly polyline points

    Coverage:
        - Geography: one KMB/LWB route × bound × service_type
        - Time:      static reference (daily refresh)

    Datasets:   hk-td-tis_21-etakmb
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{outbound|inbound}/{service_type}
                https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}
                https://data.etabus.gov.hk/v1/transport/kmb/route/{route}/{outbound|inbound}/{service_type}
    Format:     JSON

    Usage:
        >>> r = kmb_route_stops_coords("6", "O", 1)
        >>> [(s["seq"], s["name_tc"]) for s in r["stops"][:3]]

    Questions:
        - "KMB route 6 stop list with coordinates"
        - "maplink stops for KMB route"
        - "巴士路線站點座標"

    Quirks:
        - bound O→outbound, I→inbound in path
        - service_type defaults to 1 (main service)
        - fetches each stop detail; large routes take a few seconds
    """
    import json
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor, as_completed

    BASE = "https://data.etabus.gov.hk/v1/transport/kmb/"
    direction = "outbound" if str(bound).upper() in ("O", "OUTBOUND") else "inbound"
    bound_code = "O" if direction == "outbound" else "I"
    st = int(service_type)

    def _get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    rs = _get(f"{BASE}route-stop/{route}/{direction}/{st}").get("data") or []
    rs = sorted(rs, key=lambda x: int(x["seq"]))
    meta = {}
    try:
        meta = _get(f"{BASE}route/{route}/{direction}/{st}").get("data") or {}
    except Exception:
        meta = {}

    stops = []
    def _one(row):
        sid = row["stop"]
        try:
            d = _get(f"{BASE}stop/{sid}").get("data") or {}
        except Exception:
            d = {}
        return {
            "seq": int(row["seq"]),
            "stop": sid,
            "name_tc": d.get("name_tc"),
            "name_en": d.get("name_en"),
            "lat": d.get("lat"),
            "long": d.get("long"),
        }

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(_one, row) for row in rs]
        for fut in as_completed(futs):
            stops.append(fut.result())
    stops.sort(key=lambda x: x["seq"])

    return {
        "route": route,
        "bound": bound_code,
        "direction": direction,
        "service_type": st,
        "orig_tc": meta.get("orig_tc"),
        "dest_tc": meta.get("dest_tc"),
        "orig_en": meta.get("orig_en"),
        "dest_en": meta.get("dest_en"),
        "stops": stops,
        "points": [{"lat": s["lat"], "lng": s["long"]} for s in stops
                   if s.get("lat") is not None],
    }
