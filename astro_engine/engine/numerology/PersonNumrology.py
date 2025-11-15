"""
Vedic Numerology Calculations Module
All numerology and Vedic astrology calculation functions
REWRITTEN with CORRECT datetime handling for seconds
"""

import swisseph as swe
from datetime import datetime
import math

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# ============================================================================
# CONSTANTS
# ============================================================================

# Chaldean numerology chart (no 9 assigned to letters)
CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def reduce_to_root(number, keep_master=True):
    """
    Reduce number to single digit (1-9)
    Optionally preserve master numbers: 11, 22, 33
    """
    if keep_master and number in [11, 22, 33]:
        return number
    
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    
    return number

def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def parse_time_flexible(time_str):
    """
    Parse time string flexibly - handles multiple formats
    Supports: HH:MM, HH:MM:SS, H:MM, H:MM:SS
    Returns: (hour, minute, second)
    """
    if not time_str:
        return 12, 0, 0
    
    # Split by colon
    parts = time_str.split(':')
    
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
        
        # Validate ranges
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour {hour} out of range (0-23)")
        if not (0 <= minute <= 59):
            raise ValueError(f"Minute {minute} out of range (0-59)")
        if not (0 <= second <= 59):
            raise ValueError(f"Second {second} out of range (0-59)")
        
        return hour, minute, second
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid time format '{time_str}': {e}")

def parse_datetime_complete(date_str, time_str="12:00"):
    """
    Parse date and time strings into datetime object
    Handles all time formats: HH:MM, HH:MM:SS, H:MM, H:MM:SS
    
    Args:
        date_str: Date in YYYY-MM-DD format
        time_str: Time in HH:MM or HH:MM:SS format (default: "12:00")
    
    Returns:
        datetime object
    """
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}': {e}")
    
    # Parse time flexibly
    hour, minute, second = parse_time_flexible(time_str)
    
    # Combine date and time
    return datetime(date_obj.year, date_obj.month, date_obj.day, hour, minute, second)

def get_julian_day(year, month, day, hour=12, minute=0, second=0):
    """Convert datetime to Julian Day"""
    time_decimal = hour + minute/60.0 + second/3600.0
    jd = swe.julday(year, month, day, time_decimal)
    return jd

