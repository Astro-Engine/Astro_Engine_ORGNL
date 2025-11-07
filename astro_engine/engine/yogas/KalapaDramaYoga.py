import swisseph as swe

# Zodiac signs
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Sign lords mapping
sign_lords = {
    'Aries': 'Mars',
    'Taurus': 'Venus', 
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': 'Saturn',
    'Pisces': 'Jupiter'
}

# Exaltation signs
exaltation_signs = {
    'Sun': 'Aries',
    'Moon': 'Taurus',
    'Mars': 'Capricorn',
    'Mercury': 'Virgo',
    'Jupiter': 'Cancer',
    'Venus': 'Pisces',
    'Saturn': 'Libra',
    'Rahu': 'Gemini',
    'Ketu': 'Sagittarius'
}

def kalpadruma_yoga_get_house(lon, asc_sign_index):
    """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

def kalpadruma_yoga_longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def kalpadruma_yoga_format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def kalpadruma_yoga_get_dispositor(planet_sign):
    """Get the dispositor (sign lord) of a planet based on its sign."""
    return sign_lords.get(planet_sign)

def kalpadruma_yoga_is_kendra(house):
    """Check if house is a Kendra (angular house)."""
    return house in [1, 4, 7, 10]

def kalpadruma_yoga_is_trikona(house):
    """Check if house is a Trikona (trinal house)."""
    return house in [1, 5, 9]

def kalpadruma_yoga_is_exalted(planet, sign):
    """Check if planet is exalted in the given sign."""
    return exaltation_signs.get(planet) == sign

def kalpadruma_yoga_calculate_navamsa_positions(planet_positions, jd_ut):
    """Calculate Navamsa (D-9) positions for all planets."""
    navamsa_positions = {}
    
    for planet_name, (lon, retro) in planet_positions.items():
        # Navamsa calculation: Each sign is divided into 9 parts of 3°20' each
        sign_index = int(lon // 30)
        degree_in_sign = lon % 30
        navamsa_part = int(degree_in_sign // (30/9))  # 0 to 8
        
        # Navamsa sign calculation based on the rule
        if sign_index % 3 == 0:  # Cardinal signs (0, 3, 6, 9) - Aries, Cancer, Libra, Capricorn
            navamsa_sign_index = (sign_index + navamsa_part) % 12
        elif sign_index % 3 == 1:  # Fixed signs (1, 4, 7, 10) - Taurus, Leo, Scorpio, Aquarius
            navamsa_sign_index = (sign_index + 8 + navamsa_part) % 12
        else:  # Mutable signs (2, 5, 8, 11) - Gemini, Virgo, Sagittarius, Pisces
            navamsa_sign_index = (sign_index + 4 + navamsa_part) % 12
        
        navamsa_sign = signs[navamsa_sign_index]
        navamsa_positions[planet_name] = navamsa_sign
    
    return navamsa_positions

def calculate_kalpadruma_yoga(planet_positions, planet_houses, navamsa_positions, ascendant_sign):
    """
    Calculate Kalpadruma Yoga based on CORRECT BPHS rules.
    Returns detailed analysis of the yoga formation.
    """
    # Step 1: Get Ascendant Lord
    ascendant_lord = sign_lords[ascendant_sign]
    
    # Find ascendant lord's position
    asc_lord_sign = None
    asc_lord_house = None
    for planet, (lon, _) in planet_positions.items():
        if planet == ascendant_lord:
            asc_lord_sign, _ = kalpadruma_yoga_longitude_to_sign(lon)
            asc_lord_house = planet_houses[planet]
            break
    
    if not asc_lord_sign:
        return {"yoga_present": False, "error": "Ascendant lord not found"}
    
    # Step 2: Get Dispositor of Ascendant Lord
    dispositor_1 = kalpadruma_yoga_get_dispositor(asc_lord_sign)
    
    # Find first dispositor's position
    disp_1_sign = None
    disp_1_house = None
    for planet, (lon, _) in planet_positions.items():
        if planet == dispositor_1:
            disp_1_sign, _ = kalpadruma_yoga_longitude_to_sign(lon)
            disp_1_house = planet_houses[planet]
            break
    
    if not disp_1_sign:
        return {"yoga_present": False, "error": "First dispositor not found"}
    
    # Step 3: Get Dispositor of First Dispositor
    dispositor_2 = kalpadruma_yoga_get_dispositor(disp_1_sign)
    
    # Find second dispositor's position
    disp_2_sign = None
    disp_2_house = None
    for planet, (lon, _) in planet_positions.items():
        if planet == dispositor_2:
            disp_2_sign, _ = kalpadruma_yoga_longitude_to_sign(lon)
            disp_2_house = planet_houses[planet]
            break
    
    if not disp_2_sign:
        return {"yoga_present": False, "error": "Second dispositor not found"}
    
    # Step 4: Get Navamsa Dispositor of SECOND DISPOSITOR (CORRECTED)
    disp_2_navamsa_sign = navamsa_positions.get(dispositor_2)
    if not disp_2_navamsa_sign:
        return {"yoga_present": False, "error": "Navamsa position of second dispositor not found"}
    
    navamsa_dispositor = kalpadruma_yoga_get_dispositor(disp_2_navamsa_sign)
    
    # Find navamsa dispositor's position
    nav_disp_sign = None
    nav_disp_house = None
    for planet, (lon, _) in planet_positions.items():
        if planet == navamsa_dispositor:
            nav_disp_sign, _ = kalpadruma_yoga_longitude_to_sign(lon)
            nav_disp_house = planet_houses[planet]
            break
    
    if not nav_disp_sign:
        return {"yoga_present": False, "error": "Navamsa dispositor not found"}
    
    # Now check if all four planets are in Kendra, Trikona, or Exaltation
    yoga_planets = [
        {"planet": ascendant_lord, "sign": asc_lord_sign, "house": asc_lord_house, "role": "Ascendant Lord"},
        {"planet": dispositor_1, "sign": disp_1_sign, "house": disp_1_house, "role": f"Dispositor of {ascendant_lord}"},
        {"planet": dispositor_2, "sign": disp_2_sign, "house": disp_2_house, "role": f"Dispositor of {dispositor_1}"},
        {"planet": navamsa_dispositor, "sign": nav_disp_sign, "house": nav_disp_house, "role": f"Navamsa Dispositor of {dispositor_2}"}
    ]
    
    yoga_conditions = []
    yoga_present = True
    
    for planet_info in yoga_planets:
        planet = planet_info["planet"]
        sign = planet_info["sign"]
        house = planet_info["house"]
        role = planet_info["role"]
        
        # Check conditions
        in_kendra = kalpadruma_yoga_is_kendra(house)
        in_trikona = kalpadruma_yoga_is_trikona(house)
        in_exaltation = kalpadruma_yoga_is_exalted(planet, sign)
        
        condition_met = in_kendra or in_trikona or in_exaltation
        
        if not condition_met:
            yoga_present = False
        
        yoga_conditions.append({
            "planet": planet,
            "role": role,
            "sign": sign,
            "house": house,
            "in_kendra": in_kendra,
            "in_trikona": in_trikona,
            "in_exaltation": in_exaltation,
            "condition_met": condition_met
        })
    
    return {
        "yoga_present": yoga_present,
        "ascendant_lord": ascendant_lord,
        "dispositor_chain": {
            "step_1": f"{ascendant_lord} (Ascendant Lord)",
            "step_2": f"{dispositor_1} (Dispositor of {ascendant_lord})",
            "step_3": f"{dispositor_2} (Dispositor of {dispositor_1})",
            "step_4": f"{navamsa_dispositor} (Navamsa Dispositor of {dispositor_2})"
        },
        "navamsa_calculation": {
            "second_dispositor": dispositor_2,
            "navamsa_sign": disp_2_navamsa_sign,
            "navamsa_dispositor": navamsa_dispositor
        },
        "yoga_analysis": yoga_conditions,
        "summary": f"Kalpadruma Yoga is {'PRESENT' if yoga_present else 'NOT PRESENT'}"
    }

def kalpadruma_yoga_calculate_planetary_positions(jd_ut):
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

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')
    
    return planet_positions, None

def kalpadruma_yoga_calculate_ascendant(jd_ut, latitude, longitude):
    """Calculate Ascendant position."""
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    ascendant_sign = signs[asc_sign_index]
    return ascendant_lon, ascendant_sign, asc_sign_index

def kalpadruma_yoga_calculate_houses(planet_positions, asc_sign_index):
    """Calculate house positions for all planets."""
    planet_houses = {}
    for planet, (lon, _) in planet_positions.items():
        planet_houses[planet] = kalpadruma_yoga_get_house(lon, asc_sign_index)
    return planet_houses

def kalpadruma_yoga_format_planetary_positions(planet_positions, planet_houses, navamsa_positions):
    """Format planetary positions for JSON output."""
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg = kalpadruma_yoga_longitude_to_sign(lon)
        dms = kalpadruma_yoga_format_dms(sign_deg)
        house = planet_houses[planet_name]
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "navamsa_sign": navamsa_positions.get(planet_name, "N/A")
        }
    return planetary_positions_json