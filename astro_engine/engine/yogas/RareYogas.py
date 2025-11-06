from datetime import datetime, timedelta
import swisseph as swe

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Sign rulerships for calculating house lords
sign_rulers = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Sign classifications
movable_signs = ['Aries', 'Cancer', 'Libra', 'Capricorn']
fixed_signs = ['Taurus', 'Leo', 'Scorpio', 'Aquarius']
dual_signs = ['Gemini', 'Virgo', 'Sagittarius', 'Pisces']

# Planet strength in signs
planet_exaltation = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn', 'Mercury': 'Virgo',
    'Jupiter': 'Cancer', 'Venus': 'Pisces', 'Saturn': 'Libra'
}

planet_debilitation = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer', 'Mercury': 'Pisces',
    'Jupiter': 'Capricorn', 'Venus': 'Virgo', 'Saturn': 'Aries'
}

planet_own_signs = {
    'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mars': ['Aries', 'Scorpio'],
    'Mercury': ['Gemini', 'Virgo'], 'Jupiter': ['Sagittarius', 'Pisces'],
    'Venus': ['Taurus', 'Libra'], 'Saturn': ['Capricorn', 'Aquarius']
}

# Natural malefics and benefics
natural_malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
natural_benefics = ['Moon', 'Mercury', 'Jupiter', 'Venus']


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
    return sign, sign_deg

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_house_lord(house_number, asc_sign_index):
    """Get the ruling planet of a house based on Whole Sign system."""
    house_sign_index = (asc_sign_index + house_number - 1) % 12
    house_sign = signs[house_sign_index]
    return sign_rulers[house_sign]

def get_planet_strength(planet, planet_sign):
    """Determine planet's strength in its current sign."""
    if planet in ['Rahu', 'Ketu']:
        return 'neutral'  # Shadow planets don't have traditional strength
    
    if planet_sign == planet_exaltation.get(planet):
        return 'exalted'
    elif planet_sign == planet_debilitation.get(planet):
        return 'debilitated'
    elif planet_sign in planet_own_signs.get(planet, []):
        return 'own_sign'
    else:
        return 'neutral'

def is_planet_functionally_benefic(planet, asc_sign_index):
    """Check if planet is functionally benefic for given ascendant."""
    ruled_houses = []
    for house_num in range(1, 13):
        house_lord = get_house_lord(house_num, asc_sign_index)
        if house_lord == planet:
            ruled_houses.append(house_num)
    
    trikona_lord = any(house in [1, 5, 9] for house in ruled_houses)
    dusthana_lord = any(house in [6, 8, 12] for house in ruled_houses)
    kendra_lord = any(house in [4, 7, 10] for house in ruled_houses)
    
    if trikona_lord and not dusthana_lord:
        return True
    elif dusthana_lord:
        return False
    elif planet in natural_benefics and not kendra_lord:
        return True
    else:
        return False

