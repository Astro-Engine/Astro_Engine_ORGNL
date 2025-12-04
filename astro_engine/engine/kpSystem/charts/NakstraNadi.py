"""
KP Nakshatra Nadi - Calculation Module
=======================================
Krishnamurti Paddhati (KP) Astrology - Nakshatra and Sub-Lord Calculations
Multi-Ayanamsa Support with Arc-Second Precision

Features:
- Multiple KP Ayanamsa variants (kp_old, kp_new, kp_new_lahiri)
- Boundary tolerance handling (5 arc seconds)
- Sub-lord calculation with boundary warnings
- Pada calculation
- DMS formatting
"""

from datetime import datetime, timedelta
import swisseph as swe

# ==============================================================================
# CONSTANTS
# ==============================================================================

# Static Nakshatra Data
NAKSHATRAS = [
    {"num": 1, "name": "Ashwini", "lord": "Ketu", "start": 0.0},
    {"num": 2, "name": "Bharani", "lord": "Venus", "start": 13.333333333333334},
    {"num": 3, "name": "Krittika", "lord": "Sun", "start": 26.666666666666668},
    {"num": 4, "name": "Rohini", "lord": "Moon", "start": 40.0},
    {"num": 5, "name": "Mrigashira", "lord": "Mars", "start": 53.333333333333336},
    {"num": 6, "name": "Ardra", "lord": "Rahu", "start": 66.66666666666667},
    {"num": 7, "name": "Punarvasu", "lord": "Jupiter", "start": 80.0},
    {"num": 8, "name": "Pushya", "lord": "Saturn", "start": 93.33333333333333},
    {"num": 9, "name": "Ashlesha", "lord": "Mercury", "start": 106.66666666666667},
    {"num": 10, "name": "Magha", "lord": "Ketu", "start": 120.0},
    {"num": 11, "name": "Purva Phalguni", "lord": "Venus", "start": 133.33333333333334},
    {"num": 12, "name": "Uttara Phalguni", "lord": "Sun", "start": 146.66666666666666},
    {"num": 13, "name": "Hasta", "lord": "Moon", "start": 160.0},
    {"num": 14, "name": "Chitra", "lord": "Mars", "start": 173.33333333333334},
    {"num": 15, "name": "Swati", "lord": "Rahu", "start": 186.66666666666666},
    {"num": 16, "name": "Vishakha", "lord": "Jupiter", "start": 200.0},
    {"num": 17, "name": "Anuradha", "lord": "Saturn", "start": 213.33333333333334},
    {"num": 18, "name": "Jyeshtha", "lord": "Mercury", "start": 226.66666666666666},
    {"num": 19, "name": "Mula", "lord": "Ketu", "start": 240.0},
    {"num": 20, "name": "Purva Ashadha", "lord": "Venus", "start": 253.33333333333334},
    {"num": 21, "name": "Uttara Ashadha", "lord": "Sun", "start": 266.6666666666667},
    {"num": 22, "name": "Shravana", "lord": "Moon", "start": 280.0},
    {"num": 23, "name": "Dhanishta", "lord": "Mars", "start": 293.3333333333333},
    {"num": 24, "name": "Shatabhisha", "lord": "Rahu", "start": 306.6666666666667},
    {"num": 25, "name": "Purva Bhadrapada", "lord": "Jupiter", "start": 320.0},
    {"num": 26, "name": "Uttara Bhadrapada", "lord": "Saturn", "start": 333.3333333333333},
    {"num": 27, "name": "Revati", "lord": "Mercury", "start": 346.6666666666667}
]

# Vimshottari Dasha periods
VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

NAKSHATRA_SPAN_DEGREES = 360.0 / 27.0
NAKSHATRA_SPAN_MINUTES = 800.0
TOTAL_DASHA_YEARS = 120

# Calculate sub-spans
SUB_SPANS = {}
for planet, years in VIMSHOTTARI_YEARS.items():
    minutes = (years / TOTAL_DASHA_YEARS) * NAKSHATRA_SPAN_MINUTES
    degrees = minutes / 60.0
    SUB_SPANS[planet] = {"minutes": minutes, "degrees": degrees, "years": years}

# Planet mappings
PLANET_NUMBERS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Rahu": swe.TRUE_NODE
}

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# BOUNDARY TOLERANCE (in degrees) - Critical for accuracy
BOUNDARY_TOLERANCE = 0.0013888888  # 5 arc seconds = 0.0013888° 


