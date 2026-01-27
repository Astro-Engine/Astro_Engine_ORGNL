import os
import swisseph as swe
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Use absolute path or relative to current working directory
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# AYANAMSA: Sri Yukteswar (Mode 7)
AYANAMSA_MODE = 7 

# DASHA CONSTANTS
DASHA_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus"]
PLANET_YEARS = {
    "Sun": 6, "Moon": 15, "Mars": 8, "Mercury": 17, 
    "Saturn": 10, "Jupiter": 19, "Rahu": 12, "Venus": 21
}

# --- NAKSHATRA MAPPING (ARDRADI - 27 STAR GRID) ---
def build_nak_map():
    # Groups: (Lord, Start_Index, Count)
    # Indices are 0-26 based on Ashwini=0
    groups = [
        ("Sun", 5, 4),      # Ardra to Ashlesha
        ("Moon", 9, 3),     # Magha to U.Phal
        ("Mars", 12, 4),    # Hasta to Vishakha
        ("Mercury", 16, 3), # Anuradha to Mula
        ("Saturn", 19, 3),  # P.Ash to Shravana (Abhijit absorbed)
        ("Jupiter", 22, 3), # Dhanishta to P.Bhadra
        ("Rahu", 25, 4),    # U.Bhadra, Revati, Ashwini(0), Bharani(1)
        ("Venus", 2, 3)     # Krittika to Mrigashira
    ]
    
    mapping = {}
    for lord, start, count in groups:
        for i in range(count):
            idx = (start + i) % 27
            # Store: Lord, Order in Group (0 to Count-1), Total in Group
            mapping[idx] = {
                "lord": lord,
                "star_position": i,      # 0 = 1st star, 1 = 2nd star...
                "star_count": count      # How many stars this planet rules
            }
    return mapping

NAK_MAP_27 = build_nak_map()

# --- HELPERS ---

def get_julian_day(date_str, time_str, tz_offset):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_utc = dt - timedelta(hours=float(tz_offset))
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
        return jd, dt
    except ValueError:
        raise ValueError("Invalid Date/Time Format")

def add_years_exact(dt, years):
    """
    Adds years (including float fractions) to a date using 365.25 days/year standard.
    This maintains the precision required for Pratyantardashas (days/hours).
    """
    days = years * 365.25
    return dt + timedelta(days=days)

