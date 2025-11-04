# import swisseph as swe
# from datetime import datetime, timedelta
# import math

# # Set Swiss Ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# # Zodiac signs (0-based index: Aries = 0, Pisces = 11)
# SIGNS = [
#     'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
#     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
# ]

# # Shashtiamsha deities list (1 to 60, as per Brihat Parashara Hora Shastra)
# SHASHTIAMSHA_DEITIES = [
#     "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulagna",
#     "Garala", "Vahni", "Maya", "Purishaka", "Apampathi", "Marut", "Kala", "Sarpa",
#     "Amrita", "Indu", "Mridu", "Komal", "Heramba", "Brahma", "Vishnu", "Maheshwara",
#     "Deva", "Ardra", "Kala", "Kshiti", "Kamalakara", "Gulika", "Mrityu", "Kaala",
#     "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
#     "Kulanashta", "Vamsakshaya", "Utpata", "Kala", "Saumya", "Komala", "Sheetala", "Karaladamshtra",
#     "Chandramukhi", "Praveena", "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Kroora", "Atisheetala",
#     "Amrita", "Payodhi", "Brahmana", "Indu Rekha"
# ]

# # Nakshatras (27 lunar mansions, each spanning 13°20')
# NAKSHATRAS = [
#     'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
#     'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
#     'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
#     'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
#     'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
# ]

# def get_julian_day(date_str, time_str, tz_offset):
#     """
#     Convert birth date, time, and timezone offset to Julian Day (UT).
    
#     Args:
#         date_str (str): Birth date in 'YYYY-MM-DD' format.
#         time_str (str): Birth time in 'HH:MM:SS' format.
#         tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST).
    
#     Returns:
#         float: Julian Day in Universal Time.
#     """
#     date_obj = datetime.strptime(date_str, '%Y-%m-%d')
#     time_obj = datetime.strptime(time_str, '%H:%M:%S')
#     local_dt = datetime.combine(date_obj, time_obj.time())
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
#     return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

# def get_sidereal_longitude(jd_ut, planet_id, ascendant=False, lat=None, lon=None):
#     """
#     Calculate sidereal longitude for a planet or ascendant using Lahiri Ayanamsa.
    
#     Args:
#         jd_ut (float): Julian Day in UT.
#         planet_id (int): Swiss Ephemeris planet ID (e.g., swe.SUN) or None for ascendant.
#         ascendant (bool): True if calculating for ascendant, False for planets.
#         lat (float): Latitude (required for ascendant).
#         lon (float): Longitude (required for ascendant).
    
#     Returns:
#         tuple: (longitude, retrograde flag) where longitude is 0-360° and retrograde is 'R' or ''.
#     """
#     swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
#     flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
#     if ascendant:
#         if lat is None or lon is None:
#             raise ValueError("Latitude and longitude required for ascendant calculation")
#         cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
#         return ascmc[0] % 360, ''
#     else:
#         pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
#         longitude = pos[0] % 360
#         retrograde = 'R' if pos[3] < 0 else ''
#         return longitude, retrograde

# def get_d60_position(sidereal_lon):
#     """
#     Calculate D60 sign and Shashtiamsha number from sidereal longitude.
    
#     Args:
#         sidereal_lon (float): Sidereal longitude in degrees (0-360°).
    
#     Returns:
#         dict: D60 sign, sign index, Shashtiamsha number, and deity.
#     """
#     natal_sign_index = int(sidereal_lon // 30)
#     natal_degrees = sidereal_lon % 30
#     y = natal_degrees * 2
#     remainder = y % 12
#     count = math.floor(remainder) + 1
#     d60_sign_index = (natal_sign_index + count - 1) % 12
#     shashtiamsha_number = math.floor(natal_degrees / 0.5) + 1
#     if shashtiamsha_number > 60:
#         shashtiamsha_number = 60
#     deity = SHASHTIAMSHA_DEITIES[shashtiamsha_number - 1]
#     return {
#         "sign": SIGNS[d60_sign_index],
#         "sign_index": d60_sign_index,
#         "shashtiamsha": shashtiamsha_number,
#         "deity": deity,
#         "longitude": sidereal_lon
#     }

