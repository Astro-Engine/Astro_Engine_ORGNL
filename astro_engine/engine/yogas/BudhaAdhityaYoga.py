import swisseph as swe
from datetime import datetime, timedelta
import math
from itertools import combinations, permutations

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Planetary relationships
PLANETARY_RELATIONS = {
    'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 'neutral': ['Mercury'], 'enemies': ['Venus', 'Saturn']},
    'Mercury': {'friends': ['Sun', 'Venus'], 'neutral': ['Mars', 'Jupiter', 'Saturn'], 'enemies': ['Moon']}
}

# Exaltation and debilitation signs
EXALTATION = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 'Mercury': 'Virgo',
    'Jupiter': 'Cancer', 'Venus': 'Pisces', 'Saturn': 'Libra'
}

DEBILITATION = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer', 'Mercury': 'Pisces',
    'Jupiter': 'Capricorn', 'Venus': 'Virgo', 'Saturn': 'Aries'
}

class MathUtils:
    """Mathematical utilities for combinations and permutations"""
    
    @staticmethod
    def factorial(n):
        """Calculate factorial: n!"""
        if n <= 1:
            return 1
        return n * MathUtils.factorial(n - 1)
    
    @staticmethod
    def permutation(n, r):
        """Calculate P(n,r) = n!/(n-r)! - Order matters"""
        if r > n or r < 0:
            return 0
        return MathUtils.factorial(n) // MathUtils.factorial(n - r)
    
    @staticmethod
    def combination(n, r):
        """Calculate C(n,r) = n!/[r!(n-r)!] - Order doesn't matter"""
        if r > n or r < 0:
            return 0
        return MathUtils.factorial(n) // (MathUtils.factorial(r) * MathUtils.factorial(n - r))

class YogaCombinationAnalyzer:
    """Analyze yoga formations using combination and permutation rules"""
    
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        self.houses = list(range(1, 13))
        self.signs = SIGNS
    
    def get_basic_yoga_combinations(self, planet_count=2):
        """
        Get all possible yoga combinations for given planet count
        Uses COMBINATION rule: C(n,r) - order doesn't matter for basic formation
        """
        total_planets = len(self.planets)
        possible_combinations = MathUtils.combination(total_planets, planet_count)
        
        # Generate actual combinations
        planet_combinations = list(combinations(self.planets, planet_count))
        
        return {
            'total_possible': possible_combinations,
            'combinations': planet_combinations,
            'mathematical_basis': f"C({total_planets},{planet_count}) = {possible_combinations}"
        }
    
    def get_degree_permutations(self, planets_in_yoga, degree_ranges):
        """
        Get all possible degree arrangements for yoga strength analysis
        Uses PERMUTATION rule: P(n,r) - order matters for strength calculation
        """
        degree_arrangements = []
        
        # For each planet, get possible degree positions
        for perm in permutations(degree_ranges, len(planets_in_yoga)):
            arrangement = {}
            for i, planet in enumerate(planets_in_yoga):
                arrangement[planet] = perm[i]
            degree_arrangements.append(arrangement)
        
        total_permutations = MathUtils.permutation(len(degree_ranges), len(planets_in_yoga))
        
        return {
            'total_permutations': total_permutations,
            'arrangements': degree_arrangements,
            'mathematical_basis': f"P({len(degree_ranges)},{len(planets_in_yoga)}) = {total_permutations}"
        }
    
    def get_house_sign_combinations(self):
        """
        Get all possible house-sign placement combinations
        Uses COMBINATION rule: C(12,1) × C(12,1) for independent selections
        """
        house_combinations = MathUtils.combination(12, 1)  # Choose 1 house from 12
        sign_combinations = MathUtils.combination(12, 1)   # Choose 1 sign from 12
        total_combinations = house_combinations * sign_combinations  # 12 × 12 = 144
        
        return {
            'house_combinations': house_combinations,
            'sign_combinations': sign_combinations,
            'total_placement_combinations': total_combinations,
            'mathematical_basis': f"C(12,1) × C(12,1) = {total_combinations}"
        }

