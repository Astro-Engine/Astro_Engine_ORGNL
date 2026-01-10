import sys
import os
import math
import datetime
import swisseph as swe

# =================================================================================
# CONFIGURATION
# =================================================================================

EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Planet Constants
SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN = 0, 1, 4, 2, 5, 3, 6
PLANET_NAMES = {
    0: "Sun", 1: "Moon", 4: "Mars", 2: "Mercury",
    5: "Jupiter", 3: "Venus", 6: "Saturn"
}
PLANETS_LIST = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN]

# Natural Friendships
NATURAL_RELATIONSHIPS = {
    SUN:     {SUN: 0, MOON: 1, MARS: 1, MERCURY: 0, JUPITER: 1, VENUS: -1, SATURN: -1},
    MOON:    {SUN: 1, MOON: 0, MARS: 0, MERCURY: 1, JUPITER: 0, VENUS: 0,  SATURN: 0},
    MARS:    {SUN: 1, MOON: 1, MARS: 0, MERCURY: -1, JUPITER: 1, VENUS: 0,  SATURN: 0},
    MERCURY: {SUN: 1, MOON: -1, MARS: 0, MERCURY: 0, JUPITER: 0, VENUS: 1,  SATURN: 0},
    JUPITER: {SUN: 1, MOON: 1, MARS: 1, MERCURY: -1, JUPITER: 0, VENUS: -1, SATURN: 0},
    VENUS:   {SUN: -1, MOON: -1, MARS: 0, MERCURY: 1, JUPITER: 0, VENUS: 0,  SATURN: 1},
    SATURN:  {SUN: -1, MOON: -1, MARS: -1, MERCURY: 1, JUPITER: 0, VENUS: 1,  SATURN: 0},
}

# Strength Thresholds
STRENGTH_THRESHOLDS = {
    SUN: 390, MOON: 360, MARS: 300, MERCURY: 420,
    JUPITER: 390, VENUS: 330, SATURN: 300
}

# Deep Exaltation Degrees
DEBILITATION_POINTS = {
    SUN: 190.0, MOON: 213.0, MARS: 118.0, MERCURY: 345.0,
    JUPITER: 275.0, VENUS: 177.0, SATURN: 20.0
}

# Naisargika Bala
NAISARGIKA_BALA = {
    SUN: 60.0, MOON: 51.43, MARS: 17.14, MERCURY: 25.71,
    JUPITER: 34.28, VENUS: 42.85, SATURN: 8.57
}

# =================================================================================
# HELPER FUNCTIONS
# =================================================================================

def normalize(angle):
    """Normalize angle to 0-360 degrees"""
    return angle % 360

def angular_distance(p1, p2):
    """Shortest distance between two points on the circle"""
    dist = abs(p1 - p2)
    return dist if dist <= 180 else 360 - dist

def get_sign(longitude):
    """0 = Aries, 1 = Taurus, etc."""
    return int(normalize(longitude) / 30)

def calculate_varga_sign(planet_lon, varga_num):
    deg = planet_lon % 30
    sign = int(planet_lon / 30)
    if varga_num == 1: return sign
    elif varga_num == 2:
        is_odd_sign = ((sign + 1) % 2 != 0) 
        first_half = deg < 15
        if is_odd_sign: return 4 if first_half else 3 
        else: return 3 if first_half else 4 
    elif varga_num == 3:
        part = int(deg / 10)
        if part == 0: return sign
        if part == 1: return (sign + 4) % 12
        if part == 2: return (sign + 8) % 12
    elif varga_num == 7:
        part = int(deg / (30/7))
        is_odd_sign = ((sign + 1) % 2 != 0)
        start = sign if is_odd_sign else (sign + 6) % 12
        return (start + part) % 12
    elif varga_num == 9:
        part = int(deg / (30/9))
        element = sign % 4
        start_indices = {0: 0, 1: 9, 2: 6, 3: 3}
        start = start_indices[element]
        return (start + part) % 12
    elif varga_num == 12:
        part = int(deg / 2.5)
        return (sign + part) % 12
    elif varga_num == 30:
        is_odd_sign = ((sign + 1) % 2 != 0)
        if is_odd_sign:
            if deg < 5: return 0 
            elif deg < 10: return 10 
            elif deg < 18: return 8 
            elif deg < 25: return 2 
            else: return 6 
        else:
            if deg < 5: return 1 
            elif deg < 12: return 5 
            elif deg < 20: return 11 
            elif deg < 25: return 9 
            else: return 7 
    return sign

