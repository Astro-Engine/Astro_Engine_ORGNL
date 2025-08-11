# import swisseph as swe
# from datetime import datetime, timedelta
# import math

# # Constants
# ZODIAC_SIGNS = [
#     "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
# ]

# NAKSHATRAS = [
#     ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
#     ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
#     ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
#     ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
#     ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
#     ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
#     ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
#     ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
#     ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
# ]

# ODD_SIGNS = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]
# EVEN_SIGNS = ["Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"]

# PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
# SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

# # Helper Functions
# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date and time to Julian Day (UT)."""
#     try:
#         date_obj = datetime.strptime(date_str, '%Y-%m-%d')
#         time_obj = datetime.strptime(time_str, '%H:%M:%S')
#         local_dt = datetime.combine(date_obj, time_obj.time())
#         ut_dt = local_dt - timedelta(hours=tz_offset)
#         hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
#         return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
#     except ValueError as e:
#         raise ValueError(f"Invalid date or time format: {str(e)}")

# def calculate_planet_data(jd, planet_code):
#     """Calculate sidereal longitude and retrograde status of a planet."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
#     if ret < 0:
#         raise ValueError(f"Error calculating position for planet code {planet_code}")
#     longitude = pos[0] % 360
#     speed = pos[3]  # Speed in longitude
#     is_retrograde = speed < 0
#     return longitude, is_retrograde

# def get_sign(longitude):
#     """Determine zodiac sign from sidereal longitude."""
#     sign_index = int(longitude // 30) % 12
#     return ZODIAC_SIGNS[sign_index]

# def get_nakshatra_and_pada(longitude):
#     """Calculate nakshatra and pada based on longitude."""
#     longitude = longitude % 360
#     for nakshatra, start, end in NAKSHATRAS:
#         if start <= longitude < end:
#             position_in_nakshatra = longitude - start
#             pada = math.ceil(position_in_nakshatra / 3.3333)
#             return nakshatra, pada
#     return 'Revati', 4  # Fallback for edge cases

# def map_to_d2_hora(sign, degree):
#     """Map planet's sign and degree to D2 Hora chart (Cancer or Leo)."""
#     if sign in ODD_SIGNS:
#         if 0 <= degree < 15:
#             return "Leo", degree
#         elif 15 <= degree < 30:
#             return "Cancer", degree
#     elif sign in EVEN_SIGNS:
#         if 0 <= degree < 15:
#             return "Cancer", degree
#         elif 15 <= degree < 30:
#             return "Leo", degree
#     raise ValueError(f"Invalid sign or degree: {sign}, {degree}")

# def calculate_ascendant(jd, latitude, longitude):
#     """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
#     return houses[0][0]  # Ascendant longitude

# def lahairi_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate D2 Hora chart with retrograde, nakshatra, and pada."""
#     # Calculate Julian Day
#     jd = get_julian_day(birth_date, birth_time, tz_offset)

#     # Calculate planetary positions, retrograde status, nakshatra, and pada
#     planet_data = {}
#     for planet, code in zip(PLANETS, SWE_PLANETS):
#         if planet == 'Ketu':
#             rahu_lon, rahu_retro = calculate_planet_data(jd, swe.MEAN_NODE)
#             ketu_lon = (rahu_lon + 180) % 360
#             ketu_retro = rahu_retro  # Ketu retrogrades with Rahu
#             sign = get_sign(ketu_lon)
#             degree = ketu_lon % 30
#             d2_sign, d2_degree = map_to_d2_hora(sign, degree)
#             nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
#             planet_data[planet] = {
#                 'natal_sign': sign,
#                 'natal_degree': degree,
#                 'd2_sign': d2_sign,
#                 'd2_degree': d2_degree,
#                 'retrograde': ketu_retro,
#                 'nakshatra': nakshatra,
#                 'pada': pada
#             }
#         else:
#             lon, retro = calculate_planet_data(jd, code)
#             sign = get_sign(lon)
#             degree = lon % 30
#             d2_sign, d2_degree = map_to_d2_hora(sign, degree)
#             nakshatra, pada = get_nakshatra_and_pada(lon)
#             planet_data[planet] = {
#                 'natal_sign': sign,
#                 'natal_degree': degree,
#                 'd2_sign': d2_sign,
#                 'd2_degree': d2_degree,
#                 'retrograde': retro,
#                 'nakshatra': nakshatra,
#                 'pada': pada
#             }

