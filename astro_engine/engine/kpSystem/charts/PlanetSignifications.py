"""
KP Significators - Calculation Module v12.0 FINAL
=================================================
Krishnamurti Paddhati (KP) Astrology - Planet Significators Calculation

COMPLETE KP RULES:
==================

1. REGULAR PLANETS (Standard KP Hierarchy):
   - Level A: Planets in star of OCCUPANTS (Strongest)
   - Level B: Planets in star of OWNER  
   - Level C: Occupants of house
   - Level D: Owner (sign-lord)

2. PLANETS IN RAHU'S STAR:
   - If conjunction exists: Add houses whose CUSP is in Rahu's sign
   - If NO conjunction: Add Rahu's REPRESENTED planet's OWNERSHIP

3. PLANETS IN KETU'S STAR:
   - Add Ketu's OCCUPIED HOUSE only

4. CONJUNCTION RULE:
   - If planets conjunct with node (in node's star AND same sign):
     - Represented planet SKIPS Level B
     - Represented planet gains conjunct planets' significations

5. RAHU SIGNIFICATIONS:
   - If aspected by Mars/Jupiter/Saturn: 
     - Aspecting planet's OCCUPANCY + OWNERSHIP
     - Plus house(s) with cusp in Rahu's sign
   - If NOT aspected:
     - If planets in Rahu's star: Rahu's house + represented planet's OCCUPANCY
     - If NO planets in Rahu's star: Rahu's house + Ketu's house (axis)

6. KETU SIGNIFICATIONS:
   - Star lord's OWNERSHIP + OCCUPANCY
   - If planets in Ketu's star: + Ketu's OCCUPIED house
   - If NO planets in Ketu's star: + house(s) with cusp in Ketu's sign

NODE TYPE: True Node (Best Accuracy)
"""

import swisseph as swe
from datetime import datetime

# ==============================================================================
# CONSTANTS
# ==============================================================================

KP_NEW_OFFSET_ARCSEC = 50.2388475

NAKSHATRAS = [
    {"name": "Ashwini", "lord": "Ketu"}, {"name": "Bharani", "lord": "Venus"},
    {"name": "Krittika", "lord": "Sun"}, {"name": "Rohini", "lord": "Moon"},
    {"name": "Mrigashira", "lord": "Mars"}, {"name": "Ardra", "lord": "Rahu"},
    {"name": "Punarvasu", "lord": "Jupiter"}, {"name": "Pushya", "lord": "Saturn"},
    {"name": "Ashlesha", "lord": "Mercury"}, {"name": "Magha", "lord": "Ketu"},
    {"name": "Purva Phalguni", "lord": "Venus"}, {"name": "Uttara Phalguni", "lord": "Sun"},
    {"name": "Hasta", "lord": "Moon"}, {"name": "Chitra", "lord": "Mars"},
    {"name": "Swati", "lord": "Rahu"}, {"name": "Vishakha", "lord": "Jupiter"},
    {"name": "Anuradha", "lord": "Saturn"}, {"name": "Jyeshtha", "lord": "Mercury"},
    {"name": "Mula", "lord": "Ketu"}, {"name": "Purva Ashadha", "lord": "Venus"},
    {"name": "Uttara Ashadha", "lord": "Sun"}, {"name": "Shravana", "lord": "Moon"},
    {"name": "Dhanishta", "lord": "Mars"}, {"name": "Shatabhisha", "lord": "Rahu"},
    {"name": "Purva Bhadrapada", "lord": "Jupiter"}, {"name": "Uttara Bhadrapada", "lord": "Saturn"},
    {"name": "Revati", "lord": "Mercury"},
]

VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_TOTAL = 120

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

PLANET_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]
}

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

PLANET_CODES = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE  # TRUE NODE - Best accuracy with reference data
}

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
REGULAR_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def normalize_degree(degree):
    while degree < 0:
        degree += 360
    while degree >= 360:
        degree -= 360
    return degree


def get_sign_from_degree(degree):
    sign_num = int(degree / 30)
    return SIGNS[sign_num]


