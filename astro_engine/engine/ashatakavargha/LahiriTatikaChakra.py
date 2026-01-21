import os
import datetime
import swisseph as swe

# --- CONFIGURATION ---
# Ensure you have the Swiss Ephemeris files in this directory
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api/ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE  # Mean Node is standard for Vedic
}

# Order for matrix generation
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# --- HELPER FUNCTIONS ---

def decimal_to_dms(deg):
    """Helper to convert decimal degrees to Deg:Min:Sec string"""
    d = int(deg)
    m = int((deg - d) * 60)
    s = round(((deg - d) * 60 - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def get_julian_day(date_str, time_str, tz_offset):
    """Calculates Julian Day (UT) from local time"""
    dt_str = f"{date_str} {time_str}"
    dt_local = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    # Convert Local Time to UTC
    dt_utc = dt_local - datetime.timedelta(hours=float(tz_offset))
    hour_decimal = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)
    return jd

def calculate_tatkalik_relationship(source_sign_index, target_sign_index):
    """
    Calculates Temporal Relationship (Tatkalik Maitri).
    
    Logic:
    - Count signs from Source to Target (inclusive).
    - Friend: 2, 3, 4, 10, 11, 12
    - Enemy: 1, 5, 6, 7, 8, 9
    """
    # Calculate distance (0 to 11)
    # Example: Aries (0) to Taurus (1) -> (1-0)%12 = 1. House = 2.
    distance_index = (target_sign_index - source_sign_index) % 12
    house_position = distance_index + 1  # Convert 0-11 to 1-12 house count

    # Tatkalik Mitra (Temporal Friend) Rule
    if house_position in [2, 3, 4, 10, 11, 12]:
        return "Friend"
    # Tatkalik Shatru (Temporal Enemy) Rule: Houses 1, 5, 6, 7, 8, 9
    else:
        return "Enemy"

def perform_maitri_calculation_lahiri(data):
    """
    Main Logic Function.
    Receives input dictionary, performs calculations, returns result dictionary.
    """
    # 1. Extract Inputs
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 2. Set Ayanamsa to LAHIRI (Chitra Paksha)
    # SIDM_LAHIRI is the standard ID for Lahiri Ayanamsa in Swiss Ephemeris
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # 3. Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz)

    # 4. Calculate Planetary Positions
    # FLG_SIDEREAL is crucial for Vedic
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    
    planet_positions = {}
    
    # Calculate standard planets + Rahu
    for p_name, p_id in PLANET_IDS.items():
        res = swe.calc_ut(jd, p_id, flags)
        lon_deg = res[0][0] # Extract Longitude
        lon_deg = lon_deg % 360
        
        rashi_index = int(lon_deg / 30)
        
        planet_positions[p_name] = {
            "longitude": lon_deg,
            "formatted_dms": decimal_to_dms(lon_deg),
            "rashi_index": rashi_index,
            "rashi_name": RASHI_NAMES[rashi_index],
            "rashi_longitude": decimal_to_dms(lon_deg % 30)
        }

    # Calculate Ketu (Always exactly 180 degrees from Rahu)
    rahu_lon = planet_positions["Rahu"]["longitude"]
    ketu_lon = (rahu_lon + 180) % 360
    ketu_rashi_index = int(ketu_lon / 30)
    
    planet_positions["Ketu"] = {
        "longitude": ketu_lon,
        "formatted_dms": decimal_to_dms(ketu_lon),
        "rashi_index": ketu_rashi_index,
        "rashi_name": RASHI_NAMES[ketu_rashi_index],
        "rashi_longitude": decimal_to_dms(ketu_lon % 30)
    }

    # 5. Calculate Ascendant (Lagna)
    # Using 'W' for Whole Sign houses is common in Vedic for chart display,
    # but Lagna point is calculated specifically here.
    houses_result = swe.houses(jd, lat, lon, b'W')
    ascmc = houses_result[1]
    ascendant_deg = ascmc[0] # The Lagna Degree
    asc_rashi_index = int(ascendant_deg / 30)
    
    # 6. Generate Tatkalik Maitri Matrix
    # This compares every planet against every other planet
    maitri_matrix = []
    
    for source_p in PLANET_ORDER:
        relationships = {}
        source_rashi = planet_positions[source_p]['rashi_index']
        
        for target_p in PLANET_ORDER:
            # A planet cannot have a relationship with itself
            if source_p == target_p:
                relationships[target_p] = "Self"
                continue
            
            target_rashi = planet_positions[target_p]['rashi_index']
            
            # Apply the Tatkalik Logic
            status = calculate_tatkalik_relationship(source_rashi, target_rashi)
            relationships[target_p] = status
        
        maitri_matrix.append({
            "planet": source_p,
            "rashi": planet_positions[source_p]['rashi_name'],
            "relations": relationships
        })

    # 7. Final Response
    response = {
        "meta": {
            "system": "Vedic / Sidereal",
            "ayanamsa": "Lahiri (Chitra Paksha)",
            "house_system": "Whole Sign (Rashi based)",
            "status": "success"
        },
        "user_details": {
            "name": user_name,
            "datetime": f"{birth_date} {birth_time}",
            "lat": lat,
            "lon": lon
        },
        "ascendant": {
            "sign": RASHI_NAMES[asc_rashi_index],
            "degree": decimal_to_dms(ascendant_deg)
        },
        "planetary_positions": planet_positions,
        "tatkalik_maitri_chakra": maitri_matrix
    }
    
    return response