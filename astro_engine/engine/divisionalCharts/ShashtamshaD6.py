"""
D6 Shashtamsha - Calculation Module
====================================
Vedic Astrology Divisional Chart Calculator - The Chart of Resistance

Features:
- Precise D6 calculations using Parashara's method
- Lahiri Ayanamsa
- Whole Sign house system
- Nakshatra and Pada calculations
- Retrograde detection
- Shows: Health, Enemies, Debts, Obstacles, Fighting Spirit, Immunity
"""

from datetime import datetime
import swisseph as swe

# ==============================================================================
# CONSTANTS
# ==============================================================================

# Zodiac signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 27 Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Planets
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': None  # Ketu is 180° opposite to Rahu
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_julian_day(birth_date, birth_time, timezone_offset):
    """Convert birth date and time to Julian Day (UT)"""
    year = birth_date.year
    month = birth_date.month
    day = birth_date.day
    
    # Parse time
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    second = float(time_parts[2]) if len(time_parts) > 2 else 0
    
    # Convert to decimal hours
    decimal_hour = hour + minute/60.0 + second/3600.0
    
    # Adjust for timezone (convert to UT)
    ut_hour = decimal_hour - timezone_offset
    
    # Calculate Julian Day
    jd = swe.julday(year, month, day, ut_hour)
    
    return jd


