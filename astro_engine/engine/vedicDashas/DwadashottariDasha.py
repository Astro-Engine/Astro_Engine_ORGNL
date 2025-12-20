"""
Dwadashottari Dasha - Calculation Module (v8.0 FINAL - RUNNING ANTARDASHA)
===========================================================================
CRITICAL FIX v8.0:
- Show the RUNNING antardasha at birth (not previous!)
- Mars is running at birth, so show Mars balance first
- Then show subsequent antardashas

This matches "Dasha at the time of birth: Me-Ma-Ke-Sa-Ke" 
(Mercury Mahadasha, Mars Antardasha)

Features:
- 8-planet system (112-year cycle)
- Navamsha Lagna applicability (Taurus or Libra - Venus signs)
- Starting from Revati nakshatra counting
- Balance calculation at birth
- RUNNING antardasha shown first (CRITICAL FIX)
- Complete Mahadasha and Antardasha periods
"""

from datetime import datetime, timedelta
import swisseph as swe

# ============================================================================
# CONFIGURATION
# ============================================================================

DWADASHOTTARI_PLANETS = [
    {"name": "Sun", "years": 7},
    {"name": "Jupiter", "years": 9},
    {"name": "Ketu", "years": 11},
    {"name": "Mercury", "years": 13},
    {"name": "Rahu", "years": 15},
    {"name": "Mars", "years": 17},
    {"name": "Saturn", "years": 19},
    {"name": "Moon", "years": 21}
]

TOTAL_YEARS = 112

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_julian_day(date, time, tz_offset):
    year, month, day = date.year, date.month, date.day
    hour, minute, second = time.hour, time.minute, time.second
    total_seconds = hour * 3600 + minute * 60 + second - (tz_offset * 3600)
    utc_hour = total_seconds / 3600
    return swe.julday(year, month, day, utc_hour)

def calculate_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa_ut(jd)

def get_planet_position(jd, planet_id, ayanamsa):
    result = swe.calc_ut(jd, planet_id)
    tropical_long = result[0][0]
    return (tropical_long - ayanamsa) % 360

def get_ascendant(jd, latitude, longitude, ayanamsa):
    houses = swe.houses_ex(jd, latitude, longitude, b'W')
    asc_tropical = houses[0][0]
    return (asc_tropical - ayanamsa) % 360

def get_navamsha_lagna(asc_long):
    sign_num = int(asc_long / 30)
    degree_in_sign = asc_long % 30
    navamsha_num = int(degree_in_sign / (30.0 / 9.0))
    
    if sign_num % 2 == 0:
        navamsha_sign = (sign_num + navamsha_num) % 12
    else:
        navamsha_sign = (sign_num + 8 + navamsha_num) % 12
    
    return navamsha_sign

def get_moon_nakshatra_details(moon_long):
    nakshatra_span = 360.0 / 27.0
    nakshatra_num = int(moon_long / nakshatra_span)
    nakshatra_name = NAKSHATRAS[nakshatra_num]
    traversed_degrees = moon_long % nakshatra_span
    remaining_degrees = nakshatra_span - traversed_degrees
    
    return nakshatra_num, nakshatra_name, traversed_degrees, remaining_degrees, nakshatra_span

def years_to_components(years):
    years_int = int(years)
    remaining_days = (years - years_int) * 365.25
    months = int(remaining_days / 30.4375)
    days = int(remaining_days % 30.4375)
    return years_int, months, days

def add_years_to_date(start_date, years):
    days = years * 365.25
    return start_date + timedelta(days=days)

# ============================================================================
# DASHA CALCULATION
# ============================================================================

def calculate_starting_dasha_lord(janma_nakshatra):
    REVATI_INDEX = 26
    count = REVATI_INDEX - janma_nakshatra + 1
    remainder = count % 8
    
    if remainder == 0:
        planet_index = 7
    else:
        planet_index = remainder - 1
    
    return planet_index

def calculate_balance_dasha(planet_years, remaining_degrees, total_degrees):
    fraction_remaining = remaining_degrees / total_degrees
    balance_years = planet_years * fraction_remaining
    return balance_years

