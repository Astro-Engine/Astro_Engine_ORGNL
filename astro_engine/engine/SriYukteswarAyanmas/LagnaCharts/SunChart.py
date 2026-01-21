import os
import swisseph as swe
import datetime

# --- CONFIGURATION ---
# Path to Swiss Ephemeris files
EPHEMERIS_PATH = "astro_api/ephe" 

def dms_str(degrees_decimal):
    """Converts decimal degrees to formatted string: DD° MM' SS.SS" """
    d = int(degrees_decimal)
    m_full = (degrees_decimal - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """Calculates Nakshatra and Pada based on longitude."""
    # 27 Nakshatras, each 13° 20' (13.3333 degrees)
    nakshatra_list = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
        "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
        "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    # Normalize longitude (0-360)
    lon = longitude % 360
    
    one_star = 360 / 27  # 13.3333...
    nakshatra_index = int(lon / one_star)
    nakshatra_name = nakshatra_list[nakshatra_index]
    
    # Calculate Pada (4 padas per nakshatra, each 3° 20')
    rem_deg = lon - (nakshatra_index * one_star)
    one_pada = 3.333333333333333
    pada = int(rem_deg / one_pada) + 1
    
    return nakshatra_name, pada

def get_sign_name(sign_index):
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    return signs[sign_index % 12]

def perform_sun_chart_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs Sun Chart calculations, returns result dictionary.
    """
    if not data:
        raise ValueError("Invalid JSON input")

    user_name = data.get('user_name', 'Unknown')
    birth_date_str = data.get('birth_date')  # YYYY-MM-DD
    birth_time_str = data.get('birth_time')  # HH:MM:SS
    lat = float(data.get('latitude', 0.0))
    lon = float(data.get('longitude', 0.0))
    tz = float(data.get('timezone_offset', 0.0))

    # 2. Setup Swiss Ephemeris
    # Check if path exists to prevent silent errors, though user requested strictly this path
    abs_ephe_path = os.path.abspath(EPHEMERIS_PATH)
    swe.set_ephe_path(abs_ephe_path)

    # 3. Time Conversion (Local -> UTC)
    year, month, day = map(int, birth_date_str.split('-'))
    hour, minute, second = map(int, birth_time_str.split(':'))
    
    # Decimal hour (Local)
    decimal_hour_local = hour + (minute / 60.0) + (second / 3600.0)
    
    # Decimal hour (UTC)
    decimal_hour_utc = decimal_hour_local - tz
    
    # Julian Day (UT)
    jd_ut = swe.julday(year, month, day, decimal_hour_utc)

    # 4. Set Ayanamsa - CRITICAL STEP
    # ID 7 is Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # Get exact Ayanamsa value for reference
    ayanamsa_value_deg = swe.get_ayanamsa_ut(jd_ut)

    # 5. Define Planets Mapping
    # Swiss Eph ID mapping
    planets_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE  # Using Mean Node as standard in Vedic
    }

    # 6. Calculate Planetary Positions
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED  # Sidereal + Speed (for retrograde check)

    # We need to find the Sun's sign first to establish the Ascendant of the Sun Chart
    sun_longitude_sidereal = 0.0
    
    # Temp storage for raw data
    raw_planet_data = []

    for p_name, p_id in planets_map.items():
        # Calculate
        xx, ret_flag = swe.calc_ut(jd_ut, p_id, flags)
        longitude = xx[0]
        speed = xx[3]
        
        # Store Sun longitude specifically
        if p_name == "Sun":
            sun_longitude_sidereal = longitude
        
        is_retrograde = "R" if speed < 0 else ""
        if p_name in ["Sun", "Moon"]: # Luminaries are never retrograde
            is_retrograde = ""
        if p_name == "Rahu": # Nodes are always retrograde physically (mostly), marked R conventionally
            is_retrograde = "R"

        raw_planet_data.append({
            "name": p_name,
            "longitude": longitude,
            "retrograde": is_retrograde
        })

    # Handle Ketu (180 degrees from Rahu)
    rahu_data = next(p for p in raw_planet_data if p["name"] == "Rahu")
    ketu_lon = (rahu_data["longitude"] + 180.0) % 360.0
    raw_planet_data.append({
        "name": "Ketu",
        "longitude": ketu_lon,
        "retrograde": "R"
    })

    # 7. Determine Sun Chart Lagnas (Whole Sign System)
    # In Sun Chart, the Sign containing the Sun is House 1.
    sun_sign_index = int(sun_longitude_sidereal / 30)

    planetary_positions_response = {}

    for p_data in raw_planet_data:
        lon = p_data["longitude"]
        
        # Sign Calculation
        sign_index = int(lon / 30)
        sign_name = get_sign_name(sign_index)
        
        # Nakshatra Calculation
        nak_name, nak_pada = get_nakshatra(lon)
        
        # House Calculation (Whole Sign relative to Sun)
        # Formula: (Planet_Sign - Sun_Sign) + 1. normalize to 1-12
        house_num = ((sign_index - sun_sign_index) % 12) + 1
        
        degree_in_sign = lon % 30
        
        planetary_positions_response[p_data["name"]] = {
            "degrees": dms_str(degree_in_sign),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": nak_pada,
            "retrograde": p_data["retrograde"],
            "sign": sign_name
        }

    # 8. Define Ascendant Object (The Sun Itself acts as Lagna)
    # Using Sun's data for the "ascendant" block to signify Surya Lagna
    asc_nak, asc_pada = get_nakshatra(sun_longitude_sidereal)
    ascendant_response = {
        "degrees": dms_str(sun_longitude_sidereal % 30),
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": get_sign_name(sun_sign_index),
        "note": "Calculated as Surya Lagna (Sun Chart)"
    }

    # 9. Construct Final JSON Response
    response = {
        "ascendant": ascendant_response,
        "birth_details": {
            "birth_date": birth_date_str,
            "birth_time": birth_time_str,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_value_deg),
            "chart_type": "Surya Lagna (Sun Chart)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions_response,
        "user_name": user_name
    }
    
    return response