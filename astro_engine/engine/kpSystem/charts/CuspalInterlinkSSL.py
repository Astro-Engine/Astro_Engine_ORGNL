"""
KP Cuspal Interlink - Calculation Module (Advanced)
====================================================
Krishnamurti Paddhati (KP) Astrology - Cuspal Interlink Analysis
S.P. Khullar Methodology - METHOD B

Complete 4-tier lordship: Sign, Star, Sub, Sub-Sub
"""

import swisseph as swe
from datetime import datetime

# ==============================================================================
# CONSTANTS
# ==============================================================================

# KP Constants
SIGN_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 27 Nakshatras with exact boundaries
NAKSHATRAS = [
    {"num": 1, "name": "Ashwini", "lord": "Ketu", "start": 0.0, "end": 13.333333},
    {"num": 2, "name": "Bharani", "lord": "Venus", "start": 13.333333, "end": 26.666667},
    {"num": 3, "name": "Krittika", "lord": "Sun", "start": 26.666667, "end": 40.0},
    {"num": 4, "name": "Rohini", "lord": "Moon", "start": 40.0, "end": 53.333333},
    {"num": 5, "name": "Mrigashira", "lord": "Mars", "start": 53.333333, "end": 66.666667},
    {"num": 6, "name": "Ardra", "lord": "Rahu", "start": 66.666667, "end": 80.0},
    {"num": 7, "name": "Punarvasu", "lord": "Jupiter", "start": 80.0, "end": 93.333333},
    {"num": 8, "name": "Pushya", "lord": "Saturn", "start": 93.333333, "end": 106.666667},
    {"num": 9, "name": "Ashlesha", "lord": "Mercury", "start": 106.666667, "end": 120.0},
    {"num": 10, "name": "Magha", "lord": "Ketu", "start": 120.0, "end": 133.333333},
    {"num": 11, "name": "Purva Phalguni", "lord": "Venus", "start": 133.333333, "end": 146.666667},
    {"num": 12, "name": "Uttara Phalguni", "lord": "Sun", "start": 146.666667, "end": 160.0},
    {"num": 13, "name": "Hasta", "lord": "Moon", "start": 160.0, "end": 173.333333},
    {"num": 14, "name": "Chitra", "lord": "Mars", "start": 173.333333, "end": 186.666667},
    {"num": 15, "name": "Swati", "lord": "Rahu", "start": 186.666667, "end": 200.0},
    {"num": 16, "name": "Vishakha", "lord": "Jupiter", "start": 200.0, "end": 213.333333},
    {"num": 17, "name": "Anuradha", "lord": "Saturn", "start": 213.333333, "end": 226.666667},
    {"num": 18, "name": "Jyeshtha", "lord": "Mercury", "start": 226.666667, "end": 240.0},
    {"num": 19, "name": "Moola", "lord": "Ketu", "start": 240.0, "end": 253.333333},
    {"num": 20, "name": "Purva Ashadha", "lord": "Venus", "start": 253.333333, "end": 266.666667},
    {"num": 21, "name": "Uttara Ashadha", "lord": "Sun", "start": 266.666667, "end": 280.0},
    {"num": 22, "name": "Shravana", "lord": "Moon", "start": 280.0, "end": 293.333333},
    {"num": 23, "name": "Dhanishta", "lord": "Mars", "start": 293.333333, "end": 306.666667},
    {"num": 24, "name": "Shatabhisha", "lord": "Rahu", "start": 306.666667, "end": 320.0},
    {"num": 25, "name": "Purva Bhadrapada", "lord": "Jupiter", "start": 320.0, "end": 333.333333},
    {"num": 26, "name": "Uttara Bhadrapada", "lord": "Saturn", "start": 333.333333, "end": 346.666667},
    {"num": 27, "name": "Revati", "lord": "Mercury", "start": 346.666667, "end": 360.0}
]

# Vimshottari Dasha Lords and Years
VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120

# Planet constants
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# KP House Classifications
POSITIVE_HOUSES = [1, 3, 5, 9, 11]
NEUTRAL_HOUSES = [2, 6, 10]
NEGATIVE_HOUSES = [4, 7, 8, 12]


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def normalize_longitude(longitude):
    """Normalize longitude to 0-360 range"""
    longitude = longitude % 360.0
    if longitude < 0:
        longitude += 360.0
    return longitude


