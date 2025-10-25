import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (adjust if necessary)
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs and nakshatras
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
nakshatras = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
              'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
              'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
              'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
              'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']

def get_julian_day(date_str, time_str, timezone_offset):
    """
    Convert date and time to Julian Day with high precision.
    
    Args:
        date_str (str): Date in 'YYYY-MM-DD' format
        time_str (str): Time in 'HH:MM:SS' format
        timezone_offset (float): Timezone offset from UTC in hours
    
    Returns:
        float: Julian Day
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_datetime = datetime.combine(date_obj, time_obj.time())
        ut_datetime = local_datetime - timedelta(hours=timezone_offset)
        hour_decimal = ut_datetime.hour + (ut_datetime.minute / 60.0) + (ut_datetime.second / 3600.0)
        return swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds with precision."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_and_pada(longitude):
    """Calculate nakshatra and pada based on sidereal longitude."""
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    nakshatra = nakshatras[nakshatra_index]
    # Calculate pada (each nakshatra has 4 padas, each 3.3333°)
    position_in_nakshatra = longitude % 13.3333
    pada = int(position_in_nakshatra / 3.3333) + 1
    return nakshatra, pada

def get_d4_position(d1_lon):
    """
    Calculate D4 sign and degree from D1 sidereal longitude using Vedic astrology logic.
    
    Args:
        d1_lon (float): D1 sidereal longitude (0–360°)
    
    Returns:
        tuple: (D4 sign index, D4 degree within sign)
    """
    d1_sign_index = int(d1_lon // 30)  # 0–11 (Aries–Pisces)
    d1_sign_position = d1_lon % 30     # 0–30 degrees within the sign
    d4_division = 7.5
    segment = int(d1_sign_position // d4_division)  # 0, 1, 2, or 3

    # Correct offsets for D4 sign calculation (1st, 4th, 7th, 10th signs)
    offsets = [0, 3, 6, 9]
    d4_sign_index = (d1_sign_index + offsets[segment]) % 12

    # Calculate D4 degree within the sign
    segment_position = d1_sign_position % d4_division
    d4_degree = (segment_position / d4_division) * 30  # Scale to 0–30°
    return d4_sign_index, d4_degree

def get_d4_house(d4_lon, d4_asc_sign_index):
    """Calculate house number in D4 chart using Whole Sign system."""
    sign_index = int(d4_lon // 30) % 12
    house_index = (sign_index - d4_asc_sign_index) % 12
    return house_index + 1

def lahairi_Chaturthamsha(data):
    """Calculate the Chaturthamsha (D4) chart with retrograde, nakshatras, and padas."""
    # Parse inputs
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    birth_date = data['birth_date']
    birth_time = data['birth_time']

    # Calculate Julian Day
    jd_ut = get_julian_day(birth_date, birth_time, timezone_offset)

    # Set Lahiri Ayanamsa for sidereal calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Calculate D1 sidereal positions for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    d1_positions = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            error_msg = swe.get_err_msg().decode()
            raise Exception(f"Error calculating {planet_name}: {error_msg}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        d1_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu (opposite Rahu)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, '')

    # Calculate D1 Ascendant (sidereal) using Whole Sign system
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_d1 = ascmc[0] % 360

    # Calculate D4 positions
    d4_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d4_sign_index, d4_degree = get_d4_position(d1_lon)
        d4_lon = (d4_sign_index * 30) + d4_degree
        d4_positions[planet] = (d4_lon, retro)

    # Calculate D4 Ascendant
    d4_asc_sign_index, d4_asc_degree = get_d4_position(ascendant_d1)
    d4_asc_lon = (d4_asc_sign_index * 30) + d4_asc_degree

    # Assign D4 houses based on D4 Ascendant
    planet_houses = {planet: get_d4_house(d4_lon, d4_asc_sign_index) 
                     for planet, (d4_lon, _) in d4_positions.items()}

    # Calculate house signs based on D4 Ascendant
    house_signs = []
    for i in range(12):
        sign_index = (d4_asc_sign_index + i) % 12
        house_signs.append({"house": i + 1, "sign": signs[sign_index]})

    # Format output with nakshatras and padas
    planetary_positions_json = {}
    for planet, (d4_lon, retro) in d4_positions.items():
        sign_index = int(d4_lon // 30) % 12
        sign = signs[sign_index]
        sign_deg = d4_lon % 30
        dms = format_dms(sign_deg)
        house = planet_houses[planet]
        nakshatra, pada = get_nakshatra_and_pada(d4_lon)
        planetary_positions_json[planet] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    asc_nakshatra, asc_pada = get_nakshatra_and_pada(d4_asc_lon)
    ascendant_json = {
        "sign": signs[d4_asc_sign_index],
        "degrees": format_dms(d4_asc_lon % 30),
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    # Construct response
    response = {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        # "house_signs": house_signs,
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}",
            "chart_type": "Chaturthamsha (D4)",
            "house_system": "Whole Sign"
        }
    }

    return response