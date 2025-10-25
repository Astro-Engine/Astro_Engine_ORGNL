"""
calculations.py
Vedic Astrology Calculation Engine
Contains all astrological calculations for Angarak Dosha analysis
"""

import swisseph as swe
from datetime import datetime
import os
import math

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

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
    'Rahu': swe.TRUE_NODE,
    'Ketu': swe.TRUE_NODE
}

# Nakshatra list (27 nakshatras)
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Nakshatra lords
NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
    'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun',
    'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
    'Jupiter', 'Saturn', 'Mercury'
]

# Planet relationships
PLANET_RELATIONSHIPS = {
    'Mars': {
        'exalted_sign': 9,      # Capricorn
        'debilitated_sign': 3,  # Cancer
        'own_signs': [0, 7],    # Aries, Scorpio
        'friendly_signs': [4, 8, 11],  # Leo, Sagittarius, Pisces
        'neutral_signs': [1, 2, 5, 10],
        'enemy_signs': [6]  # Libra
    }
}

# Yogakaraka definitions
YOGAKARAKA_MARS = [3, 4]  # Cancer and Leo lagnas


def calculate_julian_day(birth_date, birth_time, timezone_offset):
    """
    Calculate Julian Day Number for the given date, time and timezone
    """
    try:
        date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
        time_obj = datetime.strptime(birth_time, "%H:%M:%S")
        
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        hour = time_obj.hour
        minute = time_obj.minute
        second = time_obj.second
        
        # Convert to decimal hours
        decimal_hours = hour + minute/60.0 + second/3600.0
        
        # Adjust for timezone (convert to UTC)
        decimal_hours_utc = decimal_hours - timezone_offset
        
        # Calculate Julian Day
        jd = swe.julday(year, month, day, decimal_hours_utc)
        
        return jd
    except Exception as e:
        raise ValueError(f"Error calculating Julian Day: {str(e)}")


def get_planetary_position(jd, planet_id):
    """
    Get sidereal planetary position using Lahiri ayanamsa
    """
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
        longitude = result[0][0]
        longitude = longitude % 360
        return longitude
    except Exception as e:
        raise ValueError(f"Error calculating planetary position: {str(e)}")


def get_sign_and_degree(longitude):
    """
    Convert longitude to sign number and degrees within sign
    """
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    return {
        'sign_num': sign_num,
        'sign_name': ZODIAC_SIGNS[sign_num],
        'degree': degree_in_sign,
        'total_longitude': longitude
    }


def get_nakshatra(longitude):
    """
    Calculate nakshatra from longitude
    Each nakshatra is 13°20' (13.333...)
    """
    nakshatra_num = int(longitude / 13.333333333333334)
    nakshatra_num = nakshatra_num % 27
    
    degree_in_nakshatra = longitude % 13.333333333333334
    pada = int(degree_in_nakshatra / 3.333333333333333) + 1
    
    return {
        'nakshatra_num': nakshatra_num,
        'nakshatra_name': NAKSHATRAS[nakshatra_num],
        'nakshatra_lord': NAKSHATRA_LORDS[nakshatra_num],
        'pada': pada
    }


def calculate_ascendant(jd, latitude, longitude):
    """
    Calculate Ascendant (Lagna) using Lahiri ayanamsa
    """
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        houses = swe.houses_ex(jd, latitude, longitude, b'P')
        asc_longitude = houses[0][0]
        ayanamsa = swe.get_ayanamsa_ut(jd)
        asc_longitude_sidereal = (asc_longitude - ayanamsa) % 360
        return asc_longitude_sidereal
    except Exception as e:
        raise ValueError(f"Error calculating ascendant: {str(e)}")


