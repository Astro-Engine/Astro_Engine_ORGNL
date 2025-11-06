# calculations_dhan_yoga.py
from datetime import datetime, timedelta
import swisseph as swe

# ----- Ephemeris path (same as your original) -----
swe.set_ephe_path('astro_api/ephe')

# ----- Constants & Tables (UNCHANGED) -----
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

SIGN_RULERS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun', 5: 'Mercury',
    6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Mercury', 'Moon']
NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']

EXALTATION_SIGNS = {
    'Sun': 0, 'Moon': 1, 'Mars': 9, 'Mercury': 5, 'Jupiter': 3, 'Venus': 11, 'Saturn': 6
}

DEBILITATION_SIGNS = {
    'Sun': 6, 'Moon': 7, 'Mars': 3, 'Mercury': 11, 'Jupiter': 9, 'Venus': 5, 'Saturn': 0
}

PLANETARY_FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'],
    'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Mercury', 'Venus']
}

PLANETARY_ENEMIES = {
    'Sun': ['Venus', 'Saturn'],
    'Moon': ['None'],
    'Mars': ['Mercury'],
    'Mercury': ['Moon'],
    'Jupiter': ['Mercury', 'Venus'],
    'Venus': ['Sun', 'Moon'],
    'Saturn': ['Sun', 'Moon', 'Mars']
}

# ----- Core helpers (UNCHANGED) -----
def get_house(lon, asc_sign_index):
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

