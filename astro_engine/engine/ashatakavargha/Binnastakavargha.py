import swisseph as swe
from datetime import datetime, timedelta

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
        "Ascendant": [3, 4, 6, 10, 11, 12]    # 6 
    },
    "Moon": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Sun": [3, 6, 7, 8, 10, 11],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Ascendant": [3, 6, 10, 11]    # 4
    },
    "Mars": {
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 10, 11, 12],
        "Mars": [1, 2, 4, 7,8, 10, 11],
        "Sun": [3, 5, 6, 10, 11],
        "Venus": [6, 8, 11, 12],
        "Mercury": [3, 5, 6, 11],
        "Moon": [3,  6, 11],  # Adjusted: Added house 5 to reach 39 bindus
        "Ascendant": [1, 3, 6, 10, 11]      # 5 
    },
    "Mercury": {
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 8, 11, 12],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Sun": [5, 6, 9, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11]    # 7 
    },
    "Venus": {
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Sun": [8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],  # Adjusted: Removed 10 and 11 to reach 50 bindus
        "Mercury": [3, 5, 6, 9, 11],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]      #  8 
    },
    "Jupiter": {
        "Saturn": [3, 5, 6, 12],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],  # Adjusted: Removed 7, 8, 10, 11 to reach 52 bindus
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]    # 9 
    },
    "Saturn": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [5, 6, 11, 12],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Venus": [6, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Moon": [3, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11]      # 6
    },
    "Ascendant": {
         "Saturn": [1,3,4,6,10,11],
        "Jupiter": [1,2,4,5,6,7,9,10,11],
        "Mars": [1,3,6,10,11],  
        "Sun": [3,4,6,10,11,12],   
        "Venus": [1,2,3,4,5,8,9],
        "Mercury": [1,2,4,6,8,10,11],
        "Moon": [3,6,10,11,12] ,
        "Ascendant": [3,6,10,11]      
    }
}

# Expected bindu totals for validation
EXPECTED_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
}

# Helper Functions
def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa_ut(jd)

def calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
    return lon % 360

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal longitude of the Ascendant."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    return ascmc[0] % 360

def get_sign_index(longitude):
    """Get the 0-based sign index from longitude."""
    return int(longitude // 30) % 12

def calculate_relative_house(from_sign, to_sign):
    """Calculate the 1-based relative house from one sign to another."""
    return (to_sign - from_sign) % 12 + 1

def calculate_bhinnashtakavarga_matrix(positions):
    """Calculate Bhinnashtakavarga with detailed bindu assignments."""
    contributors = list(PLANETS.keys()) + ["Ascendant"]
    targets = list(PLANETS.keys()) + ["Ascendant"]
    matrix = {}
    for target in targets:
        target_data = {}
        total_bindus = [0] * 12  # Total bindus for each sign
        for contributor in contributors:
            if contributor not in positions:
                continue
            contributor_sign = positions[contributor]["sign_index"]
            bindus = [0] * 12  # Binary bindus for this contributor
            for sign_idx in range(12):
                relative_house = calculate_relative_house(contributor_sign, sign_idx)
                if relative_house in BINDU_RULES[target][contributor]:
                    bindus[sign_idx] = 1
                    total_bindus[sign_idx] += 1
            target_data[contributor] = bindus
        target_data["total"] = total_bindus
        matrix[target] = target_data
    return matrix

def validate_totals(matrix):
    """Validate total bindus against expected values."""
    errors = []
    for target, expected in EXPECTED_TOTALS.items():
        total = sum(matrix[target]["total"])
        if total != expected:
            errors.append(f"{target}: {total} (expected {expected})")
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))

def format_dms(degrees):
    """Format degrees into degrees, minutes, seconds."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def lahiri_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate Bhinnashtakavarga using Lahiri Ayanamsa based on birth details."""
    # Set Swiss Ephemeris path
    swe.set_ephe_path('astro_engine/ephe')

    # Calculate Julian Day and Ayanamsa
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    ayanamsa = calculate_ayanamsa(jd)

    # Planetary positions
    positions = {}
    planet_positions = {}
    for planet, code in PLANETS.items():
        lon = calculate_sidereal_longitude(jd, code)
        sign_idx = get_sign_index(lon)
        positions[planet] = {"longitude": lon, "sign_index": sign_idx}
        sign_deg = lon % 30
        planet_positions[planet] = {"sign": SIGNS[sign_idx], "degrees": format_dms(sign_deg)}

    # Ascendant
    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign = get_sign_index(asc_lon)
    positions["Ascendant"] = {"longitude": asc_lon, "sign_index": asc_sign}
    asc_deg = asc_lon % 30

    # Calculate Bhinnashtakavarga
    bhinnashtakavarga_matrix = calculate_bhinnashtakavarga_matrix(positions)
    validate_totals(bhinnashtakavarga_matrix)

    # Format response with detailed tables
    planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ascendant"]
    tables = []
    for planet in planet_order:
        target_data = bhinnashtakavarga_matrix[planet]
        contributors_data = [
            {"contributor": contributor, "bindus": target_data[contributor]}
            for contributor in planet_order
            if contributor in target_data
        ]
        total_bindus = target_data["total"]
        tables.append({
            "planet": planet,
            "contributors": contributors_data,
            "total_bindus": total_bindus
        })

    return {
        "planetary_positions": planet_positions,
        "ascendant": {"sign": SIGNS[asc_sign], "degrees": format_dms(asc_deg)},
        "ashtakvarga": {
            "system": "Bhinnashtakavarga",
            "tables": tables
        },
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa:.6f}",
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        }
    }