def analyze_nabhas_yogas(planet_houses, planetary_positions):
    """Analyze Nabhas Yogas according to classical BPHS rules."""
    yogas_found = []
    traditional_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    planet_signs = {}
    for planet in traditional_planets:
        sign, _ = longitude_to_sign(planetary_positions[planet][0])
        planet_signs[planet] = sign
    
    occupied_houses = [planet_houses[planet] for planet in traditional_planets]
    unique_houses = sorted(list(set(occupied_houses)))
    num_houses = len(unique_houses)
    
    movable_count = sum(1 for planet in traditional_planets if planet_signs[planet] in movable_signs)
    fixed_count = sum(1 for planet in traditional_planets if planet_signs[planet] in fixed_signs)
    dual_count = sum(1 for planet in traditional_planets if planet_signs[planet] in dual_signs)
    
    asraya_yoga_found = False
    if movable_count == 7:
        asraya_yoga_found = True
        yogas_found.append({
            "type": "Asraya Yoga",
            "name": "Rajju",
            "description": "All 7 planets in movable signs (Aries, Cancer, Libra, Capricorn)",
            "signs_involved": [planet_signs[p] for p in traditional_planets],
            "classical_result": "Fond of travel, handsome, earns in foreign countries, somewhat cruel"
        })
    elif fixed_count == 7:
        asraya_yoga_found = True
        yogas_found.append({
            "type": "Asraya Yoga",
            "name": "Musala",
            "description": "All 7 planets in fixed signs (Taurus, Leo, Scorpio, Aquarius)",
            "signs_involved": [planet_signs[p] for p in traditional_planets],
            "classical_result": "Honorable, wealthy, wise, steady mind, famous"
        })
    elif dual_count == 7:
        asraya_yoga_found = True
        yogas_found.append({
            "type": "Asraya Yoga",
            "name": "Nala",
            "description": "All 7 planets in dual signs (Gemini, Virgo, Sagittarius, Pisces)",
            "signs_involved": [planet_signs[p] for p in traditional_planets],
            "classical_result": "Deformed body, skilled in money matters, helpful to relatives"
        })
    
    sankhya_yogas = {
        1: "Gola", 2: "Yuga", 3: "Sool", 4: "Kedara",
        5: "Paash", 6: "Daam", 7: "Veena"
    }
    if not asraya_yoga_found and num_houses in sankhya_yogas:
        classical_results = {
            "Gola": "Indigent, lazy, devoid of learning, dirty, sorrowful",
            "Yuga": "Religious hypocrite, poor, forsaken, devoid of sons",
            "Sool": "Harsh, lazy, poor, bold, successful in war",
            "Kedara": "Agriculturist, truthful, wealthy, helpful to many",
            "Paash": "Liable to imprisonment, talkative, many servants",
            "Daam": "Controls animals, charitable, rich, helpful",
            "Veena": "Eloquent, interested in arts, happy, many friends"
        }
        yogas_found.append({
            "type": "Sankhya Yoga",
            "name": sankhya_yogas[num_houses],
            "description": f"All 7 planets occupy {num_houses} houses",
            "houses_occupied": unique_houses,
            "classical_result": classical_results.get(sankhya_yogas[num_houses], "")
        })
    
    if not asraya_yoga_found:
        kendras = [1, 4, 7, 10]
        for i in range(len(kendras)):
            kendra1 = kendras[i]
            kendra2 = kendras[(i + 1) % 4]
            if set(occupied_houses).issubset({kendra1, kendra2}) and len(set(occupied_houses)) == 2:
                yogas_found.append({
                    "type": "Akriti Yoga",
                    "name": "Gada",
                    "description": f"All planets in houses {kendra1} and {kendra2} (successive Kendras)",
                    "houses_occupied": unique_houses,
                    "classical_result": "Efforts to earn wealth, skilled in shastras, wealthy"
                })
                break
        
        if set(occupied_houses).issubset({1, 7}):
            yogas_found.append({
                "type": "Akriti Yoga", 
                "name": "Sakata",
                "description": "All planets in 1st and 7th houses",
                "houses_occupied": unique_houses,
                "classical_result": "Diseased, poor, pulls carts, foolish"
            })
        
        if set(occupied_houses).issubset({4, 10}):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Vihaga", 
                "description": "All planets in 4th and 10th houses",
                "houses_occupied": unique_houses,
                "classical_result": "Messenger, travels, quarrelsome, shameless"
            })
        
        if set(occupied_houses).issubset({1, 5, 9}):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Shringataka",
                "description": "All planets in 1st, 5th, and 9th houses (all Trikonas)",
                "houses_occupied": unique_houses,
                "classical_result": "Happy, dear to king, rich, hates women"
            })
        
        hala_combinations = [
            {2, 6, 10}, {3, 7, 11}, {4, 8, 12}
        ]
        for combo in hala_combinations:
            if set(occupied_houses).issubset(combo):
                yogas_found.append({
                    "type": "Akriti Yoga",
                    "name": "Hala",
                    "description": f"All planets in houses {sorted(combo)}",
                    "houses_occupied": unique_houses,
                    "classical_result": "Eats a lot, poor, miserable, servant"
                })
                break
        
        benefic_planets = [p for p in traditional_planets if p in natural_benefics]
        malefic_planets = [p for p in traditional_planets if p in natural_malefics]
        
        benefic_houses = [planet_houses[p] for p in benefic_planets]
        malefic_houses = [planet_houses[p] for p in malefic_planets]
        
        if (all(h in [1, 7] for h in benefic_houses) or 
            all(h in [4, 10] for h in malefic_houses)):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Vajra",
                "description": "All benefics in 1st & 7th OR all malefics in 4th & 10th",
                "houses_occupied": unique_houses,
                "classical_result": "Immense happiness, wealth, virtuous"
            })
        
        if (all(h in [4, 10] for h in benefic_houses) or 
            all(h in [1, 7] for h in malefic_houses)):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Yava",
                "description": "All benefics in 4th & 10th OR all malefics in 1st & 7th",
                "houses_occupied": unique_houses,
                "classical_result": "Happy in middle age, charitable"
            })
        
        if set(occupied_houses).issubset({1, 4, 7, 10}):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Kamala",
                "description": "All planets in four Kendras (1, 4, 7, 10)",
                "houses_occupied": unique_houses,
                "classical_result": "Great wealth, long life, good reputation"
            })
        
        panapharas = {2, 5, 8, 11}
        apoklimas = {3, 6, 9, 12}
        
        if set(occupied_houses).issubset(panapharas):
            yogas_found.append({
                "type": "Akriti Yoga",
                "name": "Vapi",
                "description": "All planets in Panapharas (2, 5, 8, 11)",
                "houses_occupied": unique_houses,
                "classical_result": "Accumulates wealth, good business"
            })
        elif set(occupied_houses).issubset(apoklimas):
            yogas_found.append({
                "type": "Akriti Yoga", 
                "name": "Vapi",
                "description": "All planets in Apoklimas (3, 6, 9, 12)",
                "houses_occupied": unique_houses,
                "classical_result": "Accumulates wealth, good business"
            })
    
    planets_except_moon = [p for p in traditional_planets if p != 'Moon']
    kendra_planets = [p for p in planets_except_moon if planet_houses[p] in [1, 4, 7, 10]]
    
    if len(kendra_planets) >= 3:
        all_benefic = all(p in natural_benefics for p in kendra_planets)
        all_malefic = all(p in natural_malefics for p in kendra_planets)
        
        if all_benefic:
            yogas_found.append({
                "type": "Dala Yoga",
                "name": "Mala",
                "description": f"Benefics (excluding Moon) in Kendras: {', '.join(kendra_planets)}",
                "planets_involved": kendra_planets,
                "classical_result": "Happy, wealthy, conveyances, pleasures"
            })
        elif all_malefic:
            yogas_found.append({
                "type": "Dala Yoga",
                "name": "Sarpa",
                "description": f"Malefics (excluding Moon) in Kendras: {', '.join(kendra_planets)}", 
                "planets_involved": kendra_planets,
                "classical_result": "Crooked, cruel, poor, miserable"
            })
    
    return yogas_found

