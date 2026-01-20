import swisseph as swe
import datetime
import os
import math

# --- CONFIGURATION ---
# Ensure you have the Swiss Ephemeris files in this path
EPHEMERIS_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHEMERIS_PATH)

# Planet Mapping
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": None # Calculated from Rahu
}

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def format_dms(deg):
    """Formats degrees into the specific string format: 8° 21' 6.44" """
    d = int(deg)
    m = int((deg - d) * 60)
    s = ((deg - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    # Convert to UTC
    utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    return jd

def get_d2_sign_index(lon):
    """
    Calculates the D2 (Hora) Sign Index (0-11) based on Parashara rules.
    Odd Signs: 0-15 Leo, 15-30 Cancer
    Even Signs: 0-15 Cancer, 15-30 Leo
    """
    normalized_lon = lon % 360
    d1_sign_index = int(normalized_lon / 30)
    degree_in_sign = normalized_lon % 30
    
    # 0=Aries (Odd), 1=Taurus (Even), 2=Gemini (Odd)...
    # Even Index = Odd Sign | Odd Index = Even Sign
    is_odd_sign = (d1_sign_index % 2 == 0)
    
    # Leo is index 4, Cancer is index 3
    if is_odd_sign:
        if degree_in_sign < 15:
            return 4 # Leo
        else:
            return 3 # Cancer
    else: # Even Sign
        if degree_in_sign < 15:
            return 3 # Cancer
        else:
            return 4 # Leo

def calculate_whole_sign_house(planet_sign_index, asc_sign_index):
    """Calculates house number (1-12) based on Whole Sign system."""
    return (planet_sign_index - asc_sign_index + 12) % 12 + 1

def perform_d2_calculation(data):
    """
    Main logic function used by the API.
    """
    # 1. Parse Input
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 2. Time Calculation
    jd_ut = get_julian_day(birth_date, birth_time, tz)

    # 3. Set Sidereal Mode to Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # Get Ayanamsa value for notes
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # 4. Calculate Ascendant
    # We need the Ascendant longitude to determine the D2 Lagna
    flags = swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', flags)
    asc_lon = ascmc[0]
    
    # Determine D2 Ascendant Sign
    d2_asc_sign_index = get_d2_sign_index(asc_lon)
    d2_asc_sign_name = SIGN_NAMES[d2_asc_sign_index]

    # 5. Calculate Planets
    planetary_positions = {}
    
    # We sort keys to match typical output order if needed
    planet_keys = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for p_name in planet_keys:
        pid = PLANETS[p_name]
        
        # Calculate Longitude
        if p_name == "Ketu":
            # Ketu is opposite Rahu
            rahu_data = swe.calc_ut(jd_ut, swe.MEAN_NODE, flags)[0]
            lon_deg = (rahu_data[0] + 180.0) % 360.0
            speed = rahu_data[3] # Use Rahu's speed
        else:
            xx, _ = swe.calc_ut(jd_ut, pid, flags)
            lon_deg = xx[0]
            speed = xx[3]

        # Determine Retrograde status
        is_retro = "R" if speed < 0 else ""
        if p_name in ["Rahu", "Ketu"]:
                # Nodes are naturally retrograde, usually marked R only if True Node varies, 
                # but for Mean Node they are always Retrograde. 
                # Standard practice: Mark R if moving backwards (which they do).
                is_retro = "R" 

        # Calculate D2 Sign
        d2_sign_idx = get_d2_sign_index(lon_deg)
        d2_sign_name = SIGN_NAMES[d2_sign_idx]

        # Calculate D2 House (Whole Sign relative to D2 Ascendant)
        d2_house = calculate_whole_sign_house(d2_sign_idx, d2_asc_sign_index)
        
        # Format degree relative to sign (0-30) for display in "degrees" field
        # Note: For D2, the "degree" is technically the D1 longitude, 
        # as D2 planets don't have independent degrees in standard output.
        # We preserve the D1 degree for reference, formatted.
        degree_in_sign = lon_deg % 30

        planetary_positions[p_name] = {
            "degrees": format_dms(degree_in_sign),
            "house": d2_house,
            "retrograde": is_retro,
            "sign": d2_sign_name
        }

    # 6. Construct Final Response
    response = {
        "ascendant": {
            "degrees": format_dms(asc_lon % 30),
            "sign": d2_asc_sign_name
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
            "ayanamsa_value": f"{ayanamsa_val}",
            "chart_type": "D2 Hora",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }

    return response