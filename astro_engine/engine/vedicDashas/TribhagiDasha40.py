"""
================================================================================
TRIBHAGI DASHA CALCULATOR - FINAL CORRECTED VERSION
================================================================================
CRITICAL FIX: Balance period antardashas do NOT wrap around
Only includes REMAINING antardashas from current position to end
================================================================================

Tribhagi Dasha - Calculation Module
====================================
27 Mahadashas over 3 Cycles (~118 years)
Proportional Distribution Method
Each planet period = Vimshottari ÷ 3
Total cycle: 40 years
"""

from datetime import datetime, timedelta
from decimal import Decimal, getcontext
import swisseph as swe

getcontext().prec = 50

# ============================================================================
# CONSTANTS
# ============================================================================

TRIBHAGI_YEARS = {
    "Sun": Decimal("2.0"),
    "Moon": Decimal("3.333333333333333"),
    "Mars": Decimal("2.333333333333333"),
    "Rahu": Decimal("6.0"),
    "Jupiter": Decimal("5.333333333333333"),
    "Saturn": Decimal("6.333333333333333"),
    "Mercury": Decimal("5.666666666666667"),
    "Ketu": Decimal("2.333333333333333"),
    "Venus": Decimal("6.666666666666667")
}

TOTAL_CYCLE_YEARS = Decimal("40.0")

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

PLANET_SEQUENCE = ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

DAYS_PER_YEAR = Decimal("365.25")

# ============================================================================
# DATE UTILITIES
# ============================================================================

def parse_date_flexible(date_str):
    """Parse date from various formats"""
    formats = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")

def parse_time_flexible(time_str):
    """Parse time from various formats"""
    formats = ["%H:%M:%S", "%H:%M"]
    for fmt in formats:
        try:
            t = datetime.strptime(time_str, fmt)
            return t.hour, t.minute, t.second
        except ValueError:
            continue
    raise ValueError(f"Invalid time format: {time_str}")

def format_date_dmy(date_obj):
    """Format date as dd-mm-yyyy"""
    return date_obj.strftime("%d-%m-%Y")

def format_datetime_full(date_obj):
    """Format datetime as dd-mm-yyyy hh:mm:ss"""
    return date_obj.strftime("%d-%m-%Y %H:%M:%S")

def decimal_years_to_timedelta(years_decimal):
    """Convert decimal years to timedelta"""
    total_days = years_decimal * DAYS_PER_YEAR
    total_seconds = float(total_days * Decimal("86400"))
    return timedelta(seconds=total_seconds)

def add_years_to_datetime(dt, years_decimal):
    """Add decimal years to datetime"""
    delta = decimal_years_to_timedelta(years_decimal)
    return dt + delta

def years_to_ymd_dict(years_decimal):
    """Convert years to years-months-days dictionary"""
    total_days = years_decimal * DAYS_PER_YEAR
    years = int(years_decimal)
    remaining_days = total_days - (Decimal(years) * DAYS_PER_YEAR)
    months = int(remaining_days / Decimal("30.4375"))
    remaining_days = remaining_days - (Decimal(months) * Decimal("30.4375"))
    days = int(remaining_days)
    return {"years": years, "months": months, "days": days}

# ============================================================================
# ASTRONOMICAL CALCULATIONS
# ============================================================================

def calculate_moon_position(birth_dt, timezone_offset, ayanamsa="LAHIRI"):
    """Calculate sidereal Moon position using Swiss Ephemeris"""
    ayanamsa_map = {
        "LAHIRI": swe.SIDM_LAHIRI,
        "RAMAN": swe.SIDM_RAMAN,
        "KP": swe.SIDM_KRISHNAMURTI
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa, swe.SIDM_LAHIRI))
    
    hour_decimal = birth_dt.hour + birth_dt.minute/60.0 + birth_dt.second/3600.0
    hour_ut = hour_decimal - timezone_offset
    jd = swe.julday(birth_dt.year, birth_dt.month, birth_dt.day, hour_ut)
    moon_data = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    return moon_data[0][0]

