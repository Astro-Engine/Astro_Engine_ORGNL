# astro_calculations.py
"""
Vedic Astrology Calculations Module
Handles all astronomical and astrological calculations for Guru Chandal Dosha analysis
"""

import swisseph as swe
from datetime import datetime, timedelta
import os

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Constants
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Planet identifiers - Ketu calculated separately as Rahu + 180°
PLANET_NAMES = {
    swe.SUN: 'Sun',
    swe.MOON: 'Moon',
    swe.MARS: 'Mars',
    swe.MERCURY: 'Mercury',
    swe.JUPITER: 'Jupiter',
    swe.VENUS: 'Venus',
    swe.SATURN: 'Saturn',
    swe.TRUE_NODE: 'Rahu'
}

SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Jupiter's sign relationships (classical Vedic astrology)
JUPITER_OWN_SIGNS = ['Sagittarius', 'Pisces']
JUPITER_EXALTATION = 'Cancer'
JUPITER_DEBILITATION = 'Capricorn'
JUPITER_FRIENDLY_SIGNS = ['Aries', 'Leo', 'Scorpio', 'Cancer']  # Sun, Moon, Mars ruled
JUPITER_ENEMY_SIGNS = ['Gemini', 'Virgo', 'Taurus', 'Libra', 'Capricorn', 'Aquarius']  # Mercury, Venus, Saturn ruled

# House intensity multipliers for Guru Chandal Dosha
HOUSE_INTENSITY = {
    1: 0.9, 2: 0.8, 3: 0.6, 4: 0.8, 5: 1.0, 6: 0.3,
    7: 0.9, 8: 0.8, 9: 1.0, 10: 0.85, 11: 0.5, 12: 0.65
}

# House categories
UPACHAYA_HOUSES = [3, 6, 10, 11]  # Houses that improve with time
KENDRA_HOUSES = [1, 4, 7, 10]     # Angular houses (strong)
TRIKONA_HOUSES = [1, 5, 9]         # Trine houses (auspicious)
DUSTHANA_HOUSES = [6, 8, 12]       # Malefic houses


def calculate_julian_day(birth_date, birth_time, timezone_offset):
    """
    Calculate Julian Day for given date and time
    
    Args:
        birth_date: String in format "YYYY-MM-DD"
        birth_time: String in format "HH:MM:SS"
        timezone_offset: Float (e.g., 5.5 for IST)
    
    Returns:
        Julian Day number (float)
    """
    datetime_str = f"{birth_date} {birth_time}"
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    
    # Convert local time to UTC
    dt_utc = dt - timedelta(hours=timezone_offset)
    
    # Extract components for Swiss Ephemeris
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    
    # Calculate Julian Day
    jd = swe.julday(year, month, day, hour)
    
    return jd


def get_ayanamsa(jd):
    """
    Get Lahiri Ayanamsa for given Julian Day
    
    Args:
        jd: Julian Day number
    
    Returns:
        Ayanamsa value in degrees
    """
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    ayanamsa = swe.get_ayanamsa(jd)
    return ayanamsa


def calculate_ascendant(jd, latitude, longitude):
    """
    Calculate Ascendant (Lagna) using sidereal zodiac
    
    Args:
        jd: Julian Day number
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees
    
    Returns:
        Sidereal ascendant longitude in degrees (0-360)
    """
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate houses using Placidus (we only need ascendant)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
    
    # Get tropical ascendant
    tropical_asc = ascmc[0]
    
    # Convert to sidereal
    sidereal_asc = tropical_asc - ayanamsa
    
    # Normalize to 0-360
    if sidereal_asc < 0:
        sidereal_asc += 360
    elif sidereal_asc >= 360:
        sidereal_asc -= 360
    
    return sidereal_asc


def get_planet_position(jd, planet_id):
    """
    Get sidereal position of a planet
    
    Args:
        jd: Julian Day number
        planet_id: Swiss Ephemeris planet constant
    
    Returns:
        Sidereal longitude in degrees (0-360)
    """
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate tropical position
    tropical_pos, ret_flag = swe.calc_ut(jd, planet_id)
    
    # Convert to sidereal
    sidereal_longitude = tropical_pos[0] - ayanamsa
    
    # Normalize to 0-360
    if sidereal_longitude < 0:
        sidereal_longitude += 360
    elif sidereal_longitude >= 360:
        sidereal_longitude -= 360
    
    return sidereal_longitude


def get_sign_and_degree(longitude):
    """
    Get sign name and degree within sign from absolute longitude
    
    Args:
        longitude: Absolute longitude in degrees (0-360)
    
    Returns:
        Tuple of (sign_name, degree_in_sign)
    """
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    return SIGN_NAMES[sign_num], degree_in_sign


