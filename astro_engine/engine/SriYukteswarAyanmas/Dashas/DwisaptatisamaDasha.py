import os
import math
from datetime import datetime, timedelta
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
# Path to Swiss Ephemeris files (must exist relative to this script)
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# ASTROLOGICAL CONSTANTS
# ==========================================

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}

# Sign Lords (0=Aries ... 11=Pisces)
SIGN_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon',
    4: 'Sun', 5: 'Mercury', 6: 'Venus', 7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Dwisaptati Sama Dasha Sequence (Fixed Order)
DASHA_SEQ = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu']

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_julian_day_utc(date_str, time_str, tz_offset):
    """
    Converts Local Time -> UTC -> Julian Day (UT).
    """
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    # Subtract timezone offset to get UTC
    utc_dt = local_dt - timedelta(hours=float(tz_offset))
    
    # Calculate decimal hour
    hour_decimal = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    
    # Get JD (UT)
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

def jd_to_date_str(jd):
    """
    Converts Julian Day back to YYYY-MM-DD HH:MM:SS string.
    """
    y, m, d, h = swe.revjul(jd)
    h_int = int(h)
    remainder = (h - h_int) * 60
    m_int = int(remainder)
    s_int = int((remainder - m_int) * 60)
    return f"{y:04d}-{m:02d}-{d:02d} {h_int:02d}:{m_int:02d}:{s_int:02d}"

def get_nakshatra_info(lon_deg):
    """
    Returns (1-based index, Name, Degrees Remaining, Total Nak Length)
    """
    nak_len = 13.0 + (20.0/60.0) # 13.3333... deg
    
    idx_0 = int(lon_deg / nak_len)
    idx_1 = idx_0 + 1
    
    deg_traversed = lon_deg % nak_len
    deg_remaining = nak_len - deg_traversed
    
    name = NAKSHATRAS[idx_0] if 0 <= idx_0 < 27 else "Unknown"
    return idx_1, name, deg_remaining, nak_len

def get_antardashas(md_lord, start_jd, duration_years, is_balance):
    """
    Generates Antardashas.
    Full MD = 9 Years.
    8 Antardashas.
    Each Full AD = 1.125 Years.
    Sequence: Starts with MD Lord, then cyclical.
    """
    full_ad_years = 1.125
    full_ad_days = full_ad_years * 365.2425
    
    # Generate Sequence for this MD
    start_idx = DASHA_SEQ.index(md_lord)
    ad_lords = [DASHA_SEQ[(start_idx + i) % 8] for i in range(8)]
    
    subs = []
    
    if not is_balance:
        # Standard Full MD
        curr = start_jd
        for lord in ad_lords:
            end = curr + full_ad_days
            subs.append({
                "lord": lord,
                "start": jd_to_date_str(curr),
                "end": jd_to_date_str(end)
            })
            curr = end
    else:
        # Balance MD
        # duration_years = Time Remaining in MD.
        # Time Passed = 9.0 - duration_years
        time_passed = 9.0 - duration_years
        
        # Calculate how many full ADs have completely passed
        # Use epsilon for float precision safety
        ads_passed_count = int((time_passed + 0.00001) / full_ad_years)
        
        # Calculate time spent in the current (interrupted) AD
        time_spent_in_curr_ad = time_passed - (ads_passed_count * full_ad_years)
        time_rem_in_curr_ad = full_ad_years - time_spent_in_curr_ad
        
        # Index of current AD
        curr_ad_idx = ads_passed_count
        curr_jd = start_jd
        
        # 1. Add interrupted AD (Remaining part)
        if curr_ad_idx < 8:
            lord = ad_lords[curr_ad_idx]
            days_rem = time_rem_in_curr_ad * 365.2425
            end_jd = curr_jd + days_rem
            
            subs.append({
                "lord": lord,
                "start": jd_to_date_str(curr_jd),
                "end": jd_to_date_str(end_jd),
                "note": "Balance AD"
            })
            curr_jd = end_jd
            
            # 2. Add rest of the ADs
            for i in range(curr_ad_idx + 1, 8):
                lord = ad_lords[i]
                end_jd = curr_jd + full_ad_days
                subs.append({
                    "lord": lord,
                    "start": jd_to_date_str(curr_jd),
                    "end": jd_to_date_str(end_jd)
                })
                curr_jd = end_jd
                
    return subs

