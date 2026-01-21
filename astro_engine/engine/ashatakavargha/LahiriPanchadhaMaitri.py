import os
import math
import swisseph as swe

# =============================================================================
# CONFIGURATION
# =============================================================================

# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api/ephe')
swe.set_ephe_path(EPHE_PATH)

# Planet Mapping for Swiss Ephemeris
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": "KETU_CALC" # Custom key for Ketu calculation
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# =============================================================================
# NATURAL RELATIONSHIPS (NAISARGIKA MAITRI)
# Standard Parashara rules used in Lahiri System
# =============================================================================
NATURAL_RELATIONSHIPS = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "neutrals": ["Mercury"],
        "enemies": ["Venus", "Saturn", "Rahu", "Ketu"]
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"],
        "enemies": ["Rahu", "Ketu"] 
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter", "Ketu"],
        "neutrals": ["Venus", "Saturn"],
        "enemies": ["Mercury", "Rahu"]
    },
    "Mercury": {
        "friends": ["Sun", "Venus"], 
        "neutrals": ["Mars", "Jupiter", "Saturn", "Ketu", "Rahu"],
        "enemies": ["Moon"]
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "neutrals": ["Saturn", "Rahu", "Ketu"], 
        "enemies": ["Mercury", "Venus"]
    },
    "Venus": {
        "friends": ["Mercury", "Saturn", "Rahu", "Ketu"],
        "neutrals": ["Mars", "Jupiter"],
        "enemies": ["Sun", "Moon"]
    },
    "Saturn": {
        "friends": ["Mercury", "Venus"], 
        "neutrals": ["Jupiter", "Rahu"], 
        "enemies": ["Sun", "Moon", "Mars", "Ketu"] 
    },
    "Rahu": {
        "friends": ["Venus", "Jupiter"],
        "neutrals": ["Mercury", "Saturn"], 
        "enemies": ["Sun", "Moon", "Ketu", "Mars"] 
    },
    "Ketu": {
        "friends": ["Mars", "Venus"], 
        "neutrals": ["Mercury", "Jupiter"], 
        "enemies": ["Sun", "Moon", "Rahu", "Saturn"] 
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def decimal_to_dms(deg_float):
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def normalize_degrees(degree):
    return degree % 360

def get_julian_day(date_str, time_str, tz_offset):
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(float, time_str.split(':'))
    
    # Decimal hour in local time
    decimal_hour_local = hour + (minute / 60.0) + (second / 3600.0)
    
    # Convert to UTC
    decimal_hour_utc = decimal_hour_local - float(tz_offset)
    
    # Calculate JD
    jd = swe.julday(year, month, day, decimal_hour_utc)
    return jd

def get_planet_position_sidereal(jd, planet_id):
    """
    Get planet longitude using LAHIRI Ayanamsa.
    """
    # Flags: Ephemeris + Sidereal + Speed
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    try:
        results = swe.calc_ut(jd, planet_id, flags)
        longitude = results[0][0]
        return longitude
    except swe.Error as e:
        return 0.0

def calculate_compound_relationship(natural, temporary):
    """
    Apply the 5-Fold Compound Relationship Logic.
    """
    # 1. Great Friend (Adhi Mitra)
    if natural == "Friend" and temporary == "Friend":
        return "Great Friend"
    
    # 2. Friend (Mitra)
    if natural == "Neutral" and temporary == "Friend":
        return "Friend"
    
    # 3. Neutral (Sama) - Two ways to get this
    if (natural == "Friend" and temporary == "Enemy") or \
       (natural == "Enemy" and temporary == "Friend"):
        return "Neutral"
    
    # 4. Enemy (Shatru)
    if natural == "Neutral" and temporary == "Enemy":
        return "Enemy"
    
    # 5. Great Enemy (Adhi Shatru)
    if natural == "Enemy" and temporary == "Enemy":
        return "Great Enemy"
        
    return "Unknown"

def perform_panchadha_maitri_calculation_lahiri(data):
    """
    Main logic function used by the API.
    """
    # 1. Initialize Swiss Ephemeris
    swe.set_ephe_path(EPHE_PATH)
    
    # ---------------------------------------------------------
    # SET AYANAMSA: LAHIRI (CHITRA PAKSHA)
    # swisseph constant for Lahiri is 1 (swe.SIDM_LAHIRI)
    # ---------------------------------------------------------
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # 2. Parse Input Data
    user_name = data.get('user_name', 'User')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    tz_offset = data.get('timezone_offset', 5.5) # Default to IST

    # 3. Time Calculation
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # 4. Calculate Planetary Positions & Signs
    planet_data = {}
    
    for p_name, p_id in PLANETS.items():
        if p_name == "Ketu":
            # Ketu is exactly opposite Rahu
            rahu_long = planet_data["Rahu"]["longitude"]
            long = normalize_degrees(rahu_long + 180)
        else:
            long = get_planet_position_sidereal(jd, p_id)
        
        # Determine Sign (Whole Sign System)
        sign_index = int(long / 30) # 0=Aries, 1=Taurus, etc.
        sign_name = ZODIAC_SIGNS[sign_index]
        degree_in_sign = long % 30
        
        planet_data[p_name] = {
            "longitude": long,
            "sign_index": sign_index, 
            "sign_name": sign_name,
            "degree_fmt": decimal_to_dms(degree_in_sign)
        }

    # 5. Generate Panchadha Maitri Matrix
    maitri_report = {}

    for source_planet in PLANETS.keys():
        source_info = planet_data[source_planet]
        relations = []
        
        for target_planet in PLANETS.keys():
            if source_planet == target_planet:
                continue
            
            target_info = planet_data[target_planet]
            
            # --- Step A: Get Natural Relationship ---
            nat_rel = "Neutral" # Default fallback
            if target_planet in NATURAL_RELATIONSHIPS[source_planet]["friends"]:
                nat_rel = "Friend"
            elif target_planet in NATURAL_RELATIONSHIPS[source_planet]["enemies"]:
                nat_rel = "Enemy"
            
            # --- Step B: Get Temporary Relationship ---
            # Formula: Count from Source Sign to Target Sign (inclusive)
            # Example: Source Aries(0), Target Gemini(2). Diff = (2-0)+1 = 3rd House
            diff = (target_info['sign_index'] - source_info['sign_index']) + 1
            if diff <= 0:
                diff += 12
            
            # Tatkalika Rules for Lahiri/Parashara:
            # Friend: 2, 3, 4, 10, 11, 12
            # Enemy: 1 (Conjunct), 5, 6, 7, 8, 9
            if diff in [2, 3, 4, 10, 11, 12]:
                tat_rel = "Friend"
            else:
                tat_rel = "Enemy"
            
            # --- Step C: Combine for Compound Result ---
            final_label = calculate_compound_relationship(nat_rel, tat_rel)
            
            relations.append({
                "planet": target_planet,
                "position_diff": f"{diff}th House",
                "natural": nat_rel,
                "temporary": tat_rel,
                "compound": final_label
            })
        
        maitri_report[source_planet] = {
            "current_sign": source_info['sign_name'],
            "longitude": f"{source_info['longitude']:.2f}",
            "relations": relations
        }

    # 6. Construct Final Response
    response = {
        "meta": {
            "user": user_name,
            "system": "Lahiri (Chitra Paksha) Ayanamsa",
            "house_system": "Whole Sign",
            "ayanamsa_value": f"{swe.get_ayanamsa_ut(jd):.4f}"
        },
        "maitri_chakra": maitri_report
    }
    
    return response