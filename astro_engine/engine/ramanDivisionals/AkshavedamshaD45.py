import swisseph as swe
from datetime import datetime, timedelta
import math

# Set Swiss Ephemeris path (adjust path as needed)
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs (0-based index: Aries=0, Taurus=1, ..., Pisces=11)
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Nakshatras list
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Sign natures for D45 calculation
MOVABLE = [0, 3, 6, 9]  # Aries, Cancer, Libra, Capricorn
FIXED = [1, 4, 7, 10]    # Taurus, Leo, Scorpio, Aquarius
DUAL = [2, 5, 8, 11]     # Gemini, Virgo, Sagittarius, Pisces

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day (UT)."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def format_dms(degrees):
    """Format longitude in degrees, minutes, seconds."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}°{m}'{s:.1f}\""

def get_d45_position(sidereal_lon):
    """Calculate D45 sign based on sidereal longitude."""
    natal_sign_index = int(sidereal_lon // 30) % 12
    degrees_in_sign = sidereal_lon % 30
    minutes_in_sign = degrees_in_sign * 60
    segment_number = math.floor(minutes_in_sign / 40)  # 40 minutes per segment

    if natal_sign_index in MOVABLE:
        starting_sign_index = 0  # Aries
    elif natal_sign_index in FIXED:
        starting_sign_index = 4  # Leo
    elif natal_sign_index in DUAL:
        starting_sign_index = 8  # Sagittarius
    else:
        raise ValueError(f"Invalid natal sign index: {natal_sign_index}")

    d45_sign_index = (starting_sign_index + segment_number) % 12
    d45_sign = SIGNS[d45_sign_index]
    return {'sign': d45_sign, 'sign_index': d45_sign_index}

def get_d45_house(planet_d45_sign_index, d45_asc_sign_index):
    """Calculate house number using Whole Sign system."""
    return (planet_d45_sign_index - d45_asc_sign_index) % 12 + 1

def get_nakshatra(longitude):
    """Determine the nakshatra based on sidereal longitude."""
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]

def get_pada(longitude):
    """Determine the pada (1-4) within the nakshatra based on sidereal longitude."""
    position_in_nakshatra = (longitude % 360) % 13.3333
    pada = math.ceil(position_in_nakshatra / 3.3333)
    return pada

def raman_Akshavedamsha_D45(birth_date, birth_time, latitude, longitude, timezone_offset, user_name='Unknown'):
    """Calculate the D45 (Akshavedamsa) chart using Raman ayanamsa."""
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

    d45_asc_pos = get_d45_position(d1_asc_lon)
    d45_asc_sign_index = d45_asc_pos['sign_index']
    asc_nakshatra = get_nakshatra(d1_asc_lon)
    asc_pada = get_pada(d1_asc_lon)
    d45_asc = {
        "sign": d45_asc_pos['sign'],
        "longitude": format_dms(d1_asc_lon),
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    d45_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d45_pos = get_d45_position(d1_lon)
        house = get_d45_house(d45_pos['sign_index'], d45_asc_sign_index)
        nakshatra = get_nakshatra(d1_lon)
        pada = get_pada(d1_lon)
        d45_positions[planet] = {
            "sign": d45_pos['sign'],
            "house": house,
            "retrograde": retro,
            "longitude": format_dms(d1_lon),
            "nakshatra": nakshatra,
            "pada": pada
        }

    house_signs = [
        {"house": i + 1, "sign": SIGNS[(d45_asc_sign_index + i) % 12]}
        for i in range(12)
    ]

    response = {
        "user_name": user_name,
        "d45_ascendant": d45_asc,
        "planetary_positions": d45_positions,
        # "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Akshavedamsa (D45)",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat()
        }
    }
    return response