def longitude_to_sign(deg):
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = SIGNS[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_house_lord(house_number, asc_sign_index):
    house_sign_index = (asc_sign_index + house_number - 1) % 12
    return SIGN_RULERS[house_sign_index]

def get_all_house_lordships(asc_sign_index):
    lordships = {}
    for house in range(1, 13):
        lord = get_house_lord(house, asc_sign_index)
        if lord not in lordships:
            lordships[lord] = []
        lordships[lord].append(house)
    return lordships

def get_ordinal(num):
    if num == 1: return "1st"
    elif num == 2: return "2nd"
    elif num == 3: return "3rd"
    else: return f"{num}th"

def check_planetary_conjunction(planet_positions, planet1, planet2, orb=10):
    if planet1 not in planet_positions or planet2 not in planet_positions or planet1 == planet2:
        return False
    lon1 = planet_positions[planet1][0]
    lon2 = planet_positions[planet2][0]
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb

def get_exact_conjunction_distance(planet_positions, planet1, planet2):
    if planet1 not in planet_positions or planet2 not in planet_positions:
        return None
    lon1 = planet_positions[planet1][0]
    lon2 = planet_positions[planet2][0]
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff

def check_same_house(planet_houses, planet1, planet2):
    if planet1 not in planet_houses or planet2 not in planet_houses or planet1 == planet2:
        return False
    return planet_houses[planet1] == planet_houses[planet2]

def check_kendra_from_planet(planet_houses, reference_planet, target_planet):
    if reference_planet not in planet_houses or target_planet not in planet_houses:
        return False
    ref_house = planet_houses[reference_planet]
    target_house = planet_houses[target_planet]
    diff = (target_house - ref_house) % 12
    return diff in [0, 3, 6, 9]

def get_planet_dignity_precise(planet_name, planet_positions):
    if planet_name not in planet_positions or planet_name in ['Rahu', 'Ketu']:
        return "Neutral"
    lon, retro = planet_positions[planet_name]
    sign_name, sign_deg, sign_index = longitude_to_sign(lon)

    own_signs = {
        'Sun': [4], 'Moon': [3], 'Mars': [0, 7], 'Mercury': [2, 5],
        'Jupiter': [8, 11], 'Venus': [1, 6], 'Saturn': [9, 10]
    }

    exaltation_ranges = {
        'Sun': (0, 10), 'Moon': (30, 33), 'Mars': (270, 298), 'Mercury': (150, 165),
        'Jupiter': (90, 95), 'Venus': (330, 357), 'Saturn': (180, 200)
    }

    debilitation_ranges = {
        'Sun': (180, 190), 'Moon': (210, 213), 'Mars': (90, 118), 'Mercury': (330, 345),
        'Jupiter': (270, 275), 'Venus': (150, 177), 'Saturn': (0, 20)
    }

    if planet_name in exaltation_ranges:
        start_deg, end_deg = exaltation_ranges[planet_name]
        if start_deg <= lon <= end_deg:
            return "Exalted"

    if planet_name in debilitation_ranges:
        start_deg, end_deg = debilitation_ranges[planet_name]
        if start_deg <= lon <= end_deg:
            return "Debilitated"

    if planet_name in own_signs and sign_index in own_signs[planet_name]:
        return "Own Sign"

    sign_lord = SIGN_RULERS[sign_index]
    if planet_name in PLANETARY_FRIENDS:
        if sign_lord in PLANETARY_FRIENDS[planet_name]:
            return "Friend's Sign"
        elif sign_lord in PLANETARY_ENEMIES.get(planet_name, []):
            return "Enemy's Sign"

    return "Neutral"

def is_planet_combusted(planet_name, planet_positions):
    if planet_name == 'Sun' or planet_name not in planet_positions:
        return False, 0
    if 'Sun' not in planet_positions:
        return False, 0
    distance = get_exact_conjunction_distance(planet_positions, 'Sun', planet_name)
    if distance is None:
        return False, 0
    combustion_orbs = {
        'Moon': 12, 'Mars': 17, 'Mercury': 14, 'Jupiter': 11, 'Venus': 10, 'Saturn': 15
    }
    orb = combustion_orbs.get(planet_name, 8)
    is_combust = distance <= orb

    if planet_name == 'Mercury' and distance <= 4:
        return False, distance
    elif planet_name == 'Venus' and distance <= 6:
        return False, distance

    return is_combust, distance

def is_moon_bright(planet_positions):
    if 'Moon' not in planet_positions or 'Sun' not in planet_positions:
        return False
    moon_lon = planet_positions['Moon'][0]
    sun_lon = planet_positions['Sun'][0]
    phase = (moon_lon - sun_lon) % 360
    return 0 <= phase <= 180

def is_planet_strong_precise(planet_name, planet_positions, planet_houses, asc_sign_index):
    if planet_name not in planet_positions:
        return False

    lon, retro = planet_positions[planet_name]

    if planet_name in ['Rahu', 'Ketu']:
        house = planet_houses.get(planet_name, 0)
        if house in [3, 6, 11]:
            if planet_name == 'Rahu':
                return True
            else:
                return False
        elif house in [1, 5, 9] and planet_name == 'Ketu':
            return False
        elif house in [6, 8, 12] and planet_name == 'Rahu':
            return True
        else:
            return False

    is_retrograde = retro == 'R'
    strength_score = 0

    dignity = get_planet_dignity_precise(planet_name, planet_positions)
    if dignity == "Exalted": strength_score += 8
    elif dignity == "Own Sign": strength_score += 6
    elif dignity == "Friend's Sign": strength_score += 3
    elif dignity == "Neutral": strength_score += 1
    elif dignity == "Enemy's Sign": strength_score -= 1
    elif dignity == "Debilitated": strength_score -= 4

    house = planet_houses.get(planet_name, 0)
    if house in [1, 4, 7, 10]: strength_score += 3
    elif house in [5, 9]: strength_score += 4
    elif house in [2, 11]: strength_score += 2
    elif house in [3, 6]:
        if planet_name in NATURAL_MALEFICS: strength_score += 2
        else: strength_score += 1
    elif house in [8, 12]: strength_score -= 3
    elif house == 6:
        if planet_name in NATURAL_MALEFICS: strength_score += 1
        else: strength_score -= 2

    if is_retrograde:
        if planet_name == 'Jupiter':
            if house in [1, 4, 5, 7, 9, 10, 11]: strength_score += 1
            else: strength_score -= 1
        elif planet_name == 'Saturn':
            if house in [3, 6, 10, 11]: strength_score += 2
            else: strength_score += 1
        elif planet_name == 'Mars':
            if house in [3, 6, 10, 11]: strength_score += 1
            else: strength_score -= 1
        else: strength_score -= 2

    is_combust, _ = is_planet_combusted(planet_name, planet_positions)
    if is_combust: strength_score -= 4

    if planet_name == 'Moon':
        if is_moon_bright(planet_positions): strength_score += 2
        else: strength_score -= 2

    if planet_name == 'Mercury':
        if check_planetary_conjunction(planet_positions, 'Sun', 'Mercury', 4):
            strength_score += 2

    return strength_score >= 5

class YogaTracker:
    def __init__(self):
        self.detected_yogas = {}
        self.used_placements = set()
        self.used_exchanges = set()
        self.used_conjunctions = set()
        self.used_combinations = set()

    def add_yoga(self, yoga_name, yoga_data):
        self.detected_yogas[yoga_name] = yoga_data

    def mark_placement_used(self, planet, house):
        self.used_placements.add(f"{planet}_{house}")

    def mark_exchange_used(self, lord1, lord2, house1, house2):
        exchange = tuple(sorted([f"{lord1}_{house1}_{house2}", f"{lord2}_{house2}_{house1}"]))
        self.used_exchanges.add(exchange)

    def mark_conjunction_used(self, planet1, planet2):
        conjunction = tuple(sorted([planet1, planet2]))
        self.used_conjunctions.add(conjunction)

    def is_placement_used(self, planet, house):
        return f"{planet}_{house}" in self.used_placements

    def is_exchange_used(self, lord1, lord2, house1, house2):
        exchange = tuple(sorted([f"{lord1}_{house1}_{house2}", f"{lord2}_{house2}_{house1}"]))
        return exchange in self.used_exchanges

    def is_conjunction_used(self, planet1, planet2):
        conjunction = tuple(sorted([planet1, planet2]))
        return conjunction in self.used_conjunctions

# ----- Yoga detection (UNCHANGED) -----
def detect_dhan_yogas_final(planet_positions, planet_houses, asc_sign_index):
    yoga_tracker = YogaTracker()
    all_lordships = get_all_house_lordships(asc_sign_index)

    def get_lordship_desc(planet):
        houses = all_lordships.get(planet, [])
        if len(houses) == 1:
            return f"{get_ordinal(houses[0])} lord"
        elif len(houses) == 2:
            return f"{get_ordinal(houses[0])}/{get_ordinal(houses[1])} lord"
        else:
            return "lord"

    wealth_houses = [1, 2, 5, 9, 10, 11]
    # Priority 1: Parivartana
    for house1 in wealth_houses:
        for house2 in wealth_houses:
            if house1 < house2:
                lord1 = get_house_lord(house1, asc_sign_index)
                lord2 = get_house_lord(house2, asc_sign_index)
                if (lord1 != lord2 and 
                    lord1 in planet_houses and lord2 in planet_houses and
                    planet_houses[lord1] == house2 and planet_houses[lord2] == house1 and
                    not yoga_tracker.is_exchange_used(lord1, lord2, house1, house2)):

                    lord1_strong = is_planet_strong_precise(lord1, planet_positions, planet_houses, asc_sign_index)
                    lord2_strong = is_planet_strong_precise(lord2, planet_positions, planet_houses, asc_sign_index)

                    dignity1 = get_planet_dignity_precise(lord1, planet_positions)
                    dignity2 = get_planet_dignity_precise(lord2, planet_positions)

                    if lord1_strong and lord2_strong and dignity1 in ['Exalted', 'Own Sign'] and dignity2 in ['Exalted', 'Own Sign']:
                        strength = 'Extremely Strong'
                    elif lord1_strong and lord2_strong:
                        strength = 'Very Strong'
                    elif lord1_strong or lord2_strong:
                        strength = 'Strong'
                    else:
                        strength = 'Moderate'

                    yoga_tracker.mark_exchange_used(lord1, lord2, house1, house2)
                    yoga_tracker.mark_placement_used(lord1, house2)
                    yoga_tracker.mark_placement_used(lord2, house1)

                    house_names = {1: 'Lagna', 2: 'Dhana', 5: 'Pancham', 9: 'Bhagya', 10: 'Karma', 11: 'Labha'}
                    yoga_name = f'{house_names.get(house1, f"H{house1}")}_{house_names.get(house2, f"H{house2}")}_Parivartana'

                    yoga_tracker.add_yoga(yoga_name, {
                        'type': 'Parivartana_Yoga',
                        'lords': [lord1, lord2],
                        'houses': [house1, house2],
                        'description': f'{lord1} ({get_lordship_desc(lord1)}) and {lord2} ({get_lordship_desc(lord2)}) in mutual exchange',
                        'strength': strength,
                        'classical_reference': 'Powerful Parivartana Yoga - Brihat Parashara Hora Shastra',
                        'dignity_analysis': {lord1: dignity1, lord2: dignity2}
                    })

    # Priority 2: Gaja Kesari
    if check_kendra_from_planet(planet_houses, 'Moon', 'Jupiter'):
        jupiter_strong = is_planet_strong_precise('Jupiter', planet_positions, planet_houses, asc_sign_index)
        moon_bright = is_moon_bright(planet_positions)
        jupiter_dignity = get_planet_dignity_precise('Jupiter', planet_positions)
        moon_dignity = get_planet_dignity_precise('Moon', planet_positions)
        jupiter_combust, _ = is_planet_combusted('Jupiter', planet_positions)

        if jupiter_strong and moon_bright and jupiter_dignity == 'Exalted' and not jupiter_combust:
            strength = 'Extremely Strong'
        elif jupiter_strong and moon_bright and not jupiter_combust:
            strength = 'Very Strong'
        elif (jupiter_strong or moon_bright) and not jupiter_combust:
            strength = 'Strong'
        elif not jupiter_combust:
            strength = 'Moderate'
        else:
            strength = 'Weak'

        yoga_tracker.add_yoga('Gaja_Kesari_Yoga', {
            'type': 'Kendra_Relationship',
            'planets': ['Jupiter', 'Moon'],
            'description': f'Jupiter in kendra from Moon (Houses: {planet_houses["Jupiter"]} and {planet_houses["Moon"]})',
            'strength': strength,
            'classical_reference': 'Brihat Parashara Hora Shastra - Chapter 41',
            'special_analysis': {
                'jupiter_dignity': jupiter_dignity,
                'moon_dignity': moon_dignity,
                'moon_bright': moon_bright,
                'jupiter_combust': jupiter_combust
            }
        })

    # Priority 3: Lords in own houses
    for house in wealth_houses:
        lord = get_house_lord(house, asc_sign_index)
        if (lord in planet_houses and 
            planet_houses[lord] == house and
            not yoga_tracker.is_placement_used(lord, house)):

            lord_strong = is_planet_strong_precise(lord, planet_positions, planet_houses, asc_sign_index)
            dignity = get_planet_dignity_precise(lord, planet_positions)
            is_combust, _ = is_planet_combusted(lord, planet_positions)

            if lord_strong and dignity == 'Exalted' and not is_combust:
                strength = 'Extremely Strong'
            elif lord_strong and dignity == 'Own Sign' and not is_combust:
                strength = 'Very Strong'
            elif lord_strong and not is_combust:
                strength = 'Strong'
            elif not is_combust:
                strength = 'Moderate'
            else:
                strength = 'Weak'

            yoga_tracker.mark_placement_used(lord, house)

            house_names = {1: 'Lagna', 2: 'Dhana', 5: 'Pancham', 9: 'Bhagya', 10: 'Karma', 11: 'Labha'}
            yoga_name = f'{house_names.get(house, f"H{house}")}_Lord_Own_House'

            yoga_tracker.add_yoga(yoga_name, {
                'type': 'Own_House_Placement',
                'lords': [lord],
                'houses': [house],
                'description': f'{lord} ({get_lordship_desc(lord)}) in own house ({get_ordinal(house)} house)',
                'strength': strength,
                'classical_reference': 'Parashari System - Own house strengthening',
                'dignity_status': dignity,
                'combustion_status': is_combust
            })

    # Priority 4: Cross-house placements
    cross_placements = [
        (5, [1, 4, 7, 10], 'Trikona_Kendra_Yoga'),
        (9, [1, 4, 7, 10], 'Trikona_Kendra_Yoga'),
        (1, [5, 9], 'Kendra_Trikona_Yoga'),
        (10, [5, 9], 'Kendra_Trikona_Yoga'),
        (2, [11], 'Primary_Dhana_Yoga'),
        (11, [2], 'Primary_Dhana_Yoga'),
        (1, [2, 11], 'Lagna_Wealth_Yoga'),
        (5, [9], 'Trikona_Trikona_Yoga'),
        (9, [5], 'Trikona_Trikona_Yoga')
    ]
    for source_house, target_houses, yoga_type in cross_placements:
        lord = get_house_lord(source_house, asc_sign_index)
        for target_house in target_houses:
            if (lord in planet_houses and 
                planet_houses[lord] == target_house and
                not yoga_tracker.is_placement_used(lord, target_house)):

                lord_strong = is_planet_strong_precise(lord, planet_positions, planet_houses, asc_sign_index)
                dignity = get_planet_dignity_precise(lord, planet_positions)
                is_combust, _ = is_planet_combusted(lord, planet_positions)

                if lord_strong and dignity in ['Exalted', 'Own Sign'] and not is_combust:
                    strength = 'Very Strong'
                elif lord_strong and not is_combust:
                    strength = 'Strong'
                elif not is_combust:
                    strength = 'Moderate'
                else:
                    strength = 'Weak'

                yoga_tracker.mark_placement_used(lord, target_house)

                house_names = {1: 'Lagna', 2: 'Dhana', 5: 'Pancham', 9: 'Bhagya', 10: 'Karma', 11: 'Labha'}
                source_name = house_names.get(source_house, f'H{source_house}')
                target_name = house_names.get(target_house, f'H{target_house}')
                yoga_name = f'{source_name}_Lord_{target_name}'

                yoga_tracker.add_yoga(yoga_name, {
                    'type': yoga_type,
                    'lords': [lord],
                    'houses': [source_house, target_house],
                    'description': f'{lord} ({get_lordship_desc(lord)}) in {get_ordinal(target_house)} house',
                    'strength': strength,
                    'classical_reference': 'Raja Yoga principles',
                    'dignity_status': dignity,
                    'combustion_status': is_combust
                })

    # Priority 5: Important planetary conjunctions
    important_conjunctions = [
        (['Sun', 'Mercury'], 'Budhaditya_Yoga', 17, 'Intelligence and communication through education'),
        (['Jupiter', 'Venus'], 'Guru_Sukra_Yoga', 10, 'Wisdom, learning, and material prosperity'),
        (['Moon', 'Mars'], 'Chandra_Mangal_Yoga', 10, 'Wealth through property, land, and real estate'),
        (['Jupiter', 'Mercury'], 'Guru_Budha_Yoga', 10, 'Knowledge, teaching, and intellectual pursuits'),
        (['Venus', 'Mercury'], 'Sukra_Budha_Yoga', 10, 'Arts, commerce, and creative ventures'),
        (['Moon', 'Jupiter'], 'Chandra_Guru_Yoga', 10, 'Wisdom, fortune, and spiritual wealth')
    ]
    for planets, yoga_name, orb, description in important_conjunctions:
        if (check_planetary_conjunction(planet_positions, planets[0], planets[1], orb) and
            not yoga_tracker.is_conjunction_used(planets[0], planets[1])):

            planet1_strong = is_planet_strong_precise(planets[0], planet_positions, planet_houses, asc_sign_index)
            planet2_strong = is_planet_strong_precise(planets[1], planet_positions, planet_houses, asc_sign_index)
            planet1_house = planet_houses.get(planets[0], 0)

            dignity1 = get_planet_dignity_precise(planets[0], planet_positions)
            dignity2 = get_planet_dignity_precise(planets[1], planet_positions)

            planet1_combust = False
            planet2_combust = False
            if planets[0] != 'Sun':
                planet1_combust, _ = is_planet_combusted(planets[0], planet_positions)
            if planets[1] != 'Sun':
                planet2_combust, _ = is_planet_combusted(planets[1], planet_positions)

            if yoga_name == 'Budhaditya_Yoga':
                distance = get_exact_conjunction_distance(planet_positions, 'Sun', 'Mercury')
                if distance <= 4 and planet1_house in [1, 4, 5, 7, 9, 10, 11]:
                    strength = 'Very Strong'
                elif distance <= 10 and planet1_house in [1, 5, 9, 10]:
                    strength = 'Strong'
                elif planet1_house in [1, 5, 9, 10]:
                    strength = 'Moderate'
                else:
                    strength = 'Weak'
            else:
                if planet1_strong and planet2_strong and not planet1_combust and not planet2_combust:
                    if planet1_house in [1, 4, 5, 7, 9, 10, 11]:
                        strength = 'Very Strong'
                    else:
                        strength = 'Strong'
                elif (planet1_strong or planet2_strong) and not planet1_combust and not planet2_combust:
                    if planet1_house in [1, 4, 5, 7, 9, 10, 11]:
                        strength = 'Strong'
                    else:
                        strength = 'Moderate'
                elif planet1_house in [1, 5, 9, 10] and not planet1_combust and not planet2_combust:
                    strength = 'Moderate'
                else:
                    strength = 'Weak'

            yoga_tracker.mark_conjunction_used(planets[0], planets[1])

            yoga_tracker.add_yoga(yoga_name, {
                'type': 'Planetary_Conjunction',
                'planets': planets,
                'description': f'{planets[0]} and {planets[1]} conjunction - {description}',
                'strength': strength,
                'classical_reference': 'Classical combination yogas',
                'house_placement': planet1_house,
                'planet_dignities': {planets[0]: dignity1, planets[1]: dignity2},
                'combustion_status': {planets[0]: planet1_combust, planets[1]: planet2_combust},
                'conjunction_details': f'In {get_ordinal(planet1_house)} house'
            })

    # Priority 6: Wealth lord conjunctions
    wealth_lord_pairs = [
        (2, 11, 'Dhana_Labha_Lord_Conjunction'),
        (1, 2, 'Lagna_Dhana_Lord_Conjunction'),
        (1, 11, 'Lagna_Labha_Lord_Conjunction'),
        (5, 9, 'Pancham_Bhagya_Lord_Conjunction'),
        (9, 11, 'Bhagya_Labha_Lord_Conjunction'),
        (5, 11, 'Pancham_Labha_Lord_Conjunction')
    ]
    for house1, house2, yoga_name in wealth_lord_pairs:
        lord1 = get_house_lord(house1, asc_sign_index)
        lord2 = get_house_lord(house2, asc_sign_index)
        if (lord1 != lord2 and 
            check_planetary_conjunction(planet_positions, lord1, lord2) and
            not yoga_tracker.is_conjunction_used(lord1, lord2)):

            lord1_strong = is_planet_strong_precise(lord1, planet_positions, planet_houses, asc_sign_index)
            lord2_strong = is_planet_strong_precise(lord2, planet_positions, planet_houses, asc_sign_index)

            lord1_combust, _ = is_planet_combusted(lord1, planet_positions)
            lord2_combust, _ = is_planet_combusted(lord2, planet_positions)

            if lord1_strong and lord2_strong and not lord1_combust and not lord2_combust:
                strength = 'Very Strong'
            elif (lord1_strong or lord2_strong) and not lord1_combust and not lord2_combust:
                strength = 'Strong'
            elif not lord1_combust and not lord2_combust:
                strength = 'Moderate'
            else:
                strength = 'Weak'

            conjunction_house = planet_houses.get(lord1, 0)
            yoga_tracker.mark_conjunction_used(lord1, lord2)

            yoga_tracker.add_yoga(yoga_name, {
                'type': 'Lord_Conjunction',
                'lords': [lord1, lord2],
                'houses': [house1, house2],
                'description': f'{lord1} ({get_ordinal(house1)} lord) conjunct {lord2} ({get_ordinal(house2)} lord) in {get_ordinal(conjunction_house)} house',
                'strength': strength,
                'classical_reference': 'Wealth lord conjunction principles',
                'conjunction_house': conjunction_house,
                'combustion_analysis': {lord1: lord1_combust, lord2: lord2_combust}
            })

    # Priority 7: Vasumati & Amala
    upachaya_houses = [3, 6, 10, 11]
    benefics_in_upachaya = []
    benefics_to_check = ['Jupiter', 'Venus', 'Mercury']
    if is_moon_bright(planet_positions):
        benefics_to_check.append('Moon')
    for planet in benefics_to_check:
        if planet in planet_houses and planet_houses[planet] in upachaya_houses:
            is_strong = is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index)
            is_combust, _ = is_planet_combusted(planet, planet_positions)
            dignity = get_planet_dignity_precise(planet, planet_positions)
            benefics_in_upachaya.append({
                'planet': planet,
                'house': planet_houses[planet],
                'strong': is_strong and not is_combust,
                'dignity': dignity,
                'combust': is_combust
            })
    if len(benefics_in_upachaya) >= 2:
        strong_count = sum(1 for b in benefics_in_upachaya if b['strong'])
        exalted_count = sum(1 for b in benefics_in_upachaya if b['dignity'] == 'Exalted')
        combust_count = sum(1 for b in benefics_in_upachaya if b['combust'])
        if len(benefics_in_upachaya) >= 3 and strong_count >= 2 and combust_count == 0:
            strength = 'Very Strong'
        elif strong_count >= 2 and combust_count <= 1:
            strength = 'Strong'
        elif exalted_count >= 1 and combust_count == 0:
            strength = 'Strong'
        elif combust_count <= 1:
            strength = 'Moderate'
        else:
            strength = 'Weak'
        yoga_tracker.add_yoga('Vasumati_Yoga', {
            'type': 'Upachaya_Placement',
            'planets': benefics_in_upachaya,
            'description': f'{len(benefics_in_upachaya)} benefics in upachaya houses (3,6,10,11) - {strong_count} strong, {combust_count} combust',
            'strength': strength,
            'classical_reference': 'Saravali by Kalyana Varma - Wealth through consistent effort'
        })

    tenth_house_planets = [p for p, h in planet_houses.items() if h == 10]
    benefics_in_10th = [p for p in tenth_house_planets if p in NATURAL_BENEFICS]
    if benefics_in_10th:
        strong_benefics = []
        for planet in benefics_in_10th:
            is_strong = is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index)
            is_combust, _ = is_planet_combusted(planet, planet_positions)
            if is_strong and not is_combust:
                strong_benefics.append(planet)
        if len(strong_benefics) >= 2:
            strength = 'Very Strong'
        elif len(strong_benefics) >= 1:
            strength = 'Strong'
        elif len(benefics_in_10th) >= 2:
            strength = 'Moderate'
        else:
            strength = 'Weak'
        yoga_tracker.add_yoga('Amala_Yoga', {
            'type': '10th_House_Benefic',
            'planets': benefics_in_10th,
            'description': f'Natural benefic(s) {", ".join(benefics_in_10th)} in 10th house - career excellence through merit',
            'strength': strength,
            'classical_reference': 'Saravali - Reputation and status through virtue',
            'strong_planets': strong_benefics
        })

    # Priority 8: Stellium
    wealth_houses = [1, 2, 5, 9, 10, 11]
    for house in wealth_houses:
        planets_in_house = [p for p, h in planet_houses.items() if h == house]
        if len(planets_in_house) >= 3:
            natural_planets = [p for p in planets_in_house if p not in ['Rahu', 'Ketu']]
            benefic_count = len([p for p in natural_planets if p in NATURAL_BENEFICS])
            malefic_count = len([p for p in natural_planets if p in NATURAL_MALEFICS])
            total_count = len(planets_in_house)

            strong_planets = []
            combust_planets = []
            for planet in planets_in_house:
                if planet not in ['Rahu', 'Ketu']:
                    is_strong = is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index)
                    is_combust, _ = is_planet_combusted(planet, planet_positions)
                    if is_strong and not is_combust:
                        strong_planets.append(planet)
                    if is_combust:
                        combust_planets.append(planet)
                else:
                    if is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index):
                        strong_planets.append(planet)

            strong_planet_count = len(strong_planets)
            combust_count = len(combust_planets)
            if benefic_count >= 3 and strong_planet_count >= 2 and combust_count == 0:
                strength = 'Very Strong'
            elif benefic_count >= 2 and malefic_count <= 1 and strong_planet_count >= 1 and combust_count <= 1:
                strength = 'Strong'
            elif benefic_count > malefic_count and combust_count <= 1:
                strength = 'Moderate'
            elif total_count >= 4 and strong_planet_count >= 1 and combust_count <= 2:
                strength = 'Moderate'
            else:
                strength = 'Weak'

            house_names = {1: '1st', 2: '2nd', 5: '5th', 9: '9th', 10: '10th', 11: '11th'}
            yoga_name = f'Stellium_{house_names.get(house, str(house))}_House'
            yoga_tracker.add_yoga(yoga_name, {
                'type': 'Stellium',
                'planets': planets_in_house,
                'description': f'{total_count} planets in {get_ordinal(house)} house ({benefic_count} benefics, {malefic_count} malefics, {strong_planet_count} strong, {combust_count} combust)',
                'strength': strength,
                'classical_reference': 'Multiple planetary concentration principles',
                'detailed_analysis': {
                    'total_planets': total_count,
                    'benefics': benefic_count,
                    'malefics': malefic_count,
                    'strong_planets': strong_planet_count,
                    'combust_planets': combust_count,
                    'house_significance': get_house_significance(house)
                }
            })

    return yoga_tracker.detected_yogas

