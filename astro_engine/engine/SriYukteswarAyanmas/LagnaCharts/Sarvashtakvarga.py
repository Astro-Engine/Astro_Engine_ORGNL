import os
import swisseph as swe
from datetime import datetime, timedelta
import logging

# ==========================================
# CONFIGURATION
# ==========================================
# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api/ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS
# ==========================================
# Zodiac signs (0-based index: 0=Aries, 11=Pisces)
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Planet codes for Swiss Ephemeris
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}

# Bindu allocation rules (1-based house numbers) for Bhinnashtakavarga
BINDU_RULES = {
    "Sun": {
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Jupiter": [5, 6, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Venus": [6, 7, 12],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Moon": [3, 6, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Sun": [3, 6, 7, 8, 10, 11],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Ascendant": [3, 6, 10, 11]
    },
    "Mars": {
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 10, 11, 12],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Sun": [3, 5, 6, 10, 11],
        "Venus": [6, 8, 11, 12],
        "Mercury": [3, 5, 6, 11],
        "Moon": [3, 6, 11],
        "Ascendant": [1, 3, 6, 10, 11]
    },
    "Mercury": {
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 8, 11, 12],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Sun": [5, 6, 9, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11]
    },
    "Venus": {
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Sun": [8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 11],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
    },
    "Jupiter": {
        "Saturn": [3, 5, 6, 12],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    "Saturn": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [5, 6, 11, 12],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Venus": [6, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Moon": [3, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11]
    },
    "Ascendant": {
        "Saturn": [1, 3, 4, 6, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Mars": [1, 3, 6, 10, 11],
        "Sun": [3, 4, 6, 10, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9],
        "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Moon": [3, 6, 10, 11, 12],
        "Ascendant": [3, 6, 10, 11]
    }
}

# Expected bindu totals for validation
EXPECTED_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_ayanamsa(jd):
    """Calculate Sri Yukteswar Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR)
    return swe.get_ayanamsa_ut(jd)

def calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet using Sri Yukteswar Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR)
    try:
        lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
        return lon % 360
    except Exception as e:
        logging.error(f"Error calculating longitude for planet code {planet_code}: {str(e)}")
        raise Exception(f"Failed to calculate longitude: {str(e)}")

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Sri Yukteswar Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR)
    try:
        house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
        return ascmc[0] % 360
    except Exception as e:
        logging.error(f"Error calculating ascendant: {str(e)}")
        raise Exception(f"Failed to calculate ascendant: {str(e)}")

def get_sign_index(longitude):
    """Get the 0-based sign index from longitude."""
    return int(longitude // 30) % 12

def format_dms(degrees):
    """Format degrees into degrees, minutes, seconds."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def calculate_relative_house(from_sign, to_sign):
    """Calculate the 1-based relative house from one sign to another."""
    return (to_sign - from_sign) % 12 + 1

