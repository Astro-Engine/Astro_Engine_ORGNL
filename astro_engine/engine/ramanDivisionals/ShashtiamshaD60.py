import swisseph as swe
from datetime import datetime, timedelta
import math

swe.set_ephe_path('astro_engine/ephe')

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SHASHTIAMSHA_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulagna",
    "Garala", "Vahni", "Maya", "Purishaka", "Apampathi", "Marut", "Kala", "Sarpa",
    "Amrita", "Indu", "Mridu", "Komal", "Heramba", "Brahma", "Vishnu", "Maheshwara",
    "Deva", "Ardra", "Kala", "Kshiti", "Kamalakara", "Gulika", "Mrityu", "Kaala",
    "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
    "Kulanashta", "Vamsakshaya", "Utpata", "Kala", "Saumya", "Komala", "Sheetala", "Karaladamshtra",
    "Chandramukhi", "Praveena", "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Kroora", "Atisheetala",
    "Amrita", "Payodhi", "Brahmana", "Indu Rekha"
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

def get_sidereal_longitude(jd_ut, planet_id, ascendant=False):
    swe.set_sid_mode(swe.SIDM_RAMAN)  # Changed to Raman Ayanamsa
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    if ascendant:
        return None, ''
    else:
        pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
        longitude = pos[0] % 360
        retrograde = 'R' if pos[3] < 0 else ''
        return longitude, retrograde

def get_d60_position(sidereal_lon):
    natal_sign_index = int(sidereal_lon // 30)
    natal_degrees = sidereal_lon % 30

    y = natal_degrees * 2
    remainder = y % 12
    count = math.floor(remainder) + 1
    d60_sign_index = (natal_sign_index + count - 1) % 12

    shashtiamsha_number = math.floor(natal_degrees / 0.5) + 1
    if shashtiamsha_number > 60:
        shashtiamsha_number = 60
    
    deity = SHASHTIAMSHA_DEITIES[shashtiamsha_number - 1]

    return {
        "sign": SIGNS[d60_sign_index],
        "sign_index": d60_sign_index,
        "shashtiamsha": shashtiamsha_number,
        "deity": deity,
        "longitude": sidereal_lon
    }

def get_d60_house(d60_sign_index, d60_asc_sign_index):
    return (d60_sign_index - d60_asc_sign_index) % 12 + 1

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

def raman_Shashtiamsha_D60(birth_date, birth_time, latitude, longitude, tz_offset):
    jd_ut = get_julian_day(birth_date, birth_time, tz_offset)

    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    d1_positions = {}
    for planet_id, name in planets:
        lon, retro = get_sidereal_longitude(jd_ut, planet_id)
        d1_positions[name] = (lon, retro)

    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, 'R')  # Ketu is always retrograde

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0] % 360

    d60_asc = get_d60_position(d1_asc_lon)
    d60_asc_sign_index = d60_asc['sign_index']

    asc_nakshatra = get_nakshatra(d1_asc_lon)
    asc_pada = get_pada(d1_asc_lon)

    d60_asc.update({
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    })

    d60_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d60_pos = get_d60_position(d1_lon)
        house = get_d60_house(d60_pos['sign_index'], d60_asc_sign_index)
        nakshatra = get_nakshatra(d1_lon)
        pada = get_pada(d1_lon)
        d60_positions[planet] = {
            "sign": d60_pos['sign'],
            "shashtiamsha": d60_pos['shashtiamsha'],
            "deity": d60_pos['deity'],
            "house": house,
            "retrograde": retro,
            "longitude": format_dms(d1_lon),
            "nakshatra": nakshatra,
            "pada": pada
        }

    house_signs = [
        {"house": i + 1, "sign": SIGNS[(d60_asc_sign_index + i) % 12]}
        for i in range(12)
    ]

    chart_data = {
        "d60_ascendant": d60_asc,
        "planetary_positions": d60_positions,
        # "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Shashtiamsha (D60)",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat()
        }
    }
    return chart_data