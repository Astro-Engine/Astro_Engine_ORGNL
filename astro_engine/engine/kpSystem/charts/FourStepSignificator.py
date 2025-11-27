"""
KP 4 Step Significators - Calculation Module v6.0.0
===================================================
Krishnamurti Paddhati (KP) Astrology - 4 Step Significators Calculation

Complete 249-division KP sub-lord system using Mean Node
"""

import swisseph as swe
from datetime import datetime

# ==============================================================================
# CONSTANTS
# ==============================================================================

# KP Constants
NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu',
    'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati'
]

SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# CRITICAL FIX: Using MEAN_NODE instead of TRUE_NODE for Rahu/Ketu
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,      # Changed from TRUE_NODE to MEAN_NODE
    'Ketu': swe.MEAN_NODE       # Changed from TRUE_NODE to MEAN_NODE
}

# Vimshottari Dasha periods (in years)
VIMSHOTTARI_YEARS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17
}

VIMSHOTTARI_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
TOTAL_VIMSHOTTARI_YEARS = 120

# Global variable for sub-lord table
KP_SUBLORD_TABLE = None


# ==============================================================================
# SUB-LORD TABLE BUILDING
# ==============================================================================

def build_kp_sublord_table():
    """
    Build the complete 249-division KP sub-lord table
    
    Creates exact degree boundaries for all sub-lords across all 27 nakshatras
    based on Vimshottari Dasha proportions.
    """
    sublord_table = []
    nakshatra_length = 360.0 / 27.0  # 13.333333° per nakshatra
    
    for nak_num in range(1, 28):
        nak_name = NAKSHATRA_NAMES[nak_num - 1]
        nak_lord = NAKSHATRA_LORDS[nak_num - 1]
        nak_start = (nak_num - 1) * nakshatra_length
        
        # Build sub-lord sequence starting from nakshatra lord
        start_index = VIMSHOTTARI_SEQUENCE.index(nak_lord)
        sub_lord_sequence = VIMSHOTTARI_SEQUENCE[start_index:] + VIMSHOTTARI_SEQUENCE[:start_index]
        
        # Calculate sub-lord boundaries
        current_degree = nak_start
        
        for sub_lord in sub_lord_sequence:
            sub_lord_years = VIMSHOTTARI_YEARS[sub_lord]
            sub_lord_span = (sub_lord_years / TOTAL_VIMSHOTTARI_YEARS) * nakshatra_length
            
            sublord_table.append({
                'start_degree': current_degree,
                'end_degree': current_degree + sub_lord_span,
                'nakshatra_num': nak_num,
                'nakshatra_name': nak_name,
                'nakshatra_lord': nak_lord,
                'sub_lord': sub_lord
            })
            
            current_degree += sub_lord_span
    
    return sublord_table


def get_sub_lord_from_table(longitude):
    """
    Get sub-lord using the complete 249-division lookup table
    """
    global KP_SUBLORD_TABLE
    
    if KP_SUBLORD_TABLE is None:
        KP_SUBLORD_TABLE = build_kp_sublord_table()
    
    longitude = normalize_degrees(longitude)
    
    for entry in KP_SUBLORD_TABLE:
        if entry['start_degree'] <= longitude < entry['end_degree']:
            return entry['sub_lord']
    
    # Fallback for edge case at 360°
    return KP_SUBLORD_TABLE[-1]['sub_lord']


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def normalize_degrees(deg):
    """Normalize degrees to 0-360 range"""
    while deg < 0:
        deg += 360
    while deg >= 360:
        deg -= 360
    return deg


