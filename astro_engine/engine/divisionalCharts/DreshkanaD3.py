



# import swisseph as swe
# from datetime import datetime, timedelta

# # Constants
# PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
# SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# NAKSHATRA_NAMES = [
#     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
#     "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
#     "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
#     "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
#     "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# ]

# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert local birth time to Julian Day using UTC."""
#     dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     dt_utc = dt - timedelta(hours=tz_offset)
#     jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
#     return jd

# def calculate_sidereal_position(jd, planet_id, ayanamsa):
#     """Calculate sidereal longitude and retrograde status for a planet."""
#     pos, ret = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
#     if ret < 0:
#         return 0.0, ''
#     tropical_lon = pos[0]
#     sidereal_lon = (tropical_lon - ayanamsa) % 360
#     speed = pos[3]  # Speed in longitude
#     retrograde = 'R' if speed < 0 else ''
#     return sidereal_lon, retrograde

# def calculate_ascendant(jd, lat, lon):
#     """Calculate sidereal ascendant longitude."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
#     asc_lon = ascmc[0] % 360
#     return asc_lon

# def get_sign_and_degrees(longitude):
#     """Get sign and degrees from longitude."""
#     sign_index = int(longitude // 30)
#     degrees = longitude % 30
#     sign = SIGNS[sign_index]
#     return sign, degrees

# def calculate_d3_sign(longitude):
#     """Calculate D3 sign based on degrees in natal sign."""
#     natal_sign, degrees = get_sign_and_degrees(longitude)
#     natal_index = SIGNS.index(natal_sign)
#     if degrees < 10:
#         d3_sign = natal_sign
#     elif 10 <= degrees < 20:
#         d3_sign = SIGNS[(natal_index + 4) % 12]  # 5th sign
#     else:
#         d3_sign = SIGNS[(natal_index + 8) % 12]  # 9th sign
#     return d3_sign

# def calculate_d3_house(d3_sign, d3_asc_sign):
#     """Calculate D3 house number."""
#     d3_sign_index = SIGNS.index(d3_sign)
#     d3_asc_index = SIGNS.index(d3_asc_sign)
#     house = (d3_sign_index - d3_asc_index + 12) % 12 + 1
#     return house

# def get_nakshatra_and_pada(longitude):
#     """Calculate nakshatra and pada from sidereal longitude."""
#     nakshatra_index = int(longitude / (360 / 27))
#     position_in_nakshatra = longitude % (360 / 27)
#     pada = int(position_in_nakshatra / (360 / 108)) + 1
#     nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
#     return nakshatra_name, pada

# def lahairi_drerkhana(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate D3 chart using Lahiri ayanamsa with retrograde, nakshatras, and padas."""
#     jd = get_julian_day(birth_date, birth_time, tz_offset)
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     ayanamsa = swe.get_ayanamsa_ut(jd)

#     asc_lon = calculate_ascendant(jd, latitude, longitude)
#     natal_asc_sign, asc_degrees = get_sign_and_degrees(asc_lon)
#     d3_asc_sign = calculate_d3_sign(asc_lon)
#     asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)

#     planets = {}
#     for planet_name in PLANET_NAMES:
#         if planet_name == 'Rahu':
#             planet_id = swe.MEAN_NODE
#             lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
#             retrograde = 'R'  # Rahu is always retrograde
#         elif planet_name == 'Ketu':
#             planet_id = swe.MEAN_NODE
#             lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
#             lon = (lon + 180) % 360  # Ketu is opposite Rahu
#             retrograde = 'R'  # Ketu is always retrograde
#         else:
#             planet_id = getattr(swe, planet_name.upper())
#             lon, retrograde = calculate_sidereal_position(jd, planet_id, ayanamsa)
        
#         natal_sign, degrees = get_sign_and_degrees(lon)
#         d3_sign = calculate_d3_sign(lon)
#         house = calculate_d3_house(d3_sign, d3_asc_sign)
#         nakshatra, pada = get_nakshatra_and_pada(lon)
        
