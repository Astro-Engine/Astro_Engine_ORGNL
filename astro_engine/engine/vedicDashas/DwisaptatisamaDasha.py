import swisseph as swe
from datetime import datetime, timedelta

# Set Ephemeris Path
swe.set_ephe_path('astro_api/ephe')

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Fixed 8-planet sequence for Dwisaptatisama
DASHA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]

def get_zodiac_sign(longitude):
    return int(longitude / 30) + 1

def get_house(planet_long, lagna_long):
    lagna_sign = get_zodiac_sign(lagna_long)
    planet_sign = get_zodiac_sign(planet_long)
    house = (planet_sign - lagna_sign + 1)
    if house <= 0: house += 12
    return house

def get_lord_of_sign(sign_index):
    rulers = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury", 
              7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"}
    return rulers.get(sign_index)

def calculate_dwisaptati_dasha(user_name, dob_str, tob_str, lat, lon, tz):
    """
    Calculate Dwisaptati Dasha (72-year cycle) based on birth details
    
    Args:
        user_name: User's name
        dob_str: Date of birth (YYYY-MM-DD)
        tob_str: Time of birth (HH:MM:SS)
        lat: Latitude
        lon: Longitude
        tz: Timezone offset
        
    Returns:
        Dictionary with user info and dwisaptati dasha periods
    """
    # Julian Day calculation (UTC)
    dt_birth = datetime.strptime(f"{dob_str} {tob_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = dt_birth - timedelta(hours=tz)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # Lagna and Planet positions
    res, ascmc = swe.houses_ex(jd, lat, lon, b'W')
    lagna_long = ascmc[0]
    lagna_sign = get_zodiac_sign(lagna_long)
    
    moon_res, _ = swe.calc_ut(jd, swe.MOON, flag)
    moon_long = moon_res[0]
    
    # Condition Check: Lagna Lord in 7th or 7th Lord in 1st
    lagna_lord = get_lord_of_sign(lagna_sign)
    seventh_sign = (lagna_sign + 6) if (lagna_sign + 6) <= 12 else (lagna_sign - 6)
    seventh_lord = get_lord_of_sign(seventh_sign)
    
    lord_map = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
                "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
    
    pos_l_lord = get_house(swe.calc_ut(jd, lord_map[lagna_lord], flag)[0][0], lagna_long)
    pos_s_lord = get_house(swe.calc_ut(jd, lord_map[seventh_lord], flag)[0][0], lagna_long)
    is_applicable = (pos_l_lord == 7 or pos_s_lord == 1)

    # Dasha Selection Logic
    nak_len = 360 / 27
    janma_nak_idx = int(moon_long / nak_len)
    # Count from Moola (19th Nakshatra)
    count = (janma_nak_idx + 1) - 19 + 1
    if count <= 0: count += 27
    
    remainder = count % 8
    if remainder == 0: remainder = 8
    start_lord_idx = remainder - 1 

    # Calculation of Balance at Birth
    remaining_perc = (nak_len - (moon_long % nak_len)) / nak_len
    total_mahadasha_days = 9 * 365.2425 # Accurate year length
    balance_days = remaining_perc * total_mahadasha_days
    
    full_timeline = []
    current_date = dt_birth

    # Calculate 144 years (Two 72-year cycles)
    for cycle in range(2):
        for i in range(8):
            m_idx = (start_lord_idx + i) % 8
            m_lord = DASHA_LORDS[m_idx]
            
            # Initial balance only applies to the very first Mahadasha of the first cycle
            is_first = (cycle == 0 and i == 0)
            m_duration = balance_days if is_first else total_mahadasha_days
            m_end = current_date + timedelta(days=m_duration)
            
            # Calculate Antardashas (8 equal parts)
            antardashas = []
            a_start = current_date
            a_dur = m_duration / 8
            
            for j in range(8):
                a_idx = (m_idx + j) % 8
                a_end = a_start + timedelta(days=a_dur)
                antardashas.append({
                    "antar_lord": DASHA_LORDS[a_idx],
                    "start": a_start.strftime("%d-%m-%Y"),
                    "end": a_end.strftime("%d-%m-%Y")
                })
                a_start = a_end
            
            full_timeline.append({
                "cycle": cycle + 1,
                "mahadasha": m_lord,
                "start": current_date.strftime("%d-%m-%Y"),
                "end": m_end.strftime("%d-%m-%Y"),
                "antardashas": antardashas
            })
            current_date = m_end

    return {
        "meta": {
            "user": user_name,
            "nakshatra": NAKSHATRAS[janma_nak_idx],
            "is_applicable": is_applicable,
            "system_years": 144
        },
        "dasha_table": full_timeline
    }