def get_julian_day(date_str, time_str, timezone_offset):
    """Convert date and time to Julian Day in UTC"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        utc_hour = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0) - timezone_offset
        jd = swe.julday(dt.year, dt.month, dt.day, utc_hour)
        return jd
    except Exception as e:
        raise ValueError(f"Invalid date/time format: {str(e)}")


def get_nakshatra_info(longitude):
    """Get nakshatra information including sub-lord"""
    nakshatra_length = 360.0 / 27.0
    nak_num = int(longitude / nakshatra_length) + 1
    
    if nak_num > 27:
        nak_num = 27
    if nak_num < 1:
        nak_num = 1
    
    pada_length = nakshatra_length / 4.0
    position_in_nak = longitude % nakshatra_length
    pada = int(position_in_nak / pada_length) + 1
    if pada > 4:
        pada = 4
    
    nak_name = NAKSHATRA_NAMES[nak_num - 1]
    nak_lord = NAKSHATRA_LORDS[nak_num - 1]
    nak_start = (nak_num - 1) * nakshatra_length
    degrees_in_nak = longitude - nak_start
    
    # Get sub-lord using lookup table
    sub_lord = get_sub_lord_from_table(longitude)
    
    return {
        'nakshatra_number': nak_num,
        'nakshatra_name': nak_name,
        'nakshatra_lord': nak_lord,
        'pada': pada,
        'degrees_in_nakshatra': round(degrees_in_nak, 6),
        'sub_lord': sub_lord
    }


def get_sign_info(longitude):
    """Get sign information for a given longitude"""
    sign_num = int(longitude / 30.0)
    if sign_num >= 12:
        sign_num = 11
    if sign_num < 0:
        sign_num = 0
    
    sign_name = SIGN_NAMES[sign_num]
    degrees_in_sign = longitude - (sign_num * 30.0)
    
    return {
        'sign_number': sign_num + 1,
        'sign_name': sign_name,
        'degrees_in_sign': round(degrees_in_sign, 6),
        'sign_lord': SIGN_LORDS[sign_name]
    }


# ==============================================================================
# CORE CALCULATION FUNCTIONS
# ==============================================================================

def calculate_planets(jd):
    """
    Calculate planet positions in sidereal zodiac with KP New ayanamsa
    
    CRITICAL: Using MEAN_NODE for Rahu/Ketu for accurate sub-lord calculations
    """
    planets_data = {}
    
    # Set sidereal mode with Krishnamurti ayanamsa
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    
    for planet_name, planet_id in PLANETS.items():
        try:
            if planet_name == 'Ketu':
                # Ketu is always 180° opposite to Rahu
                rahu_data = planets_data.get('Rahu')
                if rahu_data:
                    ketu_long = normalize_degrees(rahu_data['longitude'] + 180.0)
                    planets_data['Ketu'] = {
                        'longitude': round(ketu_long, 6),
                        'latitude': round(-rahu_data['latitude'], 6),
                        'speed': round(-rahu_data['speed'], 6),
                        'is_retrograde': rahu_data['is_retrograde'],
                        **get_sign_info(ketu_long),
                        **get_nakshatra_info(ketu_long)
                    }
                continue
            
            # Calculate sidereal position
            calc_result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
            positions = calc_result[0]
            
            longitude_sid = normalize_degrees(positions[0])
            latitude_sid = positions[1]
            speed = positions[3]
            is_retrograde = speed < 0
            
            planets_data[planet_name] = {
                'longitude': round(longitude_sid, 6),
                'latitude': round(latitude_sid, 6),
                'speed': round(speed, 6),
                'is_retrograde': is_retrograde,
                **get_sign_info(longitude_sid),
                **get_nakshatra_info(longitude_sid)
            }
            
        except Exception as e:
            raise Exception(f"Error calculating {planet_name}: {str(e)}")
    
    return planets_data


def calculate_houses(jd, latitude, longitude):
    """Calculate house cusps using Placidus system in sidereal zodiac"""
    try:
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        
        houses_result = swe.houses(jd, latitude, longitude, b'P')
        cusps_tropical = houses_result[0]
        
        cusps_length = len(cusps_tropical)
        house_cusps = []
        
        if cusps_length == 13:
            for i in range(1, 13):
                cusp_tropical = float(cusps_tropical[i])
                cusp_sidereal = normalize_degrees(cusp_tropical - ayanamsa)
                house_cusps.append(round(cusp_sidereal, 6))
        elif cusps_length == 12:
            for i in range(12):
                cusp_tropical = float(cusps_tropical[i])
                cusp_sidereal = normalize_degrees(cusp_tropical - ayanamsa)
                house_cusps.append(round(cusp_sidereal, 6))
        else:
            raise Exception(f"Unexpected cusps length: {cusps_length}")
        
        ascendant_sidereal = house_cusps[0]
        mc_sidereal = house_cusps[9]
        
        signs_on_cusps = []
        for cusp in house_cusps:
            sign_info = get_sign_info(cusp)
            signs_on_cusps.append(sign_info['sign_name'])
        
        return house_cusps, signs_on_cusps, ascendant_sidereal, mc_sidereal
        
    except Exception as e:
        raise Exception(f"Error calculating houses: {str(e)}")


def is_planet_in_house(planet_longitude, house_start, house_end):
    """Check if a planet is within a house boundary"""
    planet_longitude = normalize_degrees(planet_longitude)
    house_start = normalize_degrees(house_start)
    house_end = normalize_degrees(house_end)
    
    if house_start < house_end:
        return house_start <= planet_longitude < house_end
    else:
        return planet_longitude >= house_start or planet_longitude < house_end


def get_planets_in_house(house_num, planets_data, house_cusps):
    """Find which planets are positioned in a given house"""
    planets_in_house = []
    
    house_start = house_cusps[house_num - 1]
    if house_num == 12:
        house_end = house_cusps[0]
    else:
        house_end = house_cusps[house_num]
    
    for planet_name, planet_info in planets_data.items():
        planet_long = planet_info['longitude']
        if is_planet_in_house(planet_long, house_start, house_end):
            planets_in_house.append(planet_name)
    
    return planets_in_house


def get_planets_in_star_of(star_lord_name, planets_data):
    """Find all planets whose nakshatra lord matches the given star lord"""
    planets_in_star = []
    
    for planet_name, planet_info in planets_data.items():
        if planet_info['nakshatra_lord'] == star_lord_name:
            planets_in_star.append(planet_name)
    
    return planets_in_star


def get_planet_significator_houses(planet_name, planets_data, house_cusps, signs_on_cusps):
    """Get all houses for which a planet is a significator"""
    significator_houses = set()
    
    for house_num in range(1, 13):
        house_start = house_cusps[house_num - 1]
        
        if house_num == 12:
            house_end = house_cusps[0]
        else:
            house_end = house_cusps[house_num]
        
        planet_long = planets_data[planet_name]['longitude']
        
        # Level 2: Check if planet occupies this house
        if is_planet_in_house(planet_long, house_start, house_end):
            significator_houses.add(house_num)
            continue
        
        # Level 1: Check if planet is in star of occupants
        occupants = get_planets_in_house(house_num, planets_data, house_cusps)
        for occupant in occupants:
            if planets_data[planet_name]['nakshatra_lord'] == planets_data[occupant]['nakshatra_lord']:
                significator_houses.add(house_num)
                break
        
        # Level 3: Check if planet is in star of house lord
        house_lord = SIGN_LORDS[signs_on_cusps[house_num - 1]]
        house_lord_star = planets_data[house_lord]['nakshatra_lord']
        
        if planets_data[planet_name]['nakshatra_lord'] == house_lord_star:
            significator_houses.add(house_num)
    
    return sorted(list(significator_houses))


def format_house_list(house_numbers):
    """Format house numbers as string like '1 7' or '4 5 10'"""
    if not house_numbers:
        return ''
    return ' '.join(map(str, house_numbers))


# ==============================================================================
# SIGNIFICATOR CALCULATIONS
# ==============================================================================

def calculate_four_step_significators(planets_data, house_cusps, signs_on_cusps):
    """
    Calculate 4 Step Significators for each planet (PDF format)
    
    1. Planet : house_numbers
    2. Star Lord : house_numbers
    3. Sub Lord : house_numbers
    4. Star Lord of Sub Lord : house_numbers
    """
    four_step_significators = {}
    
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    for planet_name in planet_order:
        planet_info = planets_data[planet_name]
        
        # Step 1: Planet
        planet_houses = get_planet_significator_houses(planet_name, planets_data, house_cusps, signs_on_cusps)
        
        # Step 2: Star Lord
        star_lord = planet_info['nakshatra_lord']
        star_lord_houses = get_planet_significator_houses(star_lord, planets_data, house_cusps, signs_on_cusps)
        
        # Step 3: Sub Lord
        sub_lord = planet_info['sub_lord']
        sub_lord_houses = get_planet_significator_houses(sub_lord, planets_data, house_cusps, signs_on_cusps)
        
        # Step 4: Star Lord of Sub Lord
        sub_lord_star_lord = planets_data[sub_lord]['nakshatra_lord']
        sub_lord_star_houses = get_planet_significator_houses(sub_lord_star_lord, planets_data, house_cusps, signs_on_cusps)
        
        four_step_significators[planet_name] = {
            '1_planet': planet_name,
            '1_planet_houses': format_house_list(planet_houses),
            '2_star_lord': star_lord,
            '2_star_lord_houses': format_house_list(star_lord_houses),
            '3_sub_lord': sub_lord,
            '3_sub_lord_houses': format_house_list(sub_lord_houses),
            '4_star_lord_of_sub_lord': sub_lord_star_lord,
            '4_star_lord_of_sub_lord_houses': format_house_list(sub_lord_star_houses)
        }
    
    return four_step_significators


def calculate_four_significators(house_num, planets_data, house_cusps, signs_on_cusps):
    """Calculate the Four Significators for a given house"""
    house_lord = SIGN_LORDS[signs_on_cusps[house_num - 1]]
    
    significators = {
        'house_number': house_num,
        'house_cusp_degree': house_cusps[house_num - 1],
        'sign_on_cusp': signs_on_cusps[house_num - 1],
        'house_lord': house_lord,
        'level_1_planets_in_star_of_occupants': [],
        'level_2_planets_occupying_house': [],
        'level_3_planets_in_star_of_house_lord': [],
        'level_4_house_lord': [house_lord]
    }
    
    occupants = get_planets_in_house(house_num, planets_data, house_cusps)
    significators['level_2_planets_occupying_house'] = occupants
    
    level_1_set = set()
    for occupant in occupants:
        occupant_star_lord = planets_data[occupant]['nakshatra_lord']
        planets_in_this_star = get_planets_in_star_of(occupant_star_lord, planets_data)
        for planet in planets_in_this_star:
            level_1_set.add(planet)
    
    significators['level_1_planets_in_star_of_occupants'] = sorted(list(level_1_set))
    
    house_lord_star_lord = planets_data[house_lord]['nakshatra_lord']
    level_3_planets = get_planets_in_star_of(house_lord_star_lord, planets_data)
    significators['level_3_planets_in_star_of_house_lord'] = level_3_planets
    
    return significators


def calculate_all_house_significators(planets_data, house_cusps, signs_on_cusps):
    """Calculate Four Significators for all 12 houses"""
    all_significators = []
    
    for house_num in range(1, 13):
        house_sig = calculate_four_significators(
            house_num, planets_data, house_cusps, signs_on_cusps
        )
        all_significators.append(house_sig)
    
    return all_significators


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_kp_four_step_significators(data):
    """
    Main function to calculate KP 4 Step Significators
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str (optional)
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float
    
    Returns:
    --------
    dict: Complete KP 4 Step Significators analysis
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
    except ValueError:
        raise ValueError('latitude, longitude, and timezone_offset must be numeric')
    
    if not (-90 <= latitude <= 90):
        raise ValueError('Latitude must be between -90 and 90')
    
    if not (-180 <= longitude <= 180):
        raise ValueError('Longitude must be between -180 and 180')
    
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    
    # Calculate planets with MEAN NODE
    planets_data = calculate_planets(jd)
    
    # Calculate houses
    house_cusps, signs_on_cusps, ascendant, mc = calculate_houses(jd, latitude, longitude)
    
    # Calculate 4 Step Significators
    four_step_significators = calculate_four_step_significators(planets_data, house_cusps, signs_on_cusps)
    
    # Calculate House Significators
    house_significators = calculate_all_house_significators(planets_data, house_cusps, signs_on_cusps)
    
    # Prepare response
    response = {
        'success': True,
        'user_name': user_name,
        'birth_details': {
            'date': birth_date,
            'time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset,
            'julian_day': round(jd, 6)
        },
        'calculation_settings': {
            'ayanamsa': 'KP New (Krishnamurti)',
            'house_system': 'Placidus',
            'zodiac': 'Sidereal',
            'node_type': 'Mean Node',
            'sub_lord_system': 'KP Standard (249 divisions)'
        },
        'chart_points': {
            'ascendant': round(ascendant, 6),
            'ascendant_sign': get_sign_info(ascendant)['sign_name'],
            'mc': round(mc, 6),
            'mc_sign': get_sign_info(mc)['sign_name']
        },
        'planets': planets_data,
        'houses': {
            'house_cusps': house_cusps,
            'signs_on_cusps': signs_on_cusps
        },
        'four_step_significators': four_step_significators,
        'house_significators': house_significators
    }
    
    return response