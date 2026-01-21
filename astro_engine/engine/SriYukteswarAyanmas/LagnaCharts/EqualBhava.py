import os
import swisseph as swe

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
# Path to Swiss Ephemeris files (astro_api/ephe relative to script)
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Sri Yukteswar Ayanamsa ID in Swiss Ephemeris
# 7 = SE_SIDM_YUKTESHWAR
AYANAMSA_MODE = 7 

# Nakshatra Names List
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", 
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", 
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", 
    "Uttara Bhadrapada", "Revati"
]

# Zodiac Signs List
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------

def to_dms_str(deg):
    """
    Converts decimal degrees to D° M' S.SS" string format.
    Example: 8.3517 -> 8° 21' 6.44"
    """
    d = int(deg)
    mins = (deg - d) * 60
    m = int(mins)
    secs = (mins - m) * 60
    # Format seconds to 2 decimal places to match sample
    return f"{d}° {m}' {secs:.2f}\""

def get_nakshatra_pada(longitude):
    """
    Calculates Nakshatra and Pada from absolute longitude (0-360).
    """
    # Each Nakshatra is 13° 20' (13.3333... degrees)
    nak_span = 360.0 / 27.0
    
    # Nakshatra Index (0-26)
    nak_index = int(longitude / nak_span)
    nak_name = NAKSHATRAS[nak_index % 27]
    
    # Degrees traversed within the specific Nakshatra
    rem_deg = longitude - (nak_index * nak_span)
    
    # Each Pada is 3° 20' (3.3333... degrees)
    pada_span = nak_span / 4.0
    pada = int(rem_deg / pada_span) + 1
    
    return nak_name, pada

def get_sign_data(longitude):
    """
    Returns the Sign Name and the Index (0-11).
    """
    index = int(longitude / 30)
    return SIGNS[index % 12], (index % 12)

def calculate_julian_day(date_str, time_str, tz_offset):
    """
    Calculates UT Julian Day.
    """
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    
    # Decimal hour in Local Time
    decimal_time = hour + (minute / 60.0) + (second / 3600.0)
    
    # Convert to UTC
    decimal_time_utc = decimal_time - float(tz_offset)
    
    return swe.julday(year, month, day, decimal_time_utc)

# -------------------------------------------------------------------------
# MAIN CALCULATION LOGIC
# -------------------------------------------------------------------------

def equal_bhava_chart(user_name, birth_date, birth_time, lat, lon, tz):
    
    # 1. Calculate Julian Day
    jd = calculate_julian_day(birth_date, birth_time, tz)
    
    # 2. Set Sidereal Mode (Sri Yukteswar)
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    
    # 3. Get Ayanamsa Value (for Notes)
    ayanamsa_val = swe.get_ayanamsa_ut(jd)
    
    # 4. Calculate Ascendant
    # We use 'P' (Placidus) to get the Ascendant degree correctly, 
    # but we will ignore the house cusps for the Whole Sign logic.
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc_deg_abs = ascmc[0] # Ascendant Longitude
    
    # Ascendant Details
    asc_sign_name, asc_sign_index = get_sign_data(asc_deg_abs)
    asc_nak, asc_pada = get_nakshatra_pada(asc_deg_abs)
    asc_deg_in_sign = asc_deg_abs % 30
    
    ascendant_data = {
        "degrees": to_dms_str(asc_deg_in_sign),
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": asc_sign_name
    }
    
    # 5. Calculate Planets
    # Mapping of planet names to Swiss Ephemeris IDs
    planet_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE # Using Mean Node
    }
    
    planetary_positions = {}
    
    # Common flags: Sidereal + Swiss Ephemeris Precision + Speed (for retro)
    calc_flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # Loop standard planets + Rahu
    for p_name, p_id in planet_map.items():
        res = swe.calc_ut(jd, p_id, calc_flags)
        lon_abs = res[0][0]
        speed = res[0][3]
        
        # Retrograde check
        is_retro = "R" if speed < 0 else ""
        if p_name in ["Rahu", "Ketu"]:
            is_retro = "R" # Nodes are almost always treated as Retro in display
            
        # Sign & House
        sign_name, sign_index = get_sign_data(lon_abs)
        
        # Whole Sign House Logic:
        # House = (PlanetSignIndex - AscSignIndex) + 1
        # Example: Asc in Aries(0), Sun in Aries(0) -> (0-0)+1 = 1st House
        # Example: Asc in Aries(0), Sun in Taurus(1) -> (1-0)+1 = 2nd House
        house_num = ((sign_index - asc_sign_index) % 12) + 1
        
        # Nakshatra
        nak, pada = get_nakshatra_pada(lon_abs)
        
        # Degrees in Sign
        deg_in_sign = lon_abs % 30
        
        planetary_positions[p_name] = {
            "degrees": to_dms_str(deg_in_sign),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": sign_name
        }
        
    # 6. Calculate Ketu (Opposite Rahu) manually
    rahu_data = planetary_positions["Rahu"]
    # We need the absolute longitude of Rahu to add 180
    # Re-calculating briefly or reconstructing from sign is risky due to precision.
    # Better to fetch Rahu lon again.
    res_rahu = swe.calc_ut(jd, swe.MEAN_NODE, calc_flags)
    rahu_lon_abs = res_rahu[0][0]
    
    ketu_lon_abs = (rahu_lon_abs + 180.0) % 360.0
    
    k_sign_name, k_sign_index = get_sign_data(ketu_lon_abs)
    k_house_num = ((k_sign_index - asc_sign_index) % 12) + 1
    k_nak, k_pada = get_nakshatra_pada(ketu_lon_abs)
    k_deg_in_sign = ketu_lon_abs % 30
    
    planetary_positions["Ketu"] = {
        "degrees": to_dms_str(k_deg_in_sign),
        "house": k_house_num,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "R",
        "sign": k_sign_name
    }
    
    # 7. Sort Dictionary alphabetically to match sample look (optional but good)
    sorted_positions = dict(sorted(planetary_positions.items()))

    # 8. Construct Final JSON
    response = {
        "ascendant": ascendant_data,
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
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        },
        "planetary_positions": sorted_positions,
        "user_name": user_name
    }
    
    return response