def calculate_whole_sign_house(planet_longitude, ascendant_longitude):
    """
    Calculate house using Whole Sign House System
    
    In Whole Sign system:
    - Each house equals exactly one zodiac sign (30 degrees)
    - The sign containing ascendant becomes 1st house
    - Subsequent signs become 2nd, 3rd houses, etc.
    
    Args:
        planet_longitude: Planet's longitude in degrees (0-360)
        ascendant_longitude: Ascendant longitude in degrees (0-360)
    
    Returns:
        House number (1-12)
    """
    asc_sign = int(ascendant_longitude / 30)
    planet_sign = int(planet_longitude / 30)
    
    house = ((planet_sign - asc_sign) % 12) + 1
    
    return house


def calculate_orb(degree1, degree2):
    """
    Calculate shortest angular distance between two degrees
    
    Args:
        degree1: First degree (0-360)
        degree2: Second degree (0-360)
    
    Returns:
        Shortest angular distance in degrees (0-180)
    """
    diff = abs(degree1 - degree2)
    
    if diff > 180:
        diff = 360 - diff
    
    return diff


def get_conjunct_planets(planets_data, target_house):
    """
    Get list of planets in the same house
    
    CRITICAL: Excludes Rahu, Ketu, AND Jupiter itself
    (Since we're checking planets conjunct WITH Jupiter)
    
    Args:
        planets_data: Dictionary of all planet data
        target_house: House number to check
    
    Returns:
        List of planet names in the same house (excluding Rahu, Ketu, Jupiter)
    """
    conjunct = []
    exclude_planets = ['Rahu', 'Ketu', 'Jupiter']
    
    for planet_name, planet_info in planets_data.items():
        if planet_info['house'] == target_house and planet_name not in exclude_planets:
            conjunct.append(planet_name)
    
    return conjunct


def check_planet_aspects_jupiter(planets_data, jupiter_house):
    """
    Check which planets aspect Jupiter using classical Vedic aspects
    
    Classical aspects:
    - All planets: 7th house (opposition)
    - Mars: 4th, 7th, 8th houses
    - Jupiter: 5th, 7th, 9th houses  
    - Saturn: 3rd, 7th, 10th houses
    
    Args:
        planets_data: Dictionary of all planet data
        jupiter_house: Jupiter's house number
    
    Returns:
        List of aspect dictionaries
    """
    aspects = []
    
    for planet_name, planet_info in planets_data.items():
        if planet_name in ['Rahu', 'Ketu', 'Jupiter']:
            continue
        
        planet_house = planet_info['house']
        house_diff = (jupiter_house - planet_house) % 12
        
        aspecting = False
        aspect_type = None
        
        # All planets aspect 7th house (opposition)
        if house_diff == 7:
            aspecting = True
            aspect_type = '7th aspect (opposition)'
        
        # Mars special aspects: 4th and 8th
        if planet_name == 'Mars' and house_diff in [4, 8]:
            aspecting = True
            aspect_type = f'{house_diff}th aspect'
        
        # Saturn special aspects: 3rd and 10th
        if planet_name == 'Saturn' and house_diff in [3, 10]:
            aspecting = True
            aspect_type = f'{house_diff}th aspect'
        
        if aspecting:
            aspects.append({
                'planet': planet_name,
                'type': aspect_type,
                'from_house': planet_house
            })
    
    return aspects


def is_waxing_moon(sun_longitude, moon_longitude):
    """
    Check if Moon is waxing (Shukla Paksha)
    
    Args:
        sun_longitude: Sun's longitude in degrees
        moon_longitude: Moon's longitude in degrees
    
    Returns:
        True if waxing, False if waning
    """
    diff = (moon_longitude - sun_longitude) % 360
    return diff < 180


def is_combust(planet_longitude, sun_longitude, planet_name):
    """
    Check if planet is combust (too close to Sun)
    
    Classical combustion orbs:
    - Moon: 12°, Mars: 17°, Mercury: 14°
    - Jupiter: 11°, Venus: 10°, Saturn: 15°
    
    Args:
        planet_longitude: Planet's longitude
        sun_longitude: Sun's longitude
        planet_name: Name of the planet
    
    Returns:
        True if combust, False otherwise
    """
    orb = calculate_orb(planet_longitude, sun_longitude)
    
    combustion_orbs = {
        'Moon': 12,
        'Mars': 17,
        'Mercury': 14,
        'Jupiter': 11,
        'Venus': 10,
        'Saturn': 15
    }
    
    threshold = combustion_orbs.get(planet_name, 10)
    
    return orb < threshold


