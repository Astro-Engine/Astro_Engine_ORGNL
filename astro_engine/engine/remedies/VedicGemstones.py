"""
Vedic Astrology Gemstone Calculations Module
Version: 3.0-ENHANCED
All calculation logic for gemstone recommendations
"""

from datetime import datetime, timedelta
import swisseph as swe
import os

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ============================================================================
# CONSTANTS - Vedic Astrology Data
# ============================================================================

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

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SIGN_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun', 5: 'Mercury',
    6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

# Exaltation data with exact degrees
EXALTATION_DATA = {
    'Sun': {'sign': 0, 'degree': 10},       # Aries 10°
    'Moon': {'sign': 1, 'degree': 3},       # Taurus 3°
    'Mars': {'sign': 9, 'degree': 28},      # Capricorn 28°
    'Mercury': {'sign': 5, 'degree': 15},   # Virgo 15°
    'Jupiter': {'sign': 3, 'degree': 5},    # Cancer 5°
    'Venus': {'sign': 11, 'degree': 27},    # Pisces 27°
    'Saturn': {'sign': 6, 'degree': 20}     # Libra 20°
}

# Debilitation is exactly opposite
DEBILITATION_DATA = {
    'Sun': {'sign': 6, 'degree': 10},       # Libra 10°
    'Moon': {'sign': 7, 'degree': 3},       # Scorpio 3°
    'Mars': {'sign': 3, 'degree': 28},      # Cancer 28°
    'Mercury': {'sign': 11, 'degree': 15},  # Pisces 15°
    'Jupiter': {'sign': 9, 'degree': 5},    # Capricorn 5°
    'Venus': {'sign': 5, 'degree': 27},     # Virgo 27°
    'Saturn': {'sign': 0, 'degree': 20}     # Aries 20°
}

OWN_SIGNS = {
    'Sun': [4], 'Moon': [3], 'Mars': [0, 7], 'Mercury': [2, 5],
    'Jupiter': [8, 11], 'Venus': [1, 6], 'Saturn': [9, 10]
}