# def get_d60_house(d60_sign_index, d60_asc_sign_index):
#     """
#     Assign house number using Whole Sign system.
    
#     Args:
#         d60_sign_index (int): D60 sign index of the planet (0-11).
#         d60_asc_sign_index (int): D60 ascendant sign index (0-11).
    
#     Returns:
#         int: House number (1-12).
#     """
#     return (d60_sign_index - d60_asc_sign_index) % 12 + 1

# def format_dms(degrees):
#     """
#     Format longitude in degrees, minutes, seconds (e.g., 17°41'36").
    
#     Args:
#         degrees (float): Longitude in decimal degrees.
    
#     Returns:
#         str: Formatted string in D°M'S" format.
#     """
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = (degrees - d - m / 60) * 3600
#     return f"{d}°{m}'{s:.1f}\""

# def get_nakshatra_and_pada(longitude):
#     """
#     Calculate nakshatra and pada from longitude.
    
#     Args:
#         longitude (float): Sidereal longitude in degrees (0-360°).
    
#     Returns:
#         dict: Nakshatra name and pada number (1-4).
#     """
#     nakshatra_index = int(longitude / (360 / 27)) % 27
#     pada = int((longitude % (360 / 27)) / (360 / 108)) + 1
#     nakshatra = NAKSHATRAS[nakshatra_index]
#     return {"nakshatra": nakshatra, "pada": pada}

# def lahairi_Shashtiamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
#     """
#     Calculate the D60 (Shashtiamsha) chart including nakshatras and padas.
    
#     Args:
#         birth_date (str): Birth date in 'YYYY-MM-DD' format.
#         birth_time (str): Birth time in 'HH:MM:SS' format.
#         latitude (float): Latitude of birth place.
#         longitude (float): Longitude of birth place.
#         tz_offset (float): Timezone offset in hours.
#         user_name (str): Name of the user (optional).
    
#     Returns:
#         dict: D60 chart details including ascendant, planetary positions, house signs, and metadata.
#     """
#     # Step 1: Calculate Julian Day
#     jd_ut = get_julian_day(birth_date, birth_time, tz_offset)

#     # Step 2: Calculate sidereal longitudes for planets
#     planets = [
#         (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
#         (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
#         (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
#     ]
#     d1_positions = {}
#     for planet_id, name in planets:
#         lon, retro = get_sidereal_longitude(jd_ut, planet_id)
#         d1_positions[name] = (lon, retro)

#     # Calculate Ketu (180° opposite Rahu)
#     rahu_lon = d1_positions['Rahu'][0]
#     ketu_lon = (rahu_lon + 180) % 360
#     d1_positions['Ketu'] = (ketu_lon, 'R')  # Ketu is always retrograde

#     # Step 3: Calculate ascendant sidereal longitude
#     d1_asc_lon, _ = get_sidereal_longitude(jd_ut, None, ascendant=True, lat=latitude, lon=longitude)

#     # Step 4: Calculate D60 ascendant
#     d60_asc = get_d60_position(d1_asc_lon)
#     d60_asc_sign_index = d60_asc['sign_index']

#     # Step 5: Calculate D60 positions for all planets with nakshatras and padas
#     d60_positions = {}
#     for planet, (d1_lon, retro) in d1_positions.items():
#         d60_pos = get_d60_position(d1_lon)
#         house = get_d60_house(d60_pos['sign_index'], d60_asc_sign_index)
#         nakshatra_pada = get_nakshatra_and_pada(d1_lon)
#         d60_positions[planet] = {
#             "sign": d60_pos['sign'],
#             # "shashtiamsha": d60_pos['shashtiamsha'],
#             # "deity": d60_pos['deity'],
#             "house": house,
#             "retrograde": retro,
#             "longitude": format_dms(d1_lon),
#             "nakshatra": nakshatra_pada["nakshatra"],
#             "pada": nakshatra_pada["pada"]
#         }