#     # Calculate Ascendant (Lagna) for D2 chart
#     asc_lon = calculate_ascendant(jd, latitude, longitude)
#     asc_sign = get_sign(asc_lon)
#     asc_degree = asc_lon % 30
#     d2_asc_sign, d2_asc_degree = map_to_d2_hora(asc_sign, asc_degree)
#     asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)

#     # Construct response
#     response = {
#         'ascendant': {
#             'natal_sign': asc_sign,
#             'natal_degree': asc_degree,
#             'd2_sign': d2_asc_sign,
#             'd2_degree': d2_asc_degree,
#             'nakshatra': asc_nakshatra,
#             'pada': asc_pada
#         },
#         'planets': planet_data
#     }
#     return response



import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
    ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
]

ODD_SIGNS = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]
EVEN_SIGNS = ["Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"]

PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

# Helper Functions
def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day (UT)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_planet_data(jd, planet_code):
    """Calculate sidereal longitude and retrograde status of a planet."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if ret < 0:
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    longitude = pos[0] % 360
    speed = pos[3]  # Speed in longitude
    is_retrograde = speed < 0
    return longitude, is_retrograde

def get_sign(longitude):
    """Determine zodiac sign from sidereal longitude."""
    sign_index = int(longitude // 30) % 12
    return ZODIAC_SIGNS[sign_index]

def get_nakshatra_and_pada(longitude):
    """Calculate nakshatra and pada based on longitude."""
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            position_in_nakshatra = longitude - start
            pada = math.ceil(position_in_nakshatra / 3.3333)
            return nakshatra, pada
    return 'Revati', 4  # Fallback for edge cases

def map_to_d2_hora(sign, degree):
    """Map planet's sign and degree to D2 Hora chart (Cancer or Leo)."""
    if sign in ODD_SIGNS:
        if 0 <= degree < 15:
            return "Leo", degree
        elif 15 <= degree < 30:
            return "Cancer", degree
    elif sign in EVEN_SIGNS:
        if 0 <= degree < 15:
            return "Cancer", degree
        elif 15 <= degree < 30:
            return "Leo", degree
    raise ValueError(f"Invalid sign or degree: {sign}, {degree}")

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    return houses[0][0]  # Ascendant longitude

def lahairi_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate D2 Hora chart with retrograde, nakshatra, and pada."""
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate planetary positions, retrograde status, nakshatra, and pada
    planet_data = {}
    for planet, code in zip(PLANETS, SWE_PLANETS):
        if planet == 'Ketu':
            rahu_lon, rahu_retro = calculate_planet_data(jd, swe.MEAN_NODE)
            ketu_lon = (rahu_lon + 180) % 360
            ketu_retro = rahu_retro  # Ketu retrogrades with Rahu
            sign = get_sign(ketu_lon)
            degree = ketu_lon % 30
            d2_sign, d2_degree = map_to_d2_hora(sign, degree)
            nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
            planet_data[planet] = {
                # 'natal_sign': sign,
                # 'natal_degree': degree,
                'sign': d2_sign,
                'degree': d2_degree,
                'retrograde': ketu_retro,
                'nakshatra': nakshatra,
                'pada': pada
            }
        else:
            lon, retro = calculate_planet_data(jd, code)
            sign = get_sign(lon)
            degree = lon % 30
            d2_sign, d2_degree = map_to_d2_hora(sign, degree)
            nakshatra, pada = get_nakshatra_and_pada(lon)
            planet_data[planet] = {
                # 'natal_sign': sign,
                # 'natal_degree': degree,
                'sign': d2_sign,
                'degree': d2_degree,
                'retrograde': retro,
                'nakshatra': nakshatra,
                'pada': pada
            }

    # Calculate Ascendant (Lagna) for D2 chart
    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign = get_sign(asc_lon)
    asc_degree = asc_lon % 30
    d2_asc_sign, d2_asc_degree = map_to_d2_hora(asc_sign, asc_degree)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)

    # Construct response
    response = {
        'ascendant': {
            'natal_sign': asc_sign,
            'natal_degree': asc_degree,
            'd2_sign': d2_asc_sign,
            'd2_degree': d2_asc_degree,
            'nakshatra': asc_nakshatra,
            'pada': asc_pada
        },
        'planets': planet_data
    }
    return response