# ==============================================================================
# AYANAMSA CALCULATIONS
# ==============================================================================

def calculate_kp_ayanamsa(jd, ayanamsa_type="kp_new"):
    """
    Calculate different KP Ayanamsa variants
    
    Parameters:
    - jd: Julian Day
    - ayanamsa_type: "kp_old", "kp_new", "kp_new_lahiri"
    """ 
    
    if ayanamsa_type == "kp_old":
        # Original KP (Krishnamurti) - Most widely used
        epoch_jd = 2415020.0
        epoch_ayanamsa = 22.46  # 22°27'36"
        annual_rate = 50.2388475 / 3600.0
        
    elif ayanamsa_type == "kp_new":
        # KP New (adjusted epoch)
        epoch_jd = 2415020.0
        epoch_ayanamsa = 22.363888889  # 22°21'50" - Adjusted base
        annual_rate = 50.2388475 / 3600.0
        
    elif ayanamsa_type == "kp_new_lahiri":
        # KP with Lahiri base (some software use this)
        epoch_jd = 2415020.0
        epoch_ayanamsa = 22.46416667  # 22°27'51"
        annual_rate = 50.26 / 3600.0
        
    else:  # Default to kp_old
        epoch_jd = 2415020.0
        epoch_ayanamsa = 22.46
        annual_rate = 50.2388475 / 3600.0
    
    years_from_epoch = (jd - epoch_jd) / 365.25
    ayanamsa = epoch_ayanamsa + (years_from_epoch * annual_rate)
    
    return ayanamsa


# ==============================================================================
# SUB-LORD CALCULATIONS
# ==============================================================================

def get_sub_lord_sequence(nakshatra_lord):
    """Get 9 sub-lord sequence starting from nakshatra lord"""
    try:
        start_index = VIMSHOTTARI_ORDER.index(nakshatra_lord)
    except ValueError:
        start_index = 0
    
    return [(VIMSHOTTARI_ORDER[(start_index + i) % 9]) for i in range(9)]


def calculate_sub_lord_with_boundary_check(longitude):
    """
    Calculate sub-lord with proper boundary handling
    
    Uses arc-second precision and boundary tolerance
    """
    longitude = longitude % 360.0
    
    # Find nakshatra
    nakshatra_index = int(longitude / NAKSHATRA_SPAN_DEGREES)
    if nakshatra_index >= 27:
        nakshatra_index = 26
    
    nakshatra = NAKSHATRAS[nakshatra_index]
    
    # Position within nakshatra (with high precision)
    position_in_nakshatra_degrees = longitude - nakshatra['start']
    position_in_nakshatra_minutes = position_in_nakshatra_degrees * 60.0
    
    # Round to arc-second precision (critical for boundary cases)
    position_in_nakshatra_minutes = round(position_in_nakshatra_minutes * 60) / 60.0
    position_in_nakshatra_degrees = position_in_nakshatra_minutes / 60.0
    
    # Get sub-lord sequence
    sub_sequence = get_sub_lord_sequence(nakshatra['lord'])
    
    # Find sub-lord with boundary tolerance
    cumulative_minutes = 0.0
    sub_lord = sub_sequence[0]
    sub_number = 1
    boundary_warning = False
    
    for i, planet in enumerate(sub_sequence):
        sub_span_minutes = SUB_SPANS[planet]["minutes"]
        next_boundary = cumulative_minutes + sub_span_minutes
        
        # Check if within tolerance of boundary
        distance_from_start = abs(position_in_nakshatra_minutes - cumulative_minutes)
        distance_from_end = abs(position_in_nakshatra_minutes - next_boundary)
        
        if distance_from_start < (BOUNDARY_TOLERANCE * 60) or distance_from_end < (BOUNDARY_TOLERANCE * 60):
            boundary_warning = True
        
        if position_in_nakshatra_minutes < next_boundary:
            sub_lord = planet
            sub_number = i + 1
            break
        
        cumulative_minutes = next_boundary
    
    # Calculate pada
    pada_span = NAKSHATRA_SPAN_DEGREES / 4.0
    pada = int(position_in_nakshatra_degrees / pada_span) + 1
    if pada > 4:
        pada = 4
    
    # Sign and degree
    sign_number = int(longitude / 30.0) + 1
    if sign_number > 12:
        sign_number = 1
    
    degree_in_sign = longitude % 30.0
    
    # Convert to DMS
    deg = int(degree_in_sign)
    min_val = int((degree_in_sign - deg) * 60)
    sec = ((degree_in_sign - deg) * 60 - min_val) * 60
    
    result = {
        "longitude": round(longitude, 6),
        "sign_number": sign_number,
        "sign_name": SIGN_NAMES[sign_number - 1],
        "degree_in_sign": round(degree_in_sign, 6),
        "position_dms": f"{deg}° {min_val}' {sec:.2f}\"",
        "nakshatra_number": nakshatra['num'],
        "nakshatra_name": nakshatra['name'],
        "nakshatra_lord": nakshatra['lord'],
        "pada": pada,
        "sub_lord": sub_lord,
        "sub_number": sub_number,
        "position_in_nakshatra": round(position_in_nakshatra_degrees, 6),
        "boundary_warning": boundary_warning
    }
    
    return result


