import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs list
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra list with their start degrees
NAKSHATRAS = [
    ("Ashwini", 0), ("Bharani", 13.3333), ("Krittika", 26.6667), ("Rohini", 40),
    ("Mrigashira", 53.3333), ("Ardra", 66.6667), ("Punarvasu", 80), ("Pushya", 93.3333),
    ("Ashlesha", 106.6667), ("Magha", 120), ("Purva Phalguni", 133.3333), ("Uttara Phalguni", 146.6667),
    ("Hasta", 160), ("Chitra", 173.3333), ("Swati", 186.6667), ("Vishakha", 200),
    ("Anuradha", 213.3333), ("Jyeshtha", 226.6667), ("Mula", 240), ("Purva Ashadha", 253.3333),
    ("Uttara Ashadha", 266.6667), ("Shravana", 280), ("Dhanishta", 293.3333), ("Shatabhisha", 306.6667),
    ("Purva Bhadrapada", 320), ("Uttara Bhadrapada", 333.3333), ("Revati", 346.6667)
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Calculate Julian Day in Universal Time (UT) from local time.
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format
        time_str (str): Birth time in 'HH:MM:SS' format
        tz_offset (float): Timezone offset from UTC in hours
    Returns:
        float: Julian Day in UT
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_planetary_positions(jd):
    """
    Calculate sidereal positions and retrograde status of planets using Lahiri Ayanamsa.
    Args:
        jd (float): Julian Day in UT
    Returns:
        dict: Planetary positions with longitudes and retrograde status
    """
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE, 'Ketu': None
        }
        positions = {}
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        for planet, pid in planets.items():
            if planet == 'Ketu':
                continue
            pos, ret = swe.calc_ut(jd, pid, flags)
            if ret < 0:
                raise ValueError(f"Error calculating position for {planet}")
            longitude = pos[0] % 360.0
            speed = pos[3]  # Longitudinal speed in degrees per day
            # Determine retrograde status
            if planet in ['Sun', 'Moon']:
                retrograde = False  # Sun and Moon are never retrograde
            elif planet == 'Rahu':
                retrograde = True   # Rahu is always retrograde in Vedic astrology
            else:
                retrograde = speed < 0  # Negative speed indicates retrograde motion
            positions[planet] = (longitude, retrograde)
        
        # Ketu: 180° opposite Rahu, always retrograde
        rahu_lon = positions['Rahu'][0]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        positions['Ketu'] = (ketu_lon, True)
        return positions
    except Exception as e:
        raise Exception(f"Planetary calculation failed: {str(e)}")

def calculate_whole_sign_cusps(moon_longitude):
    """
    Calculate house cusps for the Moon Chart using Whole Sign system.
    Args:
        moon_longitude (float): Moon's sidereal longitude in degrees
    Returns:
        list: 12 house cusps in degrees
    """
    moon_sign_index = int(moon_longitude // 30)
    house_cusps = [(moon_sign_index * 30 + i * 30) % 360 for i in range(12)]
    return house_cusps

def assign_planets_to_houses(planetary_positions, moon_sign_index):
    """
    Assign planets to houses in the Moon Chart using Whole Sign system.
    Args:
        planetary_positions (dict): Planetary longitudes and retrograde statuses
        moon_sign_index (int): Index of Moon's sign (0=Aries, 11=Pisces)
    Returns:
        dict: House assignments for each planet
    """
    house_assignments = {}
    for planet, (longitude, _) in planetary_positions.items():
        planet_sign_index = int(longitude // 30)
        house = (planet_sign_index - moon_sign_index) % 12 + 1
        house_assignments[planet] = house
    return house_assignments

def format_dms(degrees):
    """
    Format degrees into degrees, minutes, and seconds.
    Args:
        degrees (float): Angle in decimal degrees
    Returns:
        str: Formatted string (e.g., "21° 50' 0\"")
    """
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def validate_input(data):
    """
    Validate input JSON data.
    Args:
        data (dict): Input JSON data
    Raises:
        ValueError: If validation fails
    """
    required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in data for key in required_fields):
        raise ValueError("Missing required parameters")
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")

def get_nakshatra_and_pada(longitude):
    """
    Determine the nakshatra and pada based on longitude.
    Args:
        longitude (float): Sidereal longitude in degrees
    Returns:
        tuple: (nakshatra_name, pada_number)
    """
    longitude = longitude % 360
    for i, (nakshatra, start) in enumerate(NAKSHATRAS):
        end = NAKSHATRAS[(i + 1) % len(NAKSHATRAS)][1] if i < 26 else 360
        if start <= longitude < end:
            nakshatra_name = nakshatra
            pada = int((longitude - start) / 3.3333) + 1
            return nakshatra_name, pada
    return "Revati", 4  # Fallback for edge case

def lahairi_moon_chart(data):
    """
    Calculate Moon Chart (sidereal) with Whole Sign house system, including retrograde, nakshatras, and padas.
    Args:
        data (dict): Input JSON data
    Returns:
        dict: Moon Chart data with Chandra Lagna, house cusps, and planetary positions
    """
    # Extract input data
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    tz_offset = float(data['timezone_offset'])

    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate planetary positions with retrograde status
    planetary_positions = calculate_planetary_positions(jd)

    # Moon's position (Chandra Lagna)
    moon_longitude, moon_retro = planetary_positions['Moon']
    moon_sign_index = int(moon_longitude // 30)
    moon_sign = SIGNS[moon_sign_index]
    moon_degree = moon_longitude % 30
    moon_nakshatra, moon_pada = get_nakshatra_and_pada(moon_longitude)

    # Calculate house cusps for Moon Chart (Whole Sign)
    house_cusps = calculate_whole_sign_cusps(moon_longitude)

    # Assign planets to houses in Moon Chart
    house_assignments = assign_planets_to_houses(planetary_positions, moon_sign_index)

    # Prepare house cusps data
    house_data = [
        {
            "house": i + 1,
            "cusp": format_dms(house_cusps[i]),
            "sign": SIGNS[(moon_sign_index + i) % 12]
        }
        for i in range(12)
    ]

    # Prepare planetary positions data with retrograde, nakshatra, and pada
    planetary_data = [
        {
            "planet": planet,
            "longitude": format_dms(longitude),
            "sign": SIGNS[int(longitude // 30)],
            "retrograde": retrograde,
            "house": house_assignments[planet],
            "nakshatra": get_nakshatra_and_pada(longitude)[0],
            "pada": get_nakshatra_and_pada(longitude)[1]
        }
        for planet, (longitude, retrograde) in planetary_positions.items()
    ]

    # Construct response
    response = {
        "user_name": user_name,
        "chandra_lagna": {
            "longitude": format_dms(moon_longitude),
            "sign": moon_sign,
            "degree": format_dms(moon_degree),
            "retrograde": moon_retro,
            "nakshatra": moon_nakshatra,
            "pada": moon_pada
        },
        # "house_cusps": house_data,
        "planetary_positions": planetary_data,
        "metadata": {
            "ayanamsa": "Lahiri",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat(),
            "input": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            }
        }
    }
    return response