import os
import swisseph as swe
from datetime import datetime, timedelta

# ==========================================
# CONFIGURATION
# ==========================================
# Ensure this path points to your actual Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS: PDF RULE (Vimshottari * 2/3)
# ==========================================
# Standard Vimshottari Years
VIMSHOTTARI_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

# Scaling Factor: 2/3 (Standard 120y becomes 80y cycle)
SCALE_FACTOR = 2.0 / 3.0 

# Scaled Years (e.g. Jupiter = 10.666...)
DASHA_YEARS_SCALED = {k: v * SCALE_FACTOR for k, v in VIMSHOTTARI_YEARS.items()}
TOTAL_CYCLE_YEARS = sum(DASHA_YEARS_SCALED.values()) # Should be 80.0

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
] * 3 

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 
    'Venus': swe.VENUS, 'Saturn': swe.SATURN, 
    'Rahu': swe.MEAN_NODE, 'Ketu': None 
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                    dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    return jd

def get_nakshatra_info(moon_lon):
    nak_span = 360 / 27.0
    nak_index = int(moon_lon / nak_span)
    degree_in_nak = moon_lon % nak_span
    fraction_passed = degree_in_nak / nak_span
    
    lord = NAKSHATRA_LORDS[nak_index]
    
    return {
        'lord': lord,
        'lord_index_in_order': DASHA_ORDER.index(lord),
        'fraction_left': 1.0 - fraction_passed,
        'fraction_passed': fraction_passed
    }

def calculate_antardashas(md_lord, start_date, filter_start_date=None):
    """
    Calculates Antardashas.
    If filter_start_date is provided (for Balance Dasha), 
    it only returns Antardashas that cover the period starting from birth.
    """
    sub_periods = []
    
    # 1. Get scaled duration of the main Mahadasha lord
    md_years = DASHA_YEARS_SCALED[md_lord]
    
    # 2. Find start index for Antardashas (starts with MD lord itself)
    md_idx = DASHA_ORDER.index(md_lord)
    
    current_ad_date = start_date
    
    for i in range(9):
        # Cyclical order of sub-lords
        ad_lord_idx = (md_idx + i) % 9
        ad_lord = DASHA_ORDER[ad_lord_idx]
        
        # Duration of sub-lord
        ad_years_val = DASHA_YEARS_SCALED[ad_lord]
        
        # Formula: (MD * AD) / Total_Cycle
        # Using scaled total (80) because MD and AD are already scaled
        ad_duration_years = (md_years * ad_years_val) / TOTAL_CYCLE_YEARS
        
        ad_days = ad_duration_years * 365.2425
        ad_end_date = current_ad_date + timedelta(days=ad_days)
        
        # --- Filtering Logic for Balance Dasha ---
        if filter_start_date:
            # Case A: This sub-period ended before birth. Skip it.
            if ad_end_date <= filter_start_date:
                current_ad_date = ad_end_date
                continue
            
            # Case B: This sub-period spans across birth. 
            # We clip the start date to be the birth date.
            actual_start = current_ad_date
            if actual_start < filter_start_date:
                actual_start = filter_start_date
                
            # Recalculate duration for the remaining part (display only)
            # We don't change mathematical end date, just the displayed start
            display_duration = (ad_end_date - actual_start).days / 365.2425
            
            sub_periods.append({
                'lord': ad_lord,
                'start': actual_start.strftime("%Y-%m-%d"),
                'end': ad_end_date.strftime("%Y-%m-%d"),
                'duration_years': round(display_duration, 5)
            })
        else:
            # --- Standard Logic for Full Dashas ---
            sub_periods.append({
                'lord': ad_lord,
                'start': current_ad_date.strftime("%Y-%m-%d"),
                'end': ad_end_date.strftime("%Y-%m-%d"),
                'duration_years': round(ad_duration_years, 5)
            })
        
        current_ad_date = ad_end_date
        
    return sub_periods