def perform_Dwisaptatisama_calculation(data):
    """
    Main logic function used by the API.
    """
    # 1. Inputs
    jd_birth = get_julian_day_utc(
        data.get('birth_date'), 
        data.get('birth_time'), 
        data.get('timezone_offset')
    )
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))

    # 2. Set Ayanamsa: Sri Yukteswar (ID 7)
    swe.set_sid_mode(7, 0, 0)
    ay_val = swe.get_ayanamsa_ut(jd_birth)

    # 3. Calculate Ascendant (Lagna)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    cusps, ascmc = swe.houses_ex(jd_birth, lat, lon, b'P', flags)
    asc_deg = ascmc[0]
    lagna_sign_idx = int(asc_deg / 30)

    # 4. Calculate Planets
    bodies = {}
    for pname, pid in PLANETS.items():
        xx, _ = swe.calc_ut(jd_birth, pid, flags)
        bodies[pname] = {
            'lon': xx[0],
            'sign': int(xx[0] / 30)
        }

    # 5. Check Applicability (Logic: Lagna Lord in 7th OR 7th Lord in Lagna)
    seventh_sign_idx = (lagna_sign_idx + 6) % 12
    
    lagna_lord_name = SIGN_LORDS[lagna_sign_idx]
    seventh_lord_name = SIGN_LORDS[seventh_sign_idx]
    
    lagna_lord_pos_sign = bodies[lagna_lord_name]['sign']
    seventh_lord_pos_sign = bodies[seventh_lord_name]['sign']
    
    condition_met = (lagna_lord_pos_sign == seventh_sign_idx) or \
                    (seventh_lord_pos_sign == lagna_sign_idx)

    # 6. Determine Starting Dasha Lord
    # Logic: Count from Mula (19) to Janma Nakshatra
    moon_lon = bodies['Moon']['lon']
    nak_idx, nak_name, deg_rem, nak_len = get_nakshatra_info(moon_lon)
    
    # Count formula: (Janma - Mula) + 1
    # If Janma(20) - Mula(19) = 1 + 1 = 2.
    count = (nak_idx - 19) + 1
    if count <= 0:
        count += 27
        
    remainder = count % 8
    if remainder == 0: remainder = 8
    
    # Start Lord (0-based index for list)
    start_lord_idx = remainder - 1
    start_lord_name = DASHA_SEQ[start_lord_idx]
    
    # 7. Calculate Balance Duration
    # Total MD = 9 Years.
    balance_years = (deg_rem / nak_len) * 9.0
    
    # 8. Generate 140 Years Schedule
    schedule = []
    target_years = 140.0
    years_generated = 0.0
    
    current_jd = jd_birth
    curr_seq_idx = start_lord_idx
    
    # --- A. First Dasha (Balance) ---
    first_md_end_jd = current_jd + (balance_years * 365.2425)
    
    schedule.append({
        "dasha_lord": DASHA_SEQ[curr_seq_idx],
        "type": "Balance",
        "start_date": jd_to_date_str(current_jd),
        "end_date": jd_to_date_str(first_md_end_jd),
        "duration": round(balance_years, 4),
        "antardashas": get_antardashas(DASHA_SEQ[curr_seq_idx], current_jd, balance_years, is_balance=True)
    })
    
    # Update pointers
    years_generated += balance_years
    current_jd = first_md_end_jd
    curr_seq_idx = (curr_seq_idx + 1) % 8
    
    # --- B. Loop for remaining years ---
    while years_generated < target_years:
        lord = DASHA_SEQ[curr_seq_idx]
        duration = 9.0
        
        md_end_jd = current_jd + (duration * 365.2425)
        
        schedule.append({
            "dasha_lord": lord,
            "type": "Full",
            "start_date": jd_to_date_str(current_jd),
            "end_date": jd_to_date_str(md_end_jd),
            "duration": 9.0,
            "antardashas": get_antardashas(lord, current_jd, 9.0, is_balance=False)
        })
        
        # Update pointers
        years_generated += duration
        current_jd = md_end_jd
        curr_seq_idx = (curr_seq_idx + 1) % 8

    # 9. Response
    result = {
        "status": "success",
        "user": data.get('user_name'),
        "calculation_settings": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": round(ay_val, 4),
            "dasha_system": "Dwisaptati Sama Dasha (72 Year Cycle)",
            "calculation_span": "140 Years"
        },
        "applicability": {
            "is_applicable": condition_met,
            "details": f"Lagna Lord ({lagna_lord_name}) in Sign {lagna_lord_pos_sign}, 7th Lord ({seventh_lord_name}) in Sign {seventh_lord_pos_sign}. Lagna Sign: {lagna_sign_idx}"
        },
        "starting_info": {
            "nakshatra": f"{nak_name} ({nak_idx})",
            "count_from_mula": count,
            "remainder": remainder,
            "start_lord": start_lord_name,
            "balance_years": round(balance_years, 4)
        },
        "dasha_schedule": schedule
    }
    
    return result