def get_house_significance(house_num):
    house_meanings = {
        1: "Self, personality, overall vitality and approach to life",
        2: "Accumulated wealth, family assets, speech, food",
        3: "Efforts, courage, siblings, short journeys",
        4: "Mother, home, properties, emotional foundation",
        5: "Intelligence, creativity, speculation, children, purva punya",
        6: "Enemies, debts, diseases, service, daily work",
        7: "Partnerships, marriage, business collaborations",
        8: "Transformation, inheritance, occult, longevity",
        9: "Fortune, dharma, higher learning, guru, long journeys",
        10: "Career, profession, status, reputation, karma",
        11: "Gains, income, profits, elder siblings, fulfillment of desires",
        12: "Expenses, losses, foreign lands, spirituality, moksha"
    }
    return house_meanings.get(house_num, "Unknown house significance")

def calculate_wealth_potential_final(detected_yogas, planet_positions, planet_houses, asc_sign_index):
    total_yogas = len(detected_yogas)

    strength_weights = {
        'Extremely Strong': 12,
        'Very Strong': 8,
        'Strong': 5,
        'Moderate': 3,
        'Weak': 1
    }
    base_score = sum(strength_weights.get(yoga['strength'], 0) for yoga in detected_yogas.values())

    premium_yogas = {
        'Gaja_Kesari_Yoga': 4,
        'Budhaditya_Yoga': 3,
        'Dhana_Labha_Parivartana': 6,
        'Lagna_Pancham_Parivartana': 5,
        'Lagna_Bhagya_Parivartana': 5,
        'Dhana_Lord_Own_House': 3,
        'Labha_Lord_Own_House': 3,
        'Bhagya_Lord_Own_House': 3
    }
    bonus_score = sum(premium_yogas.get(yoga_name, 0) for yoga_name in detected_yogas.keys())

    all_lordships = get_all_house_lordships(asc_sign_index)
    wealth_lords = []
    for house in [1, 2, 5, 9, 10, 11]:
        lord = get_house_lord(house, asc_sign_index)
        if lord not in wealth_lords:
            wealth_lords.append(lord)

    fundamental_weaknesses = 0
    weakness_details = []

    for lord in wealth_lords:
        if lord in planet_positions:
            dignity = get_planet_dignity_precise(lord, planet_positions)
            if dignity == 'Debilitated':
                fundamental_weaknesses += 3
                weakness_details.append(f"Debilitated {lord}")

    for lord in wealth_lords:
        if lord in planet_positions and lord != 'Sun':
            is_combust, _ = is_planet_combusted(lord, planet_positions)
            if is_combust:
                fundamental_weaknesses += 2
                weakness_details.append(f"Combust {lord}")

    for house in [2, 11]:
        planets_in_house = [p for p, h in planet_houses.items() if h == house]
        if not planets_in_house:
            fundamental_weaknesses += 1
            weakness_details.append(f"Empty {get_ordinal(house)} house")

    for house in [2, 11]:
        planets_in_house = [p for p, h in planet_houses.items() if h == house]
        malefics_in_house = [p for p in planets_in_house if p in NATURAL_MALEFICS]
        benefics_in_house = [p for p in planets_in_house if p in NATURAL_BENEFICS]
        if len(malefics_in_house) > 0 and len(benefics_in_house) == 0:
            if len(malefics_in_house) >= 2:
                fundamental_weaknesses += 2
                weakness_details.append(f"Multiple malefics in {get_ordinal(house)} house")
            else:
                fundamental_weaknesses += 1
                weakness_details.append(f"Malefic in {get_ordinal(house)} house")

    for lord in wealth_lords:
        if lord in planet_positions:
            dignity = get_planet_dignity_precise(lord, planet_positions)
            if dignity == "Enemy's Sign":
                fundamental_weaknesses += 1
                weakness_details.append(f"{lord} in enemy's sign")

    total_score = base_score + bonus_score - fundamental_weaknesses
    total_score = max(0, total_score)

    if total_score >= 60:
        potential = 'Exceptional'
    elif total_score >= 45:
        potential = 'Very High'
    elif total_score >= 30:
        potential = 'High'
    elif total_score >= 20:
        potential = 'Above Average'
    elif total_score >= 12:
        potential = 'Average'
    elif total_score >= 6:
        potential = 'Below Average'
    else:
        potential = 'Limited'

    yoga_categories = {}
    for yoga_name, yoga_data in detected_yogas.items():
        category = yoga_data.get('type', 'Other')
        if category not in yoga_categories:
            yoga_categories[category] = 0
        yoga_categories[category] += 1

    strong_planets = []
    for planet in planet_positions.keys():
        if planet not in ['Rahu', 'Ketu']:
            is_strong = is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index)
            is_combust, _ = is_planet_combusted(planet, planet_positions)
            if is_strong and not is_combust:
                strong_planets.append(planet)
        else:
            if is_planet_strong_precise(planet, planet_positions, planet_houses, asc_sign_index):
                strong_planets.append(planet)

    return {
        'total_yogas': total_yogas,
        'base_score': base_score,
        'bonus_score': bonus_score,
        'total_score': total_score,
        'wealth_potential': potential,
        'fundamental_weaknesses': fundamental_weaknesses,
        'weakness_details': weakness_details,
        'yoga_categories': yoga_categories,
        'strength_distribution': {
            strength: len([y for y in detected_yogas.values() if y['strength'] == strength])
            for strength in ['Extremely Strong', 'Very Strong', 'Strong', 'Moderate', 'Weak']
        },
        'strong_planets': strong_planets,
        'scoring_breakdown': {
            'base_score': base_score,
            'premium_bonuses': bonus_score,
            'weakness_penalties': fundamental_weaknesses,
            'final_score': total_score
        }
    }

