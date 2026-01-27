import os
import math
import datetime
import swisseph as swe

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ---------------------------------------------------------
# SATABDIKA DASHA CONSTANTS (Corrected Rule)
# ---------------------------------------------------------
# Sequence: Sun -> Moon -> Venus -> Mercury -> Jupiter -> Mars -> Saturn
SATABDIKA_ORDER = ["Sun", "Moon", "Venus", "Mercury", "Jupiter", "Mars", "Saturn"]

SATABDIKA_YEARS = {
    "Sun": 5,
    "Moon": 5,
    "Venus": 10,
    "Mercury": 10,
    "Jupiter": 20,
    "Mars": 20,
    "Saturn": 30
}

# Mapping: Based on Chitra (Index 13) = Sun
# Formula used in code: (Nak_Index - 13) % 7
# 0 -> Sun, 1 -> Moon, 2 -> Venus, etc.
SATABDIKA_MAP_INDICES = {
    0: "Sun",
    1: "Moon",
    2: "Venus",
    3: "Mercury",
    4: "Jupiter",
    5: "Mars",
    6: "Saturn"
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", 
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", 
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", 
    "Uttara Bhadrapada", "Revati"
]

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_julian_day(birth_date, birth_time, tz_offset):
    date_parts = list(map(int, birth_date.split('-')))
    time_parts = list(map(int, birth_time.split(':')))
    
    dt_local = datetime.datetime(date_parts[0], date_parts[1], date_parts[2], 
                                 time_parts[0], time_parts[1], time_parts[2])
    
    offset_delta = datetime.timedelta(hours=float(tz_offset))
    dt_utc = dt_local - offset_delta
    
    hour_decimal = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)
    return jd

def get_sign(longitude):
    return int(longitude / 30) + 1

def add_years_precise(start_dt, years):
    """Accurately adds float years to a datetime object."""
    whole_years = int(years)
    fraction_years = years - whole_years
    
    try:
        new_year = start_dt.year + whole_years
        res_dt = start_dt.replace(year=new_year)
    except ValueError:
        res_dt = start_dt.replace(year=start_dt.year + whole_years, day=28)
        
    # 365.2425 days per year average
    extra_days = fraction_years * 365.2425
    final_dt = res_dt + datetime.timedelta(days=extra_days)
    
    return final_dt

def calculate_antardashas(md_lord, md_full_duration, md_start_date, birth_date, md_end_date):
    """
    Calculates sub-periods based on the 100-year rule.
    Returns only Antardashas relevant to the life (post-birth).
    """
    antardashas = []
    md_idx = SATABDIKA_ORDER.index(md_lord)
    
    curr_ad_date = md_start_date
    
    # Loop 7 sub-periods
    for i in range(7):
        # Sequence starts with MD Lord
        ad_idx = (md_idx + i) % 7
        ad_lord = SATABDIKA_ORDER[ad_idx]
        ad_lord_years = SATABDIKA_YEARS[ad_lord]
        
        # Satabdika Formula: (MD * AD) / 100
        ad_len = (md_full_duration * ad_lord_years) / 100.0
        
        ad_end = add_years_precise(curr_ad_date, ad_len)
        
        # Logic to handle Birth Date overlapping
        # We want to display Antardashas that end AFTER birth date
        if ad_end > birth_date:
            # If the Antardasha started before birth, we just show its original start/end
            # The client can decide if they want to clip the start date to birth_date visually
            # But standard astrology software usually lists the Antardasha active at birth with its real dates.
            antardashas.append({
                "antardasha_lord": ad_lord,
                "start": curr_ad_date.strftime("%Y-%m-%d"),
                "end": ad_end.strftime("%Y-%m-%d")
            })
            
        curr_ad_date = ad_end
        
    return antardashas