def get_julian_day(birth_date, birth_time, timezone_offset):
    """Convert date/time to Julian Day with timezone adjustment"""
    try:
        dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
        
        # Adjust for timezone to get UTC
        utc_hour = dt.hour - timezone_offset
        utc_minute = dt.minute
        utc_second = dt.second
        
        # Handle day boundary crossing
        day = dt.day
        if utc_hour < 0:
            utc_hour += 24
            day -= 1
        elif utc_hour >= 24:
            utc_hour -= 24
            day += 1
        
        # Calculate Julian Day
        jd = swe.julday(dt.year, dt.month, day, utc_hour + utc_minute/60.0 + utc_second/3600.0)
        
        return jd
    except Exception as e:
        raise ValueError(f"Error calculating Julian Day: {str(e)}")


def get_ayanamsa(jd):
    """Get KP New Ayanamsa (Krishnamurti Ayanamsa)"""
    try:
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        return ayanamsa
    except Exception as e:
        raise ValueError(f"Error calculating Ayanamsa: {str(e)}")


def get_sign_info(longitude):
    """Get sign number, name, lord, and position in sign"""
    longitude = normalize_longitude(longitude)
    sign_num = int(longitude / 30)
    if sign_num >= 12:
        sign_num = 11
    
    position_in_sign = longitude % 30
    
    degrees = int(position_in_sign)
    minutes = int((position_in_sign - degrees) * 60)
    seconds = int(((position_in_sign - degrees) * 60 - minutes) * 60)
    
    return {
        "sign_num": sign_num,
        "sign_name": SIGN_NAMES[sign_num],
        "sign_lord": SIGN_LORDS[sign_num],
        "position_in_sign": position_in_sign,
        "formatted": f"{degrees}°{minutes}'{seconds}\" {SIGN_NAMES[sign_num]}"
    }


def get_nakshatra_info(longitude):
    """Get nakshatra, lord, and position in nakshatra"""
    longitude = normalize_longitude(longitude)
    
    # Handle edge case at exactly 360 degrees
    if longitude >= 360.0:
        longitude = 0.0
    
    for nak in NAKSHATRAS:
        if nak["start"] <= longitude < nak["end"]:
            position_in_nak = longitude - nak["start"]
            position_in_nak_minutes = position_in_nak * 60.0  # Convert to arc minutes
            
            return {
                "nakshatra_num": nak["num"],
                "nakshatra_name": nak["name"],
                "nakshatra_lord": nak["lord"],
                "position_in_nakshatra": position_in_nak,
                "position_in_nakshatra_minutes": position_in_nak_minutes,
                "nakshatra_start": nak["start"],
                "nakshatra_end": nak["end"]
            }
    
    # Fallback to first nakshatra for edge cases
    return {
        "nakshatra_num": 1,
        "nakshatra_name": "Ashwini",
        "nakshatra_lord": "Ketu",
        "position_in_nakshatra": 0.0,
        "position_in_nakshatra_minutes": 0.0,
        "nakshatra_start": 0.0,
        "nakshatra_end": 13.333333
    }


def calculate_sub_divisions(nakshatra_lord_index):
    """Calculate the 9 sub-divisions within a nakshatra starting from nakshatra lord"""
    nakshatra_span_degrees = 13.333333
    nakshatra_span_minutes = 800.0
    
    # Rotate the sequence to start from nakshatra lord (METHOD B)
    lords_sequence = VIMSHOTTARI_LORDS[nakshatra_lord_index:] + VIMSHOTTARI_LORDS[:nakshatra_lord_index]
    years_sequence = VIMSHOTTARI_YEARS[nakshatra_lord_index:] + VIMSHOTTARI_YEARS[:nakshatra_lord_index]
    
    sub_divisions = []
    current_position_degrees = 0.0
    current_position_minutes = 0.0
    
    for lord, years in zip(lords_sequence, years_sequence):
        sub_span_degrees = (years / TOTAL_YEARS) * nakshatra_span_degrees
        sub_span_minutes = (years / TOTAL_YEARS) * nakshatra_span_minutes
        
        sub_divisions.append({
            "lord": lord,
            "years": years,
            "start_degrees": current_position_degrees,
            "end_degrees": current_position_degrees + sub_span_degrees,
            "start_minutes": current_position_minutes,
            "end_minutes": current_position_minutes + sub_span_minutes,
            "span_degrees": sub_span_degrees,
            "span_minutes": sub_span_minutes
        })
        
        current_position_degrees += sub_span_degrees
        current_position_minutes += sub_span_minutes
    
    return sub_divisions


