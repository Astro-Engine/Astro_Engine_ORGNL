import swisseph as swe
import math

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

kala_sarpa_types = {
    1: "Ananta", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal", 
    5: "Padma", 6: "Maha Padma", 7: "Takshak", 8: "Karkotak",
    9: "Shankhachoodh", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag"
}

# Exaltation data with exact degrees
exaltation_data = {
    'Sun': {'sign': 0, 'degree': 10},      # 10° Aries
    'Moon': {'sign': 1, 'degree': 3},      # 3° Taurus
    'Mercury': {'sign': 5, 'degree': 15},  # 15° Virgo
    'Venus': {'sign': 11, 'degree': 27},   # 27° Pisces
    'Mars': {'sign': 9, 'degree': 28},     # 28° Capricorn
    'Jupiter': {'sign': 3, 'degree': 5},   # 5° Cancer
    'Saturn': {'sign': 6, 'degree': 20},   # 20° Libra
}

def kala_sarpa_yoga_normalize_longitude(lon):
    """Normalize longitude to 0-360 range."""
    while lon < 0:
        lon += 360
    while lon >= 360:
        lon -= 360
    return lon

def kala_sarpa_yoga_get_house_whole_sign(lon, asc_sign_index):
    """
    CONSISTENT HOUSE CALCULATION - Whole Sign system
    This function MUST be used everywhere for house calculations.
    """
    planet_sign_index = int(kala_sarpa_yoga_normalize_longitude(lon) // 30)
    house_number = ((planet_sign_index - asc_sign_index) % 12) + 1
    return house_number

def kala_sarpa_yoga_longitude_to_sign_data(deg):
    """Convert longitude to comprehensive sign data."""
    deg = kala_sarpa_yoga_normalize_longitude(deg)
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return {
        'sign': sign,
        'sign_index': sign_index,
        'degree_in_sign': sign_deg,
        'total_longitude': deg
    }

def kala_sarpa_yoga_format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def kala_sarpa_yoga_verify_rahu_ketu_opposition(rahu_lon, ketu_lon, tolerance=1.0):
    """
    RULE 1: Verify Rahu and Ketu are in exact opposition (180° ± tolerance).
    This is the foundation rule - without proper opposition, no valid Kala Sarpa Yoga.
    """
    rahu_lon = kala_sarpa_yoga_normalize_longitude(rahu_lon)
    ketu_lon = kala_sarpa_yoga_normalize_longitude(ketu_lon)
    
    expected_ketu = kala_sarpa_yoga_normalize_longitude(rahu_lon + 180)
    difference = abs(expected_ketu - ketu_lon)
    if difference > 180:
        difference = 360 - difference
    
    return {
        'is_exact_opposition': difference <= tolerance,
        'difference_degrees': difference,
        'rahu_longitude': rahu_lon,
        'expected_ketu': expected_ketu,
        'actual_ketu': ketu_lon,
        'tolerance_used': tolerance
    }

def kala_sarpa_yoga_calculate_circular_arc_distance(start_lon, end_lon):
    """
    Calculate shortest circular arc distance between two longitudes.
    Handles 0°/360° boundary properly.
    """
    start_lon = kala_sarpa_yoga_normalize_longitude(start_lon)
    end_lon = kala_sarpa_yoga_normalize_longitude(end_lon)
    
    direct_distance = abs(end_lon - start_lon)
    circular_distance = 360 - direct_distance
    
    return min(direct_distance, circular_distance)

def kala_sarpa_yoga_is_planet_between_rahu_ketu_circular(planet_lon, rahu_lon, ketu_lon):
    """
    RULE 2: PRECISE CIRCULAR ZODIAC LOGIC
    Determine if planet is between Rahu and Ketu considering circular nature.
    Uses proper arc calculations, not simple comparison.
    """
    planet_lon = kala_sarpa_yoga_normalize_longitude(planet_lon)
    rahu_lon = kala_sarpa_yoga_normalize_longitude(rahu_lon)
    ketu_lon = kala_sarpa_yoga_normalize_longitude(ketu_lon)
    
    # Calculate arcs in both directions
    # Method: Check if going from Rahu → Planet → Ketu is shorter than Rahu → Ketu directly
    
    # Arc from Rahu to Ketu (should be ~180°)
    if rahu_lon <= ketu_lon:
        rahu_ketu_arc = ketu_lon - rahu_lon
    else:
        rahu_ketu_arc = (360 - rahu_lon) + ketu_lon
    
    # Arc from Rahu to Planet
    if rahu_lon <= planet_lon:
        rahu_planet_arc = planet_lon - rahu_lon
    else:
        rahu_planet_arc = (360 - rahu_lon) + planet_lon
    
    # Planet is between Rahu and Ketu if Rahu→Planet arc < Rahu→Ketu arc
    between_rahu_ketu = rahu_planet_arc < rahu_ketu_arc
    between_ketu_rahu = not between_rahu_ketu
    
    return {
        'between_rahu_ketu': between_rahu_ketu,
        'between_ketu_rahu': between_ketu_rahu,
        'rahu_planet_arc': rahu_planet_arc,
        'rahu_ketu_arc': rahu_ketu_arc,
        'planet_longitude': planet_lon
    }

def kala_sarpa_yoga_check_house_conjunction_cancellation(planet_lon, rahu_lon, ketu_lon, asc_sign_index):
    """
    RULE 3: HOUSE CONJUNCTION CANCELLATION RULE
    If planet is in same house as Rahu or Ketu, it cancels the entire yoga.
    This rule has highest priority.
    """
    planet_house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index)
    rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
    ketu_house = kala_sarpa_yoga_get_house_whole_sign(ketu_lon, asc_sign_index)
    
    conjunct_rahu = (planet_house == rahu_house)
    conjunct_ketu = (planet_house == ketu_house)
    cancels_yoga = conjunct_rahu or conjunct_ketu
    
    conjunct_with = "None"
    if conjunct_rahu:
        conjunct_with = "Rahu"
    elif conjunct_ketu:
        conjunct_with = "Ketu"
    
    return {
        'cancels_yoga': cancels_yoga,
        'conjunct_rahu': conjunct_rahu,
        'conjunct_ketu': conjunct_ketu,
        'conjunct_with': conjunct_with,
        'planet_house': planet_house,
        'rahu_house': rahu_house,
        'ketu_house': ketu_house
    }