#     # Step 6: Assign house signs using Whole Sign system
#     house_signs = [
#         {"house": i + 1, "sign": SIGNS[(d60_asc_sign_index + i) % 12]} 
#         for i in range(12)
#     ]

#     # Step 7: Calculate ascendant nakshatra and pada
#     asc_nakshatra_pada = get_nakshatra_and_pada(d1_asc_lon)

#     # Step 8: Construct response
#     response = {
#         "user_name": user_name,
#         "ascendant": {
#             "sign": d60_asc['sign'],
#             # "shashtiamsha": d60_asc['shashtiamsha'],
#             # "deity": d60_asc['deity'],
#             "longitude": format_dms(d1_asc_lon),
#             "nakshatra": asc_nakshatra_pada["nakshatra"],
#             "pada": asc_nakshatra_pada["pada"]
#         },
#         "planetary_positions": d60_positions,
#         # "house_signs": house_signs,
#         "metadata": {
#             "ayanamsa": "Lahiri",
#             "chart_type": "Shashtiamsha (D60)",
#             "house_system": "Whole Sign",
#             "calculation_time": datetime.utcnow().isoformat()
#         }
#     }
#     return response






import swisseph as swe
from datetime import datetime, timedelta
import math

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs (0-based index: Aries = 0, Pisces = 11)
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Shashtiamsha deities list (1 to 60, as per Brihat Parashara Hora Shastra)
SHASHTIAMSHA_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulagna",
    "Garala", "Vahni", "Maya", "Purishaka", "Apampathi", "Marut", "Kala", "Sarpa",
    "Amrita", "Indu", "Mridu", "Komal", "Heramba", "Brahma", "Vishnu", "Maheshwara",
    "Deva", "Ardra", "Kala", "Kshiti", "Kamalakara", "Gulika", "Mrityu", "Kaala",
    "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
    "Kulanashta", "Vamsakshaya", "Utpata", "Kala", "Saumya", "Komala", "Sheetala", "Karaladamshtra",
    "Chandramukhi", "Praveena", "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Kroora", "Atisheetala",
    "Amrita", "Payodhi", "Brahmana", "Indu Rekha"
]

