import swisseph as swe
from datetime import datetime, timedelta
from math import floor
from copy import deepcopy

# Set Swiss Ephemeris path (adjust path as needed)
swe.set_ephe_path('astro_api/ephe')

# Nakshatra details: name, start degree, ruling planet
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

# Planet durations for Mahadasha in years
PLANET_DURATIONS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

# Fixed order of planets for sequence
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

def get_julian_day_three_months(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in Universal Time (UT)."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_moon_sidereal_position_three_months(jd):
    """Calculate the Moon's sidereal longitude using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    moon_sidereal = (moon_tropical - ayanamsa) % 360
    return moon_sidereal

def get_nakshatra_and_lord_three_months(moon_longitude):
    """Determine the nakshatra, its ruling planet, and start longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < (start + 13.333):
            return nakshatra, lord, start
    if moon_longitude >= 346.666 or moon_longitude < 0:
        return "Revati", "Mercury", 346.666
    return None, None, None

def calculate_dasha_balance_three_months(moon_longitude, nakshatra_start, lord):
    """Calculate the remaining balance and elapsed time of the starting Mahadasha."""
    nakshatra_span = 13.333
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360
    fraction_elapsed = degrees_in_nakshatra / nakshatra_span
    mahadasha_duration = PLANET_DURATIONS[lord]
    elapsed_time = mahadasha_duration * fraction_elapsed
    remaining_time = mahadasha_duration - elapsed_time
    return remaining_time, mahadasha_duration, elapsed_time

def calculate_sookshma_dashas_three_months(pratyantardasha_planet, pratyantardasha_start_date, pratyantardasha_end_date):
    """Calculate Sookshma Dashas for a given Pratyantardasha with precise date adjustments."""
    sookshma_dashas = []
    pd_start_date = datetime.strptime(pratyantardasha_start_date, "%Y-%m-%d")
    pd_end_date = datetime.strptime(pratyantardasha_end_date, "%Y-%m-%d")
    pd_duration_days = (pd_end_date - pd_start_date).days
    sd_start_date = pd_start_date
    start_idx = PLANET_ORDER.index(pratyantardasha_planet)
    total_cycle = 120  # Total Vimshottari cycle in years

    for i in range(9):
        sd_planet = PLANET_ORDER[(start_idx + i) % 9]
        sd_duration_days = (pd_duration_days * PLANET_DURATIONS[sd_planet]) / total_cycle
        sd_end_date = sd_start_date + timedelta(days=sd_duration_days)

        # Adjust the last Sookshma Dasha's end date to match Pratyantardasha's end date
        if i == 8:
            sd_end_date = pd_end_date

        sookshma_dashas.append({
            'planet': sd_planet,
            'start_date': sd_start_date.strftime("%Y-%m-%d"),
            'end_date': sd_end_date.strftime("%Y-%m-%d"),
            'duration_days': round((sd_end_date - sd_start_date).total_seconds() / (24 * 3600), 2)
        })
        sd_start_date = sd_end_date

    return sookshma_dashas

def calculate_pratyantardashas_three_months(antardasha_planet, antardasha_duration_years, start_date, antardasha_end_date):
    """Calculate Pratyantardashas with nested Sookshma Dashas."""
    pratyantardashas = []
    pd_start_date = start_date
    start_idx = PLANET_ORDER.index(antardasha_planet)
    
    for i in range(9):
        pd_planet = PLANET_ORDER[(start_idx + i) % 9]
        pd_duration_years = (antardasha_duration_years * PLANET_DURATIONS[pd_planet]) / 120
        pd_duration_days = pd_duration_years * 365.25
        pd_end_date = pd_start_date + timedelta(days=pd_duration_days)
        
        if i == 8:
            pd_end_date = antardasha_end_date
        
        sookshma_dashas = calculate_sookshma_dashas_three_months(pd_planet, pd_start_date.strftime("%Y-%m-%d"), pd_end_date.strftime("%Y-%m-%d"))
        
        pratyantardashas.append({
            'planet': pd_planet,
            'start_date': pd_start_date.strftime("%Y-%m-%d"),
            'end_date': pd_end_date.strftime("%Y-%m-%d"),
            'sookshma_dashas': sookshma_dashas
        })
        pd_start_date = pd_end_date
    
    return pratyantardashas

def calculate_antardashas_three_months(mahadasha_planet, mahadasha_duration, start_date, elapsed_time=0):
    """Calculate Antardashas with nested Pratyantardashas and Sookshma Dashas."""
    antardashas = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    total_cycle = 120
    start_idx = PLANET_ORDER.index(mahadasha_planet)
    
    antardasha_durations = []
    for i in range(9):
        antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = (mahadasha_duration * PLANET_DURATIONS[antardasha_planet]) / total_cycle
        antardasha_durations.append(duration)
    
    cumulative_duration = 0
    for i in range(9):
        cumulative_duration += antardasha_durations[i]
        if cumulative_duration > elapsed_time:
            start_antardasha_idx = i
            time_already_elapsed = elapsed_time - (cumulative_duration - antardasha_durations[i])
            remaining_in_antardasha = antardasha_durations[i] - time_already_elapsed
            break
    
    for i in range(start_antardasha_idx, 9):
        antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
        if i == start_antardasha_idx:
            duration = remaining_in_antardasha
        else:
            duration = antardasha_durations[i]
        end_date = current_date + timedelta(days=duration * 365.25)
        
        pratyantardashas = calculate_pratyantardashas_three_months(antardasha_planet, duration, current_date, end_date)
        
        antardashas.append({
            "planet": antardasha_planet,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 4),
            "pratyantardashas": pratyantardashas
        })
        current_date = end_date
    
    return antardashas