def calculate_navamsa_position(longitude):
    """
    Calculate Navamsa (D9) position
    
    Each sign divided into 9 padas of 3°20' each:
    - Movable signs (Aries, Cancer, Libra, Capricorn): Start from Aries
    - Fixed signs (Taurus, Leo, Scorpio, Aquarius): Start from Cancer
    - Dual signs (Gemini, Virgo, Sagittarius, Pisces): Start from Libra
    
    Args:
        longitude: Absolute longitude in degrees (0-360)
    
    Returns:
        Navamsa sign name
    """
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    # Which navamsa pada (0-8) within the sign
    navamsa_pada = int(degree_in_sign / (30.0 / 9.0))
    
    # Determine sign type
    sign_type = sign_num % 3
    
    if sign_type == 0:      # Movable
        base_navamsa = 0    # Aries
    elif sign_type == 1:    # Fixed
        base_navamsa = 3    # Cancer
    else:                   # Dual
        base_navamsa = 6    # Libra
    
    navamsa_sign_num = (base_navamsa + navamsa_pada) % 12
    
    return SIGN_NAMES[navamsa_sign_num]


def check_neecha_bhanga(planets_data, ascendant_house):
    """
    Check for Neecha Bhanga Raja Yoga
    
    Cancels Jupiter's debilitation in Capricorn
    
    Conditions:
    1. Dispositor (Saturn) in Kendra from Ascendant
    2. Dispositor (Saturn) in Kendra from Moon
    3. Dispositor (Saturn) exalted in Libra
    4. Jupiter exalted in Navamsa (Cancer)
    5. Moon (exaltation lord) in Kendra from Ascendant
    
    Args:
        planets_data: Dictionary of all planet data
        ascendant_house: Ascendant house (always 1 in Whole Sign)
    
    Returns:
        Tuple of (is_cancelled, list_of_conditions_met)
    """
    jupiter = planets_data['Jupiter']
    
    if jupiter['sign'] != 'Capricorn':
        return False, None
    
    saturn = planets_data['Saturn']
    moon = planets_data['Moon']
    
    conditions_met = []
    
    # Condition 1: Saturn in Kendra from Ascendant
    if saturn['house'] in KENDRA_HOUSES:
        conditions_met.append('Saturn in Kendra from Ascendant')
    
    # Condition 2: Saturn in Kendra from Moon
    saturn_from_moon = (saturn['house'] - moon['house']) % 12
    if saturn_from_moon in [0, 3, 6, 9]:
        conditions_met.append('Saturn in Kendra from Moon')
    
    # Condition 3: Saturn exalted
    if saturn['sign'] == 'Libra':
        conditions_met.append('Saturn exalted in Libra')
    
    # Condition 4: Jupiter exalted in Navamsa
    if jupiter['navamsa_sign'] == 'Cancer':
        conditions_met.append('Jupiter exalted in Navamsa')
    
    # Condition 5: Moon in Kendra from Ascendant
    if moon['house'] in KENDRA_HOUSES:
        conditions_met.append('Moon in Kendra from Ascendant')
    
    is_cancelled = len(conditions_met) > 0
    
    return is_cancelled, conditions_met


def check_gajakesari_yoga(planets_data):
    """
    Check for Gajakesari Yoga
    
    Complete classical conditions:
    1. Jupiter and Moon in Kendra from each other
    2. Moon waxing (Shukla Paksha)
    3. Neither combust
    4. Not in dusthana houses
    5. Jupiter not debilitated
    6. Moon not in enemy signs
    
    Args:
        planets_data: Dictionary of all planet data
    
    Returns:
        Tuple of (yoga_present, list_of_conditions_met)
    """
    jupiter = planets_data['Jupiter']
    moon = planets_data['Moon']
    sun = planets_data['Sun']
    
    conditions = []
    
    # Condition 1: Kendra from each other
    house_diff = abs(jupiter['house'] - moon['house'])
    if house_diff > 6:
        house_diff = 12 - house_diff
    
    if house_diff not in [0, 3, 6, 9]:
        return False, []
    
    conditions.append('Jupiter and Moon in Kendra from each other')
    
    # Condition 2: Moon waxing
    if not is_waxing_moon(sun['longitude'], moon['longitude']):
        return False, conditions
    conditions.append('Moon is waxing (Shukla Paksha)')
    
    # Condition 3: Neither combust
    if is_combust(jupiter['longitude'], sun['longitude'], 'Jupiter'):
        return False, conditions
    if is_combust(moon['longitude'], sun['longitude'], 'Moon'):
        return False, conditions
    conditions.append('Neither planet is combust')
    
    # Condition 4: Not in dusthana
    if jupiter['house'] in DUSTHANA_HOUSES or moon['house'] in DUSTHANA_HOUSES:
        return False, conditions
    conditions.append('Not in dusthana houses')
    
    # Condition 5: Jupiter not debilitated
    if jupiter['sign'] == 'Capricorn':
        return False, conditions
    conditions.append('Jupiter not debilitated')
    
    # Condition 6: Moon not in enemy signs
    if moon['sign'] in ['Capricorn', 'Aquarius']:
        return False, conditions
    conditions.append('Moon not in enemy signs')
    
    return True, conditions