def analyze_indra_yoga(planet_houses, asc_sign_index, planetary_positions):
    """
    Note: Indra Yoga is NOT found in classical BPHS texts.
    This is a modern interpretation based on 5th-11th lord relationship.
    """
    yogas_found = []
    
    fifth_lord = get_house_lord(5, asc_sign_index)
    eleventh_lord = get_house_lord(11, asc_sign_index)
    
    if fifth_lord not in planetary_positions or eleventh_lord not in planetary_positions:
        return yogas_found
    
    fifth_lord_house = planet_houses.get(fifth_lord)
    eleventh_lord_house = planet_houses.get(eleventh_lord)
    
    if fifth_lord_house == 11 and eleventh_lord_house == 5:
        yogas_found.append({
            "type": "Modern Indra Yoga",
            "name": "Indra Yoga (Parivartana)",
            "description": f"5th lord ({fifth_lord}) in 11th house exchanges with 11th lord ({eleventh_lord}) in 5th house",
            "formation": "Complete exchange between wealth and intelligence lords",
            "strength": "Very Strong",
            "note": "Not found in classical BPHS - modern interpretation"
        })
    elif (fifth_lord_house in [1, 4, 5, 7, 9, 10, 11] and 
          eleventh_lord_house in [1, 4, 5, 7, 9, 10, 11]):
        both_benefic = (fifth_lord in natural_benefics and eleventh_lord in natural_benefics)
        if both_benefic:
            yogas_found.append({
                "type": "Modern Indra Yoga",
                "name": "Indra Yoga (Modified)",
                "description": f"5th lord ({fifth_lord}) in {fifth_lord_house}th house, 11th lord ({eleventh_lord}) in {eleventh_lord_house}th house",
                "formation": "Both lords well-placed in auspicious houses as benefics",
                "strength": "Medium",
                "note": "Not found in classical BPHS - modern interpretation"
            })
    
    return yogas_found

