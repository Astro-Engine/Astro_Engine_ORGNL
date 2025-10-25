

# import swisseph as swe
# from datetime import datetime, timedelta
# import math
# import logging

# # Set Swiss Ephemeris path (update to your ephemeris files' location)
# swe.set_ephe_path('astro_engine/ephe')

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

# # Nakshatra list with start and end degrees
# NAKSHATRAS = [
#     ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
#     ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
#     ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
#     ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
#     ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
#     ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
#     ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
#     ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
#     ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
# ]

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date, time, and timezone offset to Julian Day."""
#     dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     dt_utc = dt - timedelta(hours=tz_offset)
#     jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
#                     dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
#     logging.debug(f"Calculated Julian Day: {jd}")
#     return jd

# def format_degrees(deg):
#     """Convert decimal degrees to degrees, minutes, and seconds."""
#     if not isinstance(deg, (float, int)):
#         raise ValueError(f"Degree value must be a number, got {type(deg)}: {deg}")
#     degrees = int(deg)
#     minutes = int((deg - degrees) * 60)
#     seconds = int(((deg - degrees) * 60 - minutes) * 60)
#     return f"{degrees}° {minutes}' {seconds}\""

# def get_nakshatra_and_pada(longitude):
#     """Determine the nakshatra and pada for a given longitude."""
#     longitude = longitude % 360
#     for nakshatra, start, end in NAKSHATRAS:
#         if start <= longitude < end:
#             position_in_nakshatra = longitude - start
#             pada = math.ceil(position_in_nakshatra / 3.3333)
#             return nakshatra, pada
#     return 'Revati', 4  # Fallback for edge cases

# def calculate_planetary_positions(jd):
#     """Calculate sidereal planetary positions, nakshatra, and pada using Lahiri ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     positions = {}
#     for planet_name, planet_id in PLANETS.items():
#         result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
#         logging.debug(f"swe.calc_ut result for {planet_name}: {result}")
        
#         if not isinstance(result, tuple) or len(result) < 1:
#             raise ValueError(f"swe.calc_ut for {planet_name} returned invalid data: {result}")
        
#         lon = float(result[0] if not isinstance(result[0], tuple) else result[0][0])
#         sign_idx = int(lon // 30)
#         if not (0 <= sign_idx < 12):
#             raise ValueError(f"Invalid sign index for {planet_name}: {sign_idx}")
        
#         sign = SIGNS[sign_idx]
#         degree_in_sign = lon % 30
#         retrograde = result[3] < 0 if len(result) > 3 else False
#         if planet_id == swe.MEAN_NODE:
#             retrograde = True
        
#         nakshatra, pada = get_nakshatra_and_pada(lon)
        
#         positions[planet_name] = {
#             'longitude': lon,
#             'sign': sign,
#             'degree': format_degrees(degree_in_sign),
#             'retrograde': retrograde,
#             'nakshatra': nakshatra,
#             'pada': pada
#         }
    
#     nn_lon = positions['North Node']['longitude']
#     sn_lon = (nn_lon + 180) % 360
#     sign_idx = int(sn_lon // 30)
#     sign = SIGNS[sign_idx]
#     degree_in_sign = sn_lon % 30
#     nakshatra, pada = get_nakshatra_and_pada(sn_lon)
#     positions['South Node'] = {
#         'longitude': sn_lon,
#         'sign': sign,
#         'degree': format_degrees(degree_in_sign),
#         'retrograde': True,
#         'nakshatra': nakshatra,
#         'pada': pada
#     }
#     return positions

# def calculate_ascendant_and_houses(jd, lat, lon):
#     """Calculate Ascendant and Whole Sign house cusps."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     result = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
#     logging.debug(f"swe.houses_ex result: {result}")
    
#     if not isinstance(result, tuple) or len(result) < 2:
#         raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    
#     house_cusps, ascmc = result
#     ascendant = float(ascmc[0]) % 360
#     asc_sign_idx = int(ascendant // 30)
#     return ascendant, asc_sign_idx

# def assign_planets_to_houses(positions, asc_sign_idx):
#     """Assign planets to houses using Whole Sign system."""
#     houses = {}
#     for planet, data in positions.items():
#         longitude = data['longitude']
#         planet_sign_idx = int(longitude // 30)
#         house = (planet_sign_idx - asc_sign_idx) % 12 + 1
#         houses[planet] = house
#     return houses