def check_vipareeta_raja_yoga(jupiter_lordships, jupiter_house):
    """
    Check for Vipareeta Raja Yoga
    
    Three types:
    - Harsha: 6th lord in 6/8/12
    - Sarala: 8th lord in 6/8/12
    - Vimala: 12th lord in 6/8/12
    
    Args:
        jupiter_lordships: List of houses Jupiter rules
        jupiter_house: House where Jupiter is placed
    
    Returns:
        Yoga type name or None
    """
    yoga_type = None
    
    if 6 in jupiter_lordships and jupiter_house in [6, 8, 12]:
        yoga_type = 'Harsha'
    elif 8 in jupiter_lordships and jupiter_house in [6, 8, 12]:
        yoga_type = 'Sarala'
    elif 12 in jupiter_lordships and jupiter_house in [6, 8, 12]:
        yoga_type = 'Vimala'
    
    return yoga_type


def get_house_lordships(ascendant_longitude):
    """
    Calculate which houses Jupiter rules
    
    Jupiter rules:
    - Sagittarius (9th sign, index 8)
    - Pisces (12th sign, index 11)
    
    Args:
        ascendant_longitude: Ascendant longitude in degrees
    
    Returns:
        List of house numbers [house1, house2]
    """
    ascendant_sign_num = int(ascendant_longitude / 30)
    
    lordships = []
    
    # Sagittarius is 9th sign (index 8)
    sagittarius_house = ((8 - ascendant_sign_num) % 12) + 1
    lordships.append(sagittarius_house)
    
    # Pisces is 12th sign (index 11)
    pisces_house = ((11 - ascendant_sign_num) % 12) + 1
    lordships.append(pisces_house)
    
    return lordships


