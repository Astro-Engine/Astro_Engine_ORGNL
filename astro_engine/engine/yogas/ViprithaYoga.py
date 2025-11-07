# vipritha_yogas_calculations.py

import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (ensure ephemeris files are present)
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Planetary rulership mapping
sign_rulers = {
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

# Exaltation and debilitation signs
exaltation_signs = {
    'Sun': 0,       # Aries
    'Moon': 1,      # Taurus
    'Mars': 9,      # Capricorn
    'Mercury': 5,   # Virgo
    'Jupiter': 3,   # Cancer
    'Venus': 11,    # Pisces
    'Saturn': 6     # Libra
}

debilitation_signs = {
    'Sun': 6,       # Libra
    'Moon': 7,      # Scorpio
    'Mars': 3,      # Cancer
    'Mercury': 11,  # Pisces
    'Jupiter': 9,   # Capricorn
    'Venus': 5,     # Virgo
    'Saturn': 0     # Aries
}

def get_house(lon, asc_sign_index, orientation_shift=0):
    """
    Calculate house number based on planet longitude and ascendant sign index for Whole Sign system.

    Parameters:
    - lon: Planet's longitude (0–360°)
    - asc_sign_index: Ascendant's sign index (0–11, Aries–Pisces)
    - orientation_shift: Shift in house numbering (default 0 for standard Whole Sign)

    Returns:
    - House number (1–12)
    """
    sign_index = int(lon // 30) % 12  # Planet's sign index
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12  # Adjusted house index
    return house_index + 1  # 1-based house number

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

def get_house_lords(asc_sign_index):
    """Calculate house lords based on ascendant sign."""
    house_lords = {}
    for house_num in range(1, 13):
        sign_index = (asc_sign_index + house_num - 1) % 12
        house_lords[house_num] = sign_rulers[sign_index]
    return house_lords

def get_planet_sign_index(planet_positions, planet_name):
    """Get the sign index where a planet is placed."""
    if planet_name in planet_positions:
        lon = planet_positions[planet_name][0]
        return int(lon // 30) % 12
    return None

def is_planet_exalted(planet_name, sign_index):
    """Check if planet is exalted in given sign."""
    return planet_name in exaltation_signs and exaltation_signs[planet_name] == sign_index

def is_planet_debilitated(planet_name, sign_index):
    """Check if planet is debilitated in given sign."""
    return planet_name in debilitation_signs and debilitation_signs[planet_name] == sign_index

def is_planet_in_own_sign(planet_name, sign_index):
    """Check if planet is in its own sign."""
    for sign_idx, ruler in sign_rulers.items():
        if ruler == planet_name and sign_idx == sign_index:
            return True
    return False

def check_kendra_trikona_lordship(planet_name, house_lords):
    """Check if a planet also rules kendra (1,4,7,10) or trikona (1,5,9) houses."""
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]

    additional_lordships = []
    for house_num, lord in house_lords.items():
        if lord == planet_name and house_num != 6 and house_num != 8 and house_num != 12:
            if house_num in kendra_houses:
                additional_lordships.append(f"Kendra lord ({house_num}th house)")
            if house_num in trikona_houses:
                additional_lordships.append(f"Trikona lord ({house_num}th house)")

    return additional_lordships

def check_viparitha_raja_yoga(planet_positions, planet_houses, house_lords, asc_sign_index):
    """
    Check for Viparitha Raja Yoga formation based on classical rules.

    Classical Exception: Dusthana lord in its own house does NOT form the yoga.
    - Harsha: 6th lord in 8th or 12th house only (NOT in 6th house)
    - Sarala: 8th lord in 6th or 12th house only (NOT in 8th house)  
    - Vimala: 12th lord in 6th or 8th house only (NOT in 12th house)

    Returns detailed analysis of each yoga type.
    """
    yogas_found = []
    yoga_analysis = {
        "harsha_yoga": {"present": False, "details": {}},
        "sarala_yoga": {"present": False, "details": {}},
        "vimala_yoga": {"present": False, "details": {}}
    }

    # Get lords of dusthana houses (6th, 8th, 12th)
    sixth_lord = house_lords[6]
    eighth_lord = house_lords[8]
    twelfth_lord = house_lords[12]

    # Find where each dusthana lord is placed
    sixth_lord_house = planet_houses.get(sixth_lord, 0)
    eighth_lord_house = planet_houses.get(eighth_lord, 0)
    twelfth_lord_house = planet_houses.get(twelfth_lord, 0)

    # Get sign placements for strength analysis
    sixth_lord_sign_index = get_planet_sign_index(planet_positions, sixth_lord)
    eighth_lord_sign_index = get_planet_sign_index(planet_positions, eighth_lord)
    twelfth_lord_sign_index = get_planet_sign_index(planet_positions, twelfth_lord)

    # Check HARSHA YOGA (6th lord in 8th or 12th house - CLASSICAL RULE: NOT in 6th house)
    if sixth_lord_house in [8, 12]:  # Excluding 6th house as per classical exception
        strength_factors = []
        cancellation_factors = []

        if is_planet_in_own_sign(sixth_lord, sixth_lord_sign_index):
            strength_factors.append("Own sign placement")
        if is_planet_exalted(sixth_lord, sixth_lord_sign_index):
            strength_factors.append("Exalted")
        if is_planet_debilitated(sixth_lord, sixth_lord_sign_index):
            strength_factors.append("Debilitated (significantly weakens yoga)")

        additional_lordships = check_kendra_trikona_lordship(sixth_lord, house_lords)
        if additional_lordships:
            cancellation_factors.extend(additional_lordships)

        yoga_analysis["harsha_yoga"] = {
            "present": True,
            "details": {
                "lord": sixth_lord,
                "lord_house": sixth_lord_house,
                "lord_sign": signs[sixth_lord_sign_index] if sixth_lord_sign_index is not None else "Unknown",
                "formation_type": "6th lord in 8th house" if sixth_lord_house == 8 else "6th lord in 12th house",
                "strength_factors": strength_factors,
                "modifying_factors": cancellation_factors,
                "classical_reference": "Phala Deepika 6.63",
                "results": "Victory over enemies, good health, courage, ability to overcome obstacles, competitive advantage"
            }
        }
        yogas_found.append("Harsha Yoga")

    # Check SARALA YOGA (8th lord in 6th or 12th house - CLASSICAL RULE: NOT in 8th house)
    if eighth_lord_house in [6, 12]:
        strength_factors = []
        cancellation_factors = []

        if is_planet_in_own_sign(eighth_lord, eighth_lord_sign_index):
            strength_factors.append("Own sign placement")
        if is_planet_exalted(eighth_lord, eighth_lord_sign_index):
            strength_factors.append("Exalted")
        if is_planet_debilitated(eighth_lord, eighth_lord_sign_index):
            strength_factors.append("Debilitated (significantly weakens yoga)")

        additional_lordships = check_kendra_trikona_lordship(eighth_lord, house_lords)
        if additional_lordships:
            cancellation_factors.extend(additional_lordships)

        yoga_analysis["sarala_yoga"] = {
            "present": True,
            "details": {
                "lord": eighth_lord,
                "lord_house": eighth_lord_house,
                "lord_sign": signs[eighth_lord_sign_index] if eighth_lord_sign_index is not None else "Unknown",
                "formation_type": "8th lord in 6th house" if eighth_lord_house == 6 else "8th lord in 12th house",
                "strength_factors": strength_factors,
                "modifying_factors": cancellation_factors,
                "classical_reference": "Phala Deepika 6.65",
                "results": "Longevity, fearlessness, learning, spiritual inclination, research abilities, transformation through crisis"
            }
        }
        yogas_found.append("Sarala Yoga")

    # Check VIMALA YOGA (12th lord in 6th or 8th house - CLASSICAL RULE: NOT in 12th house)
    if twelfth_lord_house in [6, 8]:
        strength_factors = []
        cancellation_factors = []

        if is_planet_in_own_sign(twelfth_lord, twelfth_lord_sign_index):
            strength_factors.append("Own sign placement")
        if is_planet_exalted(twelfth_lord, twelfth_lord_sign_index):
            strength_factors.append("Exalted")
        if is_planet_debilitated(twelfth_lord, twelfth_lord_sign_index):
            strength_factors.append("Debilitated (significantly weakens yoga)")

        additional_lordships = check_kendra_trikona_lordship(twelfth_lord, house_lords)
        if additional_lordships:
            cancellation_factors.extend(additional_lordships)

        yoga_analysis["vimala_yoga"] = {
            "present": True,
            "details": {
                "lord": twelfth_lord,
                "lord_house": twelfth_lord_house,
                "lord_sign": signs[twelfth_lord_sign_index] if twelfth_lord_sign_index is not None else "Unknown",
                "formation_type": "12th lord in 6th house" if twelfth_lord_house == 6 else "12th lord in 8th house",
                "strength_factors": strength_factors,
                "modifying_factors": cancellation_factors,
                "classical_reference": "Classical texts on Vimala Yoga",
                "results": "Independence, ethical conduct, charitable nature, financial gains through own efforts, spiritual growth"
            }
        }
        yogas_found.append("Vimala Yoga")

    return yogas_found, yoga_analysis

def add_ViprithaYogas(birth_data):
    """
    Entry point for Viparitha Raja Yoga calculations.
    Accepts the same payload as the API and returns the response dict (NOT jsonified).
    """
    if not birth_data:
        raise ValueError("No JSON data provided")

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

    # Planetary positions
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

    # Calculate Ketu as 180° opposite Rahu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Ascendant and houses (Whole Sign system)
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Calculate house lords
    house_lords = get_house_lords(asc_sign_index)

    # Get orientation shift from input, default to 0 for standard Whole Sign
    orientation_shift = int(birth_data.get('orientation_shift', 0))
    planet_houses = {planet: get_house(lon, asc_sign_index, orientation_shift=orientation_shift)
                     for planet, (lon, _) in planet_positions.items()}

    # Calculate Viparitha Raja Yogas
    yogas_found, yoga_analysis = check_viparitha_raja_yoga(
        planet_positions, planet_houses, house_lords, asc_sign_index
    )

    # Format planetary positions for output
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = planet_houses[planet_name]
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house
        }

    # House lordship information
    house_lordship = {f"House {i}": lord for i, lord in house_lords.items()}

    # Dusthana houses analysis
    dusthana_analysis = {
        "6th_house": {
            "lord": house_lords[6],
            "lord_placed_in_house": planet_houses.get(house_lords[6], "Not found"),
            "lord_sign": signs[get_planet_sign_index(planet_positions, house_lords[6])] if get_planet_sign_index(planet_positions, house_lords[6]) is not None else "Unknown",
            "significance": "Enemies, diseases, debts, service, competition"
        },
        "8th_house": {
            "lord": house_lords[8],
            "lord_placed_in_house": planet_houses.get(house_lords[8], "Not found"),
            "lord_sign": signs[get_planet_sign_index(planet_positions, house_lords[8])] if get_planet_sign_index(planet_positions, house_lords[8]) is not None else "Unknown",
            "significance": "Longevity, transformation, occult, inheritance, research"
        },
        "12th_house": {
            "lord": house_lords[12],
            "lord_placed_in_house": planet_houses.get(house_lords[12], "Not found"),
            "lord_sign": signs[get_planet_sign_index(planet_positions, house_lords[12])] if get_planet_sign_index(planet_positions, house_lords[12]) is not None else "Unknown",
            "significance": "Losses, expenses, foreign lands, moksha, spirituality"
        }
    }

    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_time.strftime('%H:%M:%S'),
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "ascendant": {
            "sign": asc_sign,
            "degrees": format_dms(ascendant_lon % 30)
        },
        "house_lordship": house_lordship,
        "dusthana_analysis": dusthana_analysis,
        "viparitha_raja_yogas": {
            "total_yogas_found": len(yogas_found),
            "yoga_names": yogas_found,
            "detailed_analysis": yoga_analysis,
            "classical_rules": {
                "harsha_yoga": "6th lord in 8th or 12th house (NOT in 6th house)",
                "sarala_yoga": "8th lord in 6th or 12th house (NOT in 8th house)",
                "vimala_yoga": "12th lord in 6th or 8th house (NOT in 12th house)",
                "exception_rule": "Dusthana lord in its own house does NOT form the yoga"
            }
        },
        "planetary_positions": planetary_positions_json,
        "calculation_notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}",
            "house_system": "Whole Sign",
            "yoga_principle": "Dusthana lords in other dusthana houses create positive results through struggle",
            "classical_reference": "Based on Phala Deepika and traditional Vedic astrology texts",
            "important_note": "Results manifest after overcoming initial challenges and difficulties"
        }
    }

    return response