def get_nakshatra_info(moon_longitude):
    """Get nakshatra information from Moon longitude"""
    nakshatra_span = Decimal("13.333333333333333")
    moon_long_dec = Decimal(str(moon_longitude))
    nakshatra_number = int(moon_long_dec / nakshatra_span) + 1
    nakshatra_start = (nakshatra_number - 1) * nakshatra_span
    traversed = moon_long_dec - nakshatra_start
    remaining = nakshatra_span - traversed
    percent_completed = (traversed / nakshatra_span) * Decimal("100")
    
    return {
        "number": nakshatra_number,
        "name": NAKSHATRA_NAMES[nakshatra_number - 1],
        "lord": NAKSHATRA_LORDS[nakshatra_number - 1],
        "traversed_degrees": float(traversed),
        "remaining_degrees": float(remaining),
        "percent_completed": float(percent_completed)
    }

# ============================================================================
# BALANCE CALCULATION - PROPORTIONAL METHOD
# ============================================================================

def calculate_balance_at_birth(nakshatra_info):
    """
    Calculate balance of mahadasha at birth using PROPORTIONAL distribution
    """
    lord = nakshatra_info["lord"]
    total_period = TRIBHAGI_YEARS[lord]
    percent_completed = Decimal(str(nakshatra_info["percent_completed"]))
    
    # Mahadasha balance
    balance_years = total_period * (Decimal("1") - percent_completed / Decimal("100"))
    elapsed_years = total_period - balance_years
    
    # Get antardasha sequence for this mahadasha
    maha_index = PLANET_SEQUENCE.index(lord)
    sequence = PLANET_SEQUENCE[maha_index:] + PLANET_SEQUENCE[:maha_index]
    
    # Calculate PROPORTIONAL antardasha periods
    antardasha_periods = []
    cumulative_time = Decimal("0")
    
    for planet in sequence:
        antar_period = (TRIBHAGI_YEARS[planet] / TOTAL_CYCLE_YEARS) * total_period
        antardasha_periods.append({
            "planet": planet,
            "period": antar_period,
            "start": cumulative_time,
            "end": cumulative_time + antar_period
        })
        cumulative_time += antar_period
    
    # Find which antardasha we're in
    antardasha_position = 0
    current_antar = None
    
    for i, antar in enumerate(antardasha_periods):
        if antar["start"] <= elapsed_years < antar["end"]:
            antardasha_position = i
            current_antar = antar
            break
    
    if current_antar is None:
        antardasha_position = len(antardasha_periods) - 1
        current_antar = antardasha_periods[antardasha_position]
    
    # Calculate completion fraction
    antar_elapsed = elapsed_years - current_antar["start"]
    antar_completed_fraction = antar_elapsed / current_antar["period"]
    antar_remaining_fraction = Decimal("1") - antar_completed_fraction
    
    return {
        "planet": lord,
        "total_period_years": float(total_period),
        "balance_years": float(balance_years),
        "elapsed_years": float(elapsed_years),
        "percent_completed": float(percent_completed),
        "starting_antardasha_index": antardasha_position,
        "starting_antardasha_planet": current_antar["planet"],
        "antardasha_completed_fraction": float(antar_completed_fraction),
        "antardasha_remaining_fraction": float(antar_remaining_fraction),
        "calculation_method": "proportional_distribution"
    }

# ============================================================================
# ANTARDASHA CALCULATION - CORRECTED FOR BALANCE PERIOD
# ============================================================================

