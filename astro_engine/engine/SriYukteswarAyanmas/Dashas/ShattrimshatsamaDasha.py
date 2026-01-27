import os
import math
import datetime
from datetime import timedelta
import swisseph as swe

# --- Configuration ---
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- Constants ---
# Sri Yukteswar Ayanamsa ID (Check documentation, typically 7)
SIDM_YUKTESHWAR = 7  

# Dasha Rules
DASHA_SEQUENCE = [
    {"planet": "Moon", "id": swe.MOON, "years": 1},
    {"planet": "Sun", "id": swe.SUN, "years": 2},
    {"planet": "Jupiter", "id": swe.JUPITER, "years": 3},
    {"planet": "Mars", "id": swe.MARS, "years": 4},
    {"planet": "Mercury", "id": swe.MERCURY, "years": 5},
    {"planet": "Saturn", "id": swe.SATURN, "years": 6},
    {"planet": "Venus", "id": swe.VENUS, "years": 7},
    {"planet": "Rahu", "id": swe.MEAN_NODE, "years": 8}
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# --- Helper Functions ---

def decimal_to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - datetime.timedelta(hours=tz_offset)
    hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)

def get_nakshatra_info(moon_lon):
    nak_duration = 360.0 / 27.0
    nak_index = int(moon_lon / nak_duration)
    deg_in_nak = moon_lon % nak_duration
    fraction_passed = deg_in_nak / nak_duration
    fraction_remaining = 1.0 - fraction_passed
    
    if nak_index >= 27: nak_index = 0
    
    return {
        "index": nak_index,
        "name": NAKSHATRAS[nak_index],
        "fraction_remaining": fraction_remaining
    }

def calculate_day_night_and_hora(jd, lat, lon, asc_lon):
    """
    Robust calculation of Day/Night using Geometric Altitude calculation
    without relying on unstable swisseph constant names.
    """
    # 1. Calculate Sun's Equatorial Position (RA, Dec)
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    sun_res = swe.calc_ut(jd, swe.SUN, flags)
    ra_deg = sun_res[0][0]
    dec_deg = sun_res[0][1]

    # 2. Calculate Sidereal Time at Greenwich (GMST)
    gmst = swe.sidtime(jd)
    
    # 3. Local Sidereal Time (LST) = GMST + Longitude/15
    lst_hours = gmst + (lon / 15.0)
    lst_deg = (lst_hours * 15.0) % 360.0
    
    # 4. Hour Angle (H) = LST - RA
    H_deg = lst_deg - ra_deg
    
    # Convert to Radians for Math
    lat_rad = math.radians(lat)
    dec_rad = math.radians(dec_deg)
    H_rad = math.radians(H_deg)
    
    # 5. Calculate Altitude (sin a = sin dec * sin lat + cos dec * cos lat * cos H)
    sin_alt = (math.sin(dec_rad) * math.sin(lat_rad)) + \
              (math.cos(dec_rad) * math.cos(lat_rad) * math.cos(H_rad))
    
    alt_rad = math.asin(sin_alt)
    alt_deg = math.degrees(alt_rad)
    
    # Day if Altitude > -0.833 (Geometric horizon accounting for refraction)
    is_day = alt_deg > -0.833

    # 6. Hora Calculation
    # Odd: 0-15 Sun, 15-30 Moon
    # Even: 0-15 Moon, 15-30 Sun
    sign_index = int(asc_lon / 30) 
    deg_in_sign = asc_lon % 30
    
    is_odd_sign = ((sign_index + 1) % 2 != 0)
    is_first_half = (deg_in_sign < 15.0)
    
    hora_lord = ""
    if is_odd_sign:
        hora_lord = "Sun" if is_first_half else "Moon"
    else:
        hora_lord = "Moon" if is_first_half else "Sun"

    return is_day, hora_lord