def extract_final_strengths(detected_yogas, all_lordships):
    strengths = []
    if 'Gaja_Kesari_Yoga' in detected_yogas:
        yoga_strength = detected_yogas['Gaja_Kesari_Yoga']['strength']
        strengths.append(f"Gaja Kesari Yoga ({yoga_strength}) provides fame, respect and wealth through wisdom")
    if 'Budhaditya_Yoga' in detected_yogas:
        yoga_strength = detected_yogas['Budhaditya_Yoga']['strength']
        strengths.append(f"Budhaditya Yoga ({yoga_strength}) grants wealth through intelligence and communication")
    parivartana_yogas = [name for name in detected_yogas.keys() if 'Parivartana' in name]
    if parivartana_yogas:
        strongest_parivartana = max(parivartana_yogas, key=lambda x: detected_yogas[x]['strength'])
        strength_level = detected_yogas[strongest_parivartana]['strength']
        strengths.append(f"{len(parivartana_yogas)} Parivartana Yoga(s) create powerful planetary exchanges (strongest: {strength_level})")
    own_house_yogas = [yoga for yoga in detected_yogas.values() if yoga.get('type') == 'Own_House_Placement']
    if own_house_yogas:
        very_strong_count = len([y for y in own_house_yogas if y['strength'] in ['Extremely Strong', 'Very Strong']])
        strengths.append(f"{len(own_house_yogas)} lord(s) in own houses provide exceptional strength ({very_strong_count} very strong)")
    raja_yoga_count = len([yoga for yoga in detected_yogas.values() 
                          if yoga.get('type') in ['Trikona_Kendra_Yoga', 'Kendra_Trikona_Yoga']])
    if raja_yoga_count > 0:
        strengths.append(f"{raja_yoga_count} Raja Yoga formation(s) for leadership and success")
    conjunction_yogas = [yoga for yoga in detected_yogas.values() 
                        if yoga.get('type') in ['Planetary_Conjunction', 'Lord_Conjunction']]
    strong_conjunctions = len([y for y in conjunction_yogas if y['strength'] in ['Very Strong', 'Strong']])
    if strong_conjunctions > 0:
        strengths.append(f"{strong_conjunctions} strong conjunction(s) enhancing planetary energies")
    return strengths if strengths else ["Basic planetary combinations present - focus on strengthening fundamentals"]

