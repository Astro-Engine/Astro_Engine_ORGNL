import swisseph as swe

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def pitra_dosha_get_house(lon, asc_sign_index, orientation_shift=0):
    """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def pitra_dosha_longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def pitra_dosha_format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def pitra_dosha_is_conjunction(lon1, lon2, orb=8):
    """Check if two planets are in conjunction within given orb."""
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb

def pitra_dosha_get_planet_lord(sign_index):
    """Get the ruling planet of a sign."""
    lords = {
        0: 'Mars',      # Aries
        1: 'Venus',     # Taurus  
        2: 'Mercury',   # Gemini
        3: 'Moon',      # Cancer
        4: 'Sun',       # Leo
        5: 'Mercury',   # Virgo
        6: 'Venus',     # Libra
        7: 'Mars',      # Scorpio
        8: 'Jupiter',   # Sagittarius
        9: 'Saturn',    # Capricorn
        10: 'Saturn',   # Aquarius
        11: 'Jupiter'   # Pisces
    }
    return lords.get(sign_index, 'Unknown')

def pitra_dosha_get_aspected_houses(planet, house):
    """Get houses aspected by a planet from its house position."""
    aspected_houses = []
    
    if planet == 'Saturn':
        # Saturn aspects 3rd, 7th, and 10th houses from its position
        third_house = ((house - 1 + 2) % 12) + 1
        seventh_house = ((house - 1 + 6) % 12) + 1  
        tenth_house = ((house - 1 + 9) % 12) + 1
        aspected_houses = [third_house, seventh_house, tenth_house]
        
    elif planet == 'Mars':
        # Mars aspects 4th, 7th, and 8th houses from its position
        fourth_house = ((house - 1 + 3) % 12) + 1
        seventh_house = ((house - 1 + 6) % 12) + 1
        eighth_house = ((house - 1 + 7) % 12) + 1
        aspected_houses = [fourth_house, seventh_house, eighth_house]
        
    elif planet == 'Jupiter':
        # Jupiter aspects 5th, 7th, and 9th houses from its position
        fifth_house = ((house - 1 + 4) % 12) + 1
        seventh_house = ((house - 1 + 6) % 12) + 1
        ninth_house = ((house - 1 + 8) % 12) + 1
        aspected_houses = [fifth_house, seventh_house, ninth_house]
        
    elif planet in ['Rahu', 'Ketu']:
        # Rahu and Ketu aspect 5th, 7th, and 9th houses from their position
        fifth_house = ((house - 1 + 4) % 12) + 1
        seventh_house = ((house - 1 + 6) % 12) + 1
        ninth_house = ((house - 1 + 8) % 12) + 1
        aspected_houses = [fifth_house, seventh_house, ninth_house]
    else:
        # Other planets only have 7th house aspect
        seventh_house = ((house - 1 + 6) % 12) + 1
        aspected_houses = [seventh_house]
    
    return aspected_houses

def pitra_dosha_check_planetary_strength(planet, planet_positions, planet_houses):
    """Check planetary strength for cancellation purposes."""
    if planet not in planet_positions:
        return 'Unknown'
    
    lon = planet_positions[planet][0]
    sign_index = int(lon // 30) % 12
    house = planet_houses[planet]
    
    # Exaltation signs
    exaltation_signs = {
        'Sun': 0,      # Aries
        'Moon': 1,     # Taurus
        'Mars': 9,     # Capricorn
        'Mercury': 5,  # Virgo
        'Jupiter': 3,  # Cancer
        'Venus': 11,   # Pisces
        'Saturn': 6    # Libra
    }
    
    # Own signs
    own_signs = {
        'Sun': [4],           # Leo
        'Moon': [3],          # Cancer
        'Mars': [0, 7],       # Aries, Scorpio
        'Mercury': [2, 5],    # Gemini, Virgo
        'Jupiter': [8, 11],   # Sagittarius, Pisces
        'Venus': [1, 6],      # Taurus, Libra
        'Saturn': [9, 10]     # Capricorn, Aquarius
    }
    
    # Check strength
    if planet in exaltation_signs and sign_index == exaltation_signs[planet]:
        return 'Exalted'
    elif planet in own_signs and sign_index in own_signs[planet]:
        return 'Own_Sign'
    elif house in [1, 4, 7, 10]:  # Kendra houses
        return 'Kendra_Strong'
    elif house in [5, 9]:  # Trikona houses
        return 'Trikona_Strong'
    else:
        return 'Normal'

def pitra_dosha_check_benefic_yogas(planet_positions, planet_houses, asc_sign_index):
    """Check for major benefic yogas that can mitigate Pitra Dosha."""
    benefic_yogas = []
    
    # Gajakesari Yoga: Moon and Jupiter in Kendras from each other
    moon_house = planet_houses.get('Moon', 0)
    jupiter_house = planet_houses.get('Jupiter', 0)
    
    if moon_house and jupiter_house:
        house_diff = abs(moon_house - jupiter_house)
        if house_diff in [0, 3, 6, 9]:  # Same house or 4th, 7th, 10th from each other
            benefic_yogas.append({
                "name": "Gajakesari Yoga",
                "description": "Moon and Jupiter in mutual Kendras - provides divine protection",
                "strength": "High"
            })
    
    # Hamsa Yoga: Jupiter in Kendra in own/exaltation sign
    jupiter_strength = pitra_dosha_check_planetary_strength('Jupiter', planet_positions, planet_houses)
    if jupiter_house in [1, 4, 7, 10] and jupiter_strength in ['Exalted', 'Own_Sign']:
        benefic_yogas.append({
            "name": "Hamsa Yoga (Pancha Mahapurusha)",
            "description": "Jupiter strong in Kendra - spiritual protection and wisdom",
            "strength": "Very High"
        })
    
    # Malavya Yoga: Venus in Kendra in own/exaltation sign
    venus_house = planet_houses.get('Venus', 0)
    venus_strength = pitra_dosha_check_planetary_strength('Venus', planet_positions, planet_houses)
    if venus_house in [1, 4, 7, 10] and venus_strength in ['Exalted', 'Own_Sign']:
        benefic_yogas.append({
            "name": "Malavya Yoga (Pancha Mahapurusha)",
            "description": "Venus strong in Kendra - material comforts and family harmony",
            "strength": "High"
        })
    
    # Chandra-Mangal Yoga: Moon and Mars conjunction (wealth yoga)
    moon_lon = planet_positions.get('Moon', [0])[0]
    mars_lon = planet_positions.get('Mars', [0])[0]
    if pitra_dosha_is_conjunction(moon_lon, mars_lon, orb=8):
        benefic_yogas.append({
            "name": "Chandra-Mangal Yoga",
            "description": "Moon-Mars conjunction - wealth and prosperity",
            "strength": "Medium"
        })
    
    return benefic_yogas

def pitra_dosha_check_parivartana_yoga(planet_positions, planet_houses, asc_sign_index, ninth_lord):
    """
    Check for classical Parivartana Yoga (planetary exchange) involving 9th house/lord.
    
    Classical Rules:
    1. Two different planets must exchange signs (mutual reception)
    2. At least one planet should be 9th lord OR occupy 9th house
    3. Both planets should benefit from the exchange
    4. Creates karmic resolution for ancestral matters
    """
    
    parivartana_yogas = []
    
    # Get all planets except nodes for exchange analysis
    main_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    ninth_house_sign_index = (asc_sign_index + 8) % 12
    
    # Check all possible planet pairs for exchange
    for i, planet1 in enumerate(main_planets):
        if planet1 not in planet_positions:
            continue
            
        for j, planet2 in enumerate(main_planets[i+1:], i+1):
            if planet2 not in planet_positions:
                continue
            
            # Get sign positions
            planet1_sign_index = int(planet_positions[planet1][0] // 30) % 12
            planet2_sign_index = int(planet_positions[planet2][0] // 30) % 12
            
            # Get sign rulers
            planet1_sign_lord = pitra_dosha_get_planet_lord(planet1_sign_index)
            planet2_sign_lord = pitra_dosha_get_planet_lord(planet2_sign_index)
            
            # Check for mutual exchange (Parivartana)
            # Planet1 should be in planet2's sign AND planet2 should be in planet1's sign
            if planet1_sign_lord == planet2 and planet2_sign_lord == planet1:
                
                # Check if this exchange involves 9th house matters
                involves_ninth_house = False
                ninth_house_involvement = []
                
                # Check if either planet is 9th lord
                if planet1 == ninth_lord:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet1} is 9th lord")
                
                if planet2 == ninth_lord:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet2} is 9th lord")
                
                # Check if either planet occupies 9th house
                if planet_houses[planet1] == 9:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet1} occupies 9th house")
                
                if planet_houses[planet2] == 9:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet2} occupies 9th house")
                
                # Check if either planet's sign is 9th house sign
                if planet1_sign_index == ninth_house_sign_index:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet1} in 9th house sign")
                
                if planet2_sign_index == ninth_house_sign_index:
                    involves_ninth_house = True
                    ninth_house_involvement.append(f"{planet2} in 9th house sign")
                
                # Only consider Parivartana if it involves 9th house matters
                if involves_ninth_house:
                    
                    # Assess the strength of the exchange
                    planet1_strength = pitra_dosha_check_planetary_strength(planet1, planet_positions, planet_houses)
                    planet2_strength = pitra_dosha_check_planetary_strength(planet2, planet_positions, planet_houses)
                    
                    # Determine yoga strength based on planetary strengths
                    if planet1_strength in ['Exalted', 'Own_Sign'] or planet2_strength in ['Exalted', 'Own_Sign']:
                        yoga_strength = "Very High"
                        reduction = 5
                    elif planet1_strength in ['Kendra_Strong', 'Trikona_Strong'] or planet2_strength in ['Kendra_Strong', 'Trikona_Strong']:
                        yoga_strength = "High"
                        reduction = 4
                    else:
                        yoga_strength = "Medium"
                        reduction = 3
                    
                    parivartana_yogas.append({
                        "planet1": planet1,
                        "planet2": planet2,
                        "planet1_sign": signs[planet1_sign_index],
                        "planet2_sign": signs[planet2_sign_index],
                        "planet1_house": planet_houses[planet1],
                        "planet2_house": planet_houses[planet2],
                        "ninth_house_connection": ninth_house_involvement,
                        "strength": yoga_strength,
                        "severity_reduction": reduction,
                        "description": f"Parivartana yoga: {planet1} in {signs[planet1_sign_index]} (lord {planet2}) exchanges with {planet2} in {signs[planet2_sign_index]} (lord {planet1}) - {', '.join(ninth_house_involvement)}"
                    })
    
    return parivartana_yogas

def pitra_dosha_analyze_cancellations(planet_positions, planet_houses, asc_sign_index, pitra_indicators, ninth_lord):
    """Analyze classical Pitra Dosha cancellation and mitigation factors."""
    
    cancellations = []
    severity_reduction = 0
    
    # 1. Jupiter's Benefic Aspects (Most Important Cancellation)
    jupiter_house = planet_houses.get('Jupiter', 0)
    if jupiter_house:
        jupiter_aspects = pitra_dosha_get_aspected_houses('Jupiter', jupiter_house)
        jupiter_strength = pitra_dosha_check_planetary_strength('Jupiter', planet_positions, planet_houses)
        
        # Check if Jupiter aspects any afflicted houses
        afflicted_houses = set()
        for indicator in pitra_indicators:
            if indicator.get('house'):
                afflicted_houses.add(indicator['house'])
        
        aspected_afflicted = afflicted_houses.intersection(set(jupiter_aspects))
        
        if aspected_afflicted:
            cancellation_strength = "Medium"
            reduction = 3
            
            if jupiter_strength in ['Exalted', 'Own_Sign']:
                cancellation_strength = "High"
                reduction = 5
            elif jupiter_strength in ['Kendra_Strong', 'Trikona_Strong']:
                cancellation_strength = "Medium-High"
                reduction = 4
            
            cancellations.append({
                "type": "Jupiter Aspect Cancellation",
                "description": f"Jupiter ({jupiter_strength}) from House {jupiter_house} aspects afflicted houses: {list(aspected_afflicted)}",
                "strength": cancellation_strength,
                "houses_protected": list(aspected_afflicted),
                "severity_reduction": reduction
            })
            severity_reduction += reduction
    
    # 2. Strong 9th Lord (Direct Cancellation)
    if ninth_lord in planet_positions:
        ninth_lord_strength = pitra_dosha_check_planetary_strength(ninth_lord, planet_positions, planet_houses)
        ninth_lord_house = planet_houses[ninth_lord]
        
        if ninth_lord_strength in ['Exalted', 'Own_Sign']:
            reduction = 4
            cancellations.append({
                "type": "Strong 9th Lord",
                "description": f"9th lord {ninth_lord} is {ninth_lord_strength} in House {ninth_lord_house} - mitigates ancestral karma",
                "strength": "High",
                "severity_reduction": reduction
            })
            severity_reduction += reduction
            
        elif ninth_lord_strength in ['Kendra_Strong', 'Trikona_Strong']:
            reduction = 2
            cancellations.append({
                "type": "Well-Placed 9th Lord",
                "description": f"9th lord {ninth_lord} is {ninth_lord_strength} - provides partial protection",
                "strength": "Medium",
                "severity_reduction": reduction
            })
            severity_reduction += reduction
    
    # 3. Venus in 9th House (Special Case - Mixed Results)
    venus_house = planet_houses.get('Venus', 0)
    if venus_house == 9:
        venus_strength = pitra_dosha_check_planetary_strength('Venus', planet_positions, planet_houses)
        cancellations.append({
            "type": "Venus in 9th House",
            "description": f"Venus ({venus_strength}) in 9th house - material prosperity but spiritual obligations remain",
            "strength": "Partial",
            "effect": "Mixed - material gains, spiritual complications",
            "severity_reduction": 1
        })
        severity_reduction += 1
    
    # 4. Strong Sun in Own Sign/Exaltation (Partial Protection)
    sun_house = planet_houses.get('Sun', 0)
    sun_strength = pitra_dosha_check_planetary_strength('Sun', planet_positions, planet_houses)
    
    if sun_strength in ['Exalted', 'Own_Sign']:
        # Check if Sun is involved in Pitra Dosha
        sun_involved = any('Sun' in indicator.get('description', '') for indicator in pitra_indicators)
        
        if sun_involved:
            reduction = 2
            cancellations.append({
                "type": "Strong Sun Protection",
                "description": f"Sun is {sun_strength} - father's soul strength provides partial protection",
                "strength": "Medium",
                "severity_reduction": reduction
            })
            severity_reduction += reduction
    
    # 5. Benefic Yogas Present
    benefic_yogas = pitra_dosha_check_benefic_yogas(planet_positions, planet_houses, asc_sign_index)
    
    if benefic_yogas:
        yoga_strength_total = 0
        high_strength_yogas = [y for y in benefic_yogas if y['strength'] in ['Very High', 'High']]
        medium_strength_yogas = [y for y in benefic_yogas if y['strength'] == 'Medium']
        
        if high_strength_yogas:
            yoga_strength_total += len(high_strength_yogas) * 2
        if medium_strength_yogas:
            yoga_strength_total += len(medium_strength_yogas) * 1
        
        if yoga_strength_total > 0:
            reduction = min(yoga_strength_total, 3)  # Cap at 3 points
            cancellations.append({
                "type": "Benefic Yogas",
                "description": f"Benefic yogas present: {[y['name'] for y in benefic_yogas]}",
                "yogas": benefic_yogas,
                "strength": "Variable",
                "severity_reduction": reduction
            })
            severity_reduction += reduction
    
    # 6. Full Moon Protection (Purnima-born)
    moon_lon = planet_positions.get('Moon', [0])[0] 
    sun_lon = planet_positions.get('Sun', [0])[0]
    moon_sun_distance = abs(moon_lon - sun_lon)
    if moon_sun_distance > 180:
        moon_sun_distance = 360 - moon_sun_distance
    
    if moon_sun_distance >= 170:  # Near Full Moon
        cancellations.append({
            "type": "Full Moon Birth",
            "description": "Born near Full Moon - natural spiritual protection and ancestral blessings",
            "strength": "Medium",
            "moon_sun_distance": round(moon_sun_distance, 2),
            "severity_reduction": 2
        })
        severity_reduction += 2
    
    # 7. CORRECTED Parivartana Yoga Involving 9th House/Lord
    parivartana_yogas = pitra_dosha_check_parivartana_yoga(planet_positions, planet_houses, asc_sign_index, ninth_lord)
    
    for parivar in parivartana_yogas:
        cancellations.append({
            "type": "Parivartana Yoga (Exchange)",
            "description": parivar["description"],
            "strength": parivar["strength"],
            "planet1": parivar["planet1"],
            "planet2": parivar["planet2"],
            "ninth_house_connection": parivar["ninth_house_connection"],
            "severity_reduction": parivar["severity_reduction"]
        })
        severity_reduction += parivar["severity_reduction"]
    
    return cancellations, severity_reduction

def pitra_dosha_analyze_combinations(planet_positions, planet_houses, asc_sign_index):
    """
    Analyze Pitra Dosha based on classical combinations and permutations with corrected cancellation rules.
    """
    
    pitra_dosha_indicators = []
    severity_score = 0
    
    # Basic planetary information
    sun_lon = planet_positions['Sun'][0]
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = planet_positions['Ketu'][0]
    sun_house = planet_houses['Sun']
    rahu_house = planet_houses['Rahu']
    ketu_house = planet_houses['Ketu']
    
    # Calculate 9th house and its lord
    ninth_house_sign_index = (asc_sign_index + 8) % 12
    ninth_house_sign = signs[ninth_house_sign_index]
    ninth_lord = pitra_dosha_get_planet_lord(ninth_house_sign_index)
    ninth_lord_house = planet_houses.get(ninth_lord, 0)
    ninth_lord_lon = planet_positions.get(ninth_lord, [0])[0] if ninth_lord in planet_positions else 0
    
    # =================================================================
    # PRIMARY COMBINATIONS (Most Severe)
    # =================================================================
    
    # Combination 1: Sun-Rahu conjunction (any house)
    if pitra_dosha_is_conjunction(sun_lon, rahu_lon, orb=8):
        orb_value = abs(sun_lon - rahu_lon) if abs(sun_lon - rahu_lon) <= 180 else 360 - abs(sun_lon - rahu_lon)
        
        # House-specific permutations
        if sun_house == 9:
            severity = "Extreme"
            score = 10
            description = f"Sun-Rahu conjunction in 9th house ({ninth_house_sign}) - Maximum Pitra Dosha"
        elif sun_house == 1:
            severity = "Very High"
            score = 8
            description = f"Sun-Rahu conjunction in 1st house - affects self and lineage"
        elif sun_house == 5:
            severity = "Very High" 
            score = 8
            description = f"Sun-Rahu conjunction in 5th house - affects children/progeny"
        elif sun_house == 10:
            severity = "Very High"
            score = 8
            description = f"Sun-Rahu conjunction in 10th house - affects father directly"
        else:
            severity = "High"
            score = 6
            description = f"Sun-Rahu conjunction in House {sun_house} - General Pitra Dosha"
            
        pitra_dosha_indicators.append({
            "rule": "Sun-Rahu Conjunction",
            "description": description,
            "severity": severity,
            "house": sun_house,
            "orb": round(orb_value, 2),
            "combination_type": "Primary"
        })
        severity_score += score
    
    # Combination 2: Sun-Ketu conjunction (any house)
    if pitra_dosha_is_conjunction(sun_lon, ketu_lon, orb=8):
        orb_value = abs(sun_lon - ketu_lon) if abs(sun_lon - ketu_lon) <= 180 else 360 - abs(sun_lon - ketu_lon)
        
        # House-specific permutations
        if sun_house == 9:
            severity = "Extreme"
            score = 10
            description = f"Sun-Ketu conjunction in 9th house ({ninth_house_sign}) - Maximum Pitra Dosha"
        elif sun_house == 1:
            severity = "Very High"
            score = 8
            description = f"Sun-Ketu conjunction in 1st house - affects self and lineage"
        elif sun_house == 5:
            severity = "Very High"
            score = 8
            description = f"Sun-Ketu conjunction in 5th house - affects children/progeny"
        elif sun_house == 10:
            severity = "Very High"
            score = 8
            description = f"Sun-Ketu conjunction in 10th house - affects father directly"
        else:
            severity = "High"
            score = 6
            description = f"Sun-Ketu conjunction in House {sun_house} - General Pitra Dosha"
            
        pitra_dosha_indicators.append({
            "rule": "Sun-Ketu Conjunction",
            "description": description,
            "severity": severity,
            "house": sun_house,
            "orb": round(orb_value, 2),
            "combination_type": "Primary"
        })
        severity_score += score
    
    # Combination 3: Rahu in 9th house
    if rahu_house == 9:
        pitra_dosha_indicators.append({
            "rule": "Rahu in 9th House",
            "description": f"Rahu occupies 9th house ({ninth_house_sign}) - house of father and ancestors",
            "severity": "High",
            "house": 9,
            "combination_type": "Primary"
        })
        severity_score += 6
    
    # Combination 4: Ketu in 9th house  
    if ketu_house == 9:
        pitra_dosha_indicators.append({
            "rule": "Ketu in 9th House",
            "description": f"Ketu occupies 9th house ({ninth_house_sign}) - house of father and ancestors",
            "severity": "High", 
            "house": 9,
            "combination_type": "Primary"
        })
        severity_score += 6
    
    # =================================================================
    # SECONDARY COMBINATIONS (High Severity)
    # =================================================================
    
    # Combination 5: 9th lord with Rahu
    if ninth_lord in planet_positions and pitra_dosha_is_conjunction(ninth_lord_lon, rahu_lon, orb=8):
        orb_value = abs(ninth_lord_lon - rahu_lon) if abs(ninth_lord_lon - rahu_lon) <= 180 else 360 - abs(ninth_lord_lon - rahu_lon)
        
        # Special case: If 9th lord is Sun (Sagittarius ascendant)
        if ninth_lord == 'Sun':
            severity = "Extreme"
            score = 10
            description = f"9th lord Sun conjunct Rahu in House {ninth_lord_house} - Extreme Pitra Dosha"
        else:
            severity = "High"
            score = 6
            description = f"9th lord {ninth_lord} conjunct Rahu in House {ninth_lord_house}"
            
        pitra_dosha_indicators.append({
            "rule": "9th Lord with Rahu",
            "description": description,
            "severity": severity,
            "house": ninth_lord_house,
            "orb": round(orb_value, 2),
            "ninth_lord": ninth_lord,
            "combination_type": "Secondary"
        })
        severity_score += score
    
    # Combination 6: 9th lord with Ketu
    if ninth_lord in planet_positions and pitra_dosha_is_conjunction(ninth_lord_lon, ketu_lon, orb=8):
        orb_value = abs(ninth_lord_lon - ketu_lon) if abs(ninth_lord_lon - ketu_lon) <= 180 else 360 - abs(ninth_lord_lon - ketu_lon)
        
        # Special case: If 9th lord is Sun (Sagittarius ascendant)
        if ninth_lord == 'Sun':
            severity = "Extreme"
            score = 10
            description = f"9th lord Sun conjunct Ketu in House {ninth_lord_house} - Extreme Pitra Dosha"
        else:
            severity = "High"
            score = 6
            description = f"9th lord {ninth_lord} conjunct Ketu in House {ninth_lord_house}"
            
        pitra_dosha_indicators.append({
            "rule": "9th Lord with Ketu",
            "description": description,
            "severity": severity,
            "house": ninth_lord_house,
            "orb": round(orb_value, 2),
            "ninth_lord": ninth_lord,
            "combination_type": "Secondary"
        })
        severity_score += score
    
    # =================================================================
    # TERTIARY COMBINATIONS (Medium Severity - Aspects)
    # =================================================================
    
    # Combination 7-10: Malefic aspects on 9th house
    malefic_planets = ['Mars', 'Saturn', 'Rahu', 'Ketu']
    
    for planet in malefic_planets:
        if planet in planet_houses:
            planet_house = planet_houses[planet]
            aspected_houses = pitra_dosha_get_aspected_houses(planet, planet_house)
            
            if 9 in aspected_houses:
                pitra_dosha_indicators.append({
                    "rule": f"{planet} Aspect on 9th House",
                    "description": f"{planet} from House {planet_house} aspects 9th house ({ninth_house_sign})",
                    "severity": "Medium",
                    "house": 9,
                    "aspecting_from": planet_house,
                    "combination_type": "Tertiary"
                })
                severity_score += 3
    
    # Combination 11-14: Malefic aspects on 9th lord
    if ninth_lord in planet_positions:
        for planet in malefic_planets:
            if planet in planet_houses and planet != ninth_lord:
                planet_house = planet_houses[planet]
                aspected_houses = pitra_dosha_get_aspected_houses(planet, planet_house)
                
                if ninth_lord_house in aspected_houses:
                    pitra_dosha_indicators.append({
                        "rule": f"{planet} Aspect on 9th Lord",
                        "description": f"{planet} from House {planet_house} aspects 9th lord {ninth_lord} in House {ninth_lord_house}",
                        "severity": "Medium",
                        "house": ninth_lord_house,
                        "aspecting_from": planet_house,
                        "ninth_lord": ninth_lord,
                        "combination_type": "Tertiary"
                    })
                    severity_score += 3
    
    # =================================================================
    # SPECIAL COMBINATIONS
    # =================================================================
    
    # Papakatari Yoga on 9th house (9th house hemmed between malefics)
    eighth_house_planets = [planet for planet, house in planet_houses.items() if house == 8 and planet in malefic_planets]
    tenth_house_planets = [planet for planet, house in planet_houses.items() if house == 10 and planet in malefic_planets]
    
    if eighth_house_planets and tenth_house_planets:
        pitra_dosha_indicators.append({
            "rule": "Papakatari Yoga on 9th House",
            "description": f"9th house hemmed between malefics: {eighth_house_planets[0]} in 8th and {tenth_house_planets[0]} in 10th",
            "severity": "High",
            "house": 9,
            "combination_type": "Special"
        })
        severity_score += 5
    
    # Multiple malefics in 9th house
    planets_in_ninth = [planet for planet, house in planet_houses.items() if house == 9]
    malefics_in_ninth = [planet for planet in planets_in_ninth if planet in malefic_planets]
    
    if len(malefics_in_ninth) >= 2:
        pitra_dosha_indicators.append({
            "rule": "Multiple Malefics in 9th House",
            "description": f"Multiple malefics in 9th house: {', '.join(malefics_in_ninth)}",
            "severity": "High",
            "house": 9,
            "combination_type": "Special"
        })
        severity_score += 5
    
    # Sun in 9th with multiple malefics
    if sun_house == 9 and len([p for p in planets_in_ninth if p in malefic_planets]) >= 1:
        nodes_in_ninth = [p for p in planets_in_ninth if p in ['Rahu', 'Ketu']]
        if nodes_in_ninth:
            pitra_dosha_indicators.append({
                "rule": "Sun with Node in 9th House",
                "description": f"Sun in 9th house with {nodes_in_ninth[0]} - Creates intense Pitra Dosha",
                "severity": "Extreme",
                "house": 9,
                "combination_type": "Special"
            })
            severity_score += 8
    
    # =================================================================
    # CANCELLATION ANALYSIS
    # =================================================================
    
    # Analyze cancellations and get reduced severity
    cancellations, severity_reduction = pitra_dosha_analyze_cancellations(
        planet_positions, planet_houses, asc_sign_index, pitra_dosha_indicators, ninth_lord
    )
    
    # Apply severity reduction
    original_severity_score = severity_score
    final_severity_score = max(0, severity_score - severity_reduction)
    
    # =================================================================
    # FINAL SEVERITY CLASSIFICATION
    # =================================================================
    
    if final_severity_score >= 15:
        overall_severity = "Extreme"
    elif final_severity_score >= 10:
        overall_severity = "Very High"
    elif final_severity_score >= 6:
        overall_severity = "High"
    elif final_severity_score >= 3:
        overall_severity = "Medium"
    elif final_severity_score >= 1:
        overall_severity = "Low"
    else:
        overall_severity = "None"
    
    pitra_dosha_present = len(pitra_dosha_indicators) > 0
    
    # If significant cancellations exist, adjust the final determination
    if cancellations and final_severity_score <= 2:
        effective_pitra_dosha = False
        overall_severity = "Cancelled"
    else:
        effective_pitra_dosha = pitra_dosha_present
    
    return {
        "pitra_dosha_present": effective_pitra_dosha,
        "overall_severity": overall_severity,
        "original_severity_score": original_severity_score,
        "final_severity_score": final_severity_score,
        "severity_reduction": severity_reduction,
        "indicators": pitra_dosha_indicators,
        "total_indicators": len(pitra_dosha_indicators),
        "cancellation_factors": cancellations,
        "total_cancellations": len(cancellations),
        "ninth_house_details": {
            "house_number": 9,
            "sign": ninth_house_sign,
            "lord": ninth_lord,
            "lord_house": ninth_lord_house,
            "planets_in_ninth": [planet for planet, house in planet_houses.items() if house == 9]
        },
        "combination_summary": {
            "primary_combinations": len([i for i in pitra_dosha_indicators if i.get("combination_type") == "Primary"]),
            "secondary_combinations": len([i for i in pitra_dosha_indicators if i.get("combination_type") == "Secondary"]),
            "tertiary_combinations": len([i for i in pitra_dosha_indicators if i.get("combination_type") == "Tertiary"]),
            "special_combinations": len([i for i in pitra_dosha_indicators if i.get("combination_type") == "Special"])
        },
        "remedial_guidance": {
            "urgency": "High" if final_severity_score >= 6 else "Medium" if final_severity_score >= 3 else "Low",
            "primary_remedies": [
                "Perform Shraddha ceremonies during Pitru Paksha",
                "Feed Brahmins and poor on Amavasya days", 
                "Visit Gaya for Pinda Daan",
                "Recite Garuda Purana regularly",
                "Donate to charitable causes in father's name"
            ] if final_severity_score >= 3 else [
                "Basic ancestral worship on Amavasya",
                "Light lamp for ancestors weekly",
                "Charity to elderly people"
            ],
            "cancellation_enhanced": len(cancellations) > 0
        }
    }

def pitra_dosha_calculate_planetary_positions(jd_ut):
    """Calculate positions of all planets."""
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
            return None, f"Error calculating {planet_name}"
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu as 180° opposite Rahu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')
    
    return planet_positions, None

def pitra_dosha_calculate_ascendant(jd_ut, latitude, longitude):
    """Calculate Ascendant and houses."""
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]
    return ascendant_lon, asc_sign, asc_sign_index

def pitra_dosha_calculate_planet_houses(planet_positions, asc_sign_index):
    """Calculate planet houses."""
    planet_houses = {}
    for planet, (lon, _) in planet_positions.items():
        house = pitra_dosha_get_house(lon, asc_sign_index)
        planet_houses[planet] = house
    return planet_houses