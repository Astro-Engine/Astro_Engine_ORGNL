import swisseph as swe
from datetime import datetime, timedelta

# Set the path for Swiss Ephemeris files
swe.set_ephe_path('astro_api/ephe')

# Satabdika Dasha Config
# Order: Sun(5), Moon(5), Venus(10), Mercury(10), Jupiter(20), Mars(20), Saturn(30)
DASHA_SEQUENCE = ["Sun", "Moon", "Venus", "Mercury", "Jupiter", "Mars", "Saturn"]
DASHA_YEARS = {
    "Sun": 5, "Moon": 5, "Venus": 10, "Mercury": 10, 
    "Jupiter": 20, "Mars": 20, "Saturn": 30
}

# Remainder mapping from Revati counting
REMAINDER_MAP = {1: "Sun", 2: "Moon", 3: "Venus", 4: "Mercury", 5: "Jupiter", 6: "Mars", 0: "Saturn"}

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyesha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def get_vargottama_status(lagna_deg):
    sign_idx = int(lagna_deg / 30)
    deg_in_sign = lagna_deg % 30
    nav_idx = int(deg_in_sign / (3 + 1/3))
    # Vargottama: 1st Navamsa in Movable, 5th in Fixed, 9th in Dual
    if sign_idx in [0, 3, 6, 9] and nav_idx == 0: return True
    if sign_idx in [1, 4, 7, 10] and nav_idx == 4: return True
    if sign_idx in [2, 5, 8, 11] and nav_idx == 8: return True
    return False

def add_years(start_date, years):
    days = years * 365.25
    return start_date + timedelta(days=days)

def calculate_satabdika_dasha(user_name, dob, tob, lat, lon, tz):
    """
    Calculate Satabdika Dasha based on birth details
    
    Args:
        user_name: User's name
        dob: Date of birth (YYYY-MM-DD)
        tob: Time of birth (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with user info and satabdika dasha periods
    """
    # Time Setup
    dt_obj = datetime.strptime(f"{dob} {tob}", '%Y-%m-%d %H:%M:%S')
    utc_dt = dt_obj - timedelta(hours=tz)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

    # Sidereal Calc (Lahiri)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Lagna & Vargottama
    res, ascmc = swe.houses_ex(jd, lat, lon, b'W')
    is_vargottama = get_vargottama_status(ascmc[0])

    # Moon & Nakshatra
    moon_pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    moon_lon = moon_pos[0]
    nak_idx = int(moon_lon / (13 + 1/3))
    
    # Logic: Count from Revati (idx 26) to Janma Nakshatra
    count = (nak_idx + 1) if nak_idx == 26 else (nak_idx + 2)
    md_lord = REMAINDER_MAP[count % 7]

    # Calculate Balance
    nak_start = nak_idx * (13 + 1/3)
    rem_deg = (13 + 1/3) - (moon_lon - nak_start)
    md_total_yrs = DASHA_YEARS[md_lord]
    md_balance_yrs = (rem_deg / (13 + 1/3)) * md_total_yrs
    md_elapsed_yrs = md_total_yrs - md_balance_yrs

    dasha_output = []
    current_md_start = dt_obj - timedelta(days=md_elapsed_yrs * 365.25)
    
    # Generate 100-year cycle (7 Major periods)
    start_idx = DASHA_SEQUENCE.index(md_lord)
    for i in range(7):
        loop_md_lord = DASHA_SEQUENCE[(start_idx + i) % 7]
        loop_md_yrs = DASHA_YEARS[loop_md_lord]
        md_end = add_years(current_md_start, loop_md_yrs)
        
        # Skip MD if it ended before birth (only relevant for the very first MD)
        if md_end <= dt_obj and i == 0:
            current_md_start = md_end
            continue

        # Antardashas for this MD
        antardashas = []
        ad_start = current_md_start
        ad_seq_start_idx = DASHA_SEQUENCE.index(loop_md_lord)
        
        for j in range(7):
            ad_lord = DASHA_SEQUENCE[(ad_seq_start_idx + j) % 7]
            # Formula: (MD_Yrs * AD_Lord_Base_Yrs) / 100
            ad_duration = (loop_md_yrs * DASHA_YEARS[ad_lord]) / 100
            ad_end = add_years(ad_start, ad_duration)
            
            # Only include Antardashas that end after birth
            if ad_end > dt_obj:
                antardashas.append({
                    "lord": ad_lord,
                    "start_date": ad_start.strftime('%Y-%m-%d') if ad_start > dt_obj else dt_obj.strftime('%Y-%m-%d'),
                    "end_date": ad_end.strftime('%Y-%m-%d')
                })
            ad_start = ad_end

        dasha_output.append({
            "lord": loop_md_lord,
            "start_date": current_md_start.strftime('%Y-%m-%d') if current_md_start > dt_obj else dt_obj.strftime('%Y-%m-%d'),
            "end_date": md_end.strftime('%Y-%m-%d'),
            "antardashas": antardashas
        })
        current_md_start = md_end

    return {
        "user_info": {
            "user_name": user_name,
            "is_vargottama": is_vargottama,
            "janma_nakshatra": NAKSHATRA_NAMES[nak_idx],
            "moon_longitude": round(moon_lon, 4)
        },
        "satabdika_dasha": dasha_output
    }