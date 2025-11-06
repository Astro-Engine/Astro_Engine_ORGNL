# special_yogas_calc.py
from datetime import datetime, timedelta
import swisseph as swe

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatra data for Nadi Dosha calculation
nakshatras = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
    'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha',
    'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Nadi classification
nadi_classification = {
    'Adi': ['Ashwini', 'Ardra', 'Punarvasu', 'Uttara Phalguni', 'Hasta', 'Jyeshtha', 'Mula', 'Shatabhisha', 'Uttara Bhadrapada'],
    'Madhya': ['Bharani', 'Mrigashira', 'Pushya', 'Purva Phalguni', 'Chitra', 'Anuradha', 'Purva Ashadha', 'Dhanishtha', 'Purva Bhadrapada'],
    'Antya': ['Krittika', 'Rohini', 'Ashlesha', 'Magha', 'Swati', 'Vishakha', 'Uttara Ashadha', 'Shravana', 'Revati']
}

# Planet lordship for each sign
sign_lords = {
    0: 'Mars',    # Aries
    1: 'Venus',   # Taurus
    2: 'Mercury', # Gemini
    3: 'Moon',    # Cancer
    4: 'Sun',     # Leo
    5: 'Mercury', # Virgo
    6: 'Venus',   # Libra
    7: 'Mars',    # Scorpio
    8: 'Jupiter', # Sagittarius
    9: 'Saturn',  # Capricorn
    10: 'Saturn', # Aquarius
    11: 'Jupiter' # Pisces
}

# Planetary aspects (which houses each planet aspects from its position)
planetary_aspects = {
    'Sun': [7],
    'Moon': [7],
    'Mars': [4, 7, 8],
    'Mercury': [7],
    'Jupiter': [5, 7, 9],
    'Venus': [7],
    'Saturn': [3, 7, 10],
    'Rahu': [5, 7, 9],
    'Ketu': [5, 7, 9]
}

# Own signs and exaltation signs
own_signs = {
    'Sun': [4],           # Leo
    'Moon': [3],          # Cancer
    'Mars': [0, 7],       # Aries, Scorpio
    'Mercury': [2, 5],    # Gemini, Virgo
    'Jupiter': [8, 11],   # Sagittarius, Pisces
    'Venus': [1, 6],      # Taurus, Libra
    'Saturn': [9, 10]     # Capricorn, Aquarius
}

exaltation_signs = {
    'Sun': 0,      # Aries
    'Moon': 1,     # Taurus
    'Mars': 9,     # Capricorn
    'Mercury': 5,  # Virgo
    'Jupiter': 3,  # Cancer
    'Venus': 11,   # Pisces
    'Saturn': 6    # Libra
}

# Conjunction orbs (maximum degrees for planets to be considered conjunct)
conjunction_orbs = {
    'tight': 3,    # Very close conjunction
    'close': 6,    # Close conjunction
    'wide': 10     # Wide conjunction
}

