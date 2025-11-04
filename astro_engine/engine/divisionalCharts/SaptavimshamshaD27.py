# import swisseph as swe
# from datetime import datetime, timedelta

# # Set ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# ZODIAC_SIGNS_d27 = [
#     "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
# ]

# PLANET_CODES = {
#     "Sun": swe.SUN,
#     "Moon": swe.MOON,
#     "Mars": swe.MARS,
#     "Mercury": swe.MERCURY,
#     "Jupiter": swe.JUPITER,
#     "Venus": swe.VENUS,
#     "Saturn": swe.SATURN,
#     "Rahu": swe.MEAN_NODE
# }

# NAKSHATRA_NAMES = [
#     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
#     "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
#     "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
#     "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
#     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# ]

# NAKSHATRA_LORDS = [
#     "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
#     "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
#     "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
# ]

# def d27_get_julian_day_utc(date_str, time_str, tz_offset):
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     utc_dt = local_dt - timedelta(hours=tz_offset)
#     jd_utc = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
#                         utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
#     return jd_utc

# def d27_calculate_sidereal_longitude(jd, planet_code):
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     result = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
#     if result[1] < 0:
#         raise ValueError(f"Error calculating position for planet code {planet_code}")
#     lon = result[0][0] % 360.0
#     speed = result[0][3]
#     retrograde = speed < 0
#     return lon, retrograde

# def d27_calculate_ascendant(jd, latitude, longitude):
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     houses_data = swe.houses_ex(jd, latitude, longitude, b'P', swe.FLG_SIDEREAL)
#     asc_lon = houses_data[1][0]
#     return asc_lon

# def d27_calculate_longitude(natal_longitude):
#     return (natal_longitude * 27) % 360.0

# def d27_get_sign_index(longitude):
#     return int(longitude // 30)

# def d27_calculate_house(d27_asc_sign_index, d27_planet_sign_index):
#     return (d27_planet_sign_index - d27_asc_sign_index) % 12 + 1

# def d27_get_nakshatra_pada(longitude):
#     nak_num = int(longitude // (13 + 1/3))  # 13°20' = 13.333...
#     nakshatra = NAKSHATRA_NAMES[nak_num]
#     lord = NAKSHATRA_LORDS[nak_num]
#     nak_start = nak_num * 13.3333333333
#     deg_in_nakshatra = longitude - nak_start
#     pada = int(deg_in_nakshatra // 3.3333333333) + 1
#     return nakshatra, lord, pada





import swisseph as swe
from datetime import datetime, timedelta

# Set ephemeris path
swe.set_ephe_path('astro_engine/ephe')

ZODIAC_SIGNS_d27 = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

PLANET_CODES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

def d27_get_julian_day_utc(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=tz_offset)
    jd_utc = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
    return jd_utc

def d27_calculate_sidereal_longitude(jd, planet_code):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if result[1] < 0:
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    lon = result[0][0] % 360.0
    speed = result[0][3]
    retrograde = speed < 0
    return lon, retrograde

def d27_calculate_ascendant(jd, latitude, longitude):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses_data = swe.houses_ex(jd, latitude, longitude, b'P', swe.FLG_SIDEREAL)
    asc_lon = houses_data[1][0]
    return asc_lon

def d27_calculate_longitude(natal_longitude):
    return (natal_longitude * 27) % 360.0