def calculate_dasha_periods(birth_date_obj, moon_lon):
    """
    Core function to calculate the full dasha cycle.
    """
    nak_info = get_nakshatra_info(moon_lon)
    current_lord = nak_info['lord']
    start_idx = nak_info['lord_index_in_order']
    
    # Define Target End Date (Birth + 120 Years)
    # Even though cycle is 80y, traditional display might show multiple cycles or up to life expectancy
    target_end_date = birth_date_obj + timedelta(days=120 * 365.2425)

    # --- 1. CALCULATE BALANCE DASHA ---
    
    full_duration = DASHA_YEARS_SCALED[current_lord]
    
    # Years remaining at birth
    balance_years = full_duration * nak_info['fraction_left']
    balance_days = balance_years * 365.2425
    
    # Years passed BEFORE birth (needed for Antardasha back-calculation)
    passed_years = full_duration * nak_info['fraction_passed']
    passed_days = passed_years * 365.2425
    
    # Theoretical start date (Before Birth)
    hypothetical_start = birth_date_obj - timedelta(days=passed_days)
    balance_end_date = birth_date_obj + timedelta(days=balance_days)
    
    # Get Sub-periods for Balance (Filtered)
    balance_antars = calculate_antardashas(
        current_lord, 
        hypothetical_start, 
        filter_start_date=birth_date_obj
    )

    dashas = []
    
    # Add Balance Dasha
    dashas.append({
        'lord': current_lord,
        'type': 'Balance (Birth)',
        'start': birth_date_obj.strftime("%Y-%m-%d"),
        'end': balance_end_date.strftime("%Y-%m-%d"),
        'duration_years': round(balance_years, 4),
        'antardashas': balance_antars
    })
    
    # --- 2. CALCULATE SUBSEQUENT DASHAS (Loop until 120 years) ---
    
    curr_idx = (start_idx + 1) % 9
    current_date = balance_end_date
    
    # Continue adding Dashas until we exceed the target 120-year date
    while current_date < target_end_date:
        lord_name = DASHA_ORDER[curr_idx]
        dasha_yrs = DASHA_YEARS_SCALED[lord_name]
        
        start_date_str = current_date.strftime("%Y-%m-%d")
        dasha_days = dasha_yrs * 365.2425
        end_date = current_date + timedelta(days=dasha_days)
        
        # Get Sub-periods for Full Dasha
        antars = calculate_antardashas(lord_name, current_date)
        
        dashas.append({
            'lord': lord_name,
            'type': 'Full',
            'start': start_date_str,
            'end': end_date.strftime("%Y-%m-%d"),
            'duration_years': round(dasha_yrs, 4),
            'antardashas': antars
        })
        
        current_date = end_date
        # Move to next planet (wrap around using modulo)
        curr_idx = (curr_idx + 1) % 9
        
    return dashas

def tribhgi_dasha_calculation(data):
    """
    Main logic function used by the API.
    """
    lat = float(data['latitude'])
    lon = float(data['longitude'])
    tz = float(data['timezone_offset'])
    
    # Julian Day & Birth DateTime
    jd = get_julian_day(data['birth_date'], data['birth_time'], tz)
    birth_dt = datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M:%S")

    # Set Ayanamsa
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # Calculate Planets
    planets_data = {}
    moon_lon = 0
    
    # Ascendant for House Calculation
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_sign_index = int(ascmc[0] / 30)

    for name, pid in PLANETS.items():
        if pid is None: continue 
        # Calculate position
        res = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        longitude = res[0][0]
        if name == 'Moon': moon_lon = longitude
        
        planets_data[name] = {
            "longitude": longitude,
            "sign": ZODIAC_SIGNS[int(longitude / 30)],
            "house_whole_sign": ((int(longitude/30) - asc_sign_index + 12) % 12) + 1
        }

    # Calculate Ketu
    rahu_lon = planets_data['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    planets_data['Ketu'] = {
        "longitude": ketu_lon,
        "sign": ZODIAC_SIGNS[int(ketu_lon / 30)],
        "house_whole_sign": ((int(ketu_lon/30) - asc_sign_index + 12) % 12) + 1
    }

    # Calculate Dasha
    dasha_schedule = calculate_dasha_periods(birth_dt, moon_lon)
    
    result = {
        "status": "success",
        "system": "Tribhagi (2/3 Scaling Variation) - 120 Year Cycle",
        "data": {
            "moon_longitude": moon_lon,
            "nakshatra_lord": get_nakshatra_info(moon_lon)['lord'],
            "dashas": dasha_schedule,
            "planetary_positions": planets_data
        }
    }
    
    return result