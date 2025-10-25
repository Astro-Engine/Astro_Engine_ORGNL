import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Complete House Effects for ALL 12 Ascendants
COMPLETE_HOUSE_EFFECTS = {
    'Aries': {
        1: {'domain': 'Self, personality, health', 'effects': 'Strong leadership, commanding presence, excellent health, natural authority'},
        2: {'domain': 'Wealth, speech, family', 'effects': 'Accumulated wealth, eloquent speech, supportive family, financial stability'},
        3: {'domain': 'Siblings, courage, ventures', 'effects': 'Successful ventures, courageous nature, good sibling relationships'},
        4: {'domain': 'Home, mother, property, education', 'effects': 'Luxurious homes, happy mother, property gains, higher education'},
        5: {'domain': 'Children, creativity, speculation', 'effects': 'Intelligent children, creative abilities, gains from speculation'},
        6: {'domain': 'Service, health, enemies', 'effects': 'Success in service sector, good health, victory over enemies'},
        7: {'domain': 'Marriage, partnerships, business', 'effects': 'Excellent spouse, successful partnerships, business gains'},
        8: {'domain': 'Transformation, occult, longevity', 'effects': 'Interest in occult, transformative experiences, long life'},
        9: {'domain': 'Luck, spirituality, father', 'effects': 'Divine blessings, spiritual wisdom, supportive father'},
        10: {'domain': 'Career, reputation, authority', 'effects': 'High position, government favor, professional success'},
        11: {'domain': 'Gains, friendships, elder siblings', 'effects': 'Multiple income sources, influential friends, elder sibling support'},
        12: {'domain': 'Spirituality, foreign lands, expenses', 'effects': 'Spiritual inclinations, foreign connections, charitable nature'}
    },
    'Taurus': {
        1: {'domain': 'Self, wealth, beauty', 'effects': 'Wealthy personality, attractive appearance, material comforts, stable nature'},
        2: {'domain': 'Communication, family wealth', 'effects': 'Sweet speech, family prosperity, accumulated resources'},
        3: {'domain': 'Property, mother, education', 'effects': 'Multiple properties, educated mother, academic achievements'},
        4: {'domain': 'Entertainment, creativity, children', 'effects': 'Creative talents, intelligent children, gains from entertainment'},
        5: {'domain': 'Service, health, daily routine', 'effects': 'Success in healing professions, disciplined lifestyle'},
        6: {'domain': 'Partnerships, marriage, business', 'effects': 'Harmonious marriage, profitable partnerships'},
        7: {'domain': 'Transformation, research, occult', 'effects': 'Deep research abilities, interest in mysteries'},
        8: {'domain': 'Philosophy, higher learning, luck', 'effects': 'Higher education, philosophical wisdom, good fortune'},
        9: {'domain': 'Career, reputation, public life', 'effects': 'Stable career, good reputation, public recognition'},
        10: {'domain': 'Gains, social network, achievements', 'effects': 'Multiple income sources, influential network'},
        11: {'domain': 'Spirituality, foreign travels, charity', 'effects': 'Spiritual expenses, foreign connections'},
        12: {'domain': 'Self-development, new beginnings', 'effects': 'Continuous self-improvement, fresh starts'}
    },
    'Gemini': {
        1: {'domain': 'Communication, intellect, skills', 'effects': 'Excellent communication, multiple skills, intellectual growth, versatility'},
        2: {'domain': 'Home, emotions, nurturing', 'effects': 'Emotional security, nurturing environment, domestic happiness'},
        3: {'domain': 'Creativity, romance, entertainment', 'effects': 'Creative expression, romantic success, entertainment industry gains'},
        4: {'domain': 'Service, health, analytical abilities', 'effects': 'Analytical skills, health consciousness, service orientation'},
        5: {'domain': 'Relationships, partnerships, diplomacy', 'effects': 'Diplomatic nature, successful partnerships, social skills'},
        6: {'domain': 'Transformation, psychology, research', 'effects': 'Psychological insights, research abilities, transformative thinking'},
        7: {'domain': 'Philosophy, teaching, higher wisdom', 'effects': 'Teaching abilities, philosophical nature, higher learning'},
        8: {'domain': 'Discipline, structure, responsibility', 'effects': 'Disciplined approach, structured thinking, responsibility'},
        9: {'domain': 'Innovation, networking, friendships', 'effects': 'Innovative ideas, strong network, group leadership'},
        10: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Intuitive abilities, compassionate nature, spiritual growth'},
        11: {'domain': 'New ventures, energy, leadership', 'effects': 'Leadership in new projects, energetic approach'},
        12: {'domain': 'Material stability, persistence', 'effects': 'Material security, persistent efforts, steady growth'}
    },
    'Cancer': {
        1: {'domain': 'Nurturing, emotions, intuition', 'effects': 'Caring nature, emotional intelligence, protective instincts, intuitive wisdom'},
        2: {'domain': 'Communication, siblings, courage', 'effects': 'Eloquent speech, good sibling relationships, courageous expression'},
        3: {'domain': 'Property, mother, education', 'effects': 'Real estate gains, mother\'s blessings, educational success'},
        4: {'domain': 'Creativity, children, speculation', 'effects': 'Creative intelligence, gifted children, speculative gains'},
        5: {'domain': 'Service, health, daily work', 'effects': 'Success in healing professions, health awareness, service to others'},
        6: {'domain': 'Marriage, partnerships, cooperation', 'effects': 'Harmonious relationships, successful partnerships, cooperative nature'},
        7: {'domain': 'Transformation, occult, mysteries', 'effects': 'Interest in mysteries, transformative experiences, occult knowledge'},
        8: {'domain': 'Philosophy, spirituality, higher learning', 'effects': 'Spiritual wisdom, philosophical insights, higher education'},
        9: {'domain': 'Career, reputation, public recognition', 'effects': 'Public recognition, career success, authoritative position'},
        10: {'domain': 'Gains, friendships, social networks', 'effects': 'Influential friends, multiple income sources, social leadership'},
        11: {'domain': 'Spirituality, foreign connections, charity', 'effects': 'Charitable nature, foreign travels, spiritual expenses'},
        12: {'domain': 'Self-renewal, fresh starts', 'effects': 'Continuous self-renewal, new beginnings, personal growth'}
    },
    'Leo': {
        1: {'domain': 'Royalty, authority, leadership', 'effects': 'Royal bearing, natural authority, leadership qualities, commanding presence'},
        2: {'domain': 'Wealth accumulation, resources', 'effects': 'Multiple income sources, financial stability, resource management'},
        3: {'domain': 'Communication, skills, siblings', 'effects': 'Excellent communication, skilled expression, sibling support'},
        4: {'domain': 'Home, happiness, property', 'effects': 'Beautiful homes, domestic happiness, property ownership'},
        5: {'domain': 'Entertainment, creativity, children', 'effects': 'Creative talents, entertainment success, creative children'},
        6: {'domain': 'Service, health, competition', 'effects': 'Competitive success, health consciousness, service leadership'},
        7: {'domain': 'Partnerships, marriage, cooperation', 'effects': 'Royal partnerships, marriage success, business cooperation'},
        8: {'domain': 'Transformation, research, occult', 'effects': 'Transformative leadership, research abilities, hidden knowledge'},
        9: {'domain': 'Philosophy, higher learning, luck', 'effects': 'Philosophical wisdom, higher education, fortunate outcomes'},
        10: {'domain': 'Career, reputation, authority', 'effects': 'Authoritative career, excellent reputation, leadership positions'},
        11: {'domain': 'Gains, networks, achievements', 'effects': 'Achievement recognition, influential networks, multiple gains'},
        12: {'domain': 'Spirituality, charity, foreign connections', 'effects': 'Spiritual leadership, charitable works, international connections'}
    },
    'Virgo': {
        1: {'domain': 'Service, perfection, analysis', 'effects': 'Service-oriented nature, perfectionist approach, analytical mind, attention to detail'},
        2: {'domain': 'Relationships, beauty, partnerships', 'effects': 'Harmonious relationships, aesthetic sense, partnership success'},
        3: {'domain': 'Transformation, research, occult', 'effects': 'Research abilities, transformative insights, occult interests'},
        4: {'domain': 'Philosophy, teaching, higher wisdom', 'effects': 'Teaching abilities, philosophical nature, wisdom sharing'},
        5: {'domain': 'Discipline, structure, responsibility', 'effects': 'Disciplined approach, structured methods, responsible service'},
        6: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Innovative service methods, humanitarian approach, network building'},
        7: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Compassionate service, intuitive healing, spiritual practices'},
        8: {'domain': 'Leadership, energy, new initiatives', 'effects': 'Leadership in service, energetic approach, new service methods'},
        9: {'domain': 'Material stability, persistence, growth', 'effects': 'Steady service growth, persistent efforts, material stability'},
        10: {'domain': 'Communication, versatility, skills', 'effects': 'Skilled communication, versatile service abilities, multiple talents'},
        11: {'domain': 'Emotional intelligence, nurturing service', 'effects': 'Nurturing approach to service, emotional healing, caring methods'},
        12: {'domain': 'Creative service, entertainment, joy', 'effects': 'Creative service methods, joyful service, entertainment in healing'}
    },
    'Libra': {
        1: {'domain': 'Balance, beauty, harmony', 'effects': 'Harmonious personality, aesthetic sense, diplomatic nature, balanced approach'},
        2: {'domain': 'Transformation, research, mysteries', 'effects': 'Deep research abilities, transformative insights, interest in mysteries'},
        3: {'domain': 'Philosophy, higher learning, teaching', 'effects': 'Philosophical wisdom, teaching abilities, higher education'},
        4: {'domain': 'Discipline, structure, responsibility', 'effects': 'Disciplined approach, structured methods, responsible behavior'},
        5: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Innovative thinking, humanitarian approach, network leadership'},
        6: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual inclinations, intuitive abilities, compassionate nature'},
        7: {'domain': 'Leadership, energy, initiative', 'effects': 'Leadership qualities, energetic approach, initiative taking'},
        8: {'domain': 'Material stability, persistence', 'effects': 'Material balance, persistent efforts, steady growth'},
        9: {'domain': 'Communication, versatility, skills', 'effects': 'Diplomatic communication, versatile skills, social abilities'},
        10: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Emotional balance, nurturing relationships, caring disposition'},
        11: {'domain': 'Creativity, entertainment, joy', 'effects': 'Creative expression, entertainment abilities, joyful nature'},
        12: {'domain': 'Service, health, perfection', 'effects': 'Service through beauty, health consciousness, perfectionist approach'}
    },
    'Scorpio': {
        1: {'domain': 'Intensity, transformation, power', 'effects': 'Powerful personality, transformative abilities, intense nature, occult knowledge'},
        2: {'domain': 'Philosophy, higher learning, teaching', 'effects': 'Philosophical depth, teaching abilities, higher wisdom'},
        3: {'domain': 'Discipline, structure, responsibility', 'effects': 'Disciplined transformation, structured approach, responsible power'},
        4: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Innovative transformation, humanitarian approach, network power'},
        5: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual transformation, intuitive powers, compassionate depth'},
        6: {'domain': 'Leadership, energy, initiative', 'effects': 'Transformative leadership, energetic power, initiative in change'},
        7: {'domain': 'Material stability, persistence', 'effects': 'Material transformation, persistent power, steady intensity'},
        8: {'domain': 'Communication, versatility, skills', 'effects': 'Powerful communication, versatile transformation, skilled intensity'},
        9: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Emotional transformation, nurturing power, caring intensity'},
        10: {'domain': 'Creativity, entertainment, joy', 'effects': 'Creative transformation, powerful entertainment, joyful intensity'},
        11: {'domain': 'Service, health, perfection', 'effects': 'Transformative service, healing power, perfectionist intensity'},
        12: {'domain': 'Balance, beauty, harmony', 'effects': 'Balanced transformation, beautiful change, harmonious intensity'}
    },
    'Sagittarius': {
        1: {'domain': 'Wisdom, expansion, philosophy', 'effects': 'Wise personality, expansive thinking, philosophical nature, higher knowledge'},
        2: {'domain': 'Discipline, structure, responsibility', 'effects': 'Disciplined wisdom, structured philosophy, responsible expansion'},
        3: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Innovative wisdom, humanitarian philosophy, network expansion'},
        4: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual wisdom, intuitive philosophy, compassionate expansion'},
        5: {'domain': 'Leadership, energy, initiative', 'effects': 'Wise leadership, energetic philosophy, initiative in wisdom'},
        6: {'domain': 'Material stability, persistence', 'effects': 'Material wisdom, persistent philosophy, steady expansion'},
        7: {'domain': 'Communication, versatility, skills', 'effects': 'Wise communication, versatile philosophy, skilled expansion'},
        8: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Emotional wisdom, nurturing philosophy, caring expansion'},
        9: {'domain': 'Creativity, entertainment, joy', 'effects': 'Creative wisdom, philosophical entertainment, joyful expansion'},
        10: {'domain': 'Service, health, perfection', 'effects': 'Wise service, philosophical health, perfectionist expansion'},
        11: {'domain': 'Balance, beauty, harmony', 'effects': 'Balanced wisdom, beautiful philosophy, harmonious expansion'},
        12: {'domain': 'Transformation, research, mysteries', 'effects': 'Transformative wisdom, philosophical research, mysterious expansion'}
    },
    'Capricorn': {
        1: {'domain': 'Discipline, ambition, structure', 'effects': 'Disciplined approach, ambitious goals, structured personality, methodical nature'},
        2: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Innovative discipline, humanitarian structure, network building'},
        3: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual discipline, intuitive structure, compassionate ambition'},
        4: {'domain': 'Leadership, energy, initiative', 'effects': 'Disciplined leadership, energetic structure, ambitious initiative'},
        5: {'domain': 'Material stability, persistence', 'effects': 'Material discipline, persistent structure, stable ambition'},
        6: {'domain': 'Communication, versatility, skills', 'effects': 'Disciplined communication, structured versatility, ambitious skills'},
        7: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Emotional discipline, structured nurturing, ambitious caring'},
        8: {'domain': 'Creativity, entertainment, joy', 'effects': 'Disciplined creativity, structured entertainment, ambitious joy'},
        9: {'domain': 'Service, health, perfection', 'effects': 'Disciplined service, structured health, ambitious perfection'},
        10: {'domain': 'Balance, beauty, harmony', 'effects': 'Disciplined balance, structured beauty, ambitious harmony'},
        11: {'domain': 'Transformation, research, mysteries', 'effects': 'Disciplined transformation, structured research, ambitious mysteries'},
        12: {'domain': 'Philosophy, higher learning, teaching', 'effects': 'Disciplined philosophy, structured learning, ambitious teaching'}
    },
    'Aquarius': {
        1: {'domain': 'Innovation, humanitarian, networking', 'effects': 'Innovative thinking, humanitarian approach, network leadership, progressive nature'},
        2: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual innovation, intuitive networking, compassionate progress'},
        3: {'domain': 'Leadership, energy, initiative', 'effects': 'Innovative leadership, energetic networking, progressive initiative'},
        4: {'domain': 'Material stability, persistence', 'effects': 'Material innovation, persistent networking, stable progress'},
        5: {'domain': 'Communication, versatility, skills', 'effects': 'Innovative communication, versatile networking, progressive skills'},
        6: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Emotional innovation, nurturing networks, progressive caring'},
        7: {'domain': 'Creativity, entertainment, joy', 'effects': 'Creative innovation, entertaining networks, progressive joy'},
        8: {'domain': 'Service, health, perfection', 'effects': 'Innovative service, networked health, progressive perfection'},
        9: {'domain': 'Balance, beauty, harmony', 'effects': 'Innovative balance, networked beauty, progressive harmony'},
        10: {'domain': 'Transformation, research, mysteries', 'effects': 'Innovative transformation, networked research, progressive mysteries'},
        11: {'domain': 'Philosophy, higher learning, teaching', 'effects': 'Innovative philosophy, networked learning, progressive teaching'},
        12: {'domain': 'Discipline, structure, responsibility', 'effects': 'Innovative discipline, networked structure, progressive responsibility'}
    },
    'Pisces': {
        1: {'domain': 'Spirituality, intuition, compassion', 'effects': 'Spiritual inclinations, intuitive abilities, compassionate nature, psychic sensitivity'},
        2: {'domain': 'Leadership, energy, initiative', 'effects': 'Spiritual leadership, energetic compassion, intuitive initiative'},
        3: {'domain': 'Material stability, persistence', 'effects': 'Spiritual materialism, persistent compassion, stable intuition'},
        4: {'domain': 'Communication, versatility, skills', 'effects': 'Spiritual communication, versatile compassion, intuitive skills'},
        5: {'domain': 'Emotional intelligence, nurturing', 'effects': 'Spiritual emotions, nurturing compassion, intuitive caring'},
        6: {'domain': 'Creativity, entertainment, joy', 'effects': 'Spiritual creativity, compassionate entertainment, intuitive joy'},
        7: {'domain': 'Service, health, perfection', 'effects': 'Spiritual service, compassionate healing, intuitive perfection'},
        8: {'domain': 'Balance, beauty, harmony', 'effects': 'Spiritual balance, compassionate beauty, intuitive harmony'},
        9: {'domain': 'Transformation, research, mysteries', 'effects': 'Spiritual transformation, compassionate research, intuitive mysteries'},
        10: {'domain': 'Philosophy, higher learning, teaching', 'effects': 'Spiritual philosophy, compassionate teaching, intuitive wisdom'},
        11: {'domain': 'Discipline, structure, responsibility', 'effects': 'Spiritual discipline, compassionate structure, intuitive responsibility'},
        12: {'domain': 'Innovation, networking, humanitarian work', 'effects': 'Spiritual innovation, compassionate networking, intuitive humanitarian work'}
    }
}

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