def d27_get_sign_index(longitude):
    return int(longitude // 30)

def d27_calculate_house(d27_asc_sign_index, d27_planet_sign_index):
    return (d27_planet_sign_index - d27_asc_sign_index) % 12 + 1

def d27_get_nakshatra_pada(longitude):
    nak_num = int(longitude // (13 + 1/3))  # 13°20' = 13.333...
    nakshatra = NAKSHATRA_NAMES[nak_num]
    lord = NAKSHATRA_LORDS[nak_num]
    nak_start = nak_num * 13.3333333333
    deg_in_nakshatra = longitude - nak_start
    pada = int(deg_in_nakshatra // 3.3333333333) + 1
    return nakshatra, lord, pada

# def format_dms(decimal_degrees):
#     """Convert decimal degrees to DMS format string."""
#     degrees = int(decimal_degrees)
#     minutes_decimal = (decimal_degrees - degrees) * 60
#     minutes = int(minutes_decimal)
#     seconds = int((minutes_decimal - minutes) * 60)
#     return f"{degrees:02d}°{minutes:02d}'{seconds:02d}\""

# def lahairi_d27(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate D27 chart and format response exactly like the natal chart."""
#     jd = d27_get_julian_day_utc(birth_date, birth_time, tz_offset)
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     ayanamsa = swe.get_ayanamsa_ut(jd)

#     # Calculate natal ascendant
#     asc_natal_lon = d27_calculate_ascendant(jd, latitude, longitude)
    
#     # Calculate D27 ascendant
#     asc_d27_lon = d27_calculate_longitude(asc_natal_lon)
#     d27_asc_sign_index = d27_get_sign_index(asc_d27_lon)
#     d27_asc_sign = ZODIAC_SIGNS_d27[d27_asc_sign_index]
    
#     # Get degree within sign for ascendant
#     asc_deg_in_sign = asc_d27_lon % 30
#     asc_dms = format_dms(asc_deg_in_sign)
    
#     # Get nakshatra and pada for ascendant
#     asc_nakshatra, asc_lord, asc_pada = d27_get_nakshatra_pada(asc_d27_lon)

#     # Ascendant block
#     ascendant_json = {
#         "sign": d27_asc_sign,
#         "degrees": asc_dms,
#         "nakshatra": asc_nakshatra,
#         "pada": asc_pada
#     }

#     planetary_positions_json = {}
    
#     for planet_name in PLANET_NAMES:
#         if planet_name == 'Rahu':
#             natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, swe.MEAN_NODE)
#             retrograde = 'R'
#         elif planet_name == 'Ketu':
#             natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, swe.MEAN_NODE)
#             natal_lon = (natal_lon + 180) % 360
#             retrograde = 'R'
#         else:
#             planet_id = PLANET_CODES[planet_name]
#             natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, planet_id)
#             retrograde = 'R' if is_retro else ''
        
#         # Calculate D27 position
#         d27_lon = d27_calculate_longitude(natal_lon)
#         d27_sign_index = d27_get_sign_index(d27_lon)
#         d27_sign = ZODIAC_SIGNS_d27[d27_sign_index]
        
#         # Calculate house in D27
#         d27_house = d27_calculate_house(d27_asc_sign_index, d27_sign_index)
        
#         # Get degree within sign
#         deg_in_sign = d27_lon % 30
#         dms = format_dms(deg_in_sign)
        
#         # Get nakshatra and pada
#         nakshatra, lord, pada = d27_get_nakshatra_pada(d27_lon)
        
#         planetary_positions_json[planet_name] = {
#             "sign": d27_sign,
#             "degrees": dms,
#             "retrograde": retrograde,
#             "house": d27_house,
#             "nakshatra": nakshatra,
#             "pada": pada
#         }

#     # Return with extra ayanamsa for notes
#     return {
#         "planetary_positions": planetary_positions_json,
#         "ascendant": ascendant_json,
#         "ayanamsa_value": float(ayanamsa)
#     }



def format_dms(decimal_degrees):
    """Convert decimal degrees to DMS format string."""
    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = int((minutes_decimal - minutes) * 60)
    return f"{degrees:02d}°{minutes:02d}'{seconds:02d}\""


def lahairi_d27(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate D27 chart and format response exactly like the natal chart."""
    jd = d27_get_julian_day_utc(birth_date, birth_time, tz_offset)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Calculate natal ascendant
    asc_natal_lon = d27_calculate_ascendant(jd, latitude, longitude)
    
    # Calculate D27 ascendant
    asc_d27_lon = d27_calculate_longitude(asc_natal_lon)
    d27_asc_sign_index = d27_get_sign_index(asc_d27_lon)
    d27_asc_sign = ZODIAC_SIGNS_d27[d27_asc_sign_index]
    
    # Get degree within sign for ascendant
    asc_deg_in_sign = asc_d27_lon % 30
    asc_dms = format_dms(asc_deg_in_sign)
    
    # Get nakshatra and pada for ascendant
    asc_nakshatra, asc_lord, asc_pada = d27_get_nakshatra_pada(asc_d27_lon)

    # Ascendant block
    ascendant_json = {
        "sign": d27_asc_sign,
        "degrees": asc_dms,
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    planetary_positions_json = {}
    
    # Define planet names in order
    PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for planet_name in PLANET_NAMES:
        if planet_name == 'Rahu':
            natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, swe.MEAN_NODE)
            retrograde = 'R'
        elif planet_name == 'Ketu':
            natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, swe.MEAN_NODE)
            natal_lon = (natal_lon + 180) % 360
            retrograde = 'R'
        else:
            planet_id = PLANET_CODES[planet_name]
            natal_lon, is_retro = d27_calculate_sidereal_longitude(jd, planet_id)
            retrograde = 'R' if is_retro else ''
        
        # Calculate D27 position
        d27_lon = d27_calculate_longitude(natal_lon)
        d27_sign_index = d27_get_sign_index(d27_lon)
        d27_sign = ZODIAC_SIGNS_d27[d27_sign_index]
        
        # Calculate house in D27
        d27_house = d27_calculate_house(d27_asc_sign_index, d27_sign_index)
        
        # Get degree within sign
        deg_in_sign = d27_lon % 30
        dms = format_dms(deg_in_sign)
        
        # Get nakshatra and pada
        nakshatra, lord, pada = d27_get_nakshatra_pada(d27_lon)
        
        planetary_positions_json[planet_name] = {
            "sign": d27_sign,
            "degrees": dms,
            "retrograde": retrograde,
            "house": d27_house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    # Return with extra ayanamsa for notes
    return {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "ayanamsa_value": float(ayanamsa)
    }

