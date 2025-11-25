import swisseph as swe
from datetime import datetime, timedelta
# import logging

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

# Favorable house rules for each planet from each factor (1-based)
FAVORABLE_HOUSES = {
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

# Helper Functions
def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    # logging.debug(f"Julian Day: {jd}")
    return jd

def calculate_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    # logging.debug(f"Ayanamsa: {ayanamsa:.6f}")
    return ayanamsa

def calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    try:
        lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
        return lon % 360
    except Exception as e:
        # logging.error(f"Error calculating longitude for planet code {planet_code}: {str(e)}")
        raise Exception(f"Failed to calculate longitude: {str(e)}")

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    try:
        house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
        return ascmc[0] % 360
    except Exception as e:
        # logging.error(f"Error calculating ascendant: {str(e)}")
        raise Exception(f"Failed to calculate ascendant: {str(e)}")

def get_sign_index(longitude):
    """Convert longitude to 0-based sign index (0=Aries, 11=Pisces)."""
    return int(longitude // 30) % 12

def format_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds."""
    deg = int(degrees)
    minutes = int((degrees - deg) * 60)
    seconds = int(((degrees - deg) * 60 - minutes) * 60)
    return f"{deg}° {minutes}' {seconds}\""

def calculate_relative_house(from_sign, to_sign):
    """Calculate the relative house from one sign to another (1-based)."""
    return (to_sign - from_sign) % 12 + 1

def calculate_bhinnashtakavarga_matrix(positions):
    """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
    contributors = list(PLANETS.keys()) + ["Ascendant"]
    targets = list(PLANETS.keys())  # Only planets, not Ascendant
    bhinnashtakavarga = {target: [0] * 12 for target in targets}

    for target in targets:
        for contributor in contributors:
            if contributor not in positions:
                # logging.warning(f"Contributor {contributor} not found in positions, skipping.")
                continue
            contributor_sign = positions[contributor]["sign_index"]
            rules = FAVORABLE_HOUSES[target].get(contributor, [])
            for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
                relative_house = calculate_relative_house(contributor_sign, sign_idx)
                if relative_house in rules:
                    bhinnashtakavarga[target][sign_idx] += 1
                    # logging.debug(f"Assigned bindu to {target} in {SIGNS[sign_idx]} from {contributor} (house {relative_house})")
    
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

# def lahiri_sarvathakavargha(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate Sarvashtakavarga using Lahiri Ayanamsa based on birth details."""
#     # Calculate Julian Day and Ayanamsa
#     jd = get_julian_day(birth_date, birth_time, tz_offset)
#     ayanamsa = calculate_ayanamsa(jd)

#     # Calculate planetary positions and Ascendant
#     positions = {}
#     planet_positions = {}
#     for planet in PLANETS:
#         lon = calculate_sidereal_longitude(jd, PLANETS[planet])
#         sign_idx = get_sign_index(lon)
#         positions[planet] = {
#             "longitude": lon,
#             "sign_index": sign_idx
#         }
#         sign_deg = lon % 30
#         planet_positions[planet] = {
#             "sign": SIGNS[sign_idx],
#             "degrees": format_dms(sign_deg)
#         }

#     asc_lon = calculate_ascendant(jd, latitude, longitude)
#     asc_sign_idx = get_sign_index(asc_lon)
#     positions["Ascendant"] = {
#         "longitude": asc_lon,
#         "sign_index": asc_sign_idx
#     }
#     asc_deg = asc_lon % 30

#     # Calculate Bhinnashtakavarga for each planet
#     bhinnashtakavarga = calculate_bhinnashtakavarga_matrix(positions)

#     # Format Bhinnashtakavarga for response (signs mapped to bindus)
#     bhinnashtakavarga_formatted = {
#         planet: {SIGNS[i]: bindus[i] for i in range(12)}
#         for planet, bindus in bhinnashtakavarga.items()
#     }

#     # Calculate Sarvashtakvarga
#     sarvashtakavarga = calculate_sarvashtakavarga(bhinnashtakavarga)

#     # Map Sarvashtakvarga to houses
#     houses = map_to_houses(sarvashtakavarga, asc_sign_idx)

#     # Generate matrix table for Sarvashtakvarga
#     matrix_table = generate_matrix_table(sarvashtakavarga, asc_sign_idx)

#     # Return all calculated data
#     return {
#         "planetary_positions": planet_positions,
#         "ascendant": {"sign": SIGNS[asc_sign_idx], "degrees": format_dms(asc_deg)},
#         "bhinnashtakavarga": bhinnashtakavarga_formatted,
#         "sarvashtakavarga": {
#             "signs": {SIGNS[i]: sarvashtakavarga[i] for i in range(12)},
#             "houses": houses,
#             "matrix_table": matrix_table
#         },
#         "julian_day": jd,
#         "ayanamsa": ayanamsa
#     }




def lahiri_sarvathakavargha(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate Sarvashtakavarga using Lahiri Ayanamsa based on birth details."""
    # Calculate Julian Day and Ayanamsa
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    ayanamsa = calculate_ayanamsa(jd)

    # Calculate planetary positions and Ascendant
    positions = {}
    planet_positions = {}
    for planet in PLANETS:
        lon = calculate_sidereal_longitude(jd, PLANETS[planet])
        sign_idx = get_sign_index(lon)
        positions[planet] = {
            "longitude": lon,
            "sign_index": sign_idx
        }
        sign_deg = lon % 30
        planet_positions[planet] = {
            "sign": SIGNS[sign_idx],
            "degrees": format_dms(sign_deg)
        }

    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign_idx = get_sign_index(asc_lon)
    positions["Ascendant"] = {
        "longitude": asc_lon,
        "sign_index": asc_sign_idx
    }
    asc_deg = asc_lon % 30

    # Calculate Bhinnashtakavarga for each planet
    bhinnashtakavarga = calculate_bhinnashtakavarga_matrix(positions)

    # Calculate total bindus for each planet in Bhinnashtakavarga
    bhinnashtakavarga_totals = {
        planet: sum(bindus) for planet, bindus in bhinnashtakavarga.items()
    }

    # Format Bhinnashtakavarga for response (signs mapped to bindus)
    bhinnashtakavarga_formatted = {
        planet: {SIGNS[i]: bindus[i] for i in range(12)}
        for planet, bindus in bhinnashtakavarga.items()
    }

    # Calculate Sarvashtakvarga
    sarvashtakavarga = calculate_sarvashtakavarga(bhinnashtakavarga)

    # Calculate total bindus for Sarvashtakavarga
    sarvashtakavarga_total = sum(sarvashtakavarga)

    # Map Sarvashtakvarga to houses
    houses = map_to_houses(sarvashtakavarga, asc_sign_idx)

    # Generate matrix table for Sarvashtakvarga
    matrix_table = generate_matrix_table(sarvashtakavarga, asc_sign_idx)

    # Return all calculated data
    return {
        "planetary_positions": planet_positions,
        "ascendant": {"sign": SIGNS[asc_sign_idx], "degrees": format_dms(asc_deg)},
        "bhinnashtakavarga": bhinnashtakavarga_formatted,
        "bhinnashtakavarga_totals": bhinnashtakavarga_totals,  # NEW: Total bindus per planet
        "sarvashtakavarga": {
            "signs": {SIGNS[i]: sarvashtakavarga[i] for i in range(12)},
            "houses": houses,
            "matrix_table": matrix_table,
            "total_bindus": sarvashtakavarga_total  # NEW: Total Sarvashtakavarga bindus
        },
        "julian_day": jd,
        "ayanamsa": ayanamsa
    }

