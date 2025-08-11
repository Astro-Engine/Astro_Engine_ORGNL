

# import swisseph as swe
# from datetime import datetime, timedelta
# import math

# # Set Swiss Ephemeris path (adjust path as needed)
# swe.set_ephe_path('astro_api/ephe')

# # Constants
# PLANETS = {
#     'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
#     'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'Uranus': swe.URANUS,
#     'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO, 'North Node': swe.MEAN_NODE
# }
# ASPECTS = {
#     'Conjunction': {'angle': 0, 'orb': 8}, 'Sextile': {'angle': 60, 'orb': 6},
#     'Square': {'angle': 90, 'orb': 8}, 'Trine': {'angle': 120, 'orb': 8},
#     'Opposition': {'angle': 180, 'orb': 8}
# }
# SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio',
#          'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# NAKSHATRAS = [
#     ('Ashwini', 0, 13.3333),
#     ('Bharani', 13.3333, 26.6667),
#     ('Krittika', 26.6667, 40),
#     ('Rohini', 40, 53.3333),
#     ('Mrigashira', 53.3333, 66.6667),
#     ('Ardra', 66.6667, 80),
#     ('Punarvasu', 80, 93.3333),
#     ('Pushya', 93.3333, 106.6667),
#     ('Ashlesha', 106.6667, 120),
#     ('Magha', 120, 133.3333),
#     ('Purva Phalguni', 133.3333, 146.6667),
#     ('Uttara Phalguni', 146.6667, 160),
#     ('Hasta', 160, 173.3333),
#     ('Chitra', 173.3333, 186.6667),
#     ('Swati', 186.6667, 200),
#     ('Vishakha', 200, 213.3333),
#     ('Anuradha', 213.3333, 226.6667),
#     ('Jyeshtha', 226.6667, 240),
#     ('Mula', 240, 253.3333),
#     ('Purva Ashadha', 253.3333, 266.6667),
#     ('Uttara Ashadha', 266.6667, 280),
#     ('Shravana', 280, 293.3333),
#     ('Dhanishta', 293.3333, 306.6667),
#     ('Shatabhisha', 306.6667, 320),
#     ('Purva Bhadrapada', 320, 333.3333),
#     ('Uttara Bhadrapada', 333.3333, 346.6667),
#     ('Revati', 346.6667, 360)
# ]

# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date, time, and timezone offset to Julian Day."""
#     dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     dt_utc = dt - timedelta(hours=tz_offset)
#     return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
#                       dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)

# def format_degrees(deg):
#     """Convert decimal degrees to degrees, minutes, and seconds."""
#     degrees = int(deg)
#     minutes = int((deg - degrees) * 60)
#     seconds = int(((deg - degrees) * 60 - minutes) * 60)
#     return f"{degrees}° {minutes}' {seconds}\""

# def calculate_sidereal_position(jd, planet_id):
#     """Calculate sidereal position for a planet using Lahiri ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
#     try:
#         lon = float(result[0][0])
#         retrograde = result[3] < 0 if len(result) > 3 and planet_id != swe.MEAN_NODE else False
#     except (IndexError, TypeError) as e:
#         raise ValueError(f"Failed to extract longitude from {result} for planet {planet_id}")
#     return lon, retrograde

# def calculate_midpoint(lon1, lon2):
#     """Calculate the midpoint longitude using the shortest arc."""
#     lon1, lon2 = lon1 % 360, lon2 % 360
#     diff = abs(lon1 - lon2)
#     if diff > 180:
#         diff = 360 - diff
#         if lon1 > lon2:
#             lon1, lon2 = lon2, lon1
#         mid = (lon1 + diff / 2 + 180) % 360
#     else:
#         mid = (lon1 + lon2) / 2
#     return mid