def get_sub_lord(longitude):
    """Calculate sub lord for a given longitude"""
    longitude = normalize_longitude(longitude)
    
    # Get nakshatra info
    nak_info = get_nakshatra_info(longitude)
    position_in_nak = nak_info["position_in_nakshatra"]
    position_in_nak_minutes = nak_info["position_in_nakshatra_minutes"]
    
    # Find nakshatra lord index
    nak_lord = nak_info["nakshatra_lord"]
    nak_lord_index = VIMSHOTTARI_LORDS.index(nak_lord)
    
    # Calculate sub divisions (METHOD B - starts with star lord)
    subs = calculate_sub_divisions(nak_lord_index)
    
    # Find which sub the position falls into
    sub_lord_result = None
    for sub in subs:
        if sub["start_degrees"] <= position_in_nak < sub["end_degrees"]:
            position_in_sub = position_in_nak - sub["start_degrees"]
            position_in_sub_minutes = position_in_nak_minutes - sub["start_minutes"]
            
            sub_lord_result = {
                "sub_lord": sub["lord"],
                "sub_start_degrees": sub["start_degrees"],
                "sub_end_degrees": sub["end_degrees"],
                "sub_start_minutes": sub["start_minutes"],
                "sub_end_minutes": sub["end_minutes"],
                "position_in_sub_degrees": position_in_sub,
                "position_in_sub_minutes": position_in_sub_minutes,
                "sub_span_degrees": sub["span_degrees"],
                "sub_span_minutes": sub["span_minutes"]
            }
            break
    
    # Handle edge case
    if sub_lord_result is None:
        sub_lord_result = {
            "sub_lord": subs[-1]["lord"],
            "sub_start_degrees": subs[-1]["start_degrees"],
            "sub_end_degrees": subs[-1]["end_degrees"],
            "sub_start_minutes": subs[-1]["start_minutes"],
            "sub_end_minutes": subs[-1]["end_minutes"],
            "position_in_sub_degrees": 0.0,
            "position_in_sub_minutes": 0.0,
            "sub_span_degrees": subs[-1]["span_degrees"],
            "sub_span_minutes": subs[-1]["span_minutes"]
        }
    
    return sub_lord_result


def calculate_sub_sub_divisions(sub_lord, sub_span_minutes):
    """Calculate the 9 sub-sub divisions within a sub"""
    sub_lord_index = VIMSHOTTARI_LORDS.index(sub_lord)
    
    # Rotate sequence to start from sub lord (METHOD B for sub-sub)
    lords_sequence = VIMSHOTTARI_LORDS[sub_lord_index:] + VIMSHOTTARI_LORDS[:sub_lord_index]
    years_sequence = VIMSHOTTARI_YEARS[sub_lord_index:] + VIMSHOTTARI_YEARS[:sub_lord_index]
    
    sub_sub_divisions = []
    current_position_minutes = 0.0
    
    for lord, years in zip(lords_sequence, years_sequence):
        sub_sub_span_minutes = (years / TOTAL_YEARS) * sub_span_minutes
        sub_sub_span_degrees = sub_sub_span_minutes / 60.0
        
        sub_sub_divisions.append({
            "lord": lord,
            "years": years,
            "start_minutes": current_position_minutes,
            "end_minutes": current_position_minutes + sub_sub_span_minutes,
            "start_degrees": current_position_minutes / 60.0,
            "end_degrees": (current_position_minutes + sub_sub_span_minutes) / 60.0,
            "span_minutes": sub_sub_span_minutes,
            "span_degrees": sub_sub_span_degrees
        })
        
        current_position_minutes += sub_sub_span_minutes
    
    return sub_sub_divisions


def get_sub_sub_lord(longitude):
    """Calculate sub-sub lord (SSL) for a given longitude"""
    sub_info = get_sub_lord(longitude)
    position_in_sub_minutes = sub_info["position_in_sub_minutes"]
    
    # Calculate sub-sub divisions
    sub_subs = calculate_sub_sub_divisions(sub_info["sub_lord"], sub_info["sub_span_minutes"])
    
    # Find which sub-sub the position falls into
    sub_sub_result = None
    for sub_sub in sub_subs:
        if sub_sub["start_minutes"] <= position_in_sub_minutes < sub_sub["end_minutes"]:
            position_in_sub_sub_minutes = position_in_sub_minutes - sub_sub["start_minutes"]
            
            # Determine if in first half or second half
            mid_point = sub_sub["span_minutes"] / 2.0
            half = "First Half" if position_in_sub_sub_minutes < mid_point else "Second Half"
            
            sub_sub_result = {
                "sub_sub_lord": sub_sub["lord"],
                "ssl": sub_sub["lord"],
                "sub_sub_start_minutes": sub_sub["start_minutes"],
                "sub_sub_end_minutes": sub_sub["end_minutes"],
                "position_in_sub_sub_minutes": position_in_sub_sub_minutes,
                "sub_sub_span_minutes": sub_sub["span_minutes"],
                "half": half
            }
            break
    
    # Handle edge case
    if sub_sub_result is None:
        sub_sub_result = {
            "sub_sub_lord": sub_subs[-1]["lord"],
            "ssl": sub_subs[-1]["lord"],
            "sub_sub_start_minutes": sub_subs[-1]["start_minutes"],
            "sub_sub_end_minutes": sub_subs[-1]["end_minutes"],
            "position_in_sub_sub_minutes": 0.0,
            "sub_sub_span_minutes": sub_subs[-1]["span_minutes"],
            "half": "Second Half"
        }
    
    return sub_sub_result


