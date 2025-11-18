




# import swisseph as swe
# from datetime import datetime, timedelta
# import logging

# # Nakshatra definitions with precise start degrees and ruling planets
# NAKSHATRAS = [
#     ("Ashwini", 0.0, "Ketu"), ("Bharani", 13.333333333333334, "Venus"), ("Krittika", 26.666666666666668, "Sun"),
#     ("Rohini", 40.0, "Moon"), ("Mrigashira", 53.333333333333336, "Mars"), ("Ardra", 66.66666666666667, "Rahu"),
#     ("Punarvasu", 80.0, "Jupiter"), ("Pushya", 93.33333333333333, "Saturn"), ("Ashlesha", 106.66666666666667, "Mercury"),
#     ("Magha", 120.0, "Ketu"), ("Purva Phalguni", 133.33333333333334, "Venus"), ("Uttara Phalguni", 146.66666666666666, "Sun"),
#     ("Hasta", 160.0, "Moon"), ("Chitra", 173.33333333333334, "Mars"), ("Swati", 186.66666666666666, "Rahu"),
#     ("Vishakha", 200.0, "Jupiter"), ("Anuradha", 213.33333333333334, "Saturn"), ("Jyeshta", 226.66666666666666, "Mercury"),
#     ("Mula", 240.0, "Ketu"), ("Purva Ashadha", 253.33333333333334, "Venus"), ("Uttara Ashadha", 266.6666666666667, "Sun"),
#     ("Shravana", 280.0, "Moon"), ("Dhanishta", 293.3333333333333, "Mars"), ("Shatabhisha", 306.6666666666667, "Rahu"),
#     ("Purva Bhadrapada", 320.0, "Jupiter"), ("Uttara Bhadrapada", 333.3333333333333, "Saturn"), ("Revati", 346.6666666666667, "Mercury")
# ]

# # Mahadasha durations in years
# PLANET_DURATIONS = {
#     "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0,
#     "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0
# }

# PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# # Use solar year for date alignment with high precision
# VIMSHOTTARI_YEAR_DAYS = 365.256363051  # More precise solar year length

# def get_julian_pratyathar_day(date_str, time_str, tz_offset):
#     """Convert local birth date and time to Julian Day with timezone adjustment."""
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     hour_decimal = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
#     jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
#     logging.debug(f"Julian Day: {jd}")
#     return jd

# def jd_to_date(jd):
#     """Convert Julian Day back to Gregorian date with precise time."""
#     year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
#     hour_int = int(hour)
#     minute = (hour - hour_int) * 60
#     minute_int = int(minute)
#     second = (hour - hour_int) * 3600 - minute_int * 60
#     second_int = int(round(second))
#     if second_int >= 60:
#         second_int = 0
#         minute_int += 1
#         if minute_int >= 60:
#             minute_int = 0
#             hour_int += 1
#     return f"{year}-{month:02d}-{day:02d} {hour_int:02d}:{minute_int:02d}:{second_int:02d}"

# def calculate_moon_praty_sidereal_position(jd):
#     """Calculate Moon's sidereal longitude using Lahiri ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
#     ayanamsa = swe.get_ayanamsa_ut(jd)
#     moon_sidereal = (moon_tropical - ayanamsa) % 360
#     logging.debug(f"Moon Tropical: {moon_tropical}, Ayanamsa: {ayanamsa}, Moon Sidereal: {moon_sidereal}")
#     return moon_sidereal

# def get_nakshatra_party_and_lord(moon_longitude):
#     """Determine Nakshatra and its ruling planet based on Moon's longitude."""
#     for nakshatra, start, lord in NAKSHATRAS:
#         if start <= moon_longitude < start + 13.333333333333334:
#             return nakshatra, lord, start
#     if moon_longitude >= 346.6666666666667 or moon_longitude < 0:
#         return "Revati", "Mercury", 346.6666666666667
#     return None, None, None

# def calculate_pratythar_dasha_balance(moon_longitude, nakshatra_start, lord):
#     """Calculate elapsed and remaining time in the first Mahadasha at birth with high precision."""
#     nakshatra_span = 13.333333333333334
#     degrees_in_nakshatra = moon_longitude - nakshatra_start
#     if degrees_in_nakshatra < 0:
#         degrees_in_nakshatra += 360
#     fraction_elapsed = degrees_in_nakshatra / nakshatra_span
#     mahadasha_duration = PLANET_DURATIONS[lord]
#     elapsed_time = mahadasha_duration * fraction_elapsed
#     remaining_time = mahadasha_duration - elapsed_time
#     logging.debug(f"Degrees in Nakshatra: {degrees_in_nakshatra}, Fraction Elapsed: {fraction_elapsed}, "
#                   f"Elapsed Time: {elapsed_time}, Remaining Time: {remaining_time}")
#     return remaining_time, mahadasha_duration, elapsed_time

