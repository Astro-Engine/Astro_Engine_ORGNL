import os
import datetime
import swisseph as swe
from skyfield import almanac
from skyfield.api import load, wgs84

# =================CONFIGURATION=================
# 1. Setup Swiss Ephemeris Path
# Ensure you have the 'ephe' folder with Swiss Ephemeris files in 'astro_api/ephe'
EPHE_PATH = 'astro_api/ephe'
swe.set_ephe_path(EPHE_PATH)

# 2. Load Skyfield Data
# This will download 'de421.bsp' if missing (required for Sunrise/Sunset)
# Loading it here ensures it's done once when the module is imported
ts = load.timescale()
eph = load('de421.bsp')

# =================CONSTANTS=================
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_MAP = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 
    'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE 
}

# =================HELPER FUNCTIONS=================

def decimal_to_dms(deg_float):
    """Converts decimal degrees to D° M' S.ss" string."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_sign_name(longitude):
    """Returns the Zodiac sign name based on longitude."""
    return SIGNS[int(longitude / 30) % 12]

def get_nakshatra_details(longitude):
    """Calculates Nakshatra and Pada."""
    # Normalize longitude
    lon = longitude % 360
    
    # Each Nakshatra is 13° 20' (13.3333 degrees)
    one_star = 360 / 27
    nak_index = int(lon / one_star)
    nak_name = NAKSHATRAS[nak_index]
    
    # Calculate Pada (Quarter)
    # Each Pada is 3° 20' (3.3333 degrees)
    rem_deg = lon % one_star
    one_pada = one_star / 4
    pada = int(rem_deg / one_pada) + 1
    
    return nak_name, pada

def get_julian_day(dt_utc):
    """Convert Python datetime (UTC) to Julian Day using Swisseph."""
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                      dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

def get_precise_sunrise(lat, lon, birth_dt_utc):
    """
    Calculates the last sunrise immediately preceding the birth time using Skyfield.
    """
    try:
        observer = wgs84.latlon(lat, lon)
        
        # Search Window: Look back 30 hours from birth to find the previous sunrise
        t_end = ts.from_datetime(birth_dt_utc)
        t_start = ts.from_datetime(birth_dt_utc - datetime.timedelta(hours=30))
        
        # Calculate Sunrise/Sunset events
        t, y = almanac.find_discrete(t_start, t_end, almanac.sunrise_sunset(eph, observer))
        
        # Filter for Sunrises (y=1)
        sunrise_times = [time for time, event in zip(t, y) if event == 1]
        
        if not sunrise_times:
            return None
            
        # The last sunrise found is the one immediately preceding birth
        last_sunrise = sunrise_times[-1]
        
        return last_sunrise.utc_datetime()

    except Exception as e:
        print(f"Skyfield Error: {e}")
        return None

def calculate_planets_yukteswar(jd):
    """
    Calculate planetary positions using Sri Yukteswar Ayanamsa (ID 7).
    """
    # 7 is the integer ID for Sri Yukteswar in Swiss Ephemeris
    swe.set_sid_mode(7, 0, 0)
    
    results = {}
    for name, pid in PLANET_MAP.items():
        # Flags: Swiss Ephemeris | Sidereal | Speed
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # xx = [longitude, lat, dist, speed, ...]
        xx, ret = swe.calc_ut(jd, pid, flags)
        
        results[name] = {
            "long": xx[0],
            "speed": xx[3] # Used to check Retrograde
        }
        
        if name == 'Rahu':
            # Ketu is exactly 180 degrees from Rahu, always Retrograde logic applies similarly
            results['Ketu'] = {
                "long": (xx[0] + 180) % 360,
                "speed": xx[3] # Inherits node motion
            }

    return results

def perform_gl_calculation(data):
    """
    Main logic function used by the API.
    Calculates Ghatika Lagna (GL) chart.
    """
    # 1. Parsing Input
    user_name = data.get('user_name', 'Unknown')
    birth_date_str = data.get('birth_date')
    birth_time_str = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz_offset = float(data.get('timezone_offset'))

    # 2. DateTime Handling
    local_dt_str = f"{birth_date_str} {birth_time_str}"
    local_dt = datetime.datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M:%S")
    
    # Convert to UTC (Naive arithmetic for simple offset)
    utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
    # Make it timezone-aware for Skyfield
    utc_dt_aware = utc_dt.replace(tzinfo=datetime.timezone.utc)
    
    # 3. Calculate Sunrise
    sunrise_utc = get_precise_sunrise(lat, lon, utc_dt_aware)
    if not sunrise_utc:
        raise ValueError("Could not calculate sunrise. Check coordinates.")
    
    # Calculate Time Difference (Minutes)
    diff = utc_dt_aware - sunrise_utc
    minutes_from_sunrise = diff.total_seconds() / 60
    
    # 4. Planetary Calculations
    jd_birth = get_julian_day(utc_dt)
    planets_data = calculate_planets_yukteswar(jd_birth)
    
    # 5. Calculate Ghatika Lagna (GL)
    # GL = Sidereal Sun + (Minutes from Sunrise * 1.25)
    sun_long = planets_data['Sun']['long']
    gl_movement = minutes_from_sunrise * 1.25
    gl_long = (sun_long + gl_movement) % 360
    
    # 6. Formatting Response Data
    gl_sign_index = int(gl_long / 30) # Used for House Calculation
    
    # Prepare "ascendant" block (Ghatika Lagna details)
    gl_nak, gl_pada = get_nakshatra_details(gl_long)
    gl_sign = get_sign_name(gl_long)
    gl_dms = decimal_to_dms(gl_long % 30) # Degrees within sign
    
    ascendant_data = {
        "degrees": gl_dms,
        "nakshatra": gl_nak,
        "pada": gl_pada,
        "sign": gl_sign
    }
    
    # Prepare "planetary_positions" block
    planetary_positions_data = {}
    sorted_planets = sorted(planets_data.keys()) # Sort alphabetically or custom
    
    for p_name in sorted_planets:
        p_info = planets_data[p_name]
        p_long = p_info['long']
        p_speed = p_info['speed']
        
        p_nak, p_pada = get_nakshatra_details(p_long)
        p_sign = get_sign_name(p_long)
        p_dms = decimal_to_dms(p_long % 30) # Degrees within sign
        
        # Whole Sign House Calculation
        # House = (Planet Sign Index - GL Sign Index) + 1
        p_sign_index = int(p_long / 30)
        house_num = ((p_sign_index - gl_sign_index) % 12) + 1
        
        # Retrograde Logic
        is_retro = "R" if p_speed < 0 else ""
        if p_name in ["Rahu", "Ketu"]:
             is_retro = "R" # Nodes are almost always treated as Retrograde in display
        
        planetary_positions_data[p_name] = {
            "degrees": p_dms,
            "house": house_num,
            "nakshatra": p_nak,
            "pada": p_pada,
            "retrograde": is_retro,
            "sign": p_sign
        }

    # Get Ayanamsa Value for notes
    ayanamsa_val = swe.get_ayanamsa_ut(jd_birth)
    
    # 7. Construct Final JSON
    response = {
        "ascendant": ascendant_data,
        "birth_details": {
            "birth_date": birth_date_str,
            "birth_time": birth_time_str,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz_offset
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val:.6f}",
            "chart_type": "Ghatika Lagna Chart",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions_data,
        "user_name": user_name
    }
    
    return response