# ==============================================================================
# PLANETARY CALCULATIONS
# ==============================================================================

def calculate_planetary_positions(jd, ayanamsa):
    """Calculate positions of all planets with retrograde status"""
    planets_data = {}
    
    for planet_name in PLANET_NAMES:
        if planet_name == "Ketu":
            if "Rahu" in planets_data:
                rahu_long = planets_data["Rahu"]["longitude"]
                ketu_long = (rahu_long + 180.0) % 360.0
                
                ketu_details = calculate_sub_lord_with_boundary_check(ketu_long)
                ketu_details["is_retrograde"] = True
                ketu_details["speed"] = -planets_data["Rahu"]["speed"]
                
                planets_data["Ketu"] = ketu_details
        else:
            planet_num = PLANET_NUMBERS[planet_name]
            
            try:
                result = swe.calc_ut(jd, planet_num, swe.FLG_SPEED)
                
                tropical_long = result[0][0]
                speed = result[0][3]
                
                sidereal_long = (tropical_long - ayanamsa) % 360.0
                is_retrograde = speed < 0
                
                planet_details = calculate_sub_lord_with_boundary_check(sidereal_long)
                planet_details["is_retrograde"] = is_retrograde
                planet_details["speed"] = round(speed, 6)
                
                planets_data[planet_name] = planet_details
                
            except Exception as e:
                planets_data[planet_name] = {"error": f"Calculation failed: {str(e)}"}
    
    return planets_data


# ==============================================================================
# HOUSE CALCULATIONS
# ==============================================================================

def calculate_houses_placidus(jd, lat, lon, ayanamsa):
    """Calculate house cusps using Placidus system"""
    houses_data = {}
    
    try:
        houses_result = swe.houses(jd, lat, lon, b'P')
        cusps_tropical = houses_result[0]
        ascmc = houses_result[1]
        
        for i in range(1, 13):
            if i < len(cusps_tropical):
                tropical_cusp = cusps_tropical[i]
                sidereal_cusp = (tropical_cusp - ayanamsa) % 360.0
                
                cusp_details = calculate_sub_lord_with_boundary_check(sidereal_cusp)
                houses_data[f"House_{i}"] = cusp_details
        
        if len(ascmc) > 0:
            tropical_asc = ascmc[0]
            sidereal_asc = (tropical_asc - ayanamsa) % 360.0
            houses_data["Ascendant"] = calculate_sub_lord_with_boundary_check(sidereal_asc)
        
        if len(ascmc) > 1:
            tropical_mc = ascmc[1]
            sidereal_mc = (tropical_mc - ayanamsa) % 360.0
            houses_data["MC"] = calculate_sub_lord_with_boundary_check(sidereal_mc)
        
    except Exception as e:
        houses_data["error"] = f"House calculation failed: {str(e)}"
    
    return houses_data


# ==============================================================================
# TIME CONVERSION FUNCTIONS
# ==============================================================================

def convert_to_utc(birth_date, birth_time, timezone_offset):
    """Convert local time to UTC"""
    year, month, day = map(int, birth_date.split('-'))
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    local_dt = datetime(year, month, day, hour, minute, second)
    utc_dt = local_dt - timedelta(hours=timezone_offset)
    
    return utc_dt


def calculate_julian_day(dt_utc):
    """Calculate Julian Day from UTC datetime"""
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)
    return jd


# ==============================================================================
# INFORMATION FUNCTIONS
# ==============================================================================

