"""
Tribhagi Dasha - Calculation Module
====================================
Vedic Astrology Dasha System - Tribhagi (2/3 Scaling of Vimshottari)

Features:
- Tribhagi Dasha calculation (2/3 of Vimshottari periods)
- 80-year cycle (vs 120-year Vimshottari)
- Janma method (standard - Moon's nakshatra lord)
- Utpanna method (variant - lord + 4 positions)
- Complete Mahadasha and Antardasha periods
- Balance calculation at birth
- Multi-cycle generation
"""

from datetime import datetime, timedelta
import swisseph as swe

# ============================================================================
# CONSTANTS
# ============================================================================

NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20' (13.333...°) per nakshatra
VIMSHOTTARI_TOTAL = 120  # Total Vimshottari cycle in years
TRIBHAGI_SCALING = 2.0 / 3.0  # Tribhagi scaling factor (2/3)
TRIBHAGI_TOTAL = VIMSHOTTARI_TOTAL * TRIBHAGI_SCALING  # 80 years per cycle
TROPICAL_YEAR_DAYS = 365.2425  # Days per tropical year

# Vimshottari Dasha Lords in sequence
DASHA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# Vimshottari periods for each lord (in years)
VIMSHOTTARI_PERIODS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# Zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatra names
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]


# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def calculate_nakshatra_info(moon_longitude):
    """
    Calculate nakshatra details from Moon's sidereal longitude.
    
    Parameters:
        moon_longitude (float): Moon's sidereal longitude in degrees (0-360)
    
    Returns:
        dict: {
            'index': Nakshatra index (0-26),
            'name': Nakshatra name,
            'traversed': Degrees traversed in current nakshatra,
            'remaining': Degrees remaining in current nakshatra,
            'fraction_remaining': Fraction of nakshatra remaining (0-1)
        }
    
    Logic:
        - Divide 360° by 27 nakshatras = 13.333...° per nakshatra
        - Index = floor(longitude / 13.333...)
        - Remaining fraction used for balance calculation
    """
    nakshatra_index = int(moon_longitude / NAKSHATRA_SPAN)
    degrees_in_nakshatra = moon_longitude % NAKSHATRA_SPAN
    degrees_remaining = NAKSHATRA_SPAN - degrees_in_nakshatra
    remaining_fraction = degrees_remaining / NAKSHATRA_SPAN
    
    return {
        'index': nakshatra_index,
        'name': NAKSHATRAS[nakshatra_index] if 0 <= nakshatra_index < 27 else 'Unknown',
        'traversed': degrees_in_nakshatra,
        'remaining': degrees_remaining,
        'fraction_remaining': remaining_fraction
    }


def calculate_dasha_balance(nakshatra_info, dasha_lord_index):
    """
    Calculate the balance (remaining years) of the first Mahadasha at birth.
    
    Parameters:
        nakshatra_info (dict): Nakshatra information from calculate_nakshatra_info()
        dasha_lord_index (int): Index of the Dasha lord (0-8)
    
    Returns:
        float: Remaining years in the first Mahadasha at birth
    
    Logic:
        1. Get the Vimshottari period for the starting lord
        2. Calculate balance in Vimshottari: period × remaining_fraction
        3. Scale to Tribhagi: balance × 2/3
        
    Example:
        If Moon is in Uttara Phalguni with 72.7% remaining:
        - Starting lord: Sun (6 years in Vimshottari)
        - Vimshottari balance: 6 × 0.727 = 4.362 years
        - Tribhagi balance: 4.362 × 2/3 = 2.908 years
    """
    vimshottari_period = VIMSHOTTARI_PERIODS[dasha_lord_index]
    vimshottari_balance = nakshatra_info['fraction_remaining'] * vimshottari_period
    tribhagi_balance_years = vimshottari_balance * TRIBHAGI_SCALING
    
    return tribhagi_balance_years