def kala_sarpa_yoga_check_degree_precision_rule(planet_lon, rahu_lon, ketu_lon, asc_sign_index):
    """
    RULE 4: DEGREE PRECISION WITHIN SAME HOUSE
    When planet and node are in same house, node's degree must be greater than planet's degree.
    """
    planet_house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index)
    rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
    ketu_house = kala_sarpa_yoga_get_house_whole_sign(ketu_lon, asc_sign_index)
    
    planet_deg_in_sign = planet_lon % 30
    rahu_deg_in_sign = rahu_lon % 30
    ketu_deg_in_sign = ketu_lon % 30
    
    degree_violation = False
    violation_details = ""
    
    if planet_house == rahu_house:
        if rahu_deg_in_sign <= planet_deg_in_sign:
            degree_violation = True
            violation_details = f"Planet {planet_deg_in_sign:.2f}° ≥ Rahu {rahu_deg_in_sign:.2f}° in house {planet_house}"
    
    if planet_house == ketu_house:
        if ketu_deg_in_sign <= planet_deg_in_sign:
            degree_violation = True
            violation_details = f"Planet {planet_deg_in_sign:.2f}° ≥ Ketu {ketu_deg_in_sign:.2f}° in house {planet_house}"
    
    return {
        'degree_violation': degree_violation,
        'violation_details': violation_details,
        'planet_degree_in_sign': planet_deg_in_sign,
        'rahu_degree_in_sign': rahu_deg_in_sign,
        'ketu_degree_in_sign': ketu_deg_in_sign,
        'same_house_as_node': (planet_house == rahu_house) or (planet_house == ketu_house)
    }

