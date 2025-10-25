
import swisseph as swe
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

# --- KP Constants ---
SWISS_EPHE_PATH = "astro_engine/ephe"
KP_NEW_AYANAMSA = swe.SIDM_KRISHNAMURTI
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18,
    'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
NAKSHATRA_LENGTH = 13 + 20/60
TOTAL_NAKSHATRAS = 27
WEEKDAY_LORDS = ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"]

def normalize360(deg):
    while deg < 0:
        deg += 360
    return deg % 360.0

def sign_deg(deg):
    sign = int(deg // 30)
    sign_name = ZODIAC_SIGNS[sign]
    deg_in_sign = deg % 30
    return sign, sign_name, deg_in_sign

def get_sign_lord(sign_name):
    lords = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun",
        "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter", "Capricorn": "Saturn",
        "Aquarius": "Saturn", "Pisces": "Jupiter"
    }
    return lords[sign_name]

def get_nakshatra_chain(degree, levels=4):
    deg = normalize360(degree)
    chain = []
    nak_index = int(deg // NAKSHATRA_LENGTH)
    nak_lord = NAKSHATRA_LORDS[nak_index]
    chain.append(nak_lord)
    pos = deg - nak_index * NAKSHATRA_LENGTH
    for level in range(levels - 1):
        start_idx = DASHA_ORDER.index(chain[-1])
        sub_sequence = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]
        total_len = NAKSHATRA_LENGTH if level == 0 else sub_span
        mins_cumulative = 0
        found = False
        for lord in sub_sequence:
            sub_span = total_len * (DASHA_YEARS[lord] / 120)
            sub_span_mins = sub_span * 60
            if (pos * 60) < (mins_cumulative + sub_span_mins):
                chain.append(lord)
                pos = (pos * 60 - mins_cumulative) / sub_span_mins * sub_span if sub_span_mins != 0 else 0
                found = True
                break
            mins_cumulative += sub_span_mins
        if not found:
            chain.append(sub_sequence[-1])
            pos = 0
    return chain[:levels]

def julday_from_date_time(date_str, time_str, tz_offset):
    y, m, d = [int(x) for x in date_str.split("-")]
    tparts = [float(x) for x in time_str.split(":")]
    hour, minute = int(tparts[0]), int(tparts[1])
    second = int(tparts[2]) if len(tparts) > 2 else 0
    dt = datetime(y, m, d, hour, minute, second) - timedelta(hours=tz_offset)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)

def get_asc_from_horary_num(horary_num):
    sub_sizes = []
    for n in range(TOTAL_NAKSHATRAS):
        nak_lord = NAKSHATRA_LORDS[n]
        start_idx = DASHA_ORDER.index(nak_lord)
        sub_sequence = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]
        for lord in sub_sequence:
            size = NAKSHATRA_LENGTH * DASHA_YEARS[lord] / 120
            sub_sizes.append(size)
    degs = [0]
    for sz in sub_sizes:
        degs.append(degs[-1] + sz)
    idx = min(max(horary_num, 1), 249) - 1
    return normalize360(degs[idx])

def house_cusps(jd, lat, lon, asc_long, ayanamsha_mode):
    swe.set_sid_mode(ayanamsha_mode, 0, 0)
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'P')
    houses = list(houses)
    houses[0] = asc_long
    cusps = []
    for i in range(12):
        cusp_long = normalize360(houses[i])
        sign, sign_name, deg_in_sign = sign_deg(cusp_long)
        chain = get_nakshatra_chain(cusp_long, 4)
        cusps.append({
            "house": i+1,
            "longitude": round(cusp_long, 6),
            "sign": sign_name,
            "deg_in_sign": round(deg_in_sign, 6),
            "rasi_lord": get_sign_lord(sign_name),
            "nakshatra_lord": chain[0],
            "sub_lord": chain[1],
            "sub_sub_lord": chain[2],
            "sub_sub_sub_lord": chain[3]
        })
    return cusps