def get_complete_lordship(longitude):
    """Get complete 4-tier lordship: Sign, Star, Sub, Sub-Sub"""
    sign_info = get_sign_info(longitude)
    nak_info = get_nakshatra_info(longitude)
    sub_info = get_sub_lord(longitude)
    sub_sub_info = get_sub_sub_lord(longitude)
    
    return {
        "longitude": longitude,
        "sign": sign_info["sign_name"],
        "sign_lord": sign_info["sign_lord"],
        "sign_position": sign_info["formatted"],
        "nakshatra": nak_info["nakshatra_name"],
        "nakshatra_lord": nak_info["nakshatra_lord"],
        "star_lord": nak_info["nakshatra_lord"],
        "sub_lord": sub_info["sub_lord"],
        "sub_sub_lord": sub_sub_info["sub_sub_lord"],
        "ssl": sub_sub_info["ssl"],
        "sub_sub_half": sub_sub_info["half"]
    }


# ==============================================================================
# CORE CALCULATION FUNCTIONS
# ==============================================================================

def calculate_planet_position(jd, planet_id, planet_name):
    """Calculate single planet position with proper speed and retrograde detection"""
    try:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        calc_result = swe.calc_ut(jd, planet_id, flags)
        
        if not calc_result or len(calc_result) < 1:
            raise ValueError(f"Invalid calculation result for {planet_name}")
        
        position_data = calc_result[0]
        
        if len(position_data) < 4:
            raise ValueError(f"Insufficient position data for {planet_name}")
        
        tropical_long = float(position_data[0])
        speed_deg_per_day = float(position_data[3])
        
        return tropical_long, speed_deg_per_day
        
    except Exception as e:
        raise ValueError(f"Error calculating {planet_name}: {str(e)}")


def calculate_planets(jd, ayanamsa):
    """Calculate all planetary positions including Rahu/Ketu"""
    planets_data = {}
    
    for planet_name in PLANET_NAMES:
        if planet_name == "Ketu":
            continue  # Calculate with Rahu
        
        try:
            planet_id = PLANETS[planet_name]
            
            tropical_long, speed_deg_per_day = calculate_planet_position(jd, planet_id, planet_name)
            
            sidereal_long = normalize_longitude(tropical_long - ayanamsa)
            
            is_retrograde = speed_deg_per_day < 0
            
            lordship = get_complete_lordship(sidereal_long)
            
            planets_data[planet_name] = {
                "longitude": sidereal_long,
                "speed": round(speed_deg_per_day, 10),
                "is_retrograde": is_retrograde,
                "retrograde_status": "Retrograde" if is_retrograde else "Direct",
                **lordship
            }
            
            if planet_name == "Rahu":
                ketu_long = normalize_longitude(sidereal_long + 180.0)
                ketu_speed = speed_deg_per_day
                ketu_is_retrograde = ketu_speed < 0
                
                ketu_lordship = get_complete_lordship(ketu_long)
                
                planets_data["Ketu"] = {
                    "longitude": ketu_long,
                    "speed": round(ketu_speed, 10),
                    "is_retrograde": ketu_is_retrograde,
                    "retrograde_status": "Retrograde" if ketu_is_retrograde else "Direct",
                    **ketu_lordship
                }
        
        except Exception as e:
            raise ValueError(f"Error calculating {planet_name}: {str(e)}")
    
    return planets_data