def calculate_whole_sign_houses(asc_longitude):
    """
    Calculate Whole Sign House system
    """
    asc_sign = int(asc_longitude / 30)
    
    houses = {}
    for i in range(12):
        house_num = i + 1
        sign_num = (asc_sign + i) % 12
        houses[house_num] = {
            'sign_num': sign_num,
            'sign_name': ZODIAC_SIGNS[sign_num],
            'start_degree': sign_num * 30,
            'end_degree': (sign_num + 1) * 30
        }
    
    return houses


def get_planet_house(planet_longitude, houses):
    """
    Determine which house a planet is in (whole sign system)
    """
    planet_sign = int(planet_longitude / 30)
    
    for house_num, house_info in houses.items():
        if house_info['sign_num'] == planet_sign:
            return house_num
    
    return None


def calculate_orb(long1, long2):
    """
    Calculate the shortest angular distance between two longitudes
    """
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff


def check_conjunction(planet1_long, planet2_long, max_orb=30):
    """
    Check if two planets are in conjunction (same sign)
    """
    sign1 = int(planet1_long / 30)
    sign2 = int(planet2_long / 30)
    
    is_conjunct = (sign1 == sign2)
    orb = calculate_orb(planet1_long, planet2_long) if is_conjunct else None
    
    return {
        'is_conjunct': is_conjunct,
        'orb': orb,
        'sign1': sign1,
        'sign2': sign2
    }


def get_conjunction_strength(orb):
    """
    Determine conjunction strength based on orb
    """
    if orb is None:
        return None
    if orb < 5:
        return "Very Strong"
    elif orb < 10:
        return "Strong"
    elif orb < 15:
        return "Moderate"
    elif orb < 20:
        return "Weak"
    else:
        return "Very Weak"


def get_mars_state_in_sign(mars_sign):
    """
    Get Mars state (exalted, debilitated, own sign, etc.)
    """
    if mars_sign == PLANET_RELATIONSHIPS['Mars']['exalted_sign']:
        return "Exalted"
    elif mars_sign == PLANET_RELATIONSHIPS['Mars']['debilitated_sign']:
        return "Debilitated"
    elif mars_sign in PLANET_RELATIONSHIPS['Mars']['own_signs']:
        return "Own Sign"
    elif mars_sign in PLANET_RELATIONSHIPS['Mars']['friendly_signs']:
        return "Friendly"
    elif mars_sign in PLANET_RELATIONSHIPS['Mars']['enemy_signs']:
        return "Enemy"
    else:
        return "Neutral"


def is_mars_yogakaraka(lagna_sign):
    """
    Check if Mars is Yogakaraka for the given lagna
    """
    return lagna_sign in YOGAKARAKA_MARS


def check_planet_aspect(planet1_long, planet2_long, aspect_degrees, orb_tolerance=8):
    """
    Check if planet1 aspects planet2 at given aspect degrees
    """
    diff = calculate_orb(planet1_long, planet2_long)
    
    for aspect_deg in aspect_degrees:
        if abs(diff - aspect_deg) <= orb_tolerance:
            return {
                'has_aspect': True,
                'aspect_type': aspect_deg,
                'orb': abs(diff - aspect_deg)
            }
    
    return {'has_aspect': False}


