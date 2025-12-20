"""
D150 Nadiamsha - Calculation Module
====================================
Vedic Astrology Divisional Chart Calculator - The Most Minute Division

Features:
- 4 DIFFERENT calculation methods for testing
- Method 1: Simple Mod 12 cycle
- Method 2: Navamsha-like odd/even pattern
- Method 3: Sign type (Movable/Fixed/Dual) pattern
- Method 4: Each sign starts from itself
- Lahiri Ayanamsa
- Whole Sign house system
- Test all methods against reference software
"""

from datetime import datetime
import swisseph as swe

# ==============================================================================
# CONSTANTS
# ==============================================================================

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': -1
}

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_julian_day(date_str, time_str, timezone_offset):
    """Convert date and time to Julian Day in UTC"""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_hour = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0) - timezone_offset
    jd = swe.julday(dt.year, dt.month, dt.day, utc_hour)
    return jd


def get_ayanamsa(jd):
    """Get Lahiri Ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd)


def get_planet_position(jd, planet_id, ayanamsa):
    """Get sidereal position and retrograde status"""
    if planet_id == -1:  # Ketu
        rahu_result = swe.calc_ut(jd, swe.MEAN_NODE)
        rahu_lon = rahu_result[0][0]
        ketu_lon = (rahu_lon + 180) % 360
        ketu_lon_sidereal = ketu_lon - ayanamsa
        if ketu_lon_sidereal < 0:
            ketu_lon_sidereal += 360
        return ketu_lon_sidereal, False
    
    result = swe.calc_ut(jd, planet_id)
    tropical_lon = result[0][0]
    speed = result[0][3]
    sidereal_lon = tropical_lon - ayanamsa
    if sidereal_lon < 0:
        sidereal_lon += 360
    return sidereal_lon, speed < 0


def get_ascendant(jd, lat, lon, ayanamsa):
    """Calculate Ascendant"""
    houses = swe.houses(jd, lat, lon, b'P')
    tropical_asc = houses[0][0]
    sidereal_asc = tropical_asc - ayanamsa
    if sidereal_asc < 0:
        sidereal_asc += 360
    return sidereal_asc


def decimal_to_dms(degrees):
    """Convert decimal degrees to DMS format"""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""


def get_nakshatra_and_pada(longitude):
    """Calculate Nakshatra and Pada from longitude"""
    longitude = longitude % 360
    nakshatra_length = 360 / 27  # 13.333333°
    nakshatra_num = int(longitude / nakshatra_length)
    position_in_nakshatra = longitude % nakshatra_length
    pada = int(position_in_nakshatra / (nakshatra_length / 4)) + 1
    return NAKSHATRAS[nakshatra_num], pada


def get_house_number(planet_longitude, ascendant_longitude):
    """Calculate house number using Whole Sign House System"""
    planet_sign = int(planet_longitude / 30)
    asc_sign = int(ascendant_longitude / 30)
    house = ((planet_sign - asc_sign) % 12) + 1
    return house


# ==============================================================================
# D150 CALCULATION METHODS (4 DIFFERENT APPROACHES)
# ==============================================================================

def calculate_d150_method1(longitude):
    """
    METHOD 1: Simple modulo 12 cycle
    Each Nadiamsha cycles through 12 signs continuously
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    nadiamsha_in_sign = int(degree_in_sign / 0.2) + 1
    if nadiamsha_in_sign > 150:
        nadiamsha_in_sign = 150
    
    absolute_nadiamsha = sign_num * 150 + nadiamsha_in_sign
    
    # Method 1: Simple mod 12
    ruling_sign_num = (absolute_nadiamsha - 1) % 12
    
    position_in_nadiamsha = degree_in_sign % 0.2
    d150_degree = (nadiamsha_in_sign - 1) * 0.2 + position_in_nadiamsha
    
    return {
        'method': 'Method 1: Simple Mod 12',
        'original_sign': SIGNS[sign_num],
        'original_degree': degree_in_sign,
        'nadiamsha_number': nadiamsha_in_sign,
        'absolute_nadiamsha': absolute_nadiamsha,
        'd150_sign': SIGNS[ruling_sign_num],
        'd150_degree': d150_degree
    }


