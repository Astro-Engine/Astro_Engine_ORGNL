import swisseph as swe
from skyfield import almanac
from skyfield.api import load, wgs84
import datetime
import pytz
import os

# ---------------- CONFIGURATION ----------------
EPHE_PATH = 'astro_api/ephe'
# Load Skyfield Data once (for accurate Sunrise)
# Ensure the .bsp file exists in your directory
EPH_SKYFIELD = load('de421.bsp')
TS = load.timescale()

# ---------------- CONSTANTS ----------------
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def setup_swisseph():
    """Configures Swiss Ephemeris path and Ayanamsa."""
    abs_path = os.path.abspath(EPHE_PATH)
    swe.set_ephe_path(abs_path)
    # Set Sidereal Mode to Lahiri (matches the Image provided: Venus in Taurus)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

def decimal_to_dms(deg):
    """Formats decimal degrees to D° M' S.SS" string."""
    d = int(deg)
    rem = (deg - d) * 60
    m = int(rem)
    s = (rem - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_sign_info(longitude):
    """Returns sign name and index (1-12)."""
    longitude = longitude % 360
    index = int(longitude / 30)
    return index + 1, SIGNS[index]

def get_nakshatra_info(longitude):
    """Calculates Nakshatra and Pada."""
    normalized = longitude % 360
    nak_duration = 360.0 / 27.0
    
    nak_index = int(normalized / nak_duration)
    name = NAKSHATRAS[nak_index]
    
    # Pada Calculation
    rem_deg = normalized - (nak_index * nak_duration)
    pada_duration = nak_duration / 4.0
    pada = int(rem_deg / pada_duration) + 1
    
    return name, pada

def get_skyfield_sunrise(lat, lon, dt_local, tz_offset):
    """
    Calculates the exact Sunrise time using Skyfield.
    Robustly handles scalar Time objects.
    """
    location = wgs84.latlon(lat, lon)
    tz_delta = datetime.timedelta(hours=tz_offset)
    t_birth_utc = dt_local - tz_delta 
    
    # Check 30 hours back to ensure we find the Sunrise determining the Vedic Day
    start_dt = t_birth_utc - datetime.timedelta(hours=30)
    end_dt = t_birth_utc + datetime.timedelta(hours=2)
    
    t0 = TS.from_datetime(start_dt.replace(tzinfo=pytz.utc))
    t1 = TS.from_datetime(end_dt.replace(tzinfo=pytz.utc))
    
    t_times, t_events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(EPH_SKYFIELD, location))
    
    sunrise_objs = []
    # Iterate by index to handle both scalar and array returns safely
    for i in range(len(t_events)):
        if t_events[i] == 1: # 1 = Sunrise
            sunrise_objs.append(t_times[i])
            
    if not sunrise_objs:
        raise ValueError("No sunrise found in calculation window.")

    # Find latest sunrise <= birth time (Vedic Day Start)
    birth_tt = TS.from_datetime(t_birth_utc.replace(tzinfo=pytz.utc)).tt
    valid_sunrise = None
    
    for t_sun in reversed(sunrise_objs):
        if t_sun.tt <= birth_tt:
            valid_sunrise = t_sun
            break
            
    # Fallback if birth is before the first sunrise in window
    if valid_sunrise is None:
        valid_sunrise = sunrise_objs[0]

    return valid_sunrise

def get_tropical_sun_pos(t_obj):
    """Get Tropical (Sayana) Sun Longitude from Skyfield."""
    sun = EPH_SKYFIELD['sun']
    earth = EPH_SKYFIELD['earth']
    astrometric = earth.at(t_obj).observe(sun)
    apparent = astrometric.apparent()
    lat, lon, dist = apparent.ecliptic_latlon()
    return lon.degrees