def planet_chain(jd, ayanamsha_mode):
    swe.set_sid_mode(ayanamsha_mode, 0, 0)
    planets = []
    ids = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.TRUE_NODE]
    planet_names = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu"]
    for idx, pid in enumerate(ids):
        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        speed = pos[3]
        sid_long = normalize360(pos[0])
        sign, sign_name, deg_in_sign = sign_deg(sid_long)
        chain = get_nakshatra_chain(sid_long, 4)
        planets.append({
            "name": planet_names[idx],
            "longitude": round(sid_long, 6),
            "sign": sign_name,
            "deg_in_sign": round(deg_in_sign, 6),
            "rasi_lord": get_sign_lord(sign_name),
            "nakshatra_lord": chain[0],
            "sub_lord": chain[1],
            "sub_sub_lord": chain[2],
            "sub_sub_sub_lord": chain[3],
            "retrograde": speed < 0
        })
    rahu = planets[7]["longitude"]
    ketu_long = normalize360(rahu + 180)
    sign, sign_name, deg_in_sign = sign_deg(ketu_long)
    chain = get_nakshatra_chain(ketu_long, 4)
    planets.append({
        "name": "Ketu",
        "longitude": round(ketu_long, 6),
        "sign": sign_name,
        "deg_in_sign": round(deg_in_sign, 6),
        "rasi_lord": get_sign_lord(sign_name),
        "nakshatra_lord": chain[0],
        "sub_lord": chain[1],
        "sub_sub_lord": chain[2],
        "sub_sub_sub_lord": chain[3],
        "retrograde": planets[7]["retrograde"]
    })
    return planets

def planet_house_assignment(planets, cusps):
    cusp_bounds = [normalize360(c['longitude']) for c in cusps]
    planets_in_houses = [[] for _ in range(12)]
    for planet in planets:
        pdeg = normalize360(planet["longitude"])
        house = None
        for i in range(12):
            start = cusp_bounds[i]
            end = cusp_bounds[(i+1)%12]
            if start < end:
                if start <= pdeg < end:
                    house = i+1
                    break
            else:
                if pdeg >= start or pdeg < end:
                    house = i+1
                    break
        planet["house_occupied"] = house
        planets_in_houses[house-1].append(planet)
    return planets_in_houses, planets

def kp_chain_house_links(planet_name, planets, cusps):
    p = next((x for x in planets if x["name"] == planet_name), None)
    if not p: return []
    links = set()
    if p.get("house_occupied"):
        links.add(p["house_occupied"])
    for c in cusps:
        if p["name"] == c["rasi_lord"]:
            links.add(c["house"])
        if p["nakshatra_lord"] == c["rasi_lord"]:
            links.add(c["house"])
    return sorted(list(links))

def sub_lord_chain_judgment(house_num, cusps, planets, good_houses=None, bad_houses=None):
    if good_houses is None: good_houses = [4,11]
    if bad_houses is None: bad_houses = [3,6,12]
    cusp = cusps[house_num-1]
    chain = [cusp["sub_lord"], cusp["sub_sub_lord"], cusp["sub_sub_sub_lord"]]
    chain_house_links = []
    for lord in chain:
        house_links = kp_chain_house_links(lord, planets, cusps)
        chain_house_links.append({
            "planet": lord,
            "houses_signified": house_links,
            "good": [h for h in house_links if h in good_houses],
            "bad": [h for h in house_links if h in bad_houses],
            "neutral": [h for h in house_links if h not in good_houses and h not in bad_houses]
        })
    total_good = sum(len(x["good"]) for x in chain_house_links)
    total_bad = sum(len(x["bad"]) for x in chain_house_links)
    if total_good > total_bad:
        verdict = "YES"
        confidence = "HIGH" if total_good - total_bad >= 2 else "MEDIUM"
        rationale = f"Chain lords strongly favor good houses: {[(x['planet'], x['good']) for x in chain_house_links if x['good']]}"
    elif total_bad > total_good:
        verdict = "NO"
        confidence = "HIGH" if total_bad - total_good >= 2 else "MEDIUM"
        rationale = f"Chain lords favor bad houses: {[(x['planet'], x['bad']) for x in chain_house_links if x['bad']]}"
    else:
        verdict = "MAYBE"
        confidence = "LOW"
        rationale = "Chain lords have balanced or weak links."
    return {
        "chain": chain_house_links,
        "verdict": verdict,
        "confidence": confidence,
        "rationale": rationale
    }

