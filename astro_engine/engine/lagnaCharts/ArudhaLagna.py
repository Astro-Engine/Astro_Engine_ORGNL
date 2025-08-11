# import swisseph as swe
# from datetime import datetime, timedelta
# import math

# # Constants
# ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# LORDS = {
#     'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
#     'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
# }
# PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
# SWE_PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

# # Nakshatra list with start and end degrees
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

# def get_julian_day(birth_date, birth_time, tz_offset):
#     """Convert birth date and time to Julian Day with timezone adjustment."""
#     local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

# def calculate_ascendant(jd, latitude, longitude):
#     """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
#     return houses[0][0]  # Ascendant longitude

# def calculate_planet_data(jd, planet_code):
#     """Calculate sidereal longitude and retrograde status of a planet."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
#     if ret < 0:
#         raise ValueError(f"Error calculating position for planet code {planet_code}")
#     longitude = pos[0]
#     speed = pos[3]  # Speed in longitude
#     is_retrograde = speed < 0
#     return longitude, is_retrograde

# def get_sign(longitude):
#     """Determine zodiac sign from sidereal longitude."""
#     sign_index = int(longitude // 30) % 12
#     return ZODIAC_SIGNS[sign_index]

# def get_arudha_lagna(asc_sign, lord_sign):
#     """Calculate Arudha Lagna based on Ascendant and Lagna lord's sign."""
#     asc_index = ZODIAC_SIGNS.index(asc_sign)
#     lord_index = ZODIAC_SIGNS.index(lord_sign)
#     if asc_sign == lord_sign:
#         al_index = (asc_index + 9) % 12  # 10th house from Ascendant
#     elif (lord_index - asc_index) % 12 == 6:
#         al_index = (asc_index + 3) % 12  # 4th house from Ascendant
#     else:
#         count = (lord_index - asc_index) % 12 + 1
#         al_index = (lord_index + count - 1) % 12
#     return ZODIAC_SIGNS[al_index]

# def get_nakshatra_and_pada(longitude):
#     """Calculate nakshatra and pada based on longitude."""
#     longitude = longitude % 360
#     for nakshatra, start, end in NAKSHATRAS:
#         if start <= longitude < end:
#             position_in_nakshatra = longitude - start
#             pada = math.ceil(position_in_nakshatra / 3.3333)
#             return nakshatra, pada
#     # Fallback for edge case at 360 degrees
#     return 'Revati', 4

# def lahairi_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate Arudha Lagna chart with retrograde, nakshatras, and padas."""
#     # Calculate Julian Day
#     jd = get_julian_day(birth_date, birth_time, tz_offset)

#     # Calculate sidereal Ascendant and its sign
#     asc_lon = calculate_ascendant(jd, latitude, longitude)
#     asc_sign = get_sign(asc_lon)

#     # Calculate planetary positions, retrograde status, nakshatras, and padas
#     planet_data = {}
#     for planet, code in zip(PLANETS, SWE_PLANETS):
#         if planet == 'Ketu':
#             rahu_lon, rahu_retro = calculate_planet_data(jd, swe.MEAN_NODE)
#             ketu_lon = (rahu_lon + 180) % 360
#             ketu_retro = rahu_retro  # Ketu retrogrades with Rahu
#             nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
#             planet_data[planet] = {'longitude': ketu_lon, 'sign': get_sign(ketu_lon), 'retrograde': ketu_retro, 'nakshatra': nakshatra, 'pada': pada}
#         else:
#             lon, retro = calculate_planet_data(jd, code)
#             nakshatra, pada = get_nakshatra_and_pada(lon)
#             planet_data[planet] = {'longitude': lon, 'sign': get_sign(lon), 'retrograde': retro, 'nakshatra': nakshatra, 'pada': pada}

#     # Determine Lagna lord and its sign
#     lagna_lord = LORDS[asc_sign]
#     lord_sign = planet_data[lagna_lord]['sign']

#     # Calculate Arudha Lagna
#     al_sign = get_arudha_lagna(asc_sign, lord_sign)

#     # Construct AL chart with houses relative to Arudha Lagna
#     al_index = ZODIAC_SIGNS.index(al_sign)
#     al_houses = {}
#     for planet, data in planet_data.items():
#         sign = data['sign']
#         sign_index = ZODIAC_SIGNS.index(sign)
#         house = (sign_index - al_index) % 12 + 1
#         al_houses[planet] = {
#             'sign': sign,
#             'house': house,
#             'retrograde': data['retrograde'],
#             'nakshatra': data['nakshatra'],
#             'pada': data['pada']
#         }

#     # Construct response
#     response = {
#         'arudha_lagna': al_sign,
#         'planets': al_houses
#     }
#     return response





import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

NAKSHATRAS = [
    ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186, 200),
    ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
]

def format_degrees(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    return f"{d}° {abs(m):02d}' {abs(s):05.2f}\""

def get_julian_day(birth_date, birth_time, tz_offset):
    local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def calculate_ascendant(jd, latitude, longitude):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    return houses[0][0]  # Ascendant longitude

def calculate_planet_data(jd, planet_code):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if ret < 0:
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    longitude = pos[0] % 360
    speed = pos[3]
    is_retrograde = speed < 0
    return longitude, is_retrograde

def get_sign(longitude):
    sign_index = int(longitude // 30) % 12
    return ZODIAC_SIGNS[sign_index]

def get_nakshatra_and_pada(longitude):
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            position_in_nakshatra = longitude - start
            pada = int(position_in_nakshatra // 3.3333) + 1
            return nakshatra, pada
    return 'Revati', 4

def lahairi_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset):
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign = get_sign(asc_lon)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)
    asc_degrees = asc_lon % 30

    # Planetary positions block, formatted to match the contract
    planetary_positions = {}
    planet_lons = {}

    for planet, code in zip(PLANETS, SWE_PLANETS):
        if planet == 'Ketu':
            rahu_lon, rahu_retro = calculate_planet_data(jd, swe.MEAN_NODE)
            ketu_lon = (rahu_lon + 180) % 360
            ketu_retro = rahu_retro
            nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
            sign = get_sign(ketu_lon)
            deg = ketu_lon % 30
            planetary_positions['Ketu'] = {
                "degrees": format_degrees(deg),
                "sign": sign,
                "retrograde": "R" if ketu_retro else "",
                "nakshatra": nakshatra,
                "pada": pada,
                # House will be filled in later
            }
            planet_lons['Ketu'] = ketu_lon
        else:
            lon, retro = calculate_planet_data(jd, code)
            nakshatra, pada = get_nakshatra_and_pada(lon)
            sign = get_sign(lon)
            deg = lon % 30
            planetary_positions[planet] = {
                "degrees": format_degrees(deg),
                "sign": sign,
                "retrograde": "R" if retro else "",
                "nakshatra": nakshatra,
                "pada": pada,
                # House will be filled in later
            }
            planet_lons[planet] = lon

    # Ascendant house = 1, houses are counted from ascendant
    asc_sign_index = ZODIAC_SIGNS.index(asc_sign)
    for planet in planetary_positions:
        sign = planetary_positions[planet]['sign']
        sign_index = ZODIAC_SIGNS.index(sign)
        house = ((sign_index - asc_sign_index) % 12) + 1
        planetary_positions[planet]['house'] = house

    result = {
        "ascendant": {
            "degrees": format_degrees(asc_degrees),
            "nakshatra": asc_nakshatra,
            "pada": asc_pada,
            "sign": asc_sign
        },
        "planetary_positions": planetary_positions
    }
    return result
