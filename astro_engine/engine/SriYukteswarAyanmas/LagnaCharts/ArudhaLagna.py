import os
import math
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHEMERIS_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHEMERIS_PATH)

# ==========================================
# CONSTANTS
# ==========================================
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_MAP = {
    0: "Sun", 1: "Moon", 2: "Mercury", 3: "Venus", 4: "Mars", 
    5: "Jupiter", 6: "Saturn", 10: "Rahu", 11: "Ketu"
}

# Rulerships for Arudha Logic
RULERS = {
    0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 2, 6: 3, 
    7: [4, 11], # Scorpio: Mars/Ketu
    8: 5, 9: 6, 
    10: [6, 10], # Aquarius: Saturn/Rahu
    11: 5
}

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def to_dms_string(deg_float):
    """Formats float degrees to D° M' S.SS" string."""
    d = int(deg_float)
    mins = int((deg_float - d) * 60)
    secs = ((deg_float - d) * 60 - mins) * 60
    return f"{d}° {mins}' {secs:.2f}\""

def get_nakshatra_pada(lon):
    """Calculates Nakshatra and Pada from longitude."""
    # Normalize lon to 0-360
    lon = lon % 360
    # One Nakshatra = 13 degrees 20 minutes = 13.3333... degrees
    nak_len = 360.0 / 27.0
    nak_index = int(lon / nak_len)
    
    # Remainder degrees in current nakshatra
    rem_deg = lon - (nak_index * nak_len)
    
    # One Pada = 3 degrees 20 minutes = 3.3333... degrees
    pada_len = nak_len / 4.0
    pada = int(rem_deg / pada_len) + 1
    
    return NAKSHATRAS[nak_index], pada

