import swisseph as swe
from datetime import datetime, timedelta
import math

# Set ephemeris path (adjust path to your Swiss Ephemeris files)
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatras list
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def format_dms(degrees):
    """Format degrees into degrees, minutes, seconds (D°M'S\")."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_starting_sign_index(natal_sign_index):
    """Determine starting sign index based on odd/even natal sign."""
    return 0 if natal_sign_index % 2 == 0 else 6  # Aries (0) for odd, Libra (6) for even

def get_nakshatra(longitude):
    """Determine the nakshatra based on sidereal longitude."""
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]

def get_pada(longitude):
    """Determine the pada (1-4) within the nakshatra based on sidereal longitude."""
    position_in_nakshatra = (longitude % 360) % 13.3333
    pada = math.ceil(position_in_nakshatra / 3.3333)
    return pada

def get_d40_position(d1_sidereal_lon):
    """Calculate D40 position from D1 sidereal longitude."""
    natal_sign_index = int(d1_sidereal_lon // 30) % 12
    natal_degrees = d1_sidereal_lon % 30
    total_minutes = natal_degrees * 60
    segment_size = 45  # 0°45' = 45 minutes
    segment_number = math.ceil(total_minutes / segment_size)
    starting_sign_index = get_starting_sign_index(natal_sign_index)
    d40_sign_index = (starting_sign_index + segment_number - 1) % 12
    segment_start = (segment_number - 1) * segment_size
    position_in_segment = total_minutes - segment_start
    d40_degrees = (position_in_segment / segment_size) * 30
    d40_longitude = (d40_sign_index * 30) + d40_degrees
    return {
        "sign": SIGNS[d40_sign_index],
        "degrees": format_dms(d40_degrees),
        "sign_index": d40_sign_index,
        "longitude": d40_longitude
    }

def get_d40_house(d40_sign_index, d40_asc_sign_index):
    """Assign house number using Whole Sign system."""
    return (d40_sign_index - d40_asc_sign_index) % 12 + 1

def raman_Khavedamsha_D40(birth_date, birth_time, latitude, longitude, timezone_offset):
    """Calculate the D40 (Khavedamsa) chart using Raman ayanamsa."""
    jd_ut = get_julian_day(birth_date, birth_time, timezone_offset)
    swe.set_sid_mode(swe.SIDM_RAMAN)  # Raman ayanamsa

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

    d40_asc = get_d40_position(d1_asc_lon)
    d40_asc_sign_index = d40_asc['sign_index']
    asc_nakshatra = get_nakshatra(d1_asc_lon)
    asc_pada = get_pada(d1_asc_lon)
    d40_asc.update({
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    })

    d40_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d40_pos = get_d40_position(d1_lon)
        house = get_d40_house(d40_pos['sign_index'], d40_asc_sign_index)
        nakshatra = get_nakshatra(d1_lon)
        pada = get_pada(d1_lon)
        d40_positions[planet] = {
            "sign": d40_pos['sign'],
            "degrees": d40_pos['degrees'],
            "retrograde": retro,
            "house": house,
            "longitude": d40_pos['longitude'],
            "nakshatra": nakshatra,
            "pada": pada
        }

    house_signs = [{"house": i + 1, "sign": SIGNS[(d40_asc_sign_index + i) % 12]} for i in range(12)]

    response = {
        "d40_ascendant": d40_asc,
        "planetary_positions": d40_positions,
        # "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Khavedamsa (D40)",
            "house_system": "Whole Sign"
        }
    }
    return response