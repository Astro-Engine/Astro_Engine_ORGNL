import os
import datetime
import math
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
# Set the path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS & MAPPINGS
# ==========================================
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
# HELPER FUNCTIONS
# ==========================================

def decimal_to_dms_string(deg_float):
    """Converts decimal degrees to a formatted string: 8° 21' 6.44" """
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def get_julian_day(date_str, time_str, tz_offset):
    """Calculates Julian Day (UT) from local date/time."""
    dt_str = f"{date_str} {time_str}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=float(tz_offset))
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    return jd, utc_dt

def get_fractional_year(dt_object):
    """Calculates exact fractional year for Ayanamsa formula."""
    year = dt_object.year
    day_of_year = dt_object.timetuple().tm_yday
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    days_in_year = 366.0 if is_leap else 365.0
    fractional_day = day_of_year + (dt_object.hour / 24.0) + (dt_object.minute / 1440.0)
    return year + (fractional_day / days_in_year)

def calculate_yukteswar_ayanamsa(fractional_year):
    """
    Sri Yukteswar Formula: (Current Year - 499) * 54 arc-seconds
    """
    diff_years = fractional_year - 499.0
    # 54 arc-seconds = 0.015 degrees
    return diff_years * (54.0 / 3600.0)

def get_nakshatra_details(longitude):
    """Returns Nakshatra name and Pada."""
    pos = longitude % 360
    nak_duration = 13.3333333333
    nak_index = int(pos / nak_duration)
    
    # Calculate degrees within the nakshatra
    deg_in_nak = pos - (nak_index * nak_duration)
    
    # Calculate Pada (Quarter) - each pada is 3.333... degrees
    pada_duration = 3.3333333333
    pada = int(deg_in_nak / pada_duration) + 1
    
    return NAKSHATRAS[nak_index], pada

def natal_chart_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all calculations, returns result dictionary.
    """
    # Extract Inputs
    name = data.get('user_name')
    dob = data.get('birth_date')
    tob = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 1. Calculate Time & Julian Day
    jd, utc_dt_obj = get_julian_day(dob, tob, tz)
    
    # 2. Calculate Sri Yukteswar Ayanamsa
    frac_year = get_fractional_year(utc_dt_obj)
    ayanamsa_val = calculate_yukteswar_ayanamsa(frac_year)
    
    # 3. Calculate Ascendant
    # Get Tropical Ascendant first
    cusps, ascmc = swe.houses(jd, lat, lon, b'P') 
    trop_asc = ascmc[0]
    
    # Convert to Yukteswar Sidereal
    sid_asc_deg = (trop_asc - ayanamsa_val) % 360
    asc_sign_index = int(sid_asc_deg / 30)
    deg_in_sign = sid_asc_deg % 30
    
    asc_nak, asc_pada = get_nakshatra_details(sid_asc_deg)
    
    # 4. Planetary Calculations
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.TRUE_NODE 
    }
    
    planetary_positions = {}
    
    # Cache for Ketu Calculation
    rahu_full_deg = 0
    
    for p_name, p_id in planets_map.items():
        # Get Tropical Position
        res = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH)
        trop_deg = res[0][0]
        speed_lon = res[0][3]
        
        # Apply Ayanamsa
        sid_deg = (trop_deg - ayanamsa_val) % 360
        
        if p_name == "Rahu":
            rahu_full_deg = sid_deg

        # Details
        sign_index = int(sid_deg / 30)
        p_deg_in_sign = sid_deg % 30
        
        # Whole Sign House: (SignIndex - AscSignIndex + 12) % 12 + 1
        house_num = ((sign_index - asc_sign_index + 12) % 12) + 1
        
        nak_name, pada = get_nakshatra_details(sid_deg)
        
        # Retrograde Logic (Nodes are usually treated as Retrograde in Vedic)
        is_retro = "R" if speed_lon < 0 or p_name in ["Rahu"] else ""
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms_string(p_deg_in_sign),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": pada,
            "retrograde": is_retro,
            "sign": ZODIAC_SIGNS[sign_index]
        }

    # Calculate Ketu (Opposite Rahu)
    ketu_deg = (rahu_full_deg + 180.0) % 360
    ketu_sign_idx = int(ketu_deg / 30)
    ketu_deg_in_sign = ketu_deg % 30
    ketu_house = ((ketu_sign_idx - asc_sign_index + 12) % 12) + 1
    ketu_nak, ketu_pada = get_nakshatra_details(ketu_deg)
    
    planetary_positions["Ketu"] = {
        "degrees": decimal_to_dms_string(ketu_deg_in_sign),
        "house": ketu_house,
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "retrograde": "", # Usually left blank or 'R' depending on preference, standard is R for nodes
        "sign": ZODIAC_SIGNS[ketu_sign_idx]
    }
    
    # Sort planetary positions alphabetically to match example
    sorted_planets = dict(sorted(planetary_positions.items()))

    # Construct Final Response
    response = {
        "ascendant": {
            "degrees": decimal_to_dms_string(deg_in_sign), # Degrees within the sign
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "sign": ZODIAC_SIGNS[asc_sign_index]
        },
        "birth_details": {
            "birth_date": dob,
            "birth_time": tob,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(round(ayanamsa_val, 6)),
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        },
        "planetary_positions": sorted_planets,
        "user_name": name
    }
    
    return response