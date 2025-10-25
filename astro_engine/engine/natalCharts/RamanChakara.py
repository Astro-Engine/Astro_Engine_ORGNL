import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Define zodiac signs
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Define nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Convert local birth date and time to Julian Day in Universal Time (UT).
    
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format
        time_str (str): Birth time in 'HH:MM:SS' format
        tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        float: Julian Day for the UT time
    """
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_sidereal_positions(jd, latitude, longitude):
    """
    Calculate sidereal longitudes of planets and ascendant using Lahiri Ayanamsa.
    
    Args:
        jd (float): Julian Day in UT
        latitude (float): Latitude of birth place in degrees
        longitude (float): Longitude of birth place in degrees
    
    Returns:
        dict: Sidereal longitudes of planets and ascendant
    """
    swe.set_sid_mode(swe.SIDM_RAMAN)  # Set Lahiri Ayanamsa
    positions = {}
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": (swe.MEAN_NODE, 180)  # Ketu is 180° from Rahu
    }
    
    # Calculate planetary positions
    for planet, pid in planet_ids.items():
        if planet == "Ketu":
            rahu_pos = swe.calc_ut(jd, pid[0], swe.FLG_SIDEREAL)[0][0]
            positions[planet] = (rahu_pos + pid[1]) % 360
        else:
            pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0][0]
            positions[planet] = pos % 360
    
    # Calculate ascendant
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_SIDEREAL)  # 'W' for whole sign
    positions["Ascendant"] = ascmc[0] % 360
    
    return positions

def get_sign(longitude):
    """
    Determine the zodiac sign and degree within the sign from longitude.
    
    Args:
        longitude (float): Sidereal longitude in degrees
    
    Returns:
        tuple: (sign name, degrees within sign)
    """
    sign_idx = int(longitude // 30)
    return SIGNS[sign_idx], longitude % 30

def get_nakshatra(longitude):
    """
    Determine the nakshatra based on longitude.
    
    Args:
        longitude (float): Sidereal longitude in degrees
    
    Returns:
        str: Nakshatra name
    """
    longitude = longitude % 360
    nakshatra_index = int(longitude / (360 / 27))
    return NAKSHATRAS[nakshatra_index]

def generate_chart(positions, reference_sign_idx):
    """
    Generate a chart (Lagna, Chandra, or Surya) using the whole sign house system.
    
    Args:
        positions (dict): Sidereal longitudes of planets and ascendant
        reference_sign_idx (int): Index of the reference sign (0-11)
    
    Returns:
        dict: Chart with house numbers mapped to signs and planets
    """
    chart = {sign: [] for sign in SIGNS}
    for planet, lon in positions.items():
        sign, _ = get_sign(lon)
        chart[sign].append(planet)
    
    # Assign house numbers relative to the reference sign
    house_chart = {}
    for i, sign in enumerate(SIGNS):
        house_num = (i - reference_sign_idx) % 12 + 1
        house_chart[house_num] = {"sign": sign, "planets": chart[sign]}
    return house_chart

def format_dms(degrees):
    """
    Format degrees into degrees, minutes, and seconds.
    
    Args:
        degrees (float): Angle in decimal degrees
    
    Returns:
        str: Formatted string as "D° M' S\""
    """
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def raman_sudarshan_chakra(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """
    Calculate the Sudarshan Chakra and planetary details based on birth details.
    
    Args:
        birth_date (str): Birth date in 'YYYY-MM-DD' format
        birth_time (str): Birth time in 'HH:MM:SS' format
        latitude (float): Latitude of birth place in degrees
        longitude (float): Longitude of birth place in degrees
        tz_offset (float): Timezone offset in hours
        user_name (str): Name of the user (default 'Unknown')
    
    Returns:
        dict: Sudarshan Chakra details with planetary positions and nakshatras
    """
    # Step 1: Calculate Julian Day in UT
    jd_birth = get_julian_day(birth_date, birth_time, tz_offset)

    # Step 2: Calculate sidereal positions
    positions = calculate_sidereal_positions(jd_birth, latitude, longitude)

    # Step 3: Compute planetary positions with nakshatras
    planetary_positions = []
    for planet, lon in positions.items():
        if planet == "Ascendant":
            continue
        sign, degree = get_sign(lon)
        nakshatra = get_nakshatra(lon)
        planetary_positions.append({
            "planet": planet,
            "longitude": format_dms(lon),
            "sign": sign,
            "degree": format_dms(degree),
            "nakshatra": nakshatra
        })

    # Step 4: Ascendant details with nakshatra
    asc_lon = positions["Ascendant"]
    asc_sign, asc_degree = get_sign(asc_lon)
    asc_nakshatra = get_nakshatra(asc_lon)
    ascendant = {
        "longitude": format_dms(asc_lon),
        "sign": asc_sign,
        "degree": format_dms(asc_degree),
        "nakshatra": asc_nakshatra
    }

    # Step 5: Determine reference sign indices
    asc_sign_idx = SIGNS.index(asc_sign)
    moon_sign, _ = get_sign(positions["Moon"])
    moon_sign_idx = SIGNS.index(moon_sign)
    sun_sign, _ = get_sign(positions["Sun"])
    sun_sign_idx = SIGNS.index(sun_sign)

    # Step 6: Generate the three charts
    lagna_chart = generate_chart(positions, asc_sign_idx)
    chandra_chart = generate_chart(positions, moon_sign_idx)
    surya_chart = generate_chart(positions, sun_sign_idx)

    # Step 7: Construct the response
    response = {
        "user_name": user_name,
        "planetary_positions": planetary_positions,
        "ascendant": ascendant,
        "sudarshan_chakra": {
            "lagna_chart": lagna_chart,
            "chandra_chart": chandra_chart,
            "surya_chart": surya_chart
        }
    }
    return response