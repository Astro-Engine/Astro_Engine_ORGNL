import swisseph as swe
from datetime import datetime, timedelta

# Swiss Ephemeris Path
swe.set_ephe_path('astro_api/ephe')

# Planetary configuration based on PDF [cite: 6, 44, 136]
PLANETS = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"]
WEIGHTS = {"Moon": 1, "Sun": 2, "Jupiter": 3, "Mars": 4, "Mercury": 5, "Saturn": 6, "Venus": 7, "Rahu": 8}
TOTAL_CYCLE = 36

def calculate_timeline(birth_dt, start_planet, balance_yrs):
    timeline = []
    current_m_start = birth_dt
    
    # We calculate 24 Mahadashas (8 planets * 3 cycles = 108 years total)
    start_idx = PLANETS.index(start_planet)
    
    for total_step in range(24):
        curr_idx = (start_idx + total_step) % 8
        m_name = PLANETS[curr_idx]
        m_weight = WEIGHTS[m_name]
        
        # Duration for Mahadasha
        if total_step == 0:
            m_duration_days = balance_yrs * 365.25
        else:
            m_duration_days = m_weight * 365.25
            
        m_end_date = current_m_start + timedelta(days=m_duration_days)
        
        # Antardasha Logic
        ads = []
        ad_start_cursor = current_m_start
        
        # First Mahadasha requires handling elapsed Antardashas to match birth balance
        if total_step == 0:
            m_total_days = m_weight * 365.25
            m_elapsed_days = m_total_days - (balance_yrs * 365.25)
            ad_runner = 0
            
            for i in range(8):
                ad_name = PLANETS[(curr_idx + i) % 8]
                ad_w = WEIGHTS[ad_name]
                ad_dur = (m_weight * ad_w / TOTAL_CYCLE) * 365.25
                ad_boundary_end = ad_runner + ad_dur
                
                if ad_boundary_end > m_elapsed_days:
                    # Logic to align start with birth date [cite: 20]
                    calc_start = birth_dt + timedelta(days=max(0, ad_runner - m_elapsed_days))
                    calc_end = birth_dt + timedelta(days=ad_boundary_end - m_elapsed_days)
                    
                    ads.append({
                        "antardasha_lord": ad_name,
                        "start_date": calc_start.strftime("%d-%m-%Y"),
                        "end_date": calc_end.strftime("%d-%m-%Y")
                    })
                ad_runner = ad_boundary_end
        else:
            # Standard Full Mahadasha AD calculation [cite: 16, 18, 23]
            for i in range(8):
                ad_name = PLANETS[(curr_idx + i) % 8]
                ad_w = WEIGHTS[ad_name]
                ad_dur = (m_weight * ad_w / TOTAL_CYCLE) * 365.25
                ad_end = ad_start_cursor + timedelta(days=ad_dur)
                
                ads.append({
                    "antardasha_lord": ad_name,
                    "start_date": ad_start_cursor.strftime("%d-%m-%Y"),
                    "end_date": ad_end.strftime("%d-%m-%Y")
                })
                ad_start_cursor = ad_end

        timeline.append({
            "cycle": (total_step // 8) + 1,
            "mahadasha": m_name,
            "duration": m_weight,
            "start": current_m_start.strftime("%d-%m-%Y"),
            "end": m_end_date.strftime("%d-%m-%Y"),
            "antardashas": ads
        })
        current_m_start = m_end_date
        
    return timeline

def calculate_Shattrimshatsama_dasha(user_name, dob_str, tob_str, lat, lon, tz):
    """
    Calculate Vimshottari Dasha based on birth details
    
    Args:
        user_name: User's name
        dob_str: Date of birth (YYYY-MM-DD)
        tob_str: Time of birth (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with user info and vimshottari dasha periods
    """
    dob = datetime.strptime(f"{dob_str} {tob_str}", "%Y-%m-%d %H:%M:%S")
    
    # Julian Date and Moon Position (Lahiri)
    jd_utc = swe.julday(dob.year, dob.month, dob.day, dob.hour + dob.minute/60.0) - (tz/24.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_pos = swe.calc_ut(jd_utc, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    
    # Correct Classical Formula: Count from Shravana (22) [cite: 5]
    naks_deg = 360/27
    naks_idx = int(moon_pos / naks_deg) + 1 
    
    # Calculate Count from Shravana to Birth Nakshatra
    count_from_shravana = (naks_idx - 22 + 27) % 27 + 1
    lord_idx = count_from_shravana % 8
    if lord_idx == 0: lord_idx = 8
    
    start_planet = PLANETS[lord_idx - 1]
    
    # Balance Calculation
    deg_passed = moon_pos % naks_deg
    deg_rem = naks_deg - deg_passed
    balance_yrs = (deg_rem / naks_deg) * WEIGHTS[start_planet]
    
    res = calculate_timeline(dob, start_planet, balance_yrs)
    
    return {
        "user": user_name,
        "birth_details": {
            "nakshatra_number": naks_idx,
            "starting_mahadasha": start_planet,
            "balance_at_birth": f"{round(balance_yrs, 4)} years"
        },
        "timeline": res
    }