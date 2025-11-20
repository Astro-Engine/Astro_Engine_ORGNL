"""
PART OF FORTUNE CALCULATIONS - KP NEW AYANAMSA
===============================================
Pure calculation functions - NO Flask imports
All calculations use KP New (Krishnamurti) ayanamsa and Placidus houses
"""

import swisseph as swe
import datetime
import pytz

swe.set_ephe_path('astro_api/ephe')

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def normalize_longitude(lon):
    return lon % 360.0

def get_julian_day(birth_date, birth_time, tz_offset):
    dt_str = f"{birth_date} {birth_time}"
    dt_obj = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    tz = pytz.FixedOffset(int(float(tz_offset) * 60))
    dt_obj = tz.localize(dt_obj)
    jd = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day,
                    dt_obj.hour + dt_obj.minute / 60.0 + dt_obj.second / 3600.0)
    jd_ut = jd - (dt_obj.utcoffset().total_seconds() / 86400.0)
    return jd_ut

def get_sidereal_ayanamsa(jd_ut):
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)  # KP New
    ayanamsa = swe.get_ayanamsa(jd_ut)
    return ayanamsa

def get_longitudes(jd_ut, latitude, longitude, ayanamsa):
    flags = swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', flags)
    # Normalize cusp array to always be 12 elements, 0-indexed for houses 1-12
    if len(cusps) == 13:
        cusps = [cusps[i] for i in range(1, 13)]  # 1-based to 0-based (house 1 = index 0)
    elif len(cusps) == 12:
        cusps = list(cusps)  # already 0-based
    else:
        raise Exception(f"Swiss Ephemeris returned cusps of length {len(cusps)}, expected 12 or 13.")
    asc = ascmc[0]
    sun, _ = swe.calc_ut(jd_ut, swe.SUN)
    moon, _ = swe.calc_ut(jd_ut, swe.MOON)
    sun_sid = normalize_longitude(sun[0] - ayanamsa)
    moon_sid = normalize_longitude(moon[0] - ayanamsa)
    asc_sid = normalize_longitude(asc)
    return asc_sid, sun_sid, moon_sid, cusps

def get_house(longitude, cusps):
    # cusps: 12 elements, 0-based (houses 1-12 at indices 0-11)
    for i in range(12):
        start = normalize_longitude(cusps[i])
        end = normalize_longitude(cusps[0] if i == 11 else cusps[i + 1])
        if start < end:
            if start <= longitude < end:
                return i + 1
        else:
            # Crosses 360/0
            if longitude >= start or longitude < end:
                return i + 1
    return None

def get_sign(longitude):
    idx = int(longitude // 30)
    return SIGN_NAMES[idx], idx + 1

def is_day_birth(sun_sid, asc_sid, cusps):
    house = get_house(sun_sid, cusps)
    return house in [7, 8, 9, 10, 11, 12]

def calculate_part_of_fortune(birth_date, birth_time, latitude, longitude, tz_offset, user_name):
    """
    Main calculation function - calculates Part of Fortune
    
    Args:
        birth_date: Birth date as string "YYYY-MM-DD"
        birth_time: Birth time as string "HH:MM:SS"
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        tz_offset: Timezone offset in hours (e.g., 5.5 for IST)
        user_name: Name of the user
    
    Returns:
        Dictionary with complete Part of Fortune calculations
    """
    jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
    ayanamsa = get_sidereal_ayanamsa(jd_ut)
    asc_sid, sun_sid, moon_sid, cusps = get_longitudes(jd_ut, latitude, longitude, ayanamsa)

    # Defensive: check cusp length is 12
    if len(cusps) != 12:
        raise Exception(f"Swiss Ephemeris returned cusps of length {len(cusps)}, expected 12.")

    # Determine day or night birth
    day_birth = is_day_birth(sun_sid, asc_sid, cusps)

    # Calculate Part of Fortune
    if day_birth:
        fortuna = normalize_longitude(asc_sid + moon_sid - sun_sid)
    else:
        fortuna = normalize_longitude(asc_sid + sun_sid - moon_sid)

    fortuna_sign, fortuna_sign_num = get_sign(fortuna)
    fortuna_house = get_house(fortuna, cusps)

    # Prepare house cusps for output
    house_cusps = []
    for i in range(12):
        deg = normalize_longitude(cusps[i])
        sign, sign_num = get_sign(deg)
        house_cusps.append({
            "house": i + 1,
            "cusp_longitude": round(deg, 6),
            "cusp_sign": sign,
            "cusp_sign_num": sign_num
        })

    result = {
        "user_name": user_name,
        "sidereal_ayanamsa_kp_new": round(ayanamsa, 6),
        "ascendant_sidereal_longitude": round(asc_sid, 6),
        "sun_sidereal_longitude": round(sun_sid, 6),
        "moon_sidereal_longitude": round(moon_sid, 6),
        "house_cusps": house_cusps,
        "fortuna_longitude": round(fortuna, 6),
        "fortuna_sign": fortuna_sign,
        "fortuna_sign_num": fortuna_sign_num,
        "fortuna_house": fortuna_house,
        "day_birth": day_birth,
        "details": {
            "ascendant": {"longitude": round(asc_sid, 6), "sign": get_sign(asc_sid)[0], "house": get_house(asc_sid, cusps)},
            "sun": {"longitude": round(sun_sid, 6), "sign": get_sign(sun_sid)[0], "house": get_house(sun_sid, cusps)},
            "moon": {"longitude": round(moon_sid, 6), "sign": get_sign(moon_sid)[0], "house": get_house(moon_sid, cusps)},
        }
    }
    return result