def get_house(lon, asc_sign_index):
    """Calculate house number for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = SIGNS[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_planet_strength(planet_name, sign):
    """Determine planet strength in a sign."""
    if sign == EXALTATION.get(planet_name):
        return "Exalted"
    elif sign == DEBILITATION.get(planet_name):
        return "Debilitated"
    elif planet_name == SIGN_LORDS.get(sign):
        return "Own Sign"
    elif planet_name in PLANETARY_RELATIONS.get(planet_name, {}).get('friends', []):
        return "Friend"
    elif planet_name in PLANETARY_RELATIONS.get(planet_name, {}).get('enemies', []):
        return "Enemy"
    else:
        return "Neutral"

def calculate_separation(sun_lon, mercury_lon):
    """Calculate exact separation between Sun and Mercury."""
    diff = abs(mercury_lon - sun_lon)
    if diff > 180:
        diff = 360 - diff
    return diff

def analyze_combustion_permutations(sun_lon, mercury_lon):
    """
    Analyze combustion using PERMUTATION rules - order/sequence matters
    Different arrangements give different combustion intensities
    """
    separation = calculate_separation(sun_lon, mercury_lon)
    
    # PERMUTATION ANALYSIS: Order matters for combustion intensity
    if sun_lon < mercury_lon:
        sequence = "Mercury ahead of Sun"
        mercury_position = "Leading"
    else:
        sequence = "Sun ahead of Mercury"
        mercury_position = "Following"
    
    # Combustion intensity based on permutation (sequence)
    if separation <= 3:
        intensity = "Severe Combustion"
        strength_reduction = 90
    elif separation <= 6:
        intensity = "Moderate Combustion"
        strength_reduction = 70
    elif separation <= 8.5:
        intensity = "Mild Combustion"
        strength_reduction = 50
    else:
        intensity = "No Combustion"
        strength_reduction = 0
    
    return {
        'separation_degrees': round(separation, 2),
        'sequence': sequence,
        'mercury_position': mercury_position,
        'combustion_intensity': intensity,
        'strength_reduction_percent': strength_reduction,
        'is_combust': separation <= 8.5,
        'permutation_analysis': f"Order matters: {sequence} affects combustion intensity"
    }

def analyze_budha_aditya_yoga_with_combinations(sun_data, mercury_data, analyzer):
    """
    Analyze Budha Aditya Yoga using exact combination and permutation rules
    """
    analysis = {
        "yoga_present": False,
        "mathematical_analysis": {},
        "combination_analysis": {},
        "permutation_analysis": {},
        "yoga_strength": "Not Present",
        "overall_rating": 0,
        "conditions_met": [],
        "conditions_failed": []
    }
    
    # STEP 1: COMBINATION ANALYSIS - Basic yoga formation (order doesn't matter)
    sun_sign = sun_data['sign']
    mercury_sign = mercury_data['sign']
    
    # Basic combination: Sun + Mercury in same sign
    yoga_planets = ['Sun', 'Mercury']
    basic_combinations = analyzer.get_basic_yoga_combinations(2)
    
    analysis["combination_analysis"] = {
        "yoga_planets": yoga_planets,
        "same_sign_requirement": sun_sign == mercury_sign,
        "mathematical_basis": "C(2,2) = 1 (selecting both Sun and Mercury)",
        "formation_rule": "Order doesn't matter for basic formation",
        "total_possible_two_planet_yogas": basic_combinations['total_possible']
    }
    
    if sun_sign == mercury_sign:
        analysis["yoga_present"] = True
        analysis["conditions_met"].append("Sun and Mercury in same sign (Combination rule satisfied)")
        
        # STEP 2: PERMUTATION ANALYSIS - Degree arrangements (order matters)
        sun_lon = sun_data['longitude']
        mercury_lon = mercury_data['longitude']
        
        combustion_analysis = analyze_combustion_permutations(sun_lon, mercury_lon)
        
        # Define degree ranges for permutation analysis
        degree_ranges = [
            "0-10°", "10-20°", "20-30°"  # Three ranges in each sign
        ]
        
        sun_range = f"{int(sun_lon % 30)//10*10}-{int(sun_lon % 30)//10*10+10}°"
        mercury_range = f"{int(mercury_lon % 30)//10*10}-{int(mercury_lon % 30)//10*10+10}°"
        
        permutation_arrangements = analyzer.get_degree_permutations(
            yoga_planets, 
            [sun_range, mercury_range]
        )
        
        analysis["permutation_analysis"] = {
            "combustion_analysis": combustion_analysis,
            "degree_arrangements": permutation_arrangements,
            "sequence_importance": "Order of degrees affects yoga strength",
            "mathematical_basis": f"P(2,2) = 2 (different arrangements: Sun-Mercury vs Mercury-Sun)"
        }
        
        # Rating calculation based on both combination and permutation factors
        base_rating = 40  # Base for combination formation
        
        # Permutation-based adjustments
        if not combustion_analysis['is_combust']:
            base_rating += 30
            analysis["conditions_met"].append("Mercury not combust (Permutation sequence favorable)")
        else:
            base_rating -= combustion_analysis['strength_reduction_percent'] // 2
            analysis["conditions_failed"].append(f"Mercury combust: {combustion_analysis['combustion_intensity']}")
        
        # Sign strength (combination of planetary dignities)
        sun_strength = get_planet_strength('Sun', sun_sign)
        mercury_strength = get_planet_strength('Mercury', mercury_sign)
        
        strength_combinations = [
            (sun_strength, mercury_strength),
            (mercury_strength, sun_strength)  # Both orders considered
        ]
        
        strength_bonus = 0
        if sun_strength in ["Exalted", "Own Sign"]:
            strength_bonus += 15
            analysis["conditions_met"].append(f"Sun is {sun_strength}")
        elif sun_strength == "Enemy":
            strength_bonus -= 5
            analysis["conditions_failed"].append(f"Sun in enemy sign")
            
        if mercury_strength in ["Exalted", "Own Sign"]:
            strength_bonus += 15
            analysis["conditions_met"].append(f"Mercury is {mercury_strength}")
        elif mercury_strength == "Enemy":
            strength_bonus -= 5
            analysis["conditions_failed"].append(f"Mercury in enemy sign")
        
        # House placement (combination rule - house selection)
        house_analysis = analyzer.get_house_sign_combinations()
        house_num = sun_data['house']
        
        house_bonus = 0
        if house_num in [1, 4, 7, 10]:  # Kendra
            house_bonus = 20
            house_quality = "Kendra (Angular)"
        elif house_num in [1, 5, 9]:  # Trikona
            house_bonus = 25
            house_quality = "Trikona (Trinal)"
        elif house_num == 11:
            house_bonus = 15
            house_quality = "Gains house"
        elif house_num in [6, 8, 12]:
            house_bonus = -10
            house_quality = "Dusthana (Malefic)"
        else:
            house_bonus = 5
            house_quality = "Neutral"
        
        if house_bonus > 0:
            analysis["conditions_met"].append(f"Placed in {house_quality} house")
        else:
            analysis["conditions_failed"].append(f"Placed in {house_quality} house")
        
        # Final rating
        total_rating = base_rating + strength_bonus + house_bonus
        analysis["overall_rating"] = max(0, min(100, total_rating))
        
        # Determine yoga strength
        if total_rating >= 80:
            analysis["yoga_strength"] = "Excellent"
        elif total_rating >= 60:
            analysis["yoga_strength"] = "Good"
        elif total_rating >= 40:
            analysis["yoga_strength"] = "Moderate"
        elif total_rating >= 20:
            analysis["yoga_strength"] = "Weak"
        else:
            analysis["yoga_strength"] = "Very Weak"
        
        # Mathematical summary
        analysis["mathematical_analysis"] = {
            "combination_rule_applied": "Basic yoga formation uses C(9,2) for planet selection",
            "permutation_rule_applied": "Degree sequence uses P(n,r) for strength calculation",
            "total_possible_formations": house_analysis['total_placement_combinations'],
            "current_formation_probability": f"1/{house_analysis['total_placement_combinations']}"
        }
        
    else:
        analysis["conditions_failed"].append("Sun and Mercury not in same sign (Combination rule failed)")
        analysis["combination_analysis"]["formation_rule"] = "Basic requirement not met"
    
    return analysis

def calculate_planetary_positions_budha_aditya(birth_data):
    """Calculate Sun and Mercury positions for Budha Aditya analysis."""
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude")

    # Parse date and time
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Calculate planetary positions
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    # Get Sun position
    sun_pos, ret_sun = swe.calc_ut(jd_ut, swe.SUN, flag)
    if ret_sun < 0:
        raise Exception("Error calculating Sun position")
    sun_lon = sun_pos[0] % 360
    
    # Get Mercury position
    mercury_pos, ret_mercury = swe.calc_ut(jd_ut, swe.MERCURY, flag)
    if ret_mercury < 0:
        raise Exception("Error calculating Mercury position")
    mercury_lon = mercury_pos[0] % 360
    mercury_speed = mercury_pos[3]
    mercury_retrograde = 'R' if mercury_speed < 0 else ''

    # Calculate Ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = SIGNS[asc_sign_index]

    # Process Sun data
    sun_sign, sun_deg, sun_sign_index = longitude_to_sign(sun_lon)
    sun_house = get_house(sun_lon, asc_sign_index)
    sun_data = {
        'sign': sun_sign,
        'degrees': format_dms(sun_deg),
        'longitude': sun_lon,
        'house': sun_house
    }

    # Process Mercury data
    mercury_sign, mercury_deg, mercury_sign_index = longitude_to_sign(mercury_lon)
    mercury_house = get_house(mercury_lon, asc_sign_index)
    mercury_data = {
        'sign': mercury_sign,
        'degrees': format_dms(mercury_deg),
        'longitude': mercury_lon,
        'house': mercury_house,
        'retrograde': mercury_retrograde
    }

    # Ascendant data
    ascendant_data = {
        "sign": asc_sign,
        "degrees": format_dms(ascendant_lon % 30)
    }

    return sun_data, mercury_data, ascendant_data, ayanamsa_value