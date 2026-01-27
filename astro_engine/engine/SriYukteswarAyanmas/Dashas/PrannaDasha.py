import os
import datetime
from datetime import timedelta
import swisseph as swe

# --- CONFIGURATION ---
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
# Standard Gregorian Year is generally used for mapping to modern calendars.
DAYS_PER_YEAR = 365.2425

# Planetary Dasha Periods (Years)
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

# --- HELPER FUNCTIONS ---

def get_julian_day_et(dt_utc):
    """Calculates Julian Day in Ephemeris Time (High Precision)."""
    # Convert to fractional hours
    h_frac = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, h_frac)
    delta_t = swe.deltat(jd_ut)
    return jd_ut + delta_t

def get_nakshatra_data(moon_lon):
    """Calculates exact Nakshatra usage and balance."""
    # 360 degrees / 27 nakshatras = 13.3333... degrees per nakshatra
    nak_span = 40.0 / 3.0
    
    nak_index = int(moon_lon / nak_span)
    degrees_traversed = moon_lon - (nak_index * nak_span)
    
    fraction_passed = degrees_traversed / nak_span
    fraction_remaining = 1.0 - fraction_passed
    
    lord_name = DASHA_ORDER[nak_index % 9]
    
    return {
        "lord": lord_name,
        "fraction_remaining": fraction_remaining,
        "nak_name": NAKSHATRAS[nak_index]
    }

def add_days(dt_obj, days_float):
    """Adds floating point days to a datetime object precisely."""
    return dt_obj + timedelta(days=days_float)

