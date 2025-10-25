import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_house(lon, asc_sign_index, orientation_shift=0):
    """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_classical_dignity(longitude, planet_name):
    """
    Get classical planetary dignity based on traditional texts.
    RULE: Only 3 primary dignities as per Brihat Parashara Hora Shastra:
    - Own Sign (स्वक्षेत्र): Planet in its own sign
    - Exaltation (उच्च): Planet in exaltation sign  
    - Debilitation (नीच): Planet in debilitation sign
    All other positions are neutral for yoga analysis.
    """
    sign_index = int(longitude // 30) % 12
    sign = signs[sign_index]
    
    classical_dignities = {
        'Moon': {
            'own_sign': ['Cancer'],
            'exaltation': 'Taurus', 
            'debilitation': 'Scorpio'
        },
        'Mars': {
            'own_sign': ['Aries', 'Scorpio'],
            'exaltation': 'Capricorn',
            'debilitation': 'Cancer'
        }
    }
    
    if planet_name not in classical_dignities:
        return 'Neutral', 0.6
    
    planet_data = classical_dignities[planet_name]
    
    # Check own sign
    if sign in planet_data['own_sign']:
        return 'Own Sign', 1.0
    
    # Check exaltation
    if sign == planet_data['exaltation']:
        return 'Exalted', 1.2
    
    # Check debilitation  
    if sign == planet_data['debilitation']:
        return 'Debilitated', 0.3
    
    # All other positions are neutral
    return 'Neutral', 0.6

def get_sign_attributes(sign):
    """Get classical sign attributes."""
    sign_data = {
        'Aries': {'lord': 'Mars', 'element': 'Fire', 'quality': 'Cardinal', 'nature': 'Movable'},
        'Taurus': {'lord': 'Venus', 'element': 'Earth', 'quality': 'Fixed', 'nature': 'Fixed'},
        'Gemini': {'lord': 'Mercury', 'element': 'Air', 'quality': 'Mutable', 'nature': 'Dual'},
        'Cancer': {'lord': 'Moon', 'element': 'Water', 'quality': 'Cardinal', 'nature': 'Movable'},
        'Leo': {'lord': 'Sun', 'element': 'Fire', 'quality': 'Fixed', 'nature': 'Fixed'},
        'Virgo': {'lord': 'Mercury', 'element': 'Earth', 'quality': 'Mutable', 'nature': 'Dual'},
        'Libra': {'lord': 'Venus', 'element': 'Air', 'quality': 'Cardinal', 'nature': 'Movable'},
        'Scorpio': {'lord': 'Mars', 'element': 'Water', 'quality': 'Fixed', 'nature': 'Fixed'},
        'Sagittarius': {'lord': 'Jupiter', 'element': 'Fire', 'quality': 'Mutable', 'nature': 'Dual'},
        'Capricorn': {'lord': 'Saturn', 'element': 'Earth', 'quality': 'Cardinal', 'nature': 'Movable'},
        'Aquarius': {'lord': 'Saturn', 'element': 'Air', 'quality': 'Fixed', 'nature': 'Fixed'},
        'Pisces': {'lord': 'Jupiter', 'element': 'Water', 'quality': 'Mutable', 'nature': 'Dual'}
    }
    return sign_data.get(sign, {})

def get_house_attributes(house):
    """Get classical house attributes and classifications."""
    house_data = {
        1: {'significance': 'Self, Personality, Physical Body', 'type': ['Kendra', 'Trikona'], 'nature': 'Angular'},
        2: {'significance': 'Wealth, Family, Speech', 'type': ['Maraka'], 'nature': 'Succedent'},
        3: {'significance': 'Courage, Siblings, Efforts', 'type': ['Upachaya'], 'nature': 'Cadent'},
        4: {'significance': 'Home, Mother, Property', 'type': ['Kendra'], 'nature': 'Angular'},
        5: {'significance': 'Children, Intelligence, Creativity', 'type': ['Trikona'], 'nature': 'Succedent'},
        6: {'significance': 'Enemies, Disease, Service', 'type': ['Upachaya', 'Dusthana'], 'nature': 'Cadent'},
        7: {'significance': 'Partnership, Marriage, Business', 'type': ['Kendra', 'Maraka'], 'nature': 'Angular'},
        8: {'significance': 'Transformation, Sudden Events', 'type': ['Dusthana'], 'nature': 'Succedent'},
        9: {'significance': 'Fortune, Higher Learning, Father', 'type': ['Trikona'], 'nature': 'Cadent'},
        10: {'significance': 'Career, Reputation, Authority', 'type': ['Kendra', 'Upachaya'], 'nature': 'Angular'},
        11: {'significance': 'Gains, Friends, Desires', 'type': ['Upachaya'], 'nature': 'Succedent'},
        12: {'significance': 'Losses, Foreign, Spirituality', 'type': ['Dusthana'], 'nature': 'Cadent'}
    }
    return house_data.get(house, {})

def calculate_angular_separation(lon1, lon2):
    """Calculate exact angular separation between two planets."""
    separation = abs(lon1 - lon2)
    if separation > 180:
        separation = 360 - separation
    return separation

def get_conjunction_strength(angular_separation):
    """
    Classify conjunction strength based on traditional angular separations.
    RULE: Classical texts consider various degrees of conjunction strength.
    """
    if angular_separation <= 1:
        return {'grade': 'Exact Conjunction', 'strength': 1.0, 'sanskrit': 'शुद्ध युति'}
    elif angular_separation <= 3:
        return {'grade': 'Very Close Conjunction', 'strength': 0.9, 'sanskrit': 'अति निकट युति'}
    elif angular_separation <= 6:
        return {'grade': 'Close Conjunction', 'strength': 0.8, 'sanskrit': 'निकट युति'}
    elif angular_separation <= 10:
        return {'grade': 'Moderate Conjunction', 'strength': 0.7, 'sanskrit': 'मध्यम युति'}
    elif angular_separation <= 15:
        return {'grade': 'Wide Conjunction', 'strength': 0.6, 'sanskrit': 'विस्तृत युति'}
    elif angular_separation <= 20:
        return {'grade': 'Loose Conjunction', 'strength': 0.5, 'sanskrit': 'शिथिल युति'}
    else:
        return {'grade': 'Very Loose Conjunction', 'strength': 0.4, 'sanskrit': 'अति शिथिल युति'}

def calculate_yoga_strength(moon_lon, mars_lon, moon_dignity, mars_dignity):
    """
    Calculate comprehensive yoga strength using traditional formula.
    RULE: Classical strength = Angular Closeness (40%) + Moon Dignity (30%) + Mars Dignity (30%)
    """
    angular_separation = calculate_angular_separation(moon_lon, mars_lon)
    conjunction_data = get_conjunction_strength(angular_separation)
    
    # Traditional strength calculation
    angular_strength = conjunction_data['strength']
    moon_strength = moon_dignity[1]
    mars_strength = mars_dignity[1]
    
    overall_strength = (angular_strength * 0.4) + (moon_strength * 0.3) + (mars_strength * 0.3)
    
    return {
        'overall_strength': overall_strength,
        'angular_separation': angular_separation,
        'conjunction_data': conjunction_data,
        'component_strengths': {
            'angular': angular_strength,
            'moon_dignity': moon_strength,
            'mars_dignity': mars_strength
        }
    }

def get_traditional_strength_grade(score):
    """Get traditional strength grade with Sanskrit terminology."""
    if score >= 0.9:
        return {'grade': 'Excellent', 'sanskrit': 'उत्तम (Uttama)', 'description': 'Outstanding results'}
    elif score >= 0.8:
        return {'grade': 'Very Good', 'sanskrit': 'प्रोन्नत (Pronnat)', 'description': 'Very favorable results'}
    elif score >= 0.7:
        return {'grade': 'Good', 'sanskrit': 'मध्यम (Madhyama)', 'description': 'Good results'}
    elif score >= 0.6:
        return {'grade': 'Average', 'sanskrit': 'सामान्य (Samanya)', 'description': 'Moderate results'}
    elif score >= 0.5:
        return {'grade': 'Below Average', 'sanskrit': 'कनिष्ठ (Kanishtha)', 'description': 'Below average results'}
    else:
        return {'grade': 'Weak', 'sanskrit': 'दुर्बल (Durbala)', 'description': 'Weak results, needs remedies'}

def analyze_individual_planet_permutation(planet_name, longitude, house, planet_positions):
    """
    Analyze individual planet position in all 144 possible combinations.
    RULE: Each planet can be in any of 12 signs and any of 12 houses = 144 combinations.
    """
    sign, sign_deg, sign_index = longitude_to_sign(longitude)
    sign_attrs = get_sign_attributes(sign)
    house_attrs = get_house_attributes(house)
    dignity = get_classical_dignity(longitude, planet_name)
    
    return {
        'planet': planet_name,
        'sign_permutation': {
            'sign': sign,
            'sign_number': sign_index + 1,
            'degrees_in_sign': round(sign_deg, 2),
            'sign_lord': sign_attrs.get('lord'),
            'element': sign_attrs.get('element'),
            'quality': sign_attrs.get('quality'),
            'nature': sign_attrs.get('nature')
        },
        'house_permutation': {
            'house': house,
            'house_significance': house_attrs.get('significance'),
            'house_types': house_attrs.get('type', []),
            'house_nature': house_attrs.get('nature')
        },
        'dignity_permutation': {
            'dignity_status': dignity[0],
            'strength_score': dignity[1],
            'classical_effects': get_dignity_effects(dignity[0], planet_name)
        },
        'individual_effects': get_individual_planet_effects(planet_name, sign, house, dignity[0])
    }

def analyze_chandra_mangal_yoga_formation(moon_analysis, mars_analysis):
    """
    Check Chandra Mangal Yoga formation and analyze the specific combination.
    RULE: Moon and Mars must be in the same sign for the yoga to form.
    """
    moon_sign = moon_analysis['sign_permutation']['sign']
    mars_sign = mars_analysis['sign_permutation']['sign']
    moon_house = moon_analysis['house_permutation']['house']
    mars_house = mars_analysis['house_permutation']['house']
    
    yoga_present = (moon_sign == mars_sign)
    
    formation_analysis = {
        'yoga_present': yoga_present,
        'formation_rule': 'Classical Rule: Chandra (Moon) + Mangal (Mars) in same sign',
        'moon_position': f"{moon_sign} sign, {moon_house}th house",
        'mars_position': f"{mars_sign} sign, {mars_house}th house"
    }
    
    if yoga_present:
        formation_analysis.update({
            'yoga_sign': moon_sign,
            'yoga_house': moon_house,
            'formation_type': 'Same Sign Conjunction',
            'classical_name': 'चन्द्र मंगल योग (Chandra Mangal Yoga)'
        })
    else:
        formation_analysis.update({
            'separation_analysis': f"Moon in {moon_sign}, Mars in {mars_sign} - Different signs",
            'house_relationship': analyze_house_relationship(moon_house, mars_house),
            'alternative_combinations': suggest_alternative_combinations(moon_analysis, mars_analysis)
        })
    
    return formation_analysis

def analyze_house_relationship(moon_house, mars_house):
    """Analyze the relationship between Moon and Mars houses when yoga is not present."""
    house_difference = abs(moon_house - mars_house)
    
    # Check for 7th house relationship (mutual aspect)
    if house_difference == 6 or house_difference == 6:
        return {
            'relationship_type': 'Mutual 7th House Aspect',
            'description': 'Moon and Mars aspect each other, creating indirect connection',
            'strength': 'Moderate influence through aspect'
        }
    elif house_difference <= 3:
        return {
            'relationship_type': 'Close House Relationship',
            'description': f'Houses are {house_difference} apart, creating some mutual influence',
            'strength': 'Weak to moderate influence'
        }
    else:
        return {
            'relationship_type': 'Distant House Relationship',
            'description': f'Houses are {house_difference} apart, limited mutual influence',
            'strength': 'Minimal influence'
        }

def get_dignity_effects(dignity, planet):
    """Get classical effects based on planetary dignity."""
    effects = {
        'Moon': {
            'Own Sign': 'Strong emotional stability, natural wealth accumulation, maternal property benefits',
            'Exalted': 'Exceptional emotional strength, outstanding property gains, blessed wealth',
            'Debilitated': 'Emotional challenges with wealth, property obstacles, lunar remedies needed',
            'Neutral': 'Balanced emotional approach to wealth, steady moderate results'
        },
        'Mars': {
            'Own Sign': 'Strong willpower for wealth, courageous property investments, self-earned assets',
            'Exalted': 'Exceptional business courage, outstanding property success, leadership in wealth',
            'Debilitated': 'Impulsive financial decisions, property conflicts, martial remedies needed',
            'Neutral': 'Moderate business approach, balanced property efforts, steady progress'
        }
    }
    return effects.get(planet, {}).get(dignity, 'Balanced planetary effects')

def get_individual_planet_effects(planet, sign, house, dignity):
    """Get effects of individual planet position."""
    sign_attrs = get_sign_attributes(sign)
    house_attrs = get_house_attributes(house)
    
    base_effect = f"{planet} in {sign} ({sign_attrs.get('element')} sign) in {house}th house"
    
    if planet == 'Moon':
        specific_effects = {
            'wealth_approach': f"Emotional and intuitive approach to wealth through {sign_attrs.get('element', '').lower()} element",
            'property_focus': f"Property matters related to {house_attrs.get('significance', '').lower()}",
            'manifestation': f"Results through {dignity.lower()} lunar energy"
        }
    else:  # Mars
        specific_effects = {
            'wealth_approach': f"Active and courageous approach to wealth through {sign_attrs.get('element', '').lower()} element",
            'property_focus': f"Property initiatives related to {house_attrs.get('significance', '').lower()}",
            'manifestation': f"Results through {dignity.lower()} martial energy"
        }
    
    return {
        'base_position': base_effect,
        'specific_effects': specific_effects
    }

def suggest_alternative_combinations(moon_analysis, mars_analysis):
    """Suggest alternative wealth combinations when Chandra Mangal Yoga is not present."""
    alternatives = []
    
    moon_house = moon_analysis['house_permutation']['house']
    mars_house = mars_analysis['house_permutation']['house']
    moon_dignity = moon_analysis['dignity_permutation']['dignity_status']
    mars_dignity = mars_analysis['dignity_permutation']['dignity_status']
    
    # Check individual strengths
    if moon_dignity in ['Own Sign', 'Exalted']:
        alternatives.append(f"Strong Moon in {moon_analysis['sign_permutation']['sign']} - Independent lunar wealth benefits")
    
    if mars_dignity in ['Own Sign', 'Exalted']:
        alternatives.append(f"Strong Mars in {mars_analysis['sign_permutation']['sign']} - Independent martial wealth benefits")
    
    # Check beneficial house positions
    if moon_house in [1, 4, 5, 9, 10, 11]:
        alternatives.append(f"Moon in {moon_house}th house - Beneficial house for wealth and property")
    
    if mars_house in [1, 3, 6, 10, 11]:
        alternatives.append(f"Mars in {mars_house}th house - Beneficial house for business and property")
    
    # General alternatives
    alternatives.extend([
        "Look for other wealth-giving yogas like Dhana Yoga, Raj Yoga",
        "Analyze individual planetary periods (Moon Dasha, Mars Dasha)",
        "Check divisional charts for property indications (D4 - Chaturthamsa)"
    ])
    
    return alternatives

def generate_comprehensive_analysis(formation_analysis, moon_analysis, mars_analysis, strength_data=None):
    """Generate comprehensive traditional analysis covering all permutations and combinations."""
    
    analysis = {
        'yoga_formation_analysis': formation_analysis,
        'complete_permutation_analysis': {
            'moon_permutations': moon_analysis,
            'mars_permutations': mars_analysis,
            'total_combinations_analyzed': '144 traditional combinations (12 signs × 12 houses per planet)'
        }
    }
    
    if formation_analysis['yoga_present'] and strength_data:
        # Add yoga-specific analysis when present
        yoga_sign = formation_analysis['yoga_sign']
        yoga_house = formation_analysis['yoga_house']
        sign_attrs = get_sign_attributes(yoga_sign)
        house_attrs = get_house_attributes(yoga_house)
        
        analysis['yoga_specific_analysis'] = {
            'strength_analysis': {
                'overall_strength': round(strength_data['overall_strength'], 3),
                'strength_grade': get_traditional_strength_grade(strength_data['overall_strength']),
                'angular_separation': round(strength_data['angular_separation'], 2),
                'conjunction_type': strength_data['conjunction_data']
            },
            'yoga_combination_effects': {
                'sign_effects': get_yoga_sign_effects(yoga_sign, sign_attrs),
                'house_effects': get_yoga_house_effects(yoga_house, house_attrs),
                'dignity_combination': get_combined_dignity_effects(
                    moon_analysis['dignity_permutation'], 
                    mars_analysis['dignity_permutation']
                )
            },
            'classical_interpretation': generate_classical_yoga_interpretation(
                yoga_sign, yoga_house, moon_analysis, mars_analysis, strength_data
            )
        }
    else:
        # Add individual analysis when yoga is not present
        analysis['individual_analysis'] = {
            'moon_individual_effects': moon_analysis['individual_effects'],
            'mars_individual_effects': mars_analysis['individual_effects'],
            'combined_individual_influence': analyze_individual_combined_effects(moon_analysis, mars_analysis)
        }
    
    return analysis

def get_yoga_sign_effects(sign, sign_attrs):
    """Get specific effects when Chandra Mangal Yoga occurs in a particular sign."""
    element = sign_attrs.get('element', '')
    lord = sign_attrs.get('lord', '')
    
    sign_specific_effects = {
        'Aries': 'Pioneering wealth creation, leadership in property, quick material gains',
        'Taurus': 'Stable wealth accumulation, luxury properties, agricultural land benefits',
        'Gemini': 'Multiple income sources, communication-based wealth, commercial properties',
        'Cancer': 'Emotional property attachment, family wealth, domestic real estate focus',
        'Leo': 'Authoritative wealth approach, prestigious properties, government connections',
        'Virgo': 'Systematic wealth planning, service-based properties, analytical investments',
        'Libra': 'Partnership wealth, beautiful properties, diplomatic property dealings',
        'Scorpio': 'Hidden wealth, transformative properties, intense financial focus',
        'Sagittarius': 'Foreign properties, educational real estate, philosophical wealth approach',
        'Capricorn': 'Long-term wealth building, mountainous properties, disciplined investments',
        'Aquarius': 'Innovative wealth methods, community properties, unconventional investments',
        'Pisces': 'Intuitive wealth decisions, waterfront properties, spiritual real estate'
    }
    
    return {
        'element_influence': f"{element} element enhances {element.lower()}-based wealth approaches",
        'sign_lord_influence': f"{lord} as sign lord modifies results with {lord.lower()} characteristics",
        'specific_effects': sign_specific_effects.get(sign, 'General wealth and property benefits')
    }

def get_yoga_house_effects(house, house_attrs):
    """Get specific effects when Chandra Mangal Yoga occurs in a particular house."""
    significance = house_attrs.get('significance', '')
    house_types = house_attrs.get('type', [])
    
    house_strength = 'Strong' if 'Kendra' in house_types or 'Trikona' in house_types else 'Moderate'
    if 'Upachaya' in house_types:
        house_strength += ' (Improving over time)'
    
    return {
        'house_strength': house_strength,
        'life_area_focus': f"Wealth and property through {significance.lower()}",
        'house_classification_effects': f"Effects modified by {', '.join(house_types)} house nature"
    }

def get_combined_dignity_effects(moon_dignity_data, mars_dignity_data):
    """Analyze combined effects of Moon and Mars dignities in the yoga."""
    moon_dignity = moon_dignity_data['dignity_status']
    mars_dignity = mars_dignity_data['dignity_status']
    
    if moon_dignity == 'Exalted' and mars_dignity == 'Exalted':
        return 'Exceptional yoga - Both planets at peak strength, outstanding wealth results'
    elif moon_dignity == 'Own Sign' and mars_dignity == 'Own Sign':
        return 'Very strong yoga - Both planets comfortable, natural wealth accumulation'
    elif moon_dignity == 'Debilitated' and mars_dignity == 'Debilitated':
        return 'Challenging yoga - Both planets weakened, wealth after remedies and persistent efforts'
    elif 'Exalted' in [moon_dignity, mars_dignity]:
        return 'Enhanced yoga - One planet very strong, elevates overall results'
    elif 'Debilitated' in [moon_dignity, mars_dignity]:
        return 'Mixed yoga - One planet challenged, creates obstacles but not complete blockage'
    else:
        return 'Balanced yoga - Moderate planetary strengths, steady wealth accumulation'

def analyze_individual_combined_effects(moon_analysis, mars_analysis):
    """Analyze how Moon and Mars work individually when yoga is not present."""
    moon_house = moon_analysis['house_permutation']['house']
    mars_house = mars_analysis['house_permutation']['house']
    
    wealth_houses = [2, 11]  # Primary wealth houses
    property_houses = [4, 12]  # Primary property houses
    
    combined_effects = []
    
    if moon_house in wealth_houses:
        combined_effects.append(f"Moon in {moon_house}th house supports wealth accumulation")
    
    if mars_house in wealth_houses:
        combined_effects.append(f"Mars in {mars_house}th house supports active wealth creation")
    
    if moon_house in property_houses:
        combined_effects.append(f"Moon in {moon_house}th house indicates property connections")
    
    if mars_house in property_houses:
        combined_effects.append(f"Mars in {mars_house}th house indicates property initiatives")
    
    return {
        'individual_contributions': combined_effects if combined_effects else ['Individual planetary effects without direct yoga formation'],
        'overall_assessment': 'Separate planetary influences on wealth and property without unified yoga energy'
    }

def generate_classical_yoga_interpretation(sign, house, moon_analysis, mars_analysis, strength_data):
    """Generate final classical interpretation of the yoga."""
    strength_grade = get_traditional_strength_grade(strength_data['overall_strength'])
    sign_attrs = get_sign_attributes(sign)
    
    interpretation = {
        'yoga_summary': f"चन्द्र मंगल योग (Chandra Mangal Yoga) in {sign} sign, {house}th house",
        'strength_verdict': f"{strength_grade['sanskrit']} - {strength_grade['description']}",
        'primary_indications': [
            f"Material wealth through {sign_attrs.get('element', '').lower()}-element methods",
            f"Property focus in {house}th house life areas",
            f"Results strength: {strength_grade['grade']}"
        ],
        'classical_timing': [
            "Moon Mahadasha (10 years): Primary activation period",
            "Mars Mahadasha (7 years): Secondary activation period", 
            f"Transits through {sign}: Temporary activation"
        ],
        'remedial_suggestions': get_remedial_suggestions(moon_analysis, mars_analysis, strength_data['overall_strength'])
    }
    
    return interpretation

def get_remedial_suggestions(moon_analysis, mars_analysis, overall_strength):
    """Provide classical remedial suggestions based on planetary positions."""
    remedies = []
    
    moon_dignity = moon_analysis['dignity_permutation']['dignity_status']
    mars_dignity = mars_analysis['dignity_permutation']['dignity_status']
    
    if moon_dignity == 'Debilitated':
        remedies.extend([
            "Moon remedies: Wear Pearl (Moti), Fast on Mondays",
            "Offer water to Moon on Purnima (Full Moon)",
            "Chant 'Om Som Somaya Namah' 108 times daily"
        ])
    
    if mars_dignity == 'Debilitated':
        remedies.extend([
            "Mars remedies: Wear Red Coral (Moonga), Fast on Tuesdays",
            "Recite Hanuman Chalisa daily",
            "Chant 'Om Angarakaya Namah' 108 times daily"
        ])
    
    if overall_strength < 0.6:
        remedies.extend([
            "Perform Chandra Mangal Yoga strengthening rituals",
            "Donate red clothes and sweets on Tuesdays",
            "Feed cows and offer milk to Moon temples"
        ])
    
    return remedies if remedies else ["No specific remedies needed - Natural strength present"]

def calculate_planetary_positions_chandra_mangal(birth_data):
    """Calculate all planetary positions for Chandra Mangal analysis."""
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
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Calculate Ascendant and houses
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Calculate planet houses
    planet_houses = {planet: get_house(lon, asc_sign_index) 
                    for planet, (lon, _) in planet_positions.items()}

    # Format all planetary positions for response
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        
        # Get dignity for Moon and Mars only
        if planet_name in ['Moon', 'Mars']:
            dignity = get_classical_dignity(lon, planet_name)
            dignity_status = dignity[0]
        else:
            dignity_status = 'N/A'
        
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": format_dms(sign_deg),
            "retrograde": retro,
            "house": planet_houses[planet_name],
            "longitude": round(lon, 6),
            "dignity": dignity_status
        }

    return planetary_positions_json, asc_sign, ascendant_lon, ayanamsa_value