def get_ordinal(n):
    """
    Get ordinal suffix for numbers (1st, 2nd, 3rd, etc.)
    
    Args:
        n: Integer number
    
    Returns:
        Ordinal suffix string
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix


def analyze_guru_chandal_dosha(planets_data, ascendant_longitude):
    """
    Complete Guru Chandal Dosha analysis with precise scoring
    
    CORRECTED LOGIC:
    1. Base score from orb
    2. Add/subtract for sign dignity
    3. Add malefic conjunction effects
    4. Apply house intensity multiplier
    5. Subtract benefic reduction factors
    6. Cap final score at 150 (realistic maximum)
    
    Args:
        planets_data: Dictionary of all planet data
        ascendant_longitude: Ascendant longitude
    
    Returns:
        Dictionary with complete analysis
    """
    jupiter = planets_data['Jupiter']
    rahu = planets_data['Rahu']
    
    # STEP 1: Check if in same house
    if jupiter['house'] != rahu['house']:
        return {
            'dosha_present': False,
            'message': 'No Guru Chandal Dosha - Jupiter and Rahu are not in the same house',
            'jupiter_house': jupiter['house'],
            'rahu_house': rahu['house']
        }
    
    # STEP 2: Calculate orb
    orb = calculate_orb(jupiter['longitude'], rahu['longitude'])
    
    # STEP 3: Check orb range
    if orb > 20:
        return {
            'dosha_present': False,
            'message': f'Orb too wide ({orb:.2f}°) for effective conjunction (maximum 20°)',
            'orb_degrees': round(orb, 2),
            'jupiter_house': jupiter['house'],
            'rahu_house': rahu['house']
        }
    
    # Initialize tracking variables
    score_breakdown = []
    reduction_factors = []
    
    # STEP 4: Base score from orb
    if orb <= 5:
        base_score = 100
        orb_strength = "Very Strong"
    elif orb <= 10:
        base_score = 80
        orb_strength = "Strong"
    elif orb <= 15:
        base_score = 60
        orb_strength = "Moderate"
    else:
        base_score = 40
        orb_strength = "Weak"
    
    score_breakdown.append({
        'stage': 'Base Score from Orb',
        'description': f'Orb {orb:.2f}° = {orb_strength}',
        'score': base_score
    })
    
    current_score = base_score
    
    # STEP 5: Sign dignity modification
    sign = jupiter['sign']
    sign_effect = 0
    
    if sign in JUPITER_OWN_SIGNS:
        sign_effect = 0  # No increase, but will add reduction later
        reduction_factors.append(('Jupiter in Own Sign (Sagittarius/Pisces)', 60))
    elif sign == JUPITER_EXALTATION:
        sign_effect = 0
        reduction_factors.append(('Jupiter Exalted (Cancer)', 70))
    elif sign == JUPITER_DEBILITATION:
        sign_effect = 50
        score_breakdown.append({
            'stage': 'Sign Dignity',
            'description': 'Jupiter debilitated in Capricorn',
            'score': sign_effect
        })
        current_score += sign_effect
    elif sign in JUPITER_FRIENDLY_SIGNS:
        sign_effect = 0
        reduction_factors.append(('Jupiter in Friendly Sign', 30))
    elif sign in JUPITER_ENEMY_SIGNS:
        sign_effect = 20
        score_breakdown.append({
            'stage': 'Sign Dignity',
            'description': 'Jupiter in enemy sign',
            'score': sign_effect
        })
        current_score += sign_effect
    
    # STEP 6: Malefic conjunction effects
    house = jupiter['house']
    conjunct_planets = get_conjunct_planets(planets_data, house)
    
    conjunction_additions = []
    
    for planet in conjunct_planets:
        if planet == 'Saturn':
            addition = 40
            conjunction_additions.append((planet, addition, 'Creates triple affliction with Jupiter-Rahu'))
            current_score += addition
        elif planet == 'Mars':
            addition = 25
            conjunction_additions.append((planet, addition, 'Adds aggression and impulsiveness'))
            current_score += addition
        elif planet == 'Sun':
            addition = 15
            conjunction_additions.append((planet, addition, 'Adds ego conflicts'))
            current_score += addition
        elif planet == 'Moon':
            addition = 20
            conjunction_additions.append((planet, addition, 'Adds emotional confusion'))
            current_score += addition
        elif planet == 'Venus':
            reduction_factors.append(('Venus Conjunction - adds grace', 15))
        elif planet == 'Mercury':
            reduction_factors.append(('Mercury Conjunction - adds intellect', 10))
    
    if conjunction_additions:
        total_conjunction_addition = sum([c[1] for c in conjunction_additions])
        score_breakdown.append({
            'stage': 'Malefic Conjunctions',
            'description': ', '.join([f"{c[0]} (+{c[1]})" for c in conjunction_additions]),
            'score': total_conjunction_addition
        })
    
    # STEP 7: Apply house intensity multiplier
    house_multiplier = HOUSE_INTENSITY[house]
    score_before_house = current_score
    current_score = current_score * house_multiplier
    
    score_breakdown.append({
        'stage': 'House Intensity',
        'description': f'{house}{get_ordinal(house)} house (multiplier: {house_multiplier})',
        'score': current_score - score_before_house
    })
    
    # STEP 8: Upachaya house benefit
    if house in UPACHAYA_HOUSES:
        reduction_factors.append(('Upachaya House - improves with time', 20))
    
    # STEP 9: Kendra placement
    if house in KENDRA_HOUSES:
        reduction_factors.append(('Kendra Placement - gives strength', 25))
    
    # STEP 10: Benefic aspects
    aspects = check_planet_aspects_jupiter(planets_data, house)
    
    for aspect in aspects:
        if aspect['planet'] == 'Venus':
            reduction_factors.append((f"Venus {aspect['type']}", 25))
        elif aspect['planet'] == 'Mercury':
            reduction_factors.append((f"Mercury {aspect['type']}", 20))
        elif aspect['planet'] == 'Moon':
            if is_waxing_moon(planets_data['Sun']['longitude'], planets_data['Moon']['longitude']):
                reduction_factors.append((f"Waxing Moon {aspect['type']}", 15))
    
    # STEP 11: Navamsa strength
    d9_sign = jupiter['navamsa_sign']
    
    if d9_sign == JUPITER_EXALTATION:
        reduction_factors.append(('Jupiter Exalted in Navamsa (D9)', 50))
    elif d9_sign in JUPITER_OWN_SIGNS:
        reduction_factors.append(('Jupiter in Own Sign in Navamsa (D9)', 40))
    elif d9_sign in JUPITER_FRIENDLY_SIGNS:
        reduction_factors.append(('Jupiter in Friendly Sign in Navamsa (D9)', 25))
    
    # STEP 12: Check Neecha Bhanga
    ascendant_house = 1
    neecha_bhanga, nb_conditions = check_neecha_bhanga(planets_data, ascendant_house)
    if neecha_bhanga:
        reduction_factors.append(('Neecha Bhanga Raja Yoga', 80))
    
    # STEP 13: Check Gajakesari
    gajakesari, gk_conditions = check_gajakesari_yoga(planets_data)
    if gajakesari:
        reduction_factors.append(('Gajakesari Yoga', 50))
    
    # STEP 14: Check Vipareeta
    jupiter_lordships = get_house_lordships(ascendant_longitude)
    vipareeta_type = check_vipareeta_raja_yoga(jupiter_lordships, house)
    
    if vipareeta_type:
        reduction_factors.append((f'{vipareeta_type} Vipareeta Raja Yoga', 60))
    
    # STEP 15: Apply reductions
    total_reduction = sum([factor[1] for factor in reduction_factors])
    
    if total_reduction > 0:
        score_breakdown.append({
            'stage': 'Benefic Reductions',
            'description': f'{len(reduction_factors)} positive factors',
            'score': -total_reduction
        })
    
    # STEP 16: Calculate final score
    final_score = current_score - total_reduction
    
    # Cap at minimum 0
    final_score = max(0, final_score)
    
    # STEP 17: Determine severity (adjusted scale for scores > 100)
    if final_score >= 100:
        severity = "Extremely Strong"
        severity_level = 6
        impact = "Exceptionally challenging placement with multiple afflictions. Immediate and sustained remedial measures absolutely essential."
    elif final_score >= 70:
        severity = "Very Strong"
        severity_level = 5
        impact = "Significant challenges in Jupiter significations - wisdom, education, children, dharma. Strong remedial measures essential."
    elif final_score >= 50:
        severity = "Strong"
        severity_level = 4
        impact = "Notable obstacles in higher education, guidance, and spiritual matters. Regular remedies strongly recommended."
    elif final_score >= 30:
        severity = "Moderate"
        severity_level = 3
        impact = "Some confusion in decision-making and spiritual matters. Periodic remedies helpful."
    elif final_score >= 15:
        severity = "Mild"
        severity_level = 2
        impact = "Minor effects on Jupiter matters. Minimal remedies sufficient."
    else:
        severity = "Negligible/Cancelled"
        severity_level = 1
        impact = "Dosha largely cancelled by positive factors. May bring unconventional wisdom."
    
    # STEP 18: House-specific effects
    house_effects_map = {
        1: "Affects personality, physical health, self-confidence, and life direction. May create identity confusion.",
        2: "Impacts family relationships, wealth accumulation, speech, and values. Financial ethics tested.",
        3: "Influences courage, siblings, communication, and self-efforts. Unconventional thinking patterns.",
        4: "Affects mother, home environment, property, and emotional peace. Domestic challenges possible.",
        5: "Strongly impacts children (delays/challenges), higher education, creativity, romance, and speculation. Most sensitive placement.",
        6: "Can be positive - ability to overcome enemies through unconventional means. Health issues possible.",
        7: "Affects marriage, partnerships, and spouse. May bring unconventional or delayed marriage, foreign spouse.",
        8: "Impacts transformation, occult interests, inheritance, and sudden events. Research abilities enhanced.",
        9: "Strongly affects father, luck, dharma, higher education, and spiritual teachers. Critical placement.",
        10: "Impacts career, reputation, authority, and public image. Career in unconventional fields likely.",
        11: "Affects income, gains, friendships, and desires. Income through non-traditional sources.",
        12: "Influences expenses, foreign connections, spirituality, and isolation. Foreign settlement possible."
    }
    
    house_specific_effects = house_effects_map[house]
    
    # STEP 19: Generate remedies
    remedies = []
    
    # Universal remedies
    remedies.extend([
        "Chant Jupiter mantra daily: 'Om Gram Greem Graum Sah Gurave Namah' - 108 times minimum",
        "Perform Jupiter hora prayers on Thursdays",
        "Donate yellow items (turmeric, cloth, gram dal, bananas, gold) on Thursdays",
        "Respect teachers, elders, and father figures consistently",
        "Study sacred texts - Bhagavad Gita, Upanishads, Vishnu Sahasranama",
        "Worship Lord Vishnu, especially on Thursdays and Ekadashi",
        "Maintain vegetarianism on Thursdays (avoid alcohol, meat, eggs)",
        "Wear yellow or saffron clothes on Thursdays",
        "Light ghee lamp before Vishnu or Brihaspati yantra daily",
        "Practice ethical behavior and truthfulness in all dealings"
    ])
    
    # Severity-based remedies
    if final_score >= 50:
        remedies.extend([
            "Consult qualified astrologer for Yellow Sapphire (Pukhraj) gemstone",
            "Perform Guru Chandal Dosha Nivaran Puja by experienced priest",
            "Visit Brihaspati or Vishnu temples regularly (especially Thursdays)",
            "Observe Brihaspati Vrat (Thursday fasting) for 7, 16, or 40 weeks",
            "Recite Brihaspati Kavacham or Guru Ashtottara Shatanama",
            "Sponsor religious education or donate to Vedic schools",
            "Feed yellow food to cows on Thursdays",
            "Perform 108 or 1008 Rudrabhishekam for Rahu pacification"
        ])
    
    # House-specific remedies
    if house in [5, 9]:
        remedies.extend([
            "Strengthen relationship with father - seek blessings regularly",
            "Honor all teachers and spiritual guides",
            "Support education of underprivileged children",
            "Perform Pitru Tarpan on Amavasya if ancestral issues exist",
            "Visit pilgrimage sites with father or guru"
        ])
    
    if house == 7:
        remedies.extend([
            "Perform thorough Kundali matching before marriage",
            "Consider pre-marriage remedial pujas",
            "Worship together with spouse for harmony",
            "Donate to marriage ceremonies of underprivileged"
        ])
    
    if house in [2, 11]:
        remedies.extend([
            "Maintain ethical standards in earning - avoid shortcuts",
            "Donate portion of income to educational causes",
            "Practice transparent financial dealings"
        ])
    
    # STEP 20: Detailed explanation
    detailed_explanation = f"""
