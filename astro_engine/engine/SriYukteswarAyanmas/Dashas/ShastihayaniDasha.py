import os
import math
import datetime
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
# Path to Swiss Ephemeris
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Sri Yukteswar Ayanamsa ID
AYANAMSA_MODE = swe.SIDM_YUKTESHWAR

# ==========================================
# SHASTIHAYANI CONFIGURATION (GROUP SYSTEM)
# ==========================================
# Total Cycle: 60 Years.
# To get 120 Years, we repeat this sequence twice.
SHASTIHAYANI_GROUPS = [
    # 1. Jupiter (3 Stars: Ashwini, Bharani, Krittika)
    {"lord": "Jupiter", "years": 10, "span": 40.0, "start": 0.0, "end": 40.0},
    
    # 2. Sun (4 Stars: Rohini, Mrigashira, Ardra, Punarvasu)
    {"lord": "Sun", "years": 10, "span": 53.333333, "start": 40.0, "end": 93.333333},
    
    # 3. Mars (3 Stars: Pushya, Ashlesha, Magha)
    {"lord": "Mars", "years": 10, "span": 40.0, "start": 93.333333, "end": 133.333333},
    
    # 4. Moon (4 Stars: P.Phalguni, U.Phalguni, Hasta, Chitra)
    {"lord": "Moon", "years": 6, "span": 53.333333, "start": 133.333333, "end": 186.666667},
    
    # 5. Mercury (3 Stars: Swati, Vishakha, Anuradha)
    {"lord": "Mercury", "years": 6, "span": 40.0, "start": 186.666667, "end": 226.666667},
    
    # 6. Venus (4 Stars: Jyeshtha, Mula, P.Ashadha, U.Ashadha)
    {"lord": "Venus", "years": 6, "span": 53.333333, "start": 226.666667, "end": 280.0},
    
    # 7. Saturn (3 Stars: Abhijit, Shravana, Dhanishta)
    {"lord": "Saturn", "years": 6, "span": 26.666667, "start": 280.0, "end": 306.666667},
    
    # 8. Rahu (4 Stars: Shatabhisha, P.Bhadra, U.Bhadra, Revati)
    {"lord": "Rahu", "years": 6, "span": 53.333333, "start": 306.666667, "end": 360.0}
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    return jd

def normalize_degrees(deg):
    return deg % 360

def get_sign(longitude):
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    idx = int(longitude / 30)
    return signs[idx % 12]

def add_years(start_date, years):
    """Adds years to a date (converting to days for simple arithmetic)."""
    days = years * 365.25
    return start_date + datetime.timedelta(days=days)

# ==========================================
# DASHA LOGIC (120 YEAR IMPLEMENTATION)
# ==========================================

def calculate_shastihayani_balance(moon_deg):
    """
    Calculates the Balance based on Group Span.
    """
    moon_deg = normalize_degrees(moon_deg)
    selected_group = None
    
    # Identify Group
    for group in SHASTIHAYANI_GROUPS:
        if group["start"] <= moon_deg < group["end"]:
            selected_group = group
            break
            
    # Edge case handling for 360 boundary
    if not selected_group:
        if moon_deg < 10: selected_group = SHASTIHAYANI_GROUPS[0]
        else: selected_group = SHASTIHAYANI_GROUPS[-1]

    # Calculate Balance
    traversed = moon_deg - selected_group["start"]
    fraction_remaining = 1.0 - (traversed / selected_group["span"])
    balance_years = fraction_remaining * selected_group["years"]
    
    return {
        "lord": selected_group["lord"],
        "balance_years": balance_years,
        "group_data": selected_group
    }

def generate_periods_120_years(birth_date_str, birth_time_str, balance_info):
    """
    Generates Dashas for approx 120 years (2 Full Cycles).
    """
    birth_dt = datetime.datetime.strptime(f"{birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M:%S")
    periods = []
    
    # --- 1. First Mahadasha (Balance) ---
    start_lord = balance_info["lord"]
    start_idx = 0
    for i, g in enumerate(SHASTIHAYANI_GROUPS):
        if g["lord"] == start_lord:
            start_idx = i
            break
            
    current_group = SHASTIHAYANI_GROUPS[start_idx]
    total_md_years = current_group["years"]
    balance_years = balance_info["balance_years"]
    
    # End date of the balance period
    md_end_date = add_years(birth_dt, balance_years)
    
    # Calculate Antardashas for the Balance Period
    # We must find which sub-period corresponds to the birth moment.
    elapsed_years = total_md_years - balance_years
    
    first_md_antars = []
    temp_time = 0.0 # Timeline starts at 0 (start of Mahadasha theoretically)
    
    # Antardasha Loop
    ad_start_idx = start_idx
    for j in range(8):
        ad_idx = (ad_start_idx + j) % 8
        ad_group = SHASTIHAYANI_GROUPS[ad_idx]
        
        ad_duration = (total_md_years * ad_group["years"]) / 60.0
        
        ad_start_t = temp_time
        ad_end_t = temp_time + ad_duration
        
        # If this Antar ends AFTER the elapsed time, it is part of the user's life
        if ad_end_t > elapsed_years:
            # Determine actual start date (Birth or normal start)
            if ad_start_t < elapsed_years:
                start_d = birth_dt # It was already running at birth
            else:
                offset = ad_start_t - elapsed_years
                start_d = add_years(birth_dt, offset)
            
            # Determine end date
            offset_end = ad_end_t - elapsed_years
            end_d = add_years(birth_dt, offset_end)
            
            first_md_antars.append({
                "lord": ad_group["lord"],
                "start": start_d.strftime("%Y-%m-%d"),
                "end": end_d.strftime("%Y-%m-%d")
            })
            
        temp_time += ad_duration

    periods.append({
        "lord": start_lord,
        "type": "Mahadasha (Balance)",
        "start": birth_dt.strftime("%Y-%m-%d"),
        "end": md_end_date.strftime("%Y-%m-%d"),
        "years_duration": balance_years,
        "antardashas": first_md_antars
    })
    
    current_date = md_end_date
    
    # --- 2. Subsequent Mahadashas (Loop for 120 Years) ---
    # Standard cycle is 8 planets (60 years). 
    # To cover 120 years, we need roughly 2 cycles (~16 iterations).
    # We iterate 16 times to ensure we cover the lifespan.
    
    for k in range(1, 17): 
        curr_idx = (start_idx + k) % 8
        group = SHASTIHAYANI_GROUPS[curr_idx]
        
        duration = group["years"]
        md_end = add_years(current_date, duration)
        
        # Antardashas
        antas = []
        ad_curr_date = current_date
        
        ad_start_idx_inner = curr_idx
        for m in range(8):
            ad_inner_idx = (ad_start_idx_inner + m) % 8
            ad_inner_group = SHASTIHAYANI_GROUPS[ad_inner_idx]
            
            ad_yrs = (duration * ad_inner_group["years"]) / 60.0
            ad_end_inner = add_years(ad_curr_date, ad_yrs)
            
            antas.append({
                "lord": ad_inner_group["lord"],
                "start": ad_curr_date.strftime("%Y-%m-%d"),
                "end": ad_end_inner.strftime("%Y-%m-%d")
            })
            ad_curr_date = ad_end_inner
            
        periods.append({
            "lord": group["lord"],
            "type": "Mahadasha",
            "start": current_date.strftime("%Y-%m-%d"),
            "end": md_end.strftime("%Y-%m-%d"),
            "years_duration": duration,
            "antardashas": antas
        })
        
        current_date = md_end
        
        # Stop if we have exceeded 125 years from birth to save resources
        if (current_date - birth_dt).days > (125 * 365.25):
            break
            
    return periods

def perform_shastihayani_calculation(data):
    """
    Main logic function used by the API.
    """
    # Inputs
    user_name = data.get("user_name")
    birth_date = data.get("birth_date")
    birth_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    
    # Swiss Ephemeris Setup
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    jd = get_julian_day(birth_date, birth_time, tz)
    
    # Positions
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    
    # Moon
    moon_res = swe.calc_ut(jd, swe.MOON, flags)
    moon_deg = normalize_degrees(moon_res[0][0])
    
    # Sun & Asc (For context)
    sun_res = swe.calc_ut(jd, swe.SUN, flags)
    sun_deg = normalize_degrees(sun_res[0][0])
    
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_deg = ascmc[0]
    
    # --- CALCULATION ---
    
    # 1. Calculate Balance
    balance_info = calculate_shastihayani_balance(moon_deg)
    
    # 2. Generate 120 Years of Dashas
    dasha_list = generate_periods_120_years(birth_date, birth_time, balance_info)
    
    response = {
        "user": user_name,
        "system": {
            "ayanamsa": "Sri Yukteswar",
            "dasha": "Shastihayani (Extended to 120 Years)",
            "note": "Cycle repeats after 60 years"
        },
        "planetary_positions": {
            "Ascendant": {"deg": asc_deg, "sign": get_sign(asc_deg)},
            "Sun": {"deg": sun_deg, "sign": get_sign(sun_deg)},
            "Moon": {"deg": moon_deg, "sign": get_sign(moon_deg)}
        },
        "balance_details": {
            "birth_lord": balance_info["lord"],
            "balance_years_remaining": balance_info["balance_years"]
        },
        "dasha_periods": dasha_list
    }
    
    return response