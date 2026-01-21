import os
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Ayanamsa: Sri Yukteswar (Swiss Eph Mode 7)
AYANAMSA_MODE = swe.SIDM_YUKTESHWAR

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Standard Parasara D60 Deities
D60_DEITIES = {
    1: "Ghora", 2: "Rakshasa", 3: "Deva", 4: "Kubera", 5: "Yaksha",
    6: "Kinnara", 7: "Bhrashta", 8: "Kulaghna", 9: "Garala", 10: "Vahni",
    11: "Maya", 12: "Purishaka", 13: "Apampati", 14: "Marutwan", 15: "Kaala",
    16: "Sarpa", 17: "Amrita", 18: "Indu", 19: "Mridu", 20: "Komala",
    21: "Heramba", 22: "Brahma", 23: "Vishnu", 24: "Maheshwara", 25: "Deva",
    26: "Ardra", 27: "Kalinasana", 28: "Kshitishwara", 29: "Kamalakara", 30: "Gulika",
    31: "Mrityu", 32: "Kaala", 33: "Davagni", 34: "Ghora", 35: "Yama",
    36: "Kantaka", 37: "Sudha", 38: "Amrita", 39: "Purnachandra", 40: "Vishadagdha",
    41: "Kulanasa", 42: "Vamshakshaya", 43: "Utpata", 44: "Kaala", 45: "Saumya",
    46: "Komala", 47: "Sheetala", 48: "Karaladamshtra", 49: "Chandramukhi", 50: "Praveena",
    51: "Kalapavaka", 52: "Dandayudha", 53: "Nirmala", 54: "Saumya", 55: "Krura",
    56: "Atisheetala", 57: "Sudha", 58: "Payodhi", 59: "Bhramana", 60: "Indurekha"
}

# Planet Constants
# Use TRUE NODE for Rahu/Ketu
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE, "Ketu": None 
}

# ==========================================
# UTILS
# ==========================================