# def calculate_aspects(pos_a, pos_b):
#     """Calculate aspects between two sets of planetary positions."""
#     aspects = []
#     for planet_a, data_a in pos_a.items():
#         for planet_b, data_b in pos_b.items():
#             diff = abs(data_a['longitude'] - data_b['longitude'])
#             diff = min(diff, 360 - diff)
#             for aspect_name, aspect_data in ASPECTS.items():
#                 if abs(diff - aspect_data['angle']) <= aspect_data['orb']:
#                     aspects.append({
#                         'planet_a': planet_a,
#                         'planet_b': planet_b,
#                         'aspect': aspect_name,
#                         'angle': diff,
#                         'orb': abs(diff - aspect_data['angle'])
#                     })
#     return aspects

# def analyze_house_overlays(pos_planets, asc_sign_idx):
#     """Map one person's planets to the other's houses."""
#     overlays = {}
#     for planet, data in pos_planets.items():
#         planet_sign_idx = int(data['longitude'] // 30)
#         house = (planet_sign_idx - asc_sign_idx) % 12 + 1
#         overlays[planet] = house
#     return overlays

# def evaluate_nodal_connections(pos_planets, pos_nodes):
#     """Evaluate connections with North and South Nodes."""
#     connections = []
#     node_lons = {
#         'North Node': pos_nodes['North Node']['longitude'],
#         'South Node': pos_nodes['South Node']['longitude']
#     }
#     for planet, data in pos_planets.items():
#         for node, node_lon in node_lons.items():
#             diff = abs(data['longitude'] - node_lon)
#             angle = min(diff, 360 - diff)
#             if angle <= 5:
#                 connections.append({'planet': planet, 'node': node, 'angle': angle})
#     return connections

# def interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b):
#     """Provide detailed interpretations of synastry factors."""
#     interpretation = {
#         'aspects': [],
#         'house_overlays': {'a_in_b': [], 'b_in_a': []},
#         'nodal_connections': {'person_a': [], 'person_b': []}
#     }
#     for aspect in aspects:
#         planet_a, planet_b = aspect['planet_a'], aspect['planet_b']
#         aspect_type = aspect['aspect']
#         if aspect_type == 'Conjunction':
#             interp = f"Person A's {planet_a} conjunct Person B's {planet_b}: A powerful blend of energies."
#         elif aspect_type == 'Trine':
#             interp = f"Person A's {planet_a} trine Person B's {planet_b}: Harmonious flow."
#         elif aspect_type == 'Sextile':
#             interp = f"Person A's {planet_a} sextile Person B's {planet_b}: Opportunities for growth."
#         elif aspect_type == 'Square':
#             interp = f"Person A's {planet_a} square Person B's {planet_b}: Tension and challenges."
#         elif aspect_type == 'Opposition':
#             interp = f"Person A's {planet_a} opposite Person B's {planet_b}: Polarizing dynamics."
#         interpretation['aspects'].append(interp)
#     house_meanings = {
#         1: "identity", 2: "resources", 3: "communication", 4: "home", 5: "creativity",
#         6: "service", 7: "relationships", 8: "transformation", 9: "exploration",
#         10: "career", 11: "friendships", 12: "subconscious"
#     }
#     for planet, house in overlays_a_in_b.items():
#         interp = f"Person A's {planet} in Person B's {house} house: Influences {house_meanings[house]}."
#         interpretation['house_overlays']['a_in_b'].append(interp)
#     for planet, house in overlays_b_in_a.items():
#         interp = f"Person B's {planet} in Person A's {house} house: Influences {house_meanings[house]}."
#         interpretation['house_overlays']['b_in_a'].append(interp)
#     for conn in nodal_a:
#         interp = f"Person A's {conn['planet']} conjunct Person B's {conn['node']}: Karmic tie."
#         interpretation['nodal_connections']['person_a'].append(interp)
#     for conn in nodal_b:
#         interp = f"Person B's {conn['planet']} conjunct Person A's {conn['node']}: Karmic bond."
#         interpretation['nodal_connections']['person_b'].append(interp)
#     return interpretation

# def validate_person_data(person_data, person_label):
#     """Validate required fields for a person's birth data."""
#     required_fields = ['date', 'time', 'lat', 'lon', 'tz_offset']
#     missing_fields = [field for field in required_fields if field not in person_data]
#     if missing_fields:
#         return False, f"Missing fields for {person_label}: {', '.join(missing_fields)}"
#     return True, None

# def lahairi_synastry(person_data):
#     """Calculate chart data for one person using Lahiri ayanamsa, including nakshatra and pada."""
#     name = person_data.get('name', 'Person')
#     jd = get_julian_day(person_data['date'], person_data['time'], person_data['tz_offset'])
#     positions = calculate_planetary_positions(jd)
#     ascendant, asc_sign_idx = calculate_ascendant_and_houses(jd, person_data['lat'], person_data['lon'])
#     houses = assign_planets_to_houses(positions, asc_sign_idx)
    
