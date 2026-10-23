"""MTR Corporation — Next Train real-time arrivals (not pure data.gov.hk CKAN)."""


def mtr_lines() -> list:
    """Supported MTR Next Train line codes and station codes.

    Provides:
        - line code, English/Chinese name, list of station codes with names

    Coverage:
        - Geography: heavy-rail lines in the Next Train API (AEL, TCL, TML,
          TKL, EAL, SIL, TWL, ISL, KTL, DRL) — not Light Rail
        - Time:      static code table (API spec v1.7)

    Datasets:   mtr-data2-nexttrain-data
    Department: MTR Corporation Limited
    Endpoint:   https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php
                (codes from Next_Train_API_Spec_v1.7.pdf)
    Format:     static dict (no network)

    Usage:
        >>> lines = mtr_lines()
        >>> [L["line"] for L in lines]

    Questions:
        - "MTR Next Train line codes"
        - "which stations on Tung Chung Line"
        - "港鐵路線代碼"

    Quirks:
        - Light Rail has a separate dataset (mtr-lrnt_data-light-rail-nexttrain-data)
        - line+sta combination must be valid or API returns empty/error
        - hosted on rt.data.gov.hk but provider is MTR (opendata.mtr.com.hk docs)
    """
    return [
        {"line": "AEL", "name_en": "Airport Express", "name_tc": "機場快線",
         "stations": [
             ("HOK", "Hong Kong", "香港"), ("KOW", "Kowloon", "九龍"),
             ("TSY", "Tsing Yi", "青衣"), ("AIR", "Airport", "機場"),
             ("AWE", "AsiaWorld Expo", "博覽館")]},
        {"line": "TCL", "name_en": "Tung Chung Line", "name_tc": "東涌線",
         "stations": [
             ("HOK", "Hong Kong", "香港"), ("KOW", "Kowloon", "九龍"),
             ("OLY", "Olympic", "奧運"), ("NAC", "Nam Cheong", "南昌"),
             ("LAK", "Lai King", "荔景"), ("TSY", "Tsing Yi", "青衣"),
             ("SUN", "Sunny Bay", "欣澳"), ("TUC", "Tung Chung", "東涌")]},
        {"line": "TML", "name_en": "Tuen Ma Line", "name_tc": "屯馬線",
         "stations": [
             ("WKS", "Wu Kai Sha", "烏溪沙"), ("MOS", "Ma On Shan", "馬鞍山"),
             ("HEO", "Heng On", "恆安"), ("TSH", "Tai Shui Hang", "大水坑"),
             ("SHM", "Shek Mun", "石門"), ("CIO", "City One", "第一城"),
             ("STW", "Sha Tin Wai", "沙田圍"), ("CKT", "Che Kung Temple", "車公廟"),
             ("TAW", "Tai Wai", "大圍"), ("HIK", "Hin Keng", "顯徑"),
             ("DIH", "Diamond Hill", "鑽石山"), ("KAT", "Kai Tak", "啟德"),
             ("SUW", "Sung Wong Toi", "宋皇臺"), ("TKW", "To Kwa Wan", "土瓜灣"),
             ("HOM", "Ho Man Tin", "何文田"), ("HUH", "Hung Hom", "紅磡"),
             ("ETS", "East Tsim Sha Tsui", "尖東"), ("AUS", "Austin", "柯士甸"),
             ("NAC", "Nam Cheong", "南昌"), ("MEF", "Mei Foo", "美孚"),
             ("TWW", "Tsuen Wan West", "荃灣西"),
             ("KSR", "Kam Sheung Road", "錦上路"), ("YUL", "Yuen Long", "元朗"),
             ("LOP", "Long Ping", "朗屏"), ("TIS", "Tin Shui Wai", "天水圍"),
             ("SIH", "Siu Hong", "兆康"), ("TUM", "Tuen Mun", "屯門")]},
        {"line": "TKL", "name_en": "Tseung Kwan O Line", "name_tc": "將軍澳線",
         "stations": [
             ("NOP", "North Point", "北角"), ("QUB", "Quarry Bay", "鰂魚涌"),
             ("YAT", "Yau Tong", "油塘"), ("TIK", "Tiu Keng Leng", "調景嶺"),
             ("TKO", "Tseung Kwan O", "將軍澳"), ("LHP", "LOHAS Park", "康城"),
             ("HAH", "Hang Hau", "坑口"), ("POA", "Po Lam", "寶琳")]},
        {"line": "EAL", "name_en": "East Rail Line", "name_tc": "東鐵線",
         "stations": [
             ("ADM", "Admiralty", "金鐘"), ("EXC", "Exhibition Centre", "會展"),
             ("HUH", "Hung Hom", "紅磡"), ("MKK", "Mong Kok East", "旺角東"),
             ("KOT", "Kowloon Tong", "九龍塘"), ("TAW", "Tai Wai", "大圍"),
             ("SHT", "Sha Tin", "沙田"), ("FOT", "Fo Tan", "火炭"),
             ("RAC", "Racecourse", "馬場"), ("UNI", "University", "大學"),
             ("TAP", "Tai Po Market", "大埔墟"), ("TWO", "Tai Wo", "太和"),
             ("FAN", "Fanling", "粉嶺"), ("SHS", "Sheung Shui", "上水"),
             ("LOW", "Lo Wu", "羅湖"), ("LMC", "Lok Ma Chau", "落馬洲")]},
        {"line": "SIL", "name_en": "South Island Line", "name_tc": "南港島線",
         "stations": [
             ("ADM", "Admiralty", "金鐘"), ("OCP", "Ocean Park", "海洋公園"),
             ("WCH", "Wong Chuk Hang", "黃竹坑"), ("LET", "Lei Tung", "利東"),
             ("SOH", "South Horizons", "海怡半島")]},
        {"line": "TWL", "name_en": "Tsuen Wan Line", "name_tc": "荃灣線",
         "stations": [
             ("CEN", "Central", "中環"), ("ADM", "Admiralty", "金鐘"),
             ("TST", "Tsim Sha Tsui", "尖沙咀"), ("JOR", "Jordan", "佐敦"),
             ("YMT", "Yau Ma Tei", "油麻地"), ("MOK", "Mong Kok", "旺角"),
             ("PRE", "Prince Edward", "太子"), ("SSP", "Sham Shui Po", "深水埗"),
             ("CSW", "Cheung Sha Wan", "長沙灣"), ("LCK", "Lai Chi Kok", "荔枝角"),
             ("MEF", "Mei Foo", "美孚"), ("LAK", "Lai King", "荔景"),
             ("KWF", "Kwai Fong", "葵芳"), ("KWH", "Kwai Hing", "葵興"),
             ("TWH", "Tai Wo Hau", "大窩口"), ("TSW", "Tsuen Wan", "荃灣")]},
        {"line": "ISL", "name_en": "Island Line", "name_tc": "港島線",
         "stations": [
             ("KET", "Kennedy Town", "堅尼地城"), ("HKU", "HKU", "香港大學"),
             ("SYP", "Sai Ying Pun", "西營盤"), ("SHW", "Sheung Wan", "上環"),
             ("CEN", "Central", "中環"), ("ADM", "Admiralty", "金鐘"),
             ("WAC", "Wan Chai", "灣仔"), ("CAB", "Causeway Bay", "銅鑼灣"),
             ("TIH", "Tin Hau", "天后"), ("FOH", "Fortress Hill", "炮台山"),
             ("NOP", "North Point", "北角"), ("QUB", "Quarry Bay", "鰂魚涌"),
             ("TAK", "Tai Koo", "太古"), ("SWH", "Sai Wan Ho", "西灣河"),
             ("SKW", "Shau Kei Wan", "筲箕灣"),
             ("HFC", "Heng Fa Chuen", "杏花邨"), ("CHW", "Chai Wan", "柴灣")]},
        {"line": "KTL", "name_en": "Kwun Tong Line", "name_tc": "觀塘線",
         "stations": [
             ("WHA", "Whampoa", "黃埔"), ("HOM", "Ho Man Tin", "何文田"),
             ("YMT", "Yau Ma Tei", "油麻地"), ("MOK", "Mong Kok", "旺角"),
             ("PRE", "Prince Edward", "太子"), ("SKM", "Shek Kip Mei", "石硤尾"),
             ("KOT", "Kowloon Tong", "九龍塘"), ("LOF", "Lok Fu", "樂富"),
             ("WTS", "Wong Tai Sin", "黃大仙"), ("DIH", "Diamond Hill", "鑽石山"),
             ("CHH", "Choi Hung", "彩虹"), ("KOB", "Kowloon Bay", "九龍灣"),
             ("NTK", "Ngau Tau Kok", "牛頭角"), ("KWT", "Kwun Tong", "觀塘"),
             ("LAT", "Lam Tin", "藍田"), ("YAT", "Yau Tong", "油塘"),
             ("TIK", "Tiu Keng Leng", "調景嶺")]},
        {"line": "DRL", "name_en": "Disneyland Resort Line", "name_tc": "迪士尼線",
         "stations": [
             ("SUN", "Sunny Bay", "欣澳"),
             ("DIS", "Disneyland Resort", "迪士尼")]},
    ]


