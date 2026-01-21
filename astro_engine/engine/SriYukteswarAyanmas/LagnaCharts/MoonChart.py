import os
import swisseph as swe

# --- CONFIGURATION ---
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
# 7 = Sri Yukteswar Ayanamsa ID
SID_METHOD_YUKTESWAR = 7 

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANET_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE, 
    "Ketu": "KETU_CALC" 
}

# --- HELPER FUNCTIONS ---

def decimal_to_dms(deg):
    """Formats degrees as: 8° 21' 6.44" """
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_sign_info(longitude):
    """Returns sign index, sign name, and degrees within sign."""
    longitude = longitude % 360
    sign_index = int(longitude // 30)
    sign_degree = longitude % 30
    return sign_index, ZODIAC_SIGNS[sign_index], sign_degree

def get_nakshatra(longitude):
    """Calculates Nakshatra and Pada."""
    abs_degree = longitude % 360
    nak_duration = 13 + (20/60.0) # 13.3333 deg
    
    nak_index = int(abs_degree / nak_duration)
    nak_rem_deg = abs_degree - (nak_index * nak_duration)
    
    pada_duration = 3 + (20/60.0) # 3.3333 deg
    pada = int(nak_rem_deg / pada_duration) + 1
    
    if nak_index >= 27:
        nak_index = 0
        
    return NAKSHATRAS[nak_index], pada

def get_julian_day_ut(date_str, time_str, tz_offset):
    """Calculates Julian Day in UT."""
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    
    dec_hour_local = hour + (minute / 60.0) + (second / 3600.0)
    dec_hour_ut = dec_hour_local - float(tz_offset)
    
    jd_ut = swe.julday(year, month, day, dec_hour_ut)
    return jd_ut

def calculate_moon_chart_house(planet_sign_idx, moon_sign_idx):
    """
    Moon Chart Logic:
    Moon Sign = House 1.
    Formula: (Planet - Moon) + 1
    """
    house = (planet_sign_idx - moon_sign_idx) + 1
    if house <= 0:
        house += 12
    return house

def perform_moon_chart_calculation(data):
    """
    Main logic function used by the API.
    """
    # 1. Inputs
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 2. Set Ayanamsa: Sri Yukteswar (ID 7)
    swe.set_sid_mode(SID_METHOD_YUKTESWAR, 0, 0)
    
    # 3. Time Calculation
    jd_ut = get_julian_day_ut(birth_date, birth_time, tz)
    
    # 4. Get Ayanamsa Value
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # 5. Calculate Planetary Positions
    temp_bodies = {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED

    for p_name, p_id in PLANET_MAP.items():
        if p_name == "Ketu":
            # Ketu is 180 opposite Rahu
            rahu = temp_bodies["Rahu"]
            pl_lon = (rahu["lon"] + 180.0) % 360
            is_retro = rahu["retro"]
        else:
            res, _ = swe.calc_ut(jd_ut, p_id, flags)
            pl_lon = res[0]
            pl_speed = res[3]
            is_retro = "R" if pl_speed < 0 else ""
            
        temp_bodies[p_name] = {"lon": pl_lon, "retro": is_retro}

    # 6. IDENTIFY CHART ASCENDANT (MOON)
    # In a Moon Chart, the "Ascendant" IS the Moon.
    moon_data = temp_bodies["Moon"]
    moon_lon = moon_data["lon"]
    moon_sign_idx, moon_sign_name, moon_sign_deg = get_sign_info(moon_lon)
    moon_nak, moon_pada = get_nakshatra(moon_lon)

    # Create the 'ascendant' output block using MOON details
    # This ensures the output says "Sign: Libra" (or whatever Moon is) as House 1
    ascendant_output = {
        "degrees": decimal_to_dms(moon_sign_deg),
        "nakshatra": moon_nak,
        "pada": moon_pada,
        "sign": moon_sign_name,
        "note": "Moon Chart Lagna (Chandra Lagna)"
    }

    # 7. Calculate Physical Ascendant (Udaya Lagna) separately
    # This is the "As" point in the chart
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'W')
    udaya_lagna_lon = ascmc[0]
    # Add Udaya Lagna to the bodies list to be processed like a planet
    temp_bodies["Udaya Lagna"] = {"lon": udaya_lagna_lon, "retro": ""}

    # 8. Build Planetary Positions Output
    planetary_positions = {}
    
    # Sort for clean JSON output
    sorted_keys = sorted(temp_bodies.keys())

    for p_name in sorted_keys:
        p_data = temp_bodies[p_name]
        lon_val = p_data["lon"]
        retro_val = p_data["retro"]
        
        # Sign Info
        s_idx, s_name, s_deg = get_sign_info(lon_val)
        
        # Nakshatra Info
        n_name, n_pada = get_nakshatra(lon_val)
        
        # House Calculation:
        # All houses are calculated relative to the Moon Sign (House 1)
        house_num = calculate_moon_chart_house(s_idx, moon_sign_idx)
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms(s_deg),
            "house": house_num,
            "nakshatra": n_name,
            "pada": n_pada,
            "retrograde": retro_val,
            "sign": s_name
        }

    # 9. Construct Final Response
    response = {
        "ascendant": ascendant_output,
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
            "chart_type": "Moon Chart (Chandra Lagna)",
            "house_system": "Whole Sign (Moon = House 1)"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }
    
    return response