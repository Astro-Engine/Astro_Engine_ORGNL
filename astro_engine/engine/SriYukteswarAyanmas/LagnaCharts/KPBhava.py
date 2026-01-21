import os
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

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

PLANET_MAPPING = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE, "Ketu": None,
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def decimal_to_dms(deg_float):
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_data(longitude):
    lon = longitude % 360
    nak_duration = 13.333333333333334
    nak_index = int(lon / nak_duration)
    rem_deg = lon - (nak_index * nak_duration)
    pada_duration = 3.3333333333333335
    pada = int(rem_deg / pada_duration) + 1
    if nak_index >= len(NAKSHATRAS): nak_index = 0
    return {"name": NAKSHATRAS[nak_index], "id": nak_index + 1, "pada": pada}

def get_sign_data(longitude):
    lon = longitude % 360
    sign_index = int(lon / 30)
    norm_degree = lon % 30
    return {"index": sign_index, "name": ZODIAC_SIGNS[sign_index], "norm_degree": norm_degree}

def get_placidus_house(planet_lon, cusps):
    """
    Determines the House (1-12) based on Placidus Cusp Ranges.
    cusps: list of 13 floats (index 0 is None, 1-12 are cusps, 13 is cusp 1 again)
    """
    p_lon = planet_lon % 360
    
    for i in range(1, 13):
        low = cusps[i]
        high = cusps[i+1] # The start of the NEXT house
        
        # Normal Case: House range doesn't cross 360 (e.g., 10° to 40°)
        if low < high:
            if low <= p_lon < high:
                return i
        # Crossing Case: House range crosses 360 (e.g., 350° to 20°)
        else:
            if p_lon >= low or p_lon < high:
                return i
                
    return 1 # Fallback, though logical coverage should be 100%

def perform_chart_calculation_kp(data):
    """
    Main Logic Function.
    Receives input dictionary, performs calculations, returns result dictionary.
    """
    # 1. Parse Input
    user_name = data.get('user_name', 'User')
    dob, tob = data['birth_date'], data['birth_time']
    lat, lon, tz = float(data['latitude']), float(data['longitude']), float(data['timezone_offset'])
    
    year, month, day = map(int, dob.split('-'))
    hour, minute, second = map(int, tob.split(':'))
    
    # 2. Time Conversion
    decimal_hour = hour + (minute / 60.0) + (second / 3600.0)
    decimal_hour_utc = decimal_hour - tz
    jd_ut = swe.julday(year, month, day, decimal_hour_utc)
    
    # 3. Get Sri Yukteswar Ayanamsa Value
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)
    
    # 4. Calculate Placidus Cusps (Manual Subtraction Method)
    # Turn off sidereal mode to get Tropical Cusps
    swe.set_sid_mode(0) 
    
    # 'P' for Placidus System
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, b'P')
    
    # Convert Tropical Cusps to Sidereal (Sri Yukteswar)
    # We create a list where index 1 is House 1, etc.
    sidereal_cusps = [0.0] * 14 # Index 0 unused, 1-12 used, 13 is wrap
    
    for i in range(1, 13):
        # cusps_trop is 0-indexed tuple, so House 1 is at index 0
        trop_deg = cusps_trop[i-1]
        sid_deg = (trop_deg - ayanamsa_val) % 360
        sidereal_cusps[i] = sid_deg
        
    # Add Cusp 1 again at the end to handle the loop (House 12 ends at Cusp 1)
    sidereal_cusps[13] = sidereal_cusps[1]
    
    # Ascendant is Cusp 1
    asc_deg = sidereal_cusps[1]
    asc_sign = get_sign_data(asc_deg)
    asc_nak = get_nakshatra_data(asc_deg)
    
    ascendant_response = {
        "sign": asc_sign['name'],
        "degrees": decimal_to_dms(asc_sign['norm_degree']),
        "nakshatra": asc_nak['name'],
        "pada": asc_nak['pada']
    }
    
    # 5. Calculate Planets (Sidereal Mode ON)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    calc_flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    
    planetary_positions = {}
    
    for p_name, p_id in PLANET_MAPPING.items():
        
        # --- Ketu Logic ---
        if p_name == "Ketu":
            rahu_deg = planetary_positions["Rahu"]["absolute_degrees"]
            ketu_lon = (rahu_deg + 180.0) % 360
            
            k_sign = get_sign_data(ketu_lon)
            k_nak = get_nakshatra_data(ketu_lon)
            k_house = get_placidus_house(ketu_lon, sidereal_cusps)
            
            planetary_positions["Ketu"] = {
                "degrees": decimal_to_dms(k_sign['norm_degree']),
                "absolute_degrees": ketu_lon,
                "retrograde": "R",
                "sign": k_sign['name'],
                "house": k_house,
                "nakshatra": k_nak['name'],
                "pada": k_nak['pada']
            }
            continue
            
        # --- Planet Logic ---
        result = swe.calc_ut(jd_ut, p_id, calc_flags)
        p_lon = result[0][0]
        p_speed = result[0][3]
        is_retro = "R" if p_speed < 0 else ""
        
        p_sign = get_sign_data(p_lon)
        p_nak = get_nakshatra_data(p_lon)
        
        # Use Placidus House Logic
        p_house = get_placidus_house(p_lon, sidereal_cusps)
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms(p_sign['norm_degree']),
            "absolute_degrees": p_lon,
            "retrograde": is_retro,
            "sign": p_sign['name'],
            "house": p_house,
            "nakshatra": p_nak['name'],
            "pada": p_nak['pada']
        }

    # 6. Response
    response = {
        "user_name": user_name,
        "birth_details": {
            "birth_date": dob, "birth_time": tob,
            "latitude": lat, "longitude": lon, "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": decimal_to_dms(ayanamsa_val),
            "chart_type": "KP Bhava",
            "house_system": "Placidus (KP)"
        },
        "ascendant": ascendant_response,
        "planetary_positions": planetary_positions,
        # Optional: Return cusp degrees for verification
        "bhava_cusps": { i: decimal_to_dms(sidereal_cusps[i]) for i in range(1, 13) }
    }
    
    return response