# def calculate_planetary_positions(jd):
#     """Calculate sidereal planetary positions."""
#     positions = {}
#     for planet_name, planet_id in PLANETS.items():
#         lon, retrograde = calculate_sidereal_position(jd, planet_id)
#         sign_idx = int(lon // 30)
#         sign = SIGNS[sign_idx]
#         degree_in_sign = lon % 30
#         positions[planet_name] = {
#             'longitude': lon,
#             'sign': sign,
#             'degree': format_degrees(degree_in_sign),
#             'retrograde': retrograde
#         }
#     nn_lon = positions['North Node']['longitude']
#     sn_lon = (nn_lon + 180) % 360
#     sign_idx = int(sn_lon // 30)
#     sign = SIGNS[sign_idx]
#     degree_in_sign = sn_lon % 30
#     positions['South Node'] = {
#         'longitude': sn_lon,
#         'sign': sign,
#         'degree': format_degrees(degree_in_sign),
#         'retrograde': True
#     }
#     return positions

# def calculate_ascendant_and_houses(jd, lat, lon):
#     """Calculate Ascendant, MC, and ascendant sign index."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     house_cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
#     asc = ascmc[0] % 360
#     mc = ascmc[1] % 360
#     asc_sign_idx = int(asc // 30)
#     return asc, mc, asc_sign_idx

# def assign_planets_to_houses(positions, asc_sign_idx):
#     """Assign planets to Whole Sign houses."""
#     houses = {}
#     for planet, data in positions.items():
#         longitude = data['longitude']
#         planet_sign_idx = int(longitude // 30)
#         house = (planet_sign_idx - asc_sign_idx) % 12 + 1
#         houses[planet] = house
#     return houses

# def calculate_composite_positions(pos_a, pos_b):
#     """Calculate composite planetary positions from two natal charts."""
#     positions = {}
#     for planet in pos_a:
#         lon_a = pos_a[planet]['longitude']
#         lon_b = pos_b[planet]['longitude']
#         lon_mid = calculate_midpoint(lon_a, lon_b)
#         sign_idx = int(lon_mid // 30)
#         sign = SIGNS[sign_idx]
#         degree_in_sign = lon_mid % 30
#         retrograde = pos_a[planet]['retrograde'] or pos_b[planet]['retrograde']
#         positions[planet] = {
#             'longitude': lon_mid,
#             'sign': sign,
#             'degree': format_degrees(degree_in_sign),
#             'retrograde': retrograde
#         }
#     return positions

# def calculate_composite_angles(jd_a, jd_b, lat_a, lon_a, lat_b, lon_b):
#     """Calculate composite Ascendant and MC using midpoint method."""
#     jd_mid = (jd_a + jd_b) / 2
#     ref_lat = (lat_a + lat_b) / 2
#     ref_lon = (lon_a + lon_b) / 2
#     _, ascmc_mid = swe.houses_ex(jd_mid, ref_lat, ref_lon, b'W', flags=swe.FLG_SIDEREAL)
#     asc_composite = ascmc_mid[0] % 360
#     mc_composite = ascmc_mid[1] % 360
#     asc_sign_idx_composite = int(asc_composite // 30)
#     return asc_composite, mc_composite, asc_sign_idx_composite

# def calculate_aspects(positions):
#     """Calculate aspects between composite planets and points."""
#     aspects = []
#     points = list(positions.keys())
#     for i in range(len(points)):
#         for j in range(i + 1, len(points)):
#             p1, p2 = points[i], points[j]
#             lon1, lon2 = positions[p1]['longitude'], positions[p2]['longitude']
#             diff = min(abs(lon1 - lon2), 360 - abs(lon1 - lon2))
#             for aspect_name, data in ASPECTS.items():
#                 if abs(diff - data['angle']) <= data['orb']:
#                     aspects.append({
#                         'point_a': p1,
#                         'point_b': p2,
#                         'aspect': aspect_name,
#                         'angle': diff,
#                         'orb': abs(diff - data['angle'])
#                     })
#     return aspects

