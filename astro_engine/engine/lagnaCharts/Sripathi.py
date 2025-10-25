# import swisseph as swe
# from datetime import datetime, timedelta
# import math

# swe.set_sid_mode(swe.SIDM_LAHIRI)

# # Constants
# SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# PLANET_IDS = {
#     'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
#     'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
#     'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu calculated separately
# }

# # Nakshatra list with start degrees (27 nakshatras, each 13°20' or 13.3333°)
# NAKSHATRAS = [
#     ("Ashwini", 0), ("Bharani", 13.3333), ("Krittika", 26.6667), ("Rohini", 40),
#     ("Mrigashira", 53.3333), ("Ardra", 66.6667), ("Punarvasu", 80), ("Pushya", 93.3333),
#     ("Ashlesha", 106.6667), ("Magha", 120), ("Purva Phalguni", 133.3333), ("Uttara Phalguni", 146.6667),
#     ("Hasta", 160), ("Chitra", 173.3333), ("Swati", 186.6667), ("Vishakha", 200),
#     ("Anuradha", 213.3333), ("Jyeshtha", 226.6667), ("Mula", 240), ("Purva Ashadha", 253.3333),
#     ("Uttara Ashadha", 266.6667), ("Shravana", 280), ("Dhanishta", 293.3333), ("Shatabhisha", 306.6667),
#     ("Purva Bhadrapada", 320), ("Uttara Bhadrapada", 333.3333), ("Revati", 346.6667)
# ]

# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert local birth date and time to Julian Day in UT."""
#     dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
#     ut_dt = dt - timedelta(hours=tz_offset)
#     jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
#     return jd

# def calculate_ascendant(jd, lat, lon):
#     """Calculate the ascendant longitude and house cusps using Sripathi Bhava system."""
#     cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)  # 'S' for Sripathi
#     asc_lon = ascmc[0] % 360  # Ascendant longitude
#     asc_sign_index = math.floor(asc_lon / 30)
#     return asc_lon, asc_sign_index, cusps

# def calculate_house(planet_lon, cusps):
#     """Determine house number using Sripathi Bhava cusps."""
#     planet_lon = planet_lon % 360

#     for i in range(12):
#         cusp_start = cusps[i] % 360
#         cusp_end = cusps[(i + 1) % 12] % 360
#         if cusp_start < cusp_end:
#             if cusp_start <= planet_lon < cusp_end:
#                 return i + 1
#         else:  # Handle wrap-around at 360°
#             if planet_lon >= cusp_start or planet_lon < cusp_end:
#                 return i + 1
#     return 12  # Default to House 12 if not found

# def get_nakshatra_and_pada(longitude):
#     """Determine the nakshatra and pada based on longitude."""
#     longitude = longitude % 360
#     for i, (nakshatra, start) in enumerate(NAKSHATRAS):
#         end = NAKSHATRAS[(i + 1) % len(NAKSHATRAS)][1] if i < 26 else 360
#         if start <= longitude < end:
#             nakshatra_name = nakshatra
#             # Calculate pada: each pada is 3°20' (3.3333°)
#             pada = math.ceil((longitude - start) / 3.3333)
#             if pada > 4:  # Ensure pada doesn't exceed 4
#                 pada = 4
#             return nakshatra_name, pada
#     return "Revati", 4  # Fallback for edge case

# def get_planet_data(jd, asc_lon, cusps):
#     """Calculate planetary positions, signs, degrees, retrograde status, nakshatras, padas, and houses."""
#     natal_positions = {}
#     for planet, pid in PLANET_IDS.items():
#         if planet == 'Ketu':
#             continue
#         pos_data, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
#         lon = pos_data[0] % 360
#         retrograde = 'R' if pos_data[3] < 0 else ''
#         sign_index = math.floor(lon / 30)
#         sign = SIGNS[sign_index]
#         degrees = lon % 30
#         house = calculate_house(lon, cusps)
#         nakshatra, pada = get_nakshatra_and_pada(lon)
#         natal_positions[planet] = {
#             "sign": sign,
#             "degrees": round(degrees, 4),
#             "house": house,
#             "retrograde": retrograde,
#             "nakshatra": nakshatra,
#             "pada": pada
#         }
    
#     # Calculate Ketu (180° opposite Rahu)
#     rahu_lon = natal_positions['Rahu']['degrees'] + (SIGNS.index(natal_positions['Rahu']['sign']) * 30)
#     ketu_lon = (rahu_lon + 180) % 360
#     ketu_sign_index = math.floor(ketu_lon / 30)
#     ketu_sign = SIGNS[ketu_sign_index]
#     ketu_degrees = ketu_lon % 30
#     ketu_house = calculate_house(ketu_lon, cusps)
#     ketu_nakshatra, ketu_pada = get_nakshatra_and_pada(ketu_lon)
#     natal_positions['Ketu'] = {
#         "sign": ketu_sign,
#         "degrees": round(ketu_degrees, 4),
#         "house": ketu_house,
#         "retrograde": 'R',
#         "nakshatra": ketu_nakshatra,
#         "pada": ketu_pada
#     }
#     return natal_positions

