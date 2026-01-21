import os
import datetime
import swisseph as swe
from skyfield import almanac
from skyfield.api import load, wgs84

# --- 1. CONFIGURATION ---
# EPHE_PATH = os.path.join(os.path.dirname(__file__), 'astro_api/ephe') # Use this if relative path fails
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Load Skyfield Data
try:
    eph = load('de421.bsp')
    ts = load.timescale()
except Exception as e:
    print(f"Skyfield Load Error: {e}")

# Constants
SID_MODE_YUKTESWAR = 7  
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

# --- 2. UTILITY FUNCTIONS ---

def to_dms_string(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m/60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_pada(longitude):
    longitude = longitude % 360
    nak_duration = 13.333333333
    nak_index = int(longitude / nak_duration)
    rem_deg = longitude - (nak_index * nak_duration)
    pada = int(rem_deg / 3.333333333) + 1
    return NAKSHATRAS[nak_index], pada

def get_whole_sign_house(planet_long, asc_long):
    asc_sign_idx = int(asc_long / 30)
    planet_sign_idx = int(planet_long / 30)
    house = (planet_sign_idx - asc_sign_idx) + 1
    if house <= 0:
        house += 12
    return house

def get_julian_day_swisseph(date_str, time_str, tz_offset):
    local_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    offset_delta = datetime.timedelta(hours=float(tz_offset))
    ut_dt = local_dt - offset_delta
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, 
                      ut_dt.hour + ut_dt.minute/60.0 + ut_dt.second/3600.0)

def get_skyfield_sunrise_and_sun(date_str, time_str, tz_offset, lat, lon):
    """
    Returns: Sunrise Time (Skyfield) and Sun Tropical Longitude.
    """
    # 1. Parse Inputs and set Location
    local_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    offset_delta = datetime.timedelta(hours=float(tz_offset))
    ut_dt = local_dt - offset_delta
    
    # Create valid UTC datetime objects for Skyfield
    ut_dt = ut_dt.replace(tzinfo=datetime.timezone.utc)
    t_birth = ts.from_datetime(ut_dt)
    
    location = wgs84.latlon(lat, lon)
    
    # 2. Define Search Window
    # We look back 2 days to be safe (finding the PREVIOUS sunrise)
    # Ensure t_start and t_end are strictly separate time objects
    t_start = ts.from_datetime(ut_dt - datetime.timedelta(days=2))
    t_end = ts.from_datetime(ut_dt + datetime.timedelta(hours=1)) # Just past birth
    
    # 3. Calculate Sunrise/Sunset events
    f = almanac.sunrise_sunset(eph, location)
    times, events = almanac.find_discrete(t_start, t_end, f)
    
    # 4. Filter for Sunrise (event == 1) strictly BEFORE birth
    # We iterate backwards to find the closest one
    valid_sunrise = None
    
    # events is a numpy array, times is a Time array. 
    # Zip works safely.
    for t, e in zip(times, events):
        if e == 1: # Sunrise
            if t.tt <= t_birth.tt:
                valid_sunrise = t 
            else:
                # If we hit a sunrise AFTER birth, we stop and keep the previous one
                break
    
    if valid_sunrise is None:
        # Fallback: Force calculation for the specific day of birth start
        # This handles edge cases where the 2-day window was insufficient or empty
        t_fallback_start = ts.utc(ut_dt.year, ut_dt.month, ut_dt.day - 1)
        times_fb, events_fb = almanac.find_discrete(t_fallback_start, t_birth, f)
        for t, e in zip(times_fb, events_fb):
            if e == 1:
                valid_sunrise = t

    # 5. Get Sun Position at that Sunrise
    sun = eph['sun']
    earth = eph['earth']
    obs = earth + location
    
    astrometric = obs.at(valid_sunrise).observe(sun)
    apparent = astrometric.apparent()
    _, lon_trop, _ = apparent.ecliptic_latlon()
    
    return valid_sunrise, lon_trop.degrees, t_birth

def perform_bhava_lagna_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all calculations, returns result dictionary.
    """
    # A. Parse Input
    user_name = data.get('user_name', 'User')
    dob = data.get('birth_date')
    tob = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # B. SKYFIELD CALCULATION
    t_sunrise, sun_trop_sunrise, t_birth = get_skyfield_sunrise_and_sun(dob, tob, tz, lat, lon)

    # C. SWISSEPH AYANAMSA
    # Convert Skyfield UT1 to Julian Day for SwissEph
    jd_sunrise = t_sunrise.ut1
    swe.set_sid_mode(SID_MODE_YUKTESWAR, 0.0, 0.0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_sunrise)
    
    # D. BHAVA LAGNA LOGIC
    # 1. Sidereal Sun
    sun_sid_sunrise = (sun_trop_sunrise - ayanamsa_val) % 360.0
    
    # 2. Ishta Kala (Minutes from Sunrise to Birth)
    ishta_days = t_birth.ut1 - t_sunrise.ut1
    ishta_min = ishta_days * 1440.0
    
    # 3. BL Degree = Sun_Sid + (Ishta_Min * 0.25)
    bl_degree = (sun_sid_sunrise + (ishta_min * 0.25)) % 360.0
    
    # E. PLANETARY POSITIONS (SwissEph)
    jd_birth = get_julian_day_swisseph(dob, tob, tz)
    
    p_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    
    planetary_data = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    for p_name, p_id in p_ids.items():
        res = swe.calc_ut(jd_birth, p_id, flags)
        
        # Extract longitude safely
        if isinstance(res[0], tuple):
            p_long = res[0][0]
            p_speed = res[0][3]
        else:
            p_long = res[0]
            p_speed = 0
        
        # Format Data
        sign_idx = int(p_long / 30)
        sign_name = ZODIAC_SIGNS[sign_idx]
        nak, pada = get_nakshatra_pada(p_long)
        house = get_whole_sign_house(p_long, bl_degree)
        is_retro = "R" if p_speed < 0 else ""
        
        planetary_data[p_name] = {
            "degrees": to_dms_string(p_long % 30),
            "house": house,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": sign_name
        }
        
        if p_name == "Rahu":
            k_long = (p_long + 180.0) % 360.0
            k_sign_idx = int(k_long / 30)
            k_nak, k_pada = get_nakshatra_pada(k_long)
            k_house = get_whole_sign_house(k_long, bl_degree)
            
            planetary_data["Ketu"] = {
                "degrees": to_dms_string(k_long % 30),
                "house": k_house,
                "nakshatra": k_nak,
                "pada": k_pada,
                "retrograde": "R",
                "sign": ZODIAC_SIGNS[k_sign_idx]
            }

    # F. ASCENDANT (Bhava Lagna) OBJECT
    bl_sign_idx = int(bl_degree / 30)
    bl_nak, bl_pada = get_nakshatra_pada(bl_degree)
    
    ascendant_data = {
        "degrees": to_dms_string(bl_degree % 30),
        "nakshatra": bl_nak,
        "pada": bl_pada,
        "sign": ZODIAC_SIGNS[bl_sign_idx]
    }
    
    # G. JSON RESPONSE
    response = {
        "ascendant": ascendant_data,
        "birth_details": {
            "birth_date": dob,
            "birth_time": tob,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "Bhava Lagna (Jaimini Special)",
            "house_system": "Whole Sign",
            "engine": "Skyfield (Sunrise) + SwissEph"
        },
        "planetary_positions": planetary_data,
        "user_name": user_name
    }
    
    return response