# Nakshatras (27 lunar mansions, each spanning 13°20')
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Convert birth date, time, and timezone offset to Julian Day (UT).
    
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format.
        time_str (str): Birth time in 'HH:MM:SS' format.
        tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST).
    
    Returns:
        float: Julian Day in Universal Time.
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def get_sidereal_longitude(jd_ut, planet_id, ascendant=False, lat=None, lon=None):
    """
    Calculate sidereal longitude for a planet or ascendant using Lahiri Ayanamsa.
    
    Args:
        jd_ut (float): Julian Day in UT.
        planet_id (int): Swiss Ephemeris planet ID (e.g., swe.SUN) or None for ascendant.
        ascendant (bool): True if calculating for ascendant, False for planets.
        lat (float): Latitude (required for ascendant).
        lon (float): Longitude (required for ascendant).
    
    Returns:
        tuple: (longitude, retrograde flag) where longitude is 0-360° and retrograde is 'R' or ''.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    if ascendant:
        if lat is None or lon is None:
            raise ValueError("Latitude and longitude required for ascendant calculation")
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
        return ascmc[0] % 360, ''
    else:
        pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
        longitude = pos[0] % 360
        retrograde = 'R' if pos[3] < 0 else ''
        return longitude, retrograde

def get_d60_position(sidereal_lon):
    """
    Calculate D60 sign and Shashtiamsha number from sidereal longitude.
    
    Args:
        sidereal_lon (float): Sidereal longitude in degrees (0-360°).
    
    Returns:
        dict: D60 sign, sign index, Shashtiamsha number, and deity.
    """
    natal_sign_index = int(sidereal_lon // 30)
    natal_degrees = sidereal_lon % 30
    y = natal_degrees * 2
    remainder = y % 12
    count = math.floor(remainder) + 1
    d60_sign_index = (natal_sign_index + count - 1) % 12
    shashtiamsha_number = math.floor(natal_degrees / 0.5) + 1
    if shashtiamsha_number > 60:
        shashtiamsha_number = 60
    deity = SHASHTIAMSHA_DEITIES[shashtiamsha_number - 1]
    return {
        "sign": SIGNS[d60_sign_index],
        "sign_index": d60_sign_index,
        "shashtiamsha": shashtiamsha_number,
        "deity": deity,
        "longitude": sidereal_lon
    }

def get_d60_house(d60_sign_index, d60_asc_sign_index):
    """
    Assign house number using Whole Sign system.
    
    Args:
        d60_sign_index (int): D60 sign index of the planet (0-11).
        d60_asc_sign_index (int): D60 ascendant sign index (0-11).
    
    Returns:
        int: House number (1-12).
    """
    return (d60_sign_index - d60_asc_sign_index) % 12 + 1

def format_dms(degrees):
    """
    Format longitude in degrees, minutes, seconds (e.g., 17°41'36").
    
    Args:
        degrees (float): Longitude in decimal degrees.
    
    Returns:
        str: Formatted string in D°M'S" format.
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int((degrees - d - m / 60) * 3600)
    return f"{d:02d}°{m:02d}'{s:02d}\""

def get_nakshatra_and_pada(longitude):
    """
    Calculate nakshatra and pada from longitude.
    
    Args:
        longitude (float): Sidereal longitude in degrees (0-360°).
    
    Returns:
        dict: Nakshatra name and pada number (1-4).
    """
    nakshatra_index = int(longitude / (360 / 27)) % 27
    pada = int((longitude % (360 / 27)) / (360 / 108)) + 1
    nakshatra = NAKSHATRAS[nakshatra_index]
    return {"nakshatra": nakshatra, "pada": pada}

def lahairi_Shashtiamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """Calculate D60 chart and format response exactly like the natal chart."""
    # Step 1: Calculate Julian Day
    jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
    
    # Get ayanamsa value
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # Step 2: Calculate sidereal longitudes for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    d1_positions = {}
    for planet_id, name in planets:
        lon, retro = get_sidereal_longitude(jd_ut, planet_id)
        d1_positions[name] = (lon, retro)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, 'R')  # Ketu is always retrograde

    # Step 3: Calculate ascendant sidereal longitude
    d1_asc_lon, _ = get_sidereal_longitude(jd_ut, None, ascendant=True, lat=latitude, lon=longitude)

    # Step 4: Calculate D60 ascendant
    d60_asc = get_d60_position(d1_asc_lon)
    d60_asc_sign_index = d60_asc['sign_index']
    
    # Get degree within sign for ascendant
    asc_deg_in_sign = d1_asc_lon % 30
    asc_dms = format_dms(asc_deg_in_sign)
    
    # Calculate ascendant nakshatra and pada
    asc_nakshatra_pada = get_nakshatra_and_pada(d1_asc_lon)

    # Ascendant block
    ascendant_json = {
        "sign": d60_asc['sign'],
        "degrees": asc_dms,
        "nakshatra": asc_nakshatra_pada["nakshatra"],
        "pada": asc_nakshatra_pada["pada"]
    }

    # Step 5: Calculate D60 positions for all planets
    planetary_positions_json = {}
    
    PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    for planet in PLANET_NAMES:
        d1_lon, retro = d1_positions[planet]
        d60_pos = get_d60_position(d1_lon)
        house = get_d60_house(d60_pos['sign_index'], d60_asc_sign_index)
        nakshatra_pada = get_nakshatra_and_pada(d1_lon)
        
        # Get degree within sign
        deg_in_sign = d1_lon % 30
        dms = format_dms(deg_in_sign)
        
        planetary_positions_json[planet] = {
            "sign": d60_pos['sign'],
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "nakshatra": nakshatra_pada["nakshatra"],
            "pada": nakshatra_pada["pada"]
        }

    # Return with extra ayanamsa for notes
    return {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "ayanamsa_value": float(ayanamsa)
    }