# def lahiri_partyathar_dasha(mahadasha_planet, antardasha_planet, antardasha_start_jd, antardasha_duration, birth_jd=None, elapsed_in_antardasha=0):
#     """Calculate Pratyantardasha periods with precise start planet adjustment based on elapsed time."""
#     pratyantardashas = []
#     total_cycle = 120.0
#     start_idx = PLANET_ORDER.index(antardasha_planet)
#     current_jd = antardasha_start_jd

#     # Calculate all Pratyantardasha durations
#     pratyantardasha_durations = []
#     for i in range(9):
#         planet = PLANET_ORDER[(start_idx + i) % 9]
#         duration_years = (antardasha_duration * PLANET_DURATIONS[planet]) / total_cycle
#         pratyantardasha_durations.append(duration_years)

#     if birth_jd is not None and elapsed_in_antardasha > 0:
#         # Determine the active Pratyantardasha at birth
#         cumulative_duration = 0
#         for i in range(9):
#             cumulative_duration += pratyantardasha_durations[i]
#             if cumulative_duration > elapsed_in_antardasha:
#                 start_pratyantardasha_idx = i
#                 time_already_elapsed_in_pratyantardasha = elapsed_in_antardasha - (cumulative_duration - pratyantardasha_durations[i])
#                 remaining_in_pratyantardasha = pratyantardasha_durations[i] - time_already_elapsed_in_pratyantardasha
#                 break
#         else:
#             start_pratyantardasha_idx = 0  # Fallback to start if elapsed exceeds total duration
#             time_already_elapsed_in_pratyantardasha = 0
#             remaining_in_pratyantardasha = pratyantardasha_durations[0]

#         # Calculate the start JD of the Antardasha and adjust for elapsed time
#         elapsed_days_before_active = sum(pratyantardasha_durations[:start_pratyantardasha_idx]) * VIMSHOTTARI_YEAR_DAYS
#         active_pratyantardasha_start_jd = antardasha_start_jd + elapsed_days_before_active + (time_already_elapsed_in_pratyantardasha * VIMSHOTTARI_YEAR_DAYS)

#         # For the first Mahadasha/Antardasha, align the active Pratyantardasha start with birth_jd
#         if active_pratyantardasha_start_jd < birth_jd:
#             active_pratyantardasha_start_jd = birth_jd
#             remaining_in_pratyantardasha = pratyantardasha_durations[start_pratyantardasha_idx] - time_already_elapsed_in_pratyantardasha

#         active_pratyantardasha_end_jd = active_pratyantardasha_start_jd + (remaining_in_pratyantardasha * VIMSHOTTARI_YEAR_DAYS)
#         current_jd = antardasha_start_jd

#         # Add Pratyantardashas starting from the active one
#         for i in range(9):
#             planet_idx = (start_idx + (start_pratyantardasha_idx + i) % 9) % 9
#             planet = PLANET_ORDER[planet_idx]
#             duration_years = pratyantardasha_durations[(start_pratyantardasha_idx + i) % 9]
            
#             if i == 0:
#                 # Active Pratyantardasha at birth
#                 start_jd = active_pratyantardasha_start_jd
#                 end_jd = active_pratyantardasha_end_jd
#                 duration = remaining_in_pratyantardasha
#             else:
#                 # Subsequent Pratyantardashas
#                 start_jd = current_jd
#                 duration_days = duration_years * VIMSHOTTARI_YEAR_DAYS
#                 end_jd = start_jd + duration_days
#                 duration = duration_years

#             pratyantardashas.append({
#                 "planet": planet,
#                 "start_date": jd_to_date(start_jd),
#                 "end_date": jd_to_date(end_jd),
#                 "duration_years": duration
#             })
#             current_jd = end_jd
#     else:
#         # No elapsed time adjustment, calculate sequentially
#         for i in range(9):
#             planet = PLANET_ORDER[(start_idx + i) % 9]
#             duration_years = pratyantardasha_durations[i]
#             duration_days = duration_years * VIMSHOTTARI_YEAR_DAYS
#             end_jd = current_jd + duration_days
#             pratyantardashas.append({
#                 "planet": planet,
#                 "start_date": jd_to_date(current_jd),
#                 "end_date": jd_to_date(end_jd),
#                 "duration_years": duration_years
#             })
#             current_jd = end_jd

