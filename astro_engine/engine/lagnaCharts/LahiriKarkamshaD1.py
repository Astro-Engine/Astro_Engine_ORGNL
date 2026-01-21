import os
import math
import swisseph as swe
from datetime import datetime, timedelta

# --- Configuration ---
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- Constants ---
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

NAKSHATRAS = [
    ("Ashwini", 0, 13.333), ("Bharani", 13.333, 26.666), ("Krittika", 26.666, 40),
    ("Rohini", 40, 53.333), ("Mrigashira", 53.333, 66.666), ("Ardra", 66.666, 80),
    ("Punarvasu", 80, 93.333), ("Pushya", 93.333, 106.666), ("Ashlesha", 106.666, 120),
    ("Magha", 120, 133.333), ("Purva Phalguni", 133.333, 146.666), ("Uttara Phalguni", 146.666, 160),
    ("Hasta", 160, 173.333), ("Chitra", 173.333, 186.666), ("Swati", 186.666, 200),
    ("Vishakha", 200, 213.333), ("Anuradha", 213.333, 226.666), ("Jyeshta", 226.666, 240),
    ("Mula", 240, 253.333), ("Purva Ashadha", 253.333, 266.666), ("Uttara Ashadha", 266.666, 280),
    ("Shravana", 280, 293.333), ("Dhanishta", 293.333, 306.666), ("Shatabhisha", 306.666, 320),
    ("Purva Bhadrapada", 320, 333.333), ("Uttara Bhadrapada", 333.333, 346.666), ("Revati", 346.666, 360)
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
}

ELEMENT_NAVAMSA_START = {'Fire': 'Aries', 'Earth': 'Capricorn', 'Air': 'Libra', 'Water': 'Cancer'}
SIGN_ELEMENTS = {
    'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water',
    'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water',
    'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'
}

# --- Helper Functions ---

def to_dms_string(deg_float):
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_julian_day(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def get_sign_and_degree(longitude):
    sign_index = int(longitude // 30)
    degrees_in_sign = longitude % 30
    return SIGNS[sign_index], degrees_in_sign

def get_nakshatra_and_pada(longitude):
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            nakshatra_span = end - start
            pada = math.ceil((longitude - start) / (nakshatra_span / 4))
            return nakshatra, pada
    return "Revati", 4

def get_navamsa_sign(natal_sign, degrees_in_sign):
    element = SIGN_ELEMENTS[natal_sign]
    start_sign = ELEMENT_NAVAMSA_START[element]
    start_index = SIGNS.index(start_sign)
    navamsa_segment = math.floor(degrees_in_sign / (30 / 9)) 
    navamsa_sign_index = (start_index + navamsa_segment) % 12
    return SIGNS[navamsa_sign_index]

# --- Core Calculation Functions ---

def calculate_ascendant(jd, latitude, longitude):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    sign, degrees = get_sign_and_degree(asc_lon)
    nak, pada = get_nakshatra_and_pada(asc_lon)
    return {
        'longitude': asc_lon, 'sign': sign, 'degrees': degrees,
        'nakshatra': nak, 'pada': pada
    }

def calculate_planetary_positions(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']['longitude']
            ketu_lon = (rahu_lon + 180) % 360
            sign, degrees = get_sign_and_degree(ketu_lon)
            nak, pada = get_nakshatra_and_pada(ketu_lon)
            positions['Ketu'] = {
                'longitude': ketu_lon, 'sign': sign, 'degrees': degrees,
                'retrograde': True, 'nakshatra': nak, 'pada': pada
            }
        else:
            pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon = pos[0][0] % 360
            sign, degrees = get_sign_and_degree(lon)
            retrograde = pos[0][3] < 0 if planet not in ['Sun', 'Moon'] else False
            nak, pada = get_nakshatra_and_pada(lon)
            positions[planet] = {
                'longitude': lon, 'sign': sign, 'degrees': degrees,
                'retrograde': retrograde, 'nakshatra': nak, 'pada': pada
            }
    return positions

def find_atmakaraka(positions):
    max_degree = -1
    atmakaraka = None
    planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    for planet in planet_list:
        data = positions[planet]
        if data['degrees'] > max_degree:
            max_degree = data['degrees']
            atmakaraka = planet
    return atmakaraka

def perform_karkamsha_calculation(data):
    """
    Main logic function used by the API.
    Calculates D1 chart rotated to Karkamsha Lagna.
    """
    user_name = data.get('user_name', 'User')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 1. Calculate Standard Positions
    jd = get_julian_day(birth_date, birth_time, tz)
    ayanamsa_val = swe.get_ayanamsa_ut(jd)
    
    # Birth Ascendant (This is what appeared as 'As' in Aries in your image)
    birth_asc = calculate_ascendant(jd, lat, lon)
    
    # Planet Positions
    positions = calculate_planetary_positions(jd)
    
    # 2. Determine Karkamsha (The ACTUAL Ascendant for this chart)
    atmakaraka = find_atmakaraka(positions)
    # Calculate Navamsa Sign of Atmakaraka
    karkamsha_sign = get_navamsa_sign(positions[atmakaraka]['sign'], positions[atmakaraka]['degrees'])
    karkamsha_index = SIGNS.index(karkamsha_sign)

    # 3. Build Response
    # IMPORTANT: 'ascendant' field now represents the CHART's Lagna (Karkamsha)
    response_ascendant = {
        "degrees": "0° 0' 0.00\"", # Karkamsha is a Sign, not a point, so 0 deg is standard
        "nakshatra": "", 
        "pada": 0,
        "sign": karkamsha_sign 
    }

    # 4. Format Planets & Add Birth Ascendant to List
    formatted_planets = {}

    # Add Birth Ascendant (Lagna) as a 'planet' so it gets placed in the chart
    # Calculate house relative to Karkamsha
    birth_asc_sign_idx = SIGNS.index(birth_asc['sign'])
    birth_asc_house = (birth_asc_sign_idx - karkamsha_index) % 12 + 1
    
    formatted_planets["Lagna"] = {
        "degrees": to_dms_string(birth_asc['degrees']),
        "house": birth_asc_house, 
        "nakshatra": birth_asc['nakshatra'],
        "pada": birth_asc['pada'],
        "retrograde": "",
        "sign": birth_asc['sign']
    }

    # Format other planets
    for p_name in PLANETS.keys():
        p_data = positions[p_name]
        p_sign_idx = SIGNS.index(p_data['sign'])
        # House relative to Karkamsha
        p_house = (p_sign_idx - karkamsha_index) % 12 + 1
        
        formatted_planets[p_name] = {
            "degrees": to_dms_string(p_data['degrees']),
            "house": p_house,
            "nakshatra": p_data['nakshatra'],
            "pada": p_data['pada'],
            "retrograde": "R" if p_data['retrograde'] else "",
            "sign": p_data['sign']
        }

    response = {
        "ascendant": response_ascendant,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_val:.6f}",
            "chart_type": "D1 Karkamsha",
            "house_system": "Whole Sign (from Karkamsha)",
            "atmakaraka": atmakaraka,
            "karkamsha_sign": karkamsha_sign,
            "birth_ascendant_sign": birth_asc['sign']
        },
        "planetary_positions": formatted_planets,
        "user_name": user_name
    }
    
    return response