def analyze_arishta_yogas(planet_houses, asc_sign_index, planetary_positions):
    """Analyze Arishta Yogas with CORRECTED logic addressing all issues."""
    arishta_combinations = []
    cancellations = []
    
    lagna_sign = signs[asc_sign_index]
    lagna_lord = sign_rulers[lagna_sign]
    lagna_lord_house = planet_houses.get(lagna_lord)
    
    planet_signs = {}
    planet_strengths = {}
    for planet, (lon, _) in planetary_positions.items():
        if planet != 'Ketu':
            sign, _ = longitude_to_sign(lon)
            planet_signs[planet] = sign
            planet_strengths[planet] = get_planet_strength(planet, sign)
    
    ketu_sign, _ = longitude_to_sign(planetary_positions['Ketu'][0])
    planet_signs['Ketu'] = ketu_sign
    planet_strengths['Ketu'] = 'neutral'
    
    sun_lon = planetary_positions['Sun'][0]
    moon_lon = planetary_positions['Moon'][0]
    moon_sun_distance = abs(moon_lon - sun_lon)
    if moon_sun_distance > 180:
        moon_sun_distance = 360 - moon_sun_distance
    
    moon_house = planet_houses['Moon']
    moon_sign = planet_signs['Moon']
    moon_strength = planet_strengths['Moon']
    
    if lagna_lord_house in [6, 8, 12]:
        lord_strength = planet_strengths.get(lagna_lord, 'neutral')
        if lord_strength not in ['exalted', 'own_sign']:
            severity = "Very High" if lagna_lord_house == 8 else "High"
            arishta_combinations.append({
                "type": "Basic Arishta",
                "description": f"Lagna lord ({lagna_lord}) weak in {lagna_lord_house}th house (dusthana)",
                "severity": severity,
                "house": lagna_lord_house,
                "classical_reference": "BPHS - Weak lagna lord in evil houses"
            })
    
    if moon_house in [6, 8, 12]:
        if moon_strength in ['debilitated'] or (moon_strength == 'neutral' and moon_sun_distance < 30):
            severity = "Very High" if moon_house == 8 else "High"
            arishta_combinations.append({
                "type": "Moon Arishta",
                "description": f"Weak Moon in {moon_house}th house (dusthana)",
                "severity": severity,
                "house": moon_house,
                "classical_reference": "Classical - Weak Moon in evil houses"
            })
    
    if moon_sun_distance < 30 and moon_strength not in ['exalted', 'own_sign']:
        malefic_influence = False
        malefics_with_moon = []
        for planet, house in planet_houses.items():
            if house == moon_house and planet in natural_malefics and planet != 'Sun':
                malefic_influence = True
                malefics_with_moon.append(planet)
        if malefic_influence and moon_strength not in ['own_sign', 'exalted']:
            arishta_combinations.append({
                "type": "Weak Moon Arishta",
                "description": f"New Moon with malefic influence from: {', '.join(malefics_with_moon)}",
                "severity": "Medium",
                "house": moon_house,
                "classical_reference": "Weak Moon with malefic aspects"
            })
    
    rahu_house = planet_houses.get('Rahu')
    if rahu_house == 8:
        arishta_combinations.append({
            "type": "Rahu in 8th House",
            "description": "Rahu in 8th house (house of longevity)",
            "severity": "Very High",
            "house": 8,
            "classical_reference": "Shadow planet in house of death/longevity"
        })
    
    ketu_house = planet_houses.get('Ketu')
    if ketu_house == 2:
        arishta_combinations.append({
            "type": "Ketu in 2nd House",
            "description": "Ketu in 2nd house (Maraka house)",
            "severity": "High",
            "house": 2,
            "classical_reference": "Shadow planet in Maraka house"
        })
    
    malefics_in_lagna = [planet for planet in natural_malefics 
                        if planet_houses.get(planet) == 1]
    if len(malefics_in_lagna) >= 2:
        arishta_combinations.append({
            "type": "Multiple Malefics in Lagna",
            "description": f"Multiple malefics in Lagna: {', '.join(malefics_in_lagna)}",
            "severity": "Very High",
            "house": 1,
            "classical_reference": "Multiple malefics in ascendant"
        })
    
    eighth_house_malefics = []
    for planet in ['Mars', 'Saturn', 'Sun']:
        if planet_houses.get(planet) == 8:
            eighth_house_malefics.append(planet)
    if eighth_house_malefics:
        arishta_combinations.append({
            "type": "8th House Malefic",
            "description": f"Malefic(s) in 8th house: {', '.join(eighth_house_malefics)}",
            "severity": "Very High",
            "house": 8,
            "classical_reference": "Malefics in house of longevity"
        })
    
    mars_house = planet_houses.get('Mars')
    if mars_house == moon_house:
        if moon_strength not in ['exalted', 'own_sign'] or mars_house in [6, 8, 12]:
            arishta_combinations.append({
                "type": "Mars-Moon Conjunction",
                "description": f"Mars with Moon in {mars_house}th house",
                "severity": "Medium",
                "house": mars_house,
                "classical_reference": "Malefic with Lagna lord"
            })
    
    saturn_house = planet_houses.get('Saturn')
    if saturn_house == 8 and moon_house == 1:
        arishta_combinations.append({
            "type": "Saturn-Moon Classical Arishta",
            "description": "Saturn in 8th house with Moon in Lagna",
            "severity": "Very High",
            "house": [1, 8],
            "classical_reference": "Classical combination for health issues"
        })
    
    fifth_house_malefics = []
    for planet in ['Sun', 'Mars', 'Saturn']:
        if planet_houses.get(planet) == 5:
            fifth_house_malefics.append(planet)
    if len(fifth_house_malefics) >= 2:
        arishta_combinations.append({
            "type": "5th House Affliction",
            "description": f"Multiple malefics in 5th house: {', '.join(fifth_house_malefics)}",
            "severity": "High",
            "house": 5,
            "classical_reference": "Affliction to house of past karma"
        })
    
    balarishta_factors = []
    if mars_house == 7:
        balarishta_factors.append("Mars in 7th")
    if rahu_house == 9:
        balarishta_factors.append("Rahu in 9th")
    if saturn_house == 1:
        balarishta_factors.append("Saturn in Lagna")
    if planet_houses.get('Jupiter') == 3:
        balarishta_factors.append("Jupiter in 3rd")
    if planet_houses.get('Venus') == 6:
        balarishta_factors.append("Venus in 6th")
    if moon_house in [6, 8] and any(planet_houses.get(mal) == moon_house 
                                   for mal in ['Mars', 'Saturn'] if mal in planet_houses):
        balarishta_factors.append("Moon in 6th/8th with malefics")
    if len(balarishta_factors) >= 2:
        arishta_combinations.append({
            "type": "Balarishta",
            "description": f"Childhood Arishta factors: {', '.join(balarishta_factors)}",
            "severity": "Very High",
            "house": "Multiple",
            "classical_reference": "Classical Balarishta combinations"
        })
    
    jupiter_house = planet_houses.get('Jupiter')
    venus_house = planet_houses.get('Venus')
    jupiter_strength = planet_strengths.get('Jupiter', 'neutral')
    venus_strength = planet_strengths.get('Venus', 'neutral')
    
    if jupiter_house in [1, 4, 7, 10] and venus_house in [1, 4, 7, 10]:
        cancellations.append({
            "type": "Strong Benefic Protection",
            "description": f"Jupiter in {jupiter_house}th and Venus in {venus_house}th (both in Kendras)",
            "effect": "Strong protection against Arishta",
            "strength": "Very Strong"
        })
    elif jupiter_house in [1, 4, 7, 10] and jupiter_strength in ['exalted', 'own_sign']:
        cancellations.append({
            "type": "Strong Jupiter Protection",
            "description": f"Strong Jupiter ({jupiter_strength}) in {jupiter_house}th house (Kendra)",
            "effect": "Protection against Arishta",
            "strength": "Strong"
        })
    elif venus_house in [1, 4, 7, 10] and venus_strength in ['exalted', 'own_sign']:
        cancellations.append({
            "type": "Strong Venus Protection",
            "description": f"Strong Venus ({venus_strength}) in {venus_house}th house (Kendra)",
            "effect": "Protection against Arishta",
            "strength": "Strong"
        })
    
    if lagna_lord_house in [1, 4, 5, 7, 9, 10, 11]:
        lord_strength = planet_strengths.get(lagna_lord, 'neutral')
        if lord_strength in ['exalted', 'own_sign']:
            cancellations.append({
                "type": "Very Strong Lagna Lord",
                "description": f"Lagna lord ({lagna_lord}) {lord_strength} in {lagna_lord_house}th house",
                "effect": "Strong protection from health issues",
                "strength": "Very Strong"
            })
        else:
            cancellations.append({
                "type": "Well-placed Lagna Lord",
                "description": f"Lagna lord ({lagna_lord}) in {lagna_lord_house}th house",
                "effect": "Protection from serious health issues",
                "strength": "Strong"
            })
    
    if moon_sun_distance > 165:
        cancellations.append({
            "type": "Bright Moon Protection",
            "description": f"Full Moon (bright and strong) - {moon_sun_distance:.1f}° from Sun",
            "effect": "Cancels Moon-related Arishta",
            "strength": "Medium"
        })
    
    if moon_strength in ['exalted', 'own_sign']:
        cancellations.append({
            "type": "Strong Moon Protection",
            "description": f"Moon {moon_strength} in {moon_sign}",
            "effect": "Powerful protection against Arishta",
            "strength": "Very Strong"
        })
    
    adhi_yoga_houses = [6, 7, 8]
    benefics_in_adhi = []
    for house in adhi_yoga_houses:
        for benefic in ['Mercury', 'Jupiter', 'Venus']:
            if planet_houses.get(benefic) == house:
                benefics_in_adhi.append(f"{benefic} in {house}th")
    if len(benefics_in_adhi) >= 2:
        cancellations.append({
            "type": "Adhi Yoga Protection",
            "description": f"Benefics around Lagna: {', '.join(benefics_in_adhi)}",
            "effect": "Creates protective influence around ascendant",
            "strength": "Strong"
        })
    
    neecha_bhanga_planets = []
    for planet, strength in planet_strengths.items():
        if strength == 'debilitated':
            planet_house = planet_houses.get(planet)
            if planet_house in [1, 4, 7, 10]:
                neecha_bhanga_planets.append(planet)
    if neecha_bhanga_planets:
        cancellations.append({
            "type": "Neecha Bhanga Protection",
            "description": f"Debilitated planet(s) in Kendra: {', '.join(neecha_bhanga_planets)}",
            "effect": "Cancels debilitation effects",
            "strength": "Medium"
        })
    
    benefics_with_moon = []
    for planet in ['Jupiter', 'Venus', 'Mercury']:
        if planet_houses.get(planet) == moon_house:
            benefics_with_moon.append(planet)
    if benefics_with_moon:
        cancellations.append({
            "type": "Benefic Support to Moon",
            "description": f"Benefics with Moon: {', '.join(benefics_with_moon)}",
            "effect": "Protects Moon from malefic influences",
            "strength": "Medium"
        })
    
    kendra_lords = []
    trikona_lords = []
    for house_num in [1, 4, 7, 10]:
        lord = get_house_lord(house_num, asc_sign_index)
        if lord in planet_houses:
            kendra_lords.append(lord)
    for house_num in [1, 5, 9]:
        lord = get_house_lord(house_num, asc_sign_index)
        if lord in planet_houses:
            trikona_lords.append(lord)
    raj_yoga_combinations = []
    for k_lord in kendra_lords:
        for t_lord in trikona_lords:
            if k_lord != t_lord and planet_houses.get(k_lord) == planet_houses.get(t_lord):
                raj_yoga_combinations.append(f"{k_lord}-{t_lord}")
    if raj_yoga_combinations:
        cancellations.append({
            "type": "Raj Yoga Protection",
            "description": f"Kendra-Trikona lord combinations: {', '.join(raj_yoga_combinations)}",
            "effect": "Raj Yoga provides overall life protection",
            "strength": "Very Strong"
        })
    
    return arishta_combinations, cancellations