def calculate_satabdika_logic(moon_lon, birth_dt):
    """
    Calculates Satabdika Dasha using Chitra=Sun mapping.
    """
    
    # 1. Nakshatra Position
    star_span = 360.0 / 27.0
    nakshatra_idx = int(moon_lon / star_span) # 0-26
    
    # 2. Determine Lord
    # Shift index so Chitra (13) becomes 0
    # (Index - 13) % 7
    mapped_idx = (nakshatra_idx - 13) % 7
    start_lord = SATABDIKA_MAP_INDICES[mapped_idx]
    
    # 3. Balance Calculation
    # How far into the nakshatra is the moon?
    traversed_deg = moon_lon - (nakshatra_idx * star_span)
    remaining_deg = star_span - traversed_deg
    
    # Percentage Remaining
    balance_ratio = remaining_deg / star_span
    
    start_lord_duration = SATABDIKA_YEARS[start_lord]
    balance_years = balance_ratio * start_lord_duration
    
    # Calculate Passed Years
    passed_years = start_lord_duration - balance_years
    
    # 4. Generate Schedule
    dasha_schedule = []
    
    start_seq_idx = SATABDIKA_ORDER.index(start_lord)
    current_date = birth_dt
    
    # --- First Dasha (Balance) ---
    # We calculate the Theoretical Start Date of this Mahadasha
    # (as if the person was born at the beginning of the cycle)
    # This aligns the Antardashas correctly.
    md_start_date = add_years_precise(birth_dt, -passed_years)
    md_end_date = add_years_precise(birth_dt, balance_years)
    
    dasha_schedule.append({
        "mahadasha_lord": start_lord,
        "start_date": md_start_date.strftime("%Y-%m-%d"), # Reporting theoretical start helps debug
        "end_date": md_end_date.strftime("%Y-%m-%d"),
        "duration_years": round(balance_years, 4),
        "full_duration": start_lord_duration,
        "is_balance_period": True,
        "antardashas": calculate_antardashas(start_lord, start_lord_duration, md_start_date, birth_dt, md_end_date)
    })
    
    current_date = md_end_date
    
    # --- Subsequent Dashas (Full Cycle) ---
    for i in range(1, 8):
        next_idx = (start_seq_idx + i) % 7
        planet_name = SATABDIKA_ORDER[next_idx]
        duration = SATABDIKA_YEARS[planet_name]
        
        end_date = add_years_precise(current_date, duration)
        
        dasha_schedule.append({
            "mahadasha_lord": planet_name,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": duration,
            "full_duration": duration,
            "is_balance_period": False,
            "antardashas": calculate_antardashas(planet_name, duration, current_date, birth_dt, end_date)
        })
        
        current_date = end_date
        
    return dasha_schedule

def perform_satabdika_calculation(data):
    """
    Main logic function used by the API.
    Calculates Satabdika Dasha.
    """
    user_name = data.get('user_name', 'Unknown')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 1. Set Ayanamsa: Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 2. Get JD
    jd = get_julian_day(birth_date, birth_time, tz)
    
    # 3. Info Checks
    houses, ascmc = swe.houses(jd, lat, lon, b'W')
    asc_deg = ascmc[0]
    d1_sign = get_sign(asc_deg)
    
    # 4. Get Moon Position
    res = swe.calc_ut(jd, 1, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    moon_lon = res[0][0]
    
    # 5. Calculate Satabdika Dasha
    dt_parts = list(map(int, birth_date.split('-')))
    tm_parts = list(map(int, birth_time.split(':')))
    birth_dt = datetime.datetime(dt_parts[0], dt_parts[1], dt_parts[2], 
                                 tm_parts[0], tm_parts[1], tm_parts[2])
    
    dasha_results = calculate_satabdika_logic(moon_lon, birth_dt)
    
    # 6. Metadata
    nak_idx = int(moon_lon / (360/27))
    nak_name = NAKSHATRAS[nak_idx]

    response = {
        "status": "success",
        "user_name": user_name,
        "ayanamsa": "Sri Yukteswar",
        "calculation_type": "Satabdika Dasha (100 Years - Chitra Start)",
        "chart_info": {
            "moon_longitude": round(moon_lon, 4),
            "nakshatra": nak_name,
            "d1_lagna_sign": d1_sign,
            "note": "Mapped relative to Chitra=Sun as per referenced output."
        },
        "data": dasha_results
    }
    
    return response