GURU CHANDAL DOSHA - COMPREHENSIVE ANALYSIS

═══════════════════════════════════════════════════════════════════

DOSHA FORMATION:
Guru Chandal Dosha occurs when Jupiter (Guru - wisdom, knowledge, dharma) 
conjuncts Rahu (shadow planet - material illusions, unconventional paths).
This creates conflict between spiritual wisdom and material confusion.

═══════════════════════════════════════════════════════════════════

YOUR CHART CONFIGURATION:
- House: {house}{get_ordinal(house)} house in {sign} sign
- Orb: {orb:.2f}° ({orb_strength} conjunction)
- Jupiter: {sign} at {jupiter['degree_in_sign']:.2f}° (longitude: {jupiter['longitude']:.4f}°)
- Rahu: {rahu['sign']} at {rahu['degree_in_sign']:.2f}° (longitude: {rahu['longitude']:.4f}°)

═══════════════════════════════════════════════════════════════════

SCORING BREAKDOWN:
"""
    
    for i, stage in enumerate(score_breakdown, 1):
        sign_char = '+' if stage['score'] >= 0 else ''
        detailed_explanation += f"{i}. {stage['stage']}: {stage['description']}\n   Score adjustment: {sign_char}{stage['score']:.1f}\n"
    
    detailed_explanation += f"""