def calculate_d150_method2(longitude):
    """
    METHOD 2: Navamsha-like pattern
    Odd signs start from same sign, even signs start from 9th sign
    Each sign gets 12.5 Nadiamshas (150/12 = 12.5)
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    nadiamsha_in_sign = int(degree_in_sign / 0.2) + 1
    if nadiamsha_in_sign > 150:
        nadiamsha_in_sign = 150
    
    absolute_nadiamsha = sign_num * 150 + nadiamsha_in_sign
    
    # Method 2: Navamsha-like odd/even pattern
    # Determine which "group" of 12.5 Nadiamshas (0-11)
    group_num = int((nadiamsha_in_sign - 1) / 12.5)
    
    # Odd signs (0,2,4,6,8,10) start from same sign
    # Even signs (1,3,5,7,9,11) start from 9th sign
    if sign_num % 2 == 0:  # Odd sign (Aries=0, Gemini=2, etc.)
        start_sign = sign_num
    else:  # Even sign
        start_sign = (sign_num + 8) % 12  # 9th sign (8 positions ahead)
    
    ruling_sign_num = (start_sign + group_num) % 12
    
    position_in_group = (nadiamsha_in_sign - 1) % 12.5
    d150_degree = position_in_group * 0.2
    
    return {
        'method': 'Method 2: Navamsha-like Pattern',
        'original_sign': SIGNS[sign_num],
        'original_degree': degree_in_sign,
        'nadiamsha_number': nadiamsha_in_sign,
        'absolute_nadiamsha': absolute_nadiamsha,
        'd150_sign': SIGNS[ruling_sign_num],
        'd150_degree': d150_degree,
        'group': group_num
    }


def calculate_d150_method3(longitude):
    """
    METHOD 3: Sign-type based pattern
    Movable, Fixed, Dual signs have different starting points
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    nadiamsha_in_sign = int(degree_in_sign / 0.2) + 1
    if nadiamsha_in_sign > 150:
        nadiamsha_in_sign = 150
    
    absolute_nadiamsha = sign_num * 150 + nadiamsha_in_sign
    
    # Method 3: Based on sign type
    # Movable: 0,3,6,9 (Aries, Cancer, Libra, Capricorn)
    # Fixed: 1,4,7,10 (Taurus, Leo, Scorpio, Aquarius)
    # Dual: 2,5,8,11 (Gemini, Virgo, Sagittarius, Pisces)
    
    group_num = int((nadiamsha_in_sign - 1) / 12.5)
    
    sign_type = sign_num % 3
    if sign_type == 0:  # Movable - start from same sign
        start_sign = sign_num
    elif sign_type == 1:  # Fixed - start from 5th sign
        start_sign = (sign_num + 4) % 12
    else:  # Dual - start from 9th sign
        start_sign = (sign_num + 8) % 12
    
    ruling_sign_num = (start_sign + group_num) % 12
    
    position_in_group = (nadiamsha_in_sign - 1) % 12.5
    d150_degree = position_in_group * 0.2
    
    return {
        'method': 'Method 3: Sign Type Pattern',
        'original_sign': SIGNS[sign_num],
        'original_degree': degree_in_sign,
        'nadiamsha_number': nadiamsha_in_sign,
        'absolute_nadiamsha': absolute_nadiamsha,
        'd150_sign': SIGNS[ruling_sign_num],
        'd150_degree': d150_degree,
        'sign_type': ['Movable', 'Fixed', 'Dual'][sign_type]
    }


