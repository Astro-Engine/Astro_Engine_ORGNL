import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Zodiac signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra list
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day (UT)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_ascendant(jd, latitude, longitude):
    """Calculate the sidereal ascendant longitude using Raman Ayanamsa."""
    try:
        swe.set_sid_mode(swe.SIDM_RAMAN)  # Set Raman Ayanamsa
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
        ascendant = ascmc[0] % 360.0  # Ascendant longitude in degrees
        return ascendant
    except Exception as e:
        raise Exception(f"Ascendant calculation failed: {str(e)}")

def get_planet_positions(jd):
    """Calculate sidereal positions and retrograde status of planets."""
    try:
        planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu will be calculated as 180° opposite Rahu
        }
        positions = {}
        for planet, pid in planets.items():
            if planet == 'Ketu':
                continue
            pos, ret = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
            if ret < 0:
                raise ValueError(f"Error calculating position for {planet}")
            longitude = pos[0] % 360.0
            # Determine retrograde status
            if planet in ['Sun', 'Moon']:
                retrospective = False
            elif planet == 'Rahu':
                retrospective = True
            else:
                retrospective = pos[3] < 0  # Speed component (index 3) negative means retrograde
            positions[planet] = (longitude, retrospective)
        # Calculate Ketu (180° opposite Rahu)
        rahu_lon = positions['Rahu'][0]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        positions['Ketu'] = (ketu_lon, True)  # Ketu is always retrograde
        return positions
    except Exception as e:
        raise Exception(f"Planetary calculation failed: {str(e)}")

def calculate_equal_bhava_cusps(ascendant):
    """Calculate the midpoints (cusps) of all 12 houses, each spanning 30 degrees."""
    cusps = [(ascendant + (n - 1) * 30) % 360 for n in range(1, 13)]
    return cusps

def assign_planets_to_houses(planetary_positions, ascendant_sign_index):
    """Assign planets to houses using Whole Sign system based on Equal Bhava Lagna."""
    house_assignments = {}
    for planet, (longitude, _) in planetary_positions.items():
        planet_sign_index = int(longitude // 30)
        house = (planet_sign_index - ascendant_sign_index) % 12 + 1
        house_assignments[planet] = house
    return house_assignments

def format_dms(degrees):
    """Format degrees into degrees, minutes, and seconds."""
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def get_nakshatra(longitude):
    """Determine the nakshatra based on sidereal longitude."""
    longitude = longitude % 360
    nakshatra_index = int(longitude / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]

def get_pada(longitude):
    """Determine the pada (1-4) within the nakshatra based on sidereal longitude."""
    longitude = longitude % 360
    position_in_nakshatra = longitude % 13.3333
    pada = int(position_in_nakshatra / 3.3333) + 1
    return pada

def raman_equal_bava_lagnas(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """Calculate Equal Bhava Lagna, house cusps, and planetary positions with nakshatra and pada."""
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    ascendant = calculate_ascendant(jd, latitude, longitude)
    ascendant_sign_index = int(ascendant // 30)
    planetary_positions = get_planet_positions(jd)

    cusps_degrees = calculate_equal_bhava_cusps(ascendant)
    cusps_formatted = [format_dms(cusp) for cusp in cusps_degrees]

    house_data = [
        {
            "house": i + 1,
            "cusp": cusps_formatted[i],
            "sign": SIGNS[int(cusps_degrees[i] // 30)]
        }
        for i in range(12)
    ]

    house_assignments = assign_planets_to_houses(planetary_positions, ascendant_sign_index)

    planetary_data = [
        {
            "planet": planet,
            "longitude": format_dms(longitude),
            "sign": SIGNS[int(longitude // 30)],
            "retrograde": retrograde,
            "house": house_assignments[planet],
            "nakshatra": get_nakshatra(longitude),
            "pada": get_pada(longitude)
        }
        for planet, (longitude, retrograde) in planetary_positions.items()
    ]

    response = {
        "user_name": user_name,
        "ascendant": {
            "longitude": format_dms(ascendant),
            "sign": SIGNS[ascendant_sign_index],
            "nakshatra": get_nakshatra(ascendant),
            "pada": get_pada(ascendant)
        },
        "planetary_positions": planetary_data,
        # "house_cusps": house_data,
        "metadata": {
            "ayanamsa": "Raman",
            "house_system": "Equal Bhava (Whole Sign based)",
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