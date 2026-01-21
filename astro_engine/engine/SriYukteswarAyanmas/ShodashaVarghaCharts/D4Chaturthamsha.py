import os
import datetime
import swisseph as swe

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
EPHE_PATH = os.path.join(BASE_DIR, 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
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

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": None 
}

# --- HELPER FUNCTIONS ---

def get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - datetime.timedelta(hours=float(tz_offset))
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)

def decimal_to_dms(deg_float):
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s_float = (m_float - m) * 60
    s = round(s_float, 2) # Rounding to match your sample format
    return f"{d}° {m}' {s}\""

def get_nakshatra_pada(longitude):
    """Calculates Nakshatra and Pada based on absolute longitude (0-360)."""
    # 27 Nakshatras, each 13° 20' (13.3333 degrees)
    nak_duration = 13.333333333
    nak_index = int(longitude / nak_duration)
    
    # Calculate position within the Nakshatra to find Pada
    rem_deg = longitude - (nak_index * nak_duration)
    # Each Pada is 3° 20' (3.3333 degrees)
    pada = int(rem_deg / 3.333333333) + 1
    
    return NAKSHATRAS[nak_index % 27], pada

def calculate_house_whole_sign(planet_lon, asc_lon):
    """Calculates House number (1-12) based on Whole Sign system."""
    asc_sign_idx = int(asc_lon / 30)
    planet_sign_idx = int(planet_lon / 30)
    
    house = (planet_sign_idx - asc_sign_idx) + 1
    if house <= 0:
        house += 12
    return house

def get_planet_data_raw(jd, body_id):
    """Wrapper to get raw calculation tuple from Swiss Eph."""
    # Returns ((lon, lat, dist, speed, ...), flags) OR (lon, lat...)
    calc_data = swe.calc_ut(jd, body_id, swe.FLG_SIDEREAL)
    
    if isinstance(calc_data[0], tuple):
        coords = calc_data[0]
    else:
        coords = calc_data
        
    lon = coords[0]
    speed = coords[3] # Speed in longitude (deg/day)
    
    return lon, speed

def calculate_d4_longitude(d1_lon):
    """
    Calculates the 'Virtual' D4 Longitude.
    This logic projects the D1 placement into D4 degrees.
    Steps:
    1. Determine D4 Sign based on Kendra Rule.
    2. Map the 7.5 deg D1 sector into a full 30 deg D4 sector.
    """
    d1_lon = d1_lon % 360
    d1_sign_idx = int(d1_lon / 30)
    lon_in_sign = d1_lon % 30
    
    # Determine D4 Sign Shift & Local Degree Mapping
    # Multiplier is 4 because 7.5 * 4 = 30 degrees
    if 0.0 <= lon_in_sign < 7.5:
        shift = 0   # 1st House
        d4_local_deg = (lon_in_sign - 0) * 4
    elif 7.5 <= lon_in_sign < 15.0:
        shift = 3   # 4th House
        d4_local_deg = (lon_in_sign - 7.5) * 4
    elif 15.0 <= lon_in_sign < 22.5:
        shift = 6   # 7th House
        d4_local_deg = (lon_in_sign - 15.0) * 4
    else:
        shift = 9   # 10th House
        d4_local_deg = (lon_in_sign - 22.5) * 4
        
    d4_sign_idx = (d1_sign_idx + shift) % 12
    d4_absolute_lon = (d4_sign_idx * 30) + d4_local_deg
    
    return d4_absolute_lon

def perform_d4_calculation(data):
    """
    Main logic function. Receives input dictionary, 
    performs D4 calculations, and returns the response dictionary.
    """
    # 1. Inputs
    birth_date = data.get("birth_date")
    birth_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon_geo = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    user_name = data.get("user_name", "User")
    
    # 2. Setup
    jd = get_julian_day(birth_date, birth_time, tz)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_value = swe.get_ayanamsa_ut(jd)
    
    # 3. Calculate D1 Ascendant (for reference to calculate House numbers)
    cusps, ascmc = swe.houses_ex(jd, lat, lon_geo, b'P', swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0]
    
    # 4. Calculate D4 Ascendant
    d4_asc_lon = calculate_d4_longitude(d1_asc_lon)
    d4_asc_sign_idx = int(d4_asc_lon / 30)
    d4_asc_nak, d4_asc_pada = get_nakshatra_pada(d4_asc_lon)
    
    # Prepare Response Structure
    response = {
        "ascendant": {
            "degrees": decimal_to_dms(d4_asc_lon % 30),
            "nakshatra": d4_asc_nak,
            "pada": d4_asc_pada,
            "sign": ZODIAC_SIGNS[d4_asc_sign_idx]
        },
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon_geo,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_value),
            "chart_type": "Chaturthamsha (D4)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": {},
        "user_name": user_name
    }
    
    # 5. Process Planets
    for p_name, p_id in PLANETS.items():
        if p_name == "Ketu":
            rahu_lon, speed = get_planet_data_raw(jd, swe.MEAN_NODE)
            d1_lon = (rahu_lon + 180) % 360
            retrograde_status = "" # Ketu is always retrograde naturally
        else:
            d1_lon, speed = get_planet_data_raw(jd, p_id)
            # Check Retrograde (speed < 0)
            retrograde_status = "R" if speed < 0 else ""
            # Rahu/Ketu are always retrograde, but standard is to mark them if needed
            if p_name == "Rahu": retrograde_status = "R" 

        # TRANSFORM TO D4
        d4_lon = calculate_d4_longitude(d1_lon)
        d4_sign_idx = int(d4_lon / 30)
        
        # Calculate House relative to D4 Ascendant
        house_num = calculate_house_whole_sign(d4_lon, d4_asc_lon)
        
        # Calculate Nakshatra of the D4 Longitude (Deity/Force of D4)
        nak, pada = get_nakshatra_pada(d4_lon)
        
        response["planetary_positions"][p_name] = {
            "degrees": decimal_to_dms(d4_lon % 30),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": retrograde_status,
            "sign": ZODIAC_SIGNS[d4_sign_idx]
        }
        
    return response