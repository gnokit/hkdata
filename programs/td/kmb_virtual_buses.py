"""Transport Department — KMB/LWB virtual bus positions from route-eta (no GPS)."""


def kmb_virtual_buses(route: str, service_type: int = 1) -> dict:
    """Estimate how many KMB/LWB buses are on a route and where, from public ETA only.

    Positions are **virtual** (inferred from route-eta). This is NOT GPS tracking.
    ETA row count is not vehicle count — rows are matched into trips across stops.

    Provides:
        - directions O/I: stop list (seq, id, names, lat/lng), τ̂ segment times,
          matched virtual trips with placement / progress / lat/lng
        - per trip: stop_chain (matched ETAs), first/next stop seq, segment_index,
          remaining_s_to_next, tau_s_current
        - summary counts: n_trips_total / O / I, n_eta_rows_total
        - estimate_time, data_timestamp, generated_timestamp (Asia/Hong_Kong)

    Coverage:
        - Geography: one KMB/LWB route, both bounds when route-stop exists
        - Time:      real-time snapshot from route-eta (~1 min refresh)

    Datasets:   hk-td-tis_21-etakmb
    Department: Transport Department (data from KMB/LWB)
    Endpoint:   https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route}/{service_type}
                https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{outbound|inbound}/{service_type}
                https://data.etabus.gov.hk/v1/transport/kmb/stop/{stop_id}
    Format:     JSON

    Usage:
        >>> r = kmb_virtual_buses("B1")
        >>> r["summary"]["n_trips_total"], r["directions"]["O"]["n_trips"]
        >>> r["directions"]["O"]["trips"][0]["lat"], r["directions"]["O"]["trips"][0]["placement"]

    Questions:
        - "estimate how many KMB buses on route from ETA"
        - "virtual buses on KMB route B1"
        - "how many buses are running on route B1 right now"
        - "estimate bus positions from ETA (no GPS)"
        - "用 ETA 估算路線上有幾多架巴士"
        - "虛擬巴士位置 / 路線上巴士分佈"
        - "從到站時間推算巴士位置"

    Quirks:
        - estimated from route-eta only — NOT GPS; lat/lng are straight-line
          interpolations between stop coords (not road-snapped)
        - eta row count ≠ vehicle count (up to 3 eta_seq per stop; matched into trips)
        - τ̂ from Scheduled Bus same-eta_seq chains when complete, else median
          downstream−upstream pairs, else 150s/segment fallback
        - bound O=outbound / I=inbound; service_type defaults to 1
        - pasteable: inlines fetch + match (no import of other kmb_* programs/)
    """
    import json
    import statistics
    import time
    import urllib.error
    import urllib.request
    from collections import defaultdict
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from datetime import datetime, timedelta, timezone
    from typing import Any, Dict, List, Optional, Tuple

    HKT = timezone(timedelta(hours=8), name="Asia/Hong_Kong")
    BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
    FALLBACK_TAU_S = 150.0
    LOOSE_WINDOW_S = 45 * 60
    MATCH_MAX_ABS_ERR_S = 20 * 60
    SCHEDULED_RMK = "Scheduled Bus"
    DIR_TO_BOUND = {"O": "outbound", "I": "inbound"}
    UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    st = int(service_type)
    route = str(route).strip().upper()

    def _get(url: str, retries: int = 3) -> dict:
        last_err: Optional[Exception] = None
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = e
                time.sleep(0.4 * (attempt + 1))
            except Exception as e:
                last_err = e
                time.sleep(0.4 * (attempt + 1))
        raise RuntimeError(f"Failed to fetch {url}: {last_err}")

    def parse_eta(ts: Optional[str]) -> Optional[datetime]:
        if not ts:
            return None
        s = ts.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=HKT)
        return dt.astimezone(HKT)

    def to_hkt_iso(dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        return dt.astimezone(HKT).isoformat()

    def fetch_route_stops(direction: str) -> List[dict]:
        bound = DIR_TO_BOUND[direction]
        payload = _get(f"{BASE}/route-stop/{route}/{bound}/{st}")
        rows = sorted(payload.get("data") or [], key=lambda r: int(r["seq"]))

        def _one(r):
            sid = r["stop"]
            seq = int(r["seq"])
            try:
                sd = (_get(f"{BASE}/stop/{sid}").get("data") or {})
            except Exception:
                sd = {}
            return {
                "stop_id": sid,
                "seq": seq,
                "name_en": sd.get("name_en") or sid,
                "name_tc": sd.get("name_tc") or "",
                "lat": float(sd["lat"]) if sd.get("lat") is not None else 0.0,
                "lng": float(sd["long"]) if sd.get("long") is not None else 0.0,
            }

        stops: List[dict] = []
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = [ex.submit(_one, r) for r in rows]
            for fut in as_completed(futs):
                stops.append(fut.result())
        stops.sort(key=lambda s: s["seq"])
        return stops

    def fetch_route_etas() -> Tuple[List[dict], Optional[datetime], Optional[datetime]]:
        payload = _get(f"{BASE}/route-eta/{route}/{st}")
        data = payload.get("data") or []
        gen = parse_eta(payload.get("generated_timestamp"))
        dts = [parse_eta(r.get("data_timestamp")) for r in data]
        dts = [d for d in dts if d]
        data_ts = max(dts) if dts else gen
        return data, gen, data_ts

    def _scheduled_chain_taus(
        stops: List[dict], etas_by_seq: Dict[int, List[dict]]
    ) -> Optional[Tuple[List[float], str]]:
        n = len(stops)
        if n < 2:
            return None
        per_seg: List[List[float]] = [[] for _ in range(n - 1)]
        for es in (1, 2, 3):
            sched: Dict[int, datetime] = {}
            for stinfo in stops:
                for row in etas_by_seq.get(stinfo["seq"], []):
                    if row["eta_seq"] == es and row["rmk_en"] == SCHEDULED_RMK:
                        sched[stinfo["seq"]] = row["eta"]
                        break
            for i in range(n - 1):
                a, b = stops[i]["seq"], stops[i + 1]["seq"]
                if a in sched and b in sched:
                    dt = (sched[b] - sched[a]).total_seconds()
                    if 0 < dt < LOOSE_WINDOW_S:
                        per_seg[i].append(dt)
        if any(len(xs) == 0 for xs in per_seg):
            return None
        taus: List[float] = []
        for xs in per_seg:
            med = statistics.median(xs)
            if len(xs) >= 2:
                if max(abs(x - med) for x in xs) > max(3 * med, 600):
                    return None
            taus.append(float(med))
        return taus, "scheduled_same_eta_seq_chain"

    def _median_pair_taus(
        stops: List[dict], etas_by_seq: Dict[int, List[dict]]
    ) -> Optional[Tuple[List[float], str]]:
        n = len(stops)
        if n < 2:
            return None
        taus: List[float] = []
        covered = 0
        for i in range(n - 1):
            up = etas_by_seq.get(stops[i]["seq"], [])
            dn = etas_by_seq.get(stops[i + 1]["seq"], [])
            diffs: List[float] = []
            for a in up:
                for b in dn:
                    dt = (b["eta"] - a["eta"]).total_seconds()
                    if 0 < dt < LOOSE_WINDOW_S:
                        diffs.append(dt)
            if diffs:
                taus.append(float(statistics.median(diffs)))
                covered += 1
            else:
                taus.append(FALLBACK_TAU_S)
        method = "median_downstream_minus_upstream"
        if covered == 0:
            return None
        if covered < n - 1:
            method = "median_pair_with_fallback_constant"
        return taus, method

    def estimate_taus(
        stops: List[dict], etas_by_seq: Dict[int, List[dict]]
    ) -> Tuple[List[float], str, List[str]]:
        notes: List[str] = []
        n = len(stops)
        if n < 2:
            return [], "n/a_single_or_empty", ["fewer than 2 stops"]
        sched = _scheduled_chain_taus(stops, etas_by_seq)
        if sched:
            taus, method = sched
            notes.append(
                "τ̂ from Scheduled Bus same-eta_seq differences across consecutive stops; "
                "median per segment when multiple eta_seq chains exist."
            )
            return taus, method, notes
        notes.append(
            "Scheduled same-eta_seq chain incomplete or inconsistent; trying median pairs."
        )
        med = _median_pair_taus(stops, etas_by_seq)
        if med:
            taus, method = med
            notes.append(
                "τ̂ = median(downstream_eta − upstream_eta) over pairs with 0 < dt < 45 min "
                f"(fallback {FALLBACK_TAU_S:.0f}s where no pairs)."
            )
            return taus, method, notes
        notes.append(
            f"No usable ETA pairs; fallback constant {FALLBACK_TAU_S:.0f}s per segment."
        )
        return [FALLBACK_TAU_S] * (n - 1), "fallback_constant", notes

    def build_eta_rows(raw: List[dict], direction: str) -> Dict[int, List[dict]]:
        by_seq: Dict[int, List[dict]] = defaultdict(list)
        for r in raw:
            if r.get("dir") != direction:
                continue
            eta = parse_eta(r.get("eta"))
            if eta is None:
                continue
            seq = int(r["seq"])
            es = int(r["eta_seq"])
            uid = f"{direction}:{seq}:{es}:{to_hkt_iso(eta)}"
            by_seq[seq].append(
                {
                    "stop_seq": seq,
                    "eta_seq": es,
                    "eta": eta,
                    "rmk_en": (r.get("rmk_en") or "").strip(),
                    "data_timestamp": parse_eta(r.get("data_timestamp")),
                    "dest_en": r.get("dest_en") or "",
                    "uid": uid,
                    "used": False,
                }
            )
        for seq in by_seq:
            by_seq[seq].sort(key=lambda e: (e["eta"], e["eta_seq"]))
        return by_seq

    def match_trips(
        stops: List[dict],
        etas_by_seq: Dict[int, List[dict]],
        taus: List[float],
        direction: str,
    ) -> List[List[dict]]:
        n = len(stops)
        seqs = [s["seq"] for s in stops]
        trips: List[List[dict]] = []
        last_arrival: Dict[int, datetime] = {}

        def best_next(prev: dict, next_stop_seq: int, tau: float) -> Optional[dict]:
            cands = [e for e in etas_by_seq.get(next_stop_seq, []) if not e["used"]]
            if not cands:
                return None
            scored: List[Tuple[float, float, dict]] = []
            for c in cands:
                dt = (c["eta"] - prev["eta"]).total_seconds()
                if not (0 < dt < LOOSE_WINDOW_S):
                    continue
                err = abs(dt - tau)
                if err > MATCH_MAX_ABS_ERR_S:
                    continue
                overtake_pen = 0.0
                la = last_arrival.get(next_stop_seq)
                if la is not None and c["eta"] < la:
                    overtake_pen = (la - c["eta"]).total_seconds() * 0.25
                scored.append((err + overtake_pen, err, c))
            if not scored:
                return None
            scored.sort(key=lambda t: (t[0], t[1], t[2]["eta"]))
            best = scored[0][2]
            best_dt = (best["eta"] - prev["eta"]).total_seconds()
            if abs(best_dt - tau) > MATCH_MAX_ABS_ERR_S:
                return None
            return best

        seed_list: List[dict] = []
        for stinfo in stops:
            seed_list.extend(etas_by_seq.get(stinfo["seq"], []))
        seed_list.sort(key=lambda e: (e["stop_seq"], e["eta"], e["eta_seq"]))

        for seed in seed_list:
            if seed["used"]:
                continue
            chain = [seed]
            seed["used"] = True
            try:
                si = seqs.index(seed["stop_seq"])
            except ValueError:
                continue
            cur = seed
            for i in range(si, n - 1):
                nxt_seq = seqs[i + 1]
                tau = taus[i] if i < len(taus) else FALLBACK_TAU_S
                nxt = best_next(cur, nxt_seq, tau)
                if nxt is None:
                    break
                nxt["used"] = True
                chain.append(nxt)
                cur = nxt
            trips.append(chain)
            for row in chain:
                prev = last_arrival.get(row["stop_seq"])
                if prev is None or row["eta"] > prev:
                    last_arrival[row["stop_seq"]] = row["eta"]

        trips.sort(key=lambda ch: (ch[0]["eta"], ch[0]["stop_seq"]))
        return trips

    def lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def place_trip(
        chain: List[dict],
        stops: List[dict],
        taus: List[float],
        now: datetime,
        trip_id: str,
        direction: str,
    ) -> dict:
        seq_to_stop = {s["seq"]: s for s in stops}
        seqs = [s["seq"] for s in stops]
        matched = [
            {
                "stop_seq": e["stop_seq"],
                "eta_seq": e["eta_seq"],
                "eta": e["eta"],
                "rmk_en": e["rmk_en"],
            }
            for e in chain
        ]
        first_seq = chain[0]["stop_seq"]

        upcoming: Optional[dict] = None
        for e in chain:
            if e["eta"] >= now:
                upcoming = e
                break

        def _pack(
            placement, seg, progress, lat, lng, rem, tau_cur, next_seq, matched_etas
        ):
            return {
                "trip_id": trip_id,
                "direction": direction,
                "etas": matched_etas,
                "first_stop_seq": first_seq,
                "next_stop_seq": next_seq,
                "segment_index": seg,
                "placement": placement,
                "progress": progress,
                "lat": lat,
                "lng": lng,
                "remaining_s_to_next": rem,
                "tau_s_current": tau_cur,
            }

        if upcoming is None:
            last = chain[-1]
            stinfo = seq_to_stop[last["stop_seq"]]
            try:
                li = seqs.index(last["stop_seq"])
            except ValueError:
                li = len(seqs) - 1
            if li >= len(seqs) - 1:
                return _pack(
                    "after_last", None, 1.0, stinfo["lat"], stinfo["lng"],
                    None, None, None, matched,
                )
            placement = "on_segment"
            seg = li
            progress = 0.95
            st2 = seq_to_stop[seqs[li + 1]]
            lat = lerp(stinfo["lat"], st2["lat"], progress)
            lng = lerp(stinfo["lng"], st2["lng"], progress)
            tau_cur = taus[li] if li < len(taus) else FALLBACK_TAU_S
            return _pack(
                placement, seg, progress, lat, lng, None, tau_cur, seqs[li + 1], matched
            )

        ui = seqs.index(upcoming["stop_seq"])
        rem = (upcoming["eta"] - now).total_seconds()
        if rem < 0:
            rem = 0.0

        if ui == 0:
            stinfo = stops[0]
            tau0 = taus[0] if taus else FALLBACK_TAU_S
            if rem > tau0:
                progress = 0.0
            else:
                progress = max(0.0, min(1.0, 1.0 - rem / max(tau0, 1.0)))
            return _pack(
                "before_first", None, round(progress, 4),
                stinfo["lat"], stinfo["lng"],
                round(rem, 1), tau0, upcoming["stop_seq"], matched,
            )

        seg = ui - 1
        tau = taus[seg] if seg < len(taus) else FALLBACK_TAU_S
        if tau <= 0:
            progress = 1.0
        else:
            progress = 1.0 - (rem / tau)
        progress = max(0.0, min(1.0, progress))
        placement = "at_stop" if rem <= 15 else "on_segment"
        st_a = stops[seg]
        st_b = stops[seg + 1]
        lat = lerp(st_a["lat"], st_b["lat"], progress)
        lng = lerp(st_a["lng"], st_b["lng"], progress)
        return _pack(
            placement, seg, round(progress, 4),
            round(lat, 6), round(lng, 6),
            round(rem, 1), round(tau, 1), upcoming["stop_seq"], matched,
        )

    # --- orchestrate ---
    raw, gen_ts, data_ts = fetch_route_etas()
    now = data_ts or gen_ts or datetime.now(HKT)
    now = now.astimezone(HKT)

    result: Dict[str, Any] = {
        "route": route,
        "service_type": st,
        "generated_timestamp": to_hkt_iso(gen_ts),
        "data_timestamp": to_hkt_iso(data_ts) or to_hkt_iso(now),
        "estimate_time": to_hkt_iso(now),
        "timezone": "Asia/Hong_Kong",
        "caveat": "Estimated from route-eta only; not GPS; not road-snapped.",
        "directions": {},
    }

    for direction in ("O", "I"):
        try:
            stops = fetch_route_stops(direction)
        except Exception as e:
            result["directions"][direction] = {
                "bound": DIR_TO_BOUND[direction],
                "error": str(e),
                "n_stops": 0,
                "stops": [],
                "tau_hat_s": [],
                "tau_method": "error",
                "tau_notes": [str(e)],
                "n_eta_rows": 0,
                "n_trips": 0,
                "trips": [],
            }
            continue

        etas_by_seq = build_eta_rows(raw, direction)
        taus, tau_method, tau_notes = estimate_taus(stops, etas_by_seq)
        chains = match_trips(stops, etas_by_seq, taus, direction)

        trips_out: List[dict] = []
        for idx, chain in enumerate(chains, start=1):
            tid = f"{route}-{direction}-{idx:02d}"
            vt = place_trip(chain, stops, taus, now, tid, direction)
            trips_out.append(
                {
                    "trip_id": vt["trip_id"],
                    "direction": vt["direction"],
                    "bound": DIR_TO_BOUND[vt["direction"]],
                    "stop_chain": [
                        {
                            "stop_seq": m["stop_seq"],
                            "stop_id": next(
                                s["stop_id"] for s in stops if s["seq"] == m["stop_seq"]
                            ),
                            "stop_name_en": next(
                                s["name_en"] for s in stops if s["seq"] == m["stop_seq"]
                            ),
                            "eta_seq": m["eta_seq"],
                            "eta": to_hkt_iso(m["eta"]),
                            "rmk_en": m["rmk_en"],
                        }
                        for m in vt["etas"]
                    ],
                    "first_stop_seq": vt["first_stop_seq"],
                    "next_stop_seq": vt["next_stop_seq"],
                    "segment_index": vt["segment_index"],
                    "placement": vt["placement"],
                    "progress": vt["progress"],
                    "lat": vt["lat"],
                    "lng": vt["lng"],
                    "remaining_s_to_next": vt["remaining_s_to_next"],
                    "tau_s_current": vt["tau_s_current"],
                }
            )

        result["directions"][direction] = {
            "bound": DIR_TO_BOUND[direction],
            "n_stops": len(stops),
            "stops": [
                {
                    "seq": s["seq"],
                    "stop_id": s["stop_id"],
                    "name_en": s["name_en"],
                    "name_tc": s["name_tc"],
                    "lat": s["lat"],
                    "lng": s["lng"],
                }
                for s in stops
            ],
            "tau_hat_s": [round(t, 1) for t in taus],
            "tau_method": tau_method,
            "tau_notes": tau_notes,
            "n_eta_rows": sum(len(v) for v in etas_by_seq.values()),
            "n_trips": len(trips_out),
            "trips": trips_out,
        }

    o = result["directions"].get("O") or {}
    i = result["directions"].get("I") or {}
    result["summary"] = {
        "n_trips_total": int(o.get("n_trips") or 0) + int(i.get("n_trips") or 0),
        "n_eta_rows_total": int(o.get("n_eta_rows") or 0) + int(i.get("n_eta_rows") or 0),
        "n_trips_O": int(o.get("n_trips") or 0),
        "n_trips_I": int(i.get("n_trips") or 0),
    }
    return result
