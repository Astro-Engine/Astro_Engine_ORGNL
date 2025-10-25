import swisseph as swe
from datetime import datetime, timedelta
import math

swe.set_ephe_path('astro_engine/ephe')

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone to Julian Day."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def format_dms(degrees):
    """Format degrees into D°M'S\"."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """Calculate nakshatra from sidereal longitude."""
    nakshatra_index = int((longitude % 360) / 13.3333)
    return NAKSHATRAS[nakshatra_index % 27]

def get_pada(longitude):
    """Calculate pada (1-4) within the nakshatra."""
    position_in_nakshatra = (longitude % 360) % 13.3333
    pada = math.ceil(position_in_nakshatra / 3.3333)
    return pada

def get_d24_position(d1_sidereal_lon):
    """Calculate D24 position from D1 sidereal longitude."""
    natal_sign_index = int(d1_sidereal_lon // 30) % 12
    natal_degrees = d1_sidereal_lon % 30
    total_minutes = natal_degrees * 60
    segment_size = 75  # 1°15' = 75 minutes
    segment_number = math.ceil(total_minutes / segment_size)
    if natal_sign_index % 2 == 0:  # Odd signs
        starting_sign_index = 4  # Leo
    else:  # Even signs
        starting_sign_index = 3  # Cancer
    d24_sign_index = (starting_sign_index + segment_number - 1) % 12
    segment_start = (segment_number - 1) * segment_size
    position_in_segment = total_minutes - segment_start
    d24_degrees = (position_in_segment / segment_size) * 30
    d24_longitude = (d24_sign_index * 30) + d24_degrees
    return {
        "sign": SIGNS[d24_sign_index],
        "degrees": format_dms(d24_degrees),
        "sign_index": d24_sign_index,
        "longitude": d24_longitude
    }

def get_d24_house(d24_sign_index, d24_asc_sign_index):
    """Assign house using Whole Sign system."""
    return (d24_sign_index - d24_asc_sign_index) % 12 + 1

def raman_Chaturvimshamsha_D24(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate D24 chart using Raman ayanamsa."""
    jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
    swe.set_sid_mode(swe.SIDM_RAMAN)
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    d1_positions = {}
    for planet_id, name in planets:
        pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
        lon = pos[0] % 360
        retro = 'R' if pos[3] < 0 else ''
        d1_positions[name] = (lon, retro)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, 'R')  # Ketu is always retrograde
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0] % 360
    d24_asc = get_d24_position(d1_asc_lon)
    d24_asc_sign_index = d24_asc['sign_index']
    asc_nakshatra = get_nakshatra(d1_asc_lon)
    asc_pada = get_pada(d1_asc_lon)
    d24_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d24_pos = get_d24_position(d1_lon)
        house = get_d24_house(d24_pos['sign_index'], d24_asc_sign_index)
        nakshatra = get_nakshatra(d1_lon)
        pada = get_pada(d1_lon)
        d24_positions[planet] = {
            "sign": d24_pos['sign'],
            "degrees": d24_pos['degrees'],
            "retrograde": retro,
            "house": house,
            "longitude": d24_pos['longitude'],
            "nakshatra": nakshatra,
            "pada": pada
        }
    d24_ascendant = {
        "sign": d24_asc['sign'],
        "degrees": d24_asc['degrees'],
        "longitude": d24_asc['longitude'],
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }
    house_signs = [{"house": i + 1, "sign": SIGNS[(d24_asc_sign_index + i) % 12]} for i in range(12)]
    response = {
        "d24_ascendant": d24_ascendant,
        "planetary_positions": d24_positions,
        # "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Chaturvimshamsha (D24)",
            "house_system": "Whole Sign"
        }
    }
    return response