# Planetary relationships
RELATIONSHIPS = {
    'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 'enemies': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
    'Moon': {'friends': ['Sun', 'Mercury'], 'enemies': [], 'neutral': ['Mars', 'Jupiter', 'Venus', 'Saturn']},
    'Mars': {'friends': ['Sun', 'Moon', 'Jupiter'], 'enemies': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
    'Mercury': {'friends': ['Sun', 'Venus'], 'enemies': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
    'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 'enemies': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
    'Venus': {'friends': ['Mercury', 'Saturn'], 'enemies': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
    'Saturn': {'friends': ['Mercury', 'Venus'], 'enemies': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
}

GEMSTONES = {
    'Sun': {
        'primary': 'Ruby (Manik)',
        'substitute': ['Red Garnet', 'Red Spinel'],
        'metal': 'Gold or Copper',
        'finger': 'Ring finger',
        'day': 'Sunday',
        'time': '1 hour after sunrise',
        'min_weight': '3-5 carats',
        'mantra': 'Om Hreem Suryaya Namaha (108 times)',
        'color': 'Deep Red'
    },
    'Moon': {
        'primary': 'Pearl (Moti)',
        'substitute': ['Moonstone'],
        'metal': 'Silver',
        'finger': 'Little finger',
        'day': 'Monday',
        'time': 'Evening (2 hours before sunset)',
        'min_weight': '5-7 carats',
        'mantra': 'Om Som Somaya Namaha (108 times)',
        'color': 'White/Milky'
    },
    'Mars': {
        'primary': 'Red Coral (Moonga)',
        'substitute': ['Red Carnelian'],
        'metal': 'Gold or Copper',
        'finger': 'Ring finger',
        'day': 'Tuesday',
        'time': '1 hour after sunrise',
        'min_weight': '5-7 carats',
        'mantra': 'Om Kram Kreem Kroum Sah Bhaumaya Namaha (108 times)',
        'color': 'Red'
    },
    'Mercury': {
        'primary': 'Emerald (Panna)',
        'substitute': ['Green Tourmaline', 'Peridot'],
        'metal': 'Gold',
        'finger': 'Little finger',
        'day': 'Wednesday',
        'time': '1 hour after sunrise',
        'min_weight': '3-5 carats',
        'mantra': 'Om Bram Breem Broum Sah Budhaya Namaha (108 times)',
        'color': 'Green'
    },
    'Jupiter': {
        'primary': 'Yellow Sapphire (Pukhraj)',
        'substitute': ['Yellow Topaz', 'Citrine'],
        'metal': 'Gold',
        'finger': 'Index finger',
        'day': 'Thursday',
        'time': '1 hour after sunrise',
        'min_weight': '5-7 carats',
        'mantra': 'Om Gram Greem Groum Sah Gurave Namaha (108 times)',
        'color': 'Yellow'
    },
    'Venus': {
        'primary': 'Diamond (Heera)',
        'substitute': ['White Sapphire', 'White Zircon'],
        'metal': 'Silver or Platinum',
        'finger': 'Middle finger',
        'day': 'Friday',
        'time': '1 hour after sunrise',
        'min_weight': '1-2 carats',
        'mantra': 'Om Dram Dreem Droum Sah Shukraya Namaha (108 times)',
        'color': 'White/Colorless'
    },
    'Saturn': {
        'primary': 'Blue Sapphire (Neelam)',
        'substitute': ['Amethyst', 'Blue Spinel'],
        'metal': 'Silver or Iron',
        'finger': 'Middle finger',
        'day': 'Saturday',
        'time': '1 hour after sunrise',
        'min_weight': '5-7 carats',
        'mantra': 'Om Pram Preem Proum Sah Shanaye Namaha (108 times)',
        'color': 'Blue',
        'warning': 'CRITICAL: Test for 3 days before permanent wearing! Remove immediately if negative effects occur.'
    },
    'Rahu': {
        'primary': 'Hessonite (Gomed)',
        'substitute': ['Spessartite Garnet'],
        'metal': 'Silver or Panchdhatu',
        'finger': 'Middle finger',
        'day': 'Saturday',
        'time': '1 hour after sunset',
        'min_weight': '5-7 carats',
        'mantra': 'Om Bhram Bhreem Bhroum Sah Rahave Namaha (108 times)',
        'color': 'Honey/Brown',
        'warning': 'Shadow planet - Use only under expert guidance'
    },
    'Ketu': {
        'primary': 'Cats Eye (Lehsunia)',
        'substitute': ['Chrysoberyl Cats Eye'],
        'metal': 'Silver or Panchdhatu',
        'finger': 'Middle finger',
        'day': 'Wednesday',
        'time': '1 hour after sunset',
        'min_weight': '5-7 carats',
        'mantra': 'Om Sram Sreem Sroum Sah Ketave Namaha (108 times)',
        'color': 'Greenish/Grey',
        'warning': 'Shadow planet - Use only under expert guidance'
    }
}

MINIMUM_SHADBALA = {
    'Sun': 390, 'Moon': 360, 'Mars': 300, 'Mercury': 420,
    'Jupiter': 390, 'Venus': 330, 'Saturn': 300, 'Rahu': 300, 'Ketu': 300
}

DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3

HOUSE_SIGNIFICATIONS = {
    1: "Self, personality, health, appearance, vitality, overall life direction",
    2: "Wealth, family, speech, food, accumulated assets, early childhood",
    3: "Siblings, courage, short travels, communication, skills, efforts",
    4: "Mother, home, property, vehicles, inner peace, education, happiness",
    5: "Children, creativity, intelligence, past life merit, romance, speculation",
    6: "Enemies, debts, diseases, service, competitions, obstacles, litigation",
    7: "Spouse, marriage, partnerships, business relations, legal bindings",
    8: "Longevity, sudden events, occult, inheritance, obstacles, transformation",
    9: "Father, luck, dharma, higher education, spirituality, long travels, fortune",
    10: "Career, profession, status, authority, reputation, fame, government",
    11: "Gains, income, friends, elder siblings, fulfillment of desires, aspirations",
    12: "Losses, expenses, foreign lands, spirituality, moksha, isolation, bed pleasures"
}

# Yoga Karaka definitions per ascendant
YOGA_KARAKA = {
    'Aries': 'Saturn',    # 10th + 11th lord
    'Taurus': 'Saturn',   # 9th + 10th lord
    'Gemini': 'Venus',    # 5th + 12th lord (weak yoga karaka)
    'Cancer': 'Mars',     # 5th + 10th lord
    'Leo': 'Mars',        # 4th + 9th lord
    'Virgo': 'Venus',     # 2nd + 9th lord (weak yoga karaka)
    'Libra': 'Saturn',    # 4th + 5th lord
    'Scorpio': None,      # No yoga karaka
    'Sagittarius': None,  # No yoga karaka
    'Capricorn': 'Venus', # 5th + 10th lord
    'Aquarius': 'Venus',  # 4th + 9th lord
    'Pisces': None        # No yoga karaka (Mars is debatable)
}

# ============================================================================
# HELPER FUNCTIONS - Date/Time Conversions
# ============================================================================

def gemstone_get_julian_day(date_str, time_str, timezone_offset):
    """Convert datetime to Julian Day (UTC)"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_utc = dt - timedelta(hours=timezone_offset)
        
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        
        jd = swe.julday(year, month, day, hour)
        return jd
    except Exception as e:
        raise ValueError(f"Invalid date/time format: {e}")

def gemstone_ordinal(n):
    """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    elif n % 10 == 1:
        suffix = 'st'
    elif n % 10 == 2:
        suffix = 'nd'
    elif n % 10 == 3:
        suffix = 'rd'
    else:
        suffix = 'th'
    return f"{n}{suffix}"

# ============================================================================
# PLANETARY CALCULATIONS
# ============================================================================

def gemstone_calculate_planetary_positions(jd):
    """Calculate sidereal positions of all planets using Lahiri ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    
    positions = {}
    
    for planet_name, planet_id in PLANETS.items():
        if planet_name == 'Ketu':
            # Ketu is 180° opposite to Rahu
            rahu_long = positions['Rahu']['longitude']
            ketu_long = (rahu_long + 180) % 360
            
            positions['Ketu'] = {
                'longitude': ketu_long,
                'sign': int(ketu_long / 30),
                'sign_name': SIGNS[int(ketu_long / 30)],
                'degree_in_sign': ketu_long % 30,
                'retrograde': False
            }
        else:
            result = swe.calc_ut(jd, planet_id)
            tropical_long = result[0][0]
            speed = result[0][3]
            
            # Convert to sidereal
            sidereal_long = (tropical_long - ayanamsa) % 360
            sign_num = int(sidereal_long / 30)
            degree_in_sign = sidereal_long % 30
            
            positions[planet_name] = {
                'longitude': sidereal_long,
                'sign': sign_num,
                'sign_name': SIGNS[sign_num],
                'degree_in_sign': degree_in_sign,
                'retrograde': speed < 0 if planet_name != 'Rahu' else speed > 0
            }
    
    return positions, ayanamsa

def gemstone_calculate_ascendant(jd, latitude, longitude):
    """Calculate Ascendant (Lagna) using sidereal zodiac"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    
    # Calculate houses (Placidus for tropical ascendant calculation)
    houses = swe.houses(jd, latitude, longitude, b'P')
    tropical_asc = houses[0][0]  # Tropical ascendant
    
    # Convert to sidereal
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    asc_sign = int(sidereal_asc / 30)
    
    return sidereal_asc, asc_sign

def gemstone_calculate_houses_whole_sign(asc_sign):
    """Calculate whole sign houses"""
    houses = {}
    for i in range(1, 13):
        house_sign = (asc_sign + i - 1) % 12
        houses[i] = {
            'sign': house_sign,
            'sign_name': SIGNS[house_sign],
            'lord': SIGN_LORDS[house_sign],
            'signification': HOUSE_SIGNIFICATIONS[i]
        }
    return houses

def gemstone_get_planet_house(planet_sign, asc_sign):
    """Get house number for a planet based on whole sign system"""
    house_num = ((planet_sign - asc_sign) % 12) + 1
    return house_num

# ============================================================================
# POSITIONAL STRENGTH CALCULATIONS
# ============================================================================

def gemstone_get_positional_strength(planet_name, sign, degree_in_sign):
    """
    Calculate positional strength based on dignity
    Returns: (strength_value, status_text)
    """
    # Check exaltation
    if planet_name in EXALTATION_DATA:
        exalt_data = EXALTATION_DATA[planet_name]
        if sign == exalt_data['sign']:
            # Deep exaltation point
            deep_exalt_degree = exalt_data['degree']
            distance = abs(degree_in_sign - deep_exalt_degree)
            
            if distance <= 3:
                strength = 100 - (distance * 1.3)  # Near deep exaltation
            else:
                strength = 100 - (distance * 0.7)  # Exalted but away from deep point
            
            return (round(strength, 2), 'Exalted')
    
    # Check debilitation
    if planet_name in DEBILITATION_DATA:
        debil_data = DEBILITATION_DATA[planet_name]
        if sign == debil_data['sign']:
            # Deep debilitation point
            deep_debil_degree = debil_data['degree']
            distance = abs(degree_in_sign - deep_debil_degree)
            
            if distance <= 3:
                strength = 10 + (distance * 1.3)  # Near deep debilitation
            else:
                strength = 10 + (distance * 0.7)  # Debilitated but away from deep point
            
            return (round(strength, 2), 'Debilitated')
    
    # Check own sign
    if planet_name in OWN_SIGNS and sign in OWN_SIGNS[planet_name]:
        return (75, 'Own Sign')
    
    # Check friend/enemy sign
    sign_lord = SIGN_LORDS[sign]
    
    if planet_name in RELATIONSHIPS:
        if sign_lord in RELATIONSHIPS[planet_name]['friends']:
            return (60, "Friend's Sign")
        elif sign_lord in RELATIONSHIPS[planet_name]['enemies']:
            return (30, "Enemy's Sign")
        else:
            return (50, "Neutral")
    
    return (50, "Neutral")

def gemstone_calculate_shadbala_simplified(planet_name, planet_data, asc_sign):
    """
    Simplified Shadbala calculation
    Focus on: Positional strength + House strength + Directional strength
    """
    base_strength = MINIMUM_SHADBALA.get(planet_name, 300)
    
    # 1. Positional Strength (Exaltation, Own Sign, etc.)
    pos_strength, _ = gemstone_get_positional_strength(
        planet_name,
        planet_data['sign'],
        planet_data['degree_in_sign']
    )
    positional_bala = (pos_strength / 100) * base_strength
    
    # 2. House Strength (based on house placement)
    house = gemstone_get_planet_house(planet_data['sign'], asc_sign)
    
    # Kendras (1,4,7,10) = strong, Trikonas (1,5,9) = strong
    # Upachaya (3,6,10,11) = moderate, Dusthana (6,8,12) = weak
    if house in [1, 10]:
        house_bala = 60
    elif house in [4, 7, 5, 9]:
        house_bala = 50
    elif house in [2, 11]:
        house_bala = 40
    elif house in [3]:
        house_bala = 35
    elif house in [6, 8, 12]:
        house_bala = 20
    else:
        house_bala = 30
    
    # 3. Directional Strength (Dig Bala) - simplified
    # Sun/Mars strong in 10th, Jupiter/Mercury in 1st, Saturn in 7th, Moon/Venus in 4th
    dig_bala = 30  # base
    if planet_name in ['Sun', 'Mars'] and house == 10:
        dig_bala = 60
    elif planet_name in ['Jupiter', 'Mercury'] and house == 1:
        dig_bala = 60
    elif planet_name == 'Saturn' and house == 7:
        dig_bala = 60
    elif planet_name in ['Moon', 'Venus'] and house == 4:
        dig_bala = 60
    
    # Total Shadbala (weighted)
    total_shadbala = (positional_bala * 0.5) + (house_bala * 0.3) + (dig_bala * 0.2)
    
    return round(total_shadbala, 2)

# ============================================================================
# FUNCTIONAL NATURE CLASSIFICATION
# ============================================================================

def gemstone_get_ruled_houses(planet_name, asc_sign):
    """Get houses ruled by a planet"""
    ruled_houses = []
    for house_num in range(1, 13):
        house_sign = (asc_sign + house_num - 1) % 12
        if SIGN_LORDS[house_sign] == planet_name:
            ruled_houses.append(house_num)
    return ruled_houses

def gemstone_classify_functional_nature(planet_name, ruled_houses, asc_sign):
    """
    Classify functional nature of planet based on house lordships
    Enhanced version with clear reasoning
    """
    if not ruled_houses:
        return ('NEUTRAL', [])
    
    reasons = []
    benefic_points = 0
    malefic_points = 0
    
    # Check for Yoga Karaka
    yoga_karaka_planet = YOGA_KARAKA.get(SIGNS[asc_sign])
    if yoga_karaka_planet == planet_name:
        reasons.append(f"Yoga Karaka for {SIGNS[asc_sign]} Ascendant")
        return ('YOGA_KARAKA', reasons)
    
    for house in ruled_houses:
        # Trikona (1, 5, 9) - Most benefic
        if house in [1, 5, 9]:
            if house == 1:
                reasons.append("Lagna lord (1st house)")
                benefic_points += 3
            elif house == 5:
                reasons.append("Lord of 5th (trikona)")
                benefic_points += 4
            elif house == 9:
                reasons.append("Lord of 9th (most auspicious)")
                benefic_points += 5
        
        # Kendra (1, 4, 7, 10)
        elif house in [4, 7, 10]:
            if house == 4:
                reasons.append("Lord of 4th (kendra)")
                benefic_points += 3
            elif house == 7:
                reasons.append("Lord of 7th (maraka)")
                malefic_points += 2
            elif house == 10:
                reasons.append("Lord of 10th (karma)")
                benefic_points += 3
        
        # Upachaya (3, 6, 10, 11)
        elif house == 3:
            reasons.append("Lord of 3rd (upachaya but mild malefic)")
            malefic_points += 1
        elif house == 11:
            reasons.append("Lord of 11th (gains but also upachaya)")
            benefic_points += 1
        
        # Dusthana (6, 8, 12) - Malefic
        elif house == 6:
            reasons.append("Lord of 6th (dusthana)")
            malefic_points += 4  # 6th is worst
        elif house == 8:
            reasons.append("Lord of 8th (dusthana)")
            malefic_points += 3
        elif house == 12:
            reasons.append("Lord of 12th (dusthana)")
            malefic_points += 2
        
        # Maraka (2, 7)
        elif house == 2:
            reasons.append("Lord of 2nd (maraka)")
            malefic_points += 2
    
    # Classification
    if benefic_points >= 4 and malefic_points <= 2:
        return ('HIGHLY_BENEFIC', reasons)
    elif benefic_points >= 2 and malefic_points <= 1:
        return ('BENEFIC', reasons)
    elif malefic_points >= 4:
        return ('MALEFIC', reasons)
    elif malefic_points >= 2:
        return ('MILD_MALEFIC', reasons)
    else:
        return ('NEUTRAL', reasons)

# ============================================================================
# VIMSHOTTARI DASHA CALCULATIONS
# ============================================================================

def gemstone_calculate_vimshottari_dasha(moon_longitude, birth_date):
    """Calculate Vimshottari Dasha timeline"""
    # Determine birth nakshatra
    nakshatra_span = 360 / 27
    birth_nakshatra = int(moon_longitude / nakshatra_span)
    nakshatra_lord = NAKSHATRA_LORDS[birth_nakshatra]
    
    # Calculate balance of dasha at birth
    nakshatra_start = birth_nakshatra * nakshatra_span
    traversed = moon_longitude - nakshatra_start
    traversed_fraction = traversed / nakshatra_span
    
    birth_dasha_lord = nakshatra_lord
    birth_dasha_years = DASHA_YEARS[birth_dasha_lord]
    balance_years = birth_dasha_years * (1 - traversed_fraction)
    
    # Build dasha timeline
    timeline = []
    birth_dt = datetime.strptime(birth_date, '%Y-%m-%d')
    
    # Balance dasha at birth
    balance_end = birth_dt + timedelta(days=balance_years * 365.25)
    timeline.append({
        'planet': birth_dasha_lord,
        'start_date': birth_dt.strftime('%Y-%m-%d'),
        'end_date': balance_end.strftime('%Y-%m-%d'),
        'duration_years': round(balance_years, 2),
        'status': 'balance_at_birth'
    })
    
    # Subsequent dashas
    current_date = balance_end
    start_index = DASHA_ORDER.index(birth_dasha_lord)
    
    for i in range(1, 9):  # Next 8 dashas
        dasha_planet = DASHA_ORDER[(start_index + i) % 9]
        dasha_years = DASHA_YEARS[dasha_planet]
        end_date = current_date + timedelta(days=dasha_years * 365.25)
        
        timeline.append({
            'planet': dasha_planet,
            'start_date': current_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'duration_years': dasha_years,
            'status': 'future'
        })
        
        current_date = end_date
    
    return timeline, birth_nakshatra

def gemstone_get_current_dasha(dasha_timeline):
    """Determine current Mahadasha"""
    today = datetime.now()
    
    for dasha in dasha_timeline:
        start = datetime.strptime(dasha['start_date'], '%Y-%m-%d')
        end = datetime.strptime(dasha['end_date'], '%Y-%m-%d')
        
        if start <= today <= end:
            dasha['status'] = 'current'
            return dasha
    
    return None

# ============================================================================
# ENHANCED GEMSTONE RECOMMENDATION ENGINE
# ============================================================================

def gemstone_recommend_gemstones_enhanced(planets_analysis, current_dasha, asc_sign, asc_lord, approach='balanced'):
    """
    Enhanced gemstone recommendation with multiple approaches
    
    approach options:
    - 'classical': Traditional rules (avoid all dusthana lords)
    - 'modern': Support dasha lords even if dusthana
    - 'balanced': Balanced approach (default)
    """
    recommendations = []
    avoid_list = []
    compatibility_notes = []
    
    current_dasha_lord = current_dasha['planet'] if current_dasha else None
    
    # Get all recommended planets with reasoning
    for planet_name, analysis in planets_analysis.items():
        # Skip shadow planets unless special conditions
        if planet_name in ['Rahu', 'Ketu']:
            continue
        
        functional_nature = analysis['functional_nature']
        is_weak = analysis['is_weak']
        pos_status = analysis['positional_status']
        shadbala = analysis['shadbala']
        ruled_houses = analysis['ruled_houses']
        
        # ===== EXCLUSION RULES =====
        
        # Rule 1: NEVER recommend exalted planets
        if pos_status == 'Exalted':
            avoid_list.append({
                'planet': planet_name,
                'reason': f"EXALTED in {analysis['position']['sign_name']} - Already at maximum strength",
                'gemstone': GEMSTONES[planet_name]['primary'],
                'warning_level': 'CRITICAL'
            })
            continue
        
        # Rule 2: NEVER recommend planets in own sign (unless very weak)
        if pos_status == 'Own Sign' and not is_weak:
            avoid_list.append({
                'planet': planet_name,
                'reason': f"In Own Sign ({analysis['position']['sign_name']}) with good strength ({analysis['strength_percentage']}%)",
                'gemstone': GEMSTONES[planet_name]['primary'],
                'warning_level': 'HIGH'
            })
            continue
        
        # ===== RECOMMENDATION LOGIC =====
        
        priority = 0
        rec_type = None
        warnings = []
        
        # YOGA KARAKA - Highest Priority (if weak)
        if functional_nature == 'YOGA_KARAKA' and is_weak:
            priority = 1
            rec_type = 'YOGA_KARAKA'
            
        # HIGHLY BENEFIC - High Priority
        elif functional_nature == 'HIGHLY_BENEFIC' and is_weak:
            priority = 2
            rec_type = 'HIGHLY_BENEFIC'
        
        # LAGNA LORD - Important (if weak)
        elif planet_name == asc_lord and is_weak:
            priority = 3
            rec_type = 'LAGNA_LORD'
        
        # BENEFIC - Good to strengthen
        elif functional_nature == 'BENEFIC' and is_weak:
            priority = 4
            rec_type = 'BENEFIC'
        
        # NEUTRAL but weak - Can be considered
        elif functional_nature == 'NEUTRAL' and is_weak:
            # Check if ascendant lord
            if planet_name == asc_lord:
                priority = 3
                rec_type = 'LAGNA_LORD'
            else:
                priority = 5
                rec_type = 'NEUTRAL'
        
        # MALEFIC or MILD_MALEFIC - Special handling
        elif functional_nature in ['MALEFIC', 'MILD_MALEFIC']:
            
            # Check if 6th lord specifically
            is_sixth_lord = 6 in ruled_houses
            is_eighth_lord = 8 in ruled_houses
            is_twelfth_lord = 12 in ruled_houses
            
            # Classical approach: Avoid all dusthana lords
            if approach == 'classical':
                avoid_list.append({
                    'planet': planet_name,
                    'reason': f"Functional MALEFIC (rules: {', '.join([f'{gemstone_ordinal(h)}' for h in ruled_houses])}) - Classical approach avoids dusthana lords",
                    'gemstone': GEMSTONES[planet_name]['primary'],
                    'warning_level': 'HIGH',
                    'ruled_houses': ruled_houses
                })
                continue
            
            # Modern/Balanced approach: Consider if current dasha lord
            elif planet_name == current_dasha_lord:
                priority = 6  # Lower priority
                rec_type = 'DASHA_LORD_MALEFIC'
                
                # Add strong warnings
                warnings.append("⚠️ CAUTION: This planet is a functional malefic")
                
                if is_sixth_lord:
                    warnings.append("🚨 CRITICAL: Rules 6th house (enemies, diseases, litigation)")
                    warnings.append("❗ Classical texts advise AGAINST strengthening 6th lord")
                    warnings.append("💡 Modern approach: Wear only during favorable sub-periods")
                    warnings.append("👨‍⚕️ MANDATORY: Consult qualified astrologer before wearing")
                
                if is_eighth_lord:
                    warnings.append("⚠️ Rules 8th house (obstacles, sudden events)")
                    warnings.append("💡 Wear only during 8th lord sub-periods with caution")
                
                if is_twelfth_lord:
                    warnings.append("⚠️ Rules 12th house (losses, expenses)")
            else:
                # Not dasha lord - avoid
                avoid_list.append({
                    'planet': planet_name,
                    'reason': f"Functional {functional_nature} (rules: {', '.join([f'{gemstone_ordinal(h)}' for h in ruled_houses])}) and NOT current dasha lord",
                    'gemstone': GEMSTONES[planet_name]['primary'],
                    'warning_level': 'MEDIUM',
                    'ruled_houses': ruled_houses
                })
                continue
        
        # If we have a priority, add to recommendations
        if priority > 0:
            gem_info = GEMSTONES[planet_name].copy()
            
            # Add special warnings
            if planet_name == 'Saturn':
                warnings.insert(0, "🚨 BLUE SAPPHIRE WARNING: MUST test for 3 days before permanent wearing!")
                warnings.append("❗ Remove immediately if you experience: health issues, financial loss, relationship problems")
            
            recommendation = {
                'planet': planet_name,
                'priority': priority,
                'recommendation_type': rec_type,
                'reason': f"{rec_type.replace('_', ' ').title()} - {analysis['functional_reasons'][0] if analysis['functional_reasons'] else 'Weak planet'}",
                'strength': shadbala,
                'gemstone_info': gem_info,
                'benefits': f"Improves: {', '.join(analysis['house_significations'])}",
                'warnings': warnings
            }
            
            recommendations.append(recommendation)
    
    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'])
    
    # Add compatibility notes
    compatibility_notes = gemstone_generate_compatibility_notes(recommendations)
    
    return recommendations, avoid_list, compatibility_notes

def gemstone_generate_compatibility_notes(recommendations):
    """Generate gemstone compatibility warnings"""
    notes = []
    
    recommended_planets = [r['planet'] for r in recommendations]
    
    # Check for enemy combinations
    for i, planet1 in enumerate(recommended_planets):
        for planet2 in recommended_planets[i+1:]:
            if planet1 in RELATIONSHIPS and planet2 in RELATIONSHIPS[planet1]['enemies']:
                notes.append(f"✗ {planet1} ({GEMSTONES[planet1]['primary']}) + {planet2} ({GEMSTONES[planet2]['primary']}) = Not Compatible (enemy planets)")
            elif planet1 in RELATIONSHIPS and planet2 in RELATIONSHIPS[planet1]['friends']:
                notes.append(f"✓ {planet1} ({GEMSTONES[planet1]['primary']}) + {planet2} ({GEMSTONES[planet2]['primary']}) = Compatible")
    
    # Add general warnings
    if any(r['planet'] == 'Saturn' for r in recommendations):
        notes.append("⚠ Saturn (Blue Sapphire) should ALWAYS be tested for 3 days first")
    
    notes.append("⚠ Never wear gemstones of exalted planets - they're already at maximum strength")
    notes.append("⚠ Never wear conflicting gemstones (enemy planets) simultaneously")
    notes.append("💡 Consult a qualified Vedic astrologer for personalized timing and combinations")
    
    return notes