def get_ayanamsa(jd):
    """Get Lahiri Ayanamsa for given Julian Day"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    return ayanamsa

def get_planet_position(planet_id, jd):
    """Get sidereal planet position using Lahiri ayanamsa - FIXED VERSION"""
    # swe.calc_ut returns a tuple: (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
    result = swe.calc_ut(jd, planet_id)
    
    # Extract longitude from the tuple (first element)
    tropical_long = result[0][0] if isinstance(result[0], tuple) else result[0]
    
    # Get ayanamsa and convert to sidereal
    ayanamsa = get_ayanamsa(jd)
    sidereal_long = (tropical_long - ayanamsa) % 360
    
    return sidereal_long

def get_rashi_from_longitude(longitude):
    """Get zodiac sign (Rashi) from longitude"""
    rashis = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    rashi_num = int(longitude / 30)
    return rashis[rashi_num]

# ============================================================================
# NUMEROLOGY CORE CALCULATIONS
# ============================================================================

def calculate_compound_and_root(text):
    """Calculate compound number and root number from text"""
    text = text.upper().replace(' ', '')
    
    compound = 0
    letter_values = []
    
    for char in text:
        if char.isalpha() and char in CHALDEAN_MAP:
            value = CHALDEAN_MAP[char]
            compound += value
            letter_values.append(f"{char}={value}")
    
    root = reduce_to_root(compound)
    
    return {
        'compound': compound,
        'root': root,
        'letter_breakdown': ', '.join(letter_values)
    }

# ============================================================================
# 1. NAME NUMBER (Expression Number)
# ============================================================================

def calculate_name_number(full_name):
    """
    Calculate Name Number using full name
    Represents natural talents and abilities
    """
    result = calculate_compound_and_root(full_name)
    
    meanings = {
        1: "Leader, pioneer, independent, original, creative",
        2: "Peacemaker, diplomat, cooperative, sensitive, intuitive",
        3: "Creative, expressive, optimistic, social, artistic",
        4: "Practical, stable, organized, hardworking, disciplined",
        5: "Adventurous, freedom-loving, versatile, dynamic, progressive",
        6: "Nurturing, responsible, harmonious, compassionate, family-oriented",
        7: "Analytical, spiritual, introspective, wise, perfectionist",
        8: "Ambitious, authoritative, material success, powerful, executive",
        9: "Humanitarian, compassionate, idealistic, selfless, artistic",
        11: "Intuitive, spiritual teacher, visionary, inspirational, enlightened",
        22: "Master builder, practical idealist, large-scale projects, visionary",
        33: "Master teacher, selfless service, spiritual upliftment, compassionate"
    }
    
    return {
        'name': full_name,
        'compound_number': result['compound'],
        'root_number': result['root'],
        'letter_breakdown': result['letter_breakdown'],
        'meaning': meanings.get(result['root'], 'Unknown'),
        'interpretation': f"Your name vibrates to the number {result['root']}"
    }

# ============================================================================
# 2. DESTINY NUMBER (Life Path Number)
# ============================================================================

def calculate_destiny_number(birth_date):
    """
    Calculate Destiny Number from birth date
    Represents life purpose and path
    """
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
    
    day = birth_date.day
    month = birth_date.month
    year = birth_date.year
    
    # Sum all digits
    total = 0
    for digit in str(day) + str(month) + str(year):
        total += int(digit)
    
    root = reduce_to_root(total)
    
    meanings = {
        1: "Destined for leadership, innovation, and independence",
        2: "Destined for partnership, diplomacy, and cooperation",
        3: "Destined for creative expression and communication",
        4: "Destined for building solid foundations and stability",
        5: "Destined for freedom, change, and adventure",
        6: "Destined for nurturing, service, and responsibility",
        7: "Destined for spiritual wisdom and introspection",
        8: "Destined for material mastery and achievement",
        9: "Destined for humanitarian service and completion",
        11: "Destined for spiritual teaching and enlightenment",
        22: "Destined for manifesting grand visions into reality",
        33: "Destined for selfless service to humanity"
    }
    
    return {
        'birth_date': birth_date.strftime('%Y-%m-%d'),
        'calculation': f"{day} + {month} + {year} = {total}",
        'compound_number': total,
        'destiny_number': root,
        'meaning': meanings.get(root, 'Unknown'),
        'interpretation': f"Your life path leads to {meanings.get(root, 'Unknown').lower()}"
    }

# ============================================================================
# 3. SOUL URGE NUMBER (Heart's Desire)
# ============================================================================

def calculate_soul_urge_number(full_name):
    """
    Calculate Soul Urge Number using vowels only
    Reveals inner desires and motivations
    """
    vowels = "AEIOU"
    name = full_name.upper()
    
    compound = 0
    vowels_found = []
    
    for char in name:
        if char in vowels and char in CHALDEAN_MAP:
            value = CHALDEAN_MAP[char]
            compound += value
            vowels_found.append(f"{char}={value}")
    
    root = reduce_to_root(compound)
    
    meanings = {
        1: "Desires independence, leadership, and to be number one",
        2: "Desires peace, harmony, partnership, and balance",
        3: "Desires creative expression, joy, and social interaction",
        4: "Desires stability, order, security, and practical achievements",
        5: "Desires freedom, adventure, variety, and excitement",
        6: "Desires love, family, responsibility, and harmonious home",
        7: "Desires knowledge, spiritual understanding, and wisdom",
        8: "Desires power, success, recognition, and material abundance",
        9: "Desires to help humanity, make a difference, and achieve completion",
        11: "Desires spiritual enlightenment, inspiration, and to uplift others",
        22: "Desires to build something of lasting value for the world",
        33: "Desires to uplift and teach humanity with compassion"
    }
    
    return {
        'name': full_name,
        'vowels_used': ', '.join(vowels_found) if vowels_found else 'None',
        'compound_number': compound,
        'soul_urge_number': root,
        'meaning': meanings.get(root, 'Unknown'),
        'interpretation': f"Your heart's deepest desire is {meanings.get(root, 'Unknown').lower()}"
    }

# ============================================================================
# 4. PERSONALITY NUMBER (Outer Personality)
# ============================================================================

def calculate_personality_number(full_name):
    """
    Calculate Personality Number using consonants only
    Reveals how others perceive you
    """
    vowels = "AEIOU"
    name = full_name.upper()
    
    compound = 0
    consonants_found = []
    
    for char in name:
        if char.isalpha() and char not in vowels and char in CHALDEAN_MAP:
            value = CHALDEAN_MAP[char]
            compound += value
            consonants_found.append(f"{char}={value}")
    
    root = reduce_to_root(compound)
    
    meanings = {
        1: "Appears confident, independent, authoritative, and strong",
        2: "Appears friendly, diplomatic, gentle, and approachable",
        3: "Appears charming, entertaining, sociable, and creative",
        4: "Appears reliable, practical, conservative, and dependable",
        5: "Appears dynamic, exciting, unpredictable, and magnetic",
        6: "Appears warm, nurturing, responsible, and caring",
        7: "Appears mysterious, reserved, intellectual, and dignified",
        8: "Appears powerful, ambitious, successful, and authoritative",
        9: "Appears compassionate, wise, magnetic, and charismatic",
        11: "Appears inspiring, charismatic, spiritual, and electrifying",
        22: "Appears capable, visionary, impressive, and commanding",
        33: "Appears nurturing, wise, selfless, and enlightened"
    }
    
    return {
        'name': full_name,
        'consonants_used': ', '.join(consonants_found) if consonants_found else 'None',
        'compound_number': compound,
        'personality_number': root,
        'meaning': meanings.get(root, 'Unknown'),
        'interpretation': f"Others perceive you as {meanings.get(root, 'Unknown').lower()}"
    }

# ============================================================================
# 5. PRIME NUMBER SIGNIFICANCE
# ============================================================================

def analyze_prime_significance(compound_number):
    """
    Analyze if compound number is prime and its significance
    Prime numbers have special vibrational energy
    """
    prime_meanings = {
        2: "Duality, partnership, balance, cooperation",
        3: "Trinity, creativity, expression, joy",
        5: "Freedom, change, adventure, versatility",
        7: "Spirituality, introspection, wisdom, analysis",
        11: "Master number - Intuition, enlightenment, spiritual insight",
        13: "Transformation, rebirth, karmic debt number",
        17: "Immortality, strength, self-discipline, star number",
        19: "Independence, completion of cycle, karmic debt",
        23: "Royal star of the lion - Success, charisma, communication",
        29: "Uncertainty, spiritual trials, intuition",
        31: "Isolation, introspection, self-expression",
        37: "Creativity, imagination, spiritual growth",
        41: "Foundation, stability, hard work",
        43: "Revolution, breakthrough, transformation",
        47: "Spiritual wisdom, analysis, perfection",
        53: "Freedom, adventure, dynamic change"
    }
    
    is_prime_num = is_prime(compound_number)
    
    return {
        'compound_number': compound_number,
        'is_prime': is_prime_num,
        'significance': prime_meanings.get(compound_number, "Unique prime energy" if is_prime_num else "Composite number - blend of energies"),
        'interpretation': f"This is a {'prime' if is_prime_num else 'composite'} number with {'special' if is_prime_num else 'blended'} vibrational energy"
    }

# ============================================================================
# 6. KARAKA PLANETS (Vedic Significators)
# ============================================================================

def get_natural_karaka_planets():
    """
    Get Natural Karaka (Significator) Planets
    These are fixed significators in Vedic astrology
    """
    natural_karakas = {
        'Atma_Karaka': {
            'planet': 'Sun',
            'represents': 'Soul, self, father, authority, vitality',
            'life_areas': ['Self-realization', 'Father', 'Government', 'Authority', 'Soul purpose']
        },
        'Mana_Karaka': {
            'planet': 'Moon',
            'represents': 'Mind, emotions, mother, home, peace',
            'life_areas': ['Mental peace', 'Mother', 'Home', 'Emotions', 'Public image']
        },
        'Bhatru_Karaka': {
            'planet': 'Mars',
            'represents': 'Siblings, courage, energy, property, strength',
            'life_areas': ['Siblings', 'Courage', 'Property', 'Accidents', 'Initiative']
        },
        'Matru_Karaka': {
            'planet': 'Moon',
            'represents': 'Mother, nurturing, home comforts, education',
            'life_areas': ['Mother', 'Vehicles', 'Education', 'Happiness', 'Comforts']
        },
        'Putra_Karaka': {
            'planet': 'Jupiter',
            'represents': 'Children, wisdom, spirituality, creativity, intelligence',
            'life_areas': ['Children', 'Intelligence', 'Mantras', 'Devotion', 'Education']
        },
        'Gnati_Karaka': {
            'planet': 'Mars',
            'represents': 'Enemies, diseases, obstacles, maternal uncle, competition',
            'life_areas': ['Enemies', 'Diseases', 'Debts', 'Litigation', 'Competition']
        },
        'Kalatra_Karaka': {
            'planet': 'Venus',
            'represents': 'Spouse, marriage, partnerships, pleasures, relationships',
            'life_areas': ['Spouse', 'Marriage', 'Business partners', 'Passion', 'Relationships']
        },
        'Dhana_Karaka': {
            'planet': 'Jupiter',
            'represents': 'Wealth, knowledge, expansion, fortune, prosperity',
            'life_areas': ['Wealth', 'Education', 'Children', 'Fortune', 'Wisdom']
        },
        'Pitru_Karaka': {
            'planet': 'Sun',
            'represents': 'Father, ancestors, authority, career, status',
            'life_areas': ['Father', 'Career', 'Fame', 'Authority', 'Government']
        },
        'Bhagya_Karaka': {
            'planet': 'Jupiter',
            'represents': 'Fortune, luck, dharma, higher learning, grace',
            'life_areas': ['Fortune', 'Religion', 'Guru', 'Long journeys', 'Higher education']
        },
        'Karma_Karaka': {
            'planet': 'Saturn',
            'represents': 'Career, duty, hard work, service, responsibility',
            'life_areas': ['Career', 'Profession', 'Status', 'Responsibility', 'Service']
        }
    }
    
    return natural_karakas

def calculate_chara_karakas(birth_date, birth_time, latitude, longitude):
    """
    Calculate Chara (Variable) Karakas based on planetary longitudes
    COMPLETELY REWRITTEN with correct datetime handling
    These vary from person to person based on birth chart
    """
    # Parse birth date and time using flexible parser
    if isinstance(birth_date, str):
        dt = parse_datetime_complete(birth_date, birth_time)
    else:
        dt = birth_date
    
    # Get Julian Day with all time components
    jd = get_julian_day(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    # Planet IDs for Swiss Ephemeris
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN
    }
    
    # Get sidereal longitudes for all planets
    planetary_longitudes = {}
    for name, planet_id in planets.items():
        longitude = get_planet_position(planet_id, jd)
        planetary_longitudes[name] = longitude
    
    # Sort planets by longitude (descending)
    sorted_planets = sorted(
        planetary_longitudes.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Assign Chara Karakas
    chara_karaka_names = [
        ('Atma_Karaka', 'Soul - Highest degree planet'),
        ('Amatya_Karaka', 'Career/Minister - Second highest'),
        ('Bhatru_Karaka', 'Siblings/Father - Third highest'),
        ('Matru_Karaka', 'Mother - Fourth highest'),
        ('Putra_Karaka', 'Children - Fifth highest'),
        ('Gnati_Karaka', 'Enemies/Obstacles - Sixth highest'),
        ('Dara_Karaka', 'Spouse - Seventh/Lowest degree')
    ]
    
    chara_karakas = {}
    for i, (karaka_name, meaning) in enumerate(chara_karaka_names):
        if i < len(sorted_planets):
            planet_name, longitude = sorted_planets[i]
            chara_karakas[karaka_name] = {
                'planet': planet_name,
                'longitude': round(longitude, 4),
                'rashi': get_rashi_from_longitude(longitude),
                'represents': meaning
            }
    
    return chara_karakas

# ============================================================================
# 7. NUMBER COMPATIBILITY MATRIX
# ============================================================================

def get_compatibility_matrix():
    """
    Complete Chaldean Number Compatibility Matrix
    Based on ruling planet friendships
    """
    compatibility = {
        1: {
            'ruling_planet': 'Sun',
            'excellent': [1, 2, 3, 9],
            'good': [4, 7],
            'neutral': [5],
            'challenging': [6, 8],
            'reason': 'Sun is friendly with Moon(2), Jupiter(3), Mars(9)'
        },
        2: {
            'ruling_planet': 'Moon',
            'excellent': [1, 2, 5, 6],
            'good': [3, 9],
            'neutral': [7],
            'challenging': [4, 8],
            'reason': 'Moon is friendly with Sun(1), Mercury(5), Venus(6)'
        },
        3: {
            'ruling_planet': 'Jupiter',
            'excellent': [1, 2, 3, 6, 9],
            'good': [5],
            'neutral': [7],
            'challenging': [4, 8],
            'reason': 'Jupiter is friendly with Sun, Moon, Venus, Mars'
        },
        4: {
            'ruling_planet': 'Rahu/Uranus',
            'excellent': [4, 5, 6, 7],
            'good': [],
            'neutral': [2],
            'challenging': [1, 3, 8, 9],
            'reason': 'Rahu is compatible with Mercury(5), Venus(6), Ketu(7)'
        },
        5: {
            'ruling_planet': 'Mercury',
            'excellent': [2, 3, 4, 5, 6],
            'good': [1, 7],
            'neutral': [],
            'challenging': [8, 9],
            'reason': 'Mercury is friendly with most planets except Sun partially'
        },
        6: {
            'ruling_planet': 'Venus',
            'excellent': [2, 3, 4, 5, 6, 8, 9],
            'good': [],
            'neutral': [7],
            'challenging': [1],
            'reason': 'Venus is friendly with all except Sun'
        },
        7: {
            'ruling_planet': 'Ketu/Neptune',
            'excellent': [4, 7, 8],
            'good': [1, 5],
            'neutral': [2, 3, 6],
            'challenging': [9],
            'reason': 'Ketu is compatible with Rahu(4), Saturn(8)'
        },
        8: {
            'ruling_planet': 'Saturn',
            'excellent': [6, 7, 8],
            'good': [],
            'neutral': [],
            'challenging': [1, 2, 3, 4, 5, 9],
            'reason': 'Saturn has few friends - only Venus(6), Ketu(7)'
        },
        9: {
            'ruling_planet': 'Mars',
            'excellent': [1, 3, 6, 9],
            'good': [2],
            'neutral': [5],
            'challenging': [4, 7, 8],
            'reason': 'Mars is friendly with Sun(1), Jupiter(3), Venus(6)'
        }
    }
    
    return compatibility

def calculate_number_compatibility(number1, number2):
    """
    Calculate compatibility between two numbers
    """
    matrix = get_compatibility_matrix()
    
    if number1 not in matrix or number2 not in matrix:
        return {'error': 'Invalid number. Must be between 1-9'}
    
    person1_compat = matrix[number1]
    person2_compat = matrix[number2]
    
    # Determine compatibility level
    if number2 in person1_compat['excellent']:
        level = 'Excellent'
        score = 90
        description = 'Highly compatible - natural harmony and understanding'
    elif number2 in person1_compat['good']:
        level = 'Good'
        score = 75
        description = 'Compatible - positive relationship with mutual respect'
    elif number2 in person1_compat['neutral']:
        level = 'Neutral'
        score = 50
        description = 'Neutral - requires effort and understanding'
    else:
        level = 'Challenging'
        score = 30
        description = 'Challenging - requires significant compromise and patience'
    
    # Check reverse compatibility
    reverse_level = 'Neutral'
    if number1 in person2_compat['excellent']:
        reverse_level = 'Excellent'
    elif number1 in person2_compat['good']:
        reverse_level = 'Good'
    elif number1 in person2_compat['challenging']:
        reverse_level = 'Challenging'
    
    advice_map = {
        'Excellent': 'This is a natural match with excellent energy flow. Support each other\'s goals.',
        'Good': 'Good compatibility with positive potential. Focus on communication and mutual respect.',
        'Neutral': 'Requires conscious effort. Find common ground and respect differences.',
        'Challenging': 'Significant differences exist. Patience, understanding, and compromise are essential.'
    }
    
    return {
        'number1': number1,
        'number2': number2,
        'planet1': person1_compat['ruling_planet'],
        'planet2': person2_compat['ruling_planet'],
        'compatibility_level': level,
        'score': score,
        'description': description,
        'number1_to_number2': level,
        'number2_to_number1': reverse_level,
        'planetary_relationship': f"{person1_compat['ruling_planet']} and {person2_compat['ruling_planet']}",
        'advice': advice_map.get(level, 'Unknown')
    }

# ============================================================================
# PLANETARY ASSOCIATIONS
# ============================================================================

def get_ruling_planet_info(number):
    """Get detailed ruling planet information for a number"""
    planet_info = {
        1: {
            'planet': 'Sun',
            'element': 'Fire',
            'nature': 'Yang/Masculine',
            'colors': ['Gold', 'Orange', 'Yellow'],
            'gemstones': ['Ruby', 'Garnet', 'Red Spinel'],
            'favorable_days': ['Sunday'],
            'favorable_dates': [1, 10, 19, 28],
            'qualities': 'Leadership, authority, vitality, independence'
        },
        2: {
            'planet': 'Moon',
            'element': 'Water',
            'nature': 'Yin/Feminine',
            'colors': ['White', 'Cream', 'Light Blue', 'Silver'],
            'gemstones': ['Pearl', 'Moonstone', 'White Coral'],
            'favorable_days': ['Monday'],
            'favorable_dates': [2, 11, 20, 29],
            'qualities': 'Intuition, emotions, nurturing, receptivity'
        },
        3: {
            'planet': 'Jupiter',
            'element': 'Fire',
            'nature': 'Yang/Masculine',
            'colors': ['Yellow', 'Gold', 'Purple', 'Violet'],
            'gemstones': ['Yellow Sapphire', 'Topaz', 'Citrine'],
            'favorable_days': ['Thursday'],
            'favorable_dates': [3, 12, 21, 30],
            'qualities': 'Wisdom, expansion, optimism, spirituality'
        },
        4: {
            'planet': 'Rahu/Uranus',
            'element': 'Air',
            'nature': 'Yang/Masculine',
            'colors': ['Grey', 'Blue', 'Black'],
            'gemstones': ['Hessonite', 'Gomed', 'Smoky Quartz'],
            'favorable_days': ['Saturday', 'Sunday'],
            'favorable_dates': [4, 13, 22, 31],
            'qualities': 'Innovation, rebellion, sudden changes, unconventional'
        },
        5: {
            'planet': 'Mercury',
            'element': 'Air',
            'nature': 'Neutral',
            'colors': ['Green', 'Light Green', 'Turquoise'],
            'gemstones': ['Emerald', 'Green Tourmaline', 'Peridot'],
            'favorable_days': ['Wednesday'],
            'favorable_dates': [5, 14, 23],
            'qualities': 'Communication, intellect, versatility, business'
        },
        6: {
            'planet': 'Venus',
            'element': 'Earth',
            'nature': 'Yin/Feminine',
            'colors': ['Pink', 'White', 'Light Blue', 'Cream'],
            'gemstones': ['Diamond', 'White Sapphire', 'Opal'],
            'favorable_days': ['Friday'],
            'favorable_dates': [6, 15, 24],
            'qualities': 'Love, beauty, harmony, luxury, relationships'
        },
        7: {
            'planet': 'Ketu/Neptune',
            'element': 'Water',
            'nature': 'Yin/Feminine',
            'colors': ['Purple', 'Violet', 'Grey', 'White'],
            'gemstones': ['Cat\'s Eye', 'Amethyst', 'Turquoise'],
            'favorable_days': ['Sunday', 'Monday'],
            'favorable_dates': [7, 16, 25],
            'qualities': 'Spirituality, mysticism, introspection, intuition'
        },
        8: {
            'planet': 'Saturn',
            'element': 'Earth',
            'nature': 'Yin/Feminine',
            'colors': ['Black', 'Dark Blue', 'Purple', 'Grey'],
            'gemstones': ['Blue Sapphire', 'Amethyst', 'Black Onyx'],
            'favorable_days': ['Saturday'],
            'favorable_dates': [8, 17, 26],
            'qualities': 'Discipline, karma, responsibility, patience, endurance'
        },
        9: {
            'planet': 'Mars',
            'element': 'Fire',
            'nature': 'Yang/Masculine',
            'colors': ['Red', 'Maroon', 'Scarlet', 'Crimson'],
            'gemstones': ['Red Coral', 'Carnelian', 'Bloodstone'],
            'favorable_days': ['Tuesday'],
            'favorable_dates': [9, 18, 27],
            'qualities': 'Courage, energy, passion, action, competition'
        },
        11: {
            'planet': 'Moon (Enhanced)',
            'element': 'Water',
            'nature': 'Yin/Feminine (Spiritual)',
            'colors': ['Silver', 'White', 'Pearl'],
            'gemstones': ['Pearl', 'Moonstone', 'Clear Quartz'],
            'favorable_days': ['Monday'],
            'favorable_dates': [2, 11, 20, 29],
            'qualities': 'Spiritual intuition, enlightenment, inspiration, master energy'
        },
        22: {
            'planet': 'Saturn (Enhanced)',
            'element': 'Earth',
            'nature': 'Yang/Masculine (Visionary)',
            'colors': ['Gold', 'Black', 'Royal Blue'],
            'gemstones': ['Sapphire', 'Lapis Lazuli'],
            'favorable_days': ['Saturday'],
            'favorable_dates': [4, 13, 22, 31],
            'qualities': 'Master builder, practical vision, large-scale manifestation'
        },
        33: {
            'planet': 'Jupiter (Enhanced)',
            'element': 'Fire',
            'nature': 'Yang/Masculine (Divine)',
            'colors': ['Gold', 'Yellow', 'White'],
            'gemstones': ['Yellow Sapphire', 'Diamond'],
            'favorable_days': ['Thursday'],
            'favorable_dates': [3, 12, 21, 30],
            'qualities': 'Master teacher, spiritual service, compassion, healing'
        }
    }
    
    return planet_info.get(number, {})

# ============================================================================
# SUN SIGN CALCULATION (Vedic/Sidereal)
# ============================================================================

def calculate_sun_sign(birth_date, birth_time="12:00", latitude=0.0, longitude=0.0):
    """
    Calculate sidereal Sun sign (Rashi) using Lahiri Ayanamsa
    COMPLETELY REWRITTEN with correct datetime handling
    """
    # Parse date and time using flexible parser
    if isinstance(birth_date, str):
        dt = parse_datetime_complete(birth_date, birth_time)
    else:
        dt = birth_date
    
    # Get Julian Day with all time components
    jd = get_julian_day(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    # Get sidereal Sun position
    sun_longitude = get_planet_position(swe.SUN, jd)
    
    # Get Rashi
    rashi = get_rashi_from_longitude(sun_longitude)
    
    # Get ayanamsa
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate tropical position for reference
    result = swe.calc_ut(jd, swe.SUN)
    # Fix: Extract longitude from tuple properly
    tropical_longitude = result[0][0] if isinstance(result[0], tuple) else result[0]
    
    return {
        'birth_datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
        'ayanamsa': round(ayanamsa, 4),
        'tropical_longitude': round(tropical_longitude, 4),
        'sidereal_longitude': round(sun_longitude, 4),
        'sun_sign_rashi': rashi,
        'degree_in_sign': round(sun_longitude % 30, 4)
    }