# def lahairi_sripathi_bava(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate natal chart data using Lahiri Ayanamsa and Sripathi Bhava system."""
#     jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
#     asc_lon, asc_sign_index, cusps = calculate_ascendant(jd_ut, latitude, longitude)
#     asc_sign = SIGNS[asc_sign_index]
#     asc_degrees = asc_lon % 30
#     asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)
    
#     natal_positions = get_planet_data(jd_ut, asc_lon, cusps)
    
#     response = {
#         "ascendant": {
#             "sign": asc_sign,
#             "degrees": round(asc_degrees, 4),
#             "nakshatra": asc_nakshatra,
#             "pada": asc_pada
#         },
#         "planets": natal_positions
#     }
#     return response



import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Swiss Ephemeris
swe.set_ephe_path('astro_engine/ephe')  # Ensure this path points to your ephemeris files
swe.set_sid_mode(swe.SIDM_LAHIRI)    # Lahiri Ayanamsa for sidereal astrology

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu calculated separately
}
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
    'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Helper Functions
def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
    logger.debug(f"Julian Day: {jd} for UT: {ut_dt}")
    return jd

def calculate_ascendant_sri(jd, lat, lon):
    """Calculate the ascendant longitude and house cusps using Sripathi Bhava system."""
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'S', flags=swe.FLG_SIDEREAL)  # 'S' for Sripathi
    asc_lon = ascmc[0] % 360  # Ascendant longitude
    asc_sign_index = math.floor(asc_lon / 30)
    logger.debug(f"Ascendant Longitude: {asc_lon}, Sign Index: {asc_sign_index}, Cusps: {cusps}")
    return asc_lon, asc_sign_index, cusps

def calculate_house(planet_lon, cusps):
    """Determine house number using Sripathi Bhava cusps."""
    planet_lon = planet_lon % 360
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:  # Handle wrap-around at 360°
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
    return 12  # Default to House 12 if not found

def get_nakshatra_pada_sri(longitude):
    """Calculate nakshatra and pada from longitude."""
    nakshatra_span = 13 + 1/3  # 13.3333 degrees (13°20')
    pada_span = nakshatra_span / 4  # 3.3333 degrees (3°20')
    
    # Normalize longitude to 0-360°
    longitude = longitude % 360
    
    # Calculate nakshatra index (0-26)
    nakshatra_index = math.floor(longitude / nakshatra_span)
    
    # Calculate pada within nakshatra (1-4)
    nakshatra_start = nakshatra_index * nakshatra_span
    pada_offset = (longitude - nakshatra_start) / pada_span
    pada = math.floor(pada_offset) + 1
    
    # Get nakshatra name
    nakshatra = NAKSHATRAS[nakshatra_index]
    
    return nakshatra, pada

def get_planet_data_sri(jd, asc_lon, cusps):
    """Calculate planetary positions, signs, degrees, retrograde status, houses, nakshatra, and pada."""
    natal_positions = {}
    for planet, pid in PLANET_IDS.items():
        if planet == 'Ketu':
            continue
        pos_data, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon = pos_data[0] % 360
        retrograde = 'R' if pos_data[3] < 0 else ''
        sign_index = math.floor(lon / 30)
        sign = SIGNS[sign_index]
        degrees = lon % 30
        house = calculate_house(lon, cusps)
        nakshatra, pada = get_nakshatra_pada_sri(lon)
        natal_positions[planet] = {
            "sign": sign,
            "degrees": round(degrees, 4),
            "house": house,
            "retrograde": retrograde,
            "nakshatra": nakshatra,
            "pada": pada
        }
        logger.debug(f"{planet}: Lon={lon}, Sign={sign}, Degrees={degrees}, House={house}, Retro={retrograde}, Nakshatra={nakshatra}, Pada={pada}")
    
    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = natal_positions['Rahu']['degrees'] + (SIGNS.index(natal_positions['Rahu']['sign']) * 30)
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign_index = math.floor(ketu_lon / 30)
    ketu_sign = SIGNS[ketu_sign_index]
    ketu_degrees = ketu_lon % 30
    ketu_house = calculate_house(ketu_lon, cusps)
    ketu_nakshatra, ketu_pada = get_nakshatra_pada_sri(ketu_lon)
    natal_positions['Ketu'] = {
        "sign": ketu_sign,
        "degrees": round(ketu_degrees, 4),
        "house": ketu_house,
        "retrograde": 'R',
        "nakshatra": ketu_nakshatra,
        "pada": ketu_pada
    }
    logger.debug(f"Ketu: Lon={ketu_lon}, Sign={ketu_sign}, Degrees={ketu_degrees}, House={ketu_house}, Retro=R, Nakshatra={ketu_nakshatra}, Pada={ketu_pada}")
    return natal_positions