def is_kendra_position(house1, house2):
    """
    FIXED: Check if two houses are in Kendra positions relative to each other.
    Kendra positions are 1st, 4th, 7th, 10th from each other.
    """
    if house1 == house2:
        return True  # Same house (1st from each other)
    
    # Calculate Kendra positions from house1
    kendra_positions = []
    
    # 4th house from house1
    fourth = house1 + 3
    if fourth > 12:
        fourth -= 12
    kendra_positions.append(fourth)
    
    # 7th house from house1  
    seventh = house1 + 6
    if seventh > 12:
        seventh -= 12
    kendra_positions.append(seventh)
    
    # 10th house from house1
    tenth = house1 + 9
    if tenth > 12:
        tenth -= 12
    kendra_positions.append(tenth)
    
    return house2 in kendra_positions

def assess_planetary_strength(planet_name, longitude, house, retrograde):
    """
    COMPLETELY CORRECTED: Accurate planetary strength assessment.
    """
    sign_index = int(longitude // 30)
    strength_factors = {
        'own_sign': False,
        'exalted': False,
        'debilitated': False,
        'friend_sign': False,
        'enemy_sign': False,
        'neutral_sign': False,
        'kendra_house': house in [1, 4, 7, 10],
        'trikona_house': house in [1, 5, 9],
        'upachaya_house': house in [3, 6, 10, 11],
        'dusthana_house': house in [6, 8, 12],
        'retrograde': retrograde == 'R',
        'dignity_score': 0,
        'house_score': 0,
        'total_score': 0,
        'strong': False
    }
    
    # CORRECTED Jupiter dignities
    if planet_name == 'Jupiter':
        if sign_index == 3:  # Cancer (exalted)
            strength_factors['exalted'] = True
            strength_factors['dignity_score'] = 5
        elif sign_index in [8, 11]:  # Sagittarius, Pisces (own signs)
            strength_factors['own_sign'] = True
            strength_factors['dignity_score'] = 4
        elif sign_index in [0, 3, 7]:  # Aries, Cancer, Scorpio (friends)
            strength_factors['friend_sign'] = True
            strength_factors['dignity_score'] = 2
        elif sign_index == 5:  # Virgo (debilitated) - CRITICAL
            strength_factors['debilitated'] = True
            strength_factors['dignity_score'] = -4
        elif sign_index in [1, 2, 6]:  # Taurus, Gemini, Libra (enemies)
            strength_factors['enemy_sign'] = True
            strength_factors['dignity_score'] = -1
        else:  # Leo, Capricorn, Aquarius (neutral)
            strength_factors['neutral_sign'] = True
            strength_factors['dignity_score'] = 1
    
    # CORRECTED Moon dignities  
    elif planet_name == 'Moon':
        if sign_index == 1:  # Taurus (exalted)
            strength_factors['exalted'] = True
            strength_factors['dignity_score'] = 5
        elif sign_index == 3:  # Cancer (own sign)
            strength_factors['own_sign'] = True
            strength_factors['dignity_score'] = 4
        elif sign_index in [0, 4, 8, 11]:  # Aries, Leo, Sagittarius, Pisces (friends)
            strength_factors['friend_sign'] = True
            strength_factors['dignity_score'] = 2
        elif sign_index == 7:  # Scorpio (debilitated)
            strength_factors['debilitated'] = True
            strength_factors['dignity_score'] = -4
        elif sign_index in [2, 5, 9, 10]:  # Gemini, Virgo, Capricorn, Aquarius (enemies)
            strength_factors['enemy_sign'] = True
            strength_factors['dignity_score'] = -1  # Moon in Virgo = enemy sign
        else:  # Libra (neutral)
            strength_factors['neutral_sign'] = True
            strength_factors['dignity_score'] = 1
    
    # CORRECTED House scoring
    if strength_factors['kendra_house'] and strength_factors['trikona_house']:
        # Houses 1 and 10 are both Kendra and Trikona - give maximum benefit
        strength_factors['house_score'] = 4
    elif strength_factors['trikona_house']:
        # Houses 5 and 9 are Trikona only
        strength_factors['house_score'] = 3
    elif strength_factors['kendra_house']:
        # Houses 4 and 7 are Kendra only  
        strength_factors['house_score'] = 2
    elif strength_factors['upachaya_house']:
        # Houses 3, 6, 11 are Upachaya
        strength_factors['house_score'] = 1
    elif strength_factors['dusthana_house']:
        # Houses 6, 8, 12 are Dusthana (6 counted as Upachaya above)
        strength_factors['house_score'] = -2
    else:
        # Houses 2 is neutral
        strength_factors['house_score'] = 0
    
    # Retrograde penalty
    retrograde_penalty = -1 if strength_factors['retrograde'] else 0
    
    # Calculate total score
    strength_factors['total_score'] = (
        strength_factors['dignity_score'] + 
        strength_factors['house_score'] + 
        retrograde_penalty
    )
    
    # CORRECTED: Determine if planet is strong
    strength_factors['strong'] = (
        strength_factors['total_score'] >= 3 and 
        not strength_factors['debilitated']
    )
    
    return strength_factors

def check_malefic_influences(planet_positions, jupiter_house, moon_house):
    """
    FIXED: Comprehensive malefic influence detection with proper conjunction logic.
    """
    influences = {
        'conjunctions': [],
        'aspects': [],
        'overall_effect': 'neutral',
        'detailed_effects': [],
        'conjunction_count': 0,
        'aspect_count': 0
    }
    
    malefic_planets = ['Mars', 'Saturn', 'Rahu', 'Ketu']
    
    for planet in malefic_planets:
        if planet in planet_positions:
            planet_house = planet_positions[planet]['house']
            
            # FIXED: Check conjunctions (same house) - COUNT EACH SEPARATELY
            if planet_house == jupiter_house:
                influences['conjunctions'].append(f"{planet} conjunct Jupiter")
                influences['detailed_effects'].append(f"{planet} conjunction severely affects Jupiter's benefic nature")
                influences['conjunction_count'] += 1
            
            if planet_house == moon_house:
                influences['conjunctions'].append(f"{planet} conjunct Moon")
                influences['detailed_effects'].append(f"{planet} conjunction disturbs Moon's emotional stability")
                influences['conjunction_count'] += 1
            
            # Check 7th house aspects (opposition)
            jupiter_aspect_house = (jupiter_house + 6) % 12
            if jupiter_aspect_house == 0:
                jupiter_aspect_house = 12
                
            moon_aspect_house = (moon_house + 6) % 12  
            if moon_aspect_house == 0:
                moon_aspect_house = 12
            
            if planet_house == jupiter_aspect_house:
                influences['aspects'].append(f"{planet} aspects Jupiter")
                influences['detailed_effects'].append(f"{planet} aspect creates tension for Jupiter")
                influences['aspect_count'] += 1
                
            if planet_house == moon_aspect_house:
                influences['aspects'].append(f"{planet} aspects Moon")
                influences['detailed_effects'].append(f"{planet} aspect disturbs Moon's peace")
                influences['aspect_count'] += 1
    
    # CORRECTED: Determine overall affliction level based on total influences
    total_conjunctions = influences['conjunction_count']
    total_aspects = influences['aspect_count']
    
    if total_conjunctions >= 3:  # Triple conjunction or more
        influences['overall_effect'] = 'extremely_afflicted'
    elif total_conjunctions == 2:  # Double conjunction
        influences['overall_effect'] = 'severely_afflicted'
    elif total_conjunctions == 1 and total_aspects >= 2:
        influences['overall_effect'] = 'severely_afflicted'
    elif total_conjunctions == 1 and total_aspects == 1:
        influences['overall_effect'] = 'heavily_afflicted'
    elif total_conjunctions == 1:
        influences['overall_effect'] = 'moderately_afflicted'
    elif total_aspects >= 3:
        influences['overall_effect'] = 'heavily_afflicted'
    elif total_aspects == 2:
        influences['overall_effect'] = 'moderately_afflicted'
    elif total_aspects == 1:
        influences['overall_effect'] = 'mildly_afflicted'
    
    return influences

def calculate_yoga_strength_classification(total_score, jupiter_strong, moon_strong, jupiter_debilitated, moon_debilitated, malefic_effect):
    """
    COMPLETELY FIXED: Accurate yoga strength classification with proper penalties.
    """
    # Base strength classification from total score
    if total_score >= 10:
        base_strength = "Exceptional"
    elif total_score >= 7:
        base_strength = "Very Strong" 
    elif total_score >= 5:
        base_strength = "Strong"
    elif total_score >= 3:
        base_strength = "Moderate"
    elif total_score >= 1:
        base_strength = "Weak"
    elif total_score >= -2:
        base_strength = "Poor"
    else:
        base_strength = "Afflicted"
    
    # CRITICAL RULE: Jupiter debilitation severely limits yoga strength
    if jupiter_debilitated:
        if moon_debilitated:
            return "Extremely Afflicted"  # Both debilitated
        else:
            # Jupiter debilitation caps maximum yoga strength
            if base_strength in ["Exceptional", "Very Strong", "Strong"]:
                return "Poor"
            elif base_strength in ["Moderate", "Weak"]:
                return "Afflicted"
            else:
                return "Severely Afflicted"
    
    # Moon debilitation penalty (less severe than Jupiter)
    if moon_debilitated:
        if base_strength == "Exceptional":
            base_strength = "Strong"
        elif base_strength == "Very Strong":
            base_strength = "Moderate"
        elif base_strength == "Strong":
            base_strength = "Weak"
        elif base_strength == "Moderate":
            base_strength = "Poor"
        else:
            base_strength = "Afflicted"
    
    # Apply malefic affliction penalties
    if malefic_effect == 'extremely_afflicted':
        return "Severely Afflicted"  # Triple conjunction overrides everything
    elif malefic_effect == 'severely_afflicted':
        if base_strength in ["Exceptional", "Very Strong"]:
            return "Weak"
        elif base_strength in ["Strong", "Moderate"]:
            return "Poor"
        else:
            return "Severely Afflicted"
    elif malefic_effect == 'heavily_afflicted':
        if base_strength == "Exceptional":
            return "Strong"
        elif base_strength == "Very Strong":
            return "Moderate"
        elif base_strength == "Strong":
            return "Weak"
        elif base_strength == "Moderate":
            return "Poor"
        else:
            return "Afflicted"
    elif malefic_effect == 'moderately_afflicted':
        if base_strength == "Exceptional":
            return "Very Strong"
        elif base_strength == "Very Strong":
            return "Strong"
        elif base_strength == "Strong":
            return "Moderate"
        elif base_strength == "Moderate":
            return "Weak"
        else:
            return base_strength
    elif malefic_effect == 'mildly_afflicted':
        if base_strength == "Exceptional":
            return "Very Strong"
        else:
            return base_strength
    
    # No significant afflictions
    return base_strength

def get_house_relationship_description(jupiter_house, moon_house):
    """
    FIXED: Accurate house relationship description.
    """
    if jupiter_house == moon_house:
        return f"Conjunction in House {jupiter_house}"
    
    # Calculate which Kendra position Moon is from Jupiter
    diff = (moon_house - jupiter_house) % 12
    if diff == 0:
        return f"Conjunction in House {jupiter_house}"
    elif diff == 3:
        return f"4th House Relationship (Jupiter in {jupiter_house}, Moon in {moon_house})"
    elif diff == 6:
        return f"7th House Opposition (Jupiter in {jupiter_house}, Moon in {moon_house})"
    elif diff == 9:
        return f"10th House Relationship (Jupiter in {jupiter_house}, Moon in {moon_house})"
    else:
        return f"Non-Kendra Position (Jupiter in {jupiter_house}, Moon in {moon_house})"

def get_comprehensive_effects(ascendant_sign, jupiter_house, moon_house, jupiter_sign, moon_sign, 
                            jupiter_strength, moon_strength, malefic_influences, yoga_strength):
    """
    FIXED: Comprehensive effects with proper ascendant-specific interpretations.
    """
    # Get ascendant-specific house effects
    ascendant_effects = COMPLETE_HOUSE_EFFECTS.get(ascendant_sign, {})
    
    jupiter_house_effects = ascendant_effects.get(jupiter_house, {
        'domain': 'General Jupiter Effects', 
        'effects': 'Wisdom, knowledge, and expansion in this area'
    })
    
    if jupiter_house == moon_house:
        moon_house_effects = "Same as Jupiter (conjunction creates combined energy focus)"
    else:
        moon_house_effects = ascendant_effects.get(moon_house, {
            'domain': 'General Moon Effects', 
            'effects': 'Emotional intelligence and nurturing in this area'
        })
    
    # Enhanced sign combination effects
    if jupiter_sign == moon_sign:
        if jupiter_sign == "Virgo":
            sign_effect = "Both planets in Virgo create analytical wisdom and practical intelligence, but Jupiter's debilitation severely limits expansion and growth potential"
        elif jupiter_sign == "Cancer":
            sign_effect = "Both planets in Cancer create exceptional emotional wisdom and nurturing intelligence with maximum spiritual and material benefits"
        elif jupiter_sign == "Scorpio":
            sign_effect = "Both planets in Scorpio create intense transformative wisdom, but Moon's debilitation creates emotional instability and inner conflicts"
        elif jupiter_sign == "Taurus":
            sign_effect = "Both planets in Taurus create stable material wisdom with Moon's exaltation providing emotional strength, though Jupiter is in enemy territory"
        else:
            sign_effect = f"Both planets in {jupiter_sign} create focused and concentrated energy with blended effects of wisdom and emotion"
    else:
        jupiter_effects = {
            'Cancer': 'exalted wisdom and spiritual guidance',
            'Sagittarius': 'own sign strength with philosophical wisdom',
            'Pisces': 'own sign strength with intuitive wisdom',
            'Virgo': 'debilitated wisdom with limited expansion',
            'Capricorn': 'disciplined but restricted wisdom'
        }
        
        moon_effects = {
            'Taurus': 'exalted emotional stability and material comfort',
            'Cancer': 'own sign emotional intelligence and nurturing ability',
            'Scorpio': 'debilitated emotional intensity and transformation challenges',
            'Virgo': 'analytical but critical emotional responses'
        }
        
        jupiter_effect = jupiter_effects.get(jupiter_sign, f'neutral wisdom influence from {jupiter_sign}')
        moon_effect = moon_effects.get(moon_sign, f'standard emotional influence from {moon_sign}')
        sign_effect = f"Jupiter provides {jupiter_effect}, while Moon contributes {moon_effect}"
    
    # Detailed strength assessment
    if jupiter_strength['strong'] and moon_strength['strong']:
        strength_assessment = "Very strong yoga with maximum benefits - both planets are well-placed and powerful"
    elif jupiter_strength['strong'] and not moon_strength['strong']:
        if moon_strength['debilitated']:
            strength_assessment = "Mixed yoga - strong Jupiter provides wisdom but debilitated Moon creates emotional instability"
        else:
            strength_assessment = "Moderately strong yoga - Jupiter provides good wisdom but weak Moon limits emotional receptivity"
    elif not jupiter_strength['strong'] and moon_strength['strong']:
        if jupiter_strength['debilitated']:
            strength_assessment = "Severely weakened yoga - debilitated Jupiter cannot provide proper guidance despite strong Moon"
        else:
            strength_assessment = "Moderately strong yoga - strong Moon provides emotional intelligence but weak Jupiter limits wisdom"
    elif jupiter_strength['debilitated'] and moon_strength['debilitated']:
        strength_assessment = "Extremely afflicted yoga - both planets debilitated, creating confusion, delays, and minimal benefits"
    elif jupiter_strength['debilitated']:
        strength_assessment = "Severely weakened yoga - Jupiter's debilitation is the primary limiting factor, drastically reducing wisdom, expansion, and spiritual growth"
    elif moon_strength['debilitated']:
        strength_assessment = "Significantly weakened yoga - Moon's debilitation creates emotional instability, reducing receptivity to Jupiter's wisdom"
    else:
        strength_assessment = "Average strength yoga with moderate benefits and steady but limited progress"
    
    # Malefic influence assessment
    malefic_assessment = ""
    if malefic_influences['overall_effect'] == 'extremely_afflicted':
        malefic_assessment = f"Extremely afflicted - {malefic_influences['conjunction_count']} malefic conjunctions create severe obstacles, major delays, and substantial reduction in benefits"
    elif malefic_influences['overall_effect'] == 'severely_afflicted':
        malefic_assessment = f"Severely afflicted - {malefic_influences['conjunction_count']} conjunctions and {malefic_influences['aspect_count']} aspects create significant obstacles and delays"
    elif malefic_influences['overall_effect'] == 'heavily_afflicted':
        malefic_assessment = "Heavily afflicted by malefics - substantial obstacles, delays, and challenges in manifestation"
    elif malefic_influences['overall_effect'] == 'moderately_afflicted':
        malefic_assessment = "Moderately afflicted by malefics - some obstacles and periodic delays"
    elif malefic_influences['overall_effect'] == 'mildly_afflicted':
        malefic_assessment = "Mildly afflicted by malefics - minor challenges and occasional obstacles"
    
    # Generate comprehensive prediction
    prediction_parts = []
    prediction_parts.append(f"This Gaja Kesari Yoga primarily influences {jupiter_house_effects['domain']}")
    
    if isinstance(moon_house_effects, dict):
        prediction_parts.append(f"and {moon_house_effects['domain']}")
    elif jupiter_house == moon_house:
        prediction_parts.append("with concentrated energy in this single area")
    
    prediction_parts.append(f"Sign analysis: {sign_effect}")
    prediction_parts.append(f"Strength evaluation: {strength_assessment}")
    
    if malefic_assessment:
        prediction_parts.append(f"Affliction impact: {malefic_assessment}")
    
    # Add realistic outcome predictions
    if yoga_strength in ["Exceptional", "Very Strong"]:
        prediction_parts.append("Expected outcomes: This yoga will manifest substantial benefits, recognition, wealth, and success with proper timing.")
    elif yoga_strength == "Strong":
        prediction_parts.append("Expected outcomes: This yoga will bring good benefits, moderate success, and steady progress.")
    elif yoga_strength == "Moderate":
        prediction_parts.append("Expected outcomes: This yoga will provide average benefits with gradual improvement over time.")
    elif yoga_strength == "Weak":
        prediction_parts.append("Expected outcomes: This yoga will give limited benefits, but some positive effects are still possible with effort.")
    elif yoga_strength == "Poor":
        prediction_parts.append("Expected outcomes: This yoga provides minimal benefits with significant effort required for any positive results.")
    elif yoga_strength == "Afflicted":
        prediction_parts.append("Expected outcomes: This yoga faces major obstacles and may require remedies before benefits can manifest.")
    else:
        prediction_parts.append("Expected outcomes: This yoga is severely compromised and may bring more challenges than benefits without proper remedial measures.")
    
    return {
        'jupiter_house_effects': jupiter_house_effects,
        'moon_house_effects': moon_house_effects,
        'sign_combination_effects': sign_effect,
        'strength_assessment': strength_assessment,
        'malefic_influences': malefic_assessment,
        'malefic_details': malefic_influences,
        'overall_prediction': " ".join(prediction_parts),
        'specific_effects': generate_specific_effects(ascendant_sign, jupiter_house, moon_house, yoga_strength)
    }

def generate_specific_effects(ascendant_sign, jupiter_house, moon_house, yoga_strength):
    """Generate specific effects based on house positions and yoga strength."""
    effects = []
    
    # Base effects from house combinations for Virgo Ascendant
    house_effects_map = {
        1: "Enhanced personality, leadership abilities, and overall life direction",
        2: "Improved wealth accumulation, speech quality, and family relationships", 
        3: "Better communication skills, sibling relationships, and short ventures",
        4: "Benefits to home, property, mother's wellbeing, and emotional security",
        5: "Success in education, creativity, children's welfare, and speculative gains",
        6: "Victory over enemies, better health, and success in service/competition",
        7: "Harmonious partnerships, marriage benefits, and business success",
        8: "Transformative experiences, occult knowledge, and longevity",
        9: "Spiritual growth, higher learning, father's support, and good fortune",
        10: "Career advancement, public recognition, and professional authority",
        11: "Financial gains, influential friendships, and wish fulfillment",
        12: "Spiritual inclinations, foreign connections, and charitable activities"
    }
    
    # Add effects based on planets' house positions
    if jupiter_house in house_effects_map:
        effects.append(f"Jupiter influence: {house_effects_map[jupiter_house]}")
    
    if moon_house != jupiter_house and moon_house in house_effects_map:
        effects.append(f"Moon influence: {house_effects_map[moon_house]}")
    elif moon_house == jupiter_house:
        effects.append(f"Combined Jupiter-Moon influence: Intensified {house_effects_map[jupiter_house].lower()}")
    
    # Modify based on yoga strength
    strength_modifiers = {
        "Exceptional": "Exceptional and life-changing",
        "Very Strong": "Very strong and transformative", 
        "Strong": "Strong and beneficial",
        "Moderate": "Moderate and steady",
        "Weak": "Limited but present",
        "Poor": "Minimal and requiring effort",
        "Afflicted": "Delayed and challenging",
        "Severely Afflicted": "Severely delayed and obstacle-ridden",
        "Extremely Afflicted": "Extremely compromised and potentially harmful"
    }
    
    modifier = strength_modifiers.get(yoga_strength, "Variable")
    effects = [f"{modifier} {effect.lower()}" for effect in effects]
    
    return effects

def calculate_comprehensive_gaja_kesari_yoga(planet_positions, ascendant_sign):
    """
    COMPLETELY CORRECTED: Calculate comprehensive Gaja Kesari Yoga with perfect accuracy.
    """
    jupiter_data = planet_positions.get('Jupiter')
    moon_data = planet_positions.get('Moon')
    
    if not jupiter_data or not moon_data:
        return {"yoga_present": False, "error": "Jupiter or Moon data not found"}
    
    jupiter_house = jupiter_data['house']
    moon_house = moon_data['house']
    jupiter_lon = jupiter_data['longitude']
    moon_lon = moon_data['longitude']
    jupiter_retro = jupiter_data['retrograde']
    moon_retro = moon_data['retrograde']
    jupiter_sign = jupiter_data['sign']
    moon_sign = moon_data['sign']
    
    # Check yoga formation with corrected Kendra logic
    yoga_present = is_kendra_position(jupiter_house, moon_house)
    
    if not yoga_present:
        return {
            "yoga_present": False, 
            "reason": f"Jupiter (House {jupiter_house}) and Moon (House {moon_house}) are not in Kendra positions",
            "explanation": "Gaja Kesari Yoga requires Jupiter and Moon to be in 1st, 4th, 7th, or 10th house from each other"
        }
    
    # Assess planetary strengths with corrected logic
    jupiter_strength = assess_planetary_strength('Jupiter', jupiter_lon, jupiter_house, jupiter_retro)
    moon_strength = assess_planetary_strength('Moon', moon_lon, moon_house, moon_retro)
    
    # Check malefic influences with improved detection
    malefic_influences = check_malefic_influences(planet_positions, jupiter_house, moon_house)
    
    # Calculate base yoga strength score
    base_score = jupiter_strength['total_score'] + moon_strength['total_score']
    
    # Apply malefic penalties - CORRECTED
    malefic_penalty = 0
    if malefic_influences['overall_effect'] == 'extremely_afflicted':
        malefic_penalty = -6  # Triple conjunction
    elif malefic_influences['overall_effect'] == 'severely_afflicted':
        malefic_penalty = -4  # Double conjunction or conjunction + aspects
    elif malefic_influences['overall_effect'] == 'heavily_afflicted':
        malefic_penalty = -3  # Single conjunction + multiple aspects
    elif malefic_influences['overall_effect'] == 'moderately_afflicted':
        malefic_penalty = -2  # Single conjunction or multiple aspects
    elif malefic_influences['overall_effect'] == 'mildly_afflicted':
        malefic_penalty = -1  # Single aspect
    
    total_score = base_score + malefic_penalty
    
    # Determine final yoga strength with accurate classification
    final_strength = calculate_yoga_strength_classification(
        total_score,
        jupiter_strength['strong'],
        moon_strength['strong'], 
        jupiter_strength['debilitated'],
        moon_strength['debilitated'],
        malefic_influences['overall_effect']
    )
    
    # Get proper house relationship description
    house_relationship = get_house_relationship_description(jupiter_house, moon_house)
    
    # Get comprehensive effects with corrected interpretations
    comprehensive_effects = get_comprehensive_effects(
        ascendant_sign, jupiter_house, moon_house, jupiter_sign, moon_sign,
        jupiter_strength, moon_strength, malefic_influences, final_strength
    )
    
    return {
        "yoga_present": True,
        "yoga_type": "Gaja Kesari Yoga",
        "yoga_strength": final_strength,
        "base_strength_score": base_score,
        "malefic_penalty": malefic_penalty,
        "final_strength_score": total_score,
        "house_relationship": house_relationship,
        "ascendant_sign": ascendant_sign,
        "jupiter_analysis": {
            "house": jupiter_house,
            "sign": jupiter_sign,
            "degrees": jupiter_data['degrees'],
            "retrograde": jupiter_retro,
            "strength_factors": jupiter_strength,
            "strength_summary": f"Total Score: {jupiter_strength['total_score']} ({'Strong' if jupiter_strength['strong'] else 'Weak'})"
        },
        "moon_analysis": {
            "house": moon_house,
            "sign": moon_sign,
            "degrees": moon_data['degrees'],
            "retrograde": moon_retro,
            "strength_factors": moon_strength,
            "strength_summary": f"Total Score: {moon_strength['total_score']} ({'Strong' if moon_strength['strong'] else 'Weak'})"
        },
        "malefic_influences": malefic_influences,
        "comprehensive_effects": comprehensive_effects,
        "timing_analysis": {
            "best_periods": f"Jupiter and Moon dashas/antardashas, particularly during periods when afflicting planets are weak",
            "activation_transits": f"When Jupiter transits houses {jupiter_house}, {moon_house}, or signs {jupiter_sign}, {moon_sign}",
            "peak_effects": f"During {jupiter_sign} and {moon_sign} transits with supporting dasha periods and minimal malefic influences",
            "remedial_timing": "Perform remedies during Jupiter and Moon horas, especially on Thursdays and Mondays, avoiding Saturn horas"
        },
        "remedial_suggestions": generate_remedial_suggestions(jupiter_strength, moon_strength, final_strength, malefic_influences)
    }

def generate_remedial_suggestions(jupiter_strength, moon_strength, yoga_strength, malefic_influences):
    """Generate comprehensive remedial suggestions based on specific conditions."""
    remedies = {
        "jupiter_remedies": [],
        "moon_remedies": [],
        "malefic_remedies": [],
        "general_yoga_remedies": [],
        "gemstone_suggestions": [],
        "mantra_suggestions": [],
        "charity_suggestions": [],
        "timing_remedies": []
    }
    
    # Jupiter-specific remedies
    if jupiter_strength['debilitated']:
        remedies["jupiter_remedies"].extend([
            "Perform Jupiter remedies every Thursday for 40 days minimum",
            "Donate yellow items, turmeric, chickpeas, and educational books",
            "Respect and serve teachers, gurus, and elderly scholars",
            "Study and recite sacred texts, especially on Thursdays",
            "Feed brahmins and seek their blessings regularly"
        ])
        remedies["gemstone_suggestions"].append("Yellow Sapphire (Pukhraj) after proper astrological consultation")
        remedies["mantra_suggestions"].extend([
            "Om Gurave Namaha (108 times daily)",
            "Brihaspati Mantra: Om Brim Brihaspataye Namaha (108 times)",
            "Jupiter Beej Mantra: Om Gram Greem Graum Sah Gurave Namaha"
        ])
        remedies["charity_suggestions"].append("Donate to educational institutions and libraries on Thursdays")
    elif not jupiter_strength['strong']:
        remedies["jupiter_remedies"].extend([
            "Thursday fasting and Jupiter worship",
            "Donation to educational causes",
            "Teaching or sharing knowledge with others"
        ])
    
    # Moon-specific remedies
    if moon_strength['debilitated']:
        remedies["moon_remedies"].extend([
            "Perform Moon remedies every Monday",
            "Donate white items, milk, rice, and silver",
            "Respect and serve mother and maternal figures",
            "Wear white clothes on Mondays",
            "Avoid consuming milk products on Mondays (fasting)"
        ])
        remedies["gemstone_suggestions"].append("Natural Pearl (Moti) after proper consultation")
        remedies["mantra_suggestions"].extend([
            "Om Chandramase Namaha (108 times daily)",
            "Moon Beej Mantra: Om Shram Shreem Shraum Sah Chandraya Namaha"
        ])
    elif moon_strength['enemy_sign']:
        remedies["moon_remedies"].extend([
            "Monday fasting and Moon worship",
            "Milk donation to needy people",
            "Water offerings to Moon on Monday evenings"
        ])
    
    # Malefic-specific remedies for Saturn conjunction
    if 'Saturn conjunct Jupiter' in malefic_influences.get('conjunctions', []):
        remedies["malefic_remedies"].extend([
            "Perform Saturn remedies on Saturdays to reduce malefic influence",
            "Donate black sesame seeds, iron items, and mustard oil",
            "Recite Hanuman Chalisa daily for protection from Saturn's negative effects",
            "Avoid starting important work during Saturn transits over natal Jupiter"
        ])
    
    if 'Saturn conjunct Moon' in malefic_influences.get('conjunctions', []):
        remedies["malefic_remedies"].extend([
            "Perform special pujas for Moon-Saturn conjunction",
            "Donate to poor and elderly people regularly",
            "Practice meditation and emotional healing techniques"
        ])
    
    # General yoga enhancement remedies
    if yoga_strength in ["Severely Afflicted", "Extremely Afflicted", "Afflicted", "Poor"]:
        remedies["general_yoga_remedies"].extend([
            "Perform Gaja Kesari Yoga specific rituals and pujas",
            "Recite Ganesha mantras for obstacle removal (Ganapati Atharvashirsha)",
            "Worship both Jupiter and Moon together on their respective days",
            "Visit temples dedicated to Jupiter (Brihaspati) and Moon (Chandra)",
            "Perform Rudrabhishek for removing malefic influences"
        ])
        
        remedies["timing_remedies"].extend([
            "Avoid major decisions during Saturn transits over natal planets",
            "Time important activities during Jupiter and Moon favorable periods",
            "Perform remedies during Shukla Paksha (waxing Moon) for better results"
        ])
    
    return remedies

def calculate_planetary_positions(birth_data):
    """Calculate all planetary positions for the given birth data."""
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
        
        planet_positions[planet_name] = {
            'longitude': lon,
            'retrograde': retrograde
        }

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = {
        'longitude': ketu_lon,
        'retrograde': ''
    }

    # Calculate Ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    ascendant_sign = signs[asc_sign_index]

    # Get orientation shift
    orientation_shift = int(birth_data.get('orientation_shift', 0))

    # Calculate houses and add detailed info for each planet
    for planet_name in planet_positions:
        lon = planet_positions[planet_name]['longitude']
        house = get_house(lon, asc_sign_index, orientation_shift=orientation_shift)
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        
        planet_positions[planet_name].update({
            'house': house,
            'sign': sign,
            'sign_index': sign_index,
            'degrees': format_dms(sign_deg)
        })

    return planet_positions, ascendant_sign, ascendant_lon, ayanamsa_value