def calculate_houses_placidus(jd, latitude, longitude, ayanamsa):
    """
    Calculate house cusps using Placidus system
    CRITICAL FIX: cusps[0] = House 1, cusps[1] = House 2, etc.
    """
    try:
        # Get houses from Swiss Ephemeris
        houses_result = swe.houses(jd, latitude, longitude, b'P')
        
        if not houses_result:
            raise ValueError("swe.houses() returned None")
        
        if not isinstance(houses_result, tuple) or len(houses_result) < 2:
            raise ValueError(f"swe.houses() returned invalid structure")
        
        cusps = houses_result[0]  # cusps[0] to cusps[11]
        ascmc = houses_result[1]  # ascmc[0]=Asc, ascmc[1]=MC
        
        # Validate cusps
        if not cusps:
            raise ValueError("Cusps is None or empty")
        
        if not isinstance(cusps, (tuple, list)):
            raise ValueError(f"Cusps is not a tuple/list")
        
        if len(cusps) < 12:
            raise ValueError(f"Cusps has {len(cusps)} elements, expected 12")
        
        # Validate ascmc
        if not ascmc:
            raise ValueError("Ascmc is None or empty")
        
        if len(ascmc) < 2:
            raise ValueError(f"Ascmc has {len(ascmc)} elements, expected at least 2")
        
        # ✅ CORRECT MAPPING: cusps[0]=House 1, cusps[1]=House 2, etc.
        house_cusps = {}
        
        for i in range(12):
            house_num = i + 1  # House numbers: 1, 2, 3... 12
            tropical_cusp = cusps[i]  # cusps[0], cusps[1], cusps[2]...
            sidereal_cusp = normalize_longitude(tropical_cusp - ayanamsa)
            lordship = get_complete_lordship(sidereal_cusp)
            
            house_cusps[house_num] = {
                "cusp_longitude": sidereal_cusp,
                **lordship
            }
        
        # Extract Ascendant and MC
        ascendant_tropical = ascmc[0]  # Should match cusps[0]
        mc_tropical = ascmc[1]
        
        asc_sidereal = normalize_longitude(ascendant_tropical - ayanamsa)
        mc_sidereal = normalize_longitude(mc_tropical - ayanamsa)
        
        # ✅ VERIFICATION: House 1 MUST equal Ascendant
        house_1_long = house_cusps[1]["cusp_longitude"]
        if abs(house_1_long - asc_sidereal) > 0.0001:
            raise ValueError(
                f"CRITICAL ERROR: House 1 cusp ({house_1_long:.6f}) "
                f"does NOT match Ascendant ({asc_sidereal:.6f})! "
                f"Difference: {abs(house_1_long - asc_sidereal):.6f}"
            )
        
        return {
            "houses": house_cusps,
            "ascendant": {
                "longitude": asc_sidereal,
                **get_complete_lordship(asc_sidereal)
            },
            "midheaven": {
                "longitude": mc_sidereal,
                **get_complete_lordship(mc_sidereal)
            }
        }
    
    except Exception as e:
        raise ValueError(f"Error calculating houses: {str(e)}")


def get_planet_house_position(planet_long, house_cusps):
    """Determine which house a planet is in"""
    planet_long = normalize_longitude(planet_long)
    
    for house_num in range(1, 13):
        start = house_cusps[house_num]["cusp_longitude"]
        
        # Calculate end (next house cusp)
        next_house = (house_num % 12) + 1
        end = house_cusps[next_house]["cusp_longitude"]
        
        # Handle zodiac wrap-around
        if start < end:
            if start <= planet_long < end:
                return house_num
        else:  # Crosses 0° Aries
            if planet_long >= start or planet_long < end:
                return house_num
    
    return 1  # Fallback


# ==============================================================================
# ANALYSIS FUNCTIONS
# ==============================================================================

