import swisseph as swe
from datetime import datetime, timedelta
import math

swe.set_ephe_path('astro_engine/ephe')

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def format_dms(degrees):
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}°{m}'{s:.1f}\""

def get_nakshatra(longitude):
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]

def get_pada(longitude):
    position_in_nakshatra = (longitude % 360) % 13.3333
    pada = math.ceil(position_in_nakshatra / 3.3333)
    return pada

def get_d20_position(sidereal_lon):
    natal_sign_index = int(sidereal_lon // 30) % 12
    degrees_in_sign = sidereal_lon % 30
    segment_number = math.floor(degrees_in_sign / 1.5)
    d20_sign_index = (natal_sign_index * 20 + segment_number) % 12
    d20_sign = SIGNS[d20_sign_index]
    return {'sign': d20_sign, 'sign_index': d20_sign_index}

def get_d20_house(planet_d20_sign_index, d20_asc_sign_index):
    return (planet_d20_sign_index - d20_asc_sign_index) % 12 + 1

def raman_Vimshamsha_D20(birth_date, birth_time, latitude, longitude, timezone_offset, user_name='Unknown'):
    jd_ut = get_julian_day(birth_date, birth_time, timezone_offset)
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
    d1_positions['Ketu'] = (ketu_lon, 'R')

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0] % 360

    d20_asc_pos = get_d20_position(d1_asc_lon)
    d20_asc_sign_index = d20_asc_pos['sign_index']
    asc_nakshatra = get_nakshatra(d1_asc_lon)
    asc_pada = get_pada(d1_asc_lon)
    d20_asc = {
        "sign": d20_asc_pos['sign'],
        "longitude": format_dms(d1_asc_lon),
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    d20_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d20_pos = get_d20_position(d1_lon)
        house = get_d20_house(d20_pos['sign_index'], d20_asc_sign_index)
        nakshatra = get_nakshatra(d1_lon)
        pada = get_pada(d1_lon)
        d20_positions[planet] = {
            "sign": d20_pos['sign'],
            "house": house,
            "retrograde": retro,
            "longitude": format_dms(d1_lon),
            "nakshatra": nakshatra,
            "pada": pada
        }

    house_signs = [
        {"house": i + 1, "sign": SIGNS[(d20_asc_sign_index + i) % 12]}
        for i in range(12)
    ]

    response = {
        "user_name": user_name,
        "d20_ascendant": d20_asc,
        "planetary_positions": d20_positions,
        # "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Vimsamsa (D20)",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat()
        }
    }
    return response