def calculate_nested_dasha(start_date, root_lord, level_1_fraction, limit_year=2100):
    """
    Calculates Vimshottari Dasha down to Level 5 (Prana).
    """
    dashas = []
    
    # 1. Calculate Birth Mahadasha "Virtual" Start
    root_years = DASHA_YEARS[root_lord]
    passed_fraction = 1.0 - level_1_fraction
    days_passed = root_years * passed_fraction * DAYS_PER_YEAR
    
    # This cursor tracks the EXACT timeline
    current_cursor = start_date - timedelta(days=days_passed)
    
    # Find start index in the cycle
    start_idx = DASHA_ORDER.index(root_lord)
    
    # --- LEVEL 1: MAHA DASHA ---
    for i in range(9):
        # Cyclical Planet Index
        l1_lord = DASHA_ORDER[(start_idx + i) % 9]
        l1_years = DASHA_YEARS[l1_lord]
        l1_days = l1_years * DAYS_PER_YEAR
        
        l1_end = add_days(current_cursor, l1_days)
        
        # Optimization: Don't calculate details for dashas that ended before birth
        if l1_end < start_date:
            current_cursor = l1_end
            continue
            
        # Optimization: Stop if we are too far in the future
        if current_cursor.year > limit_year:
            break

        # Display start is birth_date if the dasha started before birth
        display_start = start_date if current_cursor < start_date else current_cursor
        
        maha_obj = {
            "lord": l1_lord,
            "start": display_start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": l1_end.strftime("%Y-%m-%d %H:%M:%S"),
            "antardashas": []
        }
        
        # --- LEVEL 2: ANTAR DASHA ---
        l2_cursor = current_cursor
        l1_idx_val = DASHA_ORDER.index(l1_lord)
        
        for j in range(9):
            l2_lord = DASHA_ORDER[(l1_idx_val + j) % 9]
            l2_years = DASHA_YEARS[l2_lord]
            # Formula: (Maha * Antar) / 120
            l2_days = (l1_years * l2_years * DAYS_PER_YEAR) / 120.0
            l2_end = add_days(l2_cursor, l2_days)
            
            if l2_end > start_date: # Only process if relevant
                l2_display_start = start_date if l2_cursor < start_date else l2_cursor
                
                antar_obj = {
                    "lord": l2_lord,
                    "start": l2_display_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": l2_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "pratyantardashas": []
                }

                # --- LEVEL 3: PRATYANTAR DASHA ---
                l3_cursor = l2_cursor
                l2_idx_val = DASHA_ORDER.index(l2_lord)
                
                for k in range(9):
                    l3_lord = DASHA_ORDER[(l2_idx_val + k) % 9]
                    l3_years = DASHA_YEARS[l3_lord]
                    # Formula: (Maha * Antar * Prat) / 120^2
                    l3_days = (l1_years * l2_years * l3_years * DAYS_PER_YEAR) / 14400.0
                    l3_end = add_days(l3_cursor, l3_days)
                    
                    if l3_end > start_date:
                        l3_display_start = start_date if l3_cursor < start_date else l3_cursor
                        
                        prat_obj = {
                            "lord": l3_lord,
                            "start": l3_display_start.strftime("%Y-%m-%d %H:%M:%S"),
                            "end": l3_end.strftime("%Y-%m-%d %H:%M:%S"),
                            "sookshmadashas": []
                        }

                        # --- LEVEL 4: SOOKSHMA DASHA ---
                        l4_cursor = l3_cursor
                        l3_idx_val = DASHA_ORDER.index(l3_lord)

                        for m in range(9):
                            l4_lord = DASHA_ORDER[(l3_idx_val + m) % 9]
                            l4_years = DASHA_YEARS[l4_lord]
                            # Formula: (Maha * Antar * Prat * Sook) / 120^3
                            l4_days = (l1_years * l2_years * l3_years * l4_years * DAYS_PER_YEAR) / 1728000.0
                            l4_end = add_days(l4_cursor, l4_days)

                            if l4_end > start_date:
                                l4_display_start = start_date if l4_cursor < start_date else l4_cursor
                                
                                sook_obj = {
                                    "lord": l4_lord,
                                    "start": l4_display_start.strftime("%Y-%m-%d %H:%M:%S"),
                                    "end": l4_end.strftime("%Y-%m-%d %H:%M:%S"),
                                    "pranadashas": []
                                }

                                # --- LEVEL 5: PRANA DASHA ---
                                l5_cursor = l4_cursor
                                l4_idx_val = DASHA_ORDER.index(l4_lord)

                                for n in range(9):
                                    l5_lord = DASHA_ORDER[(l4_idx_val + n) % 9]
                                    l5_years = DASHA_YEARS[l5_lord]
                                    # Formula: (Maha * Antar * Prat * Sook * Prana) / 120^4
                                    numerator = (l1_years * l2_years * l3_years * l4_years * l5_years * DAYS_PER_YEAR)
                                    l5_days = numerator / 207360000.0
                                    l5_end = add_days(l5_cursor, l5_days)

                                    if l5_end > start_date:
                                        l5_display_start = start_date if l5_cursor < start_date else l5_cursor
                                        
                                        prana_obj = {
                                            "lord": l5_lord,
                                            "start": l5_display_start.strftime("%Y-%m-%d %H:%M:%S"),
                                            "end": l5_end.strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                        sook_obj["pranadashas"].append(prana_obj)
                                    
                                    l5_cursor = l5_end
                                
                                prat_obj["sookshmadashas"].append(sook_obj)
                            
                            l4_cursor = l4_end
                        
                        antar_obj["pratyantardashas"].append(prat_obj)
                    
                    l3_cursor = l3_end
                
                maha_obj["antardashas"].append(antar_obj)
            
            l2_cursor = l2_end
            
        dashas.append(maha_obj)
        current_cursor = l1_end
        
    return dashas

def perform_dasha_calculation_pranna(data):
    """
    Main Logic Function.
    Receives input dictionary, performs dasha calculations, returns result dictionary.
    """
    # Inputs
    date_str = data.get("birth_date")
    time_str = data.get("birth_time")
    tz_offset = float(data.get("timezone_offset"))
    
    # 1. Date Construction
    local_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=tz_offset)
    
    # 2. Ephemeris Calculation
    jd_et = get_julian_day_et(utc_dt)
    
    # 3. SET AYANAMSA (Critical Step)
    # Using Sri Yukteswar as requested. 
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 4. Get Moon Longitude
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    moon_res = swe.calc_ut(jd_et, swe.MOON, flags)
    moon_lon = moon_res[0][0]
    
    # 5. Dasha Tree Generation
    nak_data = get_nakshatra_data(moon_lon)
    
    dasha_tree = calculate_nested_dasha(
        local_dt, 
        nak_data['lord'], 
        nak_data['fraction_remaining']
    )
    
    result = {
        "status": "success",
        "ayanamsa_used": "Sri Yukteswar",
        "moon_longitude": moon_lon,
        "starting_dasha_balance": nak_data['fraction_remaining'],
        "vimshottari_dasha": dasha_tree
    }
    
    return result