#     return pratyantardashas

# def calculate_antardashas(mahadasha_planet, mahadasha_start_jd, mahadasha_duration, birth_jd=None, elapsed_time=0):
#     """Calculate Antardasha periods within a Mahadasha, adjusting for birth date if necessary."""
#     antardashas = []
#     total_cycle = 120.0
#     start_idx = PLANET_ORDER.index(mahadasha_planet)
#     current_jd = mahadasha_start_jd

#     antardasha_durations = []
#     for i in range(9):
#         antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
#         duration_years = (mahadasha_duration * PLANET_DURATIONS[antardasha_planet]) / total_cycle
#         antardasha_durations.append(duration_years)

#     if birth_jd is not None and elapsed_time > 0:
#         cumulative_duration = 0
#         for i in range(9):
#             cumulative_duration += antardasha_durations[i]
#             if cumulative_duration > elapsed_time:
#                 start_antardasha_idx = i
#                 time_already_elapsed = elapsed_time - (cumulative_duration - antardasha_durations[i])
#                 remaining_in_antardasha = antardasha_durations[i] - time_already_elapsed
#                 break
#         else:
#             start_antardasha_idx = 0
#             time_already_elapsed = 0
#             remaining_in_antardasha = antardasha_durations[0]

#         # Adjust start JD for the active Antardasha
#         elapsed_days_before_active = sum(antardasha_durations[:start_antardasha_idx]) * VIMSHOTTARI_YEAR_DAYS
#         active_antardasha_start_jd = mahadasha_start_jd + elapsed_days_before_active
#         active_antardasha_end_jd = active_antardasha_start_jd + (antardasha_durations[start_antardasha_idx] * VIMSHOTTARI_YEAR_DAYS)

#         # Add all Antardashas, adjusting the active one to start at birth
#         for i in range(9):
#             antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
#             duration_years = antardasha_durations[i]
#             duration_days = duration_years * VIMSHOTTARI_YEAR_DAYS
            
#             if i < start_antardasha_idx:
#                 # Antardashas before birth
#                 end_jd = current_jd + duration_days
#                 pratyantardashas = lahiri_partyathar_dasha(mahadasha_planet, antardasha_planet, current_jd, duration_years)
#             elif i == start_antardasha_idx:
#                 # Active Antardasha at birth
#                 start_jd = birth_jd
#                 end_jd = start_jd + (remaining_in_antardasha * VIMSHOTTARI_YEAR_DAYS)
#                 pratyantardashas = lahiri_partyathar_dasha(mahadasha_planet, antardasha_planet, active_antardasha_start_jd, duration_years, birth_jd, time_already_elapsed)
#                 duration_years = remaining_in_antardasha
#             else:
#                 # Subsequent Antardashas
#                 start_jd = current_jd
#                 end_jd = start_jd + duration_days
#                 pratyantardashas = lahiri_partyathar_dasha(mahadasha_planet, antardasha_planet, start_jd, duration_years)

#             antardashas.append({
#                 "planet": antardasha_planet,
#                 "start_date": jd_to_date(current_jd if i < start_antardasha_idx else start_jd),
#                 "end_date": jd_to_date(end_jd),
#                 "duration_years": duration_years,
#                 "pratyantardashas": pratyantardashas
#             })
#             current_jd = end_jd
#     else:
#         for i in range(9):
#             antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
#             duration_years = antardasha_durations[i]
#             duration_days = duration_years * VIMSHOTTARI_YEAR_DAYS
#             end_jd = current_jd + duration_days
#             pratyantardashas = lahiri_partyathar_dasha(mahadasha_planet, antardasha_planet, current_jd, duration_years)
#             antardashas.append({
#                 "planet": antardasha_planet,
#                 "start_date": jd_to_date(current_jd),
#                 "end_date": jd_to_date(end_jd),
#                 "duration_years": duration_years,
#                 "pratyantardashas": pratyantardashas
#             })
#             current_jd = end_jd
#     return antardashas

# def calculate_Pratythardasha_periods(birth_jd, remaining_time, starting_planet, elapsed_time):
#     """Calculate all Mahadasha periods starting from the birth date."""
#     mahadasha_sequence = []
#     current_planet_idx = PLANET_ORDER.index(starting_planet)
#     mahadasha_start_jd = birth_jd - (elapsed_time * VIMSHOTTARI_YEAR_DAYS)
#     current_jd = mahadasha_start_jd