def kala_sarpa_yoga_analyze_continuous_chain_requirement(planet_positions, rahu_lon, ketu_lon, asc_sign_index):
    """
    RULE 5: CONTINUOUS CHAIN REQUIREMENT
    All houses between Rahu and Ketu must be continuously occupied by planets.
    No gaps should exist in the sequence.
    """
    rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
    ketu_house = kala_sarpa_yoga_get_house_whole_sign(ketu_lon, asc_sign_index)
    
    # Determine house sequence from Rahu to Ketu
    if rahu_house < ketu_house:
        house_sequence = list(range(rahu_house, ketu_house + 1))
    else:
        house_sequence = list(range(rahu_house, 13)) + list(range(1, ketu_house + 1))
    
    # Find which houses are occupied by planets (excluding Rahu/Ketu)
    occupied_houses = set()
    for planet_name, (planet_lon, _) in planet_positions.items():
        if planet_name not in ['Rahu', 'Ketu']:
            house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index)
            occupied_houses.add(house)
    
    # Check for gaps in the sequence (excluding Rahu and Ketu houses themselves)
    intermediate_houses = house_sequence[1:-1]  # Remove first (Rahu) and last (Ketu)
    gaps = [house for house in intermediate_houses if house not in occupied_houses]
    
    return {
        'continuous_chain': len(gaps) == 0,
        'gaps_in_sequence': gaps,
        'house_sequence': house_sequence,
        'intermediate_houses': intermediate_houses,
        'occupied_intermediate_houses': [h for h in intermediate_houses if h in occupied_houses]
    }

def kala_sarpa_yoga_verify_five_consecutive_empty_houses(planet_positions, asc_sign_index):
    """
    RULE 6: FIVE CONSECUTIVE EMPTY HOUSES RULE
    In valid Kala Sarpa Yoga, exactly 5 consecutive houses should be empty.
    This is a mathematical verification rule.
    """
    house_occupancy = [False] * 12
    
    # Mark houses as occupied
    for planet_name, (planet_lon, _) in planet_positions.items():
        house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index) - 1  # Convert to 0-based
        house_occupancy[house] = True
    
    # Ascendant always occupies 1st house
    house_occupancy[0] = True
    
    # Find maximum consecutive empty houses (checking circular)
    max_consecutive_empty = 0
    current_consecutive = 0
    
    # Check twice around the circle to handle wraparound
    for i in range(24):
        house_index = i % 12
        if not house_occupancy[house_index]:
            current_consecutive += 1
            max_consecutive_empty = max(max_consecutive_empty, current_consecutive)
        else:
            current_consecutive = 0
    
    return {
        'has_five_consecutive_empty': max_consecutive_empty >= 5,
        'max_consecutive_empty_houses': max_consecutive_empty,
        'occupied_houses': [i + 1 for i, occupied in enumerate(house_occupancy) if occupied],
        'empty_houses': [i + 1 for i, occupied in enumerate(house_occupancy) if not occupied],
        'total_empty_houses': sum(1 for occupied in house_occupancy if not occupied)
    }