def calculate_mahadasha_periods_three_months(birth_date, remaining_time, starting_planet, elapsed_time):
    """Calculate Mahadasha periods with nested Antardashas, Pratyantardashas, and Sookshma Dashas."""
    mahadasha_sequence = []
    current_planet_idx = PLANET_ORDER.index(starting_planet)
    current_date = datetime.strptime(birth_date, "%Y-%m-%d")
    
    for i in range(9):
        current_planet = PLANET_ORDER[current_planet_idx]
        mahadasha_duration = PLANET_DURATIONS[current_planet]
        if i == 0:
            mahadasha_duration = remaining_time
            elapsed_for_antardashas = elapsed_time
        else:
            elapsed_for_antardashas = 0
        
        end_date = current_date + timedelta(days=mahadasha_duration * 365.25)
        
        antardashas = calculate_antardashas_three_months(current_planet, mahadasha_duration, current_date.strftime("%Y-%m-%d"), elapsed_for_antardashas)
        
        mahadasha_sequence.append({
            "planet": current_planet,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(mahadasha_duration, 4),
            "antardashas": antardashas
        })
        
        current_date = end_date
        current_planet_idx = (current_planet_idx + 1) % 9
    
    return mahadasha_sequence

def filter_mahadashas_three_months(mahadasha_periods, current_date, end_date):
    """
    Filter Mahadasha periods to include only those overlapping with the specified date range.
    Includes nested filtering for Antardashas, Pratyantardashas, and Sookshma Dashas.
    
    Args:
        mahadasha_periods: List of all Mahadasha periods
        current_date: Start date of filter range (datetime object)
        end_date: End date of filter range (datetime object)
    
    Returns:
        Filtered list of Mahadasha periods
    """
    filtered_mahadashas = []
    
    for maha in mahadasha_periods:
        maha_start = datetime.strptime(maha['start_date'], "%Y-%m-%d")
        maha_end = datetime.strptime(maha['end_date'], "%Y-%m-%d")
        
        # Check if Mahadasha overlaps with date range
        if maha_end < current_date or maha_start > end_date:
            continue
        
        # Create filtered Mahadasha copy
        filtered_maha = deepcopy(maha)
        filtered_maha['antardashas'] = []
        
        # Filter Antardashas
        for antar in maha.get('antardashas', []):
            antar_start = datetime.strptime(antar['start_date'], "%Y-%m-%d")
            antar_end = datetime.strptime(antar['end_date'], "%Y-%m-%d")
            
            if antar_end < current_date or antar_start > end_date:
                continue
            
            # Create filtered Antardasha copy
            filtered_antar = {
                'planet': antar['planet'],
                'start_date': antar['start_date'],
                'end_date': antar['end_date'],
                'duration_years': antar['duration_years'],
                'pratyantardashas': []
            }
            
            # Filter Pratyantardashas
            for pratya in antar.get('pratyantardashas', []):
                pratya_start = datetime.strptime(pratya['start_date'], "%Y-%m-%d")
                pratya_end = datetime.strptime(pratya['end_date'], "%Y-%m-%d")
                
                if pratya_end < current_date or pratya_start > end_date:
                    continue
                
                # Create filtered Pratyantardasha copy
                filtered_pratya = {
                    'planet': pratya['planet'],
                    'start_date': pratya['start_date'],
                    'end_date': pratya['end_date'],
                    'sookshma_dashas': []
                }
                
                # Filter Sookshma Dashas
                for sookshma in pratya.get('sookshma_dashas', []):
                    sookshma_start = datetime.strptime(sookshma['start_date'], "%Y-%m-%d")
                    sookshma_end = datetime.strptime(sookshma['end_date'], "%Y-%m-%d")
                    
                    if sookshma_end < current_date or sookshma_start > end_date:
                        continue
                    
                    # Add Sookshma Dasha to filtered result
                    filtered_pratya['sookshma_dashas'].append(sookshma)
                
                # Only add Pratyantardasha if it has Sookshma Dashas
                if filtered_pratya['sookshma_dashas']:
                    filtered_antar['pratyantardashas'].append(filtered_pratya)
            
            # Only add Antardasha if it has Pratyantardashas
            if filtered_antar['pratyantardashas']:
                filtered_maha['antardashas'].append(filtered_antar)
        
        # Only add Mahadasha if it has Antardashas
        if filtered_maha['antardashas']:
            filtered_mahadashas.append(filtered_maha)
    
    return filtered_mahadashas