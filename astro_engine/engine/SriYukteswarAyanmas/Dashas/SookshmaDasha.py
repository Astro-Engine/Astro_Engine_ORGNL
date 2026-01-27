import sys
import os
import datetime
from datetime import timedelta
import swisseph as swe

# --- CONFIGURATION ---
# Ensure you have the Swiss Ephemeris files in this path
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
# Standard Gregorian Year (Civil Year) used by J-Hora/Parashara
DAYS_PER_YEAR = 365.2425

DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANET_NAMES = {
    0: 'Sun', 1: 'Moon', 2: 'Mercury', 3: 'Venus', 4: 'Mars',
    5: 'Jupiter', 6: 'Saturn', 10: 'Rahu', 11: 'Ketu'
}

# --- HELPER FUNCTIONS ---

def decimal_to_degree_str(decimal_deg):
    d = int(decimal_deg)
    m = int((decimal_deg - d) * 60)
    s = int(((decimal_deg - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def get_julian_day_et(dt_utc):
    """
    Calculates Julian Day in Ephemeris Time (ET).
    Crucial for Moon precision. ET = UT + DeltaT.
    """
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    delta_t = swe.deltat(jd_ut)
    return jd_ut + delta_t

def get_nakshatra_info(moon_lon):
    """
    Calculates Nakshatra exact position.
    Uses precise 40/3 degrees span to avoid float drift.
    """
    # 360 / 27 = 13.33333333... or exactly 40.0 / 3.0
    nak_span = 40.0 / 3.0
    
    nak_index = int(moon_lon / nak_span)
    
    # Calculate degrees traversed into the specific nakshatra
    degrees_in_nak = moon_lon - (nak_index * nak_span)
    
    # Calculate Fraction Passed (0.0 to 1.0)
    fraction_passed = degrees_in_nak / nak_span
    fraction_remaining = 1.0 - fraction_passed
    
    # Nakshatra Lord
    lord_index = nak_index % 9
    lord_name = DASHA_ORDER[lord_index]
    
    return {
        "nakshatra_index": nak_index,
        "nakshatra_name": NAKSHATRAS[nak_index],
        "lord": lord_name,
        "fraction_remaining": fraction_remaining,
        "degrees_in_nak": degrees_in_nak
    }

def add_precise_days(start_date, days):
    """Helper to add days with seconds precision"""
    return start_date + timedelta(days=days)

def generate_dasha_tree(birth_date, start_lord, fraction_remaining):
    """
    Generates Vimshottari Dasha up to Sookshma (Level 4).
    """
    dashas = []
    
    # 1. Determine the "Virtual Start Date" of the First Mahadasha
    start_lord_years = DASHA_YEARS[start_lord]
    fraction_passed = 1.0 - fraction_remaining
    
    days_passed = start_lord_years * fraction_passed * DAYS_PER_YEAR
    virtual_start_date = birth_date - timedelta(days=days_passed)
    
    # Cursor management
    current_cursor = virtual_start_date
    start_index = DASHA_ORDER.index(start_lord)
    
    # --- LEVEL 1: MAHA DASHA ---
    for i in range(9):
        idx = (start_index + i) % 9
        maha_lord = DASHA_ORDER[idx]
        maha_yrs = DASHA_YEARS[maha_lord]
        
        maha_days = maha_yrs * DAYS_PER_YEAR
        maha_end = add_precise_days(current_cursor, maha_days)
        
        if maha_end < birth_date:
            current_cursor = maha_end
            continue
            
        display_maha_start = birth_date if current_cursor < birth_date else current_cursor
        
        maha_obj = {
            "lord": maha_lord,
            "start": display_maha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": maha_end.strftime("%Y-%m-%d %H:%M:%S"),
            "antardashas": []
        }
        
        # --- LEVEL 2: ANTAR DASHA ---
        antar_cursor = current_cursor
        maha_idx = DASHA_ORDER.index(maha_lord)
        
        for j in range(9):
            a_idx = (maha_idx + j) % 9
            antar_lord = DASHA_ORDER[a_idx]
            antar_yrs = DASHA_YEARS[antar_lord]
            
            # Formula: (Maha * Antar) / 120
            antar_days = (maha_yrs * antar_yrs * DAYS_PER_YEAR) / 120.0
            antar_end = add_precise_days(antar_cursor, antar_days)
            
            if antar_end < birth_date:
                antar_cursor = antar_end
                continue
                
            display_antar_start = birth_date if antar_cursor < birth_date else antar_cursor
            
            antar_obj = {
                "lord": antar_lord,
                "start": display_antar_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": antar_end.strftime("%Y-%m-%d %H:%M:%S"),
                "pratyantardashas": []
            }
            
            # --- LEVEL 3: PRATYANTAR DASHA ---
            prat_cursor = antar_cursor
            antar_idx_val = DASHA_ORDER.index(antar_lord)
            
            for k in range(9):
                p_idx = (antar_idx_val + k) % 9
                prat_lord = DASHA_ORDER[p_idx]
                prat_yrs = DASHA_YEARS[prat_lord]
                
                # Formula: (Maha * Antar * Prat) / 14400
                prat_days = (maha_yrs * antar_yrs * prat_yrs * DAYS_PER_YEAR) / 14400.0
                prat_end = add_precise_days(prat_cursor, prat_days)
                
                if prat_end < birth_date:
                    prat_cursor = prat_end
                    continue

                display_prat_start = birth_date if prat_cursor < birth_date else prat_cursor
                
                prat_obj = {
                    "lord": prat_lord,
                    "start": display_prat_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": prat_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "sookshmadashas": []
                }
                
                # --- LEVEL 4: SOOKSHMA DASHA ---
                sook_cursor = prat_cursor
                prat_idx_val = DASHA_ORDER.index(prat_lord)
                
                for m in range(9):
                    s_idx = (prat_idx_val + m) % 9
                    sook_lord = DASHA_ORDER[s_idx]
                    sook_yrs = DASHA_YEARS[sook_lord]
                    
                    # Formula: (Maha * Antar * Prat * Sook) / 1,728,000
                    sook_days = (maha_yrs * antar_yrs * prat_yrs * sook_yrs * DAYS_PER_YEAR) / 1728000.0
                    sook_end = add_precise_days(sook_cursor, sook_days)
                    
                    if sook_end < birth_date:
                        sook_cursor = sook_end
                        continue
                        
                    display_sook_start = birth_date if sook_cursor < birth_date else sook_cursor
                    
                    sook_obj = {
                        "lord": sook_lord,
                        "start": display_sook_start.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": sook_end.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    prat_obj["sookshmadashas"].append(sook_obj)
                    sook_cursor = sook_end
                    
                antar_obj["pratyantardashas"].append(prat_obj)
                prat_cursor = prat_end
                
            maha_obj["antardashas"].append(antar_obj)
            antar_cursor = antar_end
            
        dashas.append(maha_obj)
        current_cursor = maha_end
        
    return dashas

# --- MAIN LOGIC WRAPPER ---

def sookshma_dasha_data_cal(user_name, lat, lon, tz_offset, date_str, time_str):
    """
    Main function called by API.
    Performs specific Sookshma dasha calc using EPHEMERIS TIME.
    """
    dt_str = f"{date_str} {time_str}"
    
    # 1. Parse Time
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # 2. Convert to UTC (Timezone logic)
    utc_dt = local_dt - timedelta(hours=tz_offset)
    
    # 3. Calculate Julian Day in EPHEMERIS Time (JD_ET)
    jd_et = get_julian_day_et(utc_dt)
    
    # 4. Set Ayanamsa: Sri Yukteswar
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 5. Calculate Moon Position
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    moon_res = swe.calc_ut(jd_et, 1, flags)
    moon_lon = moon_res[0][0]
    
    # 6. Calculate Ascendant
    houses_res = swe.houses_ex(jd_et, lat, lon, b'W', flags)
    ascendant_lon = houses_res[1][0]
    
    # 7. Planetary Positions
    planets_data = []
    for pid, pname in PLANET_NAMES.items():
        res = swe.calc_ut(jd_et, pid, flags)
        p_lon = res[0][0]
        
        p_sign = int(p_lon / 30) + 1
        asc_sign = int(ascendant_lon / 30) + 1
        house_num = (p_sign - asc_sign) + 1
        if house_num <= 0: house_num += 12
        
        planets_data.append({
            "planet": pname,
            "longitude": p_lon,
            "dms": decimal_to_degree_str(p_lon),
            "sign_number": p_sign,
            "house_number": house_num
        })

    # 8. Generate Dasha Tree
    nak_info = get_nakshatra_info(moon_lon)
    # Pass local_dt to align output dates with user's clock
    dasha_tree = generate_dasha_tree(local_dt, nak_info['lord'], nak_info['fraction_remaining'])
    
    # Get Ayanamsa Value
    ayanamsa_val = swe.get_ayanamsa_ut(jd_et)

    return {
        "meta": {
            "user_name": user_name,
            "ayanamsa_system": "Sri Yukteswar",
            "ayanamsa_value": decimal_to_degree_str(ayanamsa_val),
            "house_system": "Whole Sign",
            "birth_datetime_local": dt_str
        },
        "moon_details": {
            "longitude": decimal_to_degree_str(moon_lon),
            "nakshatra": nak_info['nakshatra_name'],
            "nakshatra_lord": nak_info['lord'],
            "nakshatra_traversed_deg": decimal_to_degree_str(nak_info['degrees_in_nak']),
            "balance_remaining_pct": round(nak_info['fraction_remaining'] * 100, 4)
        },
        "planetary_positions": planets_data,
        "vimshottari_dasha": dasha_tree
    }