def calculate_antardasha_periods(maha_lord_index, maha_period_years):
    """
    Calculate all 9 Antardashas for a given Mahadasha.
    
    Parameters:
        maha_lord_index (int): Index of the Mahadasha lord (0-8)
        maha_period_years (float): Total years of the Mahadasha (already Tribhagi-scaled)
    
    Returns:
        list: List of 9 Antardasha dictionaries with lord, years, and days
    
    Logic:
        - Each Mahadasha is divided into 9 Antardashas
        - Antardasha years = (Mahadasha years × Antardasha Vimshottari period) / 120
        - Sequence starts from Mahadasha lord and cycles through all 9 lords
        - NO additional Tribhagi scaling (maha_period_years is already scaled)
        
    Example for Sun Mahadasha (4 years in Tribhagi):
        - Sun-Sun: (4 × 6) / 120 = 0.2 years
        - Sun-Moon: (4 × 10) / 120 = 0.3333 years
        - Sun-Mars: (4 × 7) / 120 = 0.2333 years
        - ... and so on
        - Total: 4.0 years ✓
    
    CRITICAL: Do NOT multiply by TRIBHAGI_SCALING here!
    """
    antardashas = []
    
    for k in range(9):
        antar_index = (maha_lord_index + k) % 9
        antar_lord = DASHA_LORDS[antar_index]
        antar_vimshottari_period = VIMSHOTTARI_PERIODS[antar_index]
        
        # Proportionate Antardasha calculation
        # maha_period_years is ALREADY Tribhagi-scaled
        # Formula: (Maha_years × Antar_Vimshottari_period) / 120
        antar_years = (maha_period_years * antar_vimshottari_period) / VIMSHOTTARI_TOTAL
        antar_days = antar_years * TROPICAL_YEAR_DAYS
        
        antardashas.append({
            'lord': antar_lord,
            'years': antar_years,
            'days': antar_days
        })
    
    return antardashas