def calc_vimshottari_dasha_path(jd, moon_longitude):
    deg = normalize360(moon_longitude)
    nak_num = int(deg // NAKSHATRA_LENGTH)
    nak_lord = NAKSHATRA_LORDS[nak_num]
    pos_in_nak = deg - nak_num * NAKSHATRA_LENGTH
    percent = pos_in_nak / NAKSHATRA_LENGTH
    idx = DASHA_ORDER.index(nak_lord)
    sequence = DASHA_ORDER[idx:] + DASHA_ORDER[:idx]
    today = jd
    elapsed = percent * DASHA_YEARS[nak_lord]
    dasha_start = today - elapsed * 365.25
    path = []
    running = dasha_start
    for i, lord in enumerate(sequence):
        years = DASHA_YEARS[lord]
        start = running
        end = running + years*365.25
        if start <= today < end:
            major_lord = lord
            major_idx = i
            major_start = start
            major_end = end
            path.append({
                "level": "Dasha",
                "lord": major_lord,
                "start_jd": start,
                "end_jd": end,
                "start_date": swe.revjul(start)[:3],
                "end_date": swe.revjul(end)[:3]
            })
            break
        running = end
    seq2 = sequence
    major_days = major_end - major_start
    bhukti_lengths = [major_days * DASHA_YEARS[b] / 120 for b in seq2]
    bhukti_ends = [major_start]
    for l in bhukti_lengths:
        bhukti_ends.append(bhukti_ends[-1] + l)
    for i in range(9):
        if bhukti_ends[i] <= today < bhukti_ends[i+1]:
            bhukti_lord = seq2[i]
            bhukti_start = bhukti_ends[i]
            bhukti_end = bhukti_ends[i+1]
            path.append({
                "level": "Bhukti",
                "lord": bhukti_lord,
                "start_jd": bhukti_start,
                "end_jd": bhukti_end,
                "start_date": swe.revjul(bhukti_start)[:3],
                "end_date": swe.revjul(bhukti_end)[:3]
            })
            break
    antara_days = bhukti_end - bhukti_start
    antara_lengths = [antara_days * DASHA_YEARS[a] / 120 for a in seq2]
    antara_ends = [bhukti_start]
    for l in antara_lengths:
        antara_ends.append(antara_ends[-1] + l)
    for i in range(9):
        if antara_ends[i] <= today < antara_ends[i+1]:
            antara_lord = seq2[i]
            antara_start = antara_ends[i]
            antara_end = antara_ends[i+1]
            path.append({
                "level": "Antara",
                "lord": antara_lord,
                "start_jd": antara_start,
                "end_jd": antara_end,
                "start_date": swe.revjul(antara_start)[:3],
                "end_date": swe.revjul(antara_end)[:3]
            })
            break
    sukshma_days = antara_end - antara_start
    sukshma_lengths = [sukshma_days * DASHA_YEARS[s] / 120 for s in seq2]
    sukshma_ends = [antara_start]
    for l in sukshma_lengths:
        sukshma_ends.append(sukshma_ends[-1] + l)
    for i in range(9):
        if sukshma_ends[i] <= today < sukshma_ends[i+1]:
            sukshma_lord = seq2[i]
            sukshma_start = sukshma_ends[i]
            sukshma_end = sukshma_ends[i+1]
            path.append({
                "level": "Sukshma",
                "lord": sukshma_lord,
                "start_jd": sukshma_start,
                "end_jd": sukshma_end,
                "start_date": swe.revjul(sukshma_start)[:3],
                "end_date": swe.revjul(sukshma_end)[:3]
            })
            break
    for i in range(1, len(path)):
        elapsed = today - path[i]["start_jd"]
        total = path[i]["end_jd"] - path[i]["start_jd"]
        path[i]["percent_elapsed"] = round(100*elapsed/total,2)
    return path

def kp_timing_by_dasha_layers(dasha_path, planets, cusps, good_houses):
    timing = []
    for layer in dasha_path:
        lord = layer["lord"]
        houses = kp_chain_house_links(lord, planets, cusps)
        relevant = sorted([h for h in houses if h in good_houses])
        if relevant:
            timing.append({
                "dasha_layer": layer["level"],
                "lord": lord,
                "good_houses": relevant,
                "start_date": layer["start_date"],
                "end_date": layer["end_date"],
                "event_estimate": f"Event possible during {layer['level']} of {lord} ({layer['start_date']}–{layer['end_date']})"
            })
    return timing

def get_ruling_planets(ascendant, moon, date_str):
    weekday = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    day_lord = WEEKDAY_LORDS[weekday]
    return {
        "asc_sign_lord": ascendant["rasi_lord"],
        "asc_star_lord": ascendant["nakshatra_lord"],
        "moon_sign_lord": moon["rasi_lord"],
        "moon_star_lord": moon["nakshatra_lord"],
        "day_lord": day_lord
    }

def get_significators_expanded(house_num, cusps, planets):
    occupants = [p["name"] for p in planets if p["house_occupied"] == house_num]
    cusp = cusps[house_num-1]
    lord_name = cusp["rasi_lord"]
    lords = [p["name"] for p in planets if p["name"] == lord_name]
    star_lords = [p["name"] for p in planets if p["nakshatra_lord"] == lord_name]
    planets_signifying = []
    for p in planets:
        signifies = set()
        links = []
        if p["house_occupied"]:
            signifies.add(p["house_occupied"])
            links.append(f"occupant of {p['house_occupied']}")
        for c in cusps:
            if p["name"] == c["rasi_lord"]:
                signifies.add(c["house"])
                links.append(f"lord of {c['house']}")
            if p["nakshatra_lord"] == c["rasi_lord"]:
                signifies.add(c["house"])
                links.append(f"star-lord for lord of {c['house']}")
        planets_signifying.append({
            "planet": p["name"],
            "houses_signified": sorted(list(signifies)),
            "links": links,
            "house_occupied": p.get("house_occupied"),
            "rasi_lord": p.get("rasi_lord"),
            "nakshatra_lord": p.get("nakshatra_lord"),
            "sub_lord": p.get("sub_lord")
        })
    return {
        "main_house": house_num,
        "occupants": occupants,
        "lords": lords,
        "star_lords": star_lords,
        "planets_signifying": planets_signifying
    }

def check_radicality(asc_long):
    deg_in_sign = asc_long % 30
    return {
        "early_ascendant": deg_in_sign < 3,
        "late_ascendant": deg_in_sign > 27
    }

def check_void_of_course_moon(planets, cusps):
    moon = next(p for p in planets if p["name"] == "Moon")
    sign_idx = ZODIAC_SIGNS.index(moon['sign'])
    sign_end = (sign_idx+1)*30
    degrees_left = sign_end - moon['longitude']
    applying = False
    for p in planets:
        if p["name"] == "Moon":
            continue
        if p["sign"] == moon["sign"] and p["longitude"] > moon["longitude"]:
            applying = True
            break
    void = (degrees_left < 3) and (not applying)
    return {"void_of_course": void, "degrees_left": degrees_left}