def get_sign_info(lon):
    """Returns sign index, name, and degree within sign."""
    lon = lon % 360
    idx = int(lon // 30)
    deg_in_sign = lon % 30
    return idx, ZODIAC_SIGNS[idx], deg_in_sign

def to_decimal_hours(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h + m/60.0 + s/3600.0

# ==========================================
# CORE CALCULATION LOGIC
# ==========================================

def calculate_planets_and_ascendant(jd_et, lat, lon):
    """
    Calculates raw positions for Planets and Ascendant using Sri Yukteswar Ayanamsa.
    """
    # 1. Set Ayanamsa to Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    positions = {}
    
    # Planets Sun(0) to Saturn(6) + Rahu(10)
    p_ids = [0, 1, 2, 3, 4, 5, 6, 10]
    
    for pid in p_ids:
        flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
        xx, _ = swe.calc_ut(jd_et, pid, flags)
        
        long_deg = xx[0]
        speed = xx[3]
        
        sign_idx, sign_name, deg_in_sign = get_sign_info(long_deg)
        nak_name, pada = get_nakshatra_pada(long_deg)
        
        positions[pid] = {
            "name": PLANET_MAP[pid],
            "id": pid,
            "full_degree": long_deg,
            "deg_in_sign": deg_in_sign,
            "sign_index": sign_idx,
            "sign": sign_name,
            "nakshatra": nak_name,
            "pada": pada,
            "retrograde": "R" if speed < 0 else "" # Format matches sample
        }

    # Calculate Ketu (opposite Rahu)
    rahu = positions[10]
    ketu_lon = (rahu['full_degree'] + 180) % 360
    k_sign_idx, k_sign_name, k_deg_in_sign = get_sign_info(ketu_lon)
    k_nak, k_pada = get_nakshatra_pada(ketu_lon)
    
    positions[11] = {
        "name": "Ketu",
        "id": 11,
        "full_degree": ketu_lon,
        "deg_in_sign": k_deg_in_sign,
        "sign_index": k_sign_idx,
        "sign": k_sign_name,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "" # Nodes usually treated as always retro, but sample leaves Ketu blank often or R. Matching Rahu usually.
    }
    
    # Calculate Ascendant
    # Use 'P' to get accurate cusp 1, then convert to Whole Sign logic manually
    h_cusps, ascmc = swe.houses_ex(jd_et, float(lat), float(lon), b'P', swe.FLG_SIDEREAL)
    asc_lon = ascmc[0]
    asc_sign_idx, asc_sign_name, asc_deg_in_sign = get_sign_info(asc_lon)
    asc_nak, asc_pada = get_nakshatra_pada(asc_lon)
    
    ascendant = {
        "full_degree": asc_lon,
        "deg_in_sign": asc_deg_in_sign,
        "sign_index": asc_sign_idx,
        "sign": asc_sign_name,
        "nakshatra": asc_nak,
        "pada": asc_pada
    }
    
    return positions, ascendant

# ==========================================
# ARUDHA CALCULATION LOGIC
# ==========================================

def get_planet_count_in_sign(sign_idx, positions):
    count = 0
    for pid in positions:
        if positions[pid]['sign_index'] == sign_idx:
            count += 1
    return count

def resolve_dual_lord_strength(sign_idx, positions):
    """Determines stronger lord for Scorpio (4 vs 11) and Aquarius (6 vs 10)."""
    if sign_idx == 7: # Scorpio
        p1, p2 = 4, 11
    elif sign_idx == 10: # Aquarius
        p1, p2 = 6, 10
    else:
        return RULERS[sign_idx]
        
    # 1. Conjunction Strength
    c1 = get_planet_count_in_sign(positions[p1]['sign_index'], positions)
    c2 = get_planet_count_in_sign(positions[p2]['sign_index'], positions)
    
    if c1 > c2: return p1
    if c2 > c1: return p2
    
    # 2. Degree Strength (Tie-breaker)
    if positions[p1]['deg_in_sign'] >= positions[p2]['deg_in_sign']:
        return p1
    return p2

def calculate_arudha_lagna_sign(asc_idx, positions):
    # 1. Get Lord
    if asc_idx in [7, 10]:
        lord_id = resolve_dual_lord_strength(asc_idx, positions)
    else:
        lord_id = RULERS[asc_idx]
        
    lord_sign_idx = positions[lord_id]['sign_index']
    
    # 2. Distance (Lagna to Lord)
    dist = (lord_sign_idx - asc_idx) % 12
    
    # 3. Raw Arudha (Lord + Distance)
    arudha_idx = (lord_sign_idx + dist) % 12
    
    # 4. Exceptions
    # If AL is in 1st (same as Lagna), shift to 10th
    if arudha_idx == asc_idx:
        arudha_idx = (asc_idx + 9) % 12
    # If AL is in 7th, shift to 4th
    elif arudha_idx == (asc_idx + 6) % 12:
        arudha_idx = (asc_idx + 3) % 12
        
    return arudha_idx

def perform_arudha_calculation(data):
    """
    Main logic function used by the API.
    """
    # Parse Input
    uname = data.get('user_name')
    bdate = data.get('birth_date')
    btime = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 1. Time Calculation
    y, m, d = map(int, bdate.split('-'))
    h_dec = to_decimal_hours(btime)
    h_gmt = h_dec - tz
    jd_ut = swe.julday(y, m, d, h_gmt)
    delta_t = swe.deltat(jd_ut)
    jd_et = jd_ut + delta_t
    
    # 2. Get Raw Positions & Ascendant (Sri Yukteswar)
    positions, ascendant = calculate_planets_and_ascendant(jd_et, lat, lon)
    
    # 3. Calculate Arudha Lagna (AL) Index
    al_sign_idx = calculate_arudha_lagna_sign(ascendant['sign_index'], positions)
    
    # 4. Format "ascendant" Block
    # NOTE: The 'ascendant' block usually describes the Physical Ascendant (Lagna).
    # The 'house' calculation for planets will be relative to AL.
    asc_output = {
        "degrees": to_dms_string(ascendant['deg_in_sign']),
        "nakshatra": ascendant['nakshatra'],
        "pada": ascendant['pada'],
        "sign": ZODIAC_SIGNS[al_sign_idx] # This returns the AL Sign name, effectively setting AL as Lagna
    }
    
    # 5. Format "planetary_positions" Block (Houses relative to AL)
    planets_output = {}
    sorted_pids = [0, 1, 4, 2, 5, 3, 6, 10, 11] # Sun, Moon, Mars, Mer, Jup, Ven, Sat, Rahu, Ketu
    
    for pid in sorted_pids:
        p = positions[pid]
        p_name = p['name']
        
        # House Calculation Relative to Arudha Lagna (Whole Sign)
        # If AL is Aries (0) and Planet is Aries (0) -> House 1
        # If AL is Aries (0) and Planet is Taurus (1) -> House 2
        # Formula: (Planet_Sign - AL_Sign) + 1
        house_num = (p['sign_index'] - al_sign_idx) % 12 + 1
        
        planets_output[p_name] = {
            "degrees": to_dms_string(p['deg_in_sign']),
            "house": house_num,
            "nakshatra": p['nakshatra'],
            "pada": p['pada'],
            "retrograde": p['retrograde'],
            "sign": p['sign']
        }

    # 6. Format Final Response
    # Get Ayanamsa Value
    ayanamsa_val_float = swe.get_ayanamsa_ut(jd_ut)
    
    response = {
        "ascendant": asc_output,
        "birth_details": {
            "birth_date": bdate,
            "birth_time": btime,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val_float:.6f}",
            "chart_type": "Arudha Lagna",
            "arudha_lagna_sign": ZODIAC_SIGNS[al_sign_idx],
            "house_system": "Whole Sign (Relative to AL)"
        },
        "planetary_positions": planets_output,
        "user_name": uname
    }
    
    return response