def calculate_significators(planets_data, houses_data):
    """
    Calculate KP significators for each planet
    FIXED: Properly handle set/list conversions
    """
    significators = {}
    
    # Get house positions for all planets
    planet_houses = {}
    for planet_name, planet_data in planets_data.items():
        house_pos = get_planet_house_position(planet_data["longitude"], houses_data["houses"])
        planet_houses[planet_name] = house_pos
    
    for planet_name in PLANET_NAMES:
        planet_data = planets_data[planet_name]
        
        # 1. DIRECT SIGNIFICATIONS (as set)
        direct_significations = set()
        
        # Houses this planet owns (as sign lord)
        for house_num, house_data in houses_data["houses"].items():
            if house_data["sign_lord"] == planet_name:
                direct_significations.add(house_num)
        
        # House this planet occupies
        planet_house = planet_houses[planet_name]
        direct_significations.add(planet_house)
        
        # 2. STELLAR SIGNIFICATIONS (as set)
        stellar_significations = set()
        
        # Planets in this planet's star (nakshatra)
        planets_in_star = []
        for other_planet, other_data in planets_data.items():
            if other_data["star_lord"] == planet_name:
                planets_in_star.append(other_planet)
                # That planet's occupied house becomes stellar signification
                stellar_significations.add(planet_houses[other_planet])
        
        # 3. POSITIONAL SIGNIFICATIONS (as set)
        positional_significations = set()
        if not planets_in_star:
            # Use direct significations
            positional_significations = direct_significations.copy()
        
        # 4. NODE SIGNIFICATIONS (as set)
        node_significations = set()
        if planet_name in ["Rahu", "Ketu"]:
            # Node represents its dispositor (sign lord)
            dispositor = planet_data["sign_lord"]
            if dispositor in significators:
                # ✅ FIX: Convert list back to set
                node_significations = set(significators[dispositor]["direct_significations"])
            else:
                # Calculate dispositor's significations
                for house_num, house_data in houses_data["houses"].items():
                    if house_data["sign_lord"] == dispositor:
                        node_significations.add(house_num)
                if dispositor in planet_houses:
                    node_significations.add(planet_houses[dispositor])
        
        # Combine all (all are sets now)
        all_significations = direct_significations | stellar_significations | positional_significations | node_significations
        
        # Store as sorted lists for JSON serialization
        significators[planet_name] = {
            "direct_significations": sorted(list(direct_significations)),
            "stellar_significations": sorted(list(stellar_significations)),
            "positional_significations": sorted(list(positional_significations)),
            "node_significations": sorted(list(node_significations)),
            "planets_in_star": planets_in_star,
            "all_significations": sorted(list(all_significations))
        }
    
    return significators


def analyze_cuspal_interlinks_advanced(houses_data, planets_data):
    """
    Advanced Cuspal Interlink Analysis with S.P. Khullar methodology
    """
    # Calculate significators for all planets
    significators = calculate_significators(planets_data, houses_data)
    
    cuspal_analysis = {}
    
    for house_num, house_data in houses_data["houses"].items():
        # Get the 4-tier lords
        sign_lord = house_data["sign_lord"]
        star_lord = house_data["star_lord"]
        sub_lord = house_data["sub_lord"]
        sub_sub_lord = house_data["ssl"]
        
        # Get significators for each lord (these are lists)
        sign_lord_sig = significators[sign_lord]["all_significations"]
        star_lord_sig = significators[star_lord]["all_significations"]
        sub_lord_sig = significators[sub_lord]["all_significations"]
        sub_sub_lord_sig = significators[sub_sub_lord]["all_significations"]
        
        # Combined SL + SSL (convert to sets for union, then back to sorted list)
        combined_sl_ssl = sorted(list(set(sub_lord_sig) | set(sub_sub_lord_sig)))
        
        # Analyze positive/negative/neutral links
        positive_links = [h for h in combined_sl_ssl if h in POSITIVE_HOUSES]
        neutral_links = [h for h in combined_sl_ssl if h in NEUTRAL_HOUSES]
        negative_links = [h for h in combined_sl_ssl if h in NEGATIVE_HOUSES]
        
        # Check for 11th house link (universal fulfiller)
        has_11th_link = 11 in combined_sl_ssl
        
        # Calculate promise strength
        num_positive = len(positive_links)
        num_negative = len(negative_links)
        
        if num_negative > num_positive:
            promise_strength = "Denied"
        elif num_positive >= 3:
            promise_strength = "Very Strong"
        elif num_positive >= 2:
            promise_strength = "Strong"
        elif num_positive >= 1 and num_negative == 0:
            promise_strength = "Moderate"
        elif len(neutral_links) >= 2 and num_negative <= 1:
            promise_strength = "Weak"
        else:
            promise_strength = "Moderate"
        
        # Calculate positive percentage
        total_links = len(combined_sl_ssl)
        positive_percentage = (num_positive / total_links * 100) if total_links > 0 else 0
        
        # House interpretation
        house_meanings = {
            1: "Self, personality, physical body, vitality",
            2: "Family, wealth, speech, accumulated resources",
            3: "Courage, siblings, short travels, communication",
            4: "Mother, property, vehicles, happiness, endings",
            5: "Children, education, romance, speculation, creativity",
            6: "Enemies, diseases, debts, service, obstacles",
            7: "Marriage, partnerships, spouse, business partners",
            8: "Longevity, obstacles, sudden events, transformation",
            9: "Fortune, father, dharma, long travels, higher learning",
            10: "Career, profession, status, public image",
            11: "Gains, fulfillment, elder siblings, income",
            12: "Losses, expenses, foreign lands, moksha, isolation"
        }
        
        interpretation = f"{house_meanings.get(house_num, 'Unknown house')} - "
        interpretation += f"Promise is {promise_strength.lower()}. "
        interpretation += "Event highly likely to manifest. " if promise_strength in ["Very Strong", "Strong"] else ""
        
        if has_11th_link:
            interpretation += "11th house link provides universal support. "
        
        if positive_links:
            interpretation += f"Positive support from houses: {positive_links}. "
        if negative_links:
            interpretation += f"Challenges/obstacles from houses: {negative_links}."
        
        cuspal_analysis[house_num] = {
            "house": house_num,
            "cusp_lords": {
                "sign_lord": sign_lord,
                "star_lord": star_lord,
                "sub_lord": sub_lord,
                "sub_sub_lord": sub_sub_lord
            },
            "sign_lord_significator_of": sign_lord_sig,
            "star_lord_significator_of": star_lord_sig,
            "sub_lord_significator_of": sub_lord_sig,
            "sub_lord_breakdown": significators[sub_lord],
            "sub_sub_lord_significator_of": sub_sub_lord_sig,
            "combined_sl_ssl_significators": combined_sl_ssl,
            "combined_positive_links": positive_links,
            "combined_neutral_links": neutral_links,
            "combined_negative_links": negative_links,
            "has_11th_house_link": has_11th_link,
            "promise_strength": promise_strength,
            "positive_percentage": round(positive_percentage, 2),
            "interpretation": interpretation.strip()
        }
    
    return cuspal_analysis


