import os
import math
from datetime import datetime, timedelta
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
# Ensure this path points to your actual Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS & DATA
# ==========================================
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# DWADASHOTTARI LORDS
# Cycle of 112 Years
DWADASHOTTARI_LORDS = [
    {"lord": "Sun", "years": 7},
    {"lord": "Jupiter", "years": 9},
    {"lord": "Ketu", "years": 11},
    {"lord": "Mercury", "years": 13},
    {"lord": "Rahu", "years": 15},
    {"lord": "Mars", "years": 17},
    {"lord": "Saturn", "years": 19},
    {"lord": "Moon", "years": 21}
]
TOTAL_CYCLE = 112

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = round(((deg - d) * 60 - m) * 60, 2)
    return [d, m, s]

def add_months_to_date(start_date, total_months):
    """
    Accurately adds floating point months to a date.
    Uses 30.4375 days per month average (365.25 / 12) for Dasha calculations.
    """
    days_to_add = total_months * 30.4375
    return start_date + timedelta(days=days_to_add)

def sub_months_from_date(start_date, total_months):
    """Subtracts months from a date (for hypothetical start calculation)."""
    days_to_sub = total_months * 30.4375
    return start_date - timedelta(days=days_to_sub)

def get_navamsa_sign_index(lon_deg):
    rasi_idx = int(lon_deg / 30)
    deg_in_rasi = lon_deg % 30
    navamsa_sub_idx = int(deg_in_rasi / 3.333333333)
    element = rasi_idx % 4
    start_sign = [0, 9, 6, 3][element]
    return (start_sign + navamsa_sub_idx) % 12

def calculate_antardashas_for_period(md_lord_idx, md_start_date, md_duration_years, birth_date=None, is_balance=False):
    """
    Generates Antardashas for a given Mahadasha.
    If is_balance=True, it filters out periods before birth_date.
    """
    antardashas = []
    
    # In Dwadashottari, Antardasha sequence starts with the Mahadasha Lord
    ad_calc_idx = md_lord_idx 
    ad_start_cursor = md_start_date
    
    for _ in range(8):
        ad_lord_data = DWADASHOTTARI_LORDS[ad_calc_idx]
        
        # Formula: (MD Years * AD Years * 12) / 112
        months_duration = (md_duration_years * ad_lord_data["years"] * 12) / 112.0
        ad_end_cursor = add_months_to_date(ad_start_cursor, months_duration)
        
        # LOGIC FOR BALANCE DASHA FILTERING
        if is_balance and birth_date:
            # If this sub-period ended before birth, SKIP IT
            if ad_end_cursor < birth_date:
                ad_start_cursor = ad_end_cursor
                ad_calc_idx = (ad_calc_idx + 1) % 8
                continue
            
            # If this sub-period started before birth but ends after, CLAMP START
            actual_start = ad_start_cursor
            if ad_start_cursor < birth_date:
                actual_start = birth_date
            
            antardashas.append({
                "lord": ad_lord_data["lord"],
                "start": actual_start.strftime("%Y-%m-%d"),
                "end": ad_end_cursor.strftime("%Y-%m-%d")
            })
        else:
            # Standard generation
            antardashas.append({
                "lord": ad_lord_data["lord"],
                "start": ad_start_cursor.strftime("%Y-%m-%d"),
                "end": ad_end_cursor.strftime("%Y-%m-%d")
            })
            
        ad_start_cursor = ad_end_cursor
        ad_calc_idx = (ad_calc_idx + 1) % 8
        
    return antardashas