def calculate_antardashas_balance(mahadasha_planet, maha_start_datetime, 
                                  maha_duration_years_decimal, balance_info):
    """
    Calculate antardashas for BALANCE period
    
    CRITICAL FIX: Balance period includes ONLY REMAINING antardashas
    Does NOT wrap around to beginning!
    
    Example: If birth is at position 2 (Venus) in Mercury mahadasha:
    - Remaining sequence: Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn (7 antardashas)
    - Does NOT include: Mercury, Ketu (already completed before birth)
    """
    antardashas = []
    current_datetime = maha_start_datetime
    
    # Get mahadasha planet's sequence
    mahadasha_index = PLANET_SEQUENCE.index(mahadasha_planet)
    full_sequence = PLANET_SEQUENCE[mahadasha_index:] + PLANET_SEQUENCE[:mahadasha_index]
    
    # CRITICAL FIX: Take ONLY from starting position to END (no wrap-around)
    starting_index = balance_info["starting_antardasha_index"]
    antardasha_sequence = full_sequence[starting_index:]  # Only remaining!
    
    # Calculate weights using proportional method
    remaining_fraction = Decimal(str(balance_info["antardasha_remaining_fraction"]))
    
    weights = []
    for i, planet in enumerate(antardasha_sequence):
        planet_period = TRIBHAGI_YEARS[planet]
        if i == 0:
            # First antardasha: only remaining portion
            weight = planet_period * remaining_fraction
        else:
            # Subsequent antardashas: full portion
            weight = planet_period
        weights.append(weight)
    
    total_weight = sum(weights)
    
    # Distribute balance period proportionally
    for i, (planet, weight) in enumerate(zip(antardasha_sequence, weights)):
        antar_duration = (weight / total_weight) * maha_duration_years_decimal
        end_datetime = add_years_to_datetime(current_datetime, antar_duration)
        
        antardashas.append({
            "planet": planet,
            "start_date": format_date_dmy(current_datetime),
            "end_date": format_date_dmy(end_datetime),
            "start_datetime": format_datetime_full(current_datetime),
            "end_datetime": format_datetime_full(end_datetime),
            "duration_years": float(antar_duration),
            "duration": years_to_ymd_dict(antar_duration),
            "sequence_number": i + 1,
            "is_partial": i == 0,
            "partial_completion": float(Decimal("1") - remaining_fraction) if i == 0 else 0.0
        })
        
        current_datetime = end_datetime
    
    return antardashas

def calculate_antardashas_full(mahadasha_planet, maha_start_datetime, maha_duration_years_decimal):
    """
    Calculate antardashas for FULL period mahadashas
    """
    antardashas = []
    current_datetime = maha_start_datetime
    
    # Sequence starts from mahadasha planet
    start_index = PLANET_SEQUENCE.index(mahadasha_planet)
    antardasha_sequence = PLANET_SEQUENCE[start_index:] + PLANET_SEQUENCE[:start_index]
    
    # Calculate proportionally
    for i, antar_planet in enumerate(antardasha_sequence):
        antar_planet_period = TRIBHAGI_YEARS[antar_planet]
        antar_duration = (maha_duration_years_decimal * antar_planet_period) / TOTAL_CYCLE_YEARS
        end_datetime = add_years_to_datetime(current_datetime, antar_duration)
        
        antardashas.append({
            "planet": antar_planet,
            "start_date": format_date_dmy(current_datetime),
            "end_date": format_date_dmy(end_datetime),
            "start_datetime": format_datetime_full(current_datetime),
            "end_datetime": format_datetime_full(end_datetime),
            "duration_years": float(antar_duration),
            "duration": years_to_ymd_dict(antar_duration),
            "sequence_number": i + 1,
            "is_partial": False,
            "partial_completion": 0.0
        })
        
        current_datetime = end_datetime
    
    return antardashas

# ============================================================================
# MAIN TRIBHAGI DASHA CALCULATION
# ============================================================================