TOTAL REDUCTIONS: -{total_reduction:.1f} points
FINAL DOSHA SCORE: {final_score:.1f}/150
SEVERITY: {severity} (Level {severity_level}/6)

═══════════════════════════════════════════════════════════════════

IMPACT ASSESSMENT:
{impact}

HOUSE-SPECIFIC EFFECTS:
{house_specific_effects}
"""
    
    # Add conjunction details
    if conjunct_planets:
        detailed_explanation += f"""

═══════════════════════════════════════════════════════════════════

ADDITIONAL PLANETARY CONJUNCTIONS:
Planets in {house}{get_ordinal(house)} house with Jupiter and Rahu: {', '.join(conjunct_planets)}

Conjunction Effects:
"""
        for conj in conjunction_additions:
            detailed_explanation += f"• {conj[0]}: +{conj[1]} points - {conj[2]}\n"
    
    # Add aspect information
    if aspects:
        detailed_explanation += f"""

═══════════════════════════════════════════════════════════════════

BENEFIC ASPECTS RECEIVED:
Jupiter receives beneficial aspects that mitigate the dosha:
"""
        for aspect in aspects:
            detailed_explanation += f"• {aspect['planet']}: {aspect['type']} from {aspect['from_house']}{get_ordinal(aspect['from_house'])} house\n"
    
    # Add special yogas
    yoga_present = neecha_bhanga or gajakesari or vipareeta_type
    if yoga_present:
        detailed_explanation += """

═══════════════════════════════════════════════════════════════════