def extract_final_cautions(detected_yogas, planet_positions, planet_houses, all_lordships, asc_sign_index):
    cautions = []

    combust_planets = []
    for planet in planet_positions.keys():
        if planet != 'Sun':
            is_combust, distance = is_planet_combusted(planet, planet_positions)
            if is_combust:
                combust_planets.append(f"{planet} ({distance:.1f}° from Sun)")
    if combust_planets:
        cautions.append(f"Combust planet(s) {', '.join(combust_planets)} have reduced beneficial effects")

    debilitated_planets = []
    for planet in planet_positions.keys():
        if planet not in ['Rahu', 'Ketu']:
            dignity = get_planet_dignity_precise(planet, planet_positions)
            if dignity == 'Debilitated':
                debilitated_planets.append(planet)
    if debilitated_planets:
        cautions.append(f"Debilitated planet(s) {', '.join(debilitated_planets)} require remedial measures and careful timing")

    wealth_house_issues = []
    for house in [2, 11]:
        malefics_in_house = [p for p, h in planet_houses.items() 
                            if h == house and p in NATURAL_MALEFICS]
        benefics_in_house = [p for p, h in planet_houses.items() 
                           if h == house and p in NATURAL_BENEFICS]
        if malefics_in_house and not benefics_in_house:
            house_name = "2nd (savings)" if house == 2 else "11th (gains)"
            wealth_house_issues.append(f"Malefic(s) {', '.join(malefics_in_house)} in {house_name} house without benefic protection")
    if wealth_house_issues:
        cautions.extend(wealth_house_issues)

    wealth_lords = []
    for house in [1, 2, 5, 9, 10, 11]:
        lord = get_house_lord(house, asc_sign_index)
        if lord not in wealth_lords:
            wealth_lords.append(lord)
    retrograde_wealth_lords = []
    for lord in wealth_lords:
        if lord in planet_positions and planet_positions[lord][1] == 'R':
            retrograde_wealth_lords.append(lord)
    if retrograde_wealth_lords:
        cautions.append(f"Retrograde wealth lord(s) {', '.join(retrograde_wealth_lords)} may cause delays in financial gains")

    empty_houses = []
    for house in [2, 11]:
        planets_in_house = [p for p, h in planet_houses.items() if h == house]
        if not planets_in_house:
            empty_houses.append(get_ordinal(house))
    if empty_houses:
        cautions.append(f"Empty {'/'.join(empty_houses)} house(s) require activation through transits and dashas")

    return cautions if cautions else ["No major cautions detected - maintain steady financial practices"]