def get_all_ayanamsa_info():
    """Get information about all KP ayanamsa variants"""
    current_jd = swe.julday(2025, 1, 1, 0)
    
    variants = {}
    for ayanamsa_type in ["kp_old", "kp_new", "kp_new_lahiri"]:
        variants[ayanamsa_type] = {
            "value_2025": round(calculate_kp_ayanamsa(current_jd, ayanamsa_type), 6),
            "description": {
                "kp_old": "Original Krishnamurti (Most Compatible)",
                "kp_new": "KP New with adjusted base",
                "kp_new_lahiri": "KP with Lahiri base"
            }[ayanamsa_type]
        }
    
    return {
        "available_ayanamsas": variants,
        "recommended": "kp_old",
        "note": "Use 'kp_old' for maximum compatibility with most KP software"
    }


def get_all_nakshatra_info():
    """Get all nakshatra information"""
    nakshatra_list = []
    
    for nak in NAKSHATRAS:
        sub_sequence = get_sub_lord_sequence(nak['lord'])
        
        nakshatra_list.append({
            "number": nak['num'],
            "name": nak['name'],
            "lord": nak['lord'],
            "start_degree": round(nak['start'], 6),
            "end_degree": round(nak['start'] + NAKSHATRA_SPAN_DEGREES, 6),
            "span_degrees": round(NAKSHATRA_SPAN_DEGREES, 6),
            "span_dms": "13° 20' 00\"",
            "sub_lord_sequence": sub_sequence
        })
    
    return {
        "total_nakshatras": 27,
        "nakshatra_span_degrees": round(NAKSHATRA_SPAN_DEGREES, 6),
        "nakshatra_span_minutes": NAKSHATRA_SPAN_MINUTES,
        "nakshatras": nakshatra_list
    }


def get_sub_lord_info():
    """Get sub-lord division information"""
    sub_info = []
    
    for planet in VIMSHOTTARI_ORDER:
        data = SUB_SPANS[planet]
        
        deg = int(data['degrees'])
        min_val = int((data['degrees'] - deg) * 60)
        sec = ((data['degrees'] - deg) * 60 - min_val) * 60
        
        sub_info.append({
            "planet": planet,
            "dasha_years": data['years'],
            "proportion": f"{data['years']}/120",
            "sub_span_degrees": round(data['degrees'], 6),
            "sub_span_minutes": round(data['minutes'], 6),
            "sub_span_dms": f"{deg}° {min_val}' {sec:.2f}\""
        })
    
    return {
        "total_dasha_cycle_years": TOTAL_DASHA_YEARS,
        "subs_per_nakshatra": 9,
        "vimshottari_order": VIMSHOTTARI_ORDER,
        "sub_divisions": sub_info,
        "boundary_tolerance": f"{BOUNDARY_TOLERANCE * 3600} arc seconds"
    }


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_kp_chart(data):
    """
    Main function to calculate complete KP chart
    
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
        - ayanamsa_type: str (optional, default='kp_old')
    
    Returns:
    --------
    dict: Complete KP chart with planets and houses
    """
    # Extract parameters
    user_name = data.get('user_name', '')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    # Ayanamsa selection (default to kp_old for maximum compatibility)
    ayanamsa_type = data.get('ayanamsa_type', 'kp_old')
    
    # Convert to UTC
    utc_dt = convert_to_utc(birth_date, birth_time, timezone_offset)
    
    # Calculate Julian Day
    jd = calculate_julian_day(utc_dt)
    
    # Calculate KP ayanamsa
    ayanamsa = calculate_kp_ayanamsa(jd, ayanamsa_type)
    
    # Calculate planetary positions
    planets = calculate_planetary_positions(jd, ayanamsa)
    
    # Calculate houses
    houses = calculate_houses_placidus(jd, latitude, longitude, ayanamsa)
    
    # Build response
    response = {
        "status": "success",
        "user_info": {
            "name": user_name,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "timezone_offset": timezone_offset
        },
        "calculation_details": {
            "utc_datetime": utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "julian_day": round(jd, 6),
            "ayanamsa": round(ayanamsa, 6),
            "ayanamsa_type": f"KP {ayanamsa_type.replace('_', ' ').title()}",
            "house_system": "Placidus",
            "zodiac_type": "Sidereal",
            "boundary_tolerance_arcsec": 5
        },
        "planets": planets,
        "houses": houses
    }
    
    return response