SPECIAL YOGAS (CANCELLATION FACTORS):
"""
        if neecha_bhanga:
            detailed_explanation += f"\n✓ NEECHA BHANGA RAJA YOGA: Debilitation cancelled\n  Conditions: {', '.join(nb_conditions)}\n"
        
        if gajakesari:
            detailed_explanation += f"\n✓ GAJAKESARI YOGA: Auspicious Jupiter-Moon combination\n  Conditions: {', '.join(gk_conditions)}\n"
        
        if vipareeta_type:
            detailed_explanation += f"\n✓ {vipareeta_type.upper()} VIPAREETA RAJA YOGA: Obstacles become opportunities\n"
    
    # STEP 21: Return complete analysis
    return {
        'dosha_present': True,
        'severity': severity,
        'severity_level': severity_level,
        'orb_strength': orb_strength,
        'orb_degrees': round(orb, 2),
        'house': house,
        'sign': sign,
        'score_breakdown': score_breakdown,
        'base_score': base_score,
        'score_after_all_additions': round(current_score, 2),
        'reduction_factors': [
            {
                'factor': factor[0],
                'reduction_points': factor[1]
            } for factor in reduction_factors
        ],
        'total_reduction': round(total_reduction, 2),
        'final_dosha_score': round(final_score, 2),
        'impact_description': impact,
        'house_specific_effects': house_specific_effects,
        'conjunct_planets': conjunct_planets,
        'conjunction_details': [
            {
                'planet': c[0],
                'points_added': c[1],
                'effect': c[2]
            } for c in conjunction_additions
        ],
        'aspects_received': aspects,
        'jupiter_details': {
            'sign': jupiter['sign'],
            'house': jupiter['house'],
            'degree_in_sign': round(jupiter['degree_in_sign'], 2),
            'navamsa_sign': jupiter['navamsa_sign'],
            'longitude': round(jupiter['longitude'], 4)
        },
        'rahu_details': {
            'sign': rahu['sign'],
            'house': rahu['house'],
            'degree_in_sign': round(rahu['degree_in_sign'], 2),
            'longitude': round(rahu['longitude'], 4)
        },
        'special_yogas': {
            'neecha_bhanga_raja_yoga': {
                'present': neecha_bhanga,
                'conditions_met': nb_conditions if neecha_bhanga else []
            },
            'gajakesari_yoga': {
                'present': gajakesari,
                'conditions_met': gk_conditions if gajakesari else []
            },
            'vipareeta_raja_yoga': {
                'type': vipareeta_type if vipareeta_type else None,
                'description': f'{vipareeta_type} Yoga - obstacles convert to gains' if vipareeta_type else None
            }
        },
        'jupiter_house_lordships': jupiter_lordships,
        'remedies': remedies,
        'detailed_explanation': detailed_explanation.strip()
    }


def calculate_chart(birth_date, birth_time, latitude, longitude, timezone_offset):
    """
    Calculate complete birth chart with all planetary positions
    
    Args:
        birth_date: String in format "YYYY-MM-DD"
        birth_time: String in format "HH:MM:SS"
        latitude: Float latitude in degrees
        longitude: Float longitude in degrees
        timezone_offset: Float timezone offset in hours
    
    Returns:
        Dictionary with all chart data
    """
    # Calculate Julian Day
    jd = calculate_julian_day(birth_date, birth_time, timezone_offset)
    
    # Calculate Ascendant
    ascendant_longitude = calculate_ascendant(jd, latitude, longitude)
    ascendant_sign, ascendant_degree = get_sign_and_degree(ascendant_longitude)
    
    # Calculate all planet positions
    planets_data = {}
    
    for planet_id, planet_name in PLANET_NAMES.items():
        planet_longitude = get_planet_position(jd, planet_id)
        
        sign, degree = get_sign_and_degree(planet_longitude)
        house = calculate_whole_sign_house(planet_longitude, ascendant_longitude)
        navamsa_sign = calculate_navamsa_position(planet_longitude)
        
        planets_data[planet_name] = {
            'longitude': planet_longitude,
            'sign': sign,
            'degree_in_sign': round(degree, 4),
            'house': house,
            'navamsa_sign': navamsa_sign
        }
    
    # Calculate Ketu (180° opposite to Rahu)
    rahu_longitude = planets_data['Rahu']['longitude']
    ketu_longitude = (rahu_longitude + 180) % 360
    
    sign, degree = get_sign_and_degree(ketu_longitude)
    house = calculate_whole_sign_house(ketu_longitude, ascendant_longitude)
    navamsa_sign = calculate_navamsa_position(ketu_longitude)
    
    planets_data['Ketu'] = {
        'longitude': ketu_longitude,
        'sign': sign,
        'degree_in_sign': round(degree, 4),
        'house': house,
        'navamsa_sign': navamsa_sign
    }
    
    # Return complete chart data
    return {
        'julian_day': jd,
        'ayanamsa': get_ayanamsa(jd),
        'ascendant_longitude': ascendant_longitude,
        'ascendant_sign': ascendant_sign,
        'ascendant_degree': ascendant_degree,
        'planets': planets_data
    }