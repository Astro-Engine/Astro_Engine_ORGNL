import os
import math
import datetime
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS & LISTS
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

PLANET_MAPPING = {
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

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def decimal_to_dms(deg_float):
    """Converts decimal degrees to D° M' S" string format."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_pada(longitude):
    """Calculates Nakshatra and Pada based on 0-360 longitude."""
    longitude = longitude % 360
    nak_duration = 360.0 / 27.0
    nak_index = int(longitude / nak_duration)
    
    remainder = longitude - (nak_index * nak_duration)
    pada_duration = nak_duration / 4.0
    pada = int(remainder / pada_duration) + 1
    
    return NAKSHATRAS[nak_index], pada

def calculate_d10_data(longitude):
    """
    Calculates D10 Sign, D10 Longitude (0-360 representation), and D10 Sign Index.
    
    Logic:
    1. D10 Part = (Lon % 30) / 3
    2. Sign Logic (Odd/Even)
    3. The "degrees" inside a D10 chart are calculated by expanding the 3° arc back to 30°.
       D10_Longitude_In_Sign = (D1_Degree_In_Part * 10)
    """
    d1_lon = longitude % 360
    d1_sign_idx = int(d1_lon / 30)
    d1_deg_in_sign = d1_lon % 30
    
    # Each D10 part is 3 degrees
    d10_part_idx = int(d1_deg_in_sign / 3) # 0 to 9
    
    # Exact position within the 3 degree part (0.0 to 3.0)
    deg_in_part = d1_deg_in_sign % 3
    
    # Expand to 30 degrees for D10 representation
    d10_deg_in_sign = deg_in_part * 10 
    
    # Determine D10 Sign
    is_odd_sign = (d1_sign_idx % 2 == 0) # Aries=0 (Even Index) -> Odd Sign
    
    if is_odd_sign:
        # Count forward from sign itself
        d10_sign_idx = (d1_sign_idx + d10_part_idx) % 12
    else:
        # Count forward from 9th sign
        ninth_from_curr = (d1_sign_idx + 8) % 12
        d10_sign_idx = (ninth_from_curr + d10_part_idx) % 12
        
    # Absolute longitude in D10 zodiac (0-360)
    # Used for Nakshatra calculation of the D10 position
    d10_abs_lon = (d10_sign_idx * 30) + d10_deg_in_sign
    
    return {
        "sign_idx": d10_sign_idx,
        "sign_name": ZODIAC_SIGNS[d10_sign_idx],
        "deg_in_sign": d10_deg_in_sign,
        "abs_lon": d10_abs_lon
    }

def get_whole_sign_house(planet_sign_idx, asc_sign_idx):
    house = (planet_sign_idx - asc_sign_idx) + 1
    if house <= 0:
        house += 12
    return house

def perform_d10_calculation(data):
    """
    Main logic function used by the API.
    """
    # 1. Parse Input
    date_str = data.get('birth_date')
    time_str = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz_offset = float(data.get('timezone_offset'))
    
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    
    # 2. Time Conversion
    decimal_time = hour + (minute / 60.0) + (second / 3600.0)
    decimal_time_utc = decimal_time - tz_offset
    
    if decimal_time_utc < 0:
        decimal_time_utc += 24
        dt_obj = datetime.datetime(year, month, day) - datetime.timedelta(days=1)
        year, month, day = dt_obj.year, dt_obj.month, dt_obj.day
    elif decimal_time_utc >= 24:
        decimal_time_utc -= 24
        dt_obj = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
        year, month, day = dt_obj.year, dt_obj.month, dt_obj.day

    jul_day_utc = swe.julday(year, month, day, decimal_time_utc)
    
    # 3. Set Ayanamsa: Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day_utc)

    # 4. Calculate Ascendant (D1 -> D10)
    # Get Tropical Asc first
    swe.set_sid_mode(0, 0, 0)
    cusps_trop, ascmc_trop = swe.houses(jul_day_utc, lat, lon, b'P')
    asc_tropical = ascmc_trop[0]
    
    # Convert to Sri Yukteswar Sidereal D1
    asc_d1_sidereal = (asc_tropical - ayanamsa_val) % 360
    
    # Calculate D10 Ascendant
    asc_d10_data = calculate_d10_data(asc_d1_sidereal)
    asc_nak, asc_pada = get_nakshatra_pada(asc_d10_data['abs_lon'])
    
    # Prepare Response Object
    response = {
        "ascendant": {
            "degrees": decimal_to_dms(asc_d10_data['deg_in_sign']),
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "sign": asc_d10_data['sign_name']
        },
        "birth_details": {
            "birth_date": date_str,
            "birth_time": time_str,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz_offset
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "D10",
            "house_system": "Whole Sign"
        },
        "planetary_positions": {},
        "user_name": data.get("user_name")
    }
    
    # 5. Calculate Planets (D1 -> D10)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    for p_name, p_id in PLANET_MAPPING.items():
        if p_name == "Ketu":
            continue 
        
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        res = swe.calc_ut(jul_day_utc, p_id, flags)
        
        d1_lon = res[0][0]
        speed = res[0][3]
        
        # Calculate D10 Data
        d10_data = calculate_d10_data(d1_lon)
        
        # Calculate House relative to D10 Ascendant
        house_num = get_whole_sign_house(d10_data['sign_idx'], asc_d10_data['sign_idx'])
        
        # Calculate Nakshatra of the D10 Position
        nak, pada = get_nakshatra_pada(d10_data['abs_lon'])
        
        planet_entry = {
            "degrees": decimal_to_dms(d10_data['deg_in_sign']),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": "R" if speed < 0 else "",
            "sign": d10_data['sign_name']
        }
        
        response["planetary_positions"][p_name] = planet_entry
        
        # Handle Ketu
        if p_name == "Rahu":
            ketu_d1_lon = (d1_lon + 180) % 360
            
            k_d10_data = calculate_d10_data(ketu_d1_lon)
            k_house = get_whole_sign_house(k_d10_data['sign_idx'], asc_d10_data['sign_idx'])
            k_nak, k_pada = get_nakshatra_pada(k_d10_data['abs_lon'])
            
            response["planetary_positions"]["Ketu"] = {
                "degrees": decimal_to_dms(k_d10_data['deg_in_sign']),
                "house": k_house,
                "nakshatra": k_nak,
                "pada": k_pada,
                "retrograde": "R" if speed < 0 else "",
                "sign": k_d10_data['sign_name']
            }
            
    return response