def calculate_dosha_effects_by_house(house_num):
    """
    Describe effects of Angarak Dosha in specific houses
    """
    house_effects = {
        1: {
            "severity": "Very High",
            "areas": ["Self-identity", "Physical health", "Personality", "Overall vitality"],
            "effects": ["Aggressive personality", "Prone to accidents", "Impulsive behavior", "Health issues related to head/blood"],
            "positive_potential": ["Strong leadership", "Courage", "Initiative", "Physical strength"]
        },
        2: {
            "severity": "High",
            "areas": ["Wealth", "Family", "Speech", "Food"],
            "effects": ["Harsh speech", "Family conflicts", "Financial instability", "Issues with accumulated wealth"],
            "positive_potential": ["Direct communication", "Wealth through own efforts", "Strong values"]
        },
        3: {
            "severity": "Moderate",
            "areas": ["Courage", "Siblings", "Communication", "Short travels"],
            "effects": ["Conflicts with siblings", "Excessive courage leading to risks", "Communication problems"],
            "positive_potential": ["Exceptional courage", "Media success", "Technical skills"]
        },
        4: {
            "severity": "Very High",
            "areas": ["Mother", "Home", "Emotions", "Property"],
            "effects": ["Mother's health concerns", "Emotional turbulence", "Property disputes", "Unstable home environment"],
            "positive_potential": ["Real estate gains", "Strong emotional resilience", "Property development"]
        },
        5: {
            "severity": "High",
            "areas": ["Children", "Education", "Creativity", "Investments"],
            "effects": ["Concerns about children", "Education obstacles", "Speculation losses", "Creative blocks"],
            "positive_potential": ["Research abilities", "Creative innovation", "Competitive intelligence", "Strategic thinking"]
        },
        6: {
            "severity": "Beneficial",
            "areas": ["Enemies", "Diseases", "Obstacles", "Service"],
            "effects": ["This is a BENEFICIAL placement - Viparita Raja Yoga"],
            "positive_potential": ["Victory over enemies", "Success in litigation", "Healing abilities", "Competitive success", "Military/police success"]
        },
        7: {
            "severity": "Very High",
            "areas": ["Marriage", "Partnerships", "Spouse", "Business"],
            "effects": ["Marital conflicts", "Partnership problems", "Aggressive spouse or conflicts with spouse", "Business disputes"],
            "positive_potential": ["Strong business partnerships", "Marriage to strong-willed partner", "Success abroad"]
        },
        8: {
            "severity": "Very High",
            "areas": ["Longevity", "Sudden events", "Occult", "Inheritance"],
            "effects": ["Sudden unexpected events", "Chronic health issues", "Inheritance disputes", "Hidden obstacles"],
            "positive_potential": ["Occult knowledge", "Research abilities", "Transformation power", "Interest in mysteries"]
        },
        9: {
            "severity": "Moderate",
            "areas": ["Fortune", "Father", "Religion", "Higher learning"],
            "effects": ["Conflicts with father/teachers", "Spiritual confusion", "Challenges in higher education"],
            "positive_potential": ["Foreign fortune", "Spiritual warrior", "Philosophical debates", "Higher knowledge"]
        },
        10: {
            "severity": "High",
            "areas": ["Career", "Reputation", "Authority", "Public image"],
            "effects": ["Career instability", "Conflicts with authority", "Reputation challenges", "Aggressive professional approach"],
            "positive_potential": ["Leadership positions", "Military/engineering career", "Public recognition", "Administrative power"]
        },
        11: {
            "severity": "Moderate",
            "areas": ["Gains", "Elder siblings", "Aspirations", "Friends"],
            "effects": ["Gains through struggle", "Elder sibling issues", "Conflicts in social circles"],
            "positive_potential": ["Large network", "Ambitious goals achieved", "Gains through effort", "Social activism"]
        },
        12: {
            "severity": "Moderate",
            "areas": ["Losses", "Foreign lands", "Spirituality", "Isolation"],
            "effects": ["Unnecessary expenses", "Hidden enemies", "Sleep disturbances"],
            "positive_potential": ["Foreign settlement", "Spiritual practices", "Research in isolation", "Occult powers"]
        }
    }
    
    return house_effects.get(house_num, {})