def rareYogas(birth_data):
    """
    Perform the exact same calculations as the original script's /yoga-analysis endpoint
    and return the response dict (no changes to logic).
    """
    # Input validation identical to original
    required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in birth_data for key in required):
        raise ValueError("Missing required parameters")

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
    planetary_positions = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planetary_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu
    rahu_lon = planetary_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planetary_positions['Ketu'] = (ketu_lon, '')

    # Ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Houses
    planet_houses = {}
    for planet_name, (lon, _) in planetary_positions.items():
        house = get_house(lon, asc_sign_index)
        planet_houses[planet_name] = house

    # Strengths
    planet_signs = {}
    planet_strengths = {}
    for planet_name, (lon, _) in planetary_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        planet_signs[planet_name] = sign
        if planet_name != 'Ketu':
            planet_strengths[planet_name] = get_planet_strength(planet_name, sign)

    # Format positions
    planetary_positions_formatted = {}
    for planet_name, (lon, retro) in planetary_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = planet_houses[planet_name]
        strength = planet_strengths.get(planet_name, 'neutral')
        planetary_positions_formatted[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "longitude": lon,
            "strength": strength
        }

    # Analyze yogas
    nabhas_yogas = analyze_nabhas_yogas(planet_houses, planetary_positions)
    indra_yogas = analyze_indra_yoga(planet_houses, asc_sign_index, planetary_positions)
    arishta_yogas, arishta_cancellations = analyze_arishta_yogas(planet_houses, asc_sign_index, planetary_positions)

    # Overall arishta assessment
    high_severity_count = len([a for a in arishta_yogas if a["severity"] in ["Very High", "High"]])
    medium_severity_count = len([a for a in arishta_yogas if a["severity"] == "Medium"])
    strong_cancellation_count = len([c for c in arishta_cancellations if c["strength"] in ["Very Strong", "Strong"]])
    medium_cancellation_count = len([c for c in arishta_cancellations if c["strength"] == "Medium"])
    arishta_score = (high_severity_count * 2 + medium_severity_count) - (strong_cancellation_count * 2 + medium_cancellation_count)
    if arishta_score <= -3:
        arishta_status = "Excellently Protected"
    elif arishta_score <= -1:
        arishta_status = "Well Protected"
    elif arishta_score <= 1:
        arishta_status = "Protected"
    elif arishta_score <= 3:
        arishta_status = "Some Concerns"
    else:
        arishta_status = "Requires Attention"

    yoga_counts = {
        "Asraya": len([y for y in nabhas_yogas if y["type"] == "Asraya Yoga"]),
        "Sankhya": len([y for y in nabhas_yogas if y["type"] == "Sankhya Yoga"]),
        "Akriti": len([y for y in nabhas_yogas if y["type"] == "Akriti Yoga"]),
        "Dala": len([y for y in nabhas_yogas if y["type"] == "Dala Yoga"])
    }
    dominant_type = max(yoga_counts, key=yoga_counts.get) if any(yoga_counts.values()) else "None"

    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "chart_info": {
            "ascendant_sign": asc_sign,
            "ascendant_degree": format_dms(ascendant_lon % 30),
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}°",
            "house_system": "Whole Sign",
            "lagna_lord": sign_rulers[asc_sign],
            "lagna_lord_strength": planet_strengths.get(sign_rulers[asc_sign], 'neutral')
        },
        "planetary_positions": planetary_positions_formatted,
        "yoga_analysis": {
            "nabhas_yogas": {
                "total_count": len(nabhas_yogas),
                "yogas": nabhas_yogas,
                "distribution": {
                    "asraya_yogas": yoga_counts["Asraya"],
                    "sankhya_yogas": yoga_counts["Sankhya"], 
                    "akriti_yogas": yoga_counts["Akriti"],
                    "dala_yogas": yoga_counts["Dala"]
                },
                "note": "Based on classical BPHS rules - effects felt throughout lifetime"
            },
            "indra_yogas": {
                "count": len(indra_yogas),
                "yogas": indra_yogas,
                "disclaimer": "Indra Yoga is NOT found in classical BPHS texts. Modern interpretation only."
            },
            "arishta_analysis": {
                "arishta_combinations": {
                    "count": len(arishta_yogas),
                    "combinations": arishta_yogas,
                    "severity_breakdown": {
                        "very_high": len([a for a in arishta_yogas if a["severity"] == "Very High"]),
                        "high": len([a for a in arishta_yogas if a["severity"] == "High"]),
                        "medium": len([a for a in arishta_yogas if a["severity"] == "Medium"])
                    }
                },
                "arishta_cancellations": {
                    "count": len(arishta_cancellations),
                    "cancellations": arishta_cancellations,
                    "strength_breakdown": {
                        "very_strong": len([c for c in arishta_cancellations if c["strength"] == "Very Strong"]),
                        "strong": len([c for c in arishta_cancellations if c["strength"] == "Strong"]),
                        "medium": len([c for c in arishta_cancellations if c["strength"] == "Medium"])
                    }
                },
                "overall_assessment": {
                    "status": arishta_status,
                    "arishta_score": arishta_score,
                    "explanation": "Weighted score: High severity +2, Medium +1, Strong protection -2, Medium protection -1"
                }
            }
        },
        "summary": {
            "total_nabhas_yogas": len(nabhas_yogas),
            "dominant_nabhas_type": dominant_type,
            "indra_yoga_present": len(indra_yogas) > 0,
            "arishta_protection_level": arishta_status,
            "major_strengths": [y["name"] for y in nabhas_yogas if y["type"] in ["Asraya Yoga", "Akriti Yoga"]],
            "areas_of_concern": [a["type"] for a in arishta_yogas if a["severity"] in ["High", "Very High"]],
            "protective_factors": [c["type"] for c in arishta_cancellations if c["strength"] in ["Strong", "Very Strong"]],
            "moon_strength": planet_strengths.get('Moon', 'neutral'),
            "lagna_lord_placement": f"{sign_rulers[asc_sign]} in {planet_houses.get(sign_rulers[asc_sign])}th house"
        },
        "classical_notes": {
            "nabhas_source": "Brihat Parashara Hora Shastra (BPHS) - Chapter 35",
            "arishta_source": "Classical texts including BPHS, Saravali, and Phaladeepika",
            "calculation_method": "Sidereal zodiac with Lahiri Ayanamsa, Whole Sign houses",
            "traditional_planets": "Sun through Saturn (7 planets) for Nabhas yogas",
            "strength_assessment": "Based on exaltation, own sign, debilitation in sidereal zodiac"
        }
    }

    return response
