# # calculations.py
# import swisseph as swe
# from datetime import datetime, timedelta, timezone

# # List of zodiac signs
# signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
#          'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# def get_house(lon, asc_sign_index):
#     """
#     Calculate house number based on planet longitude and ascendant sign index (Whole Sign system).
    
#     Args:
#         lon (float): Planet's longitude (0–360°)
#         asc_sign_index (int): Ascendant's sign index (0–11, Aries–Pisces)
    
#     Returns:
#         int: House number (1–12)
#     """
#     sign_index = int(lon // 30) % 12  # Planet's sign index
#     house_index = (sign_index - asc_sign_index) % 12  # Adjusted house index
#     return house_index + 1  # 1-based house number

# def longitude_to_sign(deg):
#     """Convert longitude to sign and degree within sign."""
#     deg = deg % 360
#     sign_index = int(deg // 30)
#     sign = signs[sign_index]
#     sign_deg = deg % 30
#     return sign, sign_deg

# def format_dms(deg):
#     """Format degrees as degrees, minutes, seconds."""
#     d = int(deg)
#     m_fraction = (deg - d) * 60
#     m = int(m_fraction)
#     s = (m_fraction - m) * 60
#     return f"{d}° {m}' {s:.2f}\""

# def calculate_transit_chart(data):
#     """
#     Calculate the transit chart based on birth data and current time.
    
#     Parameters:
#     - data: Dictionary containing user_name, birth_date, birth_time, latitude, longitude, timezone_offset.
    
#     Returns:
#     - Dictionary containing the transit chart data or raises an exception on error.
#     """
#     # Extract and validate inputs
#     latitude = float(data['latitude'])
#     longitude = float(data['longitude'])
#     timezone_offset = float(data['timezone_offset'])

#     if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
#         raise ValueError("Invalid latitude or longitude")

#     # Parse birth date and time
#     birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
#     birth_time = datetime.strptime(data['birth_time'], '%H:%M:%S').time()
#     local_birth_datetime = datetime.combine(birth_date, birth_time)
#     ut_birth_datetime = local_birth_datetime - timedelta(hours=timezone_offset)
#     hour_decimal_birth = ut_birth_datetime.hour + ut_birth_datetime.minute / 60.0 + ut_birth_datetime.second / 3600.0
#     jd_ut_birth = swe.julday(ut_birth_datetime.year, ut_birth_datetime.month, 
#                              ut_birth_datetime.day, hour_decimal_birth)

#     # Get current UTC time for transit
#     current_utc = datetime.now(timezone.utc)
#     jd_ut_transit = swe.julday(current_utc.year, current_utc.month, current_utc.day, 
#                                current_utc.hour + current_utc.minute / 60.0 + current_utc.second / 3600.0)

#     # Set Lahiri ayanamsa for sidereal calculations
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     ayanamsa_value_birth = swe.get_ayanamsa_ut(jd_ut_birth)
#     ayanamsa_value_transit = swe.get_ayanamsa_ut(jd_ut_transit)

#     # Calculate natal ascendant for house system
#     cusps, ascmc = swe.houses_ex(jd_ut_birth, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
#     ascendant_lon = ascmc[0] % 360
#     asc_sign_index = int(ascendant_lon // 30)
#     asc_sign = signs[asc_sign_index]

#     # Calculate transit planetary positions for current time
#     planets = [
#         (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
#         (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
#         (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
#     ]
#     flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
#     transit_positions = {}
#     for planet_id, planet_name in planets:
#         pos, ret = swe.calc_ut(jd_ut_transit, planet_id, flag)
#         if ret < 0:
#             raise ValueError(f"Error calculating {planet_name} for transit")
#         lon = pos[0] % 360
#         speed = pos[3]
#         retrograde = 'R' if speed < 0 else ''
#         transit_positions[planet_name] = (lon, retrograde)

#     # Calculate Ketu (180° opposite Rahu)
#     rahu_lon_transit = transit_positions['Rahu'][0]
#     ketu_lon_transit = (rahu_lon_transit + 180) % 360
#     transit_positions['Ketu'] = (ketu_lon_transit, '')

#     # Assign transit planets to houses based on natal ascendant
#     transit_houses = {planet: get_house(lon, asc_sign_index) 
#                       for planet, (lon, _) in transit_positions.items()}

#     # Format transit output
#     transit_positions_json = {}
#     for planet_name, (lon, retro) in transit_positions.items():
#         sign, sign_deg = longitude_to_sign(lon)
#         dms = format_dms(sign_deg)
#         house = transit_houses[planet_name]
#         transit_positions_json[planet_name] = {
#             "sign": sign,
#             "degrees": dms,
#             "retrograde": retro,
#             "house": house
#         }

#     # Format ascendant and current time
#     ascendant_json = {"sign": asc_sign, "degrees": format_dms(ascendant_lon % 30)}
#     current_utc_str = current_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

