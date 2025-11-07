# spiritual_yoga_calc.py
import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Comprehensive Planet dignity definitions
DIGNITIES = {
    'Sun': {'own': ['Leo'], 'exalted': ['Aries'], 'debilitated': ['Libra'], 'mooltrikona': ['Leo']},
    'Moon': {'own': ['Cancer'], 'exalted': ['Taurus'], 'debilitated': ['Scorpio'], 'mooltrikona': ['Taurus']},
    'Mars': {'own': ['Aries', 'Scorpio'], 'exalted': ['Capricorn'], 'debilitated': ['Cancer'], 'mooltrikona': ['Aries']},
    'Mercury': {'own': ['Gemini', 'Virgo'], 'exalted': ['Virgo'], 'debilitated': ['Pisces'], 'mooltrikona': ['Virgo']},
    'Jupiter': {'own': ['Sagittarius', 'Pisces'], 'exalted': ['Cancer'], 'debilitated': ['Capricorn'], 'mooltrikona': ['Sagittarius']},
    'Venus': {'own': ['Taurus', 'Libra'], 'exalted': ['Pisces'], 'debilitated': ['Virgo'], 'mooltrikona': ['Libra']},
    'Saturn': {'own': ['Capricorn', 'Aquarius'], 'exalted': ['Libra'], 'debilitated': ['Aries'], 'mooltrikona': ['Aquarius']},
    'Rahu': {'exalted': ['Gemini', 'Virgo'], 'debilitated': ['Sagittarius', 'Pisces']},
    'Ketu': {'exalted': ['Sagittarius', 'Pisces'], 'debilitated': ['Gemini', 'Virgo']}
}

# House lordships
HOUSE_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Planetary aspects (house positions from planet)
ASPECTS = {
    'Sun': [7], 'Moon': [7], 'Mercury': [7], 'Venus': [7],
    'Mars': [4, 7, 8], 'Jupiter': [5, 7, 9], 'Saturn': [3, 7, 10],
    'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
}

# Benefic and Malefic classifications
NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Mercury', 'Moon']
NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']


def get_house(lon, asc_sign_index):
    """Calculate house number using Whole Sign system"""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign"""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds"""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_planet_dignity(planet_name, sign):
    """Check planet dignity in sign"""
    if planet_name in DIGNITIES:
        dignities = DIGNITIES[planet_name]
        if sign in dignities.get('exalted', []):
            return 'exalted'
        elif sign in dignities.get('own', []):
            return 'own'
        elif sign in dignities.get('mooltrikona', []):
            return 'mooltrikona'
        elif sign in dignities.get('debilitated', []):
            return 'debilitated'
    return 'neutral'

def get_house_lords(house_signs):
    """Calculate house lordships"""
    house_lords = {}
    for house_num in range(1, 13):
        house_sign = house_signs[f"House {house_num}"]["sign"]
        house_lords[house_num] = HOUSE_LORDS[house_sign]
    return house_lords

def is_planet_in_house(planet_positions, planet_name, house_number):
    """Check if planet is in specific house"""
    return planet_positions[planet_name]['house'] == house_number

def get_planets_in_house(planet_positions, house_number):
    """Get all planets in a specific house"""
    planets_in_house = []
    for planet, data in planet_positions.items():
        if data['house'] == house_number:
            planets_in_house.append(planet)
    return planets_in_house

def is_conjunction(planet_positions, planet1, planet2, orb=10):
    """Check if two planets are in conjunction within orb"""
    if planet_positions[planet1]['house'] != planet_positions[planet2]['house']:
        return False
    
    lon1 = planet_positions[planet1]['longitude']
    lon2 = planet_positions[planet2]['longitude']
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb

def calculate_planetary_strength(planet_positions, planet_name):
    """Calculate comprehensive planetary strength score"""
    planet_data = planet_positions[planet_name]
    sign = planet_data['sign']
    dignity = get_planet_dignity(planet_name, sign)
    house = planet_data['house']
    
    strength_score = 0
    
    # Dignity strength
    if dignity == 'exalted':
        strength_score += 5
    elif dignity == 'mooltrikona':
        strength_score += 4
    elif dignity == 'own':
        strength_score += 3
    elif dignity == 'neutral':
        strength_score += 2
    elif dignity == 'debilitated':
        strength_score += 1
    
    # House strength
    if house in [1, 10]:  # Angular houses (strongest)
        strength_score += 3
    elif house in [4, 7]:  # Angular houses
        strength_score += 2
    elif house in [5, 9]:  # Trinal houses
        strength_score += 2
    elif house in [2, 11]:  # Succedent houses
        strength_score += 1
    # Houses 3, 6, 8, 12 get no bonus
    
    # Retrograde penalty (except for outer planets where it can be beneficial)
    if planet_data.get('retrograde') == 'R' and planet_name not in ['Jupiter', 'Saturn']:
        strength_score -= 1
    
    return max(strength_score, 1)  # Minimum score of 1