#     for i in range(9):
#         current_planet = PLANET_ORDER[current_planet_idx]
#         duration_years = remaining_time if i == 0 else PLANET_DURATIONS[current_planet]
#         duration_days = duration_years * VIMSHOTTARI_YEAR_DAYS
#         end_jd = current_jd + duration_days
#         if i == 0:
#             antardashas = calculate_antardashas(current_planet, current_jd, PLANET_DURATIONS[current_planet], birth_jd, elapsed_time)
#         else:
#             antardashas = calculate_antardashas(current_planet, current_jd, PLANET_DURATIONS[current_planet])
#         mahadasha_sequence.append({
#             "planet": current_planet,
#             "start_date": jd_to_date(current_jd if i > 0 else birth_jd),
#             "end_date": jd_to_date(end_jd),
#             "duration_years": duration_years,
#             "antardashas": antardashas
#         })
#         current_jd = end_jd
#         current_planet_idx = (current_planet_idx + 1) % 9
#     return mahadasha_sequence



# New version of Pratyantardashas.py to be implemented here.

"""
VIMSHOTTARI DASHA CALCULATIONS - LAHIRI AYANAMSA
=================================================
Pure calculation functions - NO Flask imports
All calculations use Lahiri ayanamsa and sidereal year precision
"""

import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (adjust path as needed)
swe.set_ephe_path('astro_api/ephe')

# Nakshatra details: Name, Start Degree, Ruling Planet
NAKSHATRAS = [
    ("Ashwini", 0, "Ketu"), ("Bharani", 13.333, "Venus"), ("Krittika", 26.666, "Sun"),
    ("Rohini", 40, "Moon"), ("Mrigashira", 53.333, "Mars"), ("Ardra", 66.666, "Rahu"),
    ("Punarvasu", 80, "Jupiter"), ("Pushya", 93.333, "Saturn"), ("Ashlesha", 106.666, "Mercury"),
    ("Magha", 120, "Ketu"), ("Purva Phalguni", 133.333, "Venus"), ("Uttara Phalguni", 146.666, "Sun"),
    ("Hasta", 160, "Moon"), ("Chitra", 173.333, "Mars"), ("Swati", 186.666, "Rahu"),
    ("Vishakha", 200, "Jupiter"), ("Anuradha", 213.333, "Saturn"), ("Jyeshta", 226.666, "Mercury"),
    ("Mula", 240, "Ketu"), ("Purva Ashadha", 253.333, "Venus"), ("Uttara Ashadha", 266.666, "Sun"),
    ("Shravana", 280, "Moon"), ("Dhanishta", 293.333, "Mars"), ("Shatabhisha", 306.666, "Rahu"),
    ("Purva Bhadrapada", 320, "Jupiter"), ("Uttara Bhadrapada", 333.333, "Saturn"), ("Revati", 346.666, "Mercury")
]

# Planet durations in years for Vimshottari Dasha
PLANET_DURATIONS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

# Fixed order of planets
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Constants for precise calculations
SIDEREAL_YEAR = 365.256363  # Sidereal year length in days
NAKSHATRA_SPAN = 13 + 20/60  # Exactly 13 degrees 20 minutes