#     asc_nakshatra, asc_pada = get_nakshatra_and_pada(ascendant)
#     ascendant_details = {
#         'longitude': ascendant,
#         'sign': SIGNS[asc_sign_idx],
#         'degree': format_degrees(ascendant % 30),
#         'retrograde': False,
#         'nakshatra': asc_nakshatra,
#         'pada': asc_pada
#     }
#     return {
#         'name': name,
#         'positions': positions,
#         'ascendant': ascendant_details,
#         'houses': houses,
#         'asc_sign_idx': asc_sign_idx
#     }





import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Set up logging
logger = logging.getLogger(__name__)

swe.set_ephe_path('astro_engine/ephe')

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
    logger.debug(f"swe.houses_ex result: {result}")
    
    if not isinstance(result, tuple) or len(result) < 2:
        raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    
    house_cusps, ascmc = result
    ascendant = extract_longitude(ascmc[0], "Ascendant")
    midheaven = extract_longitude(ascmc[1], "Midheaven")
    asc_sign_idx = int(ascendant // 30)
    logger.debug(f"Ascendant: {ascendant}° ({SIGNS[asc_sign_idx]}), Midheaven: {midheaven}°")
    
    return ascendant, midheaven, house_cusps, asc_sign_idx

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

def calculate_aspects(pos_a, pos_b):
    """Calculate aspects between two sets of planetary positions."""
    aspects = []
    for planet_a, data_a in pos_a.items():
        for planet_b, data_b in pos_b.items():
            diff = abs(data_a['longitude'] - data_b['longitude'])
            diff = min(diff, 360 - diff)
            for aspect_name, aspect_data in ASPECTS.items():
                if abs(diff - aspect_data['angle']) <= aspect_data['orb']:
                    aspects.append({
                        'planet_a': planet_a,
                        'planet_b': planet_b,
                        'aspect': aspect_name,
                        'angle': diff,
                        'orb': abs(diff - aspect_data['angle'])
                    })
    logger.debug(f"Aspects: {aspects}")
    return aspects

def analyze_house_overlays(pos_planets, house_cusps):
    """Map one person's planets to the other's Placidus house cusps."""
    overlays = {}
    for planet, data in pos_planets.items():
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
        overlays[planet] = house
    logger.debug(f"House overlays: {overlays}")
    return overlays

def evaluate_nodal_connections(pos_planets, pos_nodes):
    """Evaluate connections with North and South Nodes."""
    connections = []
    node_lons = {
        'North Node': pos_nodes['North Node']['longitude'],
        'South Node': pos_nodes['South Node']['longitude']
    }
    for planet, data in pos_planets.items():
        for node, node_lon in node_lons.items():
            diff = abs(data['longitude'] - node_lon)
            angle = min(diff, 360 - diff)
            if angle <= 5:
                connections.append({'planet': planet, 'node': node, 'angle': angle})
    logger.debug(f"Nodal connections: {connections}")
    return connections

def interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b):
    """Provide Western astrology interpretations for synastry."""
    interpretation = {
        'aspects': [],
        'house_overlays': {'a_in_b': [], 'b_in_a': []},
        'nodal_connections': {'person_a': [], 'person_b': []}
    }
    house_meanings = {
        1: "identity", 2: "finances", 3: "communication", 4: "home",
        5: "romance", 6: "work", 7: "partnerships", 8: "intimacy",
        9: "philosophy", 10: "career", 11: "friendships", 12: "spirituality"
    }
    for aspect in aspects:
        planet_a, planet_b = aspect['planet_a'], aspect['planet_b']
        aspect_type = aspect['aspect']
        orb = aspect['orb']
        interp = f"A's {planet_a} {aspect_type.lower()} B's {planet_b} (orb: {orb:.1f}°): "
        if aspect_type == 'Conjunction':
            interp += "Intense connection, blending energies."
        elif aspect_type == 'Trine':
            interp += "Smooth harmony, mutual support."
        elif aspect_type == 'Sextile':
            interp += "Supportive bond, cooperative growth."
        elif aspect_type == 'Square':
            interp += "Dynamic tension, growth through challenges."
        elif aspect_type == 'Opposition':
            interp += "Balancing act, complementary but challenging."
        interpretation['aspects'].append(interp)
    for planet, house in overlays_a_in_b.items():
        interp = f"A's {planet} in B's {house}th house: Influences B's {house_meanings[house]}."
        interpretation['house_overlays']['a_in_b'].append(interp)
    for planet, house in overlays_b_in_a.items():
        interp = f"B's {planet} in A's {house}th house: Influences A's {house_meanings[house]}."
        interpretation['house_overlays']['b_in_a'].append(interp)
    for conn in nodal_a:
        interp = f"A's {conn['planet']} conjunct B's {conn['node']} (angle: {conn['angle']:.1f}°): Growth-oriented bond."
        interpretation['nodal_connections']['person_a'].append(interp)
    for conn in nodal_b:
        interp = f"B's {conn['planet']} conjunct A's {conn['node']} (angle: {conn['angle']:.1f}°): Developmental tie."
        interpretation['nodal_connections']['person_b'].append(interp)
    return interpretation