def get_planet_aspects(planet_positions, planet_name):
    """Get houses aspected by a planet"""
    planet_house = planet_positions[planet_name]['house']
    aspect_houses = []
    
    for aspect in ASPECTS.get(planet_name, [7]):
        aspected_house = ((planet_house + aspect - 2) % 12) + 1
        aspect_houses.append(aspected_house)
    
    return aspect_houses

def does_planet_aspect_house(planet_positions, planet_name, target_house):
    """Check if planet aspects specific house"""
    aspected_houses = get_planet_aspects(planet_positions, planet_name)
    return target_house in aspected_houses

def detect_sanyasa_yoga(planet_positions, house_signs):
    """Detect all types of Sanyasa Yoga with comprehensive rules"""
    sanyasa_yogas = []
    house_lords = get_house_lords(house_signs)
    
    # Type 1: Classical Sanyasa - 4+ planets in one house
    for house_num in range(1, 13):
        planets = get_planets_in_house(planet_positions, house_num)
        if len(planets) >= 4:
            # Determine strongest planet by comprehensive strength
            strongest_planet = None
            max_strength = 0
            for planet in planets:
                strength = calculate_planetary_strength(planet_positions, planet)
                if strength > max_strength:
                    max_strength = strength
                    strongest_planet = planet
            
            # Check for combust planets (yoga breaker)
            sun_in_house = 'Sun' in planets
            combust_planets = []
            if sun_in_house:
                sun_lon = planet_positions['Sun']['longitude']
                for planet in planets:
                    if planet != 'Sun':
                        planet_lon = planet_positions[planet]['longitude']
                        diff = abs(sun_lon - planet_lon)
                        if diff > 180:
                            diff = 360 - diff
                        if diff <= 8:  # Combustion orb
                            combust_planets.append(planet)
            
            # Check 10th lord involvement (strengthener)
            tenth_lord = house_lords[10]
            tenth_lord_involved = tenth_lord in planets
            
            # Determine yoga quality
            is_moksha_granting = house_num in [1, 4, 5, 7, 9, 10]  # Kendra + Trikona
            is_yogabhrashta = house_num == 8  # 8th house breaks yoga
            is_combust_broken = strongest_planet in combust_planets
            
            yoga_strength = 'Strong'
            if is_combust_broken:
                yoga_strength = 'Broken (Combust)'
            elif is_yogabhrashta:
                yoga_strength = 'Yogabhrashta (8th house)'
            elif not is_moksha_granting:
                yoga_strength = 'Weak'
            elif tenth_lord_involved:
                yoga_strength = 'Very Strong (10th lord involved)'
            
            sanyasa_yogas.append({
                'type': 'Classical Sanyasa Yoga',
                'house': house_num,
                'house_sign': house_signs[f"House {house_num}"]["sign"],
                'planets_involved': planets,
                'strongest_planet': strongest_planet,
                'strongest_planet_effects': get_sanyasa_planet_effects(strongest_planet),
                'tenth_lord_involved': tenth_lord_involved,
                'combust_planets': combust_planets,
                'moksha_potential': is_moksha_granting,
                'yogabhrashta': is_yogabhrashta,
                'strength': yoga_strength
            })
    
    # Type 2: Saturn-Moon Sanyasa configurations
    moon_house = planet_positions['Moon']['house']
    saturn_house = planet_positions['Saturn']['house']
    mars_house = planet_positions['Mars']['house']
    
    # Check Saturn aspects Moon
    saturn_aspects_moon = does_planet_aspect_house(planet_positions, 'Saturn', moon_house)
    mars_aspects_moon = does_planet_aspect_house(planet_positions, 'Mars', moon_house)
    
    if saturn_aspects_moon and mars_aspects_moon:
        sanyasa_yogas.append({
            'type': 'Saturn-Mars-Moon Sanyasa Yoga',
            'description': 'Saturn and Mars both aspecting Moon',
            'moon_house': moon_house,
            'saturn_house': saturn_house,
            'mars_house': mars_house,
            'strength': 'Strong'
        })
    elif saturn_aspects_moon:
        sanyasa_yogas.append({
            'type': 'Saturn-Moon Sanyasa Yoga',
            'description': 'Saturn aspecting Moon indicates spiritual detachment',
            'moon_house': moon_house,
            'saturn_house': saturn_house,
            'strength': 'Medium'
        })
    
    # Type 3: Moon in drekkana of Saturn
    moon_sign = planet_positions['Moon']['sign']
    moon_degrees = planet_positions['Moon']['degrees']
    
    # Each sign has 3 drekkanas (0-10°, 10-20°, 20-30°)
    if moon_sign in ['Capricorn', 'Aquarius']:  # Saturn's signs
        drekkana = int(moon_degrees // 10) + 1
        if drekkana in [1, 2, 3]:  # Any drekkana in Saturn's sign
            sanyasa_yogas.append({
                'type': 'Moon in Saturn Drekkana Sanyasa',
                'description': 'Moon in drekkana of Saturn',
                'moon_sign': moon_sign,
                'moon_degrees': moon_degrees,
                'drekkana': drekkana,
                'strength': 'Medium'
            })
    
    # Type 4: Scholarly Sanyasa (Jupiter in 9th with Saturn aspecting Lagna, Moon, Jupiter)
    jupiter_house = planet_positions['Jupiter']['house']
    if jupiter_house == 9:
        lagna_aspected = does_planet_aspect_house(planet_positions, 'Saturn', 1)
        jupiter_aspected = does_planet_aspect_house(planet_positions, 'Saturn', jupiter_house)
        
        if lagna_aspected and saturn_aspects_moon and jupiter_aspected:
            sanyasa_yogas.append({
                'type': 'Scholarly Sanyasa Yoga',
                'description': 'Jupiter in 9th with Saturn aspecting Lagna, Moon, and Jupiter',
                'jupiter_house': jupiter_house,
                'saturn_aspects': ['Lagna', 'Moon', 'Jupiter'],
                'strength': 'Very Strong'
            })
    
    return sanyasa_yogas

def get_sanyasa_planet_effects(strongest_planet):
    """Get effects based on strongest planet in Sanyasa Yoga"""
    effects = {
        'Sun': 'High morals, intellectual prowess, severe practices in remote places',
        'Moon': 'Seclusion focused on scripture study and contemplation',
        'Mercury': 'Easily influenced by others philosophy, scholarly pursuits',
        'Mars': 'Red-colored clothes, struggles with temper control, warrior ascetic',
        'Jupiter': 'Complete control over senses, traditional guru figure',
        'Venus': 'Wandering mendicant lifestyle, artistic spiritual expression',
        'Saturn': 'Exceedingly severe practices, extreme austerity'
    }
    return effects.get(strongest_planet, 'General renunciation tendencies')

def detect_vishnu_yoga(planet_positions, house_signs):
    """Detect Vishnu Yoga with comprehensive strength analysis"""
    house_lords = get_house_lords(house_signs)
    vishnu_yogas = []
    
    # Primary formation: 9th and 10th lords in 2nd house (Dharma-Karma Adhipati Yoga)
    ninth_lord = house_lords[9]
    tenth_lord = house_lords[10]
    
    ninth_lord_house = planet_positions[ninth_lord]['house']
    tenth_lord_house = planet_positions[tenth_lord]['house']
    
    if ninth_lord_house == 2 and tenth_lord_house == 2:
        # Check Shadbala strength requirements
        ninth_lord_strength = calculate_planetary_strength(planet_positions, ninth_lord)
        tenth_lord_strength = calculate_planetary_strength(planet_positions, tenth_lord)
        
        # Check if planets are conjunct (stronger yoga)
        lords_conjunct = is_conjunction(planet_positions, ninth_lord, tenth_lord, orb=10)
        
        # Check navamsha strength (simplified - checking dignity)
        ninth_lord_dignity = get_planet_dignity(ninth_lord, planet_positions[ninth_lord]['sign'])
        tenth_lord_dignity = get_planet_dignity(tenth_lord, planet_positions[tenth_lord]['sign'])
        
        navamsha_strong = ninth_lord_dignity in ['exalted', 'own', 'mooltrikona'] and \
                         tenth_lord_dignity in ['exalted', 'own', 'mooltrikona']
        
        total_strength = ninth_lord_strength + tenth_lord_strength
        
        yoga_strength = 'Strong'
        if total_strength >= 8 and lords_conjunct and navamsha_strong:
            yoga_strength = 'Very Strong'
        elif total_strength >= 6 and (lords_conjunct or navamsha_strong):
            yoga_strength = 'Strong'
        elif total_strength >= 4:
            yoga_strength = 'Medium'
        else:
            yoga_strength = 'Weak'
        
        vishnu_yogas.append({
            'type': 'Primary Vishnu Yoga (Dharma-Karma Adhipati)',
            'description': '9th and 10th lords in 2nd house',
            'ninth_lord': ninth_lord,
            'tenth_lord': tenth_lord,
            'house': 2,
            'lords_conjunct': lords_conjunct,
            'ninth_lord_strength': ninth_lord_strength,
            'tenth_lord_strength': tenth_lord_strength,
            'ninth_lord_dignity': ninth_lord_dignity,
            'tenth_lord_dignity': tenth_lord_dignity,
            'total_strength_score': total_strength,
            'navamsha_support': navamsha_strong,
            'strength': yoga_strength,
            'effects': ['Long life', 'Good health', 'Wealth', 'Spiritual devotion', 'Protection from enemies']
        })
    
    # Alternative formation: Venus in 1st, Jupiter in 10th, Sun+Mars in 11th
    venus_house = planet_positions['Venus']['house']
    jupiter_house = planet_positions['Jupiter']['house']
    sun_house = planet_positions['Sun']['house']
    mars_house = planet_positions['Mars']['house']
    
    if venus_house == 1 and jupiter_house == 10 and sun_house == 11 and mars_house == 11:
        # Check if Sun and Mars are conjunct for stronger effect
        sun_mars_conjunct = is_conjunction(planet_positions, 'Sun', 'Mars', orb=8)
        
        vishnu_yogas.append({
            'type': 'Alternative Vishnu Yoga',
            'description': 'Venus in 1st, Jupiter in 10th, Sun and Mars in 11th',
            'planet_positions': {
                'Venus': {'house': 1, 'strength': calculate_planetary_strength(planet_positions, 'Venus')},
                'Jupiter': {'house': 10, 'strength': calculate_planetary_strength(planet_positions, 'Jupiter')},
                'Sun': {'house': 11, 'strength': calculate_planetary_strength(planet_positions, 'Sun')},
                'Mars': {'house': 11, 'strength': calculate_planetary_strength(planet_positions, 'Mars')}
            },
            'sun_mars_conjunct': sun_mars_conjunct,
            'strength': 'Very Strong' if sun_mars_conjunct else 'Strong',
            'effects': ['Fame in foreign countries', 'Authority', 'Spiritual inclination', 'Extensive travel', 'Eloquent speech']
        })
    
    return vishnu_yogas

def detect_spiritual_wealth_yogas(planet_positions, house_signs):
    """Detect comprehensive spiritual wealth and growth yogas"""
    spiritual_yogas = []
    house_lords = get_house_lords(house_signs)
    
    # 1. Moksha Trikona Yoga (4th, 8th, 12th house lords connected)
    fourth_lord = house_lords[4]
    eighth_lord = house_lords[8]
    twelfth_lord = house_lords[12]
    
    moksha_lords = [fourth_lord, eighth_lord, twelfth_lord]
    moksha_connections = []
    
    # Check all possible connections
    if is_conjunction(planet_positions, fourth_lord, eighth_lord):
        moksha_connections.append(f"{fourth_lord}-{eighth_lord} conjunction")
    if is_conjunction(planet_positions, fourth_lord, twelfth_lord):
        moksha_connections.append(f"{fourth_lord}-{twelfth_lord} conjunction")
    if is_conjunction(planet_positions, eighth_lord, twelfth_lord):
        moksha_connections.append(f"{eighth_lord}-{twelfth_lord} conjunction")
    
    # Check mutual aspects
    for lord1, lord2 in [(fourth_lord, eighth_lord), (fourth_lord, twelfth_lord), (eighth_lord, twelfth_lord)]:
        lord1_house = planet_positions[lord1]['house']
        lord2_house = planet_positions[lord2]['house']
        if does_planet_aspect_house(planet_positions, lord1, lord2_house):
            moksha_connections.append(f"{lord1} aspects {lord2}")
        elif does_planet_aspect_house(planet_positions, lord2, lord1_house):
            moksha_connections.append(f"{lord2} aspects {lord1}")
    
    if moksha_connections:
        spiritual_yogas.append({
            'type': 'Moksha Trikona Yoga',
            'description': 'Connection between 4th, 8th, 12th house lords (liberation houses)',
            'lords_involved': moksha_lords,
            'connections': moksha_connections,
            'connection_count': len(moksha_connections),
            'strength': 'Very Strong' if len(moksha_connections) >= 3 else 'Strong' if len(moksha_connections) >= 2 else 'Medium'
        })
    
    # 2. Dharma Yoga (9th lord strong and well-placed)
    ninth_lord = house_lords[9]
    ninth_lord_house = planet_positions[ninth_lord]['house']
    ninth_lord_strength = calculate_planetary_strength(planet_positions, ninth_lord)
    ninth_lord_dignity = get_planet_dignity(ninth_lord, planet_positions[ninth_lord]['sign'])
    
    if ninth_lord_strength >= 4 and ninth_lord_house in [1, 4, 5, 7, 9, 10]:
        spiritual_yogas.append({
            'type': 'Dharma Yoga',
            'description': '9th lord strong in kendra/trikona (righteous path)',
            'ninth_lord': ninth_lord,
            'house': ninth_lord_house,
            'dignity': ninth_lord_dignity,
            'strength_score': ninth_lord_strength,
            'strength': 'Very Strong' if ninth_lord_strength >= 6 else 'Strong'
        })
    
    # 3. Saraswati Yoga (Jupiter, Venus, Mercury in kendras in own/exaltation)
    jupiter_house = planet_positions['Jupiter']['house']
    venus_house = planet_positions['Venus']['house']
    mercury_house = planet_positions['Mercury']['house']
    
    jupiter_dignity = get_planet_dignity('Jupiter', planet_positions['Jupiter']['sign'])
    venus_dignity = get_planet_dignity('Venus', planet_positions['Venus']['sign'])
    mercury_dignity = get_planet_dignity('Mercury', planet_positions['Mercury']['sign'])
    
    kendras = [1, 4, 7, 10]
    saraswati_planets = []
    
    if jupiter_house in kendras and jupiter_dignity in ['own', 'exalted']:
        saraswati_planets.append({'planet': 'Jupiter', 'house': jupiter_house, 'dignity': jupiter_dignity})
    if venus_house in kendras and venus_dignity in ['own', 'exalted']:
        saraswati_planets.append({'planet': 'Venus', 'house': venus_house, 'dignity': venus_dignity})
    if mercury_house in kendras and mercury_dignity in ['own', 'exalted']:
        saraswati_planets.append({'planet': 'Mercury', 'house': mercury_house, 'dignity': mercury_dignity})
    
    if len(saraswati_planets) >= 2:
        spiritual_yogas.append({
            'type': 'Saraswati Yoga',
            'description': 'Jupiter, Venus, Mercury in kendras in own/exaltation (wisdom and learning)',
            'qualifying_planets': saraswati_planets,
            'planet_count': len(saraswati_planets),
            'strength': 'Very Strong' if len(saraswati_planets) == 3 else 'Strong'
        })
    
    # 4. Hamsa Yoga (Jupiter in kendra in own/exaltation)
    if jupiter_house in kendras and jupiter_dignity in ['own', 'exalted']:
        spiritual_yogas.append({
            'type': 'Hamsa Yoga (Pancha Mahapurusha)',
            'description': 'Jupiter in kendra in own sign or exaltation (spiritual wisdom)',
            'planet': 'Jupiter',
            'house': jupiter_house,
            'sign': planet_positions['Jupiter']['sign'],
            'dignity': jupiter_dignity,
            'strength': 'Very Strong' if jupiter_dignity == 'exalted' else 'Strong'
        })
    
    # 5. Brahma Yoga (Jupiter aspecting lagna from own/exaltation)
    if jupiter_dignity in ['own', 'exalted'] and does_planet_aspect_house(planet_positions, 'Jupiter', 1):
        spiritual_yogas.append({
            'type': 'Brahma Yoga',
            'description': 'Jupiter in own/exaltation aspecting lagna (divine wisdom)',
            'jupiter_house': jupiter_house,
            'jupiter_sign': planet_positions['Jupiter']['sign'],
            'jupiter_dignity': jupiter_dignity,
            'aspects_lagna': True,
            'strength': 'Very Strong' if jupiter_dignity == 'exalted' else 'Strong'
        })
    
    # 6. Pandit Yoga (Mercury-Jupiter conjunction)
    if is_conjunction(planet_positions, 'Mercury', 'Jupiter', orb=8):
        mercury_house = planet_positions['Mercury']['house']
        mercury_strength = calculate_planetary_strength(planet_positions, 'Mercury')
        jupiter_strength = calculate_planetary_strength(planet_positions, 'Jupiter')
        
        # Check if conjunction is in good houses
        good_houses = [1, 2, 4, 5, 7, 9, 10, 11]
        in_good_house = mercury_house in good_houses
        
        conjunction_strength = (mercury_strength + jupiter_strength) / 2
        
        spiritual_yogas.append({
            'type': 'Pandit Yoga',
            'description': 'Mercury and Jupiter conjunction (scholarly spirituality)',
            'house': mercury_house,
            'mercury_strength': mercury_strength,
            'jupiter_strength': jupiter_strength,
            'conjunction_strength': conjunction_strength,
            'in_good_house': in_good_house,
            'strength': 'Very Strong' if conjunction_strength >= 5 and in_good_house else 'Strong' if conjunction_strength >= 4 else 'Medium'
        })
    
    # 7. Tapasya Yoga (Saturn aspecting 9th house/lord)
    saturn_house = planet_positions['Saturn']['house']
    saturn_aspects_ninth_house = does_planet_aspect_house(planet_positions, 'Saturn', 9)
    saturn_aspects_ninth_lord = does_planet_aspect_house(planet_positions, 'Saturn', ninth_lord_house)
    
    if saturn_aspects_ninth_house or saturn_aspects_ninth_lord:
        spiritual_yogas.append({
            'type': 'Tapasya Yoga',
            'description': 'Saturn aspecting 9th house or 9th lord (spiritual discipline)',
            'saturn_house': saturn_house,
            'aspects_ninth_house': saturn_aspects_ninth_house,
            'aspects_ninth_lord': saturn_aspects_ninth_lord,
            'ninth_lord': ninth_lord,
            'ninth_lord_house': ninth_lord_house,
            'strength': 'Strong' if saturn_aspects_ninth_house else 'Medium'
        })
    
    # 8. Guru Chandal Yoga (Jupiter-Ketu conjunction - can be spiritual when positive)
    if is_conjunction(planet_positions, 'Jupiter', 'Ketu', orb=8):
        jupiter_ketu_house = planet_positions['Jupiter']['house']
        
        # Positive in 9th, 12th houses or if Jupiter is very strong
        jupiter_strength = calculate_planetary_strength(planet_positions, 'Jupiter')
        is_positive = jupiter_ketu_house in [9, 12] or jupiter_strength >= 5
        
        if is_positive:
            spiritual_yogas.append({
                'type': 'Guru Chandal Yoga (Positive)',
                'description': 'Jupiter-Ketu conjunction in favorable position (mystical wisdom)',
                'house': jupiter_ketu_house,
                'jupiter_strength': jupiter_strength,
                'positive_placement': jupiter_ketu_house in [9, 12],
                'strength': 'Strong' if jupiter_strength >= 5 else 'Medium'
            })
    
    # 9. Spiritual Raja Yoga (9th lord and lagna lord conjunction/aspect)
    lagna_lord = house_lords[1]
    lagna_lord_house = planet_positions[lagna_lord]['house']
    
    if is_conjunction(planet_positions, lagna_lord, ninth_lord, orb=10):
        spiritual_yogas.append({
            'type': 'Spiritual Raja Yoga',
            'description': '1st and 9th lords conjunction (spiritual leadership)',
            'lagna_lord': lagna_lord,
            'ninth_lord': ninth_lord,
            'conjunction_house': lagna_lord_house,
            'strength': 'Very Strong'
        })
    elif does_planet_aspect_house(planet_positions, lagna_lord, ninth_lord_house) or \
         does_planet_aspect_house(planet_positions, ninth_lord, lagna_lord_house):
        spiritual_yogas.append({
            'type': 'Spiritual Raja Yoga (Aspect)',
            'description': '1st and 9th lords in mutual aspect (spiritual authority)',
            'lagna_lord': lagna_lord,
            'ninth_lord': ninth_lord,
            'lagna_lord_house': lagna_lord_house,
            'ninth_lord_house': ninth_lord_house,
            'strength': 'Strong'
        })
    
    # 10. Kemadruma Yoga Cancellation (Moon with planets on both sides - spiritual protection)
    moon_house = planet_positions['Moon']['house']
    second_house_from_moon = (moon_house % 12) + 1
    twelfth_house_from_moon = ((moon_house - 2) % 12) + 1
    
    planets_second = get_planets_in_house(planet_positions, second_house_from_moon)
    planets_twelfth = get_planets_in_house(planet_positions, twelfth_house_from_moon)
    
    # Remove Sun, Rahu, Ketu as they don't cancel Kemadruma effectively
    planets_second = [p for p in planets_second if p not in ['Sun', 'Rahu', 'Ketu']]
    planets_twelfth = [p for p in planets_twelfth if p not in ['Sun', 'Rahu', 'Ketu']]
    
    if planets_second and planets_twelfth:
        spiritual_yogas.append({
            'type': 'Kemadruma Cancellation (Spiritual Protection)',
            'description': 'Planets flanking Moon provide spiritual and mental stability',
            'moon_house': moon_house,
            'planets_second': planets_second,
            'planets_twelfth': planets_twelfth,
            'strength': 'Medium'
        })
    
    return spiritual_yogas

def calculate_moksha_potential_score(sanyasa_yogas, vishnu_yogas, spiritual_yogas):
    """Calculate comprehensive moksha potential score"""
    total_score = 0
    
    # Sanyasa Yogas scoring (higher weight for moksha)
    for yoga in sanyasa_yogas:
        strength = yoga.get('strength', 'Medium')
        if 'Very Strong' in strength:
            total_score += 5
        elif strength == 'Strong':
            total_score += 4
        elif strength == 'Medium':
            total_score += 3
        elif strength == 'Weak':
            total_score += 2
        # Broken yogas get no points
    
    # Vishnu Yogas scoring
    for yoga in vishnu_yogas:
        strength = yoga.get('strength', 'Medium')
        if 'Very Strong' in strength:
            total_score += 4
        elif strength == 'Strong':
            total_score += 3
        elif strength == 'Medium':
            total_score += 2
        elif strength == 'Weak':
            total_score += 1
    
    # Spiritual Wealth Yogas scoring
    for yoga in spiritual_yogas:
        strength = yoga.get('strength', 'Medium')
        if 'Very Strong' in strength:
            total_score += 3
        elif strength == 'Strong':
            total_score += 2
        elif strength == 'Medium':
            total_score += 1
    
    return total_score

def generate_spiritual_recommendations(moksha_score, sanyasa_yogas, vishnu_yogas, spiritual_yogas):
    """Generate comprehensive personalized spiritual recommendations"""
    recommendations = []
    
    # Overall spiritual potential recommendations
    if moksha_score >= 15:
        recommendations.append("Exceptional spiritual potential - Consider advanced meditation and teaching roles")
        recommendations.append("Natural spiritual leader - Share wisdom with others")
        recommendations.append("Strong likelihood of spiritual attainment in this lifetime")
    elif moksha_score >= 10:
        recommendations.append("Strong spiritual potential - Regular intensive practices recommended")
        recommendations.append("Study of advanced spiritual texts and philosophy highly beneficial")
        recommendations.append("Consider periods of spiritual retreat and deep contemplation")
    elif moksha_score >= 6:
        recommendations.append("Good spiritual foundation - Establish consistent daily practices")
        recommendations.append("Study of scriptures and philosophical texts will accelerate growth")
        recommendations.append("Pilgrimage and spiritual community involvement recommended")
    elif moksha_score >= 3:
        recommendations.append("Moderate spiritual inclination - Begin with basic meditation and prayer")
        recommendations.append("Gradual introduction to spiritual concepts through daily rituals")
        recommendations.append("Focus on ethical living and service to others")
    else:
        recommendations.append("Developing spiritual awareness - Start with karma yoga (selfless service)")
        recommendations.append("Simple daily practices like gratitude and compassion cultivation")
        recommendations.append("Seek spiritual guidance from qualified teachers")
    
    # Specific yoga-based recommendations
    sanyasa_present = len(sanyasa_yogas) > 0
    vishnu_present = len(vishnu_yogas) > 0
    
    if sanyasa_present:
        recommendations.append("Strong renunciation tendency - Balance material responsibilities with spiritual growth")
        recommendations.append("Natural inclination for periods of solitude and contemplation")
        if any('Very Strong' in yoga.get('strength', '') for yoga in sanyasa_yogas):
            recommendations.append("Consider formal spiritual training or monastic lifestyle")
    
    if vishnu_present:
        recommendations.append("Devotional practices, especially Vishnu worship, will be highly beneficial")
        recommendations.append("Mantras, bhajans, and devotional music will enhance spiritual growth")
    
    # Specific spiritual yoga recommendations
    yoga_types = [yoga['type'] for yoga in spiritual_yogas]
    
    if any('Saraswati' in yoga_type for yoga_type in yoga_types):
        recommendations.append("Focus on learning, teaching, and creative spiritual expression")
        recommendations.append("Writing, speaking, or artistic expression can be spiritual practices")
    
    if any('Hamsa' in yoga_type or 'Brahma' in yoga_type for yoga_type in yoga_types):
        recommendations.append("Traditional Vedic studies and Jupiter-related practices highly favorable")
        recommendations.append("Thursday fasting and Jupiter mantras recommended")
    
    if any('Pandit' in yoga_type for yoga_type in yoga_types):
        recommendations.append("Scholarly approach to spirituality - study multiple traditions")
        recommendations.append("Teaching and sharing knowledge is a spiritual duty")
    
    if any('Tapasya' in yoga_type for yoga_type in yoga_types):
        recommendations.append("Disciplined practices and austerities will yield significant results")
        recommendations.append("Saturday spiritual observances and Saturn mantras beneficial")
    
    if any('Raja Yoga' in yoga_type for yoga_type in yoga_types):
        recommendations.append("Natural spiritual leadership abilities - guide others on the path")
        recommendations.append("Meditation and self-realization practices are your forte")
    
    return recommendations


def add_spiritualYoga(birth_data):
    """
    Perform the exact calculations from the original endpoint and return the response dict.
    """
    # --- Input parsing and JD ---
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])

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
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planet_positions = {}
    
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        planet_positions[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degrees': sign_deg,
            'retrograde': retrograde,
            'dignity': get_planet_dignity(planet_name, sign),
            'house': None  # Will be calculated below
        }

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign, ketu_sign_deg, ketu_sign_index = longitude_to_sign(ketu_lon)
    planet_positions['Ketu'] = {
        'longitude': ketu_lon,
        'sign': ketu_sign,
        'degrees': ketu_sign_deg,
        'retrograde': '',
        'dignity': get_planet_dignity('Ketu', ketu_sign),
        'house': None
    }

    # Calculate Ascendant and houses
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Assign house signs with lords
    house_signs = {}
    for i in range(12):
        sign_index = (asc_sign_index + i) % 12
        house_signs[f"House {i+1}"] = {
            "sign": signs[sign_index],
            "lord": HOUSE_LORDS[signs[sign_index]]
        }

    # Calculate house positions for all planets
    for planet_name in planet_positions:
        lon = planet_positions[planet_name]['longitude']
        house = get_house(lon, asc_sign_index)
        planet_positions[planet_name]['house'] = house

    # Format planetary positions for output
    planetary_positions_json = {}
    for planet_name, data in planet_positions.items():
        planetary_positions_json[planet_name] = {
            "sign": data['sign'],
            "degrees": format_dms(data['degrees']),
            "house": data['house'],
            "retrograde": data['retrograde'],
            "dignity": data['dignity'],
            "strength_score": calculate_planetary_strength(planet_positions, planet_name)
        }

    # Calculate all spiritual prosperity yogas
    sanyasa_yogas = detect_sanyasa_yoga(planet_positions, house_signs)
    vishnu_yogas = detect_vishnu_yoga(planet_positions, house_signs)
    spiritual_wealth_yogas = detect_spiritual_wealth_yogas(planet_positions, house_signs)
    
    # Calculate overall moksha potential
    moksha_score = calculate_moksha_potential_score(sanyasa_yogas, vishnu_yogas, spiritual_wealth_yogas)
    recommendations = generate_spiritual_recommendations(moksha_score, sanyasa_yogas, vishnu_yogas, spiritual_wealth_yogas)

    # Prepare comprehensive response (identical structure/fields)
    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "location": f"Lat: {latitude}, Lon: {longitude}",
            "timezone_offset": timezone_offset
        },
        "chart_foundations": {
            "ascendant": {
                "sign": asc_sign,
                "degrees": format_dms(ascendant_lon % 30),
                "lord": HOUSE_LORDS[asc_sign]
            },
            "planetary_positions": planetary_positions_json,
            "house_signs": house_signs
        },
        "spiritual_prosperity_analysis": {
            "moksha_yogas": {
                "sanyasa_yogas": sanyasa_yogas,
                "count": len(sanyasa_yogas),
                "types_checked": ["Classical 4+ Planet", "Saturn-Moon", "Moon in Saturn Drekkana", "Scholarly (Jupiter 9th)"]
            },
            "vishnu_yogas": {
                "yogas": vishnu_yogas,
                "count": len(vishnu_yogas),
                "types_checked": ["Primary (Dharma-Karma Adhipati)", "Alternative Formation"]
            },
            "spiritual_wealth_yogas": {
                "yogas": spiritual_wealth_yogas,
                "count": len(spiritual_wealth_yogas),
                "types_checked": [
                    "Moksha Trikona", "Dharma", "Saraswati", "Hamsa", "Brahma", 
                    "Pandit", "Tapasya", "Guru Chandal (Positive)", "Spiritual Raja", 
                    "Kemadruma Cancellation"
                ]
            },
            "overall_assessment": {
                "moksha_potential_score": moksha_score,
                "spiritual_strength": (
                    "Exceptional" if moksha_score >= 15 else
                    "Very Strong" if moksha_score >= 10 else
                    "Strong" if moksha_score >= 6 else
                    "Moderate" if moksha_score >= 3 else
                    "Developing"
                ),
                "total_yogas_found": len(sanyasa_yogas) + len(vishnu_yogas) + len(spiritual_wealth_yogas),
                "total_yogas_checked": 16
            },
            "spiritual_recommendations": recommendations
        },
        "yoga_validation_report": {
            "comprehensive_analysis": True,
            "sanyasa_yoga_variants": 4,
            "vishnu_yoga_variants": 2,
            "spiritual_wealth_yoga_variants": 10,
            "aspect_calculations_included": True,
            "conjunction_analysis_included": True,
            "planetary_dignity_assessed": True,
            "house_lordship_verified": True,
            "strength_scoring_applied": True
        },
        "technical_details": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}",
            "house_system": "Whole Sign",
            "calculation_type": "Sidereal",
            "aspect_orbs": {"conjunction": 10, "combustion": 8},
            "strength_factors": ["dignity", "house_position", "retrograde_status"]
        }
    }

    return response