def calculate_d150_method4(longitude):
    """
    METHOD 4: Each sign divides its 150 into own 12 signs
    Each sign's 150 Nadiamshas distributed as 12.5 per zodiac sign starting from itself
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    nadiamsha_in_sign = int(degree_in_sign / 0.2) + 1
    if nadiamsha_in_sign > 150:
        nadiamsha_in_sign = 150
    
    absolute_nadiamsha = sign_num * 150 + nadiamsha_in_sign
    
    # Method 4: Each sign's 150 divided into 12 groups of 12.5
    # Starting from the sign itself
    group_num = int((nadiamsha_in_sign - 1) / 12.5)
    ruling_sign_num = (sign_num + group_num) % 12
    
    position_in_group = (nadiamsha_in_sign - 1) % 12.5
    d150_degree = position_in_group * 0.2
    
    return {
        'method': 'Method 4: Each Sign Starts From Itself',
        'original_sign': SIGNS[sign_num],
        'original_degree': degree_in_sign,
        'nadiamsha_number': nadiamsha_in_sign,
        'absolute_nadiamsha': absolute_nadiamsha,
        'd150_sign': SIGNS[ruling_sign_num],
        'd150_degree': d150_degree
    }


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def test_all_d150_methods(data):
    """
    Test ALL 4 calculation methods for D150
    Use this to compare against your reference chart and determine which method is correct
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float
    
    Returns:
    --------
    dict: Results from all 4 methods for comparison
    """
    user_name = data['user_name']
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    ayanamsa = get_ayanamsa(jd)
    asc_longitude = get_ascendant(jd, latitude, longitude, ayanamsa)
    
    response = {
        'user_name': user_name,
        'birth_details': {
            'birth_date': birth_date,
            'birth_time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset
        },
        'ayanamsa': f"{ayanamsa:.6f}",
        'ascendant_original': {
            'longitude': asc_longitude,
            'sign': SIGNS[int(asc_longitude / 30)],
            'degree': decimal_to_dms(asc_longitude % 30)
        },
        'calculation_methods': {
            'method1': {},
            'method2': {},
            'method3': {},
            'method4': {}
        },
        'instruction': 'Compare each method against your reference chart to determine which is correct'
    }
    
    # Test all 4 methods for Ascendant
    response['ascendant_d150_tests'] = {
        'method1': calculate_d150_method1(asc_longitude),
        'method2': calculate_d150_method2(asc_longitude),
        'method3': calculate_d150_method3(asc_longitude),
        'method4': calculate_d150_method4(asc_longitude)
    }
    
    # Test all 4 methods for each planet
    for planet_name, planet_id in PLANETS.items():
        try:
            planet_lon, is_retro = get_planet_position(jd, planet_id, ayanamsa)
            
            response['calculation_methods']['method1'][planet_name] = calculate_d150_method1(planet_lon)
            response['calculation_methods']['method2'][planet_name] = calculate_d150_method2(planet_lon)
            response['calculation_methods']['method3'][planet_name] = calculate_d150_method3(planet_lon)
            response['calculation_methods']['method4'][planet_name] = calculate_d150_method4(planet_lon)
            
        except Exception as e:
            response['calculation_methods']['method1'][planet_name] = {'error': str(e)}
    
    return response


def calculate_d150_with_method(data, method_num=1):
    """
    Calculate D150 using the method specified by user
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float
    method_num : int
        Method number (1, 2, 3, or 4)
    
    Returns:
    --------
    dict: Complete D150 Nadiamsha chart using specified method
    """
    if method_num not in [1, 2, 3, 4]:
        raise ValueError('Method must be 1, 2, 3, or 4')
    
    method_func = {
        1: calculate_d150_method1,
        2: calculate_d150_method2,
        3: calculate_d150_method3,
        4: calculate_d150_method4
    }[method_num]
    
    user_name = data['user_name']
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    ayanamsa = get_ayanamsa(jd)
    asc_longitude = get_ascendant(jd, latitude, longitude, ayanamsa)
    
    # Calculate D150 for Ascendant
    asc_d150 = method_func(asc_longitude)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_longitude)  # From ORIGINAL position
    
    response = {
        'user_name': user_name,
        'birth_details': {
            'birth_date': birth_date,
            'birth_time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset
        },
        'notes': {
            'ayanamsa': 'Lahiri',
            'ayanamsa_value': f"{ayanamsa:.6f}",
            'chart_type': f"D150 Nadiamsha (Method {method_num})",
            'house_system': 'Whole Sign',
            'calculation_method': asc_d150['method']
        },
        'ascendant': {
            'original_sign': asc_d150['original_sign'],
            'original_degrees': decimal_to_dms(asc_d150['original_degree']),
            'd150_sign': asc_d150['d150_sign'],
            'd150_degrees': decimal_to_dms(asc_d150['d150_degree']),
            'nakshatra': asc_nakshatra,
            'pada': asc_pada,
            'nadiamsha_number': asc_d150['nadiamsha_number'],
            'absolute_nadiamsha': asc_d150['absolute_nadiamsha']
        },
        'planetary_positions': {}
    }
    
    # Calculate D150 for all planets
    for planet_name, planet_id in PLANETS.items():
        try:
            planet_lon, is_retro = get_planet_position(jd, planet_id, ayanamsa)
            planet_d150 = method_func(planet_lon)
            
            planet_nakshatra, planet_pada = get_nakshatra_and_pada(planet_lon)  # From ORIGINAL
            d150_house = get_house_number(planet_d150['d150_degree'] + (SIGNS.index(planet_d150['d150_sign']) * 30), 
                                         asc_d150['d150_degree'] + (SIGNS.index(asc_d150['d150_sign']) * 30))
            
            if planet_name == 'Rahu':
                is_retro = True
            
            response['planetary_positions'][planet_name] = {
                'original_sign': planet_d150['original_sign'],
                'original_degrees': decimal_to_dms(planet_d150['original_degree']),
                'd150_sign': planet_d150['d150_sign'],
                'd150_degrees': decimal_to_dms(planet_d150['d150_degree']),
                'house': d150_house,
                'nakshatra': planet_nakshatra,
                'pada': planet_pada,
                'retrograde': 'R' if is_retro else '',
                'nadiamsha_number': planet_d150['nadiamsha_number'],
                'absolute_nadiamsha': planet_d150['absolute_nadiamsha']
            }
            
        except Exception as e:
            response['planetary_positions'][planet_name] = {'error': str(e)}
    
    return response