def calculate_cancellation_factors(planetary_data, mars_rahu_conjunction, lagna_sign):
    """
    Calculate various cancellation factors for Angarak Dosha
    Using conservative, well-established rules
    """
    cancellations = []
    
    if not mars_rahu_conjunction['is_conjunct']:
        return cancellations
    
    mars_data = planetary_data['Mars']
    rahu_data = planetary_data['Rahu']
    jupiter_data = planetary_data['Jupiter']
    venus_data = planetary_data['Venus']
    mercury_data = planetary_data['Mercury']
    saturn_data = planetary_data['Saturn']
    
    mars_house = mars_data['house']
    mars_sign = mars_data['sign_num']
    mars_long = mars_data['longitude']
    rahu_long = rahu_data['longitude']
    
    # CRITICAL FIX: Check for benefic planets in SAME SIGN (conjunction)
    # Factor 1: Jupiter CONJUNCTION (same sign)
    if jupiter_data['sign_num'] == mars_sign:
        jupiter_mars_orb = calculate_orb(jupiter_data['longitude'], mars_long)
        jupiter_rahu_orb = calculate_orb(jupiter_data['longitude'], rahu_long)
        min_orb = min(jupiter_mars_orb, jupiter_rahu_orb)
        
        if min_orb < 15:  # Close conjunction
            strength = "Very Strong" if min_orb < 5 else "Strong" if min_orb < 10 else "Moderate"
            cancellations.append({
                'factor': 'Jupiter Conjunction (Same Sign)',
                'description': f'Jupiter is conjunct Mars-Rahu in {ZODIAC_SIGNS[mars_sign]}, within {min_orb:.2f}° orb',
                'impact': f'{strength} cancellation - Jupiter provides wisdom, expansion, and protection',
                'strength': strength,
                'orb': round(min_orb, 2),
                'verified': True
            })
    
    # Factor 2: Jupiter ASPECT (from different house)
    elif jupiter_data['sign_num'] != mars_sign:
        # Jupiter's special aspects: 5th (120°), 7th (180°), 9th (240°)
        jupiter_aspects = [120, 180, 240]
        
        mars_aspect = check_planet_aspect(jupiter_data['longitude'], mars_long, jupiter_aspects)
        rahu_aspect = check_planet_aspect(jupiter_data['longitude'], rahu_long, jupiter_aspects)
        
        if mars_aspect['has_aspect'] or rahu_aspect['has_aspect']:
            cancellations.append({
                'factor': 'Jupiter Aspect',
                'description': f'Jupiter aspects Mars-Rahu conjunction from {jupiter_data["sign"]}',
                'impact': 'Moderate to Strong cancellation - Jupiter\'s grace protects',
                'strength': 'Moderate',
                'aspect_type': mars_aspect.get('aspect_type') or rahu_aspect.get('aspect_type'),
                'verified': True
            })
    
    # Factor 3: Venus CONJUNCTION (same sign)
    if venus_data['sign_num'] == mars_sign:
        venus_mars_orb = calculate_orb(venus_data['longitude'], mars_long)
        venus_rahu_orb = calculate_orb(venus_data['longitude'], rahu_long)
        min_orb = min(venus_mars_orb, venus_rahu_orb)
        
        if min_orb < 15:
            strength = "Strong" if min_orb < 8 else "Moderate"
            cancellations.append({
                'factor': 'Venus Conjunction (Same Sign)',
                'description': f'Venus is conjunct Mars-Rahu in {ZODIAC_SIGNS[mars_sign]}, within {min_orb:.2f}° orb',
                'impact': f'{strength} reduction - Venus brings harmony and balance',
                'strength': strength,
                'orb': round(min_orb, 2),
                'verified': True
            })
    
    # Factor 4: Venus in Kendra (Angular houses 1, 4, 7, 10)
    if venus_data['house'] in [1, 4, 7, 10] and venus_data['sign_num'] != mars_sign:
        cancellations.append({
            'factor': 'Venus in Kendra',
            'description': f'Venus is strong in angular house {venus_data["house"]} ({venus_data["sign"]})',
            'impact': 'Moderate reduction - Provides stability and harmony',
            'strength': 'Moderate',
            'verified': True
        })
    
    # Factor 5: Mercury CONJUNCTION (same sign) - helps with mental control
    if mercury_data['sign_num'] == mars_sign:
        mercury_mars_orb = calculate_orb(mercury_data['longitude'], mars_long)
        min_orb = min(mercury_mars_orb, calculate_orb(mercury_data['longitude'], rahu_long))
        
        if min_orb < 15:
            cancellations.append({
                'factor': 'Mercury Conjunction (Same Sign)',
                'description': f'Mercury conjunct Mars-Rahu, provides intellectual control',
                'impact': 'Mild to Moderate reduction - Brings logic and reasoning',
                'strength': 'Mild',
                'orb': round(min_orb, 2),
                'verified': True
            })
    
    # Factor 6: 6th House Placement (Viparita - complete cancellation)
    if mars_house == 6:
        cancellations.append({
            'factor': '6th House Placement (Viparita Raja Yoga)',
            'description': 'Mars-Rahu in 6th house creates beneficial Viparita Yoga',
            'impact': 'COMPLETE CANCELLATION - Converts to beneficial yoga',
            'strength': 'Complete',
            'verified': True
        })
    
    # Factor 7: Mars as Yogakaraka (Cancer or Leo lagna)
    if is_mars_yogakaraka(lagna_sign):
        cancellations.append({
            'factor': 'Mars Yogakaraka Status',
            'description': f'Mars is Yogakaraka (best planet) for {ZODIAC_SIGNS[lagna_sign]} ascendant',
            'impact': 'Strong reduction - Mars becomes benefic for this lagna',
            'strength': 'Strong',
            'verified': True
        })
    
    # Factor 8: Mars Exalted (Capricorn)
    mars_state = get_mars_state_in_sign(mars_sign)
    if mars_state == "Exalted":
        cancellations.append({
            'factor': 'Mars Exalted',
            'description': 'Mars in Capricorn (exalted) - dignified energy',
            'impact': 'Moderate reduction - Channelizes energy constructively',
            'strength': 'Moderate',
            'verified': True
        })
    
    # Factor 9: Mars in Own Sign (Aries or Scorpio)
    if mars_state == "Own Sign":
        cancellations.append({
            'factor': 'Mars in Own Sign',
            'description': f'Mars in {ZODIAC_SIGNS[mars_sign]} (own sign) - comfortable placement',
            'impact': 'Mild reduction - Mars is strong and confident',
            'strength': 'Mild',
            'verified': True
        })
    
    return cancellations


