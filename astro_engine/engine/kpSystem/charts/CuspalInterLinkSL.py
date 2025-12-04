"""
KP Cuspal Interlink - Calculation Module (Basic)
=================================================
Krishnamurti Paddhati (KP) Astrology - Basic Cuspal Interlink Analysis

Features:
- Complete 4-tier lordship: Sign, Star, Sub, Sub-Sub
- Positional Status (PS) analysis
- Cuspal interlink matrix
- House relationships (Favorable, Neutral, Adverse)
- Accurate retrograde detection
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
    
    # Rotate the sequence to start from nakshatra lord
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
    
    # Calculate sub divisions
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
    
    # Rotate sequence to start from sub lord
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
    """
    Calculate single planet position with proper speed and retrograde detection
    
    Swiss Ephemeris calc_ut returns:
    result = (xx, ret_flag)
    where xx = (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
    
    speed_long is in degrees per day
    """
    try:
        # Calculate with SWIEPH flag and SPEED flag (speed is default but we make it explicit)
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        calc_result = swe.calc_ut(jd, planet_id, flags)
        
        # Validate result
        if not calc_result or len(calc_result) < 1:
            raise ValueError(f"Invalid calculation result for {planet_name}")
        
        position_data = calc_result[0]
        
        if len(position_data) < 4:
            raise ValueError(f"Insufficient position data for {planet_name}")
        
        # Extract values
        # position_data[0] = longitude in degrees
        # position_data[3] = speed in longitude (degrees per day)
        tropical_long = float(position_data[0])
        speed_deg_per_day = float(position_data[3])
        
        return tropical_long, speed_deg_per_day
        
    except Exception as e:
        raise ValueError(f"Error calculating {planet_name}: {str(e)}")


def calculate_planets(jd, ayanamsa):
    """Calculate all planetary positions including Rahu/Ketu with accurate speed and retrograde detection"""
    planets_data = {}
    
    for planet_name in PLANET_NAMES:
        if planet_name == "Ketu":
            continue  # Calculate with Rahu
        
        try:
            planet_id = PLANETS[planet_name]
            
            # Calculate position and speed
            tropical_long, speed_deg_per_day = calculate_planet_position(jd, planet_id, planet_name)
            
            # Convert to sidereal
            sidereal_long = normalize_longitude(tropical_long - ayanamsa)
            
            # Determine retrograde status
            # A planet is retrograde when its speed in longitude is negative
            is_retrograde = speed_deg_per_day < 0
            
            # Get complete lordship
            lordship = get_complete_lordship(sidereal_long)
            
            planets_data[planet_name] = {
                "longitude": sidereal_long,
                "speed": round(speed_deg_per_day, 10),  # degrees per day
                "is_retrograde": is_retrograde,
                "retrograde_status": "Retrograde" if is_retrograde else "Direct",
                **lordship
            }
            
            # Calculate Ketu when processing Rahu
            if planet_name == "Rahu":
                # Ketu is always 180° opposite to Rahu
                ketu_long = normalize_longitude(sidereal_long + 180.0)
                
                # Ketu has same speed as Rahu but considered separately
                # Both Rahu and Ketu (mean nodes) move backwards, so speed is negative
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
    """Calculate house cusps using Placidus system"""
    try:
        # Use swe.houses() function
        # Returns tuple: (cusps, ascmc)
        # cusps: tuple with 12 elements (index 0-11 representing houses 1-12)
        # ascmc: tuple with 10 elements (0=Asc, 1=MC, 2=ARMC, 3=Vertex, etc.)
        
        houses_result = swe.houses(jd, latitude, longitude, b'P')
        
        # Validate result structure
        if not houses_result:
            raise ValueError("swe.houses() returned None")
        
        if not isinstance(houses_result, tuple) or len(houses_result) < 2:
            raise ValueError(f"swe.houses() returned invalid structure")
        
        cusps = houses_result[0]
        ascmc = houses_result[1]
        
        # Validate cusps - Swiss Ephemeris returns 12 elements (0-indexed)
        if not cusps:
            raise ValueError("Cusps is None or empty")
        
        if not isinstance(cusps, (tuple, list)):
            raise ValueError(f"Cusps is not a tuple/list")
        
        if len(cusps) < 12:
            raise ValueError(f"Cusps has insufficient elements: {len(cusps)}, expected 12")
        
        # Validate ascmc
        if not ascmc:
            raise ValueError("Ascmc is None or empty")
        
        if not isinstance(ascmc, (tuple, list)):
            raise ValueError(f"Ascmc is not a tuple/list")
        
        if len(ascmc) < 2:
            raise ValueError(f"Ascmc has insufficient elements: {len(ascmc)}, expected at least 2")
        
        # Convert houses to sidereal
        # cusps[0] = House 1, cusps[1] = House 2, ..., cusps[11] = House 12
        house_cusps = {}
        for i in range(12):
            house_num = i + 1
            tropical_cusp = cusps[i]
            sidereal_cusp = normalize_longitude(tropical_cusp - ayanamsa)
            lordship = get_complete_lordship(sidereal_cusp)
            
            house_cusps[house_num] = {
                "cusp_longitude": sidereal_cusp,
                **lordship
            }
        
        # Add Ascendant and MC
        ascendant_tropical = ascmc[0]
        mc_tropical = ascmc[1]
        
        asc_sidereal = normalize_longitude(ascendant_tropical - ayanamsa)
        mc_sidereal = normalize_longitude(mc_tropical - ayanamsa)
        
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


# ==============================================================================
# ANALYSIS FUNCTIONS
# ==============================================================================

def analyze_positional_status(planets_data):
    """
    Analyze Positional Status (PS) for each planet
    
    PS Factors:
    1. In own star - Planet is in a nakshatra it rules
    2. In own sub - Planet is in a sub-division it rules
    3. In own sub-sub - Planet is in a sub-sub-division it rules
    4. Untenanted nakshatras - No other planets occupy the nakshatras ruled by this planet
    5. Mutual star exchange - Planet A is in nakshatra ruled by Planet B, and Planet B is in nakshatra ruled by Planet A
    """
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
        
        # Factor 1: Check if in own star
        if data["star_lord"] == planet_name:
            ps_factors.append("In own star")
        
        # Factor 2: Check if in own sub
        if data["sub_lord"] == planet_name:
            ps_factors.append("In own sub")
        
        # Factor 3: Check if in own sub-sub
        if data["ssl"] == planet_name:
            ps_factors.append("In own sub-sub")
        
        # Factor 4: Check if no other planets in its ruled nakshatras (Untenanted)
        ruled_naks = [nak["name"] for nak in NAKSHATRAS if nak["lord"] == planet_name]
        untenanted = True
        for nak in ruled_naks:
            if nak in nak_occupancy and len(nak_occupancy[nak]) > 0:
                # Check if only this planet is there
                if not (len(nak_occupancy[nak]) == 1 and nak_occupancy[nak][0] == planet_name):
                    untenanted = False
                    break
        
        if untenanted and ruled_naks:
            ps_factors.append("Untenanted nakshatras")
        
        # Factor 5: Check for mutual star interchange
        # CRITICAL FIX: Ensure planet cannot have mutual exchange with itself
        star_lord = data["star_lord"]
        if star_lord != planet_name and star_lord in planets_data:
            # Check if star_lord's star_lord is the current planet
            if planets_data[star_lord]["star_lord"] == planet_name:
                ps_factors.append(f"Mutual star exchange with {star_lord}")
        
        ps_analysis[planet_name] = {
            "has_positional_status": len(ps_factors) > 0,
            "ps_factors": ps_factors,
            "strength": len(ps_factors)
        }
    
    return ps_analysis


def analyze_cuspal_interlinks(houses_data, planets_data):
    """Analyze cuspal interlinks between houses"""
    planet_cusp_links = {}
    
    for planet_name in PLANET_NAMES:
        links = {
            "as_sign_lord": [],
            "as_star_lord": [],
            "as_sub_lord": [],
            "as_sub_sub_lord": []
        }
        
        # Check each house cusp
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
    
    # Analyze house relationships (Favorable, Neutral, Adverse)
    house_relationships = {}
    for house_num in range(1, 13):
        relationships = {
            "favorable": [],  # 1, 3, 5, 9, 11 from this house
            "neutral": [],    # 2, 6, 10 from this house
            "adverse": []     # 4, 7, 8, 12 from this house
        }
        
        favorable_offsets = [1, 3, 5, 9, 11]
        neutral_offsets = [2, 6, 10]
        adverse_offsets = [4, 7, 8, 12]
        
        for offset in favorable_offsets:
            target = ((house_num + offset - 2) % 12) + 1
            relationships["favorable"].append(target)
        
        for offset in neutral_offsets:
            target = ((house_num + offset - 2) % 12) + 1
            relationships["neutral"].append(target)
        
        for offset in adverse_offsets:
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

def calculate_kp_cuspal_interlink_Sub(data):
    """
    Main function to calculate KP Cuspal Interlink (Basic)
    
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
    dict: Complete KP Cuspal Interlink Analysis
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    
    # Get Ayanamsa (KP New)
    ayanamsa = get_ayanamsa(jd)
    
    # Calculate planetary positions with accurate speeds
    planets = calculate_planets(jd, ayanamsa)
    
    # Calculate houses using Placidus
    houses = calculate_houses_placidus(jd, latitude, longitude, ayanamsa)
    
    # Analyze Positional Status
    positional_status = analyze_positional_status(planets)
    
    # Analyze Cuspal Interlinks
    cuspal_interlinks = analyze_cuspal_interlinks(houses, planets)
    
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