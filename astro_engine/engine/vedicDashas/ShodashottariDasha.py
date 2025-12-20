"""
Shodashottari Dasha - Calculation Module
=========================================
Vedic Astrology Dasha System - 8-Planet System (116-year cycle)

Features:
- 8-planet system (Sun, Mars, Jupiter, Saturn, Ketu, Moon, Mercury, Venus)
- 116-year complete cycle
- Modulo 8 nakshatra lordship pattern
- Balance calculation at birth
- Mahadasha and Antardasha periods
- Applicability check (Day/Night birth + Odd/Even Lagna)
- Lahiri Ayanamsa
- Whole Sign house system
"""

from datetime import datetime, timedelta
import swisseph as swe

# =====================================================
# SHODASHOTTARI DASHA CONFIGURATION (8-Planet System)
# =====================================================

# Planetary sequence in Shodashottari Dasha
SHODASHOTTARI_SEQUENCE = ['Sun', 'Mars', 'Jupiter', 'Saturn', 'Ketu', 'Moon', 'Mercury', 'Venus']

# Years allotted to each planet (Total = 116 years)
SHODASHOTTARI_YEARS = {
    'Sun': 11,
    'Mars': 12,
    'Jupiter': 13,
    'Saturn': 14,
    'Ketu': 15,
    'Moon': 16,
    'Mercury': 17,
    'Venus': 18
}

TOTAL_YEARS = 116  # Complete Dasha cycle

# Nakshatra names (27 nakshatras)
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# =====================================================
# CORRECT NAKSHATRA LORDSHIP FOR SHODASHOTTARI DASHA
# Using MODULO 8 arithmetic pattern
# =====================================================

# Nakshatra lordship sequence (cyclic starting from Mars)
# Main sequence: Sun → Mars → Jupiter → Saturn → Ketu → Moon → Mercury → Venus
# Nakshatra sequence: Mars → Jupiter → Saturn → Ketu → Moon → Mercury → Venus → Sun
NAKSHATRA_LORD_SEQUENCE = ['Mars', 'Jupiter', 'Saturn', 'Ketu', 'Moon', 'Mercury', 'Venus', 'Sun']

def get_nakshatra_lord(nakshatra_number):
    """
    Get Shodashottari Dasha lord for a nakshatra using modulo 8 pattern
    
    Formula: Lord = NAKSHATRA_LORD_SEQUENCE[nakshatra_number % 8]
    
    Args:
        nakshatra_number: Nakshatra index (0-26)
    
    Returns:
        Planet name (string)
    
    Examples:
        Vishakha (15): 15 % 8 = 7 → Sun
        Shatabhisha (23): 23 % 8 = 7 → Sun
        Ashwini (0): 0 % 8 = 0 → Mars
    """
    return NAKSHATRA_LORD_SEQUENCE[nakshatra_number % 8]

# Sign names
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_julian_day(year, month, day, hour, minute, second, timezone_offset):
    """Calculate Julian Day in UTC"""
    dt = datetime(year, month, day, hour, minute, second)
    utc_dt = dt - timedelta(hours=timezone_offset)
    time_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, time_decimal)
    return jd

