"""Transport Department — parking finder (car parks + metered + non-metered near a place)."""


def parking_near(place: str = None, lat: float = None, lng: float = None,
                 radius_m: float = 800, top: int = 5,
                 include: str = "carpark,metered,nonmetered") -> dict:
    """Best live parking near a place: TD car parks + metered + non-metered.

    Provides:
        - centre (lat/lng, label, source ALS|coords|carpark, als_score)
        - results[] ranked by score: type, name, address, distance_m, vacant,
          fee, height_m, gmaps, score_parts
        - stale_carparks[] (lastupdate > 60 min, not ranked)
        - stats, warnings, ranking formula, sources

    Coverage:
        - Geography: HK-wide within radius_m of centre (straight-line)
        - Time:      real-time vacancy/occupancy; inventories change rarely

    Datasets:   hk-td-tis_5-real-time-parking-vacancy-data,
                hk-td-msd_1-metered-parking-spaces-data,
                hk-td-msd_2-non-metered-parking-spaces-data,
                hk-dpo-als_01-als (centre geocode)
    Department: Transport Department; ALS (OGCIO)
    Endpoint:   https://resource.data.one.gov.hk/td/carpark/basic_info_all.json
                https://resource.data.one.gov.hk/td/carpark/vacancy_all.json
                https://resource.data.one.gov.hk/td/psiparkingspaces/...
                https://data.nmospiot.gov.hk/api/pvds/Download/...
                https://www.als.gov.hk/lookup?q=
    Format:     JSON + CSV

    Usage:
        >>> r = parking_near("元州邨", radius_m=800, top=5)
        >>> r["results"][0]["name"], r["results"][0]["vacant"]
        >>> parking_near(lat=22.338, lng=114.155, top=3)

    Questions:
        - "附近邊度泊車最好"
        - "find parking near Un Chau Estate"
        - "元州邨附近停車場空位"
        - "best metered parking near [place]"

    Quirks:
        - self-contained: inlines ALS geocode + TD vacancy + street feeds
          (do NOT import other programs/)
        - score = 0.50*distance + 0.35*vacancy + 0.15*confidence
        - car parks with lastupdate > 60 min go to stale_carparks, not ranked
        - only vacancy_type A (actual count) and vacancy > 0
        - metered inventory: header on line 3; PoleId > 90000 = test
        - ALS always returns something — check centre.als_score (≤50 warn)
        - non-metered sensors sparse in urban core (~145 HK-wide)
        - public holidays not detected for metered operating periods
        - distances are straight-line metres
    """
    import csv
    import io
    import json
    import math
    import urllib.parse
    import urllib.request
    from datetime import datetime, timezone, timedelta

    HKT = timezone(timedelta(hours=8))
    W_DIST, W_VAC, W_CONF = 0.50, 0.35, 0.15
    VAC_SATURATION = 20
    STALE_MINUTES = 60
    STREET_CONF = {1: 0.5, 2: 0.75}
    TYPE_LABEL = {"carpark": "停車場", "metered": "咪錶", "nonmetered": "非咪錶"}
    OP_ALIASES = {"3A": "A", "3B": "B", "3D": "D", "3E": "E", "3F": "F",
                  "3G": "G", "3H": "H", "4J": "J", "7J": "J", "4N": "N",
                  "4P": "P", "4Q": "Q", "4S": "S", "5T": "T"}
    UA = "Mozilla/5.0"

    def _get(url: str, accept: str = None, timeout: int = 60) -> bytes:
        headers = {"User-Agent": UA}
        if accept:
            headers["Accept"] = accept
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()

    def _haversine(lat1, lng1, lat2, lng2):
        r = 6371008.8
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = p2 - p1, math.radians(lng2 - lng1)
        a = (math.sin(dp / 2) ** 2
             + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
        return 2 * r * math.asin(math.sqrt(a))

    def _gmaps(la, ln):
        return f"https://www.google.com/maps/search/?api=1&query={la:.6f},{ln:.6f}"

    def _parse_dt(value, fmts):
        value = (value or "").strip()
        for fmt in fmts:
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=HKT)
                return dt
            except ValueError:
                continue
        return None

    def _clean_fee(remark):
        if not remark:
            return ""
        text = remark.replace("\r", "").replace("<br>", " / ").replace("<BR>", " / ")
        lines = text.split("\n")
        if lines and (lines[0].startswith("高度限制")
                      or lines[0].lower().startswith("height limit")):
            lines = lines[1:]
        parts = [" ".join(p.split()).strip(" :：")
                 for p in " ".join(lines).split(" / ")]
        parts = [p for p in parts if p and p not in
                 ("高度限制", "Height Limit", "Height limit")]
        return " / ".join(parts)

    def _no_parking_now(code, now):
        base = OP_ALIASES.get((code or "").upper(), (code or "").upper())
        wd = now.weekday()
        if base == "P":
            return wd == 6
        if base == "S":
            return wd <= 4 and 8 <= now.hour < 17
        return False

    def _read_td_csv(raw):
        text = raw.decode("utf-8-sig", errors="replace")
        lines = text.splitlines()
        header_idx = 0
        for i, line in enumerate(lines[:5]):
            if "ParkingSpaceId" in line:
                header_idx = i
                break
        rows = list(csv.DictReader(io.StringIO("\n".join(lines[header_idx:]))))
        return rows

    def _als(q):
        url = ("https://www.als.gov.hk/lookup?q="
               + urllib.parse.quote(q) + "&n=1")
        data = json.loads(_get(url, accept="application/json").decode("utf-8-sig"))
        sugg = data.get("SuggestedAddress") or []
        if not sugg:
            return None
        s = sugg[0]
        prem = s["Address"]["PremisesAddress"]
        geo = prem.get("GeospatialInformation") or {}
        if isinstance(geo, list):
            geo = geo[0]
        chi = prem.get("ChiPremisesAddress") or {}
        st = chi.get("ChiStreet") or {}
        label = " ".join(x for x in [
            (chi.get("ChiDistrict") or {}).get("DcDistrict", ""),
            f"{st.get('StreetName', '')}{st.get('BuildingNoFrom', '')}"
            f"{'號' if st.get('BuildingNoFrom') else ''}",
            chi.get("BuildingName", "")
            or (chi.get("ChiEstate") or {}).get("EstateName", ""),
        ] if x)
        score = (s.get("ValidationInformation") or {}).get("Score")
        try:
            score = int(score) if score is not None else None
        except (TypeError, ValueError):
            pass
        return {"lat": float(geo["Latitude"]), "lng": float(geo["Longitude"]),
                "label": label or q, "source": "ALS",
                "als_score": score, "query": q}

    now = datetime.now(HKT)
    sources = [s.strip() for s in (include or "").split(",") if s.strip()]
    if not sources:
        sources = ["carpark", "metered", "nonmetered"]

    # Fetch carpark basic always (centre may resolve via carpark name)
    basic = json.loads(
        _get("https://resource.data.one.gov.hk/td/carpark/basic_info_all.json")
        .decode("utf-8-sig"))["car_park"]

    centre = None
    warnings = []
    if lat is not None and lng is not None:
        centre = {"lat": float(lat), "lng": float(lng),
                  "label": f"{lat},{lng}", "source": "coords",
                  "als_score": None, "query": None}
    elif place:
        ql = place.strip().lower()
        matched = None
        for c in basic:
            if c["park_id"].lower() == ql:
                matched = c
                break
        if not matched:
            for c in basic:
                if ql in ((c.get("name_tc") or "").lower(),
                          (c.get("name_en") or "").lower()):
                    matched = c
                    break
        if not matched:
            for field in ("name_tc", "name_en", "displayAddress_tc",
                          "displayAddress_en"):
                for c in basic:
                    if ql and ql in (c.get(field) or "").lower():
                        matched = c
                        break
                if matched:
                    break
        if matched:
            centre = {
                "lat": float(matched["latitude"]),
                "lng": float(matched["longitude"]),
                "label": matched.get("name_tc") or matched.get("name_en"),
                "source": "carpark", "als_score": None,
                "query": place, "park_id": matched["park_id"],
            }
        else:
            centre = _als(place)
            if centre is None:
                raise ValueError(f"could not geocode place: {place!r}")
            if (centre.get("als_score") or 0) <= 50:
                warnings.append(
                    f"ALS score {centre.get('als_score')} low — verify centre")
    else:
        raise ValueError("provide place= or lat=/lng=")

    clat, clng = centre["lat"], centre["lng"]
    radius = float(radius_m)
    top_n = int(top)

    results = []
    stale_carparks = []
    stats = {}

    if "carpark" in sources:
        vacancy = json.loads(
            _get("https://resource.data.one.gov.hk/td/carpark/vacancy_all.json")
            .decode("utf-8-sig"))["car_park"]
        vac_by_id = {p["park_id"]: p for p in vacancy}
        cp_stats = {"in_radius": 0, "no_data": 0, "full": 0,
                    "fresh": 0, "stale": 0}
        for c in basic:
            try:
                plat, plng = float(c["latitude"]), float(c["longitude"])
            except (TypeError, ValueError, KeyError):
                continue
            d = _haversine(clat, clng, plat, plng)
            if d > radius:
                continue
            v = vac_by_id.get(c["park_id"])
            if not v:
                continue
            entry = None
            for vt in v.get("vehicle_type", []):
                if vt.get("type") != "P":
                    continue
                for sc in vt.get("service_category", []):
                    if (sc.get("vacancy_type") == "A"
                            and sc.get("category", "HOURLY") == "HOURLY"):
                        entry = sc
            if entry is None:
                continue
            cp_stats["in_radius"] += 1
            vac = entry.get("vacancy")
            if vac is None or vac < 0:
                cp_stats["no_data"] += 1
                continue
            if vac == 0:
                cp_stats["full"] += 1
                continue
            upd = _parse_dt(entry.get("lastupdate", ""),
                            ["%Y-%m-%d %H:%M:%S", "%Y%m%dT%H:%M:%S%z"])
            age = ((now - upd).total_seconds() / 60) if upd else None
            height = c.get("height")
            try:
                height = (float(height)
                          if height not in (None, "", 0, "0") else None)
            except (TypeError, ValueError):
                height = None
            item = {
                "type": "carpark", "type_label": TYPE_LABEL["carpark"],
                "id": c["park_id"],
                "name": c.get("name_tc") or c.get("name_en"),
                "name_en": c.get("name_en"),
                "address": (c.get("displayAddress_tc")
                            or c.get("displayAddress_en")),
                "lat": plat, "lng": plng, "distance_m": round(d),
                "vacant": vac, "total": None,
                "updated": upd.isoformat() if upd else None,
                "age_min": round(age, 1) if age is not None else None,
                "height_m": height,
                "fee": _clean_fee(c.get("remark_tc", "")),
                "gmaps": _gmaps(plat, plng),
            }
            if age is None or age > STALE_MINUTES:
                item["stale"] = True
                stale_carparks.append(item)
                cp_stats["stale"] += 1
            else:
                item["stale"] = False
                results.append(item)
                cp_stats["fresh"] += 1
        stats["carpark"] = cp_stats

    def _street(kind, spaces_url, occ_url):
        spaces = _read_td_csv(_get(spaces_url))
        occ = _read_td_csv(_get(occ_url))
        occ_by_id = {o["ParkingSpaceId"].strip(): o for o in occ}
        groups = {}
        st_stats = {"spaces_in_radius": 0, "no_status": 0, "not_for_use": 0,
                    "no_parking_now": 0, "sections": 0}
        date_fmts = (["%m/%d/%Y %I:%M:%S %p"] if kind == "metered"
                     else ["%d/%m/%Y %H:%M:%S", "%-d/%-m/%Y %-H:%-M:%-S"])
        # also try without leading-zero variants via flexible parse
        date_fmts_extra = ["%m/%d/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S"]
        for s in spaces:
            if (s.get("VehicleType") or "").strip().upper() != "A":
                continue
            if kind == "metered":
                if "TEST" in (s.get("District") or "").upper():
                    continue
                try:
                    if int(float(s.get("PoleId") or 0)) > 90000:
                        continue
                except ValueError:
                    continue
            try:
                slat, slng = float(s["Latitude"]), float(s["Longitude"])
            except (TypeError, ValueError, KeyError):
                continue
            d = _haversine(clat, clng, slat, slng)
            if d > radius:
                continue
            st_stats["spaces_in_radius"] += 1
            sid = s["ParkingSpaceId"].strip()
            o = occ_by_id.get(sid)
            if not o:
                st_stats["no_status"] += 1
                continue
            if kind == "metered":
                if (o.get("ParkingMeterStatus") or "").strip().upper() != "N":
                    st_stats["not_for_use"] += 1
                    continue
                status = (o.get("OccupancyStatus") or "").strip().upper()
            else:
                status = (o.get("OccupancyStatus") or "").strip().upper()
                if status == "NU":
                    st_stats["not_for_use"] += 1
                    continue
            opcode = ((s.get("OperatingPeriod") or "").strip().upper()
                      if kind == "metered" else "")
            if kind == "metered" and _no_parking_now(opcode, now):
                st_stats["no_parking_now"] += 1
                continue
            key = (s.get("Street_tc") or s.get("Street") or "",
                   s.get("SectionOfStreet_tc") or s.get("SectionOfStreet") or "")
            g = groups.setdefault(key, {
                "spaces": 0, "vacant": 0, "nearest_vac": None,
                "district": s.get("District_tc", ""),
                "subdistrict": s.get("SubDistrict_tc", ""),
                "street_en": s.get("Street", ""),
                "section_en": s.get("SectionOfStreet", ""),
                "fees": {}, "vac_changed": [],
            })
            g["spaces"] += 1
            if kind == "metered":
                fee_key = (s.get("PaymentUnit", ""), s.get("TimeUnit", ""),
                           s.get("LPP", ""), opcode)
                g["fees"][fee_key] = g["fees"].get(fee_key, 0) + 1
            if status == "V":
                g["vacant"] += 1
                changed = None
                raw_ch = o.get("OccupancyDateChanged", "")
                for fmt in date_fmts_extra:
                    changed = _parse_dt(raw_ch, [fmt])
                    if changed:
                        break
                if not changed and kind == "nonmetered" and raw_ch:
                    # flexible D/M/YYYY H:M:S
                    try:
                        parts = raw_ch.replace("/", " ").replace(":", " ").split()
                        if len(parts) >= 6:
                            d0, m0, y0, h0, mi0, s0 = (
                                int(parts[0]), int(parts[1]), int(parts[2]),
                                int(parts[3]), int(parts[4]), int(parts[5]))
                            changed = datetime(
                                y0, m0, d0, h0, mi0, s0, tzinfo=HKT)
                    except (ValueError, IndexError):
                        changed = None
                if changed:
                    g["vac_changed"].append(changed)
                if g["nearest_vac"] is None or d < g["nearest_vac"][0]:
                    g["nearest_vac"] = (d, slat, slng, sid, changed)
        out = []
        st_stats["sections"] = len(groups)
        for (street, section), g in groups.items():
            if g["vacant"] <= 0 or g["nearest_vac"] is None:
                continue
            d, slat, slng, sid, changed = g["nearest_vac"]
            fee_txt = ""
            if g["fees"]:
                top_fee = sorted(g["fees"].items(), key=lambda kv: -kv[1])[0]
                (pay, unit, lpp, opc), _n = top_fee
                try:
                    pay_s = f"${float(pay):g}"
                except ValueError:
                    pay_s = f"${pay}"
                fee_txt = (f"{pay_s}/{unit}分鐘，最長{lpp}分鐘；時段{opc}")
            elif kind == "nonmetered":
                fee_txt = "非咪錶（免費路旁車位，以現場標誌為準）"
            if not section or section == street:
                name = street
            elif section.startswith(street):
                name = section
            else:
                name = f"{street}（{section}）"
            latest_vac = max(g["vac_changed"]) if g["vac_changed"] else None
            out.append({
                "type": kind, "type_label": TYPE_LABEL[kind],
                "id": sid, "name": name, "street": street, "section": section,
                "name_en": f"{g['street_en']} ({g['section_en']})",
                "address": " ".join(
                    x for x in [g["district"], g["subdistrict"], street] if x),
                "lat": slat, "lng": slng, "distance_m": round(d),
                "vacant": g["vacant"], "total": g["spaces"],
                "updated": latest_vac.isoformat() if latest_vac else None,
                "height_m": None, "fee": fee_txt,
                "gmaps": _gmaps(slat, slng), "stale": False,
            })
        return out, st_stats

    if "metered" in sources:
        mt, mt_stats = _street(
            "metered",
            "https://resource.data.one.gov.hk/td/psiparkingspaces/"
            "spaceinfo/parkingspaces.csv",
            "https://resource.data.one.gov.hk/td/psiparkingspaces/"
            "occupancystatus/occupancystatus.csv")
        results.extend(mt)
        stats["metered"] = mt_stats

    if "nonmetered" in sources:
        nm, nm_stats = _street(
            "nonmetered",
            "https://data.nmospiot.gov.hk/api/pvds/Download/parkingspace",
            "https://data.nmospiot.gov.hk/api/pvds/Download/occupancystatus")
        results.extend(nm)
        stats["nonmetered"] = nm_stats

    for item in results:
        dist = max(0.0, 1 - item["distance_m"] / radius)
        vac = min(1.0, math.log1p(item["vacant"]) / math.log1p(VAC_SATURATION))
        if item["type"] == "carpark":
            age = item.get("age_min") or 0.0
            conf = 1.0 - 0.5 * min(age, STALE_MINUTES) / STALE_MINUTES
        else:
            conf = STREET_CONF.get(item["vacant"], 1.0)
        total = W_DIST * dist + W_VAC * vac + W_CONF * conf
        item["score"] = round(total, 4)
        item["score_parts"] = {
            "distance": round(dist, 3),
            "vacancy": round(vac, 3),
            "confidence": round(conf, 3),
        }

    results.sort(key=lambda x: (-x["score"], x["distance_m"]))
    more = max(0, len(results) - top_n)
    top_results = results[:top_n]

    # strip non-JSON-friendly leftovers (none expected)
    def _strip(it):
        return {k: v for k, v in it.items() if k != "updated_dt"}

    return {
        "fetched_at_hkt": now.isoformat(),
        "centre": centre,
        "radius_m": radius,
        "top": top_n,
        "ranking": {
            "zh": (f"score = {W_DIST}×距離 + {W_VAC}×空位 + {W_CONF}×可信度；"
                   f"空位分 = ln(1+v)/ln(1+{VAC_SATURATION})；"
                   f"停車場 >{STALE_MINUTES} 分鐘未更新另列 stale"),
            "en": (f"score = {W_DIST}*distance + {W_VAC}*vacancy + "
                   f"{W_CONF}*confidence"),
            "weights": {"distance": W_DIST, "vacancy": W_VAC,
                        "confidence": W_CONF},
            "vacancy_saturation": VAC_SATURATION,
            "stale_minutes": STALE_MINUTES,
        },
        "results": [_strip(x) for x in top_results],
        "stale_carparks": [_strip(x) for x in stale_carparks[:top_n]],
        "more_candidates": more,
        "stats": stats,
        "warnings": warnings,
        "sources": sources,
    }
