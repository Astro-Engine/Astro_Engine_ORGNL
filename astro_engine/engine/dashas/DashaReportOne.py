import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (adjust path as needed)
swe.set_ephe_path('astro_engine/ephe')

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

def get_julian_day_daily_report(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def jd_to_date_daily_report(jd):
    """Convert Julian Day to readable date-time string."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    return f"{year}-{month:02d}-{day:02d} {hour_int:02d}:{minute:02d}:{second:02d}"

def date_str_to_jd_daily_report(date_str):
    """Convert date string to Julian Day (assumes 00:00:00 time)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return swe.julday(dt.year, dt.month, dt.day, 0.0, swe.GREG_CAL)

def calculate_moon_sidereal_position_daily_report(jd):
    """Calculate Moon's sidereal longitude using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return (moon_tropical - ayanamsa) % 360

def get_nakshatra_and_lord_daily_report(moon_longitude):
    """Determine Nakshatra and its ruling planet based on Moon's longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < (start + NAKSHATRA_SPAN):
            return nakshatra, lord, start
    return "Revati", "Mercury", 346.666  # Default to Revati if at the end

def calculate_dasha_balance_daily_report(moon_longitude, nakshatra_start, lord):
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

def calculate_pran_dashas_daily_report(sookshma_planet, sookshma_duration_days, sookshma_start_jd):
    """Calculate all 9 Pran Dashas for a given Sookshma Dasha."""
    pran_dashas = []
    start_idx = PLANET_ORDER.index(sookshma_planet)
    total_cycle = 120
    current_jd = sookshma_start_jd

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_days = (PLANET_DURATIONS[planet] * sookshma_duration_days) / total_cycle
        pran_dashas.append({
            'planet': planet,
            'start_date': jd_to_date_daily_report(current_jd),
            'end_date': jd_to_date_daily_report(current_jd + duration_days),
            'duration_hours': round(duration_days * 24, 4)
        })
        current_jd += duration_days

    return pran_dashas

def calculate_sookshma_dashas_daily_report(pratyantardasha_planet, pratyantardasha_duration_days, pratyantardasha_start_jd):
    """Calculate all 9 Sookshma Dashas for a given Pratyantardasha."""
    sookshma_dashas = []
    start_idx = PLANET_ORDER.index(pratyantardasha_planet)
    total_cycle = 120
    current_jd = pratyantardasha_start_jd

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_days = (PLANET_DURATIONS[planet] * pratyantardasha_duration_days) / total_cycle
        pran_dashas = calculate_pran_dashas_daily_report(planet, duration_days, current_jd)
        sookshma_dashas.append({
            'planet': planet,
            'start_date': jd_to_date_daily_report(current_jd),
            'end_date': jd_to_date_daily_report(current_jd + duration_days),
            'duration_days': round(duration_days, 2),
            'pran_dashas': pran_dashas
        })
        current_jd += duration_days

    return sookshma_dashas

def calculate_pratyantardashas_daily_report(antardasha_planet, antardasha_duration_days, antardasha_start_jd):
    """Calculate all 9 Pratyantardashas for a given Antardasha."""
    pratyantardashas = []
    start_idx = PLANET_ORDER.index(antardasha_planet)
    total_cycle = 120
    current_jd = antardasha_start_jd

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_days = (PLANET_DURATIONS[planet] * antardasha_duration_days) / total_cycle
        sookshma_dashas = calculate_sookshma_dashas_daily_report(planet, duration_days, current_jd)
        pratyantardashas.append({
            'planet': planet,
            'start_date': jd_to_date_daily_report(current_jd),
            'end_date': jd_to_date_daily_report(current_jd + duration_days),
            'duration_days': round(duration_days, 2),
            'sookshma_dashas': sookshma_dashas
        })
        current_jd += duration_days

    return pratyantardashas

def calculate_antardashas_daily_report(mahadasha_planet, mahadasha_duration_days, mahadasha_start_jd):
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
        pratyantardashas = calculate_pratyantardashas_daily_report(planet, duration_days, current_jd)
        antardashas.append({
            'planet': planet,
            'start_date': jd_to_date_daily_report(current_jd),
            'end_date': jd_to_date_daily_report(end_jd),
            'duration_years': round(duration_years, 4),
            'pratyantardashas': pratyantardashas
        })
        current_jd = end_jd

    return antardashas

def calculate_mahadasha_periods_daily_report(birth_jd, starting_planet, elapsed_days):
    """Calculate all 9 Mahadashas starting from the birth Nakshatra lord."""
    mahadasha_sequence = []
    start_idx = PLANET_ORDER.index(starting_planet)
    mahadasha_start_jd = birth_jd - elapsed_days  # Adjust start using elapsed days

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration_years = PLANET_DURATIONS[planet]
        duration_days = duration_years * SIDEREAL_YEAR  # Use sidereal year for precision
        end_jd = mahadasha_start_jd + duration_days
        antardashas = calculate_antardashas_daily_report(planet, duration_days, mahadasha_start_jd)
        mahadasha_sequence.append({
            'planet': planet,
            'start_date': jd_to_date_daily_report(mahadasha_start_jd),
            'end_date': jd_to_date_daily_report(end_jd),
            'duration_years': duration_years,
            'antardashas': antardashas
        })
        mahadasha_start_jd = end_jd

    return mahadasha_sequence

def find_dasha_levels_at_date_daily_report(mahadasha_periods, target_jd):
    """Find all dasha levels at a specific date in proper hierarchical sequence."""
    
    for mahadasha in mahadasha_periods:
        maha_start_jd = date_str_to_jd_daily_report(mahadasha['start_date'].split()[0])
        maha_end_jd = date_str_to_jd_daily_report(mahadasha['end_date'].split()[0])
        
        if maha_start_jd <= target_jd < maha_end_jd:
            
            for antardasha in mahadasha['antardashas']:
                antar_start_jd = date_str_to_jd_daily_report(antardasha['start_date'].split()[0])
                antar_end_jd = date_str_to_jd_daily_report(antardasha['end_date'].split()[0])
                
                if antar_start_jd <= target_jd < antar_end_jd:
                    
                    for pratyantardasha in antardasha['pratyantardashas']:
                        pratyantar_start_jd = date_str_to_jd_daily_report(pratyantardasha['start_date'].split()[0])
                        pratyantar_end_jd = date_str_to_jd_daily_report(pratyantardasha['end_date'].split()[0])
                        
                        if pratyantar_start_jd <= target_jd < pratyantar_end_jd:
                            
                            for sookshma in pratyantardasha['sookshma_dashas']:
                                sookshma_start_jd = date_str_to_jd_daily_report(sookshma['start_date'].split()[0])
                                sookshma_end_jd = date_str_to_jd_daily_report(sookshma['end_date'].split()[0])
                                
                                if sookshma_start_jd <= target_jd < sookshma_end_jd:
                                    
                                    for pran in sookshma['pran_dashas']:
                                        pran_start_jd = date_str_to_jd_daily_report(pran['start_date'].split()[0])
                                        pran_end_jd = date_str_to_jd_daily_report(pran['end_date'].split()[0])
                                        
                                        if pran_start_jd <= target_jd < pran_end_jd:
                                            
                                            # Create dasha sequence string
                                            dasha_sequence = f"{mahadasha['planet']} > {antardasha['planet']} > {pratyantardasha['planet']} > {sookshma['planet']} > {pran['planet']}"
                                            
                                            # CRITICAL: Build as list of tuples to maintain order
                                            levels = [
                                                ('mahadasha', {
                                                    'planet': mahadasha['planet'],
                                                    'start_date': mahadasha['start_date'],
                                                    'end_date': mahadasha['end_date'],
                                                    'duration_years': mahadasha['duration_years']
                                                }),
                                                ('antardasha', {
                                                    'planet': antardasha['planet'],
                                                    'start_date': antardasha['start_date'],
                                                    'end_date': antardasha['end_date'],
                                                    'duration_years': antardasha['duration_years']
                                                }),
                                                ('pratyantardasha', {
                                                    'planet': pratyantardasha['planet'],
                                                    'start_date': pratyantardasha['start_date'],
                                                    'end_date': pratyantardasha['end_date'],
                                                    'duration_days': pratyantardasha['duration_days']
                                                }),
                                                ('sookshma', {
                                                    'planet': sookshma['planet'],
                                                    'start_date': sookshma['start_date'],
                                                    'end_date': sookshma['end_date'],
                                                    'duration_days': sookshma['duration_days']
                                                }),
                                                ('pran', {
                                                    'planet': pran['planet'],
                                                    'start_date': pran['start_date'],
                                                    'end_date': pran['end_date'],
                                                    'duration_hours': pran['duration_hours']
                                                })
                                            ]
                                            
                                            return {
                                                'dasha_sequence': dasha_sequence,
                                                'levels': levels
                                            }
    return None