"""
Sade Sati Calculator - Calculations Module
Complete Vedic Astrology calculation with proper Swiss Ephemeris handling
"""

from datetime import datetime
import swisseph as swe

# Constants
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
}

# Planet relationships with Saturn
SATURN_FRIENDS = [1, 2, 5, 6, 9, 10]  # Taurus, Gemini, Virgo, Libra, Capricorn, Aquarius
SATURN_ENEMIES = [0, 3, 4, 7]  # Aries, Cancer, Leo, Scorpio
SATURN_NEUTRAL = [8, 11]  # Sagittarius, Pisces

# Exaltation and Debilitation signs
EXALTATION_SIGNS = {
    'Sun': 0, 'Moon': 1, 'Mars': 9, 'Mercury': 5,
    'Jupiter': 3, 'Venus': 11, 'Saturn': 6
}

DEBILITATION_SIGNS = {
    'Sun': 6, 'Moon': 7, 'Mars': 3, 'Mercury': 11,
    'Jupiter': 9, 'Venus': 5, 'Saturn': 0
}

OWN_SIGNS = {
    'Sun': [4], 'Moon': [3], 'Mars': [0, 7],
    'Mercury': [2, 5], 'Jupiter': [8, 11],
    'Venus': [1, 6], 'Saturn': [9, 10]
}

YOGAKARAKA_FOR = {
    1: 'Saturn',  # Taurus Ascendant
    6: 'Saturn'   # Libra Ascendant
}


def sade_sati_calculate_julian_day(date_str, time_str, timezone_offset):
    """
    Calculate Julian Day Number for given date, time and timezone
    
    Args:
        date_str: Date in format 'YYYY-MM-DD'
        time_str: Time in format 'HH:MM:SS'
        timezone_offset: Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        float: Julian Day Number in UT
    """
    try:
        # Parse datetime
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        
        # Extract components
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second
        
        # Convert time to UTC by subtracting timezone offset
        utc_hour = hour + minute/60.0 + second/3600.0 - timezone_offset
        
        # Calculate Julian Day in UT
        jd_ut = swe.julday(year, month, day, utc_hour)
        
        return jd_ut
        
    except Exception as e:
        raise ValueError(f"Error calculating Julian Day: {str(e)}")


def sade_sati_get_ayanamsa(jd_ut):
    """
    Get Lahiri Ayanamsa value for given Julian Day
    
    Args:
        jd_ut: Julian Day in UT
    
    Returns:
        float: Ayanamsa value in degrees
    """
    try:
        # Set Lahiri ayanamsa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Get ayanamsa value
        ayanamsa = swe.get_ayanamsa(jd_ut)
        
        return ayanamsa
        
    except Exception as e:
        raise ValueError(f"Error calculating Ayanamsa: {str(e)}")


