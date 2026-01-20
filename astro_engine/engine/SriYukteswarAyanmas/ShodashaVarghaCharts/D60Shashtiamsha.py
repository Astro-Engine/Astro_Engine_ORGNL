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
# Using TRUE NODE (0) for Rahu/Ketu as it often aligns better with some software
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE, "Ketu": None # Calculated
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
    # Convert Local -> UT
    ut = (hr + (mn/60.0) + (sc/3600.0)) - float(tz_offset)
    return swe.julday(y, m, d, ut)

def get_nakshatra(deg):
    mins = deg * 60
    idx = int(mins / 800)
    nak = NAKSHATRAS[idx % 27]
    rem = mins % 800
    pada = int(rem / 200) + 1
    return nak, pada

def calc_d60(d1_abs_deg):
    """
    Parashara D60 Calculation
    1. Part = int(deg_in_sign * 2) + 1
    2. Sign = (D1_Sign + Part - 1) % 12
    3. Deity = Odd(Forward), Even(Reverse)
    """
    d1_sign_idx = int(d1_abs_deg / 30)
    d1_deg_in_sign = d1_abs_deg % 30
    
    # 1. Part (1-60)
    # 0.00-0.50 -> Part 1
    # 0.50-1.00 -> Part 2
    part = int(d1_deg_in_sign * 2) + 1
    
    # 2. D60 Sign (Count from Sign)
    # Start counting from the D1 sign. 
    # e.g., If D1 is Aries (0) and Part is 1, D60 is Aries.
    d60_sign_idx = (d1_sign_idx + (part - 1)) % 12
    
    # 3. D60 Degrees (0-30)
    # The progress within the 0.5 degree slice
    slice_deg = (d1_deg_in_sign * 2) % 1
    d60_deg = slice_deg * 30
    d60_abs_deg = (d60_sign_idx * 30) + d60_deg
    
    # 4. Deity
    # Odd Signs (0,2,4...): Forward (1 to 60)
    # Even Signs (1,3,5...): Reverse (60 to 1)
    is_odd = (d1_sign_idx % 2 == 0) # 0=Aries (Odd)
    
    if is_odd:
        deity_idx = part
    else:
        deity_idx = 61 - part
        
    return {
        "sign": ZODIAC_SIGNS[d60_sign_idx],
        "sign_idx": d60_sign_idx,
        "degrees": d60_deg,
        "abs_degrees": d60_abs_deg,
        "deity": D60_DEITIES.get(deity_idx, "Unknown")
    }

def perform_d60_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs D60 calculations, returns result dictionary.
    """
    if not data:
        raise ValueError("No data provided")
    
    # Handle Nested or Flat input
    inp = data.get("birth_details", data)
    
    # Parse inputs
    try:
        date = inp["birth_date"]
        time = inp["birth_time"]
        lat = float(inp["latitude"])
        lon = float(inp["longitude"])
        tz = float(inp["timezone_offset"])
        user = data.get("user_name", "Unknown")
    except KeyError as e:
        raise KeyError(f"Missing field: {str(e)}")

    # 1. Init Swiss Eph
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    jd = get_julian_day(date, time, tz)
    
    # 2. Calc Ascendant (D1)
    cusps, ascmc = swe.houses(jd, lat, lon, b'W')
    asc_d1 = ascmc[0]
    
    # 3. Calc D60 Asc
    d60_asc = calc_d60(asc_d1)
    asc_nak, asc_pada = get_nakshatra(d60_asc["abs_degrees"])
    
    # 4. Response Structure
    response = {
        "ascendant": {
            "sign": d60_asc["sign"],
            "degrees": to_dms(d60_asc["degrees"]),
            "deity": d60_asc["deity"],
            "nakshatra": asc_nak,
            "pada": asc_pada
        },
        "birth_details": inp,
        "notes": {
            "chart_type": "Shashtiamsha (D60)",
            "ayanamsa": "Sri Yukteswar",
            "calculation": "Parashara (Count from Sign)",
            "node_type": "True Node"
        },
        "planetary_positions": {},
        "user_name": user
    }
    
    # 5. Calc Planets
    plist = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    flags = swe.FLG_SIDEREAL
    
    for name in plist:
        pid = PLANETS[name]
        
        # Calc D1
        if name == "Ketu":
            # Ketu = Rahu + 180
            rahu = swe.calc_ut(jd, swe.TRUE_NODE, flags)[0][0]
            d1_deg = normalize(rahu + 180.0)
            retro = ""
        else:
            res = swe.calc_ut(jd, pid, flags)
            d1_deg = res[0][0]
            retro = "R" if res[0][3] < 0 else ""
        
        # Calc D60
        p_d60 = calc_d60(d1_deg)
        
        # House (Relative to D60 Asc)
        h = (p_d60["sign_idx"] - d60_asc["sign_idx"]) + 1
        if h <= 0: h += 12
        
        nak, pada = get_nakshatra(p_d60["abs_degrees"])
        
        response["planetary_positions"][name] = {
            "sign": p_d60["sign"],
            "degrees": to_dms(p_d60["degrees"]),
            "deity": p_d60["deity"],
            "house": h,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": retro,
            # Debug Info: Helpful to verify why D60 is calculated this way
            "d1_longitude": to_dms(d1_deg) 
        }
        
    return response