def get_ayanamsa(jd):
    """Get Lahiri Ayanamsa for given Julian Day"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    return ayanamsa


def get_planet_position(planet_id, jd, ayanamsa):
    """Get sidereal position of planet with speed for retrograde check"""
    if planet_id is None:
        return None, 0
    
    # Calculate position with speed
    position, ret_flag = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    
    # Convert to sidereal
    sidereal_long = position[0] - ayanamsa
    speed = position[3]  # Daily motion in longitude
    
    # Normalize to 0-360
    if sidereal_long < 0:
        sidereal_long += 360
    elif sidereal_long >= 360:
        sidereal_long -= 360
    
    return sidereal_long, speed


def calculate_ascendant(jd, latitude, longitude, ayanamsa):
    """Calculate Ascendant (Lagna) - Sidereal with Whole Sign House System"""
    # Get tropical ascendant using Whole Sign house system
    houses, ascmc = swe.houses(jd, latitude, longitude, b'W')
    tropical_asc = ascmc[0]
    
    # Convert to sidereal
    sidereal_asc = tropical_asc - ayanamsa
    
    # Normalize to 0-360
    if sidereal_asc < 0:
        sidereal_asc += 360
    elif sidereal_asc >= 360:
        sidereal_asc -= 360
    
    return sidereal_asc


def get_nakshatra_and_pada(longitude):
    """
    Calculate Nakshatra and Pada from longitude
    
    Logic:
    - 27 Nakshatras span 360° → Each nakshatra = 13°20' = 13.333...°
    - Each Nakshatra has 4 Padas → Each pada = 3°20' = 3.333...°
    
    Nakshatra number = floor(longitude / 13.333...)
    Pada number = floor((longitude % 13.333...) / 3.333...) + 1
    """
    # Each nakshatra spans 13°20' (800 arc minutes = 13.333... degrees)
    nakshatra_span = 360.0 / 27.0  # 13.333...°
    
    # Calculate nakshatra index (0-26)
    nakshatra_index = int(longitude / nakshatra_span)
    
    # Ensure within bounds
    if nakshatra_index >= 27:
        nakshatra_index = 26
    
    # Calculate position within the nakshatra
    position_in_nakshatra = longitude % nakshatra_span
    
    # Each pada spans 3°20' (200 arc minutes = 3.333... degrees)
    pada_span = nakshatra_span / 4.0  # 3.333...°
    
    # Calculate pada (1-4)
    pada = int(position_in_nakshatra / pada_span) + 1
    
    # Ensure pada is within 1-4
    if pada > 4:
        pada = 4
    
    return NAKSHATRAS[nakshatra_index], pada


def get_sign_info(longitude):
    """Get sign number and degree within sign from longitude"""
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    # Ensure sign_num is within 0-11
    if sign_num >= 12:
        sign_num = 11
    
    return sign_num, degree_in_sign


def calculate_d6_position(longitude):
    """
    Calculate D6 Shashtamsha position using Parashara's precise method
    
    Rules (Parashara):
    - Each sign divided into 6 parts of 5° each (30°/6 = 5°)
    - ODD signs (Aries=0, Gemini=2, Leo=4, Libra=6, Sagittarius=8, Aquarius=10): 
      All divisions go Aries → Taurus → Gemini → Cancer → Leo → Virgo
    - EVEN signs (Taurus=1, Cancer=3, Virgo=5, Scorpio=7, Capricorn=9, Pisces=11): 
      All divisions go Libra → Scorpio → Sagittarius → Capricorn → Aquarius → Pisces
    
    Degree Ranges:
    0°-5°: 1st division (index 0)
    5°-10°: 2nd division (index 1)
    10°-15°: 3rd division (index 2)
    15°-20°: 4th division (index 3)
    20°-25°: 5th division (index 4)
    25°-30°: 6th division (index 5)
    """
    # Get sign number (0-11) and degrees within sign
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    # Calculate division (0-5) - which 5° segment
    division = int(degree_in_sign / 5)
    
    # Ensure division is within 0-5
    if division > 5:
        division = 5
    
    # Check if sign is odd or even
    # Odd signs: Aries(0), Gemini(2), Leo(4), Libra(6), Sagittarius(8), Aquarius(10)
    # Even signs: Taurus(1), Cancer(3), Virgo(5), Scorpio(7), Capricorn(9), Pisces(11)
    is_odd_sign = (sign_num % 2 == 0)
    
    if is_odd_sign:
        # For ODD signs: Start from Aries (sign 0)
        # Division 0 → Aries(0), 1 → Taurus(1), 2 → Gemini(2), 3 → Cancer(3), 4 → Leo(4), 5 → Virgo(5)
        d6_sign = division
    else:
        # For EVEN signs: Start from Libra (sign 6)
        # Division 0 → Libra(6), 1 → Scorpio(7), 2 → Sagittarius(8), 3 → Capricorn(9), 4 → Aquarius(10), 5 → Pisces(11)
        d6_sign = 6 + division
    
    # Calculate precise degree within D6 sign
    # Take the fractional part within the 5° division and scale to 30°
    degree_fraction = (degree_in_sign % 5) / 5.0
    d6_degree = degree_fraction * 30.0
    
    # Calculate full D6 longitude
    d6_longitude = d6_sign * 30 + d6_degree
    
    return d6_sign, d6_degree, d6_longitude


def calculate_house_number(planet_longitude, ascendant_longitude):
    """
    Calculate house number using Whole Sign House System
    
    Logic:
    - In Whole Sign system, each sign is a complete house
    - House 1 = Sign of Ascendant
    - House 2 = Next sign, and so on
    
    House number = (Planet's sign - Ascendant's sign) + 1
    If result < 1, add 12
    """
    planet_sign = int(planet_longitude / 30)
    asc_sign = int(ascendant_longitude / 30)
    
    # Calculate house (1-12)
    house = ((planet_sign - asc_sign) % 12) + 1
    
    return house


def format_dms(decimal_degrees):
    """Convert decimal degrees to degrees, minutes, seconds format"""
    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    return f"{degrees}° {minutes}' {seconds:.2f}\""


def is_retrograde(speed):
    """Check if planet is retrograde based on speed"""
    # Negative speed means retrograde motion
    return "R" if speed < 0 else ""


# ==============================================================================
# CORE CALCULATION FUNCTIONS
# ==============================================================================

def calculate_d1_positions(jd, ayanamsa, ascendant_longitude):
    """Calculate D1 (Rasi) planetary positions"""
    d1_planets = {}
    planet_speeds = {}  # Store speeds for retrograde check
    
    for planet_name, planet_id in PLANETS.items():
        if planet_name == 'Ketu':
            # Calculate Ketu as 180° opposite to Rahu
            if 'Rahu' in d1_planets:
                rahu_long = d1_planets['Rahu']['longitude']
                ketu_long = (rahu_long + 180) % 360
                
                ketu_sign, ketu_degree = get_sign_info(ketu_long)
                ketu_nakshatra, ketu_pada = get_nakshatra_and_pada(ketu_long)
                ketu_house = calculate_house_number(ketu_long, ascendant_longitude)
                
                d1_planets['Ketu'] = {
                    'sign': SIGNS[ketu_sign],
                    'degrees': format_dms(ketu_degree),
                    'longitude': ketu_long,
                    'nakshatra': ketu_nakshatra,
                    'pada': ketu_pada,
                    'house': ketu_house,
                    'retrograde': ""
                }
                planet_speeds['Ketu'] = 0
        else:
            # Calculate planet position
            planet_long, speed = get_planet_position(planet_id, jd, ayanamsa)
            
            if planet_long is not None:
                planet_sign, planet_degree = get_sign_info(planet_long)
                planet_nakshatra, planet_pada = get_nakshatra_and_pada(planet_long)
                planet_house = calculate_house_number(planet_long, ascendant_longitude)
                retro = is_retrograde(speed)
                
                d1_planets[planet_name] = {
                    'sign': SIGNS[planet_sign],
                    'degrees': format_dms(planet_degree),
                    'longitude': planet_long,
                    'nakshatra': planet_nakshatra,
                    'pada': planet_pada,
                    'house': planet_house,
                    'retrograde': retro
                }
                planet_speeds[planet_name] = speed
    
    return d1_planets, planet_speeds


def calculate_d6_positions(d1_planets, d6_asc_longitude):
    """Calculate D6 (Shashtamsha) planetary positions from D1 positions"""
    d6_planets = {}
    
    for planet_name in PLANETS.keys():
        if planet_name in d1_planets:
            planet_d1_long = d1_planets[planet_name]['longitude']
            
            # Calculate D6 position
            d6_sign, d6_degree, d6_longitude = calculate_d6_position(planet_d1_long)
            d6_nakshatra, d6_pada = get_nakshatra_and_pada(d6_longitude)
            d6_house = calculate_house_number(d6_longitude, d6_asc_longitude)
            
            # Get D1 info for reference
            d1_sign_num, d1_degree_in_sign = get_sign_info(planet_d1_long)
            division_index = int(d1_degree_in_sign / 5)
            degree_range_start = division_index * 5
            degree_range_end = degree_range_start + 5
            
            d6_planets[planet_name] = {
                'sign': SIGNS[d6_sign],
                'degrees': format_dms(d6_degree),
                'longitude': d6_longitude,
                'nakshatra': d6_nakshatra,
                'pada': d6_pada,
                'house': d6_house,
                'retrograde': d1_planets[planet_name]['retrograde'],
                'from_d1_sign': d1_planets[planet_name]['sign'],
                'from_d1_degree_range': f"{degree_range_start}°-{degree_range_end}°"
            }
    
    return d6_planets


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_d6_chart(data):
    """
    Main function to calculate D6 Shashtamsha chart
    
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
    dict: Complete D6 Shashtamsha chart (D1 removed from response)
    """
    # Extract input data
    user_name = data.get('user_name')
    birth_date_str = data.get('birth_date')
    birth_time = data.get('birth_time')
    latitude = float(data.get('latitude'))
    longitude = float(data.get('longitude'))
    timezone_offset = float(data.get('timezone_offset'))
    
    # Parse birth date
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
    
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    
    # Get Lahiri Ayanamsa
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate Ascendant (D1) - Sidereal with Whole Sign House System
    asc_d1 = calculate_ascendant(jd, latitude, longitude, ayanamsa)
    asc_d1_sign, asc_d1_degree = get_sign_info(asc_d1)
    asc_d1_nakshatra, asc_d1_pada = get_nakshatra_and_pada(asc_d1)
    
    # Calculate D6 Ascendant
    d6_asc_sign, d6_asc_degree, d6_asc_longitude = calculate_d6_position(asc_d1)
    d6_asc_nakshatra, d6_asc_pada = get_nakshatra_and_pada(d6_asc_longitude)
    
    # Calculate D1 planetary positions (needed for D6 calculation)
    d1_planets, planet_speeds = calculate_d1_positions(jd, ayanamsa, asc_d1)
    
    # Calculate D6 positions from D1
    d6_planets = calculate_d6_positions(d1_planets, d6_asc_longitude)
    
    # Prepare D6 Shashtamsha chart response (D1 removed as requested)
    d6_shashtamsha_chart = {
        'ascendant': {
            'sign': SIGNS[d6_asc_sign],
            'degrees': format_dms(d6_asc_degree),
            'nakshatra': d6_asc_nakshatra,
            'pada': d6_asc_pada,
            'from_d1_sign': SIGNS[asc_d1_sign],
            'from_d1_degree_range': f"{int(asc_d1_degree/5)*5}°-{int(asc_d1_degree/5)*5+5}°"
        },
        'planetary_positions': {}
    }
    
    for planet_name, planet_data in d6_planets.items():
        d6_shashtamsha_chart['planetary_positions'][planet_name] = {
            'sign': planet_data['sign'],
            'degrees': planet_data['degrees'],
            'house': planet_data['house'],
            'nakshatra': planet_data['nakshatra'],
            'pada': planet_data['pada'],
            'retrograde': planet_data['retrograde'],
            'from_d1_sign': planet_data['from_d1_sign'],
            'from_d1_degree_range': planet_data['from_d1_degree_range']
        }
    
    # Prepare final response
    response = {
        'status': 'success',
        'user_name': user_name,
        'birth_details': {
            'birth_date': birth_date_str,
            'birth_time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset
        },
        'notes': {
            'chart_type': 'D6 Shashtamsha',
            'ayanamsa': 'Lahiri',
            'ayanamsa_value': f"{ayanamsa:.6f}",
            'house_system': 'Whole Sign',
            'coordinate_system': 'Sidereal'
        },
        'D6_Shashtamsha_chart': d6_shashtamsha_chart,
        'D6_signifies': [
            'Health & Diseases - Physical immunity and vitality',
            'Enemies & Adversaries - Open enemies and competitors',
            'Debts & Litigation - Legal matters and loans',
            'Obstacles & Struggles - Life challenges and hurdles',
            'Maternal Uncle - Mother\'s brother and his family',
            'Service & Subordinates - Servants and employees'
        ],
        'calculation_method': {
            'division_rule': 'Each sign divided into 6 equal parts of 5° each',
            'odd_signs': 'Aries, Gemini, Leo, Libra, Sagittarius, Aquarius → Start from Aries',
            'even_signs': 'Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces → Start from Libra',
            'degree_ranges': [
                '0°-5° → Division 1',
                '5°-10° → Division 2',
                '10°-15° → Division 3',
                '15°-20° → Division 4',
                '20°-25° → Division 5',
                '25°-30° → Division 6'
            ]
        },
        'interpretation_guidelines': {
            'lagna_strength': 'Strong D6 Lagna lord = High immunity and recovery power',
            'malefics_power': 'Mars, Saturn, Sun, Rahu in D6 = Fighting spirit to overcome diseases/enemies',
            'benefics_caution': 'Jupiter, Venus, Moon unless very strong = May indicate soft/compromising approach',
            'upachaya_houses': 'Malefics in 3rd, 6th, 10th, 11th houses of D6 = Maximum fighting capacity',
            'sixth_lord': 'D1\'s 6th lord position in D6 shows nature of health issues/enemies',
            'd6_vs_d30': 'D6 = Acute/fightable issues | D30 = Chronic/karmic suffering'
        }
    }
    
    return response