def kala_sarpa_yoga_check_comprehensive_cancellations(planet_positions, ascendant_lon, asc_sign_index, yoga_present):
    """
    RULE 7: COMPREHENSIVE CANCELLATION (YOGA BHANGA) ANALYSIS
    Check all known cancellation factors that can nullify Kala Sarpa Yoga.
    """
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = planet_positions['Ketu'][0]
    
    cancellations = {
        'ascendant_outside_axis': False,
        'b_v_raman_neutralization': False,
        'planets_in_truth_houses': [],
        'exalted_planets': [],
        'nodes_in_trikona': {'rahu': False, 'ketu': False},
        'house_conjunction_cancellation': [],
        'total_cancellation_score': 0
    }
    
    # Check if ascendant is outside Rahu-Ketu axis
    asc_arc_analysis = kala_sarpa_yoga_is_planet_between_rahu_ketu_circular(ascendant_lon, rahu_lon, ketu_lon)
    cancellations['ascendant_outside_axis'] = not (asc_arc_analysis['between_rahu_ketu'] or asc_arc_analysis['between_ketu_rahu'])
    
    # B.V. Raman's rule: Ascendant outside axis while planets hemmed neutralizes yoga
    cancellations['b_v_raman_neutralization'] = cancellations['ascendant_outside_axis'] and yoga_present
    
    # Check planets in truth houses (1st and 7th from ascendant)
    for planet_name, (planet_lon, _) in planet_positions.items():
        if planet_name in ['Rahu', 'Ketu']:
            continue
        
        planet_house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index)
        if planet_house in [1, 7]:
            cancellations['planets_in_truth_houses'].append({
                'planet': planet_name,
                'house': planet_house
            })
    
    # Check for exalted planets
    for planet_name, (planet_lon, _) in planet_positions.items():
        if planet_name in ['Rahu', 'Ketu']:
            continue
        
        planet_sign = int(planet_lon // 30)
        planet_deg_in_sign = planet_lon % 30
        
        if planet_name in exaltation_data:
            exalt_sign = exaltation_data[planet_name]['sign']
            exalt_degree = exaltation_data[planet_name]['degree']
            
            if planet_sign == exalt_sign:
                degree_diff = abs(planet_deg_in_sign - exalt_degree)
                if degree_diff <= 2:  # Within 2° of exact exaltation
                    cancellations['exalted_planets'].append({
                        'planet': planet_name,
                        'exaltation_closeness': degree_diff
                    })
    
    # Check if nodes are in trikona houses (1, 5, 9)
    rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
    ketu_house = kala_sarpa_yoga_get_house_whole_sign(ketu_lon, asc_sign_index)
    
    cancellations['nodes_in_trikona']['rahu'] = rahu_house in [1, 5, 9]
    cancellations['nodes_in_trikona']['ketu'] = ketu_house in [1, 5, 9]
    
    # Check house conjunction cancellations
    for planet_name, (planet_lon, _) in planet_positions.items():
        if planet_name in ['Rahu', 'Ketu']:
            continue
        
        conjunction_check = kala_sarpa_yoga_check_house_conjunction_cancellation(planet_lon, rahu_lon, ketu_lon, asc_sign_index)
        if conjunction_check['cancels_yoga']:
            cancellations['house_conjunction_cancellation'].append({
                'planet': planet_name,
                'conjunct_with': conjunction_check['conjunct_with'],
                'house': conjunction_check['planet_house']
            })
    
    # Calculate total cancellation score
    score = 0
    if cancellations['b_v_raman_neutralization']:
        score += 3  # Strongest cancellation
    if cancellations['ascendant_outside_axis']:
        score += 2
    if len(cancellations['house_conjunction_cancellation']) > 0:
        score += 2
    if len(cancellations['exalted_planets']) > 0:
        score += 1
    if len(cancellations['planets_in_truth_houses']) > 0:
        score += 1
    if cancellations['nodes_in_trikona']['rahu'] or cancellations['nodes_in_trikona']['ketu']:
        score += 1
    
    cancellations['total_cancellation_score'] = score
    
    return cancellations

def kala_sarpa_yoga_comprehensive_analysis(planet_positions, ascendant_lon, asc_sign_index):
    """
    MASTER ANALYSIS FUNCTION
    Applies all Kala Sarpa Yoga rules with mathematical precision and consistent logic.
    """
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = planet_positions['Ketu'][0]
    main_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    
    # Initialize comprehensive results
    analysis_result = {
        'opposition_verification': kala_sarpa_yoga_verify_rahu_ketu_opposition(rahu_lon, ketu_lon),
        'rule_analysis': {
            'house_conjunction_rule': {
                'yoga_present': False,
                'planets_between_rahu_ketu': [],
                'cancellation_planets': [],
                'description': 'Planet in same house as Rahu/Ketu cancels entire yoga'
            },
            'degree_precision_rule': {
                'yoga_present': False,
                'planets_valid': [],
                'degree_violations': [],
                'description': 'Within same house, node degrees must exceed planet degrees'
            },
            'rahu_ketu_arc_rule': {
                'yoga_present': False,
                'planets_between': [],
                'planets_outside': [],
                'description': 'All planets between Rahu→Ketu arc (materialistic tendency)'
            },
            'ketu_rahu_arc_rule': {
                'yoga_present': False,
                'planets_between': [],
                'planets_outside': [],
                'description': 'All planets between Ketu→Rahu arc (spiritual tendency)'
            }
        },
        'individual_planet_analysis': {},
        'structural_analysis': {},
        'cancellation_analysis': {},
        'final_assessment': {}
    }
    
    # Analyze each planet individually with CONSISTENT house calculations
    for planet_name in main_planets:
        planet_lon = planet_positions[planet_name][0]
        
        # Use consistent house calculation throughout
        planet_house = kala_sarpa_yoga_get_house_whole_sign(planet_lon, asc_sign_index)
        rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
        ketu_house = kala_sarpa_yoga_get_house_whole_sign(ketu_lon, asc_sign_index)
        
        # Arc analysis
        arc_analysis = kala_sarpa_yoga_is_planet_between_rahu_ketu_circular(planet_lon, rahu_lon, ketu_lon)
        
        # House conjunction analysis
        house_conjunction = kala_sarpa_yoga_check_house_conjunction_cancellation(planet_lon, rahu_lon, ketu_lon, asc_sign_index)
        
        # Degree precision analysis
        degree_precision = kala_sarpa_yoga_check_degree_precision_rule(planet_lon, rahu_lon, ketu_lon, asc_sign_index)
        
        # Store individual analysis
        analysis_result['individual_planet_analysis'][planet_name] = {
            'longitude': planet_lon,
            'house': planet_house,
            'arc_analysis': arc_analysis,
            'house_conjunction': house_conjunction,
            'degree_precision': degree_precision
        }
        
        # Populate rule analysis
        # House conjunction rule
        if house_conjunction['cancels_yoga']:
            analysis_result['rule_analysis']['house_conjunction_rule']['cancellation_planets'].append(planet_name)
        elif arc_analysis['between_rahu_ketu']:
            analysis_result['rule_analysis']['house_conjunction_rule']['planets_between_rahu_ketu'].append(planet_name)
        
        # Degree precision rule
        if degree_precision['degree_violation']:
            analysis_result['rule_analysis']['degree_precision_rule']['degree_violations'].append(planet_name)
        elif arc_analysis['between_rahu_ketu'] and not house_conjunction['cancels_yoga']:
            analysis_result['rule_analysis']['degree_precision_rule']['planets_valid'].append(planet_name)
        
        # Arc-based rules
        if arc_analysis['between_rahu_ketu']:
            analysis_result['rule_analysis']['rahu_ketu_arc_rule']['planets_between'].append(planet_name)
        else:
            analysis_result['rule_analysis']['rahu_ketu_arc_rule']['planets_outside'].append(planet_name)
        
        if arc_analysis['between_ketu_rahu']:
            analysis_result['rule_analysis']['ketu_rahu_arc_rule']['planets_between'].append(planet_name)
        else:
            analysis_result['rule_analysis']['ketu_rahu_arc_rule']['planets_outside'].append(planet_name)
    
    # Determine yoga presence for each rule
    total_planets = len(main_planets)
    
    # House conjunction rule: No cancellation planets AND all others between Rahu-Ketu
    house_rule = analysis_result['rule_analysis']['house_conjunction_rule']
    house_rule['yoga_present'] = (len(house_rule['cancellation_planets']) == 0 and 
                                  len(house_rule['planets_between_rahu_ketu']) == total_planets)
    
    # Degree precision rule: No violations AND all valid planets between nodes
    degree_rule = analysis_result['rule_analysis']['degree_precision_rule']
    degree_rule['yoga_present'] = (len(degree_rule['degree_violations']) == 0 and 
                                   len(degree_rule['planets_valid']) == total_planets)
    
    # Arc rules: All planets on one side
    rahu_arc_rule = analysis_result['rule_analysis']['rahu_ketu_arc_rule']
    rahu_arc_rule['yoga_present'] = len(rahu_arc_rule['planets_outside']) == 0
    
    ketu_arc_rule = analysis_result['rule_analysis']['ketu_rahu_arc_rule']
    ketu_arc_rule['yoga_present'] = len(ketu_arc_rule['planets_outside']) == 0
    
    # Structural analysis
    analysis_result['structural_analysis'] = {
        'continuous_chain': kala_sarpa_yoga_analyze_continuous_chain_requirement(planet_positions, rahu_lon, ketu_lon, asc_sign_index),
        'five_consecutive_empty': kala_sarpa_yoga_verify_five_consecutive_empty_houses(planet_positions, asc_sign_index)
    }
    
    # Check if any yoga is present
    any_yoga_present = any(rule['yoga_present'] for rule in analysis_result['rule_analysis'].values())
    
    # Cancellation analysis
    analysis_result['cancellation_analysis'] = kala_sarpa_yoga_check_comprehensive_cancellations(
        planet_positions, ascendant_lon, asc_sign_index, any_yoga_present
    )
    
    # Final assessment
    analysis_result['final_assessment'] = kala_sarpa_yoga_generate_final_assessment(analysis_result, rahu_lon, asc_sign_index)
    
    return analysis_result

def kala_sarpa_yoga_generate_final_assessment(analysis_result, rahu_lon, asc_sign_index):
    """Generate comprehensive final assessment."""
    # Count rules satisfied
    rules_satisfied = sum(1 for rule in analysis_result['rule_analysis'].values() if rule['yoga_present'])
    total_rules = len(analysis_result['rule_analysis'])
    
    # Opposition validity
    opposition_valid = analysis_result['opposition_verification']['is_exact_opposition']
    
    # Cancellation strength
    cancellation_score = analysis_result['cancellation_analysis']['total_cancellation_score']
    
    # Determine yoga type
    rahu_house = kala_sarpa_yoga_get_house_whole_sign(rahu_lon, asc_sign_index)
    yoga_type = kala_sarpa_types.get(rahu_house, "Unknown")
    
    # Determine variant
    rahu_arc_yoga = analysis_result['rule_analysis']['rahu_ketu_arc_rule']['yoga_present']
    ketu_arc_yoga = analysis_result['rule_analysis']['ketu_rahu_arc_rule']['yoga_present']
    
    if rahu_arc_yoga and not ketu_arc_yoga:
        variant = "Kala Sarpa Yoga (Rahu-headed - Materialistic tendency)"
    elif ketu_arc_yoga and not rahu_arc_yoga:
        variant = "Kala Amrita Yoga (Ketu-headed - Spiritual tendency)"
    elif rahu_arc_yoga and ketu_arc_yoga:
        variant = "Impossible formation - manual verification needed"
    else:
        variant = "No clear directional formation"
    
    # Determine classification
    if not opposition_valid:
        classification = "Invalid - Rahu/Ketu not in proper opposition"
        strength = "None"
    elif rules_satisfied == 0:
        classification = "No Kala Sarpa Yoga present"
        strength = "None"
    elif cancellation_score >= 3:
        classification = "Kala Sarpa Yoga present but neutralized by strong cancellations"
        strength = "Neutralized"
    elif rules_satisfied == total_rules:
        classification = "Complete Kala Sarpa Yoga - All rules satisfied"
        strength = "Very Strong" if cancellation_score == 0 else "Strong"
    elif rules_satisfied >= 3:
        classification = "Strong Kala Sarpa Yoga - Most rules satisfied"
        strength = "Strong" if cancellation_score <= 1 else "Moderate"
    elif rules_satisfied >= 2:
        classification = "Partial Kala Sarpa Yoga - Some rules satisfied"
        strength = "Moderate" if cancellation_score <= 1 else "Weak"
    else:
        classification = "Weak Kala Sarpa indication"
        strength = "Weak"
    
    # Generate recommendation
    if strength in ["None", "Neutralized"]:
        recommendation = "No Kala Sarpa Yoga remedies needed. Focus on other chart factors."
    elif strength in ["Very Strong", "Strong"]:
        recommendation = "Strong Kala Sarpa Yoga present. Consider traditional remedies and spiritual practices."
    else:
        recommendation = "Partial Kala Sarpa formation. Light remedial measures may be beneficial."
    
    return {
        'yoga_classification': classification,
        'strength': strength,
        'yoga_type': yoga_type,
        'variant': variant,
        'rules_satisfied': f"{rules_satisfied}/{total_rules}",
        'opposition_valid': opposition_valid,
        'cancellation_score': cancellation_score,
        'recommendation': recommendation
    }

def kala_sarpa_yoga_calculate_planetary_positions(jd_ut):
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
        
        lon = kala_sarpa_yoga_normalize_longitude(pos[0])
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu as exact 180° opposite Rahu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = kala_sarpa_yoga_normalize_longitude(rahu_lon + 180)
    planet_positions['Ketu'] = (ketu_lon, '')
    
    return planet_positions, None

def kala_sarpa_yoga_calculate_ascendant(jd_ut, latitude, longitude):
    """Calculate Ascendant position."""
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = kala_sarpa_yoga_normalize_longitude(ascmc[0])
    asc_sign_data = kala_sarpa_yoga_longitude_to_sign_data(ascendant_lon)
    asc_sign_index = asc_sign_data['sign_index']
    return ascendant_lon, asc_sign_data, asc_sign_index

def kala_sarpa_yoga_format_planetary_positions(planet_positions, asc_sign_index):
    """Format planetary positions for JSON output."""
    formatted_positions = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign_data = kala_sarpa_yoga_longitude_to_sign_data(lon)
        house = kala_sarpa_yoga_get_house_whole_sign(lon, asc_sign_index)
        
        formatted_positions[planet_name] = {
            "longitude": f"{lon:.6f}°",
            "sign": sign_data['sign'],
            "degree_in_sign": f"{sign_data['degree_in_sign']:.6f}°",
            "formatted_degree": kala_sarpa_yoga_format_dms(sign_data['degree_in_sign']),
            "house": house,
            "retrograde": retro,
            "sign_index": sign_data['sign_index']
        }
    return formatted_positions