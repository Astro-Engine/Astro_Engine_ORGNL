import os
import math
from datetime import datetime, timedelta
import swisseph as swe

# =============================================================================
# CONFIGURATION
# =============================================================================

# Ensure this path exists and contains Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Sri Yukteswar Ayanamsa ID (ID 7 in Swiss Ephemeris)
SIDM_YUKTESWAR = 7 

# Average days in a year for Antardasha/Balance day conversion
DAYS_PER_YEAR = 365.25

# Panchottari Dasha Structure (Cycle: 105 Years)
PANCHOTTARI_PLANETS = [
    {'id': 'Sun',     'years': 12, 'swe_id': swe.SUN},
    {'id': 'Mercury', 'years': 13, 'swe_id': swe.MERCURY},
    {'id': 'Saturn',  'years': 14, 'swe_id': swe.SATURN},
    {'id': 'Mars',    'years': 15, 'swe_id': swe.MARS},
    {'id': 'Venus',   'years': 16, 'swe_id': swe.VENUS},
    {'id': 'Moon',    'years': 17, 'swe_id': swe.MOON},
    {'id': 'Jupiter', 'years': 18, 'swe_id': swe.JUPITER}
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def add_calendar_years(start_dt, years):
    """
    Adds exact calendar years to a date.
    Example: 1989-06-28 + 18 years = 2007-06-28.
    Handles Leap Year edge case (Feb 29 -> Feb 28).
    """
    try:
        return start_dt.replace(year=start_dt.year + int(years))
    except ValueError:
        return start_dt.replace(year=start_dt.year + int(years), day=28)

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=float(tz_offset))
    hour_decimal = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)
    return jd + swe.deltat(jd)