def calculate_overall_severity(house_effects, cancellations, orb, mars_state):
    """
    Calculate overall severity considering all factors
    """
    base_severity = house_effects.get('severity', 'Moderate')
    
    # If in 6th house, it's beneficial
    if base_severity == "Beneficial":
        return "Cancelled - Beneficial Yoga"
    
    # Count strong cancellations
    complete_cancellations = sum(1 for c in cancellations if c.get('strength') == 'Complete')
    very_strong_cancellations = sum(1 for c in cancellations if c.get('strength') == 'Very Strong')
    strong_cancellations = sum(1 for c in cancellations if c.get('strength') == 'Strong')
    moderate_cancellations = sum(1 for c in cancellations if c.get('strength') == 'Moderate')
    
    # Complete cancellation
    if complete_cancellations > 0:
        return "Cancelled - Beneficial"
    
    # Very strong cancellation present (like close Jupiter conjunction)
    if very_strong_cancellations > 0:
        if base_severity == "Very High":
            return "Moderate"
        else:
            return "Low"
    
    # Multiple strong cancellations
    if strong_cancellations >= 2:
        if base_severity == "Very High":
            return "Moderate"
        else:
            return "Low"
    
    # One strong cancellation
    if strong_cancellations == 1:
        if base_severity == "Very High":
            return "High to Moderate"
        elif base_severity == "High":
            return "Moderate"
        else:
            return "Low to Moderate"
    
    # Multiple moderate cancellations
    if moderate_cancellations >= 2:
        if base_severity == "Very High":
            return "High"
        else:
            return "Moderate"
    
    # One moderate cancellation
    if moderate_cancellations == 1:
        if base_severity == "Very High":
            return "Very High to High"
        else:
            return base_severity
    
    # No cancellations - full severity
    if orb < 5 and base_severity == "Very High":
        return "Very High"
    
    return base_severity