def calculate_bhinnashtakavarga_matrix(positions):
    """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
    contributors = list(PLANETS.keys()) + ["Ascendant"]
    targets = list(PLANETS.keys())  # Only planets, not Ascendant
    bhinnashtakavarga = {target: [0] * 12 for target in targets}

    for target in targets:
        for contributor in contributors:
            if contributor not in positions:
                continue
            contributor_sign = positions[contributor]["sign_index"]
            rules = BINDU_RULES[target].get(contributor, [])
            for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
                relative_house = calculate_relative_house(contributor_sign, sign_idx)
                if relative_house in rules:
                    bhinnashtakavarga[target][sign_idx] += 1
    
    return bhinnashtakavarga

def calculate_sarvashtakavarga(bhinnashtakavarga):
    """Calculate Sarvashtakvarga by summing bindus from all Bhinnashtakavarga charts."""
    sarvashtakavarga = [0] * 12
    for planet in bhinnashtakavarga:
        for sign_idx in range(12):
            sarvashtakavarga[sign_idx] += bhinnashtakavarga[planet][sign_idx]
    return sarvashtakavarga

def map_to_houses(sarvashtakavarga, asc_sign_idx):
    """Map Sarvashtakvarga bindus to houses based on ascendant."""
    houses = {}
    for house in range(1, 13):
        sign_idx = (asc_sign_idx + house - 1) % 12
        houses[f"House {house}"] = sarvashtakavarga[sign_idx]
    return houses

def generate_matrix_table(sarvashtakavarga, asc_sign_idx):
    """Generate a matrix table for Sarvashtakvarga with signs and houses."""
    matrix = []
    for house in range(1, 13):
        sign_idx = (asc_sign_idx + house - 1) % 12
        matrix.append({
            "House": house,
            "Sign": SIGNS[sign_idx],
            "Bindus": sarvashtakavarga[sign_idx]
        })
    return matrix

def validate_totals(matrix):
    """Validate total bindus against expected values."""
    errors = []
    # Reconstruct totals from matrix structure
    # matrix passed here is bhinnashtakavarga dict
    # But validation logic in original script assumed a specific structure.
    # We will adapt validation to the calculated dictionary structure.
    for target, expected in EXPECTED_TOTALS.items():
        if target == "Ascendant": continue # Ascendant doesn't have a row in bhinnashtakavarga usually as a target
        if target not in matrix: continue
        
        total = sum(matrix[target])
        if total != expected:
            errors.append(f"{target}: {total} (expected {expected})")
    
    # Note: Original script had 'Ascendant' in expected totals but didn't calculate it as a target row 
    # in 'calculate_bhinnashtakavarga_matrix'. We adhere to the logic provided.
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))

def perform_sarvashtakavarga_calculation_cal(data):
    """
    Main logic function used by the API.
    Receives input dictionary, performs all calculations, returns result dictionary.
    """
    required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in data for key in required):
        raise ValueError("Missing required parameters")

    user_name = data['user_name']
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    tz_offset = float(data['timezone_offset'])

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude")

    # Calculate astronomical data
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    
    # Calculate Ayanamsa (Sri Yukteswar)
    ayanamsa = calculate_ayanamsa(jd)

    # Planetary positions (Sidereal Sri Yukteswar)
    positions = {}
    planet_positions = {}
    for planet, code in PLANETS.items():
        lon = calculate_sidereal_longitude(jd, code)
        sign_idx = get_sign_index(lon)
        positions[planet] = {"longitude": lon, "sign_index": sign_idx}
        sign_deg = lon % 30
        planet_positions[planet] = {"sign": SIGNS[sign_idx], "degrees": format_dms(sign_deg)}

    # Ascendant (Sidereal Sri Yukteswar)
    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign = get_sign_index(asc_lon)
    positions["Ascendant"] = {"longitude": asc_lon, "sign_index": asc_sign}
    asc_deg = asc_lon % 30

    # Calculate Bhinnashtakavarga
    bhinnashtakavarga_matrix = calculate_bhinnashtakavarga_matrix(positions)
    validate_totals(bhinnashtakavarga_matrix)

    # Format Bhinnashtakavarga for response
    bhinnashtakavarga_formatted = {
        planet: {SIGNS[i]: bindus[i] for i in range(12)}
        for planet, bindus in bhinnashtakavarga_matrix.items()
    }

    # Format response with detailed tables (Breakdown by contributor)
    # Re-logic needed to match the nested structure of original script's response
    # The matrix calculation function above returns [target][sign_idx] = total points
    # But the original script had a detailed breakdown structure. 
    # We must replicate the inner loop logic to generate the 'tables' list correctly.
    
    planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ascendant"]
    # Targets for the table only include the 7 planets (Ascendant is contributor, not target in standard AV)
    targets_for_table = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    tables = []
    for target in targets_for_table:
        target_data_breakdown = []
        total_bindus = [0] * 12
        
        for contributor in planet_order:
            if contributor not in positions: continue
            
            contributor_sign = positions[contributor]["sign_index"]
            bindus = [0] * 12
            
            for sign_idx in range(12):
                relative_house = calculate_relative_house(contributor_sign, sign_idx)
                if relative_house in BINDU_RULES[target][contributor]:
                    bindus[sign_idx] = 1
                    total_bindus[sign_idx] += 1
            
            target_data_breakdown.append({"contributor": contributor, "bindus": bindus})
            
        tables.append({
            "planet": target,
            "contributors": target_data_breakdown,
            "total_bindus": total_bindus
        })

    # Calculate Sarvashtakvarga
    sarvashtakavarga = calculate_sarvashtakavarga(bhinnashtakavarga_matrix)

    # Map Sarvashtakvarga to houses
    houses = map_to_houses(sarvashtakavarga, asc_sign)

    # Generate matrix table for Sarvashtakvarga
    matrix_table = generate_matrix_table(sarvashtakavarga, asc_sign)

    response = {
        "user_name": user_name,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": tz_offset
        },
        "planetary_positions": planet_positions,
        "ascendant": {"sign": SIGNS[asc_sign], "degrees": format_dms(asc_deg)},
        "bhinnashtakavarga": bhinnashtakavarga_formatted,
        "sarvashtakavarga": {
            "signs": {SIGNS[i]: sarvashtakavarga[i] for i in range(12)},
            "houses": houses,
            "matrix_table": matrix_table
        },
        "ashtakvarga": {
            "system": "Bhinnashtakavarga",
            "tables": tables
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa:.6f}",
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        },
        "debug": {
            "julian_day": jd,
            "ayanamsa": f"{ayanamsa:.6f}"
        }
    }
    
    return response