# =================================================================================
# CORE CALCULATION
# =================================================================================

def calculate_shad_bala_core(jd_ut, lat, lon, planets_sid, planets_trop, asc_sid, mc_sid, cusps_sripati, ayanamsa):
    
    SB = {p: {} for p in PLANETS_LIST}
    TOTALS = {p: 0.0 for p in PLANETS_LIST}
    PHALA = {p: {'Ishta': 0.0, 'Kashta': 0.0} for p in PLANETS_LIST}

    # 1. STHANA BALA
    # --------------
    
    # A. Uchcha Bala
    for p in PLANETS_LIST:
        dist = abs(planets_sid[p]['lon'] - DEBILITATION_POINTS[p])
        if dist > 180: dist = 360 - dist
        SB[p]['Uchcha Bala'] = dist / 3.0

    # B. Saptavarga Bala
    temp_rels = {p: {} for p in PLANETS_LIST}
    p_signs = {p: get_sign(planets_sid[p]['lon']) for p in PLANETS_LIST}
    
    for p1 in PLANETS_LIST:
        for p2 in PLANETS_LIST:
            if p1 == p2:
                temp_rels[p1][p2] = 0
                continue
            count = (p_signs[p2] - p_signs[p1]) + 1
            if count <= 0: count += 12
            if count in [2, 3, 4, 10, 11, 12]: temp_rels[p1][p2] = 1 
            else: temp_rels[p1][p2] = -1 

    SIGN_LORDS = [4, 3, 2, 1, 0, 2, 3, 4, 5, 6, 6, 5]
    
    for p in PLANETS_LIST:
        total_varga = 0
        for v in [1, 2, 3, 7, 9, 12, 30]:
            s_idx = calculate_varga_sign(planets_sid[p]['lon'], v)
            lord = SIGN_LORDS[s_idx]
            val = 0
            if p == lord: val = 30.0
            else:
                combined = NATURAL_RELATIONSHIPS[p][lord] + temp_rels[p][lord]
                if combined == 2: val = 22.5
                elif combined == 1: val = 15.0
                elif combined == 0: val = 7.5
                elif combined == -1: val = 3.75
                elif combined == -2: val = 1.875
                else: val = 7.5
            
            if v == 1: 
                deg = planets_sid[p]['lon'] % 30
                sign = p_signs[p]
                is_mt = False
                if p==SUN and sign==4 and deg<=20: is_mt=True
                if p==MOON and sign==1 and 3<deg<=30: is_mt=True
                if p==MARS and sign==0 and deg<=12: is_mt=True
                if p==MERCURY and sign==5 and 15<=deg<=20: is_mt=True
                if p==JUPITER and sign==8 and deg<=10: is_mt=True
                if p==VENUS and sign==6 and deg<=5: is_mt=True
                if p==SATURN and sign==10 and deg<=20: is_mt=True
                if is_mt: val = 45.0
            total_varga += val
        SB[p]['Saptavarga Bala'] = total_varga

    # C. Ojayugma Bala
    for p in PLANETS_LIST:
        score = 0
        d1_odd = ((get_sign(planets_sid[p]['lon']) + 1) % 2 != 0)
        d9_odd = ((calculate_varga_sign(planets_sid[p]['lon'], 9) + 1) % 2 != 0)
        is_female = p in [MOON, VENUS]
        if is_female:
            if not d1_odd: score += 15
            if not d9_odd: score += 15
        else:
            if d1_odd: score += 15
            if d9_odd: score += 15
        SB[p]['Ojayugma Bala'] = score

    # D. Kendra Bala (FIX: Proximity + Rasi Logic)
    # This logic maximizes chances of planet being "Angular" (Kendra)
    for p in PLANETS_LIST:
        plon = planets_sid[p]['lon']
        
        # 1. Proximity Check (15 degree orb from Angle Cusps)
        # If planet is close to Asc, MC, Dsc, or IC, it is effectively Angular
        is_proximity_kendra = False
        
        # Angles: Asc (1), MC (10), Dsc (7), IC (4)
        # Sripati uses specific cusps for these.
        # Usually Cusp 1 = Asc, Cusp 10 = MC.
        
        idx_asc = 1 if len(cusps_sripati) == 13 else 0
        idx_mc = idx_asc + 9
        
        asc_deg = normalize(cusps_sripati[idx_asc])
        mc_deg = normalize(cusps_sripati[idx_mc])
        dsc_deg = normalize(asc_deg + 180)
        ic_deg = normalize(mc_deg + 180)
        
        orb = 15.0 # Generous Orb for "In the House"
        
        if (angular_distance(plon, asc_deg) < orb or 
            angular_distance(plon, mc_deg) < orb or
            angular_distance(plon, dsc_deg) < orb or
            angular_distance(plon, ic_deg) < orb):
            is_proximity_kendra = True

        # 2. Rasi Check
        # 1-based House from Ascendant Sign
        sign_num = get_sign(plon) + 1
        asc_sign = get_sign(asc_sid) + 1
        rasi_house = (sign_num - asc_sign) + 1
        if rasi_house <= 0: rasi_house += 12
        
        score = 15.0 # Default (Cadent)
        
        if is_proximity_kendra:
            score = 60.0
        else:
            # Fallback to Rasi Logic
            if rasi_house in [1, 4, 7, 10]: score = 60.0
            elif rasi_house in [2, 5, 8, 11]: score = 30.0
            else: score = 15.0
            
        SB[p]['Kendra Bala'] = score

    # E. Drekkana Bala
    for p in PLANETS_LIST:
        deg = planets_sid[p]['lon'] % 30
        decanate = 1 if deg < 10 else (2 if deg < 20 else 3)
        val = 0
        if p in [SUN, JUPITER, MARS] and decanate == 1: val = 15
        elif p in [SATURN, MERCURY] and decanate == 2: val = 15
        elif p in [MOON, VENUS] and decanate == 3: val = 15
        SB[p]['Drekkana Bala'] = val

    # 2. DIG BALA
    # -----------
    idx_1 = 1 if len(cusps_sripati) == 13 else 0
    power_points = {
        MERCURY: cusps_sripati[idx_1],        # Asc
        JUPITER: cusps_sripati[idx_1],
        SUN: cusps_sripati[idx_1+9],          # MC
        MARS: cusps_sripati[idx_1+9],
        SATURN: cusps_sripati[idx_1+6],       # Dsc
        VENUS: cusps_sripati[idx_1+3],        # IC
        MOON: cusps_sripati[idx_1+3]
    }
    for p in PLANETS_LIST:
        arc = angular_distance(planets_sid[p]['lon'], power_points[p])
        SB[p]['Dig Bala'] = (180.0 - arc) / 3.0

    # 3. KAALA BALA
    # -------------
    sun_mc_arc = angular_distance(planets_sid[SUN]['lon'], mc_sid) 
    day_strength = (180.0 - sun_mc_arc) / 3.0
    night_strength = sun_mc_arc / 3.0
    
    for p in PLANETS_LIST:
        if p == MERCURY: SB[p]['Natonnata Bala'] = 60.0
        elif p in [SUN, JUPITER, VENUS]: SB[p]['Natonnata Bala'] = day_strength
        else: SB[p]['Natonnata Bala'] = night_strength

    angle_mo_su = normalize(planets_sid[MOON]['lon'] - planets_sid[SUN]['lon'])
    eff_angle = angle_mo_su if angle_mo_su <= 180 else (360 - angle_mo_su)
    paksha_score = eff_angle / 3.0
    
    for p in PLANETS_LIST:
        if p in [JUPITER, VENUS, MOON, MERCURY]: SB[p]['Paksha Bala'] = paksha_score
        else: SB[p]['Paksha Bala'] = 60.0 - paksha_score

    for p in PLANETS_LIST:
        decl = planets_trop[p]['decl']
        val = 0
        if p == MERCURY: val = 30.0
        elif p in [SUN, MARS, JUPITER, VENUS]: val = ((24.0 + decl) / 48.0) * 60.0
        elif p in [MOON, SATURN]: val = ((24.0 - decl) / 48.0) * 60.0
        SB[p]['Ayana Bala'] = max(0, min(60, val))

    # Bonus for Jupiter
    for p in PLANETS_LIST: SB[p]['Tri-Bhaga Bala'] = 0.0
    SB[JUPITER]['Tri-Bhaga Bala'] = 60.0

    # 4. CHESTA BALA
    # --------------
    SB[SUN]['Chesta Bala'] = SB[SUN]['Ayana Bala']
    SB[MOON]['Chesta Bala'] = SB[MOON]['Paksha Bala']
    
    seeghrocha = {}
    seeghrocha[MARS] = planets_sid[SUN]['lon']
    seeghrocha[JUPITER] = planets_sid[SUN]['lon']
    seeghrocha[SATURN] = planets_sid[SUN]['lon']
    for p in [MERCURY, VENUS]:
        res_helio = swe.calc_ut(jd_ut, p, swe.FLG_HELCTR) 
        seeghrocha[p] = normalize(res_helio[0][0] - ayanamsa)

    for p in [MARS, MERCURY, JUPITER, VENUS, SATURN]:
        kendra = normalize(seeghrocha[p] - planets_sid[p]['lon'])
        if kendra > 180: kendra = 360 - kendra
        SB[p]['Chesta Bala'] = kendra / 3.0

    # 5. NAISARGIKA BALA
    # ------------------
    for p in PLANETS_LIST:
        SB[p]['Naisargika Bala'] = NAISARGIKA_BALA[p]

    # 6. DRIK BALA
    # ------------
    for aspected in PLANETS_LIST:
        net_score = 0
        for aspector in PLANETS_LIST:
            if aspected == aspector: continue
            angle = normalize(planets_sid[aspector]['lon'] - planets_sid[aspected]['lon'])
            drishti = 0
            is_special = False
            orb = 8.0 
            
            if aspector == MARS:
                if abs(angle - 90) <= orb or abs(angle - 210) <= orb: drishti = 60; is_special = True
            elif aspector == JUPITER:
                if abs(angle - 120) <= orb or abs(angle - 240) <= orb: drishti = 60; is_special = True
            elif aspector == SATURN:
                if abs(angle - 60) <= orb or abs(angle - 270) <= orb: drishti = 60; is_special = True
            
            if not is_special:
                if 30 <= angle < 60: drishti = (angle - 30) / 2.0
                elif 60 <= angle < 90: drishti = (angle - 60) + 15.0
                elif 90 <= angle < 120: drishti = 45.0 - ((angle - 90) / 2.0)
                elif 120 <= angle < 150: drishti = 30.0 - (angle - 120)
                elif 150 <= angle < 180: drishti = (angle - 150) * 2.0
                else: drishti = 0
            
            impact = drishti
            if aspector in [JUPITER, VENUS, MERCURY]: net_score += impact
            elif aspector == MOON:
                if SB[MOON]['Paksha Bala'] > 30: net_score += impact
                else: net_score -= impact
            else: net_score -= impact
        
        SB[aspected]['Drik Bala'] = net_score / 4.0

    # SUMMATION
    # ---------
    for p in PLANETS_LIST:
        sthana = (SB[p]['Uchcha Bala'] + SB[p]['Saptavarga Bala'] + 
                  SB[p]['Ojayugma Bala'] + SB[p]['Kendra Bala'] + 
                  SB[p]['Drekkana Bala'])
        SB[p]['STHANA TOTAL'] = sthana
        
        kaala = (SB[p].get('Natonnata Bala',0) + SB[p]['Paksha Bala'] + 
                 SB[p]['Ayana Bala'] + SB[p].get('Tri-Bhaga Bala', 0))
                 
        total = (sthana + SB[p]['Dig Bala'] + kaala + 
                 SB[p]['Chesta Bala'] + SB[p]['Naisargika Bala'] + 
                 SB[p]['Drik Bala'])
                 
        TOTALS[p] = total
        u, c = SB[p]['Uchcha Bala'], SB[p]['Chesta Bala']
        PHALA[p]['Ishta'] = (u + c) / 2.0
        PHALA[p]['Kashta'] = ((60.0 - u) + (60.0 - c)) / 2.0

    return SB, TOTALS, PHALA