def get_nakshatra_details(sidereal_longitude):
    degree = normalize_degree(sidereal_longitude)
    nakshatra_span = 13.333333333333334
    nakshatra_index = int(degree / nakshatra_span)
    if nakshatra_index >= 27:
        nakshatra_index = 26
    nakshatra = NAKSHATRAS[nakshatra_index]
    return {"nakshatra": nakshatra["name"], "star_lord": nakshatra["lord"]}


def get_sub_lord(sidereal_longitude):
    degree = normalize_degree(sidereal_longitude)
    nakshatra_span = 13.333333333333334
    nakshatra_index = int(degree / nakshatra_span)
    if nakshatra_index >= 27:
        nakshatra_index = 26
    position_in_nakshatra = degree - (nakshatra_index * nakshatra_span)
    nakshatra_lord = NAKSHATRAS[nakshatra_index]["lord"]
    start_index = VIMSHOTTARI_ORDER.index(nakshatra_lord)
    accumulated = 0.0
    for i in range(9):
        planet_index = (start_index + i) % 9
        planet = VIMSHOTTARI_ORDER[planet_index]
        sub_span = (VIMSHOTTARI_YEARS[planet] / VIMSHOTTARI_TOTAL) * nakshatra_span
        if accumulated + sub_span > position_in_nakshatra:
            return planet
        accumulated += sub_span
    return nakshatra_lord


def datetime_to_jd(date_str, time_str, timezone_offset=5.5):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_hour = dt.hour + dt.minute / 60 + dt.second / 3600 - timezone_offset
    day, month, year = dt.day, dt.month, dt.year
    if utc_hour < 0:
        utc_hour += 24
        day -= 1
        if day < 1:
            month -= 1
            if month < 1:
                month, year = 12, year - 1
            day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
            if month == 2 and ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
                day = 29
    elif utc_hour >= 24:
        utc_hour -= 24
        day += 1
    return swe.julday(year, month, day, utc_hour)


def get_kp_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd) + (KP_NEW_OFFSET_ARCSEC / 3600)


# ==============================================================================
# CORE CALCULATION FUNCTIONS
# ==============================================================================

def calculate_planet_positions(jd, ayanamsa):
    planets_data = {}
    for planet_name, planet_code in PLANET_CODES.items():
        position, _ = swe.calc_ut(jd, planet_code)
        sidereal_longitude = normalize_degree(position[0] - ayanamsa)
        nak_details = get_nakshatra_details(sidereal_longitude)
        planets_data[planet_name] = {
            "longitude": round(sidereal_longitude, 6),
            "sign": get_sign_from_degree(sidereal_longitude),
            "nakshatra": nak_details["nakshatra"],
            "star_lord": nak_details["star_lord"],
            "sub_lord": get_sub_lord(sidereal_longitude)
        }
    
    ketu_longitude = normalize_degree(planets_data["Rahu"]["longitude"] + 180)
    nak_details = get_nakshatra_details(ketu_longitude)
    planets_data["Ketu"] = {
        "longitude": round(ketu_longitude, 6),
        "sign": get_sign_from_degree(ketu_longitude),
        "nakshatra": nak_details["nakshatra"],
        "star_lord": nak_details["star_lord"],
        "sub_lord": get_sub_lord(ketu_longitude)
    }
    return planets_data


def calculate_house_cusps(jd, latitude, longitude, ayanamsa):
    cusps, _ = swe.houses(jd, latitude, longitude, b'P')
    houses_data = {}
    for i in range(12):
        house_num = i + 1
        sidereal_cusp = normalize_degree(cusps[i] - ayanamsa)
        nak_details = get_nakshatra_details(sidereal_cusp)
        houses_data[house_num] = {
            "cusp_longitude": round(sidereal_cusp, 6),
            "sign": get_sign_from_degree(sidereal_cusp),
            "sign_lord": SIGN_LORDS[get_sign_from_degree(sidereal_cusp)],
            "nakshatra": nak_details["nakshatra"],
            "star_lord": nak_details["star_lord"],
            "sub_lord": get_sub_lord(sidereal_cusp)
        }
    return houses_data


