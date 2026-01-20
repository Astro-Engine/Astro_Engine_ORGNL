import os
import swisseph as swe

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# CORE CALCULATION LOGIC
# ---------------------------------------------------------

def decimal_to_dms(deg_decimal):
    """Formats decimal degrees to D° M' S.SS" string."""
    d = int(deg_decimal)
    m_float = (deg_decimal - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(lon_decimal):
    """
    Returns Nakshatra name and Pada based on D1 longitude.
    Nakshatras are fixed to the ecliptic, so we usually report 
    the original Nakshatra even in divisional charts.
    """
    lon = lon_decimal % 360
    nak_span = 13.333333333333334 # 13 deg 20 min
    
    nak_index = int(lon / nak_span)
    nak_name = NAKSHATRAS[nak_index % 27]
    
    rem_deg = lon - (nak_index * nak_span)
    pada_span = 3.3333333333333335 # 3 deg 20 min
    pada = int(rem_deg / pada_span) + 1
    
    return nak_name, pada

def calculate_d16_components(lon_decimal):
    """
    Calculates D16 specific data:
    1. D16 Sign Index & Name
    2. D16 Localized Longitude (0-30 degrees within that D16 sign)
    """
    # D1 Constants
    d1_sign_idx = int((lon_decimal % 360) / 30)
    deg_in_sign = (lon_decimal % 360) % 30
    
    # D16 Calculation
    # Span of one D16 part = 30 / 16 = 1.875 degrees
    d16_span = 1.875
    
    # Which part (0 to 15) is the planet in?
    part_index = int(deg_in_sign / d16_span)
    
    # Calculate D16 Local Degree
    # How far into this specific part are we? 
    # We expand the remainder to a full 30 degrees.
    rem_deg = deg_in_sign - (part_index * d16_span)
    d16_local_deg = (rem_deg / d16_span) * 30.0
    
    # Determine D16 Sign based on Modality (Parashara)
    modality = d1_sign_idx % 3
    
    if modality == 0:   # Movable (Aries start) -> Index 0
        start_idx = 0
    elif modality == 1: # Fixed (Leo start) -> Index 4
        start_idx = 4
    else:               # Dual (Sag start) -> Index 8
        start_idx = 8
        
    d16_sign_idx = (start_idx + part_index) % 12
    d16_sign_name = ZODIAC_SIGNS[d16_sign_idx]
    
    return d16_sign_idx, d16_sign_name, d16_local_deg

def get_whole_sign_house(planet_sign_idx, asc_sign_idx):
    """Calculates Whole Sign House (1-12)."""
    return (planet_sign_idx - asc_sign_idx + 12) % 12 + 1

def perform_d16_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all D16 calculations, returns result dictionary.
    """
    # 1. Parse Input
    user_name = data.get("user_name", "Unknown")
    date_str = data.get("birth_date")
    time_str = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz_offset = float(data.get("timezone_offset"))

    # 2. Time Conversion (UTC)
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    decimal_time = hour + (minute / 60.0) + (second / 3600.0)
    utc_decimal_time = decimal_time - tz_offset
    jul_day_ut = swe.julday(year, month, day, utc_decimal_time)
    
    # 3. Configure Ayanamsa: Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 4. Calculate Ascendant (Lagna) in D1
    # We need D1 Ascendant to calculate D16 Ascendant
    cusps, ascmc = swe.houses_ex(jul_day_ut, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    asc_d1_lon = ascmc[0]
    
    # Calculate D16 Ascendant
    asc_d16_idx, asc_d16_sign, asc_d16_deg = calculate_d16_components(asc_d1_lon)
    asc_nak, asc_pada = get_nakshatra(asc_d1_lon)
    
    # 5. Process Planets
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }
    
    planetary_positions = {}
    
    for p_name, p_id in planets_map.items():
        # Get D1 Longitude
        res = swe.calc_ut(jul_day_ut, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        p_lon = res[0][0]
        p_speed = res[0][3]
        is_retro = "R" if p_speed < 0 else ""
        
        # Calculate D16 Data
        # Note: We pass the D1 longitude, the function converts it to D16
        p_d16_idx, p_d16_sign, p_d16_deg = calculate_d16_components(p_lon)
        
        # Calculate House (Relative to D16 Ascendant)
        house = get_whole_sign_house(p_d16_idx, asc_d16_idx)
        
        # Nakshatra (Based on D1, standard practice)
        nak, pada = get_nakshatra(p_lon)
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms(p_d16_deg), # Localized D16 Degree
            "house": house,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": p_d16_sign # D16 Sign
        }
        
    # 6. Process Ketu
    # Recalculate Rahu D1 Lon
    rahu_res = swe.calc_ut(jul_day_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    rahu_lon = rahu_res[0][0]
    ketu_lon = (rahu_lon + 180) % 360
    
    k_d16_idx, k_d16_sign, k_d16_deg = calculate_d16_components(ketu_lon)
    k_house = get_whole_sign_house(k_d16_idx, asc_d16_idx)
    k_nak, k_pada = get_nakshatra(ketu_lon)
    
    planetary_positions["Ketu"] = {
        "degrees": decimal_to_dms(k_d16_deg),
        "house": k_house,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "R",
        "sign": k_d16_sign
    }

    # 7. Response Construction
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day_ut)
    
    response = {
        "ascendant": {
            "degrees": decimal_to_dms(asc_d16_deg), # Localized D16 Degree
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "sign": asc_d16_sign
        },
        "birth_details": {
            "birth_date": date_str,
            "birth_time": time_str,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz_offset
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val:.6f}",
            "chart_type": "D16 (Shodashamsha)",
            "house_system": "Whole Sign (Calculated from D16 Ascendant)"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }
    
    return response