def get_house(lon, asc_sign_index):
    """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def get_nakshatra(longitude):
    """Get nakshatra from longitude."""
    longitude = longitude % 360
    nakshatra_index = int(longitude / (360/27))
    return nakshatras[nakshatra_index]

def get_nadi(nakshatra):
    """Get Nadi for given nakshatra."""
    for nadi, naks in nadi_classification.items():
        if nakshatra in naks:
            return nadi
    return None

def get_house_lord(house_num, asc_sign_index):
    """Get the ruling planet for a house based on ascendant."""
    house_sign_index = (asc_sign_index + house_num - 1) % 12
    return sign_lords[house_sign_index]

def get_planet_house_from_positions(planet_name, planet_positions, asc_sign_index):
    """Get house position of a planet."""
    if planet_name in planet_positions:
        lon = planet_positions[planet_name][0]
        return get_house(lon, asc_sign_index)
    return None

def normalize_longitude_difference(lon1, lon2):
    """Calculate the shortest angular distance between two longitudes."""
    diff = abs(lon1 - lon2)
    return min(diff, 360 - diff)

def are_planets_conjunct(planet1_lon, planet2_lon, orb_type='close'):
    """Check if two planets are conjunct within specified orb."""
    distance = normalize_longitude_difference(planet1_lon, planet2_lon)
    return distance <= conjunction_orbs[orb_type], distance

def get_planetary_aspects(planet_name, planet_house, all_planet_houses):
    """Get which planets this planet aspects."""
    if planet_name not in planetary_aspects:
        return []
    aspected_houses = []
    for aspect_distance in planetary_aspects[planet_name]:
        aspected_house = ((planet_house - 1 + aspect_distance - 1) % 12) + 1
        aspected_houses.append(aspected_house)
    aspected_planets = []
    for planet, house in all_planet_houses.items():
        if house in aspected_houses and planet != planet_name:
            aspected_planets.append(planet)
    return aspected_planets

def is_planet_strong(planet_name, sign_index):
    """Check if planet is strong (own sign, exaltation, or friendly sign)."""
    if planet_name in own_signs and sign_index in own_signs[planet_name]:
        return True, "Own Sign"
    if planet_name in exaltation_signs and sign_index == exaltation_signs[planet_name]:
        return True, "Exaltation"
    return False, "Neutral"

def calculate_kalsarpa_yoga(planet_positions):
    """
    Calculate Kalsarpa Yoga - All 7 planets should be hemmed in one semicircle between Rahu-Ketu axis.
    Uses correct traditional method: Check if all planets are within 180-degree arc.
    """
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = planet_positions['Ketu'][0]
    planets_to_check = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

    def is_between_rahu_ketu_clockwise(planet_lon, rahu_lon, ketu_lon):
        if rahu_lon <= ketu_lon:
            return rahu_lon <= planet_lon <= ketu_lon
        else:
            return planet_lon >= rahu_lon or planet_lon <= ketu_lon

    planets_in_rahu_ketu_arc = []
    planets_in_ketu_rahu_arc = []
    for planet in planets_to_check:
        planet_lon = planet_positions[planet][0]
        if is_between_rahu_ketu_clockwise(planet_lon, rahu_lon, ketu_lon):
            planets_in_rahu_ketu_arc.append(planet)
        else:
            planets_in_ketu_rahu_arc.append(planet)

    kalsarpa_present = (len(planets_in_rahu_ketu_arc) == 7) or (len(planets_in_ketu_rahu_arc) == 7)
    rahu_house = get_house(rahu_lon, 0)
    kalsarpa_types = {
        1: 'Ananta', 2: 'Kulik', 3: 'Vasuki', 4: 'Shankhapal',
        5: 'Padma', 6: 'Mahapadma', 7: 'Takshak', 8: 'Karkotak',
        9: 'Shankhnaad', 10: 'Patak', 11: 'Vishdhar', 12: 'Sheshnag'
    }

    return {
        'present': kalsarpa_present,
        'type': kalsarpa_types.get(rahu_house, 'Unknown') if kalsarpa_present else 'None',
        'planets_in_rahu_ketu_arc': planets_in_rahu_ketu_arc,
        'planets_in_ketu_rahu_arc': planets_in_ketu_rahu_arc,
        'rahu_longitude': round(rahu_lon, 2),
        'ketu_longitude': round(ketu_lon, 2)
    }

def calculate_mangal_dosha(mars_house, mars_sign_index, planet_positions, asc_sign_index):
    """Calculate Mangal Dosha with strict traditional rules and proper cancellations."""
    manglik_houses = [1, 2, 4, 7, 8, 12]
    is_manglik = mars_house in manglik_houses
    cancellations = []

    if mars_sign_index in [0, 7, 9]:  # Aries, Scorpio, Capricorn
        cancellations.append("Mars in own sign or exaltation")

    if mars_house == 2 and mars_sign_index in [2, 5]:
        cancellations.append("Mars in 2nd house in Gemini/Virgo")

    jupiter_house = get_planet_house_from_positions('Jupiter', planet_positions, asc_sign_index)
    if jupiter_house:
        jupiter_strong_aspects = []
        for aspect_distance in [5, 9]:
            aspected_house = ((jupiter_house - 1 + aspect_distance - 1) % 12) + 1
            jupiter_strong_aspects.append(aspected_house)
        if mars_house in jupiter_strong_aspects:
            cancellations.append("Jupiter's strong aspect (5th/9th) on Mars")

    if 'Moon' in planet_positions:
        mars_lon = planet_positions['Mars'][0]
        moon_lon = planet_positions['Moon'][0]
        is_conjunct, distance = are_planets_conjunct(mars_lon, moon_lon, 'close')
        if is_conjunct:
            cancellations.append(f"Mars conjunct Moon (within {distance:.1f}°)")

    dosha_strength = 'None'
    if is_manglik and not cancellations:
        if mars_house in [1, 7, 8]:
            dosha_strength = 'High'
        elif mars_house in [2, 4, 12]:
            dosha_strength = 'Medium'
    elif is_manglik and cancellations:
        dosha_strength = 'Cancelled'

    return {
        'present': is_manglik and not cancellations,
        'mars_house': mars_house,
        'mars_sign': signs[mars_sign_index],
        'dosha_strength': dosha_strength,
        'cancellations': cancellations,
        'raw_manglik': is_manglik
    }

def calculate_nadi_dosha(moon_nakshatra):
    """Calculate Nadi for the person."""
    nadi = get_nadi(moon_nakshatra)
    return {
        'nakshatra': moon_nakshatra,
        'nadi': nadi,
        'note': 'Same Nadi between partners causes Nadi Dosha'
    }

def calculate_indra_yoga(planet_positions, asc_sign_index, planet_houses):
    """
    Calculate Indra Yoga with strict traditional rules.
    """
    fifth_lord = get_house_lord(5, asc_sign_index)
    eleventh_lord = get_house_lord(11, asc_sign_index)
    fifth_lord_house = get_planet_house_from_positions(fifth_lord, planet_positions, asc_sign_index)
    eleventh_lord_house = get_planet_house_from_positions(eleventh_lord, planet_positions, asc_sign_index)
    moon_house = get_planet_house_from_positions('Moon', planet_positions, asc_sign_index)
    indra_conditions = []

    if fifth_lord_house == 11 and eleventh_lord_house == 5:
        indra_conditions.append("5th and 11th lords in exact mutual exchange")

    if (fifth_lord in planet_positions and eleventh_lord in planet_positions and fifth_lord != eleventh_lord):
        fifth_lord_lon = planet_positions[fifth_lord][0]
        eleventh_lord_lon = planet_positions[eleventh_lord][0]
        is_conjunct, distance = are_planets_conjunct(fifth_lord_lon, eleventh_lord_lon, 'close')
        if is_conjunct:
            indra_conditions.append(f"5th lord {fifth_lord} and 11th lord {eleventh_lord} in tight conjunction ({distance:.1f}°)")

    if fifth_lord in planet_positions and eleventh_lord in planet_positions:
        fifth_lord_sign = int(planet_positions[fifth_lord][0] // 30)
        eleventh_lord_sign = int(planet_positions[eleventh_lord][0] // 30)
        fifth_strong, fifth_reason = is_planet_strong(fifth_lord, fifth_lord_sign)
        eleventh_strong, eleventh_reason = is_planet_strong(eleventh_lord, eleventh_lord_sign)
        moon_in_kendra = moon_house in [1, 4, 7, 10] if moon_house else False
        if fifth_strong and eleventh_strong and moon_in_kendra:
            indra_conditions.append(f"Both lords strong ({fifth_lord}: {fifth_reason}, {eleventh_lord}: {eleventh_reason}) with Moon in Kendra")

    if fifth_lord_house and eleventh_lord_house and fifth_lord != eleventh_lord:
        fifth_lord_aspects = get_planetary_aspects(fifth_lord, fifth_lord_house, planet_houses)
        eleventh_lord_aspects = get_planetary_aspects(eleventh_lord, eleventh_lord_house, planet_houses)
        mutual_aspect = (eleventh_lord in fifth_lord_aspects and fifth_lord in eleventh_lord_aspects)
        if mutual_aspect:
            jupiter_house = planet_houses.get('Jupiter')
            venus_house = planet_houses.get('Venus')
            benefic_influence = False
            if jupiter_house:
                jupiter_aspects = get_planetary_aspects('Jupiter', jupiter_house, planet_houses)
                if fifth_lord in jupiter_aspects or eleventh_lord in jupiter_aspects:
                    benefic_influence = True
            if venus_house and not benefic_influence:
                venus_aspects = get_planetary_aspects('Venus', venus_house, planet_houses)
                if fifth_lord in venus_aspects or eleventh_lord in venus_aspects:
                    benefic_influence = True
            if benefic_influence:
                indra_conditions.append("5th and 11th lords in mutual aspect with benefic influence")

    indra_present = len(indra_conditions) > 0
    return {
        'present': indra_present,
        'conditions_met': indra_conditions,
        'fifth_lord': fifth_lord,
        'eleventh_lord': eleventh_lord,
        'fifth_lord_house': fifth_lord_house,
        'eleventh_lord_house': eleventh_lord_house,
        'moon_house': moon_house,
        'strength': 'Strong' if len(indra_conditions) >= 2 else 'Moderate' if len(indra_conditions) == 1 else 'None'
    }

def calculate_sanyasa_yoga(planet_positions, asc_sign_index, planet_houses):
    """
    Calculate Sanyasa Yoga with strict traditional conditions:
    Requires at least 2 strong conditions for true Sanyasa Yoga
    """
    sanyasa_conditions = []
    house_groups = {}
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        house = planet_houses.get(planet)
        if house:
            house_groups.setdefault(house, []).append(planet)

    for house, planets_in_house in house_groups.items():
        if len(planets_in_house) >= 4:
            longitudes = [planet_positions[planet][0] for planet in planets_in_house]
            longitude_span = max(longitudes) - min(longitudes)
            if longitude_span <= 20 or longitude_span >= 340:
                sanyasa_conditions.append(f"Four planets in tight conjunction in house {house}: {', '.join(planets_in_house)}")

    tenth_lord = get_house_lord(10, asc_sign_index)
    tenth_lord_house = get_planet_house_from_positions(tenth_lord, planet_positions, asc_sign_index)
    if tenth_lord_house and tenth_lord_house in house_groups:
        if len(house_groups[tenth_lord_house]) >= 4:
            sanyasa_conditions.append(f"10th lord {tenth_lord} with four planets in house {tenth_lord_house}")

    saturn_house = planet_houses.get('Saturn')
    moon_house = planet_houses.get('Moon')
    venus_house = planet_houses.get('Venus')
    if saturn_house and moon_house and venus_house and saturn_house == moon_house == venus_house:
        saturn_lon = planet_positions['Saturn'][0]
        moon_lon = planet_positions['Moon'][0]
        venus_lon = planet_positions['Venus'][0]
        distances = [
            normalize_longitude_difference(saturn_lon, moon_lon),
            normalize_longitude_difference(saturn_lon, venus_lon),
            normalize_longitude_difference(moon_lon, venus_lon)
        ]
        if all(d <= 10 for d in distances):
            sanyasa_conditions.append(f"Saturn, Moon, Venus in tight conjunction in house {saturn_house}")

    jupiter_house = planet_houses.get('Jupiter')
    if jupiter_house and jupiter_house in [1, 4, 7, 10]:
        jupiter_house_planets = house_groups.get(jupiter_house, [])
        if len(jupiter_house_planets) == 1:
            planets_in_8_12 = []
            for planet, house in planet_houses.items():
                if planet not in ['Jupiter', 'Rahu', 'Ketu'] and house in [8, 12]:
                    planets_in_8_12.append(f"{planet} in {house}th")
            if len(planets_in_8_12) >= 4:
                sanyasa_conditions.append(f"Jupiter alone in Kendra (house {jupiter_house}) with {len(planets_in_8_12)} planets in 8th/12th")

    benefics = ['Jupiter', 'Venus', 'Mercury', 'Moon']
    benefic_kendras = {}
    for benefic in benefics:
        house = planet_houses.get(benefic)
        if house and house in [1, 4, 7, 10]:
            benefic_kendras[benefic] = house
    if len(benefic_kendras) == 4 and len(set(benefic_kendras.values())) == 4:
        sanyasa_conditions.append("All four benefics in four different Kendras")

    sanyasa_present = len(sanyasa_conditions) >= 2
    return {
        'present': sanyasa_present,
        'conditions_met': sanyasa_conditions,
        'strength': 'Very Strong' if len(sanyasa_conditions) >= 3 else 'Strong' if len(sanyasa_conditions) == 2 else 'Weak' if len(sanyasa_conditions) == 1 else 'None',
        'total_conditions': len(sanyasa_conditions),
        'note': 'Requires at least 2 strong conditions for true Sanyasa Yoga'
    }

def calculate_moksha_yogas(planet_positions, asc_sign_index, planet_houses):
    """
    Calculate Moksha (Liberation) yogas with strict traditional rules:
    Requires multiple strong indicators for true Moksha Yoga
    """
    moksha_indicators = []
    twelfth_lord = get_house_lord(12, asc_sign_index)
    twelfth_lord_house = get_planet_house_from_positions(twelfth_lord, planet_positions, asc_sign_index)
    if twelfth_lord_house == 12:
        jupiter_house = planet_houses.get('Jupiter')
        venus_house = planet_houses.get('Venus')
        benefic_aspect = False
        if jupiter_house:
            jupiter_aspects = get_planetary_aspects('Jupiter', jupiter_house, planet_houses)
            if twelfth_lord in jupiter_aspects:
                benefic_aspect = True
        if venus_house and not benefic_aspect:
            venus_aspects = get_planetary_aspects('Venus', venus_house, planet_houses)
            if twelfth_lord in venus_aspects:
                benefic_aspect = True
        if benefic_aspect:
            moksha_indicators.append(f"12th lord {twelfth_lord} in 12th house with benefic aspect")
        else:
            moksha_indicators.append(f"12th lord {twelfth_lord} in 12th house")

    ketu_house = planet_houses.get('Ketu')
    jupiter_house = planet_houses.get('Jupiter')
    if ketu_house == 12 and jupiter_house:
        jupiter_aspects = get_planetary_aspects('Jupiter', jupiter_house, planet_houses)
        if 'Ketu' in jupiter_aspects:
            moksha_indicators.append("Ketu in 12th house with Jupiter's direct aspect")

    moon_house = planet_houses.get('Moon')
    if jupiter_house == 12 and moon_house == 12:
        jupiter_lon = planet_positions['Jupiter'][0]
        moon_lon = planet_positions['Moon'][0]
        is_conjunct, distance = are_planets_conjunct(jupiter_lon, moon_lon, 'close')
        if is_conjunct:
            moksha_indicators.append(f"Jupiter-Moon tight conjunction in 12th house ({distance:.1f}°)")

    if jupiter_house and ketu_house:
        if jupiter_house == ketu_house:
            jupiter_lon = planet_positions['Jupiter'][0]
            ketu_lon = planet_positions['Ketu'][0]
            is_conjunct, distance = are_planets_conjunct(jupiter_lon, ketu_lon, 'close')
            if is_conjunct:
                moksha_indicators.append(f"Ketu-Jupiter tight conjunction ({distance:.1f}°)")
        else:
            jupiter_aspects = get_planetary_aspects('Jupiter', jupiter_house, planet_houses)
            ketu_aspects = get_planetary_aspects('Ketu', ketu_house, planet_houses)
            if 'Ketu' in jupiter_aspects and 'Jupiter' in ketu_aspects:
                moksha_indicators.append("Ketu-Jupiter mutual aspect")

    saturn_house = planet_houses.get('Saturn')
    if saturn_house == 8:
        spiritual_enhancement = False
        if jupiter_house:
            jupiter_aspects = get_planetary_aspects('Jupiter', jupiter_house, planet_houses)
            if 'Saturn' in jupiter_aspects:
                spiritual_enhancement = True
        if not spiritual_enhancement and moon_house == saturn_house:
            spiritual_enhancement = True
        if spiritual_enhancement:
            moksha_indicators.append("Saturn in 8th house with spiritual enhancement")
        else:
            moksha_indicators.append("Saturn in 8th house")

    moksha_house_planets = []
    strong_moksha_planets = []
    for planet, house in planet_houses.items():
        if house in [4, 8, 12] and planet not in ['Rahu', 'Ketu']:
            moksha_house_planets.append(f"{planet} in {house}th")
            if planet in planet_positions:
                sign_index = int(planet_positions[planet][0] // 30)
                is_strong, reason = is_planet_strong(planet, sign_index)
                if is_strong:
                    strong_moksha_planets.append(f"{planet} ({reason}) in {house}th")

    if len(moksha_house_planets) >= 5:
        moksha_indicators.append(f"Multiple planets in moksha houses: {', '.join(moksha_house_planets)}")
    if len(strong_moksha_planets) >= 2:
        moksha_indicators.append(f"Strong planets in moksha houses: {', '.join(strong_moksha_planets)}")

    moksha_present = len(moksha_indicators) >= 2
    return {
        'present': moksha_present,
        'indicators': moksha_indicators,
        'moksha_house_planets': moksha_house_planets,
        'strength': 'Very Strong' if len(moksha_indicators) >= 4 else 'Strong' if len(moksha_indicators) == 3 else 'Moderate' if len(moksha_indicators) == 2 else 'Weak' if len(moksha_indicators) == 1 else 'None',
        'note': 'Requires at least 2 strong indicators for true Moksha Yoga'
    }

def calculate_brahma_yoga(planet_positions, asc_sign_index, planet_houses):
    """
    Calculate Brahma Yoga with strict traditional rules.
    """
    brahma_conditions = []
    jupiter_house = planet_houses.get('Jupiter')
    venus_house = planet_houses.get('Venus')
    mercury_house = planet_houses.get('Mercury')
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]
    good_houses = [1, 4, 5, 7, 9, 10]

    jupiter_in_kendra = jupiter_house in kendra_houses if jupiter_house else False
    venus_in_kendra = venus_house in kendra_houses if venus_house else False
    mercury_in_kendra = mercury_house in kendra_houses if mercury_house else False
    venus_in_good_house = venus_house in good_houses if venus_house else False
    mercury_in_good_house = mercury_house in good_houses if mercury_house else False

    sun_lon = planet_positions['Sun'][0]
    planet_strengths_map = {}
    combustion_issues = []
    for planet in ['Jupiter', 'Venus', 'Mercury']:
        if planet in planet_positions:
            planet_lon = planet_positions[planet][0]
            sign_index = int(planet_lon // 30)
            is_strong, strength_reason = is_planet_strong(planet, sign_index)
            planet_strengths_map[planet] = (is_strong, strength_reason)
            distance = normalize_longitude_difference(sun_lon, planet_lon)
            combustion_distances = {'Jupiter': 11, 'Venus': 10, 'Mercury': 14}
            if distance <= combustion_distances[planet]:
                combustion_issues.append(f"{planet} combusted by Sun ({distance:.1f}°)")

    malefic_aspects = []
    malefics = ['Mars', 'Saturn', 'Rahu']
    for malefic in malefics:
        malefic_house = planet_houses.get(malefic)
        if malefic_house:
            malefic_aspect_list = get_planetary_aspects(malefic, malefic_house, planet_houses)
            for planet in ['Jupiter', 'Venus', 'Mercury']:
                if planet in malefic_aspect_list:
                    malefic_aspects.append(f"{malefic} aspects {planet}")

    primary_brahma = jupiter_in_kendra and venus_in_kendra and mercury_in_kendra
    alternative_brahma = jupiter_in_kendra and venus_in_good_house and mercury_in_good_house
    all_planets_strong = all(planet_strengths_map.get(p, (False, ""))[0] for p in ['Jupiter', 'Venus', 'Mercury'])
    at_least_two_strong = sum(1 for p in ['Jupiter', 'Venus', 'Mercury'] if planet_strengths_map.get(p, (False, ""))[0]) >= 2

    conditions_for_brahma = []
    if primary_brahma:
        conditions_for_brahma.append("All three planets (Jupiter, Venus, Mercury) in Kendra houses")
    elif alternative_brahma:
        conditions_for_brahma.append("Jupiter in Kendra with Venus and Mercury in good houses")
    if len(combustion_issues) == 0:
        conditions_for_brahma.append("No combustion issues")
    if len(malefic_aspects) <= 1:
        conditions_for_brahma.append("Minimal malefic aspects")
    if at_least_two_strong:
        conditions_for_brahma.append("At least two planets are strong")

    brahma_present = (primary_brahma or alternative_brahma) and len(combustion_issues) == 0 and len(malefic_aspects) <= 1

    return {
        'present': brahma_present,
        'type': 'Primary' if primary_brahma and brahma_present else 'Alternative' if alternative_brahma and brahma_present else 'None',
        'conditions_met': conditions_for_brahma,
        'jupiter_house': jupiter_house,
        'venus_house': venus_house,
        'mercury_house': mercury_house,
        'planet_strengths': planet_strengths_map,
        'combustion_issues': combustion_issues,
        'malefic_aspects': malefic_aspects,
        'primary_brahma': primary_brahma,
        'alternative_brahma': alternative_brahma,
        'note': 'Requires proper placement, strength, and freedom from combustion/malefic aspects'
    }

def addSpecialYogas(birth_data):
    """
    Pure function that performs the exact same calculations as your original /special-yogas endpoint
    and returns the response dict (no Flask objects here).
    """
    # Extract & validate inputs (same logic as original)
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
            raise RuntimeError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Ketu opposite Rahu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Ascendant & houses
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    planet_houses = {}
    planet_signs = {}
    for planet, (lon, _) in planet_positions.items():
        planet_houses[planet] = get_house(lon, asc_sign_index)
        _, _, sign_index = longitude_to_sign(lon)
        planet_signs[planet] = sign_index

    # Moon nakshatra for Nadi
    moon_lon = planet_positions['Moon'][0]
    moon_nakshatra = get_nakshatra(moon_lon)

    # Calculate all Special Yogas (exact rules preserved)
    special_yogas = {}

    kalsarpa = calculate_kalsarpa_yoga(planet_positions)
    kalsarpa['rahu_house'] = planet_houses['Rahu']
    kalsarpa['ketu_house'] = planet_houses['Ketu']
    special_yogas['kalsarpa_yoga'] = kalsarpa

    special_yogas['mangal_dosha'] = calculate_mangal_dosha(
        planet_houses['Mars'],
        planet_signs['Mars'],
        planet_positions,
        asc_sign_index
    )

    special_yogas['nadi_dosha'] = calculate_nadi_dosha(moon_nakshatra)

    special_yogas['indra_yoga'] = calculate_indra_yoga(planet_positions, asc_sign_index, planet_houses)

    special_yogas['sanyasa_yoga'] = calculate_sanyasa_yoga(planet_positions, asc_sign_index, planet_houses)

    special_yogas['moksha_yogas'] = calculate_moksha_yogas(planet_positions, asc_sign_index, planet_houses)

    special_yogas['brahma_yoga'] = calculate_brahma_yoga(planet_positions, asc_sign_index, planet_houses)

    chart_details = {
        'ascendant_sign': asc_sign,
        'ascendant_longitude': round(ascendant_lon, 4),
        'ayanamsa_value': round(ayanamsa_value, 6),
        'planetary_houses': planet_houses,
        'planetary_signs': {planet: signs[sign_idx] for planet, sign_idx in planet_signs.items()},
        'planetary_longitudes': {planet: round(lon, 4) for planet, (lon, _) in planet_positions.items()}
    }

    active_yogas = []
    for yoga_name, yoga_data in special_yogas.items():
        if isinstance(yoga_data, dict) and yoga_data.get('present', False):
            strength = yoga_data.get('strength', 'Unknown')
            if strength in ['Strong', 'Very Strong', 'Moderate']:
                active_yogas.append(f"{yoga_name.replace('_', ' ').title()} ({strength})")
            elif yoga_name in ['kalsarpa_yoga', 'mangal_dosha', 'nadi_dosha']:
                active_yogas.append(yoga_name.replace('_', ' ').title())

    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "birth_location": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": timezone_offset
            }
        },
        "chart_details": chart_details,
        "special_yogas": special_yogas,
        "active_yogas_summary": active_yogas,
        "calculation_notes": {
            "ayanamsa": "Lahiri",
            "house_system": "Whole Sign",
            "calculation_method": "Sidereal",
            "ephemeris": "Swiss Ephemeris",
            "yoga_validation": "Strict traditional rules applied",
            "conjunction_orbs": conjunction_orbs,
            "aspects_included": True,
            "combustion_checked": True
        }
    }
    return response
