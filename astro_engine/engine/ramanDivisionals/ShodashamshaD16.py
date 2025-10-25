import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (adjust this path as needed)
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs (0 = Aries, 1 = Taurus, ..., 11 = Pisces)
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatras (27 nakshatras)
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, timezone_offset):
    """Convert birth date and time to Julian Day."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=timezone_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
        print(f"Julian Day: {jd}")
        return jd
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def format_dms(degrees):
    """Format degrees into degrees, minutes, seconds with high precision."""
    d = int(degrees)
    m_fraction = (degrees - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_pada(longitude):
    """Calculate nakshatra and pada from sidereal longitude."""
    longitude = longitude % 360
    nakshatra_index = int(longitude / 13.3333) % 27
    position_in_nakshatra = longitude % 13.3333
    pada = int(position_in_nakshatra / 3.3333) + 1
    return NAKSHATRAS[nakshatra_index], pada

def get_d16_position(sidereal_lon):
    """Calculate D16 position from sidereal longitude."""
    natal_sign_index = int(sidereal_lon // 30)
    d1_sign_deg = sidereal_lon % 30
    d16_segment = int(d1_sign_deg / 1.875)  # Each D16 segment is 1.875 degrees

    # Determine starting sign based on natal sign's nature
    if natal_sign_index in [0, 3, 6, 9]:  # Movable: Aries, Cancer, Libra, Capricorn
        start_sign = 0  # Aries
    elif natal_sign_index in [1, 4, 7, 10]:  # Fixed: Taurus, Leo, Scorpio, Aquarius
        start_sign = 4  # Leo
    elif natal_sign_index in [2, 5, 8, 11]:  # Dual: Gemini, Virgo, Sagittarius, Pisces
        start_sign = 8  # Sagittarius

    d16_sign_index = (start_sign + d16_segment) % 12
    segment_start = d16_segment * 1.875
    segment_position = d1_sign_deg - segment_start
    d16_deg = (segment_position / 1.875) * 30  # Scale to 30 degrees per sign

    nakshatra, pada = get_nakshatra_pada(sidereal_lon)
    return {
        "sign": SIGNS[d16_sign_index],
        "degrees": format_dms(d16_deg),
        "nakshatra": nakshatra,
        "pada": pada,
        "sign_index": d16_sign_index
    }

def get_d16_house(d16_sign_index, d16_asc_sign_index, is_ketu=False, rahu_house=None, enforce_opposition=False):
    """Assign house number using Whole Sign system, with optional opposition for Ketu."""
    if is_ketu and rahu_house is not None and enforce_opposition:
        # Place Ketu 6 houses (180 degrees) opposite Rahu
        house_number = (rahu_house + 5) % 12 + 1  # +5 for 6th house ahead (opposite)
    else:
        # Standard Whole Sign house calculation
        house_number = (d16_sign_index - d16_asc_sign_index + 12) % 12 + 1
    return house_number

def raman_Shodashamsha_D16(birth_date, birth_time, latitude, longitude, timezone_offset, enforce_opposition=False):
    """Calculate the Shodasamsa (D16) chart using Raman ayanamsa."""
    jd_ut = get_julian_day(birth_date, birth_time, timezone_offset)
    swe.set_sid_mode(swe.SIDM_RAMAN)
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_sidereal = ascmc[0] % 360
    d1_asc_sign = SIGNS[int(d1_asc_sidereal // 30)]

    d16_asc = get_d16_position(d1_asc_sidereal)
    d16_asc_sign_index = d16_asc['sign_index']

    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    d1_positions = {}
    for planet_id, name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {name}")
        lon = pos[0] % 360
        retrograde = 'R' if pos[3] < 0 else ''
        d1_positions[name] = (lon, retrograde)

    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, 'R')  # Ketu is always retrograde

    d16_positions = {}
    rahu_house = None
    for planet, (d1_lon, retro) in d1_positions.items():
        d16_pos = get_d16_position(d1_lon)
        if planet == 'Rahu':
            rahu_house = get_d16_house(d16_pos['sign_index'], d16_asc_sign_index, enforce_opposition=enforce_opposition)
            d16_positions[planet] = {
                "sign": d16_pos['sign'],
                "degrees": d16_pos['degrees'],
                "retrograde": retro,
                "house": rahu_house,
                "nakshatra": d16_pos['nakshatra'],
                "pada": d16_pos['pada']
            }
        elif planet == 'Ketu':
            house = get_d16_house(d16_pos['sign_index'], d16_asc_sign_index, 
                                  is_ketu=True, rahu_house=rahu_house, enforce_opposition=enforce_opposition)
            d16_positions[planet] = {
                "sign": d16_pos['sign'],
                "degrees": d16_pos['degrees'],
                "retrograde": retro,
                "house": house,
                "nakshatra": d16_pos['nakshatra'],
                "pada": d16_pos['pada']
            }
        else:
            house = get_d16_house(d16_pos['sign_index'], d16_asc_sign_index, enforce_opposition=enforce_opposition)
            d16_positions[planet] = {
                "sign": d16_pos['sign'],
                "degrees": d16_pos['degrees'],
                "retrograde": retro,
                "house": house,
                "nakshatra": d16_pos['nakshatra'],
                "pada": d16_pos['pada']
            }

    house_signs = [{"house": i + 1, "sign": SIGNS[(d16_asc_sign_index + i) % 12]} for i in range(12)]

    response = {
        "d1_ascendant": {"sign": d1_asc_sign, "degrees": format_dms(d1_asc_sidereal)},
        "d16_ascendant": {
            "sign": d16_asc['sign'],
            "degrees": d16_asc['degrees'],
            "nakshatra": d16_asc['nakshatra'],
            "pada": d16_asc['pada']
        },
        "planetary_positions": d16_positions,
        "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Raman",
            "chart_type": "Shodasamsa (D16)",
            "house_system": "Whole Sign",
            "enforce_opposition": enforce_opposition
        }
    }
    return response