# def validate_person_data(person_data, person_label):
#     """Validate required fields for birth data."""
#     required = ['date', 'time', 'lat', 'lon', 'tz_offset']
#     missing = [field for field in required if field not in person_data]
#     if missing:
#         return False, f"Missing fields for {person_label}: {', '.join(missing)}"
#     return True, None

# def get_nakshatra_pada(longitude):
#     """Calculate nakshatra and pada for a given longitude."""
#     longitude = longitude % 360
#     for name, start, end in NAKSHATRAS:
#         if start <= longitude < end:
#             position_in_nakshatra = longitude - start
#             pada = math.ceil(position_in_nakshatra / 3.3333)
#             return name, pada
#     if math.isclose(longitude, 360, rel_tol=1e-5):
#         return 'Revati', 4
#     raise ValueError(f"Longitude {longitude} not in any nakshatra range")

# def lahairi_composite(person_a_data, person_b_data):
#     """Calculate composite chart with nakshatras and padas using Lahiri ayanamsa."""
#     # Person A calculations
#     jd_a = get_julian_day(person_a_data['date'], person_a_data['time'], float(person_a_data['tz_offset']))
#     lat_a = float(person_a_data['lat'])
#     lon_a = float(person_a_data['lon'])
#     pos_a = calculate_planetary_positions(jd_a)
#     asc_a, mc_a, asc_sign_idx_a = calculate_ascendant_and_houses(jd_a, lat_a, lon_a)
#     houses_a = assign_planets_to_houses(pos_a, asc_sign_idx_a)

#     # Person B calculations
#     jd_b = get_julian_day(person_b_data['date'], person_b_data['time'], float(person_b_data['tz_offset']))
#     lat_b = float(person_b_data['lat'])
#     lon_b = float(person_b_data['lon'])
#     pos_b = calculate_planetary_positions(jd_b)
#     asc_b, mc_b, asc_sign_idx_b = calculate_ascendant_and_houses(jd_b, lat_b, lon_b)
#     houses_b = assign_planets_to_houses(pos_b, asc_sign_idx_b)

#     # Composite calculations
#     positions = calculate_composite_positions(pos_a, pos_b)
#     asc_composite, mc_composite, asc_sign_idx_composite = calculate_composite_angles(
#         jd_a, jd_b, lat_a, lon_a, lat_b, lon_b
#     )
#     houses_composite = assign_planets_to_houses(positions, asc_sign_idx_composite)

#     # Add nakshatra and pada to composite planets
#     for planet in positions:
#         lon = positions[planet]['longitude']
#         nakshatra, pada = get_nakshatra_pada(lon)
#         positions[planet]['nakshatra'] = nakshatra
#         positions[planet]['pada'] = pada

#     # Calculate nakshatra and pada for composite ascendant and midheaven
#     asc_nakshatra, asc_pada = get_nakshatra_pada(asc_composite)
#     mc_nakshatra, mc_pada = get_nakshatra_pada(mc_composite)

#     # Calculate aspects including Ascendant and Midheaven
#     positions_with_angles = {
#         **positions,
#         'Ascendant': {'longitude': asc_composite, 'sign': SIGNS[asc_sign_idx_composite], 'degree': format_degrees(asc_composite % 30), 'retrograde': False},
#         'Midheaven': {'longitude': mc_composite, 'sign': SIGNS[int(mc_composite // 30)], 'degree': format_degrees(mc_composite % 30), 'retrograde': False}
#     }
#     aspects = calculate_aspects(positions_with_angles)

#     # Prepare natal data for Person A
#     natal_a = {
#         'planets': {planet: {**pos_a[planet], 'house': houses_a[planet]} for planet in pos_a},
#         'ascendant': {'longitude': asc_a, 'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30)},
#         'midheaven': {'longitude': mc_a, 'sign': SIGNS[int(mc_a // 30)], 'degree': format_degrees(mc_a % 30)},
#         'houses': {i+1: SIGNS[(asc_sign_idx_a + i) % 12] for i in range(12)}
#     }