def perform_dwadashottari_calculation(data):
    """
    Main logic function used by the API.
    Calculates Dwadashottari Dasha sequence.
    """
    user_name = data.get("user_name")
    birth_date_str = data.get("birth_date")
    birth_time_str = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz_offset = float(data.get("timezone_offset"))

    # 1. Astro Setup
    local_dt = datetime.strptime(f"{birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=tz_offset)
    jul_day_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day_ut)

    # 2. Points
    cusps, ascmc = swe.houses_ex(jul_day_ut, lat, lon, b'W')
    ascendant_deg = ascmc[0]
    
    calc_flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    moon_data = swe.calc_ut(jul_day_ut, swe.MOON, calc_flag)
    moon_lon = moon_data[0][0]

    nak_duration = 360.0 / 27.0
    moon_nak_idx = int(moon_lon / nak_duration)
    deg_in_nak = moon_lon % nak_duration
    
    # 3. Eligibility Check
    # Dwadashottari applies if Lagna Navamsa is Taurus (1) or Libra (6)
    navamsa_sign_idx = get_navamsa_sign_index(ascendant_deg)
    is_technically_eligible = navamsa_sign_idx in [1, 6]

    # 4. Calculation
    # Sequence: Count from Moon Nakshatra to Revati (inclusive count logic)
    # Formula used: (Revati_Index - Moon_Nak_Index + 1)
    revati_idx = 26
    count = (revati_idx - moon_nak_idx + 1)
    if count <= 0: count += 27
    
    # Lord Index
    lord_rem = (count - 1) % 8
    start_lord_idx = lord_rem 
    
    # Balance Calculation
    # Proportion of nakshatra passed
    passed_fraction = deg_in_nak / nak_duration
    balance_fraction = 1.0 - passed_fraction
    
    start_lord_data = DWADASHOTTARI_LORDS[start_lord_idx]
    full_years = start_lord_data["years"]
    balance_years = balance_fraction * full_years
    elapsed_years = full_years - balance_years
    
    dasha_output = []
    current_date = local_dt
    
    # --- A. BALANCE DASHA ---
    hypothetical_start_date = sub_months_from_date(local_dt, elapsed_years * 12)
    balance_end_date = add_months_to_date(local_dt, balance_years * 12)
    
    balance_antardashas = calculate_antardashas_for_period(
        start_lord_idx, 
        hypothetical_start_date, 
        full_years, 
        birth_date=local_dt, 
        is_balance=True
    )
    
    dasha_output.append({
        "lord": start_lord_data["lord"],
        "start_date": local_dt.strftime("%Y-%m-%d"),
        "end_date": balance_end_date.strftime("%Y-%m-%d"),
        "duration_years": round(balance_years, 4),
        "is_balance": True,
        "note": "Balance at Birth",
        "antardashas": balance_antardashas
    })
    
    current_date = balance_end_date
    
    # --- B. SUBSEQUENT DASHAS ---
    calc_idx = (start_lord_idx + 1) % 8
    
    # Generate for 112 years from birth
    while (current_date.year - local_dt.year) < 112:
        lord_data = DWADASHOTTARI_LORDS[calc_idx]
        md_duration = lord_data["years"]
        
        md_end_date = add_months_to_date(current_date, md_duration * 12)
        
        full_antardashas = calculate_antardashas_for_period(
            calc_idx, 
            current_date, 
            md_duration, 
            is_balance=False
        )
        
        dasha_output.append({
            "lord": lord_data["lord"],
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": md_end_date.strftime("%Y-%m-%d"),
            "duration_years": md_duration,
            "is_balance": False,
            "antardashas": full_antardashas
        })
        
        current_date = md_end_date
        calc_idx = (calc_idx + 1) % 8

    # 5. Response
    response = {
        "meta": {
            "system": "Dwadashottari Dasha",
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": to_dms(ayanamsa_val),
            "is_technically_eligible": is_technically_eligible,
            "eligibility_note": f"Lagna Navamsa is {ZODIAC_SIGNS[navamsa_sign_idx]}. Displayed as requested."
        },
        "profile": {
            "name": user_name,
            "birth_date": birth_date_str,
            "birth_time": birth_time_str
        },
        "astronomical_points": {
            "Lagna": {
                "deg": ascendant_deg,
                "sign": ZODIAC_SIGNS[int(ascendant_deg/30)],
                "navamsa_sign": ZODIAC_SIGNS[navamsa_sign_idx]
            },
            "Moon": {
                "deg": moon_lon,
                "sign": ZODIAC_SIGNS[int(moon_lon/30)],
                "nakshatra": NAKSHATRAS[moon_nak_idx],
            }
        },
        "dasha_calculations": dasha_output
    }
    
    return response