def calculate_complete_balance_antardashas(maha_planet_index, maha_total_years, 
                                          balance_years, birth_date):
    """
    Calculate COMPLETE antardashas for balance Mahadasha
    
    CORRECT LOGIC (v8.0):
    ====================
    1. Find RUNNING antardasha at birth
    2. Show RUNNING antardasha with BALANCE duration
    3. Then show all SUBSEQUENT antardashas
    
    Example:
    - Mars is RUNNING at birth
    - Show Mars with balance (~0.574 years)
    - Then show Saturn, Moon, Sun, Jupiter, Ketu
    
    This matches: "Dasha at time of birth: Me-Ma" (Mercury-Mars)
    """
    
    # STEP 1: Calculate elapsed time
    elapsed_years = maha_total_years - balance_years
    
    # STEP 2: Calculate all 8 antardasha durations
    all_antardashas = []
    cumulative = 0.0
    
    for i in range(8):
        antar_index = (maha_planet_index + i) % 8
        antar_planet = DWADASHOTTARI_PLANETS[antar_index]
        antar_years = (maha_total_years * antar_planet["years"]) / TOTAL_YEARS
        
        all_antardashas.append({
            "planet": antar_planet["name"],
            "planet_index": antar_index,
            "years": antar_years,
            "cumulative_start": cumulative,
            "cumulative_end": cumulative + antar_years
        })
        
        cumulative += antar_years
    
    # STEP 3: Find RUNNING antardasha at birth
    running_index = None
    for i, antar in enumerate(all_antardashas):
        if antar["cumulative_start"] <= elapsed_years < antar["cumulative_end"]:
            running_index = i
            break
    
    if running_index is None:
        running_index = 7
    
    # STEP 4: Use RUNNING antardasha (NOT previous!)
    first_antar_index = running_index
    
    # STEP 5: Calculate subsequent full antardashas
    subsequent_indices = []
    for i in range(running_index + 1, 8):
        subsequent_indices.append(i)
    
    # Calculate sum of subsequent full antardashas
    sum_subsequent = sum(all_antardashas[i]["years"] for i in subsequent_indices)
    
    # STEP 6: Calculate BALANCE duration for running antardasha
    first_antar_duration = balance_years - sum_subsequent
    
    # STEP 7: Build result
    result = []
    current_date = birth_date
    
    # Add RUNNING antardasha (BALANCE)
    running_antar = all_antardashas[first_antar_index]
    years, months, days = years_to_components(first_antar_duration)
    end_date = add_years_to_date(current_date, first_antar_duration)
    
    result.append({
        "planet": running_antar["planet"],
        "start_date": current_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "duration_years": round(first_antar_duration, 6),
        "duration_formatted": f"{years}Y {months}M {days}D",
        "is_balance": True,
        "antardasha_type": "Balance of running antardasha"
    })
    
    current_date = end_date
    
    # Add subsequent antardashas (FULL)
    for i in subsequent_indices:
        antar = all_antardashas[i]
        years, months, days = years_to_components(antar["years"])
        end_date = add_years_to_date(current_date, antar["years"])
        
        result.append({
            "planet": antar["planet"],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(antar["years"], 6),
            "duration_formatted": f"{years}Y {months}M {days}D",
            "is_balance": False,
            "antardasha_type": "Complete antardasha"
        })
        
        current_date = end_date
    
    # Metadata
    calc_details = {
        "total_mahadasha_years": maha_total_years,
        "balance_at_birth": balance_years,
        "elapsed_before_birth": elapsed_years,
        "running_antardasha_at_birth": running_antar["planet"],
        "shown_first_antardasha": running_antar["planet"],
        "first_antardasha_duration": first_antar_duration,
        "rule_applied": "Show RUNNING antardasha with BALANCE duration",
        "total_antardashas_shown": len(result)
    }
    
    return result, calc_details

def calculate_full_antardashas(maha_planet_index, maha_years, maha_start_date):
    """Calculate antardashas for FULL Mahadasha"""
    result = []
    
    if isinstance(maha_start_date, str):
        current_date = datetime.strptime(maha_start_date, "%Y-%m-%d")
    else:
        current_date = maha_start_date
    
    for i in range(8):
        antar_index = (maha_planet_index + i) % 8
        antar_planet = DWADASHOTTARI_PLANETS[antar_index]
        antar_years = (maha_years * antar_planet["years"]) / TOTAL_YEARS
        
        years, months, days = years_to_components(antar_years)
        end_date = add_years_to_date(current_date, antar_years)
        
        result.append({
            "planet": antar_planet["name"],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(antar_years, 6),
            "duration_formatted": f"{years}Y {months}M {days}D",
            "is_balance": False,
            "antardasha_type": "Complete antardasha"
        })
        
        current_date = end_date
    
    return result