def generate_final_recommendations(detected_yogas, wealth_analysis, planet_positions, planet_houses, asc_sign_index):
    recommendations = []
    potential = wealth_analysis['wealth_potential']
    total_score = wealth_analysis['total_score']

    if potential in ['Exceptional', 'Very High']:
        recommendations.append(f"Excellent wealth potential (Score: {total_score}) - focus on timing and strategic investments")
        recommendations.append("Multiple strong yogas present - diversify income sources and consider entrepreneurship")
    elif potential in ['High', 'Above Average']:
        recommendations.append(f"Good wealth potential (Score: {total_score}) - strengthen yoga-forming planets through remedies")
        recommendations.append("Focus on career advancement and skill development during favorable planetary periods")
    elif potential == 'Average':
        recommendations.append(f"Moderate wealth potential (Score: {total_score}) - consistent effort and planning essential")
        recommendations.append("Build financial foundation through steady savings and conservative investments")
    else:
        recommendations.append(f"Limited wealth indicators (Score: {total_score}) - focus on skill development and patient accumulation")
        recommendations.append("Strengthen fundamental wealth significators through comprehensive remedial measures")

    weakness_details = wealth_analysis.get('weakness_details', [])
    if weakness_details:
        recommendations.append(f"Address key weaknesses: {', '.join(weakness_details[:3])}")

    strong_planets = wealth_analysis.get('strong_planets', [])
    if strong_planets:
        recommendations.append(f"Utilize strong planets during favorable periods: {', '.join(strong_planets)}")

    if 'Budhaditya_Yoga' in detected_yogas:
        recommendations.append("Leverage Budhaditya Yoga through education, communication, and intellectual pursuits")
    if any('Parivartana' in name for name in detected_yogas.keys()):
        recommendations.append("Parivartana Yoga indicates mutual support - consider partnerships and collaborative ventures")

    return recommendations