#     # Construct response
#     response = {
#         "user_name": data['user_name'],
#         "birth_details": {
#             "birth_date": data['birth_date'],
#             "birth_time": birth_time.strftime('%H:%M:%S'),
#             "latitude": latitude,
#             "longitude": longitude,
#             "timezone_offset": timezone_offset
#         },
#         "transit_time": current_utc_str,
#         "natal_ascendant": ascendant_json,
#         "transit_positions": transit_positions_json,
#         "notes": {
#             "ayanamsa": "Lahiri",
#             "ayanamsa_value_birth": f"{ayanamsa_value_birth:.6f}",
#             "ayanamsa_value_transit": f"{ayanamsa_value_transit:.6f}",
#             "chart_type": "Transit",
#             "house_system": "Whole Sign"
#         }
#     }

#     return response






import swisseph as swe
from datetime import datetime, timedelta, timezone

# Set Swiss Ephemeris path (ensure ephemeris files are in this directory)
swe.set_ephe_path('astro_engine/ephe')

# List of zodiac signs
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatra list with their start and end degrees
nakshatras = [
    ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
    ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
]

def get_house(lon, asc_sign_index):
    """
    Calculate house number based on planet longitude and ascendant sign index (Whole Sign system).
    
    Args:
        lon (float): Planet's longitude (0–360°)
        asc_sign_index (int): Ascendant's sign index (0–11, Aries–Pisces)
    
    Returns:
        int: House number (1–12)
    """
    sign_index = int(lon // 30) % 12  # Planet's sign index
    house_index = (sign_index - asc_sign_index) % 12  # Adjusted house index
    return house_index + 1  # 1-based house number

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_and_pada(longitude):
    """Determine the nakshatra and pada based on longitude."""
    longitude = longitude % 360
    for nakshatra, start, end in nakshatras:
        if start <= longitude < end:
            pada = int(((longitude - start) / (end - start)) * 4) + 1
            return nakshatra, pada
    return 'Revati', 4 if longitude >= 346.6667 else 1

def lahairi_tranist(data):
    """Calculate transit positions for current time based on birth data.
    
    Args:
        data: Dictionary containing:
            - birth_date: YYYY-MM-DD format
            - birth_time: HH:MM:SS format
            - latitude: -90 to 90
            - longitude: -180 to 180
            - timezone_offset: UTC offset in hours
            - user_name: optional
            
    Returns:
        Dictionary containing:
            - user_name (if provided)
            - birth_details (input data)
            - transit_positions (planetary positions in natal format)
            - natal_ascendant (birth chart ascendant)
            - notes (ayanamsa values, transit time)
            
    Raises:
        ValueError: If required fields are missing or invalid
        Exception: For calculation errors
    """
    # Validate inputs
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid input data: {str(e)}")

    if not (-90 <= latitude <= 90):
        raise ValueError(f"Invalid latitude: {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Invalid longitude: {longitude}")

    # Parse birth date and time
    birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(data['birth_time'], '%H:%M:%S').time()
    local_birth_datetime = datetime.combine(birth_date, birth_time)
    ut_birth_datetime = local_birth_datetime - timedelta(hours=timezone_offset)
    hour_decimal_birth = ut_birth_datetime.hour + ut_birth_datetime.minute / 60.0 + ut_birth_datetime.second / 3600.0
    jd_ut_birth = swe.julday(ut_birth_datetime.year, ut_birth_datetime.month, 
                             ut_birth_datetime.day, hour_decimal_birth)

    # Get current UTC time for transit
    current_utc = datetime.now(timezone.utc)
    jd_ut_transit = swe.julday(current_utc.year, current_utc.month, current_utc.day, 
                               current_utc.hour + current_utc.minute / 60.0 + current_utc.second / 3600.0)

    # Set Lahiri ayanamsa for sidereal calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value_birth = swe.get_ayanamsa_ut(jd_ut_birth)
    ayanamsa_value_transit = swe.get_ayanamsa_ut(jd_ut_transit)

    # Calculate natal ascendant for house system
    cusps, ascmc = swe.houses_ex(jd_ut_birth, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Calculate transit planetary positions for current time
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    transit_positions = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut_transit, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {planet_name} for transit")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        transit_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon_transit = transit_positions['Rahu'][0]
    ketu_lon_transit = (rahu_lon_transit + 180) % 360
    transit_positions['Ketu'] = (ketu_lon_transit, '')

    # Assign transit planets to houses based on natal ascendant
    transit_houses = {planet: get_house(lon, asc_sign_index) 
                      for planet, (lon, _) in transit_positions.items()}

    # Format transit output with nakshatra and pada
    transit_positions_json = {}
    for planet_name, (lon, retro) in transit_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = transit_houses[planet_name]
        nakshatra, pada = get_nakshatra_and_pada(lon)
        transit_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    # Format ascendant with nakshatra and pada
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(ascendant_lon)
    ascendant_json = {
        "sign": asc_sign,
        "degrees": format_dms(ascendant_lon % 30),
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    # Format current time
    current_utc_str = current_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Construct response in natal-style format
    response = {
        "user_name": data.get('user_name'),
        "birth_details": {
            "birth_date": data['birth_date'],
            "birth_time": data['birth_time'],
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "transit_time": current_utc_str,
        "transit_positions": transit_positions_json,  # This becomes planetary_positions in batch response
        "natal_ascendant": ascendant_json,          # This becomes ascendant in batch response
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value_birth": f"{ayanamsa_value_birth:.6f}",
            "ayanamsa_value_transit": f"{ayanamsa_value_transit:.6f}",
            "chart_type": "Transit",
            "house_system": "Whole Sign"
        }
    }

    return response