def sade_sati_calculate_planet_position(jd_ut, planet_id, ayanamsa):
    """
    Calculate sidereal position of a single planet
    
    Args:
        jd_ut: Julian Day in UT
        planet_id: Swiss Ephemeris planet ID
        ayanamsa: Ayanamsa value in degrees
    
    Returns:
        dict: Planet position details
    """
    try:
        # Calculate planetary position
        # swe.calc_ut returns (xx, ret) where xx is tuple of 6 values
        result = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH)
        
        # Extract longitude (first element of result tuple)
        if isinstance(result, tuple) and len(result) >= 1:
            if isinstance(result[0], tuple) and len(result[0]) >= 1:
                tropical_longitude = result[0][0]
            else:
                tropical_longitude = result[0]
        else:
            raise ValueError(f"Unexpected result format from swe.calc_ut: {result}")
        
        # Convert tropical to sidereal
        sidereal_longitude = tropical_longitude - ayanamsa
        
        # Normalize to 0-360 range
        while sidereal_longitude < 0:
            sidereal_longitude += 360
        while sidereal_longitude >= 360:
            sidereal_longitude -= 360
        
        # Calculate sign (0-11) and degree within sign
        sign_num = int(sidereal_longitude / 30)
        degree_in_sign = sidereal_longitude % 30
        
        return {
            'longitude': round(sidereal_longitude, 6),
            'sign_num': sign_num,
            'sign_name': ZODIAC_SIGNS[sign_num],
            'degree': round(degree_in_sign, 6),
            'sign_degree': f"{ZODIAC_SIGNS[sign_num]} {round(degree_in_sign, 2)}°"
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating planet position: {str(e)}")


def sade_sati_calculate_all_planets(jd_ut, ayanamsa):
    """
    Calculate positions of all planets
    
    Args:
        jd_ut: Julian Day in UT
        ayanamsa: Ayanamsa value in degrees
    
    Returns:
        dict: All planetary positions
    """
    planets = {}
    
    try:
        for planet_name, planet_id in PLANETS.items():
            if planet_name == 'Rahu':
                # Rahu (North Node)
                planets['Rahu'] = sade_sati_calculate_planet_position(jd_ut, planet_id, ayanamsa)
                
                # Ketu is exactly opposite to Rahu (180 degrees)
                ketu_longitude = (planets['Rahu']['longitude'] + 180) % 360
                ketu_sign = int(ketu_longitude / 30)
                ketu_degree = ketu_longitude % 30
                
                planets['Ketu'] = {
                    'longitude': round(ketu_longitude, 6),
                    'sign_num': ketu_sign,
                    'sign_name': ZODIAC_SIGNS[ketu_sign],
                    'degree': round(ketu_degree, 6),
                    'sign_degree': f"{ZODIAC_SIGNS[ketu_sign]} {round(ketu_degree, 2)}°"
                }
            else:
                planets[planet_name] = sade_sati_calculate_planet_position(jd_ut, planet_id, ayanamsa)
        
        return planets
        
    except Exception as e:
        raise ValueError(f"Error calculating planetary positions: {str(e)}")


def sade_sati_calculate_ascendant(jd_ut, latitude, longitude, ayanamsa):
    """
    Calculate Ascendant (Lagna) using Whole Sign system
    
    Args:
        jd_ut: Julian Day in UT
        latitude: Geographic latitude
        longitude: Geographic longitude
        ayanamsa: Ayanamsa value in degrees
    
    Returns:
        dict: Ascendant details
    """
    try:
        # Calculate house cusps and ascendant using Placidus system
        # swe.houses returns (cusps, ascmc)
        result = swe.houses(jd_ut, latitude, longitude, b'P')
        
        # Extract ascendant (first element of ascmc tuple)
        if isinstance(result, tuple) and len(result) >= 2:
            cusps = result[0]
            ascmc = result[1]
            tropical_asc = ascmc[0]  # Ascendant is first element
        else:
            raise ValueError(f"Unexpected result format from swe.houses: {result}")
        
        # Convert tropical to sidereal
        sidereal_asc = tropical_asc - ayanamsa
        
        # Normalize
        while sidereal_asc < 0:
            sidereal_asc += 360
        while sidereal_asc >= 360:
            sidereal_asc -= 360
        
        # Calculate sign and degree
        asc_sign = int(sidereal_asc / 30)
        asc_degree = sidereal_asc % 30
        
        return {
            'longitude': round(sidereal_asc, 6),
            'sign_num': asc_sign,
            'sign_name': ZODIAC_SIGNS[asc_sign],
            'degree': round(asc_degree, 6),
            'sign_degree': f"{ZODIAC_SIGNS[asc_sign]} {round(asc_degree, 2)}°"
        }
        
    except Exception as e:
        raise ValueError(f"Error calculating Ascendant: {str(e)}")


def sade_sati_calculate_houses_whole_sign(ascendant_sign):
    """
    Calculate 12 houses using Whole Sign House System
    In this system, each house = one complete sign
    
    Args:
        ascendant_sign: Sign number (0-11) of the Ascendant
    
    Returns:
        dict: House details
    """
    houses = {}
    
    for house_num in range(1, 13):
        house_sign = (ascendant_sign + house_num - 1) % 12
        houses[house_num] = {
            'sign_num': house_sign,
            'sign_name': ZODIAC_SIGNS[house_sign]
        }
    
    return houses


def sade_sati_get_planet_house(planet_sign, ascendant_sign):
    """
    Get house number for a planet using Whole Sign system
    
    Args:
        planet_sign: Sign number of the planet
        ascendant_sign: Sign number of the Ascendant
    
    Returns:
        int: House number (1-12)
    """
    house = ((planet_sign - ascendant_sign) % 12) + 1
    return house


def sade_sati_check_jupiter_aspect_moon(jupiter_sign, moon_sign):
    """
    Check if Jupiter aspects the Moon
    Jupiter aspects: 5th, 7th, 9th houses from its position
    
    Args:
        jupiter_sign: Sign number of Jupiter
        moon_sign: Sign number of Moon
    
    Returns:
        bool: True if Jupiter aspects Moon
    """
    # Calculate aspects
    fifth_aspect = (jupiter_sign + 4) % 12
    seventh_aspect = (jupiter_sign + 6) % 12
    ninth_aspect = (jupiter_sign + 8) % 12
    
    return moon_sign in [fifth_aspect, seventh_aspect, ninth_aspect]


def sade_sati_analyze_moon_strength(moon_position, birth_date):
    """
    Analyze Moon's strength (Chandra Bala)
    
    Args:
        moon_position: Moon's position data
        birth_date: Birth date string 'YYYY-MM-DD'
    
    Returns:
        dict: Moon strength analysis
    """
    moon_sign = moon_position['sign_num']
    
    strength = {
        'exalted': False,
        'own_sign': False,
        'debilitated': False,
        'paksha': '',
        'strength_level': 'Average',
        'score': 50
    }
    
    # Check exaltation (Taurus)
    if moon_sign == EXALTATION_SIGNS['Moon']:
        strength['exalted'] = True
        strength['score'] += 40
        strength['strength_level'] = 'Very Strong'
    
    # Check own sign (Cancer)
    elif moon_sign in OWN_SIGNS['Moon']:
        strength['own_sign'] = True
        strength['score'] += 30
        strength['strength_level'] = 'Strong'
    
    # Check debilitation (Scorpio)
    elif moon_sign == DEBILITATION_SIGNS['Moon']:
        strength['debilitated'] = True
        strength['score'] -= 30
        strength['strength_level'] = 'Weak'
    
    # Determine Paksha (waxing/waning) - simplified based on date
    day = int(birth_date.split('-')[2])
    if day <= 15:
        strength['paksha'] = 'Shukla Paksha (Waxing)'
        strength['score'] += 10
    else:
        strength['paksha'] = 'Krishna Paksha (Waning)'
        strength['score'] -= 5
    
    # Normalize score
    strength['score'] = max(0, min(100, strength['score']))
    
    return strength


def sade_sati_analyze_saturn_status(saturn_position, ascendant_sign):
    """
    Analyze Saturn's status in birth chart
    
    Args:
        saturn_position: Saturn's position data
        ascendant_sign: Ascendant sign number
    
    Returns:
        dict: Saturn status analysis
    """
    saturn_sign = saturn_position['sign_num']
    saturn_house = sade_sati_get_planet_house(saturn_sign, ascendant_sign)
    
    status = {
        'sign': ZODIAC_SIGNS[saturn_sign],
        'house': saturn_house,
        'exalted': False,
        'own_sign': False,
        'debilitated': False,
        'yogakaraka': False,
        'in_kendra': False,
        'in_trikona': False,
        'strength_level': 'Average',
        'score': 50
    }
    
    # Check exaltation (Libra)
    if saturn_sign == EXALTATION_SIGNS['Saturn']:
        status['exalted'] = True
        status['score'] += 40
        status['strength_level'] = 'Very Strong (Exalted)'
    
    # Check own sign (Capricorn, Aquarius)
    elif saturn_sign in OWN_SIGNS['Saturn']:
        status['own_sign'] = True
        status['score'] += 30
        status['strength_level'] = 'Strong (Own Sign)'
    
    # Check debilitation (Aries)
    elif saturn_sign == DEBILITATION_SIGNS['Saturn']:
        status['debilitated'] = True
        status['score'] -= 30
        status['strength_level'] = 'Weak (Debilitated)'
    
    # Check Yogakaraka status
    if ascendant_sign in YOGAKARAKA_FOR and YOGAKARAKA_FOR[ascendant_sign] == 'Saturn':
        status['yogakaraka'] = True
        status['score'] += 35
        status['strength_level'] = 'Very Strong (Yogakaraka)'
    
    # Check Kendra houses (1, 4, 7, 10)
    if saturn_house in [1, 4, 7, 10]:
        status['in_kendra'] = True
        status['score'] += 10
    
    # Check Trikona houses (1, 5, 9)
    if saturn_house in [1, 5, 9]:
        status['in_trikona'] = True
        status['score'] += 10
    
    # Normalize score
    status['score'] = max(0, min(100, status['score']))
    
    return status


def sade_sati_calculate_status(natal_moon_sign, current_saturn_sign):
    """
    Calculate current Sade Sati status and phase
    
    Args:
        natal_moon_sign: Natal Moon sign number (0-11)
        current_saturn_sign: Current transiting Saturn sign number (0-11)
    
    Returns:
        dict: Sade Sati status
    """
    # Calculate relevant houses from Moon
    twelfth_from_moon = (natal_moon_sign - 1) % 12
    same_as_moon = natal_moon_sign
    second_from_moon = (natal_moon_sign + 1) % 12
    
    sade_sati = {
        'active': False,
        'phase': 'Not Active',
        'phase_number': 0,
        'description': 'Not currently in Sade Sati period',
        'affected_signs': [
            ZODIAC_SIGNS[twelfth_from_moon],
            ZODIAC_SIGNS[same_as_moon],
            ZODIAC_SIGNS[second_from_moon]
        ]
    }
    
    # Check Phase 1: Rising (12th from Moon)
    if current_saturn_sign == twelfth_from_moon:
        sade_sati['active'] = True
        sade_sati['phase'] = 'Phase 1 - Rising (Arohani)'
        sade_sati['phase_number'] = 1
        sade_sati['description'] = 'First phase: Increased expenses, mental anxiety, losses may occur'
    
    # Check Phase 2: Peak (Same as Moon)
    elif current_saturn_sign == same_as_moon:
        sade_sati['active'] = True
        sade_sati['phase'] = 'Phase 2 - Peak (Madhya)'
        sade_sati['phase_number'] = 2
        sade_sati['description'] = 'Most intense phase: Maximum impact on mind, emotions, and health'
    
    # Check Phase 3: Setting (2nd from Moon)
    elif current_saturn_sign == second_from_moon:
        sade_sati['active'] = True
        sade_sati['phase'] = 'Phase 3 - Setting (Avarohi)'
        sade_sati['phase_number'] = 3
        sade_sati['description'] = 'Final phase: Family tensions, speech issues, gradual relief begins'
    
    return sade_sati


def sade_sati_calculate_dhaiya(natal_moon_sign, current_saturn_sign):
    """
    Calculate Dhaiya (Small Panoti) - Saturn in 4th or 8th from Moon
    
    Args:
        natal_moon_sign: Natal Moon sign number
        current_saturn_sign: Current Saturn sign number
    
    Returns:
        dict: Dhaiya status
    """
    fourth_from_moon = (natal_moon_sign + 3) % 12
    eighth_from_moon = (natal_moon_sign + 7) % 12
    
    dhaiya = {
        'active': False,
        'position': None,
        'description': 'Not in Dhaiya period'
    }
    
    if current_saturn_sign == fourth_from_moon:
        dhaiya['active'] = True
        dhaiya['position'] = '4th from Moon'
        dhaiya['description'] = 'Small Panoti: Saturn transiting 4th house from Moon (2.5 years of moderate challenges)'
    
    elif current_saturn_sign == eighth_from_moon:
        dhaiya['active'] = True
        dhaiya['position'] = '8th from Moon'
        dhaiya['description'] = 'Small Panoti: Saturn transiting 8th house from Moon (2.5 years of moderate challenges)'
    
    return dhaiya


def sade_sati_analyze_cancellation_factors(planets, ascendant_sign, moon_strength, saturn_status):
    """
    Analyze all factors that cancel or mitigate Sade Sati
    
    Returns:
        dict: Cancellation factors analysis
    """
    moon_sign = planets['Moon']['sign_num']
    
    # Determine Moon sign's relationship with Saturn
    if moon_sign in SATURN_FRIENDS:
        moon_relation = 'Friend'
    elif moon_sign in SATURN_ENEMIES:
        moon_relation = 'Enemy'
    else:
        moon_relation = 'Neutral'
    
    factors = {
        'saturn_exalted': saturn_status['exalted'],
        'saturn_own_sign': saturn_status['own_sign'],
        'saturn_debilitated': saturn_status['debilitated'],
        'saturn_yogakaraka': saturn_status['yogakaraka'],
        'saturn_in_kendra': saturn_status['in_kendra'],
        'saturn_in_trikona': saturn_status['in_trikona'],
        'jupiter_aspects_moon': sade_sati_check_jupiter_aspect_moon(
            planets['Jupiter']['sign_num'],
            planets['Moon']['sign_num']
        ),
        'moon_exalted': moon_strength['exalted'],
        'moon_own_sign': moon_strength['own_sign'],
        'moon_debilitated': moon_strength['debilitated'],
        'moon_paksha': moon_strength['paksha'],
        'moon_sign_relation_with_saturn': moon_relation,
        'saturn_strength_score': saturn_status['score'],
        'moon_strength_score': moon_strength['score']
    }
    
    return factors


def sade_sati_calculate_intensity(sade_sati, cancellation_factors):
    """
    Calculate Sade Sati intensity score (0-100)
    
    Args:
        sade_sati: Sade Sati status dict
        cancellation_factors: Cancellation factors dict
    
    Returns:
        float: Intensity score
    """
    if not sade_sati['active']:
        return 0.0
    
    # Base intensity
    intensity = 50.0
    
    # Saturn factors
    if cancellation_factors['saturn_exalted']:
        intensity -= 40
    elif cancellation_factors['saturn_own_sign']:
        intensity -= 30
    elif cancellation_factors['saturn_debilitated']:
        intensity += 30
    
    # Yogakaraka effect (strongest cancellation)
    if cancellation_factors['saturn_yogakaraka']:
        intensity -= 35
    
    # Jupiter protection
    if cancellation_factors['jupiter_aspects_moon']:
        intensity -= 25
    
    # Moon strength
    if cancellation_factors['moon_exalted']:
        intensity -= 20
    elif cancellation_factors['moon_own_sign']:
        intensity -= 15
    elif cancellation_factors['moon_debilitated']:
        intensity += 20
    
    # Paksha effect
    if 'Shukla' in cancellation_factors['moon_paksha']:
        intensity -= 10
    else:
        intensity += 5
    
    # Moon-Saturn relationship
    if cancellation_factors['moon_sign_relation_with_saturn'] == 'Friend':
        intensity -= 15
    elif cancellation_factors['moon_sign_relation_with_saturn'] == 'Enemy':
        intensity += 15
    
    # Phase impact
    if sade_sati['phase_number'] == 2:  # Peak phase
        intensity += 15
    elif sade_sati['phase_number'] == 1:  # Rising
        intensity += 10
    elif sade_sati['phase_number'] == 3:  # Setting
        intensity += 5
    
    # Saturn house position
    if cancellation_factors['saturn_in_kendra']:
        intensity -= 10
    if cancellation_factors['saturn_in_trikona']:
        intensity -= 10
    
    # Normalize to 0-100 range
    intensity = max(0, min(100, intensity))
    
    return round(intensity, 2)


def sade_sati_get_intensity_interpretation(intensity):
    """
    Get interpretation of intensity score
    
    Args:
        intensity: Intensity score (0-100)
    
    Returns:
        dict: Interpretation details
    """
    if intensity == 0:
        return {
            'level': 'Not Active',
            'description': 'You are not currently in Sade Sati period.'
        }
    elif intensity <= 20:
        return {
            'level': 'Minimal/Beneficial',
            'description': 'Sade Sati is highly mitigated or even beneficial. Hard work brings significant rewards. This is a growth period.'
        }
    elif intensity <= 40:
        return {
            'level': 'Mild',
            'description': 'Some challenges but manageable with effort. Discipline and patience will help you navigate this period successfully.'
        }
    elif intensity <= 60:
        return {
            'level': 'Moderate',
            'description': 'Noticeable challenges requiring consistent effort. You will experience growth through difficulties. Stay focused.'
        }
    elif intensity <= 80:
        return {
            'level': 'Significant',
            'description': 'Major challenges in multiple life areas. Strong remedies and disciplined approach recommended. Seek guidance.'
        }
    else:
        return {
            'level': 'Severe',
            'description': 'Intense period requiring maximum effort, patience, and spiritual practices. This is a major karmic cleansing phase.'
        }


def sade_sati_get_personalized_recommendations(intensity, cancellation_factors, sade_sati):
    """
    Get personalized remedies and recommendations
    
    Args:
        intensity: Intensity score
        cancellation_factors: Cancellation factors
        sade_sati: Sade Sati status
    
    Returns:
        list: Recommendations
    """
    recommendations = []
    
    if not sade_sati['active']:
        return [
            'You are not in Sade Sati. Maintain good karma and discipline.',
            'Continue spiritual practices regularly.',
            'Save resources for future challenges.'
        ]
    
    # Universal recommendations
    recommendations.extend([
        '🕉️ Daily Practice: Chant "Om Sham Shanicharaya Namah" 108 times',
        '🙏 Worship: Pray to Lord Hanuman on Tuesdays and Saturdays',
        '📿 Mantra: Recite Hanuman Chalisa regularly for strength'
    ])
    
    # Intensity-based recommendations
    if intensity > 60:
        recommendations.extend([
            '💝 Charity: Donate black items, iron, mustard oil, or black sesame on Saturdays',
            '🪔 Lamp: Light sesame oil lamp under Peepal tree every Saturday',
            '👴 Service: Serve elderly people and those in need',
            '⏸️ Decisions: Avoid major life decisions if possible; focus on consolidation'
        ])
    
    # Jupiter-related
    if not cancellation_factors['jupiter_aspects_moon']:
        recommendations.extend([
            '💛 Jupiter Remedies: Wear yellow clothes on Thursdays',
            '📖 Spiritual Study: Read Bhagavad Gita or other sacred texts',
            '🧘 Meditation: Practice meditation for wisdom and clarity'
        ])
    
    # Moon-related (mental health)
    if intensity > 40:
        recommendations.extend([
            '🤍 Moon Remedies: Wear white clothes on Mondays',
            '🥛 Diet: Drink milk before sleep for mental peace',
            '😴 Sleep: Maintain regular sleep schedule (before 10 PM)',
            '🧘‍♀️ Mental Health: Practice pranayama and meditation daily'
        ])
    
    # Phase-specific
    if sade_sati['phase_number'] == 1:
        recommendations.extend([
            '💰 Finance: Control expenses and build emergency savings',
            '🤝 Relationships: Avoid unnecessary conflicts with others'
        ])
    elif sade_sati['phase_number'] == 2:
        recommendations.extend([
            '🏥 Health: Take extra care of health, especially mental wellbeing',
            '👨‍👩‍👧 Support: Seek emotional support from family and friends',
            '📉 Risk: Avoid major investments or risky ventures'
        ])
    elif sade_sati['phase_number'] == 3:
        recommendations.extend([
            '💬 Communication: Watch your speech; avoid harsh words',
            '🔄 Recovery: Focus on rebuilding and gradual improvement'
        ])
    
    # General advice
    recommendations.extend([
        '⚖️ Patience: Accept delays as opportunities for growth',
        '💪 Discipline: Maintain strict discipline in all areas of life',
        '🎯 Focus: Work hard consistently; results will come later',
        '🕊️ Karma: Do good deeds without expecting immediate returns'
    ])
    
    return recommendations