def calculate_tribhagi_dasha_40(birth_date, birth_time, latitude, longitude,
                             timezone_offset=5.5, ayanamsa="LAHIRI"):
    """
    Calculate complete Tribhagi Dasha system (27 mahadashas)
    CORRECTED: Balance period antardashas do NOT wrap around
    """
    
    # Parse inputs
    birth_date_obj = parse_date_flexible(birth_date)
    hour, minute, second = parse_time_flexible(birth_time)
    birth_datetime = datetime(birth_date_obj.year, birth_date_obj.month, birth_date_obj.day,
                             hour, minute, second)
    
    # Calculate Moon position
    moon_longitude = calculate_moon_position(birth_datetime, timezone_offset, ayanamsa)
    nakshatra_info = get_nakshatra_info(moon_longitude)
    balance_info = calculate_balance_at_birth(nakshatra_info)
    
    # Build all 27 mahadashas
    mahadashas = []
    current_datetime = birth_datetime
    maha_counter = 1
    
    balance_planet = balance_info["planet"]
    balance_years = Decimal(str(balance_info["balance_years"]))
    
    # ------------------------------------------------------------------------
    # CYCLE 1: Balance Period + 8 Full Periods
    # ------------------------------------------------------------------------
    
    # 1. Balance Period (CORRECTED - no wrap-around)
    antardashas = calculate_antardashas_balance(
        balance_planet, current_datetime, balance_years, balance_info
    )
    end_datetime = add_years_to_datetime(current_datetime, balance_years)
    
    mahadashas.append({
        "mahadasha_number": maha_counter,
        "planet": balance_planet,
        "start_date": format_date_dmy(current_datetime),
        "end_date": format_date_dmy(end_datetime),
        "start_datetime": format_datetime_full(current_datetime),
        "end_datetime": format_datetime_full(end_datetime),
        "duration_years": float(balance_years),
        "duration": years_to_ymd_dict(balance_years),
        "period_type": "balance",
        "cycle": 1,
        "antardashas": antardashas,
        "balance_info": {
            "starting_antardasha_index": balance_info["starting_antardasha_index"],
            "starting_antardasha_planet": balance_info["starting_antardasha_planet"],
            "antardasha_remaining_fraction": balance_info["antardasha_remaining_fraction"],
            "antardashas_count": len(antardashas)
        }
    })
    
    current_datetime = end_datetime
    maha_counter += 1
    
    # 2-9. Remaining 8 planets in Cycle 1
    balance_index = PLANET_SEQUENCE.index(balance_planet)
    remaining_cycle1_planets = (PLANET_SEQUENCE[balance_index + 1:] + 
                                PLANET_SEQUENCE[:balance_index])
    
    for planet in remaining_cycle1_planets:
        planet_years = TRIBHAGI_YEARS[planet]
        antardashas = calculate_antardashas_full(planet, current_datetime, planet_years)
        end_datetime = add_years_to_datetime(current_datetime, planet_years)
        
        mahadashas.append({
            "mahadasha_number": maha_counter,
            "planet": planet,
            "start_date": format_date_dmy(current_datetime),
            "end_date": format_date_dmy(end_datetime),
            "start_datetime": format_datetime_full(current_datetime),
            "end_datetime": format_datetime_full(end_datetime),
            "duration_years": float(planet_years),
            "duration": years_to_ymd_dict(planet_years),
            "period_type": "full",
            "cycle": 1,
            "antardashas": antardashas
        })
        
        current_datetime = end_datetime
        maha_counter += 1
    
    # ------------------------------------------------------------------------
    # CYCLE 2: 9 Full Periods
    # ------------------------------------------------------------------------
    
    for planet in PLANET_SEQUENCE:
        planet_years = TRIBHAGI_YEARS[planet]
        antardashas = calculate_antardashas_full(planet, current_datetime, planet_years)
        end_datetime = add_years_to_datetime(current_datetime, planet_years)
        
        mahadashas.append({
            "mahadasha_number": maha_counter,
            "planet": planet,
            "start_date": format_date_dmy(current_datetime),
            "end_date": format_date_dmy(end_datetime),
            "start_datetime": format_datetime_full(current_datetime),
            "end_datetime": format_datetime_full(end_datetime),
            "duration_years": float(planet_years),
            "duration": years_to_ymd_dict(planet_years),
            "period_type": "full",
            "cycle": 2,
            "antardashas": antardashas
        })
        
        current_datetime = end_datetime
        maha_counter += 1
    
    # ------------------------------------------------------------------------
    # CYCLE 3: 9 Full Periods
    # ------------------------------------------------------------------------
    
    for planet in PLANET_SEQUENCE:
        planet_years = TRIBHAGI_YEARS[planet]
        antardashas = calculate_antardashas_full(planet, current_datetime, planet_years)
        end_datetime = add_years_to_datetime(current_datetime, planet_years)
        
        mahadashas.append({
            "mahadasha_number": maha_counter,
            "planet": planet,
            "start_date": format_date_dmy(current_datetime),
            "end_date": format_date_dmy(end_datetime),
            "start_datetime": format_datetime_full(current_datetime),
            "end_datetime": format_datetime_full(end_datetime),
            "duration_years": float(planet_years),
            "duration": years_to_ymd_dict(planet_years),
            "period_type": "full",
            "cycle": 3,
            "antardashas": antardashas
        })
        
        current_datetime = end_datetime
        maha_counter += 1
    
    # Calculate cycle summaries
    cycle1_mahas = [m for m in mahadashas if m['cycle'] == 1]
    cycle2_mahas = [m for m in mahadashas if m['cycle'] == 2]
    cycle3_mahas = [m for m in mahadashas if m['cycle'] == 3]
    
    cycle1_total = sum(Decimal(str(m['duration_years'])) for m in cycle1_mahas)
    cycle2_total = sum(Decimal(str(m['duration_years'])) for m in cycle2_mahas)
    cycle3_total = sum(Decimal(str(m['duration_years'])) for m in cycle3_mahas)
    
    # Build final result
    result = {
        "birth_details": {
            "date": birth_date,
            "time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset,
            "datetime_parsed": format_datetime_full(birth_datetime)
        },
        "ayanamsa": ayanamsa,
        "moon_details": {
            "sidereal_longitude": round(moon_longitude, 6),
            "nakshatra_number": nakshatra_info["number"],
            "nakshatra_name": nakshatra_info["name"],
            "nakshatra_lord": nakshatra_info["lord"],
            "traversed_degrees": round(nakshatra_info["traversed_degrees"], 6),
            "remaining_degrees": round(nakshatra_info["remaining_degrees"], 6),
            "percentage_completed": round(nakshatra_info["percent_completed"], 2)
        },
        "balance_at_birth": {
            "planet": balance_info["planet"],
            "total_period_years": balance_info["total_period_years"],
            "balance_years": round(balance_info["balance_years"], 6),
            "elapsed_years": round(balance_info["elapsed_years"], 6),
            "balance_duration": years_to_ymd_dict(Decimal(str(balance_info["balance_years"]))),
            "elapsed_duration": years_to_ymd_dict(Decimal(str(balance_info["elapsed_years"]))),
            "starting_antardasha_index": balance_info["starting_antardasha_index"],
            "starting_antardasha_planet": balance_info["starting_antardasha_planet"],
            "antardasha_completed_fraction": round(balance_info["antardasha_completed_fraction"], 6),
            "antardasha_remaining_fraction": round(balance_info["antardasha_remaining_fraction"], 6),
            "calculation_method": balance_info["calculation_method"]
        },
        "tribhagi_dasha_info": {
            "description": "Tribhagi Dasha - 27 mahadashas over ~118 years",
            "concept": "Each planet period = Vimshottari ÷ 3",
            "total_cycle_years": 40.0,
            "structure": "Cycle 1: Balance + 8 Full | Cycles 2 & 3: 9 Full each",
            "total_mahadashas": len(mahadashas),
            "calculation_method": "Proportional distribution - Balance period does NOT wrap around",
            "balance_antardashas_count": len(mahadashas[0]["antardashas"])
        },
        "cycle_summary": {
            "cycle_1": {
                "start_date": cycle1_mahas[0]["start_date"],
                "end_date": cycle1_mahas[-1]["end_date"],
                "total_years": round(float(cycle1_total), 6),
                "mahadasha_count": len(cycle1_mahas),
                "description": "Balance + 8 Full periods"
            },
            "cycle_2": {
                "start_date": cycle2_mahas[0]["start_date"],
                "end_date": cycle2_mahas[-1]["end_date"],
                "total_years": round(float(cycle2_total), 6),
                "mahadasha_count": len(cycle2_mahas),
                "description": "9 Full periods"
            },
            "cycle_3": {
                "start_date": cycle3_mahas[0]["start_date"],
                "end_date": cycle3_mahas[-1]["end_date"],
                "total_years": round(float(cycle3_total), 6),
                "mahadasha_count": len(cycle3_mahas),
                "description": "9 Full periods"
            }
        },
        "mahadashas": mahadashas,
        "calculation_timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    
    return result