#         planets[planet_name] = {
#             "natal_sign": natal_sign,
#             "degrees": round(degrees, 6),
#             "retrograde": retrograde,
#             "nakshatra": nakshatra,
#             "pada": pada,
#             "d3_sign": d3_sign,
#             "house": house
#         }

#     ascendant = {
#         "natal_sign": natal_asc_sign,
#         "degrees": round(asc_degrees, 6),
#         "retrograde": "",
#         "nakshatra": asc_nakshatra,
#         "pada": asc_pada,
#         "d3_sign": d3_asc_sign,
#         "house": 1
#     }

#     return {
#         "ascendant": ascendant,
#         "planets": planets
#     }






import swisseph as swe
from datetime import datetime, timedelta

# Constants
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
    return jd

def calculate_sidereal_position(jd, planet_id, ayanamsa):
    pos, ret = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    if ret < 0:
        return 0.0, ''
    tropical_lon = pos[0]
    sidereal_lon = (tropical_lon - ayanamsa) % 360
    speed = pos[3]
    retrograde = 'R' if speed < 0 else ''
    return sidereal_lon, retrograde

def calculate_ascendant(jd, lat, lon):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    return asc_lon

def get_sign_and_degrees(longitude):
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    sign = SIGNS[sign_index]
    return sign, degrees

def calculate_d3_sign(longitude):
    natal_sign, degrees = get_sign_and_degrees(longitude)
    natal_index = SIGNS.index(natal_sign)
    if degrees < 10:
        d3_sign = natal_sign
    elif 10 <= degrees < 20:
        d3_sign = SIGNS[(natal_index + 4) % 12]
    else:
        d3_sign = SIGNS[(natal_index + 8) % 12]
    return d3_sign

def calculate_d3_house(d3_sign, d3_asc_sign):
    d3_sign_index = SIGNS.index(d3_sign)
    d3_asc_index = SIGNS.index(d3_asc_sign)
    house = (d3_sign_index - d3_asc_index + 12) % 12 + 1
    return house

def get_nakshatra_and_pada(longitude):
    nakshatra_index = int(longitude / (360 / 27))
    position_in_nakshatra = longitude % (360 / 27)
    pada = int(position_in_nakshatra / (360 / 108)) + 1
    nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
    return nakshatra_name, pada

def format_dms(degrees):
    deg = int(degrees)
    minutes_float = (degrees - deg) * 60
    minutes = int(minutes_float)
    seconds = int((minutes_float - minutes) * 60)
    return f"{deg}° {minutes}' {seconds}\""

def lahairi_drerkhana(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate D3 chart and format response exactly like the natal chart."""
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    asc_lon = calculate_ascendant(jd, latitude, longitude)
    d3_asc_sign = calculate_d3_sign(asc_lon)
    asc_sign, asc_deg = get_sign_and_degrees(asc_lon)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_lon)
    asc_dms = format_dms(asc_deg)

    # Ascendant block
    ascendant_json = {
        "sign": d3_asc_sign,
        "degrees": asc_dms,
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    planetary_positions_json = {}
    for planet_name in PLANET_NAMES:
        if planet_name == 'Rahu':
            planet_id = swe.MEAN_NODE
            lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
            retrograde = 'R'
        elif planet_name == 'Ketu':
            planet_id = swe.MEAN_NODE
            lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
            lon = (lon + 180) % 360
            retrograde = 'R'
        else:
            planet_id = getattr(swe, planet_name.upper())
            lon, retrograde = calculate_sidereal_position(jd, planet_id, ayanamsa)
        natal_sign, sign_deg = get_sign_and_degrees(lon)
        d3_sign = calculate_d3_sign(lon)
        d3_house = calculate_d3_house(d3_sign, d3_asc_sign)
        nakshatra, pada = get_nakshatra_and_pada(lon)
        dms = format_dms(sign_deg)
        planetary_positions_json[planet_name] = {
            "sign": d3_sign,
            "degrees": dms,
            "retrograde": retrograde,
            "house": d3_house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    # Return with extra ayanamsa for notes
    return {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "ayanamsa_value": float(ayanamsa)
    }