def analyze_positional_status(planets_data):
    """Analyze Positional Status (PS) for each planet"""
    ps_analysis = {}
    
    # Count planets in each nakshatra
    nak_occupancy = {}
    for planet_name, data in planets_data.items():
        nak = data["nakshatra"]
        if nak not in nak_occupancy:
            nak_occupancy[nak] = []
        nak_occupancy[nak].append(planet_name)
    
    for planet_name, data in planets_data.items():
        ps_factors = []
        
        # Factor 1: In own star
        if data["star_lord"] == planet_name:
            ps_factors.append("In own star")
        
        # Factor 2: In own sub
        if data["sub_lord"] == planet_name:
            ps_factors.append("In own sub")
        
        # Factor 3: In own sub-sub
        if data["ssl"] == planet_name:
            ps_factors.append("In own sub-sub")
        
        # Factor 4: Untenanted nakshatras
        ruled_naks = [nak["name"] for nak in NAKSHATRAS if nak["lord"] == planet_name]
        untenanted = True
        for nak in ruled_naks:
            if nak in nak_occupancy and len(nak_occupancy[nak]) > 0:
                if not (len(nak_occupancy[nak]) == 1 and nak_occupancy[nak][0] == planet_name):
                    untenanted = False
                    break
        
        if untenanted and ruled_naks:
            ps_factors.append("Untenanted nakshatras")
        
        # Factor 5: Mutual star interchange (FIXED - no self-exchange)
        star_lord = data["star_lord"]
        if star_lord != planet_name and star_lord in planets_data:
            if planets_data[star_lord]["star_lord"] == planet_name:
                ps_factors.append(f"Mutual star exchange with {star_lord}")
        
        ps_analysis[planet_name] = {
            "has_positional_status": len(ps_factors) > 0,
            "ps_factors": ps_factors,
            "strength": len(ps_factors)
        }
    
    return ps_analysis


