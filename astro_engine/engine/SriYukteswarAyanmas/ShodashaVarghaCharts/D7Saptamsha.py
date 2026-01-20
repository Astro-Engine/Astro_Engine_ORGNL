import os
import math
import swisseph as swe
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Sri Yukteswar Ayanamsa
AYANAMSA_MODE = swe.SIDM_YUKTESHWAR

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": None # Calculated manually
}

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

# ==========================================
# 2. MATHEMATICAL LOGIC
# ==========================================

def decimal_to_dms(deg_float):
    """Converts decimal degrees to formatted string: D° M' S.SS"."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def normalize_degree(deg):
    """Ensure degree is between 0 and 360."""
    return deg % 360

def get_nakshatra_pada(longitude):
    """Calculates Nakshatra and Pada for a given 0-360 longitude."""
    # Nakshatra span = 13° 20' = 13.33333333 degrees
    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0
    
    nak_index = int(longitude / nak_span) % 27
    
    # Remainder degrees into the specific nakshatra
    rem_deg = longitude - (nak_index * nak_span)
    # Handle floating point edge cases
    if rem_deg < 0: rem_deg += nak_span
    
    pada = int(rem_deg / pada_span) + 1
    if pada > 4: pada = 4
    
    return NAKSHATRAS[nak_index], pada

def calculate_saptamsa_position(d1_deg_total):
    """
    Converts a D1 longitude to D7 (Saptamsa) longitude.
    Logic:
    1. Divide Sign into 7 parts (30 / 7 = 4.2857 deg per part).
    2. Odd Signs: Count from Sign itself.
    3. Even Signs: Count from 7th Sign from itself.
    """
    
    # 1. Get D1 Sign and Degree within Sign
    d1_sign_idx = int(d1_deg_total / 30) % 12
    d1_deg_in_sign = d1_deg_total % 30
    
    # 2. Determine which 'Part' (1-7) the planet is in
    # Part Size = 30 / 7
    part_size = 30.0 / 7.0
    part_index = int(d1_deg_in_sign / part_size) # 0 to 6
    if part_index >= 7: part_index = 6 # Safety cap
    
    # 3. Determine D7 Sign Index
    # Check if D1 Sign is Odd or Even
    # Aries(0) is Odd, Taurus(1) is Even.
    # So: if index is even number (0, 2, 4), it is an ODD sign (1st, 3rd, 5th).
    # If index is odd number (1, 3, 5), it is an EVEN sign (2nd, 4th, 6th).
    
    is_odd_sign = (d1_sign_idx % 2 == 0)
    
    if is_odd_sign:
        # Count from the sign itself
        d7_sign_idx = (d1_sign_idx + part_index) % 12
    else:
        # Count from the 7th sign from itself
        # 7th from X is (X + 6) index
        start_sign_idx = (d1_sign_idx + 6) % 12
        d7_sign_idx = (start_sign_idx + part_index) % 12
        
    # 4. Calculate Projected Degrees in D7
    # We expand the small D1 sector (4.28 deg) into a full 30 deg for D7 precision
    deg_in_part = d1_deg_in_sign - (part_index * part_size)
    d7_deg_in_sign = (deg_in_part / part_size) * 30.0
    
    # Total D7 Longitude (0-360)
    d7_total_long = (d7_sign_idx * 30) + d7_deg_in_sign
    
    return {
        "sign_idx": d7_sign_idx,
        "sign_name": ZODIAC_SIGNS[d7_sign_idx],
        "deg_in_sign": d7_deg_in_sign,
        "total_long": d7_total_long
    }

def get_whole_sign_house(planet_sign_idx, asc_sign_idx):
    """Calculates house 1-12 based on D7 Ascendant."""
    h = (planet_sign_idx - asc_sign_idx) + 1
    if h <= 0: h += 12
    return h

def perform_d7_calculation(data):
    """
    Main logic function used by the API.
    """
    # --- A. Parse Request ---
    user_name = data.get("user_name", "User")
    b_date = data.get("birth_date")
    b_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    
    # --- B. Initialize Swiss Ephemeris ---
    # Convert Local Time to UTC
    local_dt = datetime.strptime(f"{b_date} {b_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=tz)
    
    # Calculate Julian Day
    jul_day = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    )
    
    # Set Sri Yukteswar Ayanamsa
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day)
    
    # --- C. Calculate D1 Ascendant to get D7 Ascendant ---
    # Calculate D1 Ascendant
    cusps, ascmc = swe.houses_ex(jul_day, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    d1_asc_deg = ascmc[0]
    
    # Convert D1 Ascendant to D7 Ascendant
    d7_asc_data = calculate_saptamsa_position(d1_asc_deg)
    d7_asc_sign_idx = d7_asc_data['sign_idx']
    
    # Get Nakshatra for D7 Ascendant (Projected)
    asc_nak, asc_pada = get_nakshatra_pada(d7_asc_data['total_long'])
    
    # Prepare Response Structure
    response = {
        "user_name": user_name,
        "birth_details": {
            "birth_date": b_date,
            "birth_time": b_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "chart_type": "D7 Saptamsa",
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "house_system": "Whole Sign (Relative to D7 Lagna)",
            "calculation_rule": "Odd: Direct / Even: 7th from Sign"
        },
        "ascendant": {
            "sign": d7_asc_data['sign_name'],
            "degrees": decimal_to_dms(d7_asc_data['deg_in_sign']),
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "house": 1 # Ascendant is always 1st house
        },
        "planetary_positions": {}
    }
    
    # --- D. Calculate Planets in D7 ---
    for p_name, p_id in PLANETS.items():
        
        # 1. Get D1 Positions
        if p_name == "Ketu":
            # Ketu is Rahu + 180
            rahu_data = swe.calc_ut(jul_day, swe.MEAN_NODE, flags=swe.FLG_SIDEREAL)
            d1_long = normalize_degree(rahu_data[0][0] + 180)
            is_retro = True
        else:
            p_data = swe.calc_ut(jul_day, p_id, flags=swe.FLG_SIDEREAL)
            d1_long = p_data[0][0]
            speed = p_data[0][3]
            # Retrograde check (Nodes always R)
            is_retro = True if (p_name == "Rahu" or speed < 0) else False

        # 2. Convert to D7 Position
        d7_data = calculate_saptamsa_position(d1_long)
        
        # 3. Calculate House relative to D7 Ascendant
        house_num = get_whole_sign_house(d7_data['sign_idx'], d7_asc_sign_idx)
        
        # 4. Calculate Nakshatra based on D7 projected longitude
        nak, pada = get_nakshatra_pada(d7_data['total_long'])
        
        # 5. Add to Response
        response["planetary_positions"][p_name] = {
            "sign": d7_data['sign_name'],
            "degrees": decimal_to_dms(d7_data['deg_in_sign']),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": "R" if is_retro else ""
        }
        
    return response