def analyze_angarak_dosha(planetary_data, mars_rahu_conjunction, lagna_sign):
    """
    Comprehensive Angarak Dosha analysis with precise cancellation logic
    """
    
    if not mars_rahu_conjunction['is_conjunct']:
        return {
            'has_angarak_dosha': False,
            'message': 'No Angarak Dosha found - Mars and Rahu are not in conjunction (not in same sign)'
        }
    
    mars_data = planetary_data['Mars']
    rahu_data = planetary_data['Rahu']
    
    conjunction_house = mars_data['house']
    conjunction_sign = mars_data['sign']
    orb = mars_rahu_conjunction['orb']
    
    # Get house effects
    house_effects = calculate_dosha_effects_by_house(conjunction_house)
    
    # Calculate cancellations with new precise logic
    cancellations = calculate_cancellation_factors(
        planetary_data, 
        mars_rahu_conjunction, 
        lagna_sign
    )
    
    # Get Mars state
    mars_state = get_mars_state_in_sign(mars_data['sign_num'])
    
    # Calculate overall severity with new logic
    overall_severity = calculate_overall_severity(
        house_effects, 
        cancellations, 
        orb, 
        mars_state
    )
    
    # Determine conjunction strength
    conjunction_strength = get_conjunction_strength(orb)
    
    # Positive manifestations
    positive_aspects = [
        "Exceptional courage and fearlessness",
        "Strong determination and willpower",
        "Success in competitive fields (sports, military, surgery)",
        "Research and investigation abilities",
        "Technical and mechanical skills",
        "Leadership in crisis situations",
        "Breaking barriers and conventions",
        "Occult and mystical knowledge"
    ]
    
    # Remedies
    remedies = {
        'mantras': [
            "Om Kram Kreem Kroum Sah Bhaumaya Namah (Mars mantra - 108 times daily)",
            "Om Bhram Bhreem Bhroum Sah Rahave Namah (Rahu mantra - 108 times daily)",
            "Hanuman Chalisa daily recitation",
            "Om Namo Bhagavate Narasimhaya (for protection)"
        ],
        'donations': [
            "Tuesdays: Red lentils (masoor dal), red cloth, jaggery, copper items",
            "Saturdays: Black blankets, mustard oil, iron items for Rahu",
            "Feed dogs regularly (especially black or brown dogs)",
            "Donate blood if health permits"
        ],
        'gemstones': [
            "Red Coral for Mars (3-5 carats, worn after astrological consultation)",
            "Hessonite (Gomed) for Rahu (5-7 carats, after consultation)",
            "Note: Gemstones should only be worn after proper consultation"
        ],
        'spiritual_practices': [
            "Visit Hanuman temples on Tuesdays",
            "Worship Lord Kartikeya (Murugan/Subramanya)",
            "Practice Hanuman Chalisa or Bajrang Baan",
            "Perform Mars puja on Tuesdays",
            "Meditation and pranayama for anger management"
        ],
        'lifestyle': [
            "Practice anger management techniques daily",
            "Regular physical exercise or martial arts",
            "Avoid impulsive financial decisions",
            "Avoid speculation and gambling",
            "Channel aggression into sports or productive work",
            "Practice patience and mindfulness"
        ]
    }
    
    # Additional insights based on cancellations
    interpretation_notes = []
    
    if cancellations:
        interpretation_notes.append(
            f"Important: {len(cancellations)} cancellation factor(s) detected. "
            f"These significantly modify the dosha's effects."
        )
    
    if any(c.get('strength') in ['Very Strong', 'Complete'] for c in cancellations):
        interpretation_notes.append(
            "Strong benefic influence present. Negative effects are substantially reduced. "
            "Focus on channeling the positive manifestations."
        )
    
    if overall_severity in ["Low", "Moderate", "Low to Moderate"]:
        interpretation_notes.append(
            "With proper awareness and remedies, this dosha can be effectively managed "
            "and even converted into positive drive and achievement."
        )
    
    analysis = {
        'has_angarak_dosha': True,
        'conjunction_details': {
            'orb': round(orb, 2),
            'conjunction_strength': conjunction_strength,
            'mars_degree': round(mars_data['degree_in_sign'], 2),
            'rahu_degree': round(rahu_data['degree_in_sign'], 2)
        },
        'placement': {
            'house': conjunction_house,
            'sign': conjunction_sign,
            'nakshatra': mars_data['nakshatra'],
            'nakshatra_lord': mars_data['nakshatra_lord']
        },
        'mars_state': mars_state,
        'overall_severity': overall_severity,
        'house_effects': house_effects,
        'cancellation_factors': cancellations,
        'cancellation_summary': {
            'total_factors': len(cancellations),
            'has_strong_cancellation': any(c.get('strength') in ['Very Strong', 'Strong'] for c in cancellations),
            'has_complete_cancellation': any(c.get('strength') == 'Complete' for c in cancellations)
        },
        'positive_manifestations': positive_aspects,
        'remedies': remedies,
        'interpretation_notes': interpretation_notes
    }
    
    return analysis