def get_ashtottari_balance_per_star(moon_sidereal):
    """
    Calculates balance based on the individual Nakshatra.
    """
    # 1. Get Standard Nakshatra Index (0-26) and Fraction
    # 360 / 27 = 13.3333 degrees
    nak_span = 360.0 / 27.0
    nak_idx = int(moon_sidereal // nak_span)
    nak_fraction = (moon_sidereal % nak_span) / nak_span
    
    # 2. Get Lord Info
    info = NAK_MAP_27.get(nak_idx)
    lord = info['lord']
    star_pos = info['star_position'] # 0-based index of star within planet's group
    total_stars = info['star_count']
    
    # 3. Calculate Years Per Star for this Planet
    total_planet_years = PLANET_YEARS[lord]
    years_per_star = total_planet_years / total_stars
    
    # 4. Calculate Balance
    # Balance in CURRENT star
    balance_in_current = (1.0 - nak_fraction) * years_per_star
    
    # Balance from FUTURE stars in the group
    stars_remaining = (total_stars - 1) - star_pos
    balance_from_future = stars_remaining * years_per_star
    
    total_balance = balance_in_current + balance_from_future
    
    return lord, total_balance

def generate_dasha_schedule(birth_date, start_lord, balance_years):
    periods = []
    
    # 1. Theoretical Start
    total_duration = PLANET_YEARS[start_lord]
    elapsed = total_duration - balance_years
    theoretical_start = add_years_exact(birth_date, -elapsed)
    
    # 2. Sequence
    start_idx = DASHA_ORDER.index(start_lord)
    seq = DASHA_ORDER[start_idx:] + DASHA_ORDER[:start_idx]
    
    current_md_start = theoretical_start
    accumulated = 0
    
    # --- LEVEL 1: MAHADASHA LOOP ---
    for planet in seq:
        md_years = PLANET_YEARS[planet]
        md_end = add_years_exact(current_md_start, md_years)
        
        # Only process if this MD ends after birth (standard filtering)
        if md_end > birth_date:
            disp_start = birth_date if current_md_start < birth_date else current_md_start
            
            # --- LEVEL 2: ANTARDASHA LOOP ---
            antardashas = []
            
            # Ashtottari Rule: AD starts with the MD Lord
            ad_start_idx = DASHA_ORDER.index(planet)
            ad_seq = DASHA_ORDER[ad_start_idx:] + DASHA_ORDER[:ad_start_idx]
            
            curr_ad_start = current_md_start
            
            for ad_planet in ad_seq:
                ad_planet_years = PLANET_YEARS[ad_planet]
                
                # Formula: (MD Years * AD Planet Years) / 108
                ad_duration_years = (md_years * ad_planet_years) / 108.0
                
                ad_end = add_years_exact(curr_ad_start, ad_duration_years)
                
                if ad_end > birth_date:
                    disp_ad_start = birth_date if curr_ad_start < birth_date else curr_ad_start
                    
                    # --- LEVEL 3: PRATYANTARDASHA LOOP ---
                    pratyantardashas = []
                    
                    # Ashtottari Rule: PD starts with the AD Lord
                    pd_start_idx = DASHA_ORDER.index(ad_planet)
                    pd_seq = DASHA_ORDER[pd_start_idx:] + DASHA_ORDER[:pd_start_idx]
                    
                    curr_pd_start = curr_ad_start
                    
                    for pd_planet in pd_seq:
                        pd_planet_years = PLANET_YEARS[pd_planet]
                        
                        # Formula: (AD Duration * PD Planet Years) / 108
                        # We use the 'ad_duration_years' calculated in Level 2
                        pd_duration_years = (ad_duration_years * pd_planet_years) / 108.0
                        
                        pd_end = add_years_exact(curr_pd_start, pd_duration_years)
                        
                        if pd_end > birth_date:
                            disp_pd_start = birth_date if curr_pd_start < birth_date else curr_pd_start
                            
                            pratyantardashas.append({
                                "planet": pd_planet,
                                "start": disp_pd_start.strftime("%Y-%m-%d %H:%M"),
                                "end": pd_end.strftime("%Y-%m-%d %H:%M")
                            })
                        
                        curr_pd_start = pd_end
                    # --- END PD LOOP ---

                    antardashas.append({
                        "planet": ad_planet,
                        "start": disp_ad_start.strftime("%Y-%m-%d"),
                        "end": ad_end.strftime("%Y-%m-%d"),
                        "pratyantardashas": pratyantardashas
                    })
                
                curr_ad_start = ad_end
            # --- END AD LOOP ---
            
            periods.append({
                "mahadasha": planet,
                "start": disp_start.strftime("%Y-%m-%d"),
                "end": md_end.strftime("%Y-%m-%d"),
                "antardashas": antardashas
            })
            
        current_md_start = md_end
        accumulated += md_years
        if accumulated >= 108: break
        
    return periods, balance_years

def ashtottari_pratyantardashas_calculation(data):
    """
    Main logic function used by the API.
    Calculates Ashtottari Dasha.
    """
    # Input Parsing
    date_in = data.get("birth_date")
    time_in = data.get("birth_time")
    tz = data.get("timezone") or data.get("tz") or data.get("timezone_offset")
    lat = data.get("latitude") or data.get("lat")
    lon = data.get("longitude") or data.get("lon")
    
    if any(x is None for x in [date_in, time_in, tz, lat, lon]):
        raise ValueError("Missing input fields")

    # 1. AYANAMSA
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    
    # 2. MOON
    jd, dt = get_julian_day(date_in, time_in, tz)
    moon_trop = swe.calc_ut(jd, swe.MOON, 0)[0][0]
    ayanamsa = swe.get_ayanamsa(jd)
    moon_sid = (moon_trop - ayanamsa) % 360
    
    # 3. BALANCE
    lord, balance = get_ashtottari_balance_per_star(moon_sid)
    
    # 4. SCHEDULE
    schedule, bal_out = generate_dasha_schedule(dt, lord, balance)
    
    result = {
        "status": "success",
        "settings": {
            "ayanamsa": "Sri Yukteswar" if AYANAMSA_MODE==7 else "Lahiri",
            "ayanamsa_val": round(ayanamsa, 4),
            "moon_deg": round(moon_sid, 4)
        },
        "dasha_balance": {
            "lord": lord,
            "balance_years": round(bal_out, 6)
        },
        "schedule": schedule
    }
    
    return result