def calculate_shadbala_advanced(uname, bdate, btime, lat, lon, tz):
    """
    Calculate Advanced Shadbala with Sripati house system
    
    Args:
        uname: User's name
        bdate: Birth date (YYYY-MM-DD)
        btime: Birth time (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with complete Shadbala results
    """
    local_dt = datetime.datetime.strptime(f"{bdate} {btime}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=tz)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                       utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    
    planets_sid = {}
    for pid in PLANETS_LIST:
        res = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        planets_sid[pid] = {'lon': res[0][0], 'speed': res[0][3]}

    cusps_sripati, ascmc = swe.houses(jd_ut, lat, lon, b'O')
    asc_sid = ascmc[0]
    mc_sid = ascmc[1]

    planets_trop = {}
    for pid in PLANETS_LIST:
        res = swe.calc_ut(jd_ut, pid, swe.FLG_EQUATORIAL)
        planets_trop[pid] = {'decl': res[0][1]}

    details, totals, phala = calculate_shad_bala_core(
        jd_ut, lat, lon, planets_sid, planets_trop, asc_sid, mc_sid, cusps_sripati, ayanamsa
    )

    weekday = utc_dt.weekday()
    day_map = {0: MOON, 1: MARS, 2: MERCURY, 3: JUPITER, 4: VENUS, 5: SATURN, 6: SUN}
    day_lord = day_map[weekday]
    totals[day_lord] += 45.0
    details[day_lord]['Kaala_Dina_Bala'] = 45.0
    
    rank_list = []
    for p in PLANETS_LIST:
        pct = totals[p] / STRENGTH_THRESHOLDS[p]
        rank_list.append({'planet': p, 'pct': pct})
    rank_list.sort(key=lambda x: x['pct'], reverse=True)
    ranks = {item['planet']: idx+1 for idx, item in enumerate(rank_list)}

    output = {
        "meta": {
            "user": uname,
            "ascendant": asc_sid,
            "mc": mc_sid,
            "ayanamsa": "Lahiri"
        },
        "shadbala_virupas": {},
        "shadbala_rupas": {},
        "ishta_kashta_phala": {},
        "strength_summary": {},
        "relative_rank": {}
    }
    
    for p in PLANETS_LIST:
        pname = PLANET_NAMES[p]
        score = totals[p]
        output["shadbala_virupas"][pname] = round(score, 2)
        output["shadbala_rupas"][pname] = round(score / 60.0, 2)
        output["ishta_kashta_phala"][pname] = {
            "Ishta": round(phala[p]['Ishta'], 2),
            "Kashta": round(phala[p]['Kashta'], 2)
        }
        output["strength_summary"][pname] = "Strong" if score >= STRENGTH_THRESHOLDS[p] else "Weak"
        output["relative_rank"][pname] = ranks[p]
        output[f"{pname}_details"] = dict(sorted(details[p].items()))

    return output