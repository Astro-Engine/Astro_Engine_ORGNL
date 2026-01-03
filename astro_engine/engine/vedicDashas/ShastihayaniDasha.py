import swisseph as swe
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION
# =============================================================================
EPHE_PATH = 'astro_api/ephe' 
swe.set_ephe_path(EPHE_PATH)

# =============================================================================
# VALIDATED SHASTIHAYANI MAPPING (Double-Verified against PDFs)
# =============================================================================
# Sequence pattern: 3, 4, 3, 4, 3, 3, 3, 4 = 27 Stars
SHASTIHAYANI_BLOCKS = [
    # 1. Jupiter: 3 Stars (Ashwini, Bharani, Krittika)
    {"lord": "Jupiter", "years": 10, "stars": [0, 1, 2]}, 

    # 2. Sun: 4 Stars (Rohini, Mrigashira, Ardra, Punarvasu)
    {"lord": "Sun",     "years": 10, "stars": [3, 4, 5, 6]}, 

    # 3. Mars: 3 Stars (Pushya, Ashlesha, Magha) -- Matches Vishnu PDF
    {"lord": "Mars",    "years": 10, "stars": [7, 8, 9]}, 

    # 4. Moon: 4 Stars (P.Phal, U.Phal, Hasta, Chitra)
    {"lord": "Moon",    "years": 6,  "stars": [10, 11, 12, 13]}, 

    # 5. Mercury: 3 Stars (Swati, Vishakha, Anuradha) -- Matches Tumul PDF
    {"lord": "Mercury", "years": 6,  "stars": [14, 15, 16]}, 

    # 6. Venus: 3 Stars (Jyeshtha, Mula, P.Ashadha)
    {"lord": "Venus",   "years": 6,  "stars": [17, 18, 19]}, 

    # 7. Saturn: 3 Stars (U.Ashadha, Shravana, Dhanishta)
    {"lord": "Saturn",  "years": 6,  "stars": [20, 21, 22]}, 

    # 8. Rahu: 4 Stars (Shatabhisha, P.Bhadra, U.Bhadra, Revati)
    {"lord": "Rahu",    "years": 6,  "stars": [23, 24, 25, 26]} 
]