def generate_mahadashas(birth_datetime, starting_planet_index, balance_years):
    """Generate complete Mahadasha timeline"""
    mahadashas = []
    current_date = birth_datetime
    total_elapsed = 0.0
    
    # First Mahadasha: Balance period
    planet = DWADASHOTTARI_PLANETS[starting_planet_index]
    years, months, days = years_to_components(balance_years)
    end_date = add_years_to_date(current_date, balance_years)
    
    mahadashas.append({
        "planet": planet["name"],
        "planet_index": starting_planet_index,
        "total_years": planet["years"],
        "start_date": current_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "duration_years": round(balance_years, 6),
        "duration_formatted": f"{years}Y {months}M {days}D",
        "is_balance": True
    })
    
    current_date = end_date
    total_elapsed = balance_years
    planet_index = starting_planet_index
    
    # Continue with full periods
    while total_elapsed < 120:
        planet_index = (planet_index + 1) % 8
        planet = DWADASHOTTARI_PLANETS[planet_index]
        planet_years = planet["years"]
        
        if total_elapsed + planet_years > 120:
            planet_years = 120 - total_elapsed
        
        years, months, days = years_to_components(planet_years)
        end_date = add_years_to_date(current_date, planet_years)
        
        mahadashas.append({
            "planet": planet["name"],
            "planet_index": planet_index,
            "total_years": planet["years"],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(planet_years, 6),
            "duration_formatted": f"{years}Y {months}M {days}D",
            "is_balance": False
        })
        
        current_date = end_date
        total_elapsed += planet_years
    
    return mahadashas

# ============================================================================
# MAIN CALCULATION ORCHESTRATION
# ============================================================================

def calculate_dwadashottari_dasha(data):
    """
    Main function to calculate Dwadashottari Dasha system
    
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
    dict: Complete Dwadashottari Dasha calculations
    """
    # Parse input
    user_name = data.get('user_name', 'User')
    birth_date_str = data['birth_date']
    birth_time_str = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    
    # Parse date and time
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
    birth_time = datetime.strptime(birth_time_str, '%H:%M:%S').time()
    birth_datetime = datetime.combine(birth_date, birth_time)
    
    # Calculate astronomical positions
    jd = calculate_julian_day(birth_date, birth_time, timezone_offset)
    ayanamsa = calculate_ayanamsa(jd)
    asc_sidereal = get_ascendant(jd, latitude, longitude, ayanamsa)
    navamsha_sign = get_navamsha_lagna(asc_sidereal)
    moon_long = get_planet_position(jd, swe.MOON, ayanamsa)
    
    # Check applicability
    is_applicable = navamsha_sign in [1, 6]
    sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Get nakshatra details
    nakshatra_num, nakshatra_name, traversed, remaining, total = \
        get_moon_nakshatra_details(moon_long)
    
    # Calculate Dasha
    starting_planet_index = calculate_starting_dasha_lord(nakshatra_num)
    starting_planet = DWADASHOTTARI_PLANETS[starting_planet_index]
    balance_years = calculate_balance_dasha(starting_planet["years"], remaining, total)
    
    # Generate Mahadashas
    mahadashas = generate_mahadashas(birth_datetime, starting_planet_index, balance_years)
    
    # Calculate antardashas for ALL Mahadashas
    detailed_mahadashas = []
    
    for maha in mahadashas:
        if maha["is_balance"]:
            antardashas, calc_details = calculate_complete_balance_antardashas(
                maha["planet_index"],
                maha["total_years"],
                maha["duration_years"],
                birth_datetime
            )
            
            detailed_mahadashas.append({
                "mahadasha": maha,
                "antardashas": antardashas,
                "antardasha_calculation": calc_details
            })
        else:
            antardashas = calculate_full_antardashas(
                maha["planet_index"],
                maha["duration_years"],
                maha["start_date"]
            )
            
            detailed_mahadashas.append({
                "mahadasha": maha,
                "antardashas": antardashas,
                "antardasha_calculation": {
                    "type": "Full Mahadasha",
                    "total_antardashas": len(antardashas)
                }
            })
    
    # Response
    response = {
        "user_name": user_name,
        "birth_details": {
            "date": birth_date_str,
            "time": birth_time_str,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "ayanamsa": round(ayanamsa, 6),
        "navamsha_lagna": {
            "sign": sign_names[navamsha_sign],
            "sign_number": navamsha_sign
        },
        "applicability": {
            "is_applicable": is_applicable,
            "condition": "Navamsha Lagna in Taurus or Libra (Venus signs)",
            "message": f"Dwadashottari Dasha is {'APPLICABLE' if is_applicable else 'NOT APPLICABLE'} for this chart"
        },
        "birth_nakshatra": nakshatra_name,
        "starting_dasha": {
            "planet": starting_planet["name"],
            "total_years": starting_planet["years"],
            "balance_years": round(balance_years, 4),
            "balance_formatted": f"{years_to_components(balance_years)[0]}Y {years_to_components(balance_years)[1]}M {years_to_components(balance_years)[2]}D"
        },
        "dasha_system_info": {
            "name": "Dwadashottari Dasha",
            "total_cycle": "112 years",
            "planets_involved": 8,
            "planetary_periods": [
                {"planet": p["name"], "years": p["years"]} 
                for p in DWADASHOTTARI_PLANETS
            ]
        },
        "mahadashas": mahadashas,
        "detailed_mahadashas_with_antardashas": detailed_mahadashas,
        "total_mahadashas_calculated": len(detailed_mahadashas)
    }
    
    return response