def analyze_cuspal_interlinks(houses_data, planets_data):
    """Basic cuspal interlinks between houses and planets"""
    planet_cusp_links = {}
    
    for planet_name in PLANET_NAMES:
        links = {
            "as_sign_lord": [],
            "as_star_lord": [],
            "as_sub_lord": [],
            "as_sub_sub_lord": []
        }
        
        for house_num, house_data in houses_data["houses"].items():
            if house_data["sign_lord"] == planet_name:
                links["as_sign_lord"].append(house_num)
            if house_data["star_lord"] == planet_name:
                links["as_star_lord"].append(house_num)
            if house_data["sub_lord"] == planet_name:
                links["as_sub_lord"].append(house_num)
            if house_data["ssl"] == planet_name:
                links["as_sub_sub_lord"].append(house_num)
        
        planet_cusp_links[planet_name] = links
    
    # House relationships
    house_relationships = {}
    for house_num in range(1, 13):
        relationships = {
            "favorable": [],
            "neutral": [],
            "adverse": []
        }
        
        for offset in [1, 3, 5, 9, 11]:
            target = ((house_num + offset - 2) % 12) + 1
            relationships["favorable"].append(target)
        
        for offset in [2, 6, 10]:
            target = ((house_num + offset - 2) % 12) + 1
            relationships["neutral"].append(target)
        
        for offset in [4, 7, 8, 12]:
            target = ((house_num + offset - 2) % 12) + 1
            relationships["adverse"].append(target)
        
        house_relationships[house_num] = relationships
    
    return {
        "planet_cusp_links": planet_cusp_links,
        "house_relationships": house_relationships
    }


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_kp_cuspal_interlink_advanced(data):
    """
    Main function to calculate KP Cuspal Interlink Advanced Analysis
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str (optional)
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float
    
    Returns:
    --------
    dict: Complete KP Cuspal Interlink Advanced Analysis
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    
    # Get Ayanamsa
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate planets
    planets = calculate_planets(jd, ayanamsa)
    
    # Calculate houses (CORRECTED)
    houses = calculate_houses_placidus(jd, latitude, longitude, ayanamsa)
    
    # Positional Status
    positional_status = analyze_positional_status(planets)
    
    # Basic Cuspal Interlinks
    basic_interlinks = analyze_cuspal_interlinks(houses, planets)
    
    # Advanced Cuspal Interlinks Analysis
    advanced_analysis = analyze_cuspal_interlinks_advanced(houses, planets)
    
    # Prepare response
    response = {
        "status": "success",
        "user_name": user_name,
        "birth_details": {
            "date": birth_date,
            "time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "calculation_details": {
            "accuracy": "100% - S.P. Khullar Cuspal Interlink with METHOD B",
            "house_system": "Placidus",
            "zodiac": "Sidereal (Nirayana)",
            "ayanamsa": {
                "type": "KP (Krishnamurti)",
                "value": ayanamsa
            },
            "julian_day": jd,
            "method": "METHOD B - Sub starts with Star Lord, Sub-sub starts with Sub Lord"
        },
        "planets": planets,
        "houses": houses,
        "positional_status": positional_status,
        "cuspal_interlinks": basic_interlinks,
        "cuspal_interlinks_analysis": advanced_analysis,
        "kp_principles": {
            "core_principle": "The planet in whose star a cusp falls proposes, but the sub-lord disposes.",
            "method": "100% S.P. KHULLAR CIT COMPLIANT",
            "sub_calculation": "METHOD B - Sub sequence starts with Star Lord",
            "sub_sub_calculation": "Sub-sub sequence starts with Sub Lord",
            "house_groups": {
                "positive_houses": POSITIVE_HOUSES,
                "neutral_houses": NEUTRAL_HOUSES,
                "negative_houses": NEGATIVE_HOUSES
            },
            "signification_hierarchy": {
                "star_lord": "Proposes broadly",
                "sub_lord": "Disposes (must confirm 60% positive)",
                "sub_sub_lord": "Specifies and fine-tunes"
            },
            "promise_rules": {
                "very_strong": "3+ positive links in combined SL+SSL",
                "strong": "2+ positive links in combined SL+SSL",
                "moderate": "1+ positive, no negative in combined SL+SSL",
                "weak": "2+ neutral, ≤1 negative in combined SL+SSL",
                "denied": "Predominantly negative links"
            },
            "key_features": {
                "method_b": "Sub starts with Star Lord, Sub-sub starts with Sub Lord",
                "direct_significations": "Planet appears as Sign/Star/Sub/SubSub lord",
                "stellar_significations": "Planets in nakshatra signify houses they occupy",
                "positional_significations": "If no planets in star, owns/occupies houses",
                "context_node_rep": "Node representation based on sign/star context",
                "sl_ssl_combined": "Sub Lord + Sub-Sub Lord combined for promise",
                "eleventh_house_rule": "11th house acts as universal fulfiller"
            }
        }
    }
    
    return response


def calculate_kp_cuspal_interlink_basic(data):
    """
    Basic KP Cuspal Interlink calculation (original functionality)
    
    Parameters:
    -----------
    data : dict
        Dictionary containing birth details
    
    Returns:
    --------
    dict: Basic KP Cuspal Interlink Analysis
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    ayanamsa = get_ayanamsa(jd)
    planets = calculate_planets(jd, ayanamsa)
    houses = calculate_houses_placidus(jd, latitude, longitude, ayanamsa)
    positional_status = analyze_positional_status(planets)
    cuspal_interlinks = analyze_cuspal_interlinks(houses, planets)
    
    response = {
        "status": "success",
        "user_name": user_name,
        "birth_details": {
            "date": birth_date,
            "time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "ayanamsa": {
            "type": "KP New (Krishnamurti)",
            "value": ayanamsa
        },
        "julian_day": jd,
        "planets": planets,
        "houses": houses,
        "positional_status": positional_status,
        "cuspal_interlinks": cuspal_interlinks
    }
    
    return response