def gatika_lagna_calculations(data):
    """
    Main logic function used by the API.
    """
    setup_swisseph()
    
    # 1. Parse Input
    user_name = data.get("user_name")
    birth_date_str = data.get("birth_date")
    birth_time_str = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz_offset = float(data.get("timezone_offset"))
    
    # Datetime Setup
    local_dt_str = f"{birth_date_str} {birth_time_str}"
    local_dt = datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M:%S")
    tz_delta = datetime.timedelta(hours=tz_offset)
    birth_dt_utc = local_dt - tz_delta
    
    # 2. Ghatika Lagna (GL) Calculation
    # A. Get Sunrise (Vedic Day Start)
    t_sunrise = get_skyfield_sunrise(lat, lon, local_dt, tz_offset)
    
    # B. Get Sun Position at Sunrise (Tropical)
    sun_trop_sunrise = get_tropical_sun_pos(t_sunrise)
    
    # C. Get Ayanamsa (Lahiri)
    ayanamsa_val = swe.get_ayanamsa_ut(t_sunrise.tt)
    
    # D. Sidereal Sun at Sunrise
    sun_sid_sunrise = (sun_trop_sunrise - ayanamsa_val) % 360
    
    # E. Time Difference (Minutes)
    t_birth = TS.from_datetime(birth_dt_utc.replace(tzinfo=pytz.utc))
    diff_days = t_birth.tt - t_sunrise.tt
    diff_minutes = diff_days * 24 * 60
    
    # F. Calculate GL (Speed 1.25 deg/min)
    gl_motion = diff_minutes * 1.25
    gl_longitude = (sun_sid_sunrise + gl_motion) % 360
    
    # G. GL Details
    gl_sign_num, gl_sign_name = get_sign_info(gl_longitude)
    gl_nak, gl_pada = get_nakshatra_info(gl_longitude)
    
    # 3. Planetary Calculation (at Birth Time)
    # Convert to Decimal Hour for swe.julday
    decimal_hour = birth_dt_utc.hour + (birth_dt_utc.minute / 60.0) + (birth_dt_utc.second / 3600.0)
    # Note: Using 'julday' (correct function name)
    jd_birth_ut = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day, decimal_hour)
    
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
    
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }
    
    planetary_positions = {}
    calculated_planets = []

    for p_name, p_id in planets_map.items():
        res = swe.calc_ut(jd_birth_ut, p_id, flags)
        lon_deg = res[0][0]
        speed = res[0][3]
        calculated_planets.append({"name": p_name, "deg": lon_deg, "speed": speed})
        
    # Add Ketu (Opposite Rahu)
    rahu = next(p for p in calculated_planets if p["name"] == "Rahu")
    ketu_deg = (rahu["deg"] + 180) % 360
    calculated_planets.append({"name": "Ketu", "deg": ketu_deg, "speed": rahu["speed"]})
    
    # 4. Construct Output
    for p in calculated_planets:
        sign_num, sign_name = get_sign_info(p["deg"])
        nak_name, nak_pada = get_nakshatra_info(p["deg"])
        
        # GL House Logic: (Planet_Sign - GL_Sign) + 1
        house_num = (sign_num - gl_sign_num) + 1
        if house_num <= 0:
            house_num += 12
            
        # Retrograde Logic
        is_retro = ""
        if p["name"] in ["Rahu", "Ketu"]:
            is_retro = "R" # Nodes always Retrograde
        elif p["speed"] < 0 and p["name"] not in ["Sun", "Moon"]:
            is_retro = "R"

        planetary_positions[p["name"]] = {
            "degrees": decimal_to_dms(p["deg"]),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": nak_pada,
            "retrograde": is_retro,
            "sign": sign_name
        }
        
    response = {
        "ascendant": {
            "degrees": decimal_to_dms(gl_longitude),
            "nakshatra": gl_nak,
            "pada": gl_pada,
            "sign": gl_sign_name
        },
        "birth_details": {
            "birth_date": birth_date_str,
            "birth_time": birth_time_str,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz_offset
        },
        "notes": {
            "ayanamsa": "Lahiri", # Updated to reflect the correct calculation
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "Ghatika Lagna (GL)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }
    
    return response