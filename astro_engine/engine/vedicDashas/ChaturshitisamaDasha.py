import swisseph as swe
from datetime import datetime, timedelta

# Swiss Ephemeris root path
swe.set_ephe_path('astro_api/ephe')

# Constants for Chaturshitisama (Strict Weekday Order)
PLANETS_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
# Remainder mapping: 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 0=Saturn
REM_TO_PLANET = {1: "Sun", 2: "Moon", 3: "Mars", 4: "Mercury", 5: "Jupiter", 6: "Venus", 0: "Saturn"}

MD_YEARS = 12
AD_YEARS = 12 / 7 

def add_precise_years(start_date, years_val):
    # Standard solar year for dasha alignment
    return start_date + timedelta(days=years_val * 365.25)

def calculate_chaturshitisama_swati_dasha(user_name, dob_str, tob_str, lat, lon, tz):
    """
    Calculate Chaturshitisama Dasha based on birth details (Swati-based counting)
    
    Args:
        user_name: User's name
        dob_str: Date of birth (YYYY-MM-DD)
        tob_str: Time of birth (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with user info and chaturshitisama dasha periods
    """
    birth_dt = datetime.strptime(f"{dob_str} {tob_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = birth_dt - timedelta(hours=tz)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_data, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    moon_lon = moon_data[0]

    # 1. CORRECT NAKSHATRA ROOT LOGIC (Count from Swati)
    nak_no = int(moon_lon / (360/27)) + 1
    # Calculate count from Swati (15th Nakshatra)
    # formula: (Birth Nak - 15 + 1). If <= 0, add 27.
    count_from_swati = (nak_no - 15) + 1
    if count_from_swati <= 0:
        count_from_swati += 27
    
    # 2. ASSIGN MD LORD
    rem = count_from_swati % 7
    md_lord = REM_TO_PLANET[rem]
    
    # 3. CALCULATE BALANCE
    nak_width = 360/27
    elapsed_in_nak = moon_lon % nak_width
    frac_rem = (nak_width - elapsed_in_nak) / nak_width
    md_balance = frac_rem * MD_YEARS
    md_elapsed = MD_YEARS - md_balance
    
    # Start of the current Mahadasha cycle (pre-birth)
    theoretical_md_start = birth_dt - timedelta(days=md_elapsed * 365.25)

    dasha_table = []
    current_md_start = theoretical_md_start
    start_idx = PLANETS_ORDER.index(md_lord)

    # Generate 8-9 Mahadasha Blocks
    for i in range(9):
        current_md_lord = PLANETS_ORDER[(start_idx + i) % 7]
        current_md_end = add_precise_years(current_md_start, MD_YEARS)
        
        # Sub-periods (Antardashas)
        antardashas = []
        # In Chaturshitisama, AD starts with the MD Lord itself
        ad_start_idx = PLANETS_ORDER.index(current_md_lord)
        current_ad_start = current_md_start
        
        for j in range(7):
            ad_lord = PLANETS_ORDER[(ad_start_idx + j) % 7]
            current_ad_end = add_precise_years(current_ad_start, AD_YEARS)
            
            # Show only Antardashas that end AFTER birth
            if current_ad_end > birth_dt:
                display_start = birth_dt if current_ad_start < birth_dt else current_ad_start
                antardashas.append({
                    "antardasha_lord": ad_lord,
                    "beginning": display_start.strftime("%d-%m-%Y"),
                    "ending": current_ad_end.strftime("%d-%m-%Y")
                })
            current_ad_start = current_ad_end

        # Clip MD start for the very first block displayed
        md_display_start = birth_dt if current_md_start < birth_dt else current_md_start

        dasha_table.append({
            "mahadasha_lord": current_md_lord,
            "mahadasha_beginning": md_display_start.strftime("%d-%m-%Y"),
            "mahadasha_ending": current_md_end.strftime("%d-%m-%Y"),
            "duration": "12y",
            "antardashas": antardashas
        })
        current_md_start = current_md_end

    return {
        "user": user_name,
        "dasha_system": "Chaturshitisama Mahadasha",
        "dasha_balance_at_birth": f"{md_lord} {round(md_balance, 4)} years",
        "dasha_table": dasha_table
    }