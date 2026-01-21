import os
import math
import datetime
import swisseph as swe

# --- CONFIGURATION ---
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
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

# --- HELPER FUNCTIONS ---

def decimal_to_dms(deg_float):
    """Convert decimal degrees to D° M' S.SS" string."""
    d = int(deg_float)
    m = int((deg_float - d) * 60)
    s = (deg_float - d - m/60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_julian_day(date_str, time_str, tz_offset):
    """Convert Local Date/Time to Julian Day (UT)."""
    dt_str = f"{date_str} {time_str}"
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    
    # Convert to UTC
    utc_dt = dt - datetime.timedelta(hours=float(tz_offset))
    hour_decimal = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    return jd_ut

def get_nakshatra_pada(longitude):
    """Calculate Nakshatra and Pada from absolute longitude."""
    # Total 27 Nakshatras, each 13°20' (13.3333 degrees)
    # 13 degrees 20 minutes = 800 minutes
    # Longitude in minutes
    total_minutes = longitude * 60
    nakshatra_span = 800 # minutes
    
    nakshatra_index = int(total_minutes / nakshatra_span)
    nakshatra_name = NAKSHATRAS[nakshatra_index % 27]
    
    # Remainder gives position within nakshatra
    minutes_in_nak = total_minutes % nakshatra_span
    # Each pada is 3°20' = 200 minutes
    pada = int(minutes_in_nak / 200) + 1
    
    return nakshatra_name, pada

def get_whole_sign_house(planet_sign_id, lagna_sign_id):
    """Calculates Whole Sign House number (1-12)."""
    h = (planet_sign_id - lagna_sign_id) + 1
    if h <= 0:
        h += 12
    return h

def calculate_karakamsha_chart(data):
    """
    Main logic function used by the API.
    Calculates Karakamsha Lagna chart.
    """
    # 1. Parse Inputs
    dob = data.get("birth_date")
    tob = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    user_name = data.get("user_name", "User")

    # 2. Get Julian Day
    jd_ut = get_julian_day(dob, tob, tz)

    # 3. SET AYANAMSA (Sri Yukteswar)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # 4. Calculate Planets
    # Map: Sun=0 to Saturn=6. Rahu=10.
    planet_map = {
        "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, 
        "Mars": 4, "Jupiter": 5, "Saturn": 6, "Rahu": 10
    }
    
    raw_planets = []
    ak_candidates = [] # Sun to Saturn

    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED

    for name, pid in planet_map.items():
        # calc_ut returns ( (long, lat, dist, speed), flags )
        calc_res, _ = swe.calc_ut(jd_ut, pid, flags)
        longitude = calc_res[0]
        speed = calc_res[3]
        
        is_retro = "R" if speed < 0 else ""
        if name in ["Rahu", "Ketu"]: is_retro = "R" # Nodes always retrograde usually
        
        raw_planets.append({
            "name": name,
            "longitude": longitude,
            "pid": pid,
            "retro": is_retro
        })

    # 5. Add Ketu (Rahu + 180)
    rahu_data = next(p for p in raw_planets if p["name"] == "Rahu")
    ketu_lon = (rahu_data["longitude"] + 180.0) % 360.0
    raw_planets.append({
        "name": "Ketu",
        "longitude": ketu_lon,
        "pid": 11,
        "retro": "R"
    })

    # 6. Process Signs & Identify Atmakaraka
    processed_planets = []
    
    for p in raw_planets:
        lon = p["longitude"]
        sign_id = int(lon / 30)
        deg_in_sign = lon % 30
        
        # Navamsha Calculation (D9) for Karakamsha
        nav_abs_lon = (lon * 9) % 360
        nav_sign_id = int(nav_abs_lon / 30)
        
        p_obj = {
            "name": p["name"],
            "longitude": lon,
            "sign_id": sign_id,
            "deg_in_sign": deg_in_sign,
            "nav_sign_id": nav_sign_id,
            "nav_sign_name": ZODIAC_SIGNS[nav_sign_id],
            "retro": p["retro"],
            "pid": p["pid"]
        }
        processed_planets.append(p_obj)
        
        # Add to AK Candidates (Sun to Saturn only)
        if p["pid"] <= 6:
            ak_candidates.append(p_obj)

    # 7. Determine Atmakaraka (AK)
    ak_candidates.sort(key=lambda x: x['deg_in_sign'], reverse=True)
    atmakaraka = ak_candidates[0]
    
    # 8. Determine Karakamsha (Sign of AK in D9)
    # This sign becomes the "Ascendant" for the output chart
    karakamsha_sign_id = atmakaraka['nav_sign_id']
    karakamsha_sign_name = atmakaraka['nav_sign_name']

    # 9. Build Planetary Positions Dictionary
    planetary_positions = {}
    
    for p in processed_planets:
        # Calculate House relative to Karakamsha
        # House 1 = Karakamsha Sign
        house_num = get_whole_sign_house(p['sign_id'], karakamsha_sign_id)
        
        nak_name, pada_num = get_nakshatra_pada(p['longitude'])
        
        planetary_positions[p['name']] = {
            "degrees": decimal_to_dms(p['deg_in_sign']),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": pada_num,
            "retrograde": p['retro'],
            "sign": ZODIAC_SIGNS[p['sign_id']]
        }

    # 10. Construct "Ascendant" Object (Karakamsha Lagna)
    # We use the Karakamsha Sign. For 'degrees', we use the AK's position 
    # as it defines the chart, or 0 if preferred. Here we use AK's degree details.
    ak_nak, ak_pada = get_nakshatra_pada(atmakaraka['longitude'])
    
    ascendant_obj = {
        "degrees": decimal_to_dms(atmakaraka['deg_in_sign']),
        "nakshatra": ak_nak,
        "pada": ak_pada,
        "sign": karakamsha_sign_name # THIS is the critical part (Calculated Karakamsha)
    }

    # 11. Final Response Structure
    response = {
        "ascendant_karkamsha": ascendant_obj,
        "birth_details": {
            "birth_date": dob,
            "birth_time": tob,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar", # Correctly labeling the calculation used
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "Karakamsha Lagna",
            "house_system": "Whole Sign (Karakamsha = House 1)"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }

    return response