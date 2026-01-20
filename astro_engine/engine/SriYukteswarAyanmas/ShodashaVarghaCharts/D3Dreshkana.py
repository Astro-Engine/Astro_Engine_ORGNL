import os
import math
import swisseph as swe

# ==========================================
# 1. CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# 2. CONSTANTS
# ==========================================
SIGNS = [
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

PLANET_MAP = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
}

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def decimal_to_dms(deg_float):
    """Converts decimal degrees to formatted string."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(lon):
    """
    Returns Nakshatra based on D1 longitude.
    """
    normalized_lon = lon % 360
    nak_len = 360 / 27
    index = int(normalized_lon / nak_len)
    fraction = normalized_lon % nak_len
    pada = int(fraction / (nak_len / 4)) + 1
    if index >= 27: index = 0
    return NAKSHATRAS[index], pada

def calculate_d3_data(d1_lon_deg):
    """
    CONVERTS D1 LONGITUDE TO D3 SIGN & DEGREE
    Rule (Parashara):
    0-10 deg: 1st Drekkana (Starts at Sign itself)
    10-20 deg: 2nd Drekkana (Starts at 5th from Sign)
    20-30 deg: 3rd Drekkana (Starts at 9th from Sign)
    """
    # 1. Identify D1 Sign and Degree
    d1_sign_idx = int(d1_lon_deg // 30)
    d1_deg_in_sign = d1_lon_deg % 30
    
    # 2. Determine Decan (1, 2, or 3)
    if d1_deg_in_sign < 10:
        jump = 0
        remainder = d1_deg_in_sign
    elif d1_deg_in_sign < 20:
        jump = 4  # +4 signs to reach the 5th
        remainder = d1_deg_in_sign - 10
    else:
        jump = 8  # +8 signs to reach the 9th
        remainder = d1_deg_in_sign - 20
        
    # 3. Calculate D3 Sign
    d3_sign_idx = (d1_sign_idx + jump) % 12
    
    # 4. Calculate D3 Degree (Expansion)
    # Each 10 degrees of D1 maps to 30 degrees of D3
    d3_deg_value = remainder * 3
    
    return d3_sign_idx, d3_deg_value

def get_whole_sign_house(planet_sign_idx, asc_sign_idx):
    """Calculates Whole Sign House Number."""
    return (planet_sign_idx - asc_sign_idx + 12) % 12 + 1

def perform_d3_calculation(data):
    """
    Main logic function used by the API.
    """
    # --- A. Parse Input ---
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    year, month, day = map(int, birth_date.split('-'))
    h, m, s = map(int, birth_time.split(':'))
    
    # --- B. Time Calculation ---
    decimal_local = h + (m / 60.0) + (s / 3600.0)
    decimal_ut = decimal_local - tz
    jd_ut = swe.julday(year, month, day, decimal_ut)
    
    # --- C. Configure Ayanamsa (Sri Yukteswar) ---
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)
    
    # --- D. Calculate Ascendant (Convert to D3) ---
    # 1. Get D1 Ascendant
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, b'P')
    asc_deg_d1 = (ascmc_trop[0] - ayanamsa_val) % 360
    
    # 2. Convert to D3 Ascendant
    asc_d3_sign_idx, asc_d3_deg = calculate_d3_data(asc_deg_d1)
    
    # 3. Get Nakshatra (of D1 position usually, or use Asc D1 lon)
    asc_nak_name, asc_nak_pada = get_nakshatra(asc_deg_d1)
    
    asc_data = {
        "degrees": decimal_to_dms(asc_d3_deg), # Using D3 expansion degrees
        "nakshatra": asc_nak_name,
        "pada": asc_nak_pada,
        "sign": SIGNS[asc_d3_sign_idx]
    }
    
    # --- E. Calculate Planetary Positions (Convert to D3) ---
    planetary_positions = {}
    calc_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    # Prepare list (Planets + Ketu)
    raw_planets = []
    for p_name, p_id in PLANET_MAP.items():
        xx, _ = swe.calc_ut(jd_ut, p_id, calc_flags)
        raw_planets.append({"name": p_name, "lon": xx[0], "speed": xx[3]})
        
    # Add Ketu
    rahu = next(p for p in raw_planets if p["name"] == "Rahu")
    raw_planets.append({"name": "Ketu", "lon": (rahu["lon"] + 180) % 360, "speed": rahu["speed"]})

    # Process Each Planet
    for p in raw_planets:
        d1_lon = p["lon"]
        
        # 1. Convert to D3 Coordinates
        d3_sign_idx, d3_deg = calculate_d3_data(d1_lon)
        
        # 2. Calculate D3 House (Relative to D3 Ascendant)
        house_num = get_whole_sign_house(d3_sign_idx, asc_d3_sign_idx)
        
        # 3. Other Details
        nak_name, nak_pada = get_nakshatra(d1_lon) # Nakshatra stays with D1 lon
        is_retro = "R" if p["speed"] < 0 else ""
        
        planetary_positions[p["name"]] = {
            "degrees": decimal_to_dms(d3_deg),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": nak_pada,
            "retrograde": is_retro,
            "sign": SIGNS[d3_sign_idx]
        }

    # --- F. Construct Final JSON Response ---
    response = {
        "ascendant": asc_data,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val:.6f}",
            "chart_type": "D3 (Drekkana)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": dict(sorted(planetary_positions.items())),
        "user_name": user_name
    }
    
    return response