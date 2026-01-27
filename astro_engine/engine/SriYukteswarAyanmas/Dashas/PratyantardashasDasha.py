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

def get_nakshatra_info(moon_lon):
    """
    Calculates Nakshatra index, passed degrees, and remaining fraction.
    Each Nakshatra is 13° 20' (13.333333... degrees).
    """
    nak_span = 13 + (20/60.0) # 13.333333
    nak_index = int(moon_lon / nak_span)
    
    # Nakshatra Lord is determined by the sequence repeating every 9 Nakshatras
    lord_index = nak_index % 9
    lord_name = DASHA_ORDER[lord_index]
    
    degrees_in_nak = moon_lon % nak_span
    fraction_passed = degrees_in_nak / nak_span
    fraction_remaining = 1.0 - fraction_passed
    
    return {
        "nakshatra_index": nak_index,
        "nakshatra_name": NAKSHATRAS[nak_index],
        "lord": lord_name,
        "fraction_remaining": fraction_remaining,
        "degrees_in_nak": degrees_in_nak
    }

def generate_dasha_tree(birth_date, start_lord, fraction_remaining):
    """
    Generates the Vimshottari Dasha tree (Maha > Antar > Pratyantar).
    """
    dashas = []
    
    # Find start index in the dasha cycle
    start_index = DASHA_ORDER.index(start_lord)
    
    # 1. Calculate Theoretical Start Date of the Birth Maha Dasha
    total_years_birth_lord = DASHA_YEARS[start_lord]
    fraction_passed = 1.0 - fraction_remaining
    days_passed_value = total_years_birth_lord * fraction_passed * 365.25
    
    # Current cursor tracks the theoretical timeline
    current_cursor = birth_date - timedelta(days=days_passed_value)
    
    # Generate for 120 years (9 planets)
    for i in range(9):
        maha_idx = (start_index + i) % 9
        maha_lord = DASHA_ORDER[maha_idx]
        maha_yrs = DASHA_YEARS[maha_lord]
        
        # Calculate Maha Duration in Days
        maha_days = maha_yrs * 365.25
        maha_end = current_cursor + timedelta(days=maha_days)
        
        # --- FILTER 1: Skip if Maha Dasha ended before birth ---
        if maha_end < birth_date:
            current_cursor = maha_end
            continue
        
        # --- CLAMP 1: Adjust start date if born during this period ---
        display_maha_start = birth_date if current_cursor < birth_date else current_cursor
        
        maha_obj = {
            "lord": maha_lord,
            "start": display_maha_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": maha_end.strftime("%Y-%m-%d %H:%M:%S"),
            "antardashas": []
        }
        
        # --- ANTARDASHAS ---
        antar_cursor = current_cursor
        maha_lord_idx = DASHA_ORDER.index(maha_lord)
        
        for j in range(9):
            antar_idx = (maha_lord_idx + j) % 9
            antar_lord = DASHA_ORDER[antar_idx]
            antar_yrs = DASHA_YEARS[antar_lord]
            
            # Calculate Antar Duration in Days
            antar_duration_days = (maha_yrs * antar_yrs * 365.25) / 120.0
            antar_end = antar_cursor + timedelta(days=antar_duration_days)
            
            # --- FILTER 2: Skip Antar if ended before birth ---
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
            
            # --- PRATYANTARDASHAS ---
            prat_cursor = antar_cursor
            antar_lord_idx = DASHA_ORDER.index(antar_lord)
            
            for k in range(9):
                prat_idx = (antar_lord_idx + k) % 9
                prat_lord = DASHA_ORDER[prat_idx]
                prat_yrs = DASHA_YEARS[prat_lord]
                
                # Calculate Prat Duration in Days
                prat_duration_days = (maha_yrs * antar_yrs * prat_yrs * 365.25) / 14400.0
                prat_end = prat_cursor + timedelta(days=prat_duration_days)
                
                # --- FILTER 3: Skip Prat if ended before birth ---
                if prat_end < birth_date:
                    prat_cursor = prat_end
                    continue
                
                display_prat_start = birth_date if prat_cursor < birth_date else prat_cursor
                
                prat_obj = {
                    "lord": prat_lord,
                    "start": display_prat_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": prat_end.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                antar_obj["pratyantardashas"].append(prat_obj)
                prat_cursor = prat_end # Move Prat cursor
            
            maha_obj["antardashas"].append(antar_obj)
            antar_cursor = antar_end # Move Antar cursor
            
        dashas.append(maha_obj)
        current_cursor = maha_end # Move Maha cursor

    return dashas

# --- MAIN CALCULATION WRAPPER ---

def calcu_praPratyantardashas_yuktewar(user_name, lat, lon, tz_offset, date_str, time_str):
    """
    Performs the full astrological calculation.
    """
    dt_str = f"{date_str} {time_str}"
    
    # Create Local DateTime Object
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # Convert to UTC for Swiss Ephemeris
    utc_dt = local_dt - timedelta(hours=tz_offset)
    
    # Convert to Julian Day
    jul_day_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                            utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    # 1. Set Ayanamsa: Sri Yukteswar (Code 7)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 2. Calculate Moon Position
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    moon_res = swe.calc_ut(jul_day_ut, 1, flags)
    moon_lon = moon_res[0][0]
    
    # 3. Calculate Ascendant
    houses_res = swe.houses_ex(jul_day_ut, lat, lon, b'W', flags)
    ascendant_lon = houses_res[1][0]
    
    # 4. Planetary Positions
    planets_data = []
    for pid, pname in PLANET_NAMES.items():
        res = swe.calc_ut(jul_day_ut, pid, flags)
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

    # 5. Generate Dasha Tree
    nak_info = get_nakshatra_info(moon_lon)
    # Note: We pass local_dt as birth_date because reports display local time
    dasha_tree = generate_dasha_tree(local_dt, nak_info['lord'], nak_info['fraction_remaining'])
    
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day_ut)

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
            "balance_remaining_pct": round(nak_info['fraction_remaining'] * 100, 2)
        },
        "planetary_positions": planets_data,
        "vimshottari_dasha": dasha_tree
    }