PLANET_ORDER = ["Jupiter", "Sun", "Mars", "Moon", "Mercury", "Venus", "Saturn", "Rahu"]
PLANET_YEARS = {
    "Jupiter": 10, "Sun": 10, "Mars": 10,
    "Moon": 6, "Mercury": 6, "Venus": 6, "Saturn": 6, "Rahu": 6
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_julian_day(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=tz_offset)
    
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    
    jd = swe.julday(year, month, day, hour)
    return jd

def add_years(start_dt, years_float):
    # Standard Tropical Year
    days = years_float * 365.242199
    return start_dt + timedelta(days=days)

def get_antardasha_duration(md_years, ad_lord):
    ad_years = PLANET_YEARS[ad_lord]
    return (md_years * ad_years) / 60.0

# =============================================================================
# LOGIC
# =============================================================================

def calculate_shastihayani(moon_lon, birth_dt):
    # 1. Identify Nakshatra (0-26)
    nak_span = 13 + (20/60.0) # 13.33333 degrees
    nak_idx = int(moon_lon / nak_span)
    
    current_block = None
    block_idx = 0
    
    for i, block in enumerate(SHASTIHAYANI_BLOCKS):
        if nak_idx in block["stars"]:
            current_block = block
            block_idx = i
            break
            
    if not current_block:
        return 0, [{"error": "Invalid Moon Position"}]

    # 2. Calculate Balance
    # Start/End degrees of the specific block
    start_star_idx = current_block["stars"][0]
    end_star_idx = current_block["stars"][-1]
    
    block_start_deg = start_star_idx * nak_span
    block_end_deg = (end_star_idx + 1) * nak_span
    total_block_span = block_end_deg - block_start_deg
    
    traveled_deg = moon_lon - block_start_deg
    remaining_deg = total_block_span - traveled_deg
    
    balance_fraction = remaining_deg / total_block_span
    balance_years = balance_fraction * current_block["years"]
    
    # 3. Generate Sequence
    sequence = []
    
    # --- Balance Dasha ---
    md_lord = current_block["lord"]
    md_full_years = current_block["years"]
    
    # Theoretical start of this dasha
    years_passed = md_full_years - balance_years
    md_theoretical_start = add_years(birth_dt, -years_passed)
    md_end_date = add_years(birth_dt, balance_years)
    
    # Antardashas for Balance
    ad_list = []
    ad_start_ptr = md_theoretical_start
    start_p_idx = PLANET_ORDER.index(md_lord)
    
    for i in range(8):
        curr_p_idx = (start_p_idx + i) % 8
        ad_lord = PLANET_ORDER[curr_p_idx]
        
        dur_years = get_antardasha_duration(md_full_years, ad_lord)
        ad_end_ptr = add_years(ad_start_ptr, dur_years)
        
        # Only add future/active sub-periods
        if ad_end_ptr > birth_dt:
            display_start = birth_dt if ad_start_ptr < birth_dt else ad_start_ptr
            
            ad_list.append({
                "antardasha_lord": ad_lord,
                "start_date": display_start.strftime("%Y-%m-%d"),
                "end_date": ad_end_ptr.strftime("%Y-%m-%d"),
                "duration_months": round(dur_years * 12, 1)
            })
            
        ad_start_ptr = ad_end_ptr

    sequence.append({
        "type": "Balance",
        "mahadasha_lord": md_lord,
        "start_date": birth_dt.strftime("%Y-%m-%d"),
        "end_date": md_end_date.strftime("%Y-%m-%d"),
        "duration_years": balance_years,
        "antardashas": ad_list
    })
    
    current_date = md_end_date
    
    # --- Future Dashas ---
    iter_idx = (block_idx + 1) % len(SHASTIHAYANI_BLOCKS)
    
    # Generate for 85 years approx
    while current_date.year < (birth_dt.year + 85):
        block = SHASTIHAYANI_BLOCKS[iter_idx]
        md_lord = block["lord"]
        md_years = block["years"]
        md_end = add_years(current_date, md_years)
        
        future_ads = []
        ad_cursor = current_date
        start_p_idx = PLANET_ORDER.index(md_lord)
        
        for i in range(8):
            curr_p_idx = (start_p_idx + i) % 8
            ad_lord = PLANET_ORDER[curr_p_idx]
            dur = get_antardasha_duration(md_years, ad_lord)
            ad_end_c = add_years(ad_cursor, dur)
            
            future_ads.append({
                "antardasha_lord": ad_lord,
                "start_date": ad_cursor.strftime("%Y-%m-%d"),
                "end_date": ad_end_c.strftime("%Y-%m-%d"),
                "duration_months": round(dur * 12, 1)
            })
            ad_cursor = ad_end_c
            
        sequence.append({
            "type": "Full",
            "mahadasha_lord": md_lord,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": md_end.strftime("%Y-%m-%d"),
            "duration_years": md_years,
            "antardashas": future_ads
        })
        
        current_date = md_end
        iter_idx = (iter_idx + 1) % len(SHASTIHAYANI_BLOCKS)
        
    return balance_years, sequence

def calculate_shastihayani_dasha(user_name, date_str, time_str, lat, lon, tz):
    """
    Calculate Shastihayani Dasha based on birth details
    
    Args:
        user_name: User's name
        date_str: Date of birth (YYYY-MM-DD)
        time_str: Time of birth (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with user info and shastihayani dasha periods
    """
    # 1. Ephemeris
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = get_julian_day(date_str, time_str, tz)
    
    moon_res = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    sun_res = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    houses = swe.houses(jd, lat, lon, b'W')
    
    moon_deg = moon_res[0][0]
    sun_deg = sun_res[0][0]
    asc_deg = houses[1][0]
    
    # 2. Condition Check
    sun_sign = int(sun_deg / 30) + 1
    asc_sign = int(asc_deg / 30) + 1
    condition = (sun_sign == asc_sign)
    
    # 3. Calculation
    birth_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    bal_years, dasha_seq = calculate_shastihayani(moon_deg, birth_dt)
    
    # Readable balance
    y = int(bal_years)
    m = int((bal_years - y) * 12)
    d = int(((bal_years - y) * 12 - m) * 30)
    
    return {
        "user_name": user_name,
        "chart_details": {
            "moon_deg": moon_deg,
            "sun_deg": sun_deg,
            "asc_deg": asc_deg,
            "moon_nakshatra_idx": int(moon_deg / 13.333333)
        },
        "shastihayani_condition": {
            "status": "APPLICABLE" if condition else "NOT APPLICABLE",
            "is_sun_in_lagna": condition
        },
        "dasha_balance": {
            "years": bal_years,
            "readable": f"{y}y {m}m {d}d"
        },
        "dasha_system": dasha_seq
    }