#     # Prepare natal data for Person B
#     natal_b = {
#         'planets': {planet: {**pos_b[planet], 'house': houses_b[planet]} for planet in pos_b},
#         'ascendant': {'longitude': asc_b, 'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30)},
#         'midheaven': {'longitude': mc_b, 'sign': SIGNS[int(mc_b // 30)], 'degree': format_degrees(mc_b % 30)},
#         'houses': {i+1: SIGNS[(asc_sign_idx_b + i) % 12] for i in range(12)}
#     }

#     # Prepare composite data with nakshatras and padas
#     composite = {
#         'planets': {planet: {**positions[planet], 'house': houses_composite[planet]} for planet in positions},
#         'ascendant': {
#             'longitude': asc_composite,
#             'sign': SIGNS[asc_sign_idx_composite],
#             'degree': format_degrees(asc_composite % 30),
#             'nakshatra': asc_nakshatra,
#             'pada': asc_pada
#         },
#         'midheaven': {
#             'longitude': mc_composite,
#             'sign': SIGNS[int(mc_composite // 30)],
#             'degree': format_degrees(mc_composite % 30),
#             'nakshatra': mc_nakshatra,
#             'pada': mc_pada
#         },
#         'aspects': aspects,
#         'houses': {i+1: SIGNS[(asc_sign_idx_composite + i) % 12] for i in range(12)}
#     }

#     return {
#         'natal_a': natal_a,
#         'natal_b': natal_b,
#         'composite': composite
#     }




import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Constants
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO, 'North Node': swe.MEAN_NODE
}
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8}, 'Sextile': {'angle': 60, 'orb': 6},
    'Square': {'angle': 90, 'orb': 8}, 'Trine': {'angle': 120, 'orb': 8},
    'Opposition': {'angle': 180, 'orb': 8}
}
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio',
         'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Interpretations for Western astrology
