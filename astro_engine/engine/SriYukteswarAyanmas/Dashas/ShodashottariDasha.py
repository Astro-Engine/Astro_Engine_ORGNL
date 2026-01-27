import os
import math
from datetime import datetime, timedelta
import swisseph as swe

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

KETU_CUSTOM_ID = 101 # Custom ID for internal logic

# Shodashottari Dasha Sequence
# Order: Sun, Mars, Jupiter, Saturn, Ketu, Moon, Mercury, Venus
# Cycle repeats. Total = 116 Years.
SHODASHOTTARI_ORDER = [
    {'planet_id': swe.SUN,       'name': 'Sun',      'years': 11},
    {'planet_id': swe.MARS,      'name': 'Mars',     'years': 12},
    {'planet_id': swe.JUPITER,   'name': 'Jupiter', 'years': 13},
    {'planet_id': swe.SATURN,    'name': 'Saturn',  'years': 14},
    {'planet_id': KETU_CUSTOM_ID,'name': 'Ketu',     'years': 15},
    {'planet_id': swe.MOON,      'name': 'Moon',     'years': 16},
    {'planet_id': swe.MERCURY,   'name': 'Mercury', 'years': 17},
    {'planet_id': swe.VENUS,     'name': 'Venus',    'years': 18}
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def to_decimal_hours(time_str):
    try:
        parts = list(map(float, time_str.split(':')))
        if len(parts) == 2: return parts[0] + parts[1]/60.0
        elif len(parts) == 3: return parts[0] + parts[1]/60.0 + parts[2]/3600.0
    except: return 0.0
    return 0.0

def normalize_degree(deg):
    return deg % 360

def get_julian_day_ut(birth_date, birth_time, tz_offset):
    year, month, day = map(int, birth_date.split('-'))
    dec_time = to_decimal_hours(birth_time)
    
    # Adjust to UT
    # Note: Logic slightly adjusted to ensure precise float hours handling
    dt_local = datetime(year, month, day) + timedelta(hours=dec_time)
    dt_ut = dt_local - timedelta(hours=tz_offset)
    
    # Calculate UT fractional hours for julday
    ut_hours = dt_ut.hour + dt_ut.minute/60.0 + dt_ut.second/3600.0 + dt_ut.microsecond/3600000000.0
    return swe.julday(dt_ut.year, dt_ut.month, dt_ut.day, ut_hours)

def get_body_position_yukteswar(jd, body_id):
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    if body_id == KETU_CUSTOM_ID:
        # Calculate Rahu (Mean Node)
        xx, _ = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        rahu_lon = xx[0]
        # Ketu is Rahu + 180
        return normalize_degree(rahu_lon + 180.0)
    
    xx, _ = swe.calc_ut(jd, body_id, flags)
    return xx[0]

def get_ascendant_yukteswar(jd, lat, lon):
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    # Using 'W' (Whole Sign) or 'P' (Placidus) doesn't affect Asc degree, 
    # but 'P' is safer for general calculations. Using 'W' as per original script.
    cusps, ascmc = swe.houses(jd, lat, lon, b'W')
    return ascmc[0]

# ---------------------------------------------------------
# SHODASHOTTARI LOGIC
# ---------------------------------------------------------

def check_applicability(sun_lon, moon_lon, asc_lon):
    """
    Applicable if:
    1. Krishna Paksha (Waning) + Moon Hora Lagna
    2. Shukla Paksha (Waxing) + Sun Hora Lagna
    """
    angle_sun_to_moon = normalize_degree(moon_lon - sun_lon)
    is_shukla = (0 < angle_sun_to_moon <= 180)
    paksha_str = "Shukla (Waxing)" if is_shukla else "Krishna (Waning)"
    
    sign_index = int(asc_lon / 30)
    degree_in_sign = asc_lon % 30
    
    # Odd Signs (Aries=0, Gemini=2...): 0-15 Sun, 15-30 Moon
    # Even Signs (Taurus=1, Cancer=3...): 0-15 Moon, 15-30 Sun
    is_odd_sign = (sign_index % 2 == 0) 
    
    is_sun_hora = False
    if is_odd_sign:
        if degree_in_sign < 15: is_sun_hora = True
    else:
        if degree_in_sign >= 15: is_sun_hora = True
            
    hora_str = "Sun" if is_sun_hora else "Moon"
    
    applicable = False
    if is_shukla and is_sun_hora: applicable = True
    elif (not is_shukla) and (not is_sun_hora): applicable = True
        
    return applicable, paksha_str, hora_str

def calculate_antardashas(md_planet_idx, md_start_date, birth_date_obj=None, is_birth_dasha=False):
    """
    Calculates Antardashas (Sub-periods).
    Formula: AD Years = (MD Years * AD Planet Years) / 116
    """
    md_planet = SHODASHOTTARI_ORDER[md_planet_idx]
    md_years = md_planet['years']
    
    antardashas = []
    current_ad_start = md_start_date
    
    # In Shodashottari, ADs start with the MD lord and follow the same sequence
    # We iterate through all 8 planets starting from the MD lord
    curr_ad_idx = md_planet_idx
    
    for _ in range(8):
        ad_planet = SHODASHOTTARI_ORDER[curr_ad_idx]
        
        # Calculate Duration
        ad_duration_years = (md_years * ad_planet['years']) / 116.0
        ad_duration_days = ad_duration_years * 365.2425
        
        ad_end_date = current_ad_start + timedelta(days=ad_duration_days)
        
        # Logic to handle Birth Time filtering
        if is_birth_dasha and birth_date_obj:
            if ad_end_date > birth_date_obj:
                # If this AD started before birth, clamp start to birth
                display_start = current_ad_start
                if current_ad_start < birth_date_obj:
                    display_start = birth_date_obj
                
                antardashas.append({
                    "ad_lord": ad_planet['name'],
                    "start_date": display_start.strftime("%Y-%m-%d"),
                    "end_date": ad_end_date.strftime("%Y-%m-%d"),
                })
        else:
            # Standard logic for future Dashas
            antardashas.append({
                "ad_lord": ad_planet['name'],
                "start_date": current_ad_start.strftime("%Y-%m-%d"),
                "end_date": ad_end_date.strftime("%Y-%m-%d"),
            })
            
        # Move to next
        current_ad_start = ad_end_date
        curr_ad_idx = (curr_ad_idx + 1) % 8
        
    return antardashas

def calculate_full_dasha_system(moon_lon, birth_date_str):
    # 1. Nakshatra & Count
    nak_span = 360.0 / 27.0
    nak_index = int(moon_lon / nak_span)
    nak_name = NAKSHATRAS[nak_index]
    
    # Count from Pushya (Index 7)
    PUSHYA_INDEX = 7
    if nak_index >= PUSHYA_INDEX:
        count = (nak_index - PUSHYA_INDEX) + 1
    else:
        count = (27 - PUSHYA_INDEX) + nak_index + 1
        
    # 2. Starting Lord
    remainder = count % 8
    if remainder == 0: remainder = 8
    start_lord_index = remainder - 1
    start_planet = SHODASHOTTARI_ORDER[start_lord_index]
    
    # 3. Balance Calculation
    degrees_traversed = moon_lon % nak_span
    degrees_remaining = nak_span - degrees_traversed
    
    balance_fraction = degrees_remaining / nak_span
    balance_years = balance_fraction * start_planet['years']
    years_passed = start_planet['years'] - balance_years
    
    # 4. Timeline Generation
    timeline = []
    birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d")
    
    # --- A. Birth Mahadasha ---
    # We back-calculate the theoretical start of this MD to get accurate AD dates
    theoretical_start_days = years_passed * 365.2425
    theoretical_md_start = birth_date_obj - timedelta(days=theoretical_start_days)
    md_end_date = birth_date_obj + timedelta(days=balance_years * 365.2425)
    
    # Generate ADs for birth MD
    birth_ads = calculate_antardashas(
        start_lord_index, 
        theoretical_md_start, 
        birth_date_obj, 
        is_birth_dasha=True
    )
    
    timeline.append({
        "mahadasha_lord": start_planet['name'],
        "start_date": birth_date_obj.strftime("%Y-%m-%d"),
        "end_date": md_end_date.strftime("%Y-%m-%d"),
        "duration_years": start_planet['years'],
        "is_balance": True,
        "antardashas": birth_ads
    })
    
    current_date = md_end_date
    
    # --- B. Future Dashas (Generate 1 Cycle) ---
    curr_idx = (start_lord_index + 1) % 8
    
    for _ in range(8):
        p_data = SHODASHOTTARI_ORDER[curr_idx]
        p_years = p_data['years']
        
        md_end_date = current_date + timedelta(days=p_years * 365.2425)
        
        # Generate ADs
        ads = calculate_antardashas(curr_idx, current_date)
        
        timeline.append({
            "mahadasha_lord": p_data['name'],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": md_end_date.strftime("%Y-%m-%d"),
            "duration_years": p_years,
            "is_balance": False,
            "antardashas": ads
        })
        
        current_date = md_end_date
        curr_idx = (curr_idx + 1) % 8
        
    return {
        "birth_nakshatra": nak_name,
        "count_from_pushya": count,
        "timeline": timeline
    }

def shodashottari_dasha_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all calculations, returns result dictionary.
    """
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 1. Astro Calcs
    jd = get_julian_day_ut(birth_date, birth_time, tz)
    sun = get_body_position_yukteswar(jd, swe.SUN)
    moon = get_body_position_yukteswar(jd, swe.MOON)
    asc = get_ascendant_yukteswar(jd, lat, lon)
    
    # 2. Applicability
    is_app, paksha, hora = check_applicability(sun, moon, asc)
    
    # 3. Dasha + Antardasha
    dasha_data = calculate_full_dasha_system(moon, birth_date)
    
    result = {
        "status": "success",
        "metadata": {
            "name": user_name,
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_val": swe.get_ayanamsa_ut(jd)
        },
        "applicability": {
            "status": is_app,
            "details": f"Paksha: {paksha}, Hora: {hora}"
        },
        "shodashottari_dasha": dasha_data
    }
    
    return result