def mtr_next_train(line: str, sta: str, lang: str = "TC") -> dict:
    """Live MTR Next Train arrivals (up to 4) for one line × station.

    Provides:
        - sys_time / curr_time (HKT)
        - UP[] / DOWN[] trains: ttnt (minutes), plat, time, dest, seq, valid
        - status, message, isdelay
        - resolved line/station names when codes known

    Coverage:
        - Geography: one station on one heavy-rail line (see mtr_lines)
        - Time:      real-time, ~every 10 seconds

    Datasets:   mtr-data2-nexttrain-data
    Department: MTR Corporation Limited
    Endpoint:   https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line=&sta=&lang=
    Format:     JSON

    Usage:
        >>> r = mtr_next_train("TCL", "TUC")   # Tung Chung Line @ Tung Chung
        >>> r["data"]["TCL-TUC"]["UP"][:2]
        >>> mtr_next_train("TWL", "MOK", lang="EN")

    Questions:
        - "東涌線下一班車"
        - "next train Tung Chung Line"
        - "MTR ETA Mong Kok Tsuen Wan Line"
        - "港鐵實時到站"

    Quirks:
        - NOT a pure data.gov.hk CKAN download — MTR-operated API on
          rt.data.gov.hk; docs at opendata.mtr.com.hk (Next_Train_API_Spec)
        - line and sta are uppercase codes (TCL+TUC, TWL+MOK, …)
        - invalid line+sta combo → empty data or status 0 message
        - status 0 may mean special service / suspension (see message + url)
        - isdelay Y with empty trains = data absence / last-train edge
        - HTTP 429 = too many requests; back off
        - Light Rail / MTR Bus are separate APIs
        - dest field is a station code, not a full name
    """
    import json
    import urllib.parse
    import urllib.request

    line = (line or "").strip().upper()
    sta = (sta or "").strip().upper()
    lang = (lang or "TC").strip().upper()
    if lang not in ("EN", "TC"):
        lang = "TC"

    params = urllib.parse.urlencode(
        {"line": line, "sta": sta, "lang": lang})
    url = ("https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?"
           + params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    # attach friendly names when known
    line_name_en = line_name_tc = None
    sta_name_en = sta_name_tc = None
    for L in mtr_lines():
        if L["line"] == line:
            line_name_en, line_name_tc = L["name_en"], L["name_tc"]
            for code, en, tc in L["stations"]:
                if code == sta:
                    sta_name_en, sta_name_tc = en, tc
                    break
            break

    payload["query"] = {
        "line": line, "sta": sta, "lang": lang,
        "line_name_en": line_name_en, "line_name_tc": line_name_tc,
        "sta_name_en": sta_name_en, "sta_name_tc": sta_name_tc,
        "url": url,
    }
    return payload
