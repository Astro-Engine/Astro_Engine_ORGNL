import os
import datetime
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
# Set the path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS
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
    """Converts decimal degrees to formatted string: 8° 21' 6.44" """
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=float(tz_offset))
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    return jd, utc_dt

def get_fractional_year(dt_object):
    year = dt_object.year
    day_of_year = dt_object.timetuple().tm_yday
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    days_in_year = 366.0 if is_leap else 365.0
    fractional_day = day_of_year + (dt_object.hour / 24.0) + (dt_object.minute / 1440.0)
    return year + (fractional_day / days_in_year)

def calculate_yukteswar_ayanamsa(fractional_year):
    # (Current Year - 499) * 54 arc-seconds
    diff_years = fractional_year - 499.0
    return diff_years * (54.0 / 3600.0)

def get_nakshatra_details(longitude_in_sign, sign_index):
    """
    Calculates Nakshatra based on the absolute longitude (0-360).
    Used here to calculate the 'D9 Nakshatra' from the projected D9 degree.
    """
    absolute_pos = (sign_index * 30) + longitude_in_sign
    nak_duration = 13.3333333333
    nak_index = int(absolute_pos / nak_duration)
    deg_in_nak = absolute_pos - (nak_index * nak_duration)
    pada_duration = 3.3333333333
    pada = int(deg_in_nak / pada_duration) + 1
    return NAKSHATRAS[nak_index % 27], pada

# ==========================================
# CORE D9 LOGIC
# ==========================================

def calculate_d9_parameters(sidereal_lon):
    """
    Returns the Sign Index, Projected Degree (0-30), and Vargottama status for D9.
    """
    # 1. Navamsha Span (3° 20')
    navamsha_span = 3.333333333333333
    
    # 2. D9 Sign Calculation
    # Get absolute index (0-107)
    absolute_idx = int(sidereal_lon / navamsha_span)
    d9_sign_index = absolute_idx % 12
    
    # 3. D9 Degree Calculation (Projected)
    # How far into the specific navamsha are we? (0.0 to 3.333...)
    remainder = sidereal_lon % navamsha_span
    # Scale this up to 30 degrees (x9)
    d9_degree_projected = remainder * 9.0
    
    return d9_sign_index, d9_degree_projected

def perform_d9_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs D9 calculations, returns result dictionary.
    """
    name = data.get('user_name')
    dob = data.get('birth_date')
    tob = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 1. Standard Calculations (Hidden D1 Layer)
    jd, utc_dt_obj = get_julian_day(dob, tob, tz)
    frac_year = get_fractional_year(utc_dt_obj)
    ayanamsa_val = calculate_yukteswar_ayanamsa(frac_year)
    
    # 2. Ascendant (Calculate D1 -> Convert to D9)
    cusps, ascmc = swe.houses(jd, lat, lon, b'P') 
    trop_asc = ascmc[0]
    sid_asc_deg = (trop_asc - ayanamsa_val) % 360
    
    # D9 Ascendant
    d9_asc_sign_idx, d9_asc_deg = calculate_d9_parameters(sid_asc_deg)
    d9_asc_nak, d9_asc_pada = get_nakshatra_details(d9_asc_deg, d9_asc_sign_idx)
    
    # 3. Planets (Calculate D1 -> Convert to D9)
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.TRUE_NODE 
    }
    
    planetary_positions = {}
    rahu_sid_deg = 0
    
    for p_name, p_id in planets_map.items():
        res = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH)
        trop_deg = res[0][0]
        speed = res[0][3]
        sid_deg = (trop_deg - ayanamsa_val) % 360
        
        if p_name == "Rahu":
            rahu_sid_deg = sid_deg
        
        # --- D9 LOGIC APPLIED ---
        d9_sign_idx, d9_deg = calculate_d9_parameters(sid_deg)
        
        # D9 House (Relative to D9 Ascendant)
        d9_house = ((d9_sign_idx - d9_asc_sign_idx + 12) % 12) + 1
        
        # D9 Nakshatra (Projected)
        d9_nak, d9_pada = get_nakshatra_details(d9_deg, d9_sign_idx)
        
        # Retrograde Status (Inherited from D1)
        is_retro = "R" if speed < 0 or p_name == "Rahu" else ""
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms_string(d9_deg), # Expanded D9 degree
            "house": d9_house,
            "nakshatra": d9_nak,
            "pada": d9_pada,
            "retrograde": is_retro,
            "sign": ZODIAC_SIGNS[d9_sign_idx]
        }

    # Handle Ketu (Opposite Rahu)
    ketu_sid_deg = (rahu_sid_deg + 180.0) % 360
    
    # D9 Logic for Ketu
    k_sign_idx, k_deg = calculate_d9_parameters(ketu_sid_deg)
    k_house = ((k_sign_idx - d9_asc_sign_idx + 12) % 12) + 1
    k_nak, k_pada = get_nakshatra_details(k_deg, k_sign_idx)
    
    planetary_positions["Ketu"] = {
        "degrees": decimal_to_dms_string(k_deg),
        "house": k_house,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "", 
        "sign": ZODIAC_SIGNS[k_sign_idx]
    }
    
    # Sort Alphabetically
    sorted_planets = dict(sorted(planetary_positions.items()))

    # Construct Final Response (D1 Structure, D9 Data)
    response = {
        "ascendant": {
            "degrees": decimal_to_dms_string(d9_asc_deg),
            "nakshatra": d9_asc_nak,
            "pada": d9_asc_pada,
            "sign": ZODIAC_SIGNS[d9_asc_sign_idx]
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
            "chart_type": "D9 Navamsha (Projected)",
            "house_system": "Whole Sign (D9 Ascendant as House 1)"
        },
        "planetary_positions": sorted_planets,
        "user_name": name
    }
    
    return response