def get_planet_house_positions(planets_data, houses_data):
    planet_houses = {}
    cusps = [(h, houses_data[h]["cusp_longitude"]) for h in range(1, 13)]
    
    for planet_name, planet_info in planets_data.items():
        planet_long = planet_info["longitude"]
        for i in range(12):
            current_house, current_cusp = cusps[i]
            next_cusp = cusps[(i + 1) % 12][1]
            
            if current_cusp > next_cusp:
                if planet_long >= current_cusp or planet_long < next_cusp:
                    planet_houses[planet_name] = current_house
                    break
            else:
                if current_cusp <= planet_long < next_cusp:
                    planet_houses[planet_name] = current_house
                    break
    return planet_houses


def get_house_occupants(planet_houses):
    house_occupants = {i: [] for i in range(1, 13)}
    for planet, house in planet_houses.items():
        house_occupants[house].append(planet)
    return house_occupants


def get_planets_in_star_of(target_planet, planets_data):
    return [p for p, info in planets_data.items() if info["star_lord"] == target_planet]


def get_houses_owned_by_planet(planet, houses_data):
    """Get houses where the cusp sign is owned by this planet."""
    if planet not in PLANET_SIGNS:
        return []
    owned_signs = PLANET_SIGNS[planet]
    return [h for h, info in houses_data.items() if info["sign"] in owned_signs]


def get_houses_with_cusp_in_sign(sign, houses_data):
    """Get houses whose cusp falls in the given sign."""
    return [h for h, info in houses_data.items() if info["sign"] == sign]


def get_planets_aspecting_planet(target_planet, planets_data, planet_houses):
    """Check if Mars, Jupiter, or Saturn aspects the target planet's house."""
    target_house = planet_houses.get(target_planet)
    if not target_house:
        return []
    
    aspecting = []
    for planet in ["Mars", "Jupiter", "Saturn"]:
        if planet not in planet_houses:
            continue
        planet_house = planet_houses[planet]
        
        aspected_houses = []
        aspected_houses.append(((planet_house - 1 + 6) % 12) + 1)  # 7th aspect
        
        if planet == "Mars":
            aspected_houses.append(((planet_house - 1 + 3) % 12) + 1)  # 4th
            aspected_houses.append(((planet_house - 1 + 7) % 12) + 1)  # 8th
        elif planet == "Jupiter":
            aspected_houses.append(((planet_house - 1 + 4) % 12) + 1)  # 5th
            aspected_houses.append(((planet_house - 1 + 8) % 12) + 1)  # 9th
        elif planet == "Saturn":
            aspected_houses.append(((planet_house - 1 + 2) % 12) + 1)  # 3rd
            aspected_houses.append(((planet_house - 1 + 9) % 12) + 1)  # 10th
        
        if target_house in aspected_houses:
            aspecting.append(planet)
    
    return aspecting


# ==============================================================================
# KP SIGNIFICATORS CALCULATION
# ==============================================================================

def calculate_house_significators(house_num, houses_data, planets_data, house_occupants, skip_level_b_for):
    """Calculate house significators using standard KP Level A, B, C, D."""
    significators = {
        "level_A_star_of_occupants": [],
        "level_B_star_of_owner": [],
        "level_C_occupants": [],
        "level_D_owner": []
    }
    
    owner = houses_data[house_num]["sign_lord"]
    occupants = [p for p in house_occupants.get(house_num, []) if p in REGULAR_PLANETS]
    
    significators["level_D_owner"].append(owner)
    significators["level_C_occupants"] = occupants.copy()
    
    # Level B: Planets in star of Owner (skip if owner should skip Level B)
    if owner not in skip_level_b_for:
        for planet in get_planets_in_star_of(owner, planets_data):
            if planet in REGULAR_PLANETS:
                significators["level_B_star_of_owner"].append(planet)
    
    # Level A: Planets in star of Occupants
    for occupant in occupants:
        for planet in get_planets_in_star_of(occupant, planets_data):
            if planet in REGULAR_PLANETS and planet not in significators["level_A_star_of_occupants"]:
                significators["level_A_star_of_occupants"].append(planet)
    
    return significators


def get_combined_significators(significators):
    combined = []
    for level in ["level_A_star_of_occupants", "level_B_star_of_owner", "level_C_occupants", "level_D_owner"]:
        for planet in significators[level]:
            if planet not in combined:
                combined.append(planet)
    return combined