ASCENDANT_INTERPRETATIONS = {
    'Aries': "The relationship presents itself with bold, assertive energy.",
    'Taurus': "A stable, grounded public image defines the relationship.",
    'Gemini': "The relationship appears lively and communicative.",
    'Cancer': "A nurturing, protective persona shapes the relationship's image.",
    'Leo': "The relationship radiates confidence and charisma.",
    'Virgo': "A practical, service-oriented image marks the relationship.",
    'Libra': "Grace and diplomacy define the relationship's public presence.",
    'Scorpio': "An intense, magnetic persona shapes the relationship.",
    'Sagittarius': "The relationship appears adventurous and optimistic.",
    'Capricorn': "A disciplined, ambitious image defines the relationship.",
    'Aquarius': "An innovative, independent persona marks the relationship.",
    'Pisces': "A compassionate, dreamy public image shapes the relationship."
}
MIDHEAVEN_INTERPRETATIONS = {
    'Aries': "The relationship pursues bold, leadership-driven goals.",
    'Taurus': "Stable, value-oriented ambitions define the relationship.",
    'Gemini': "Communication and versatility drive the relationship's goals.",
    'Cancer': "Nurturing, family-oriented ambitions shape the relationship.",
    'Leo': "The relationship seeks recognition through creative goals.",
    'Virgo': "Practical, service-oriented ambitions guide the relationship.",
    'Libra': "Diplomacy and partnerships shape the relationship's goals.",
    'Scorpio': "Intense, transformative ambitions drive the relationship.",
    'Sagittarius': "Exploration and wisdom define the relationship's goals.",
    'Capricorn': "Discipline and structure shape the relationship's ambitions.",
    'Aquarius': "Innovative, collective goals drive the relationship.",
    'Pisces': "Intuitive, spiritual ambitions shape the relationship."
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        if not -14 <= tz_offset <= 14:
            raise ValueError(f"Timezone offset {tz_offset} out of range (±14 hours)")
        dt_utc = dt - timedelta(hours=tz_offset)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
        logger.debug(f"Julian Day for {date_str} {time_str} (TZ {tz_offset}): {jd}")
        return jd
    except ValueError as e:
        raise ValueError(f"Invalid date/time format or timezone: {str(e)}")

def format_degrees(deg):
    """Convert decimal degrees to degrees, minutes, and seconds."""
    deg = float(deg) % 360
    degrees = int(deg)
    minutes = int((deg - degrees) * 60)
    seconds = int(((deg - degrees) * 60 - minutes) * 60)
    return f"{degrees}° {minutes}' {seconds}\""

def extract_longitude(value, context):
    """Safely extract longitude from Swiss Ephemeris output."""
    if isinstance(value, tuple):
        logger.debug(f"Nested tuple detected in {context}: {value}")
        if len(value) < 1:
            raise ValueError(f"Empty tuple in {context}")
        value = value[0]
    if not isinstance(value, (float, int)):
        raise ValueError(f"Invalid longitude type in {context}: {type(value)}")
    lon = float(value) % 360
    logger.debug(f"Extracted longitude in {context}: {lon}°")
    return lon

def calculate_planetary_positions(jd):
    """Calculate tropical planetary positions."""
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
        logger.debug(f"swe.calc_ut result for {planet_name}: {result}")
        if not isinstance(result, tuple) or len(result) < 1:
            raise ValueError(f"swe.calc_ut for {planet_name} returned invalid result: {result}")
        
        lon = extract_longitude(result[0], f"{planet_name} longitude")
        sign_idx = int(lon // 30)
        if not 0 <= sign_idx < 12:
            raise ValueError(f"Invalid sign index for {planet_name}: {sign_idx}")
        
        sign = SIGNS[sign_idx]
        degree_in_sign = lon % 30
        retrograde = result[3] < 0 if len(result) > 3 else False
        if planet_id == swe.MEAN_NODE:
            retrograde = True
        
        positions[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde
        }
    
    nn_lon = positions['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    sign_idx = int(sn_lon // 30)
    sign = SIGNS[sign_idx]
    degree_in_sign = sn_lon % 30
    positions['South Node'] = {
        'longitude': sn_lon,
        'sign': sign,
        'degree': format_degrees(degree_in_sign),
        'retrograde': True
    }
    logger.debug(f"Planetary positions: {positions}")
    return positions

def calculate_ascendant_and_houses(jd, lat, lon):
    """Calculate Ascendant, Midheaven, and Placidus house cusps."""
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude {lat} out of range (±90°)")
    if not -180 <= lon <= 180:
        raise ValueError(f"Longitude {lon} out of range (±180°)")
    if abs(lat) > 66:
        logger.warning(f"High latitude ({lat}°) may affect Placidus house accuracy")
    
    result = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SWIEPH)
    logger.debug(f"swe.houses_ex inputs: jd={jd}, lat={lat}, lon={lon}, house_system=Placidus")
    logger.debug(f"swe.houses_ex result: house_cusps={result[0]}, ascmc={result[1]}")
    
    if not isinstance(result, tuple) or len(result) < 2:
        raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    
    house_cusps, ascmc = result
    ascendant = extract_longitude(ascmc[0], "Ascendant")
    midheaven = extract_longitude(ascmc[1], "Midheaven")
    asc_sign_idx = int(ascendant // 30)
    logger.debug(f"Ascendant: {ascendant}° ({SIGNS[asc_sign_idx]}), Midheaven: {midheaven}°")
    
    return ascendant, midheaven, house_cusps, asc_sign_idx

def calculate_midpoint(lon1, lon2):
    """Calculate the midpoint longitude using the shortest arc."""
    lon1, lon2 = lon1 % 360, lon2 % 360
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
        if lon1 > lon2:
            lon1, lon2 = lon2, lon1
        mid = (lon1 + diff / 2 + 180) % 360
    else:
        mid = (lon1 + lon2) / 2
    logger.debug(f"Midpoint of {lon1}° and {lon2}°: {mid}°")
    return mid

def calculate_composite_positions(pos_a, pos_b):
    """Calculate composite planetary positions from two natal charts."""
    positions = {}
    for planet in pos_a:
        lon_a = pos_a[planet]['longitude']
        lon_b = pos_b[planet]['longitude']
        lon_mid = calculate_midpoint(lon_a, lon_b)
        sign_idx = int(lon_mid // 30)
        sign = SIGNS[sign_idx]
        degree_in_sign = lon_mid % 30
        retrograde = pos_a[planet]['retrograde'] or pos_b[planet]['retrograde']
        positions[planet] = {
            'longitude': lon_mid,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde
        }
    logger.debug(f"Composite positions: {positions}")
    return positions

def calculate_composite_angles(jd_a, jd_b, lat_a, lon_a, lat_b, lon_b, reference_date=None, reference_time=None, tz_offset=None):
    """Calculate composite Ascendant, Midheaven, and Placidus houses."""
    if reference_date and reference_time and tz_offset is not None:
        jd_mid = get_julian_day(reference_date, reference_time, tz_offset)
        lat_mid = lat_a  # Use Person A's latitude for consistency
        lon_mid = lon_a  # Use Person A's longitude
    else:
        jd_mid = (jd_a + jd_b) / 2
        lat_mid = (lat_a + lat_b) / 2
        lon_mid = (lon_a + lon_b) / 2
    if not -90 <= lat_mid <= 90:
        raise ValueError(f"Composite latitude {lat_mid} out of range (±90°)")
    if not -180 <= lon_mid <= 180:
        raise ValueError(f"Composite longitude {lon_mid} out of range (±180°)")
    result = swe.houses_ex(jd_mid, lat_mid, lon_mid, b'P', flags=swe.FLG_SWIEPH)
    logger.debug(f"Composite swe.houses_ex inputs: jd={jd_mid}, lat={lat_mid}, lon={lon_mid}, house_system=Placidus")
    logger.debug(f"Composite swe.houses_ex result: house_cusps={result[0]}, ascmc={result[1]}")
    if not isinstance(result, tuple) or len(result) < 2:
        raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    house_cusps, ascmc = result
    asc_composite = extract_longitude(ascmc[0], "Composite Ascendant")
    mc_composite = extract_longitude(ascmc[1], "Composite Midheaven")
    asc_sign_idx_composite = int(asc_composite // 30)
    return asc_composite, mc_composite, house_cusps, asc_sign_idx_composite

def assign_planets_to_houses(positions, house_cusps):
    """Assign planets to Placidus houses based on cusp longitudes."""
    houses = {}
    for planet, data in positions.items():
        lon = data['longitude'] % 360
        house = None
        for i in range(12):
            cusp1 = house_cusps[i] % 360
            cusp2 = house_cusps[(i + 1) % 12] % 360
            if cusp2 < cusp1:
                cusp2 += 360
            if cusp1 <= lon < cusp2:
                house = i + 1
                break
        if house is None:
            house = 12
        houses[planet] = house
    logger.debug(f"House assignments: {houses}")
    return houses

def calculate_aspects(positions):
    """Calculate aspects between composite planets and points."""
    aspects = []
    points = list(positions.keys())
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p1, p2 = points[i], points[j]
            lon1, lon2 = positions[p1]['longitude'], positions[p2]['longitude']
            diff = min(abs(lon1 - lon2), 360 - abs(lon1 - lon2))
            for aspect_name, data in ASPECTS.items():
                if abs(diff - data['angle']) <= data['orb']:
                    aspects.append({
                        'point_a': p1,
                        'point_b': p2,
                        'aspect': aspect_name,
                        'angle': diff,
                        'orb': abs(diff - data['angle'])
                    })
    logger.debug(f"Aspects: {aspects}")
    return aspects

def interpret_composite(positions, houses, aspects, asc_sign, mc_sign):
    """Provide Western astrology interpretations for composite chart."""
    interpretation = {
        'planets': [],
        'houses': [],
        'angles': [],
        'aspects': []
    }
    house_meanings = {
        1: "identity", 2: "finances", 3: "communication", 4: "home",
        5: "romance", 6: "work", 7: "partnerships", 8: "intimacy",
        9: "philosophy", 10: "career", 11: "friendships", 12: "spirituality"
    }
    for planet, data in positions.items():
        if planet in ['North Node', 'South Node']:
            continue
        interp = f"Composite {planet} in {data['sign']}: "
        if planet == 'Sun':
            interp += f"Defines the relationship's core purpose as {data['sign'].lower()}-oriented."
        elif planet == 'Moon':
            interp += f"Emotional tone is {data['sign'].lower()}-driven."
        elif planet == 'Venus':
            interp += f"Love and harmony expressed through {data['sign'].lower()} qualities."
        elif planet == 'Mars':
            interp += f"Drive and conflict style shaped by {data['sign'].lower()}."
        else:
            interp += f"Influences the relationship through {data['sign'].lower()} qualities."
        interpretation['planets'].append(interp)
    for planet, house in houses.items():
        interp = f"Composite {planet} in {house}th house: Influences the relationship's {house_meanings[house]}."
        interpretation['houses'].append(interp)
    interpretation['angles'].append(f"Composite Ascendant in {asc_sign}: {ASCENDANT_INTERPRETATIONS.get(asc_sign, 'Unique public image.')}")
    interpretation['angles'].append(f"Composite Midheaven in {mc_sign}: {MIDHEAVEN_INTERPRETATIONS.get(mc_sign, 'Unique shared goals.')}")
    for aspect in aspects:
        p1, p2 = aspect['point_a'], aspect['point_b']
        aspect_type = aspect['aspect']
        orb = aspect['orb']
        interp = f"Composite {p1} {aspect_type.lower()} {p2} (orb: {orb:.1f}°): "
        if aspect_type == 'Conjunction':
            interp += "Intense blending of energies."
        elif aspect_type == 'Trine':
            interp += "Smooth harmony, mutual support."
        elif aspect_type == 'Sextile':
            interp += "Supportive bond, cooperative growth."
        elif aspect_type == 'Square':
            interp += "Dynamic tension, growth through challenges."
        elif aspect_type == 'Opposition':
            interp += "Balancing act, complementary but challenging."
        interpretation['aspects'].append(interp)
    return interpretation

def validate_person_data(person_data, person_label):
    """Validate required fields for a person's birth data."""
    required = ['date', 'time', 'lat', 'lon', 'tz_offset']
    missing = [field for field in required if field not in person_data]
    if missing:
        return False, f"Missing fields for {person_label}: {', '.join(missing)}"
    try:
        datetime.strptime(f"{person_data['date']} {person_data['time']}", "%Y-%m-%d %H:%M:%S")
        lat = float(person_data['lat'])
        lon = float(person_data['lon'])
        tz_offset = float(person_data['tz_offset'])
        if not -90 <= lat <= 90:
            return False, f"Invalid latitude for {person_label}: {lat}"
        if not -180 <= lon <= 180:
            return False, f"Invalid longitude for {person_label}: {lon}"
        if not -14 <= tz_offset <= 14:
            return False, f"Invalid timezone offset for {person_label}: {tz_offset}"
    except ValueError:
        return False, f"Invalid date/time format or numeric values for {person_label}"
    return True, None

def composite(person_a, person_b, reference_date=None, reference_time=None):
    """Calculate composite chart data for two people."""
    # Validate input
    valid_a, error_a = validate_person_data(person_a, 'person_a')
    if not valid_a:
        raise ValueError(error_a)
    valid_b, error_b = validate_person_data(person_b, 'person_b')
    if not valid_b:
        raise ValueError(error_b)

    # Person A calculations
    name_a = person_a.get('name', 'Person A')
    jd_a = get_julian_day(person_a['date'], person_a['time'], float(person_a['tz_offset']))
    lat_a = float(person_a['lat'])
    lon_a = float(person_a['lon'])
    pos_a = calculate_planetary_positions(jd_a)
    asc_a, mc_a, house_cusps_a, asc_sign_idx_a = calculate_ascendant_and_houses(jd_a, lat_a, lon_a)
    houses_a = assign_planets_to_houses(pos_a, house_cusps_a)

    # Person B calculations
    name_b = person_b.get('name', 'Person B')
    jd_b = get_julian_day(person_b['date'], person_b['time'], float(person_b['tz_offset']))
    lat_b = float(person_b['lat'])
    lon_b = float(person_b['lon'])
    pos_b = calculate_planetary_positions(jd_b)
    asc_b, mc_b, house_cusps_b, asc_sign_idx_b = calculate_ascendant_and_houses(jd_b, lat_b, lon_b)
    houses_b = assign_planets_to_houses(pos_b, house_cusps_b)

    # Composite calculations
    positions = calculate_composite_positions(pos_a, pos_b)
    tz_offset = float(person_a['tz_offset']) if reference_date and reference_time else None
    asc_composite, mc_composite, house_cusps_composite, asc_sign_idx_composite = calculate_composite_angles(
        jd_a, jd_b, lat_a, lon_a, lat_b, lon_b, reference_date, reference_time, tz_offset
    )
    houses_composite = assign_planets_to_houses(positions, house_cusps_composite)

    # Calculate aspects including Ascendant and Midheaven
    positions_with_angles = {
        **positions,
        'Ascendant': {'longitude': asc_composite, 'sign': SIGNS[asc_sign_idx_composite], 'degree': format_degrees(asc_composite % 30), 'retrograde': False},
        'Midheaven': {'longitude': mc_composite, 'sign': SIGNS[int(mc_composite // 30)], 'degree': format_degrees(mc_composite % 30), 'retrograde': False}
    }
    aspects = calculate_aspects(positions_with_angles)
    interpretation = interpret_composite(positions, houses_composite, aspects, SIGNS[asc_sign_idx_composite], SIGNS[int(mc_composite // 30)])

    # Prepare natal data for Person A
    natal_a = {
        'planets': {planet: {**pos_a[planet], 'house': houses_a[planet]} for planet in pos_a},
        'ascendant': {'longitude': asc_a, 'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30)},
        'midheaven': {'longitude': mc_a, 'sign': SIGNS[int(mc_a // 30)], 'degree': format_degrees(mc_a % 30)},
        'houses': {i+1: format_degrees(house_cusps_a[i] % 360) for i in range(12)}
    }

    # Prepare natal data for Person B
    natal_b = {
        'planets': {planet: {**pos_b[planet], 'house': houses_b[planet]} for planet in pos_b},
        'ascendant': {'longitude': asc_b, 'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30)},
        'midheaven': {'longitude': mc_b, 'sign': SIGNS[int(mc_b // 30)], 'degree': format_degrees(mc_b % 30)},
        'houses': {i+1: format_degrees(house_cusps_b[i] % 360) for i in range(12)}
    }

    # Prepare composite data
    composite = {
        'planets': {planet: {**positions[planet], 'house': houses_composite[planet]} for planet in positions},
        'ascendant': {'longitude': asc_composite, 'sign': SIGNS[asc_sign_idx_composite], 'degree': format_degrees(asc_composite % 30)},
        'midheaven': {'longitude': mc_composite, 'sign': SIGNS[int(mc_composite // 30)], 'degree': format_degrees(mc_composite % 30)},
        'aspects': aspects,
        'houses': {i+1: format_degrees(house_cusps_composite[i] % 360) for i in range(12)},
        'interpretation': interpretation
    }

    # Construct response
    return {
        'person_a': {
            'name': name_a,
            'natal': natal_a
        },
        'person_b': {
            'name': name_b,
            'natal': natal_b
        },
        'composite': composite
    }