def generate_remedial_suggestions_final(planet_positions, planet_houses, asc_sign_index, wealth_analysis):
    remedies = []

    debilitated_planets = []
    for planet in planet_positions.keys():
        if planet not in ['Rahu', 'Ketu']:
            dignity = get_planet_dignity_precise(planet, planet_positions)
            if dignity == 'Debilitated':
                debilitated_planets.append(planet)

    planet_remedies = {
        'Sun': "Chant Surya mantras, wear ruby, donate wheat/jaggery on Sundays",
        'Moon': "Chant Chandra mantras, wear pearl, donate rice/milk on Mondays",
        'Mars': "Chant Mangal mantras, wear red coral, donate red lentils on Tuesdays",
        'Mercury': "Chant Budha mantras, wear emerald, donate green items on Wednesdays",
        'Jupiter': "Chant Guru mantras, wear yellow sapphire, donate yellow items on Thursdays",
        'Venus': "Chant Shukra mantras, wear diamond/white sapphire, donate white items on Fridays",
        'Saturn': "Chant Shani mantras, wear blue sapphire, donate black items on Saturdays"
    }
    for planet in debilitated_planets:
        if planet in planet_remedies:
            remedies.append(f"For debilitated {planet}: {planet_remedies[planet]}")

    combust_planets = []
    for planet in planet_positions.keys():
        if planet != 'Sun':
            is_combust, _ = is_planet_combusted(planet, planet_positions)
            if is_combust:
                combust_planets.append(planet)
    if combust_planets:
        remedies.append(f"For combust planets {', '.join(combust_planets)}: Perform early morning prayers and wear respective gemstones")

    wealth_houses = [2, 11]
    for house in wealth_houses:
        lord = get_house_lord(house, asc_sign_index)
        if lord in planet_positions:
            lord_strong = is_planet_strong_precise(lord, planet_positions, planet_houses, asc_sign_index)
            if not lord_strong:
                house_name = "wealth (2nd)" if house == 2 else "gains (11th)"
                remedies.append(f"Strengthen {house_name} house lord {lord} through dedicated worship and gemstone")

    remedies.append("Regular worship of Goddess Lakshmi on Fridays with lotus flowers and yellow items")
    remedies.append("Maintain cleanliness in financial areas and keep money in organized, clean spaces")

    if wealth_analysis['wealth_potential'] in ['Limited', 'Below Average']:
        remedies.append("Perform regular charity, especially food donation, to improve karmic wealth patterns")

    return remedies

def get_combustion_analysis(planet_positions):
    combustion_data = {}
    for planet in planet_positions.keys():
        if planet != 'Sun':
            is_combust, distance = is_planet_combusted(planet, planet_positions)
            combustion_data[planet] = {
                'is_combust': is_combust,
                'distance_from_sun': round(distance, 2) if distance else 0,
                'status': 'Combust' if is_combust else 'Not Combust'
            }
    return combustion_data

def get_retrograde_analysis(planet_positions, planet_houses):
    retrograde_data = {}
    for planet, (lon, retro) in planet_positions.items():
        if planet not in ['Rahu', 'Ketu']:
            is_retro = retro == 'R'
            house = planet_houses.get(planet, 0)
            retrograde_data[planet] = {
                'is_retrograde': is_retro,
                'house_placement': house,
                'effect': 'Delayed but deep results' if is_retro else 'Direct results'
            }
    return retrograde_data

def get_dignity_summary(planet_positions):
    dignity_data = {}
    for planet in planet_positions.keys():
        if planet not in ['Rahu', 'Ketu']:
            dignity = get_planet_dignity_precise(planet, planet_positions)
            dignity_data[planet] = dignity
    return dignity_data