def perform_shattrimshatsama_calculation(data):
    """
    Main logic function used by the API.
    Calculates Shattrimshat Sama Dasha.
    """
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    # 1. Time Setup
    jd = get_julian_day(birth_date, birth_time, tz)
    
    # 2. Set Ayanamsa
    swe.set_sid_mode(SIDM_YUKTESHWAR, 0, 0)
    
    # 3. Calculate Ascendant (Lagna)
    # We need Ascendant for Hora check. 
    # House system 'W' used.
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    asc_lon = ascmc[0]
    
    # 4. Check Applicability
    is_day, hora_lord = calculate_day_night_and_hora(jd, lat, lon, asc_lon)
    
    applicable = False
    if is_day and hora_lord == "Sun":
        applicable = True
    elif (not is_day) and hora_lord == "Moon":
        applicable = True
        
    # 5. Calculate Moon for Dasha
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_res = swe.calc_ut(jd, swe.MOON, flags)
    moon_lon = moon_res[0][0]
    
    # 6. Dasha Logic
    nak_info = get_nakshatra_info(moon_lon)
    janma_index = nak_info['index']
    shravana_index = 21 # 22nd Nakshatra is index 21
    
    # Calculate Count from Shravana
    diff = janma_index - shravana_index
    if diff < 0: diff += 27
    count = diff + 1 # Inclusive count
    
    remainder = count % 8
    if remainder == 0: remainder = 8
    
    # Start Lord (Index = Remainder - 1)
    start_idx = remainder - 1
    start_lord = DASHA_SEQUENCE[start_idx]
    
    # Balance Calculation
    balance_yrs = nak_info['fraction_remaining'] * start_lord['years']
    
    # 7. Generate Periods
    result_dashas = []
    birth_dt = datetime.datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    
    # Logic: We calculate backward to find the theoretical start of the current dasha
    # End of current dasha = Birth + Balance
    # Start of current dasha = End - Full Duration
    
    current_dasha_end_dt = birth_dt + datetime.timedelta(days=balance_yrs * 365.25)
    theoretical_start_dt = current_dasha_end_dt - datetime.timedelta(days=start_lord['years'] * 365.25)
    
    running_date = theoretical_start_dt
    curr_idx = start_idx
    
    # Generate enough cycles to cover life (e.g., 3 cycles = 108 years)
    for _ in range(24): # 8 planets * 3
        lord = DASHA_SEQUENCE[curr_idx]
        duration_days = lord['years'] * 365.25
        end_date = running_date + datetime.timedelta(days=duration_days)
        
        # If period ends after birth, include it
        if end_date > birth_dt:
            # Sub Periods (Antardasha)
            antardashas = []
            ad_running = running_date
            
            # AD Sequence starts from MD Lord
            for i in range(8):
                ad_idx = (curr_idx + i) % 8
                ad_lord = DASHA_SEQUENCE[ad_idx]
                
                # Formula: Months = (MD * AD) / 3
                months = (lord['years'] * ad_lord['years']) / 3.0
                ad_days = months * 30.4375 
                
                ad_end = ad_running + datetime.timedelta(days=ad_days)
                
                # Only show if AD ends after birth
                if ad_end > birth_dt:
                    antardashas.append({
                        "lord": ad_lord['planet'],
                        "start": max(birth_dt, ad_running).strftime("%Y-%m-%d"),
                        "end": ad_end.strftime("%Y-%m-%d")
                    })
                ad_running = ad_end
            
            result_dashas.append({
                "mahadasha_lord": lord['planet'],
                "start_date": max(birth_dt, running_date).strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration_years": lord['years'],
                "antardashas": antardashas
            })
        
        running_date = end_date
        curr_idx = (curr_idx + 1) % 8
        
        if running_date.year > birth_dt.year + 100:
            break
    
    result = {
        "status": "success",
        "meta": {
            "system": "Shat Trimshat Sama Dasha",
            "ayanamsa": "Sri Yukteswar",
            "is_applicable": applicable,
            "reason": f"Birth: {'Day' if is_day else 'Night'}, Asc Hora: {hora_lord}"
        },
        "calc": {
            "moon_nakshatra": nak_info['name'],
            "count_from_shravana": count,
            "remainder": remainder,
            "balance_years": round(balance_yrs, 3)
        },
        "dasha_periods": result_dashas
    }
    
    return result