def get_planet_longitude(jd, planet_id):
    """Get sidereal longitude of a planet using Lahiri ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
    longitude = result[0][0]
    return longitude

def get_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant using Lahiri ayanamsa and Whole Sign houses"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.houses(jd, latitude, longitude, b'W')
    ascendant = result[1][0]
    return ascendant

def years_to_ymd(decimal_years):
    """Convert decimal years to Years-Months-Days"""
    total_days = decimal_years * 365.25
    years = int(total_days / 365.25)
    remaining = total_days - (years * 365.25)
    months = int(remaining / 30.4375)
    remaining = remaining - (months * 30.4375)
    days = int(remaining)
    return years, months, days

def add_years_to_date(date, decimal_years):
    """Add decimal years to a datetime object"""
    days = decimal_years * 365.25
    return date + timedelta(days=days)

# =====================================================
# CORE DASHA CALCULATION FUNCTIONS
# =====================================================

def get_moon_nakshatra_details(jd):
    """
    Calculate Moon's nakshatra and position within it
    
    Returns:
        Dictionary with nakshatra details including:
        - nakshatra_number (0-26)
        - nakshatra_name
        - moon_longitude
        - fraction_traversed (0.0-1.0)
    """
    moon_long = get_planet_longitude(jd, swe.MOON)
    
    nakshatra_span = 360.0 / 27.0  # 13.333333°
    nakshatra_num = int(moon_long / nakshatra_span)
    degrees_traversed = moon_long % nakshatra_span
    fraction_traversed = degrees_traversed / nakshatra_span
    
    return {
        'nakshatra_number': nakshatra_num,
        'nakshatra_name': NAKSHATRAS[nakshatra_num],
        'moon_longitude': moon_long,
        'degrees_in_nakshatra': degrees_traversed,
        'fraction_traversed': fraction_traversed,
        'arc_minutes_traversed': degrees_traversed * 60.0,
        'total_arc_minutes': nakshatra_span * 60.0
    }

def calculate_dasha_balance(nakshatra_info):
    """
    Calculate balance of Mahadasha at birth
    
    Formula: Balance Years = Total Dasha Years × (1 - Fraction Traversed)
    
    Logic:
        Moon's position in nakshatra indicates how much Dasha has elapsed.
        If Moon has traversed 35% of nakshatra:
            - 35% of Dasha period has elapsed before birth
            - 65% remains as balance at birth
    
    Example:
        Moon in Shatabhisha (23) at 35.73% traversed
        Nakshatra lord: 23 % 8 = 7 → Sun (11 years)
        Elapsed: 35.73% × 11 = 3.93 years
        Balance: 64.27% × 11 = 7.07 years
    """
    nakshatra_num = nakshatra_info['nakshatra_number']
    fraction = nakshatra_info['fraction_traversed']
    
    # Get Dasha lord using modulo 8 pattern
    dasha_lord = get_nakshatra_lord(nakshatra_num)
    
    # Get total years for this Dasha lord
    total_years = SHODASHOTTARI_YEARS[dasha_lord]
    
    # Calculate balance (remaining years at birth)
    balance_years = total_years * (1.0 - fraction)
    
    return {
        'dasha_lord': dasha_lord,
        'total_years': total_years,
        'balance_years': balance_years,
        'elapsed_fraction': fraction,
        'remaining_fraction': 1.0 - fraction
    }

def calculate_mahadasha_periods(birth_date, balance_info):
    """
    Calculate all 8 Mahadasha periods
    
    Returns:
        List of 8 Mahadasha periods:
        - Period 1: Balance of birth Dasha lord
        - Periods 2-8: Complete cycles of next 7 planets in sequence
    """
    mahadashas = []
    
    starting_lord = balance_info['dasha_lord']
    balance_years = balance_info['balance_years']
    start_idx = SHODASHOTTARI_SEQUENCE.index(starting_lord)
    
    current_date = birth_date
    
    # Period 1: Balance of birth Dasha
    end_date = add_years_to_date(current_date, balance_years)
    y, m, d = years_to_ymd(balance_years)
    
    mahadashas.append({
        'planet': starting_lord,
        'start_date': current_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'duration_years': round(balance_years, 6),
        'duration_ymd': {'years': y, 'months': m, 'days': d},
        'is_balance': True
    })
    
    current_date = end_date
    
    # Periods 2-8: Complete Dasha cycles
    for i in range(1, 8):
        planet_idx = (start_idx + i) % 8
        planet = SHODASHOTTARI_SEQUENCE[planet_idx]
        years = SHODASHOTTARI_YEARS[planet]
        
        end_date = add_years_to_date(current_date, years)
        y, m, d = years_to_ymd(years)
        
        mahadashas.append({
            'planet': planet,
            'start_date': current_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'duration_years': years,
            'duration_ymd': {'years': y, 'months': m, 'days': d},
            'is_balance': False
        })
        
        current_date = end_date
    
    return mahadashas

def calculate_antardasha_periods(maha_planet, maha_start_date, maha_duration_years, is_balance):
    """
    Calculate Antardasha periods with proper balance handling
    
    Formula: Antardasha Duration = (Mahadasha Years × Antardasha Base Years) / 116
    
    CRITICAL LOGIC FOR BALANCE MAHADASHA:
    When is_balance = True:
        1. Calculate elapsed = total - balance
        2. Build all Antardasha durations with cumulative sums
        3. Find which Antardasha is active at birth
        4. Calculate balance of that Antardasha
        5. Return only remaining Antardashas from birth point
    """
    maha_idx = SHODASHOTTARI_SEQUENCE.index(maha_planet)
    maha_total_years = SHODASHOTTARI_YEARS[maha_planet]
    
    # Calculate all Antardasha durations with cumulative sums
    antar_details = []
    cumulative = 0.0
    
    for i in range(8):
        antar_idx = (maha_idx + i) % 8
        antar_planet = SHODASHOTTARI_SEQUENCE[antar_idx]
        antar_base_years = SHODASHOTTARI_YEARS[antar_planet]
        antar_duration = (maha_total_years * antar_base_years) / TOTAL_YEARS
        cumulative += antar_duration
        
        antar_details.append({
            'index': i,
            'planet': antar_planet,
            'duration': antar_duration,
            'cumulative': cumulative
        })
    
    # Determine starting point
    if is_balance:
        elapsed_years = maha_total_years - maha_duration_years
        
        # Find which Antardasha is active at birth
        start_antar_idx = 0
        elapsed_in_current_antar = 0.0
        
        for i, antar in enumerate(antar_details):
            if elapsed_years <= antar['cumulative']:
                start_antar_idx = i
                if i == 0:
                    elapsed_in_current_antar = elapsed_years
                else:
                    elapsed_in_current_antar = elapsed_years - antar_details[i-1]['cumulative']
                break
        
        current_antar = antar_details[start_antar_idx]
        balance_of_current_antar = current_antar['duration'] - elapsed_in_current_antar
    else:
        start_antar_idx = 0
        balance_of_current_antar = antar_details[0]['duration']
    
    # Build Antardasha list (only remaining ones)
    antardashas = []
    current_date = datetime.strptime(maha_start_date, '%Y-%m-%d')
    
    for i in range(start_antar_idx, 8):
        antar_planet = antar_details[i]['planet']
        
        if i == start_antar_idx and is_balance:
            duration = balance_of_current_antar
        else:
            duration = antar_details[i]['duration']
        
        end_date = add_years_to_date(current_date, duration)
        y, m, d = years_to_ymd(duration)
        
        antardashas.append({
            'planet': antar_planet,
            'start_date': current_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'duration_years': round(duration, 6),
            'duration_ymd': {'years': y, 'months': m, 'days': d}
        })
        
        current_date = end_date
    
    return antardashas

def check_shodashottari_applicability(jd, latitude, longitude):
    """
    Check if Shodashottari Dasha is applicable
    
    Rule: (Day Birth + Odd Lagna) OR (Night Birth + Even Lagna)
    """
    sun_long = get_planet_longitude(jd, swe.SUN)
    asc_long = get_ascendant(jd, latitude, longitude)
    
    lagna_sign_num = int(asc_long / 30.0) + 1
    lagna_sign_name = SIGNS[(lagna_sign_num - 1) % 12]
    is_lagna_odd = (lagna_sign_num % 2 == 1)
    
    sun_sign_num = int(sun_long / 30.0)
    asc_sign_num = int(asc_long / 30.0)
    sun_house = ((sun_sign_num - asc_sign_num) % 12) + 1
    
    is_day_birth = (sun_house <= 6)
    is_applicable = (is_day_birth and is_lagna_odd) or (not is_day_birth and not is_lagna_odd)
    
    return {
        'is_applicable': is_applicable,
        'is_day_birth': is_day_birth,
        'birth_time': 'Day' if is_day_birth else 'Night',
        'lagna_sign_number': lagna_sign_num,
        'lagna_sign_name': lagna_sign_name,
        'is_lagna_odd': is_lagna_odd,
        'lagna_type': 'Odd' if is_lagna_odd else 'Even',
        'ascendant_degree': round(asc_long, 6),
        'sun_longitude': round(sun_long, 6),
        'sun_house': sun_house,
        'rule': f"{'Day' if is_day_birth else 'Night'} Birth + {'Odd' if is_lagna_odd else 'Even'} Lagna = {'Applicable' if is_applicable else 'Not Applicable'}"
    }

# =====================================================
# MAIN CALCULATION ORCHESTRATION
# =====================================================

def calculate_shodashottari_dasha(data):
    """
    Main function to calculate Shodashottari Dasha system
    
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
    dict: Complete Shodashottari Dasha calculations
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date_str = data.get('birth_date')
    birth_time_str = data.get('birth_time')
    latitude = float(data.get('latitude'))
    longitude = float(data.get('longitude'))
    timezone_offset = float(data.get('timezone_offset'))
    
    birth_dt = datetime.strptime(f"{birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M:%S")
    
    jd = get_julian_day(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour, birth_dt.minute, birth_dt.second,
        timezone_offset
    )
    
    applicability = check_shodashottari_applicability(jd, latitude, longitude)
    moon_nakshatra = get_moon_nakshatra_details(jd)
    dasha_balance = calculate_dasha_balance(moon_nakshatra)
    mahadashas = calculate_mahadasha_periods(birth_dt, dasha_balance)
    
    for maha in mahadashas:
        maha['antardashas'] = calculate_antardasha_periods(
            maha['planet'],
            maha['start_date'],
            maha['duration_years'],
            maha['is_balance']
        )
    
    bal_y, bal_m, bal_d = years_to_ymd(dasha_balance['balance_years'])
    
    response = {
        'success': True,
        'user_name': user_name,
        'birth_info': {
            'date': birth_date_str,
            'time': birth_time_str,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset,
            'julian_day': round(jd, 6)
        },
        'applicability': applicability,
        'moon_nakshatra': {
            'number': moon_nakshatra['nakshatra_number'] + 1,
            'name': moon_nakshatra['nakshatra_name'],
            'longitude': round(moon_nakshatra['moon_longitude'], 6),
            'degrees_in_nakshatra': round(moon_nakshatra['degrees_in_nakshatra'], 6),
            'fraction_traversed': round(moon_nakshatra['fraction_traversed'], 6),
            'arc_minutes_traversed': round(moon_nakshatra['arc_minutes_traversed'], 4)
        },
        'dasha_balance': {
            'lord': dasha_balance['dasha_lord'],
            'total_years': dasha_balance['total_years'],
            'balance_years': round(dasha_balance['balance_years'], 6),
            'balance_ymd': {'years': bal_y, 'months': bal_m, 'days': bal_d},
            'elapsed_percent': round(dasha_balance['elapsed_fraction'] * 100, 4),
            'remaining_percent': round(dasha_balance['remaining_fraction'] * 100, 4)
        },
        'system_info': {
            'name': 'Shodashottari Dasha (8-Planet System)',
            'cycle_years': TOTAL_YEARS,
            'sequence': SHODASHOTTARI_SEQUENCE,
            'planet_years': SHODASHOTTARI_YEARS,
            'ayanamsa': 'Lahiri',
            'house_system': 'Whole Sign',
            'nakshatra_distribution': 'Modulo 8 Pattern (Mars-Jupiter-Saturn-Ketu-Moon-Mercury-Venus-Sun)'
        },
        'mahadashas': mahadashas
    }
    
    return response