def get_house_strength_analysis(planet_houses, asc_sign_index, planet_positions):
    wealth_houses = [1, 2, 5, 9, 10, 11]
    house_analysis = {}
    for house in wealth_houses:
        lord = get_house_lord(house, asc_sign_index)
        planets_in_house = [p for p, h in planet_houses.items() if h == house]

        lord_strong = False
        lord_dignity = "Neutral"
        lord_combust = False
        if lord in planet_positions:
            lord_strong = is_planet_strong_precise(lord, planet_positions, planet_houses, asc_sign_index)
            lord_dignity = get_planet_dignity_precise(lord, planet_positions)
            if lord != 'Sun':
                lord_combust, _ = is_planet_combusted(lord, planet_positions)

        benefics_in_house = [p for p in planets_in_house if p in NATURAL_BENEFICS]
        malefics_in_house = [p for p in planets_in_house if p in NATURAL_MALEFICS]

        if lord_strong and not lord_combust and len(benefics_in_house) > len(malefics_in_house):
            overall_strength = 'Strong'
        elif lord_strong and not lord_combust:
            overall_strength = 'Moderate'
        elif not lord_combust and lord_dignity not in ['Debilitated', "Enemy's Sign"]:
            overall_strength = 'Average'
        else:
            overall_strength = 'Weak'

        house_analysis[f'house_{house}'] = {
            'lord': lord,
            'lord_strong': lord_strong,
            'lord_dignity': lord_dignity,
            'lord_combust': lord_combust,
            'planets_count': len(planets_in_house),
            'benefics_count': len(benefics_in_house),
            'malefics_count': len(malefics_in_house),
            'overall_strength': overall_strength
        }
    return house_analysis

# ----- Public orchestration function: dhanYoga (NEW WRAPPER, calculations identical to your endpoint) -----
def dhanYoga(birth_data: dict) -> dict:
    """
    Runs the full Dhan Yoga analysis pipeline and returns the response dict.
    This mirrors your original /dhan-yoga-analysis endpoint logic exactly, without Flask I/O.
    """
    # Validate required fields
    required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in birth_data for key in required):
        raise ValueError("Missing required parameters")

    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude")

    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

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
            raise RuntimeError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = SIGNS[asc_sign_index]

    planet_houses = {planet: get_house(lon, asc_sign_index) 
                    for planet, (lon, _) in planet_positions.items()}

    all_lordships = get_all_house_lordships(asc_sign_index)
    house_lords = {}
    for house_num in range(1, 13):
        house_lords[f'house_{house_num}'] = get_house_lord(house_num, asc_sign_index)

    detected_yogas = detect_dhan_yogas_final(planet_positions, planet_houses, asc_sign_index)
    wealth_analysis = calculate_wealth_potential_final(detected_yogas, planet_positions, planet_houses, asc_sign_index)

    planetary_positions_formatted = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        house = planet_houses[planet_name]
        dignity = get_planet_dignity_precise(planet_name, planet_positions)
        is_combust = False
        combust_distance = 0
        if planet_name != 'Sun':
            is_combust, combust_distance = is_planet_combusted(planet_name, planet_positions)
        planetary_positions_formatted[planet_name] = {
            "longitude": f"{lon:.6f}°",
            "sign": sign,
            "degrees_in_sign": format_dms(sign_deg),
            "house": house,
            "retrograde": retro,
            "is_strong": is_planet_strong_precise(planet_name, planet_positions, planet_houses, asc_sign_index),
            "dignity": dignity,
            "house_significance": get_house_significance(house),
            "lordships": all_lordships.get(planet_name, []),
            "combustion_status": {
                "is_combust": is_combust,
                "distance_from_sun": combust_distance
            }
        }

    wealth_houses_analysis = {}
    for house in [1, 2, 5, 9, 10, 11]:
        lord = get_house_lord(house, asc_sign_index)
        planets_in_house = [p for p, h in planet_houses.items() if h == house]
        lord_placement = planet_houses.get(lord, 0)
        lord_dignity = get_planet_dignity_precise(lord, planet_positions)
        lord_combust = False
        if lord != 'Sun' and lord in planet_positions:
            lord_combust, _ = is_planet_combusted(lord, planet_positions)
        wealth_houses_analysis[f'{get_ordinal(house).lower()}_house'] = {
            "lord": lord,
            "lord_placement": f"{get_ordinal(lord_placement)} house" if lord_placement else "Unknown",
            "lord_dignity": lord_dignity,
            "lord_strong": is_planet_strong_precise(lord, planet_positions, planet_houses, asc_sign_index),
            "lord_lordships": all_lordships.get(lord, []),
            "lord_combust": lord_combust,
            "planets": planets_in_house,
            "planet_count": len(planets_in_house),
            "benefic_count": len([p for p in planets_in_house if p in NATURAL_BENEFICS]),
            "malefic_count": len([p for p in planets_in_house if p in NATURAL_MALEFICS]),
            "significance": get_house_significance(house)
        }

    recommendations = generate_final_recommendations(detected_yogas, wealth_analysis, planet_positions, planet_houses, asc_sign_index)

    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": timezone_offset
            }
        },
        "chart_details": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}°",
            "house_system": "Whole Sign",
            "ascendant": {
                "sign": asc_sign,
                "degrees": format_dms(ascendant_lon % 30),
                "longitude": f"{ascendant_lon:.6f}°"
            }
        },
        "planetary_positions": planetary_positions_formatted,
        "house_lords": house_lords,
        "lordship_analysis": all_lordships,
        "dhan_yogas": {
            "detected_yogas": detected_yogas,
            "summary": wealth_analysis,
            "methodology_notes": [
                "100% accurate lordship descriptions with dual house rulerships",
                "Precise planetary strength assessment with dignity, combustion, and retrograde analysis",
                "Priority-based yoga detection prevents all double-counting",
                "Realistic scoring system with refined thresholds and comprehensive weakness analysis",
                "Classical accuracy with exact degree calculations for exaltation/debilitation"
            ]
        },
        "wealth_houses_analysis": wealth_houses_analysis,
        "classical_analysis": {
            "key_strengths": extract_final_strengths(detected_yogas, all_lordships),
            "recommendations": recommendations,
            "timing_notes": "Dasha periods of yoga-forming planets will be most beneficial for wealth creation",
            "cautions": extract_final_cautions(detected_yogas, planet_positions, planet_houses, all_lordships, asc_sign_index),
            "remedial_suggestions": generate_remedial_suggestions_final(planet_positions, planet_houses, asc_sign_index, wealth_analysis)
        },
        "technical_analysis": {
            "combustion_analysis": get_combustion_analysis(planet_positions),
            "retrograde_analysis": get_retrograde_analysis(planet_positions, planet_houses),
            "dignity_summary": get_dignity_summary(planet_positions),
            "house_strength_analysis": get_house_strength_analysis(planet_houses, asc_sign_index, planet_positions)
        }
    }
    return response