def calculate_chart_data(birth_date, birth_time, latitude, longitude, timezone_offset):
    """
    Master function to calculate complete chart data
    Returns all planetary positions, houses, and dosha analysis
    """
    # Calculate Julian Day
    jd = calculate_julian_day(birth_date, birth_time, timezone_offset)
    
    # Calculate Ascendant
    asc_longitude = calculate_ascendant(jd, latitude, longitude)
    asc_info = get_sign_and_degree(asc_longitude)
    
    # Calculate Whole Sign Houses
    houses = calculate_whole_sign_houses(asc_longitude)
    
    # Calculate all planetary positions
    planetary_positions = {}
    for planet_name, planet_id in PLANETS.items():
        if planet_name == 'Ketu':
            # Ketu is 180° opposite to Rahu
            rahu_long = planetary_positions['Rahu']['longitude']
            ketu_long = (rahu_long + 180) % 360
            planet_long = ketu_long
        else:
            planet_long = get_planetary_position(jd, planet_id)
        
        sign_info = get_sign_and_degree(planet_long)
        nakshatra_info = get_nakshatra(planet_long)
        house_num = get_planet_house(planet_long, houses)
        
        planetary_positions[planet_name] = {
            'longitude': round(planet_long, 6),
            'sign': sign_info['sign_name'],
            'sign_num': sign_info['sign_num'],
            'degree_in_sign': round(sign_info['degree'], 2),
            'nakshatra': nakshatra_info['nakshatra_name'],
            'nakshatra_lord': nakshatra_info['nakshatra_lord'],
            'pada': nakshatra_info['pada'],
            'house': house_num
        }
    
    # Check Mars-Rahu conjunction
    mars_long = planetary_positions['Mars']['longitude']
    rahu_long = planetary_positions['Rahu']['longitude']
    
    mars_rahu_conjunction = check_conjunction(mars_long, rahu_long)
    
    # Perform comprehensive Angarak Dosha analysis
    dosha_analysis = analyze_angarak_dosha(
        planetary_positions,
        mars_rahu_conjunction,
        asc_info['sign_num']
    )
    
    return {
        'ascendant': {
            'sign': asc_info['sign_name'],
            'degree': round(asc_info['degree'], 2),
            'longitude': round(asc_longitude, 6)
        },
        'houses': houses,
        'planetary_positions': planetary_positions,
        'angarak_dosha_analysis': dosha_analysis
    }