def to_dms(deg):
    d = int(deg)
    rem = (deg - d) * 60
    m = int(rem)
    s = round((rem - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def normalize(deg):
    while deg < 0: deg += 360
    while deg >= 360: deg -= 360
    return deg

def get_julian_day(date_str, time_str, tz_offset):
    y, m, d = map(int, date_str.split('-'))
    hr, mn, sc = map(int, time_str.split(':'))
    # Convert Local Time -> Universal Time (UT)
    ut = (hr + (mn/60.0) + (sc/3600.0)) - float(tz_offset)
    return swe.julday(y, m, d, ut)

def get_nakshatra(deg):
    """Calculates Nakshatra based on absolute longitude (0-360)"""
    mins = deg * 60
    idx = int(mins / 800) # 800 mins per Nakshatra (13 deg 20 min)
    nak = NAKSHATRAS[idx % 27]
    rem = mins % 800
    pada = int(rem / 200) + 1
    return nak, pada

def calc_d60(d1_abs_deg):
    """
    Parashara D60 Calculation Rules:
    1. Division: Each sign (30 deg) divided into 60 parts of 0.5 deg (30 mins).
    2. Counting: 
       - Odd Signs (Aries, Gemini...): Count Forward (1 to 60)
       - Even Signs (Taurus, Cancer...): Count Reverse (60 to 1)
       - The Sign logic: Start counting FROM the D1 sign.
    """
    d1_sign_idx = int(d1_abs_deg / 30)
    d1_deg_in_sign = d1_abs_deg % 30
    
    # Rule 1: Determine the Part (1 to 60)
    part = int(d1_deg_in_sign * 2) + 1
    
    # Rule 2: Determine D60 Sign Placement
    d60_sign_idx = (d1_sign_idx + (part - 1)) % 12
    
    # Rule 3: Determine D60 Degrees (0-30 relative to D60 sign)
    slice_deg = (d1_deg_in_sign * 2) % 1
    d60_deg = slice_deg * 30
    d60_abs_deg = (d60_sign_idx * 30) + d60_deg
    
    # Rule 4: Determine the Deity (Amsha Ruler)
    is_odd_sign = (d1_sign_idx % 2 == 0) 
    
    if is_odd_sign:
        deity_idx = part
    else:
        deity_idx = 61 - part
        
    return {
        "sign": ZODIAC_SIGNS[d60_sign_idx],
        "sign_idx": d60_sign_idx,
        "degrees": d60_deg,
        "abs_degrees": d60_abs_deg,
        "deity": D60_DEITIES.get(deity_idx, "Unknown"),
        "part_num": part 
    }

def perform_d60_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all D60 calculations, returns result dictionary.
    """
    if not data:
        raise ValueError("No data provided")
        
    # Normalize input structure
    inp = data.get("birth_details", data)
    
    try:
        date = inp["birth_date"]
        time = inp["birth_time"]
        lat = float(inp["latitude"])
        lon = float(inp["longitude"])
        tz = float(inp["timezone_offset"])
        user = data.get("user_name", "Unknown")
    except KeyError as e:
        raise KeyError(f"Missing field: {str(e)}")

    # 1. Initialize Ayanamsa
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    
    # 2. Get Julian Day (UT)
    jd = get_julian_day(date, time, tz)
    
    # ---------------------------------------------------------
    # THE FIX: TOPOCENTRIC ASCENDANT CALCULATION
    # ---------------------------------------------------------
    # We must set the observer's location (Topo) to get the exact Ascendant.
    swe.set_topo(lon, lat, 0) # 0 altitude (sea level default)
    
    # Use houses_ex with FLG_TOPOCTR
    flags_asc = swe.FLG_SIDEREAL | swe.FLG_TOPOCTR
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags_asc)
    
    asc_d1_deg = ascmc[0] # The exact Topocentric Ascendant
    
    # Calculate D60 Ascendant
    d60_asc = calc_d60(asc_d1_deg)
    asc_nak, asc_pada = get_nakshatra(d60_asc["abs_degrees"])
    
    # ---------------------------------------------------------
    # PLANETARY CALCULATIONS
    # ---------------------------------------------------------
    # Using Geocentric for planets to maintain your existing perfect match
    flags_planet = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    planetary_positions = {}
    plist = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for name in plist:
        pid = PLANETS[name]
        
        d1_deg = 0.0
        is_retro = False
        
        if name == "Ketu":
            # Ketu is always Rahu + 180
            rahu_res = swe.calc_ut(jd, swe.TRUE_NODE, flags_planet)
            d1_deg = normalize(rahu_res[0][0] + 180.0)
            # Ketu retrograde status follows Rahu
            is_retro = (rahu_res[0][3] < 0) 
        else:
            res = swe.calc_ut(jd, pid, flags_planet)
            d1_deg = res[0][0]
            is_retro = (res[0][3] < 0)
        
        # Calculate D60 Position
        p_d60 = calc_d60(d1_deg)
        
        # Calculate House relative to D60 Ascendant (Whole Sign)
        h = (p_d60["sign_idx"] - d60_asc["sign_idx"]) + 1
        if h <= 0: h += 12
        
        # Get "D60 Nakshatra" (Projection)
        p_nak, p_pada = get_nakshatra(p_d60["abs_degrees"])
        
        planetary_positions[name] = {
            "sign": p_d60["sign"],
            "degrees": to_dms(p_d60["degrees"]),
            "deity": p_d60["deity"],
            "house": h,
            "nakshatra": p_nak,
            "pada": p_pada,
            "retrograde": "R" if is_retro else "",
            # Debug info to verify D1 input matches
            "d1_longitude_deg": round(d1_deg, 6) 
        }
        
    # Response Construction
    response = {
        "user_name": user,
        "birth_details": inp,
        "notes": {
            "chart_type": "Shashtiamsha (D60)",
            "ayanamsa": "Sri Yukteswar",
            "calculation_mode": "Topocentric Ascendant / Geocentric Planets",
            "deity_rule": "Parashara (Odd=Fwd, Even=Rev)"
        },
        "ascendant": {
            "sign": d60_asc["sign"],
            "degrees": to_dms(d60_asc["degrees"]),
            "deity": d60_asc["deity"],
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "d1_longitude_deg": round(asc_d1_deg, 6) 
        },
        "planetary_positions": planetary_positions
    }
    
    return response