def validate_person_data(person_data, person_label):
    """Validate required fields for a person's birth data."""
    required_fields = ['date', 'time', 'lat', 'lon', 'tz_offset']
    missing_fields = [field for field in required_fields if field not in person_data]
    if missing_fields:
        return False, f"Missing fields for {person_label}: {', '.join(missing_fields)}"
    try:
        datetime.strptime(f"{person_data['date']} {person_data['time']}", "%Y-%m-%d %H:%M:%S")
        if not -90 <= person_data['lat'] <= 90:
            return False, f"Invalid latitude for {person_label}: {person_data['lat']}"
        if not -180 <= person_data['lon'] <= 180:
            return False, f"Invalid longitude for {person_label}: {person_data['lon']}"
        if not -14 <= person_data['tz_offset'] <= 14:
            return False, f"Invalid timezone offset for {person_label}: {person_data['tz_offset']}"
    except ValueError:
        return False, f"Invalid date/time format for {person_label}"
    return True, None

def synastry(person_a, person_b):
    """Calculate synastry chart data for two people."""
    # Validate input
    valid_a, error_a = validate_person_data(person_a, 'person_a')
    if not valid_a:
        raise ValueError(error_a)
    valid_b, error_b = validate_person_data(person_b, 'person_b')
    if not valid_b:
        raise ValueError(error_b)

    # Person A calculations
    name_a = person_a.get('name', 'Person A')
    jd_a = get_julian_day(person_a['date'], person_a['time'], person_a['tz_offset'])
    pos_a = calculate_planetary_positions(jd_a)
    asc_a, mc_a, house_cusps_a, asc_sign_idx_a = calculate_ascendant_and_houses(
        jd_a, person_a['lat'], person_a['lon'])
    houses_a = assign_planets_to_houses(pos_a, house_cusps_a)

    # Person B calculations
    name_b = person_b.get('name', 'Person B')
    jd_b = get_julian_day(person_b['date'], person_b['time'], person_b['tz_offset'])
    pos_b = calculate_planetary_positions(jd_b)
    asc_b, mc_b, house_cusps_b, asc_sign_idx_b = calculate_ascendant_and_houses(
        jd_b, person_b['lat'], person_b['lon'])
    houses_b = assign_planets_to_houses(pos_b, house_cusps_b)

    # Include Ascendant for aspects
    pos_a_with_asc = {**pos_a, 'Ascendant': {
        'longitude': asc_a, 'sign': SIGNS[asc_sign_idx_a], 
        'degree': format_degrees(asc_a % 30), 'retrograde': False}}
    pos_b_with_asc = {**pos_b, 'Ascendant': {
        'longitude': asc_b, 'sign': SIGNS[asc_sign_idx_b], 
        'degree': format_degrees(asc_b % 30), 'retrograde': False}}

    # Synastry analysis
    aspects = calculate_aspects(pos_a_with_asc, pos_b_with_asc)
    overlays_a_in_b = analyze_house_overlays(pos_a, house_cusps_b)
    overlays_b_in_a = analyze_house_overlays(pos_b, house_cusps_a)
    nodal_a = evaluate_nodal_connections(pos_a, pos_b)
    nodal_b = evaluate_nodal_connections(pos_b, pos_a)
    interpretation = interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b)

    # Response
    response = {
        'person_a': {
            'name': name_a,
            'birth_details': person_a,
            'ascendant': {'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30)},
            'midheaven': {'sign': SIGNS[int(mc_a // 30)], 'degree': format_degrees(mc_a % 30)},
            'planets': {k: {**v, 'house': houses_a[k]} for k, v in pos_a.items()}
        },
        'person_b': {
            'name': name_b,
            'birth_details': person_b,
            'ascendant': {'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30)},
            'midheaven': {'sign': SIGNS[int(mc_b // 30)], 'degree': format_degrees(mc_b % 30)},
            'planets': {k: {**v, 'house': houses_b[k]} for k, v in pos_b.items()}
        },
        'synastry': {
            'house_system': 'Placidus',
            'aspects': aspects,
            'house_overlays': {'a_in_b': overlays_a_in_b, 'b_in_a': overlays_b_in_a},
            'nodal_connections': {'person_a': nodal_a, 'person_b': nodal_b},
            # 'interpretation': interpretation
        }
    }
    return response