def generate_complete_dasha_cycle(birth_datetime, start_lord_index, nakshatra_info, num_cycles=2):
    """
    Generate complete Tribhagi Dasha cycles with all Mahadashas and Antardashas.
    
    Parameters:
        birth_datetime (datetime): Birth date and time (local)
        start_lord_index (int): Starting Mahadasha lord index (0-8)
        nakshatra_info (dict): Nakshatra information
        num_cycles (int): Number of complete 80-year cycles to generate
    
    Returns:
        list: Complete list of Mahadashas with nested Antardashas
    
    Logic Flow:
        1. Calculate balance of first Mahadasha (years remaining at birth)
        2. For each Mahadasha in sequence:
           a. Calculate Tribhagi period (Vimshottari period × 2/3)
           b. If first Mahadasha: adjust start date backwards by elapsed time
           c. Calculate all 9 Antardashas with dates
           d. Move to next Mahadasha lord
        3. Continue for num_cycles complete cycles (default: 2 cycles = 160 years)
    
    Date Calculation:
        - First Mahadasha starts BEFORE birth
        - Elapsed time = Total period - Balance
        - Start date = Birth date - Elapsed days
        - All subsequent Mahadashas start from previous end date
    """
    
    # Calculate initial balance (remaining years at birth)
    balance_years = calculate_dasha_balance(nakshatra_info, start_lord_index)
    balance_days = balance_years * TROPICAL_YEAR_DAYS
    
    dasha_list = []
    current_datetime = birth_datetime
    current_lord_index = start_lord_index
    
    # Total Mahadashas to calculate (9 lords per cycle)
    total_mahadashas = 9 * num_cycles
    
    for i in range(total_mahadashas):
        planet = DASHA_LORDS[current_lord_index]
        vimshottari_period = VIMSHOTTARI_PERIODS[current_lord_index]
        
        # Calculate Tribhagi period (2/3 of Vimshottari)
        tribhagi_period_years = vimshottari_period * TRIBHAGI_SCALING
        tribhagi_period_days = tribhagi_period_years * TROPICAL_YEAR_DAYS
        
        # Handle first Mahadasha (balance calculation)
        if i == 0:
            # This Mahadasha started before birth
            elapsed_days = tribhagi_period_days - balance_days
            start_datetime = birth_datetime - timedelta(days=elapsed_days)
            effective_period_days = tribhagi_period_days
        else:
            # All subsequent Mahadashas start from previous end
            start_datetime = current_datetime
            effective_period_days = tribhagi_period_days
        
        # Calculate Mahadasha end date
        end_datetime = start_datetime + timedelta(days=effective_period_days)
        
        # Calculate all 9 Antardashas for this Mahadasha
        antardashas = calculate_antardasha_periods(current_lord_index, tribhagi_period_years)
        
        # Build Antardasha list with exact dates
        antar_list = []
        antar_current_datetime = start_datetime
        
        for antar_data in antardashas:
            antar_start = antar_current_datetime
            antar_end = antar_start + timedelta(days=antar_data['days'])
            
            antar_list.append({
                'planet': antar_data['lord'],
                'start': antar_start.strftime('%d-%m-%Y'),
                'end': antar_end.strftime('%d-%m-%Y'),
                'years': round(antar_data['years'], 4)
            })
            
            antar_current_datetime = antar_end
        
        # Add Mahadasha to list
        dasha_list.append({
            'planet': planet,
            'start': start_datetime.strftime('%d-%m-%Y'),
            'end': end_datetime.strftime('%d-%m-%Y'),
            'years': round(tribhagi_period_years, 4),
            'balance_at_birth': round(balance_years, 4) if i == 0 else None,
            'antardashas': antar_list,
            'cycle': (i // 9) + 1  # Track which cycle (1, 2, 3...)
        })
        
        # Move to next Mahadasha
        current_datetime = end_datetime
        current_lord_index = (current_lord_index + 1) % 9
    
    return dasha_list


# ============================================================================
# MAIN CALCULATION ORCHESTRATION
# ============================================================================

def calculate_tribhagi_dasha(data):
    """
    Main function to calculate Tribhagi Dasha system
    
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
        - num_cycles: int (optional, default: 2)
    
    Returns:
    --------
    dict: Complete Tribhagi Dasha calculations for Janma and Utpanna methods
    """
    # ====================================================================
    # STEP 1: Extract and parse input data
    # ====================================================================
    user_name = data.get('user_name', 'User')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])
    num_cycles = data.get('num_cycles', 2)  # Default: 2 cycles (160 years)
    
    # Parse birth date and time
    year, month, day = map(int, birth_date.split('-'))
    hour, minute, second = map(int, birth_time.split(':'))
    
    # Create local datetime object
    local_datetime = datetime(year, month, day, hour, minute, second)
    
    # ====================================================================
    # STEP 2: Convert to UTC and calculate Julian Day
    # ====================================================================
    utc_components = swe.utc_time_zone(
        year, month, day, hour, minute, second, timezone_offset
    )
    jd_ut = swe.utc_to_jd(
        utc_components[0], utc_components[1], utc_components[2],
        utc_components[3], utc_components[4], utc_components[5],
        1  # Gregorian calendar flag
    )[1]  # Returns (jd_et, jd_ut) - we use jd_ut
    
    # ====================================================================
    # STEP 3: Set sidereal mode and calculate planetary positions
    # ====================================================================
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)  # Lahiri Ayanamsa
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    
    # Calculate Moon's sidereal longitude
    moon_data = swe.calc_ut(jd_ut, swe.MOON, flags)
    moon_longitude = moon_data[0][0]  # Sidereal longitude in degrees
    
    # Calculate Ascendant (Lagna)
    houses_data = swe.houses_ex(jd_ut, latitude, longitude, b'P', flags)
    ascendant_longitude = houses_data[1][0]  # Ascendant sidereal longitude
    ascendant_sign = SIGNS[int(ascendant_longitude / 30)]
    
    # ====================================================================
    # STEP 4: Calculate nakshatra information
    # ====================================================================
    nakshatra_info = calculate_nakshatra_info(moon_longitude)
    
    # ====================================================================
    # STEP 5: Determine starting Mahadasha lords
    # ====================================================================
    # Janma (#1): Standard method - starts from Moon's nakshatra lord
    janma_start_index = nakshatra_info['index'] % 9
    
    # Utpanna (#2): Variant method - lord + 4 positions
    # Used in some regional/traditional variations
    utpanna_start_index = (nakshatra_info['index'] + 4) % 9
    
    # ====================================================================
    # STEP 6: Generate complete Dasha cycles
    # ====================================================================
    janma_dashas = generate_complete_dasha_cycle(
        local_datetime, 
        janma_start_index, 
        nakshatra_info,
        num_cycles
    )
    
    utpanna_dashas = generate_complete_dasha_cycle(
        local_datetime,
        utpanna_start_index,
        nakshatra_info,
        num_cycles
    )
    
    # ====================================================================
    # STEP 7: Build comprehensive response
    # ====================================================================
    response = {
        'status': 'success',
        'user_name': user_name,
        'birth_details': {
            'date': birth_date,
            'time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset
        },
        'ascendant_sign': ascendant_sign,
        'moon_nakshatra': {
            'index': nakshatra_info['index'],
            'name': nakshatra_info['name'],
            'degrees_traversed': round(nakshatra_info['traversed'], 4),
            'degrees_remaining': round(nakshatra_info['remaining'], 4),
            'fraction_remaining': round(nakshatra_info['fraction_remaining'], 4)
        },
        'cycle_info': {
            'tribhagi_cycle_years': TRIBHAGI_TOTAL,
            'num_cycles_calculated': num_cycles,
            'total_years': TRIBHAGI_TOTAL * num_cycles
        },
        'janma_starting_lord': DASHA_LORDS[janma_start_index],
        'utpanna_starting_lord': DASHA_LORDS[utpanna_start_index],
        'tribhagi_dashas_janma': janma_dashas,
        # 'tribhagi_dashas_utpanna': utpanna_dashas
    }
    
    return response