def calculate_planet_significations(planets_data, houses_data, planet_houses, house_occupants):
    """Calculate significations for all planets using complete KP rules."""
    planet_significations = {planet: [] for planet in PLANETS}
    
    # Node info
    rahu_sign = planets_data["Rahu"]["sign"]
    ketu_sign = planets_data["Ketu"]["sign"]
    rahu_represents = SIGN_LORDS[rahu_sign]
    ketu_represents = SIGN_LORDS[ketu_sign]
    rahu_house = planet_houses["Rahu"]
    ketu_house = planet_houses["Ketu"]
    ketu_star_lord = planets_data["Ketu"]["star_lord"]
    
    # Represented planet's ownership houses
    rahu_rep_ownership = get_houses_owned_by_planet(rahu_represents, houses_data)
    ketu_rep_ownership = get_houses_owned_by_planet(ketu_represents, houses_data)
    
    # Represented planet's occupancy
    rahu_rep_occupancy = planet_houses.get(rahu_represents)
    ketu_rep_occupancy = planet_houses.get(ketu_represents)
    
    # Houses with cusp in node's sign
    houses_cusp_in_rahu_sign = get_houses_with_cusp_in_sign(rahu_sign, houses_data)
    houses_cusp_in_ketu_sign = get_houses_with_cusp_in_sign(ketu_sign, houses_data)
    
    # Planets in nodes' stars (regular planets only)
    planets_in_rahu_star = [p for p in get_planets_in_star_of("Rahu", planets_data) if p in REGULAR_PLANETS]
    planets_in_ketu_star = [p for p in get_planets_in_star_of("Ketu", planets_data) if p in REGULAR_PLANETS]
    
    # Conjunction info
    planets_conjunct_ketu = [p for p in REGULAR_PLANETS 
                             if planets_data[p]["sign"] == ketu_sign 
                             and planets_data[p]["star_lord"] == "Ketu"]
    planets_conjunct_rahu = [p for p in REGULAR_PLANETS 
                             if planets_data[p]["sign"] == rahu_sign 
                             and planets_data[p]["star_lord"] == "Rahu"]
    
    rahu_aspected_by = get_planets_aspecting_planet("Rahu", planets_data, planet_houses)
    
    # Track planets that should skip Level B due to conjunction
    skip_level_b_for = []
    if planets_conjunct_ketu:
        skip_level_b_for.append(ketu_represents)
    if planets_conjunct_rahu:
        skip_level_b_for.append(rahu_represents)
    
    node_rep_info = {
        "rahu_sign": rahu_sign, "ketu_sign": ketu_sign,
        "rahu_represents": rahu_represents, "ketu_represents": ketu_represents,
        "rahu_house": rahu_house, "ketu_house": ketu_house,
        "ketu_star_lord": ketu_star_lord,
        "rahu_aspected_by": rahu_aspected_by,
        "planets_conjunct_ketu": planets_conjunct_ketu,
        "planets_conjunct_rahu": planets_conjunct_rahu,
        "planets_in_rahu_star": planets_in_rahu_star,
        "planets_in_ketu_star": planets_in_ketu_star
    }
    
    # =========================================================================
    # STEP 1: Calculate significations for REGULAR PLANETS using Level A,B,C,D
    # =========================================================================
    
    all_house_significators = {}
    for house_num in range(1, 13):
        significators = calculate_house_significators(
            house_num, houses_data, planets_data, house_occupants, skip_level_b_for
        )
        all_house_significators[house_num] = significators
        
        combined = get_combined_significators(significators)
        for planet in combined:
            if planet in REGULAR_PLANETS and house_num not in planet_significations[planet]:
                planet_significations[planet].append(house_num)
    
    # =========================================================================
    # STEP 2: Planets in RAHU's star → Conditional based on conjunction
    # =========================================================================
    
    if planets_conjunct_ketu or planets_conjunct_rahu:
        # Conjunction exists: Add only houses with CUSP in Rahu's sign
        for planet in planets_in_rahu_star:
            for house in houses_cusp_in_rahu_sign:
                if house not in planet_significations[planet]:
                    planet_significations[planet].append(house)
    else:
        # No conjunction: Add Rahu's REPRESENTED planet's OWNERSHIP
        for planet in planets_in_rahu_star:
            for house in rahu_rep_ownership:
                if house not in planet_significations[planet]:
                    planet_significations[planet].append(house)
    
    # =========================================================================
    # STEP 3: Planets in KETU's star → Add Ketu's OCCUPIED HOUSE only
    # =========================================================================
    
    for planet in planets_in_ketu_star:
        if ketu_house not in planet_significations[planet]:
            planet_significations[planet].append(ketu_house)
    
    # =========================================================================
    # STEP 4: Conjunction rule - represented planet gains conjunct planets' sigs
    # =========================================================================
    
    if planets_conjunct_ketu:
        for conjunct_planet in planets_conjunct_ketu:
            for house in planet_significations[conjunct_planet]:
                if house not in planet_significations[ketu_represents]:
                    planet_significations[ketu_represents].append(house)
    
    if planets_conjunct_rahu:
        for conjunct_planet in planets_conjunct_rahu:
            for house in planet_significations[conjunct_planet]:
                if house not in planet_significations[rahu_represents]:
                    planet_significations[rahu_represents].append(house)
    
    # =========================================================================
    # STEP 5: Calculate RAHU significations
    # =========================================================================
    
    rahu_sigs = []
    
    if rahu_aspected_by:
        # RAHU aspected: Aspecting planet's OCCUPANCY + OWNERSHIP
        for asp_planet in rahu_aspected_by:
            # Aspecting planet's OCCUPANCY
            asp_planet_house = planet_houses.get(asp_planet)
            if asp_planet_house and asp_planet_house not in rahu_sigs:
                rahu_sigs.append(asp_planet_house)
            
            # Aspecting planet's OWNERSHIP
            asp_planet_ownership = get_houses_owned_by_planet(asp_planet, houses_data)
            for house in asp_planet_ownership:
                if house not in rahu_sigs:
                    rahu_sigs.append(house)
        
        # Add house(s) with cusp in Rahu's sign
        for house in houses_cusp_in_rahu_sign:
            if house not in rahu_sigs:
                rahu_sigs.append(house)
    else:
        # RAHU not aspected
        if planets_in_rahu_star:
            # Planets exist in Rahu's star: Rahu's house + represented planet's OCCUPANCY
            rahu_sigs.append(rahu_house)
            if rahu_rep_occupancy and rahu_rep_occupancy not in rahu_sigs:
                rahu_sigs.append(rahu_rep_occupancy)
        else:
            # NO planets in Rahu's star: Rahu's house + Ketu's house (axis)
            rahu_sigs.append(rahu_house)
            if ketu_house not in rahu_sigs:
                rahu_sigs.append(ketu_house)
    
    planet_significations["Rahu"] = sorted(rahu_sigs)
    
    # =========================================================================
    # STEP 6: Calculate KETU significations
    # =========================================================================
    
    ketu_sigs = []
    
    # Star lord's OWNERSHIP houses
    if ketu_star_lord in REGULAR_PLANETS:
        for house in get_houses_owned_by_planet(ketu_star_lord, houses_data):
            if house not in ketu_sigs:
                ketu_sigs.append(house)
        
        # Star lord's OCCUPIED house
        star_lord_house = planet_houses.get(ketu_star_lord)
        if star_lord_house and star_lord_house not in ketu_sigs:
            ketu_sigs.append(star_lord_house)
    
    # Conditional: Ketu's occupied house OR cusp in Ketu's sign
    if planets_in_ketu_star:
        # Planets exist in Ketu's star: use Ketu's OCCUPIED house
        if ketu_house not in ketu_sigs:
            ketu_sigs.append(ketu_house)
    else:
        # NO planets in Ketu's star: use house(s) with cusp in Ketu's sign
        for house in houses_cusp_in_ketu_sign:
            if house not in ketu_sigs:
                ketu_sigs.append(house)
    
    planet_significations["Ketu"] = sorted(ketu_sigs)
    
    # =========================================================================
    # STEP 7: Sort all significations
    # =========================================================================
    
    for planet in REGULAR_PLANETS:
        planet_significations[planet].sort()
    
    return planet_significations, all_house_significators, node_rep_info


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_kp_significators(data):
    """
    Main function to calculate KP Significators
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str (optional)
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float (default 5.5)
    
    Returns:
    --------
    dict: Complete KP Significators analysis
    """
    user_name = data.get('user_name', '')
    date_str = data.get('birth_date')
    time_str = data.get('birth_time')
    lat_value = data.get('latitude')
    lon_value = data.get('longitude')
    
    latitude = float(lat_value) if lat_value is not None else None
    longitude = float(lon_value) if lon_value is not None else None
    timezone = float(data.get('timezone_offset', 5.5))
    
    # Calculate Julian Day and Ayanamsa
    jd = datetime_to_jd(date_str, time_str, timezone)
    ayanamsa = get_kp_ayanamsa(jd)
    
    # Calculate planetary positions
    planets_data = calculate_planet_positions(jd, ayanamsa)
    
    # Calculate house cusps
    houses_data = calculate_house_cusps(jd, latitude, longitude, ayanamsa)
    
    # Determine planet house positions
    planet_houses = get_planet_house_positions(planets_data, houses_data)
    
    # Get house occupants
    house_occupants = get_house_occupants(planet_houses)
    
    # Calculate planet significations (main KP logic)
    planet_significations, all_house_significators, node_rep_info = calculate_planet_significations(
        planets_data, houses_data, planet_houses, house_occupants
    )
    
    # Prepare response
    response = {
        "input": {
            "user_name": user_name, 
            "birth_date": date_str, 
            "birth_time": time_str,
            "latitude": latitude, 
            "longitude": longitude, 
            "timezone_offset": timezone
        },
        "ayanamsa": {
            "type": "KP New (Lahiri + 50.2388475\")", 
            "value": round(ayanamsa, 6)
        },
        "node_representation": {
            "rahu_in_sign": node_rep_info["rahu_sign"],
            "rahu_represents": node_rep_info["rahu_represents"],
            "rahu_aspected_by": node_rep_info["rahu_aspected_by"],
            "planets_conjunct_rahu": node_rep_info["planets_conjunct_rahu"],
            "planets_in_rahu_star": node_rep_info["planets_in_rahu_star"],
            "ketu_in_sign": node_rep_info["ketu_sign"],
            "ketu_represents": node_rep_info["ketu_represents"],
            "ketu_star_lord": node_rep_info["ketu_star_lord"],
            "planets_conjunct_ketu": node_rep_info["planets_conjunct_ketu"],
            "planets_in_ketu_star": node_rep_info["planets_in_ketu_star"]
        },
        "planets": {},
        "houses": {},
        "planet_house_positions": planet_houses,
        "house_occupants": {str(k): v for k, v in house_occupants.items()},
        "house_significators": {},
        "planet_significations": planet_significations
    }
    
    # Add planet details
    for planet in PLANETS:
        response["planets"][planet] = {
            "longitude": planets_data[planet]["longitude"],
            "sign": planets_data[planet]["sign"],
            "nakshatra": planets_data[planet]["nakshatra"],
            "star_lord": planets_data[planet]["star_lord"],
            "sub_lord": planets_data[planet]["sub_lord"],
            "house_position": planet_houses.get(planet),
            "signifies_houses": planet_significations[planet]
        }
    
    # Add house details
    for house_num in range(1, 13):
        sig = all_house_significators[house_num]
        response["houses"][str(house_num)] = {
            "cusp_longitude": houses_data[house_num]["cusp_longitude"],
            "sign": houses_data[house_num]["sign"],
            "sign_lord": houses_data[house_num]["sign_lord"],
            "nakshatra": houses_data[house_num]["nakshatra"],
            "star_lord": houses_data[house_num]["star_lord"],
            "sub_lord": houses_data[house_num]["sub_lord"],
            "occupants": house_occupants.get(house_num, []),
            "significators": {
                "level_A_star_of_occupants": sig["level_A_star_of_occupants"],
                "level_B_star_of_owner": sig["level_B_star_of_owner"],
                "level_C_occupants": sig["level_C_occupants"],
                "level_D_owner": sig["level_D_owner"],
                "combined": get_combined_significators(sig)
            }
        }
    
    # Add combined house significators
    for house_num in range(1, 13):
        response["house_significators"][str(house_num)] = get_combined_significators(
            all_house_significators[house_num]
        )
    
    return response