def get_julian_day_lahiri(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def jd_to_date_lahiri(jd):
    """Convert Julian Day to readable date-time string."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    return f"{year}-{month:02d}-{day:02d} {hour_int:02d}:{minute:02d}:{second:02d}"

def calculate_moon_sidereal_position_lahiri(jd):
    """Calculate Moon's sidereal longitude using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return (moon_tropical - ayanamsa) % 360

def get_nakshatra_and_lord_lahiri(moon_longitude):
    """Determine Nakshatra and its ruling planet based on Moon's longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < (start + NAKSHATRA_SPAN):
            return nakshatra, lord, start
    return "Revati", "Mercury", 346.666  # Default to Revati if at the end

def calculate_dasha_balance_lahiri(moon_longitude, nakshatra_start, lord):
    """Calculate remaining and elapsed time of the first Mahadasha in days."""
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360
    fraction_elapsed = degrees_in_nakshatra / NAKSHATRA_SPAN
    mahadasha_duration_years = PLANET_DURATIONS[lord]
    elapsed_time_years = mahadasha_duration_years * fraction_elapsed
    remaining_time_years = mahadasha_duration_years - elapsed_time_years
    
    # Convert years to days using sidereal year
    elapsed_days = elapsed_time_years * SIDEREAL_YEAR
    remaining_days = remaining_time_years * SIDEREAL_YEAR
    return remaining_days, mahadasha_duration_years * SIDEREAL_YEAR, elapsed_days

def calculate_pratyantardashas_lahiri(antardasha_planet, antardasha_duration_days, antardasha_start_jd):
    """Calculate all 9 Pratyantardashas for a given Antardasha."""
    pratyantardashas = []
    start_idx = PLANET_ORDER.index(antardasha_planet)
    total_cycle = 120
    current_jd = antardasha_start_jd

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_days = (PLANET_DURATIONS[planet] * antardasha_duration_days) / total_cycle
        end_jd = current_jd + duration_days
        
        pratyantardashas.append({
            'planet': planet,
            'start_date': jd_to_date_lahiri(current_jd),
            'end_date': jd_to_date_lahiri(end_jd),
            'duration_days': round(duration_days, 2)
        })
        current_jd = end_jd

    return pratyantardashas

def calculate_antardashas_lahiri(mahadasha_planet, mahadasha_duration_days, mahadasha_start_jd):
    """Calculate all 9 Antardashas for a given Mahadasha."""
    antardashas = []
    start_idx = PLANET_ORDER.index(mahadasha_planet)
    total_cycle = 120  # Total years in Vimshottari cycle
    current_jd = mahadasha_start_jd

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_years = (PLANET_DURATIONS[planet] * mahadasha_duration_days) / total_cycle / SIDEREAL_YEAR
        duration_days = duration_years * SIDEREAL_YEAR
        end_jd = current_jd + duration_days
        
        # Calculate Pratyantardashas for this Antardasha
        pratyantardashas = calculate_pratyantardashas_lahiri(planet, duration_days, current_jd)
        
        antardashas.append({
            'planet': planet,
            'start_date': jd_to_date_lahiri(current_jd),
            'end_date': jd_to_date_lahiri(end_jd),
            'duration_years': round(duration_years, 4),
            'pratyantardashas': pratyantardashas
        })
        current_jd = end_jd

    return antardashas

def calculate_mahadasha_periods_lahiri(birth_jd, starting_planet, elapsed_days):
    """Calculate all 9 Mahadashas starting from the birth Nakshatra lord."""
    mahadasha_sequence = []
    start_idx = PLANET_ORDER.index(starting_planet)
    mahadasha_start_jd = birth_jd - elapsed_days  # Adjust start using elapsed days

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_years = PLANET_DURATIONS[planet]
        duration_days = duration_years * SIDEREAL_YEAR  # Use sidereal year for precision
        end_jd = mahadasha_start_jd + duration_days
        
        # Calculate Antardashas for this Mahadasha
        antardashas = calculate_antardashas_lahiri(planet, duration_days, mahadasha_start_jd)
        
        mahadasha_sequence.append({
            'planet': planet,
            'start_date': jd_to_date_lahiri(mahadasha_start_jd),
            'end_date': jd_to_date_lahiri(end_jd),
            'duration_years': duration_years,
            'antardashas': antardashas
        })
        mahadasha_start_jd = end_jd

    return mahadasha_sequence

def calculate_complete_vimshottari_dasha(birth_date, birth_time, tz_offset):
    """
    Main calculation function - calculates complete Vimshottari Dasha
    
    Args:
        birth_date: Birth date as string "YYYY-MM-DD"
        birth_time: Birth time as string "HH:MM:SS"
        tz_offset: Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        Dictionary with complete dasha calculations
    """
    # Calculate Julian Day for birth
    jd_birth = get_julian_day_lahiri(birth_date, birth_time, tz_offset)
    
    # Calculate Moon's sidereal position
    moon_longitude = calculate_moon_sidereal_position_lahiri(jd_birth)
    
    # Determine Nakshatra and lord
    nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_lahiri(moon_longitude)
    
    # Calculate dasha balance
    remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_lahiri(
        moon_longitude, nakshatra_start, lord
    )
    
    # Calculate all Mahadasha periods with Antardashas and Pratyantardashas
    mahadasha_periods = calculate_mahadasha_periods_lahiri(jd_birth, lord, elapsed_days)

    return {
        "nakshatra_at_birth": nakshatra,
        "moon_longitude": round(moon_longitude, 4),
        "birth_dasha_lord": lord,
        "elapsed_at_birth_days": round(elapsed_days, 2),
        "remaining_at_birth_days": round(remaining_days, 2),
        "mahadashas": mahadasha_periods
    }