def decimal_to_dms_str(deg):
    d = int(deg)
    mins = (deg - d) * 60
    m = int(mins)
    s = round((mins - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def get_nakshatra_info(lon):
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span)
    traversed = lon - (idx * nak_span)
    remaining = nak_span - traversed
    return {
        "index": idx,
        "name": NAKSHATRAS[idx % 27],
        "traversed": traversed,
        "remaining": remaining,
        "span": nak_span
    }

def get_d12_sign_index(lon):
    # D12 calculation: Each sign (30 deg) divided into 12 parts (2.5 deg each)
    # Starts from the sign itself.
    sign_idx = int(lon / 30)
    deg_in_sign = lon % 30
    part_idx = int(deg_in_sign / 2.5)
    final_sign = (sign_idx + part_idx) % 12
    return final_sign

def perform_panchottari_calculation(data):
    """
    Main logic function used by the API.
    Calculates Panchottari Dasha.
    """
    name = data.get('user_name')
    b_date = data.get('birth_date')
    b_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 1. Set Ayanamsa
    swe.set_sid_mode(SIDM_YUKTESWAR, 0, 0)
    
    jd = get_julian_day(b_date, b_time, tz)
    
    # 2. Ascendant & Applicability Check
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_deg = ascmc[0]
    asc_sign_idx = int(asc_deg / 30)
    d12_asc_idx = get_d12_sign_index(asc_deg)
    
    # Rule: Lagna in Cancer (3) AND D12 Lagna in Cancer (3)
    is_applicable = (asc_sign_idx == 3 and d12_asc_idx == 3)
    
    # 3. Moon Position
    xx, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    moon_deg = xx[0]
    moon_nak = get_nakshatra_info(moon_deg)
    
    # 4. Starting Dasha Calculation
    # Count from Anuradha (16) to Birth Nak
    anuradha_idx = 16
    birth_idx = moon_nak['index']
    
    count = (birth_idx - anuradha_idx) + 1
    if count <= 0: count += 27
        
    remainder = count % 7
    if remainder == 0: remainder = 7
    
    # Index of the Mahadasha Lord at birth (0-6)
    md_start_idx = remainder - 1 
    
    # 5. Balance Calculation
    # Fraction of current Nakshatra REMAINING
    fraction_left = moon_nak['remaining'] / moon_nak['span']
    
    first_md_data = PANCHOTTARI_PLANETS[md_start_idx]
    
    # Balance in Years (Float)
    balance_years_float = first_md_data['years'] * fraction_left
    
    # Convert Balance Years to Days (for accurate date addition)
    balance_days = balance_years_float * DAYS_PER_YEAR
    
    birth_dt = datetime.strptime(f"{b_date} {b_time}", "%Y-%m-%d %H:%M:%S")
    
    # Date when the first (Balance) Mahadasha Ends
    first_md_end_dt = birth_dt + timedelta(days=balance_days)
    
    # 6. Generate Cycle
    dasha_result = []
    last_md_end_dt = first_md_end_dt # Cursor
    
    for i in range(7):
        current_idx = (md_start_idx + i) % 7
        p_data = PANCHOTTARI_PLANETS[current_idx]
        
        # --- Mahadasha Start/End Dates ---
        if i == 0:
            # First Dasha (Balance)
            md_start = birth_dt
            md_end = first_md_end_dt
            is_balance = True
            display_years = (first_md_end_dt - birth_dt).days / DAYS_PER_YEAR
        else:
            # Subsequent Dashas: Add CALENDAR YEARS to the previous End Date
            md_start = last_md_end_dt
            md_end = add_calendar_years(md_start, p_data['years'])
            is_balance = False
            display_years = p_data['years']
            last_md_end_dt = md_end # Update cursor for next loop
        
        # --- Antardasha Calculation ---
        # To calculate AD dates correctly, we need the "Theoretical Start" of this MD
        if is_balance:
            theoretical_start = add_calendar_years(md_end, -p_data['years'])
        else:
            theoretical_start = md_start
        
        ad_cursor = theoretical_start
        sub_periods = []
        
        for j in range(7):
            # AD Order: Always starts from the MD Lord itself
            ad_idx = (current_idx + j) % 7
            ad_data = PANCHOTTARI_PLANETS[ad_idx]
            
            # Formula: (MD Years * AD Years * 12) / 105 = Months
            months_val = (p_data['years'] * ad_data['years'] * 12) / 105.0
            
            # Convert Months to Days
            # Use Standard Average Month = 365.25 / 12 = 30.4375
            days_val = months_val * (DAYS_PER_YEAR / 12.0)
            
            ad_end_dt = ad_cursor + timedelta(days=days_val)
            
            # Filter: Only show ADs that end AFTER birth (for the balance dasha)
            if ad_end_dt > birth_dt:
                # Clip start date to birth date if it started before birth
                real_start = ad_cursor if ad_cursor > birth_dt else birth_dt
                
                sub_periods.append({
                    "lord": ad_data['id'],
                    "start_date": real_start.strftime("%Y-%m-%d"),
                    "end_date": ad_end_dt.strftime("%Y-%m-%d")
                })
            
            ad_cursor = ad_end_dt

        dasha_result.append({
            "mahadasha_lord": p_data['id'],
            "start_date": md_start.strftime("%Y-%m-%d"),
            "end_date": md_end.strftime("%Y-%m-%d"),
            "duration_years": round(display_years, 2),
            "is_balance": is_balance,
            "antardashas": sub_periods
        })

    response = {
        "meta": {
            "ayanamsa": "Sri Yukteswar (ID: 7)",
            "calculation_method": "Exact Degree Balance / Calendar Year MDs",
            "applicability": {
                "is_classically_applicable": is_applicable,
                "reason": "Applicable" if is_applicable else f"Lagna ({SIGNS[asc_sign_idx]}) or D12 ({SIGNS[d12_asc_idx]}) is not Cancer."
            }
        },
        "planetary_positions": {
            "ascendant": decimal_to_dms_str(asc_deg),
            "moon": decimal_to_dms_str(moon_deg),
            "moon_nakshatra": moon_nak['name'],
            "nakshatra_traversed": round(moon_nak['traversed'], 4),
            "nakshatra_remaining": round(moon_nak['remaining'], 4)
        },
        "panchottari_dasha": dasha_result
    }
    
    return response