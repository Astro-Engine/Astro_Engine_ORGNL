import os
import math
import datetime
import swisseph as swe

# =================================================================================
# CONFIGURATION
# =================================================================================
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# =================================================================================
# UTILITIES
# =================================================================================

def decimal_to_dms(deg_float):
    """Converts decimal degrees to Degrees:Minutes:Seconds string."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def normalize_degree(deg):
    """Normalizes angle to 0-360 range."""
    while deg < 0:
        deg += 360
    while deg >= 360:
        deg -= 360
    return deg

def get_julian_day(date_str, time_str, tz_offset):
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    
    dt_local = datetime.datetime(year, month, day, hour, minute, second)
    decimal_hours_offset = float(tz_offset)
    # Subtract offset to get UTC
    dt_utc = dt_local - datetime.timedelta(hours=decimal_hours_offset)
    
    jd_ut = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )
    return jd_ut

def get_rashi_details(longitude):
    """Returns Sign Name and Sign Index (0-11) for a given longitude."""
    rashis = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio", 
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_index = int(longitude / 30)
    return sign_index, rashis[sign_index % 12]

def get_nakshatra_details(longitude):
    """Calculates Nakshatra and Pada for a given longitude."""
    # 27 Nakshatras, each 13° 20' (13.3333 degrees)
    nakshatra_list = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
        "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
        "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    # 13 degrees 20 minutes = 13.3333... degrees
    nak_duration = 13.333333333333334
    
    nak_index = int(longitude / nak_duration)
    nak_name = nakshatra_list[nak_index % 27]
    
    # Calculate Pada (Quarter)
    # Each Nakshatra has 4 padas. 
    # Find how far into the nakshatra we are
    deg_in_nak = longitude % nak_duration
    # Each pada is 3° 20' = 3.3333... degrees
    pada_duration = 3.3333333333333335
    pada = int(deg_in_nak / pada_duration) + 1
    
    return nak_name, pada

# =================================================================================
# D27 LOGIC
# =================================================================================

def calculate_d27_longitude(d1_lon_sidereal):
    """
    Calculates the exact projected longitude in the D27 chart.
    """
    # 1. Get D1 Sign and Degree
    d1_sign_index = int(d1_lon_sidereal / 30)
    d1_degree = d1_lon_sidereal % 30
    
    # 2. Determine Element of D1 Sign (0=Fire, 1=Earth, 2=Air, 3=Water)
    element_remainder = d1_sign_index % 4
    
    # 3. Determine Starting Sign for D27 count
    if element_remainder == 0:   # Fire
        start_sign_d27 = 0       # Aries
    elif element_remainder == 1: # Earth
        start_sign_d27 = 3       # Cancer
    elif element_remainder == 2: # Air
        start_sign_d27 = 6       # Libra
    else:                        # Water
        start_sign_d27 = 9       # Capricorn
        
    # 4. Calculate Part Number
    # D27 Part size = 30 / 27 = 1.11111... degrees
    part_size = 30.0 / 27.0
    part_index = int(d1_degree / part_size) # 0 to 26
    
    # 5. Calculate D27 Sign
    d27_sign_index = (start_sign_d27 + part_index) % 12
    
    # 6. Calculate exact degree within D27 sign
    # Remainder in part / Part size * 30
    remainder_in_part = d1_degree % part_size
    d27_degree_in_sign = (remainder_in_part / part_size) * 30.0
    
    # Total absolute longitude in D27
    d27_total_lon = (d27_sign_index * 30) + d27_degree_in_sign
    
    return d27_total_lon

def perform_d27_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all D27 calculations, returns result dictionary.
    """
    # 1. Inputs
    user_name = data.get('user_name', '')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 2. Julian Day
    jd_ut = get_julian_day(birth_date, birth_time, tz)

    # 3. Set Ayanamsa: Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # 4. Calculate D1 Ascendant (needed to derive D27 Ascendant)
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'W')
    asc_tropical = ascmc[0]
    asc_sidereal = normalize_degree(asc_tropical - ayanamsa_val)
    
    # 5. Calculate D27 Ascendant
    d27_asc_lon = calculate_d27_longitude(asc_sidereal)
    d27_asc_sign_id, d27_asc_sign_name = get_rashi_details(d27_asc_lon)
    d27_asc_nak, d27_asc_pada = get_nakshatra_details(d27_asc_lon)
    d27_asc_deg_str = decimal_to_dms(d27_asc_lon % 30)
    
    # This is the House 1 Sign Index for Whole Sign House calculation in D27
    lagna_sign_index = d27_asc_sign_id

    # 6. Planets Calculation
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    
    planetary_positions = {}
    
    for p_name, p_id in planets_map.items():
        # Get D1 Position
        xx, ret = swe.calc_ut(jd_ut, p_id, swe.FLG_SWIEPH)
        tropical = xx[0]
        speed = xx[3]
        is_retrograde = "R" if speed < 0 else ""
        
        d1_sidereal = normalize_degree(tropical - ayanamsa_val)
        
        # Convert to D27 Position
        d27_lon = calculate_d27_longitude(d1_sidereal)
        
        # Get Details of D27 Position
        p_sign_id, p_sign_name = get_rashi_details(d27_lon)
        p_nak, p_pada = get_nakshatra_details(d27_lon)
        p_deg_str = decimal_to_dms(d27_lon % 30)
        
        # Calculate House in D27 (Whole Sign relative to D27 Lagna)
        # Logic: (Planet Sign - Lagna Sign) + 1
        # Adjust for negative results by adding 12
        house_num = (p_sign_id - lagna_sign_index) + 1
        if house_num <= 0:
            house_num += 12
            
        planetary_positions[p_name] = {
            "degrees": p_deg_str,
            "house": house_num,
            "nakshatra": p_nak,
            "pada": p_pada,
            "retrograde": is_retrograde,
            "sign": p_sign_name
        }

    # Handle Ketu (Opposite Rahu in D1, then convert to D27)
    # Note: We must convert D1 Ketu to D27, not just take opposite of D27 Rahu
    rahu_d1_lon = normalize_degree(swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SWIEPH)[0][0] - ayanamsa_val)
    ketu_d1_lon = normalize_degree(rahu_d1_lon + 180)
    
    ketu_d27_lon = calculate_d27_longitude(ketu_d1_lon)
    k_sign_id, k_sign_name = get_rashi_details(ketu_d27_lon)
    k_nak, k_pada = get_nakshatra_details(ketu_d27_lon)
    k_deg_str = decimal_to_dms(ketu_d27_lon % 30)
    
    k_house_num = (k_sign_id - lagna_sign_index) + 1
    if k_house_num <= 0:
        k_house_num += 12
        
    planetary_positions["Ketu"] = {
        "degrees": k_deg_str,
        "house": k_house_num,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "R", # Mean nodes are always retrograde roughly speaking
        "sign": k_sign_name
    }

    # 7. Construct Final Response
    response = {
        "ascendant": {
            "degrees": d27_asc_deg_str,
            "nakshatra": d27_asc_nak,
            "pada": d27_asc_pada,
            "sign": d27_asc_sign_name
        },
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "D27 (Saptavimshamsha)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }

    return response