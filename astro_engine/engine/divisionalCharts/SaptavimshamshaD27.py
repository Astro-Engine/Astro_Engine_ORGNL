import swisseph as swe
from datetime import datetime, timedelta

# Set ephemeris path
swe.set_ephe_path('astro_engine/ephe')

ZODIAC_SIGNS_d27 = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

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