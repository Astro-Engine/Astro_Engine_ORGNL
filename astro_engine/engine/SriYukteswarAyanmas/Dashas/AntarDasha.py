import os
import math
import datetime
import swisseph as swe

# --- CONFIGURATION ---
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
DASHA_SYSTEM = [
    {"planet": "Ketu", "years": 7, "lords": [0, 9, 18]},
    {"planet": "Venus", "years": 20, "lords": [1, 10, 19]},
    {"planet": "Sun", "years": 6, "lords": [2, 11, 20]},
    {"planet": "Moon", "years": 10, "lords": [3, 12, 21]},
    {"planet": "Mars", "years": 7, "lords": [4, 13, 22]},
    {"planet": "Rahu", "years": 18, "lords": [5, 14, 23]},
    {"planet": "Jupiter", "years": 16, "lords": [6, 15, 24]},
    {"planet": "Saturn", "years": 19, "lords": [7, 16, 25]},
    {"planet": "Mercury", "years": 17, "lords": [8, 17, 26]}
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# --- HELPER FUNCTIONS ---

def normalize_degrees(deg):
    """Normalize degrees to 0-360 range."""
    deg = deg % 360.0
    if deg < 0:
        deg += 360.0
    return deg

def decimal_to_dms(deg):
    """Converts decimal float to DMS string."""
    if isinstance(deg, tuple):
        deg = float(deg[0])
    val = float(deg)
    d = int(val)
    m = int((val - d) * 60)
    s = int(((val - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=float(tz_offset))
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    return float(jd)

def add_years(start_date_obj, years):
    days = years * 365.25
    return start_date_obj + datetime.timedelta(days=days)

def subtract_years(start_date_obj, years):
    days = years * 365.25
    return start_date_obj - datetime.timedelta(days=days)

# --- CORE CALCULATION LOGIC ---

def calculate_antardashas_logic(mahadasha_planet, md_start_date_str, md_end_date_str, birth_date_str, is_balance):
    # Find the main lord object
    main_lord = next((item for item in DASHA_SYSTEM if item["planet"] == mahadasha_planet), None)
    if not main_lord:
        return []

    start_idx = DASHA_SYSTEM.index(main_lord)
    
    birth_dt = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d")
    md_end_dt = datetime.datetime.strptime(md_end_date_str, "%Y-%m-%d")

    if is_balance:
        theoretical_start_dt = subtract_years(md_end_dt, main_lord['years'])
        current_calculation_dt = theoretical_start_dt
    else:
        current_calculation_dt = datetime.datetime.strptime(md_start_date_str, "%Y-%m-%d")

    antardashas = []
    
    curr_idx = start_idx
    for _ in range(9):
        if curr_idx >= len(DASHA_SYSTEM):
            curr_idx = 0
            
        sub_lord = DASHA_SYSTEM[curr_idx]
        
        months_duration = (float(main_lord['years']) * float(sub_lord['years'])) / 10.0
        days_duration = months_duration * 30.4375
        
        ad_end_dt = current_calculation_dt + datetime.timedelta(days=days_duration)
        
        if is_balance:
            if ad_end_dt > birth_dt:
                real_start = current_calculation_dt
                if current_calculation_dt < birth_dt:
                    real_start = birth_dt 
                
                antardashas.append({
                    "antardasha_lord": sub_lord['planet'],
                    "start": real_start.strftime("%Y-%m-%d"),
                    "end": ad_end_dt.strftime("%Y-%m-%d")
                })
        else:
            antardashas.append({
                "antardasha_lord": sub_lord['planet'],
                "start": current_calculation_dt.strftime("%Y-%m-%d"),
                "end": ad_end_dt.strftime("%Y-%m-%d")
            })
            
        current_calculation_dt = ad_end_dt
        curr_idx += 1
        
    return antardashas

def calculate_vimshottari(moon_lon_sidereal, birth_date):
    moon_lon_sidereal = float(moon_lon_sidereal)
    nakshatra_span = 13.3333333333
    
    nakshatra_idx = int(moon_lon_sidereal / nakshatra_span)
    nakshatra_name = NAKSHATRAS[nakshatra_idx]
    
    start_dasha_idx = 0
    for i, dasha in enumerate(DASHA_SYSTEM):
        if nakshatra_idx in dasha['lords']:
            start_dasha_idx = i
            break
            
    current_lord = DASHA_SYSTEM[start_dasha_idx]
    
    degrees_in_nakshatra = moon_lon_sidereal % nakshatra_span
    degrees_remaining = nakshatra_span - degrees_in_nakshatra
    
    balance_fraction = degrees_remaining / nakshatra_span
    balance_years = balance_fraction * current_lord['years']
    
    bal_y = int(balance_years)
    bal_m = int((balance_years - bal_y) * 12)
    bal_d = int(((balance_years - bal_y) * 12 - bal_m) * 30.44)
    balance_text = f"{current_lord['planet']} Balance: {bal_y}y {bal_m}m {bal_d}d"
    
    birth_dt = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
    timeline = []
    
    balance_days = balance_years * 365.25
    first_end_date_dt = birth_dt + datetime.timedelta(days=balance_days)
    first_end_date_str = first_end_date_dt.strftime("%Y-%m-%d")
    
    balance_antardashas = calculate_antardashas_logic(
        current_lord['planet'], 
        birth_date,            
        first_end_date_str,   
        birth_date,            
        True
    )

    timeline.append({
        "planet": current_lord['planet'],
        "start_date": birth_date,
        "end_date": first_end_date_str,
        "duration_years": round(balance_years, 2),
        "is_balance": True,
        "antardashas": balance_antardashas
    })
    
    current_date_dt = first_end_date_dt
    cycle_idx = start_dasha_idx + 1
    
    for _ in range(12): 
        if cycle_idx >= len(DASHA_SYSTEM):
            cycle_idx = 0
            
        lord = DASHA_SYSTEM[cycle_idx]
        duration_days = lord['years'] * 365.25
        end_date_dt = current_date_dt + datetime.timedelta(days=duration_days)
        
        start_str = current_date_dt.strftime("%Y-%m-%d")
        end_str = end_date_dt.strftime("%Y-%m-%d")
        
        normal_antardashas = calculate_antardashas_logic(
            lord['planet'],
            start_str,
            end_str,
            birth_date,
            False
        )
        
        timeline.append({
            "planet": lord['planet'],
            "start_date": start_str,
            "end_date": end_str,
            "duration_years": lord['years'],
            "is_balance": False,
            "antardashas": normal_antardashas
        })
        
        current_date_dt = end_date_dt
        cycle_idx += 1
        
    return {
        "birth_nakshatra": nakshatra_name,
        "nakshatra_lord": current_lord['planet'],
        "balance_string": balance_text,
        "mahadasha_timeline": timeline
    }

def maha_antar_dasha_cal(name, b_date, b_time, lat, lon, tz):
    """
    Main function to generate the complete chart data.
    Previously this logic was inside the Flask route.
    """
    
    jd = get_julian_day(b_date, b_time, tz)
    
    # Set Sri Yukteswar Ayanamsa
    swe.set_sid_mode(7, 0, 0) # 7 = SIDM_YUKTESHWAR
    ayanamsa_val = float(swe.get_ayanamsa_ut(jd))
    
    # Ascendant
    cusps, ascmc = swe.houses(jd, lat, lon, b'P') 
    asc_tropical = float(ascmc[0]) 
    asc_sidereal = normalize_degrees(asc_tropical - ayanamsa_val)
    
    # Whole Sign House Calc
    asc_sign_index = int(asc_sidereal / 30.0) 
    
    houses_data = []
    for i in range(12):
        house_num = i + 1
        current_sign_index = (asc_sign_index + i) % 12
        sign_name = SIGNS[current_sign_index]
        house_start_deg = current_sign_index * 30.0
        
        houses_data.append({
            "house": house_num,
            "sign": sign_name,
            "start_degree": house_start_deg,
            "is_ascendant": (i == 0)
        })

    # Planets
    planets_data = []
    planet_mapping = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE 
    }
    
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
    moon_long_sidereal = 0.0
    
    for p_name, p_code in planet_mapping.items():
        res = swe.calc_ut(jd, p_code, flags)
        
        if isinstance(res[0], tuple):
            lon_deg = float(res[0][0])
            is_retro = res[0][3] < 0
        else:
            lon_deg = float(res[0])
            is_retro = res[3] < 0
            
        if p_name == "Moon":
            moon_long_sidereal = lon_deg
            
        sign_idx = int(lon_deg / 30.0)
        sign_name = SIGNS[sign_idx]
        deg_in_sign = lon_deg % 30.0
        house_pos = (sign_idx - asc_sign_index + 12) % 12 + 1
        nak_idx = int(lon_deg / 13.3333333333)
        nak_name = NAKSHATRAS[nak_idx]
        
        planets_data.append({
            "name": p_name,
            "longitude": lon_deg,
            "formatted": decimal_to_dms(deg_in_sign),
            "sign": sign_name,
            "house": house_pos,
            "nakshatra": nak_name,
            "is_retrograde": is_retro
        })
        
    # Ketu
    rahu = next(p for p in planets_data if p["name"] == "Rahu")
    rahu_lon = float(rahu["longitude"])
    ketu_lon = normalize_degrees(rahu_lon + 180.0)
    ketu_sign_idx = int(ketu_lon / 30.0)
    ketu_house = (ketu_sign_idx - asc_sign_index + 12) % 12 + 1
    ketu_nak_idx = int(ketu_lon / 13.3333333333)
    
    planets_data.append({
        "name": "Ketu",
        "longitude": ketu_lon,
        "formatted": decimal_to_dms(ketu_lon % 30.0),
        "sign": SIGNS[ketu_sign_idx],
        "house": ketu_house,
        "nakshatra": NAKSHATRAS[ketu_nak_idx],
        "is_retrograde": True
    })

    # Vimshottari
    dasha_data = calculate_vimshottari(moon_long_sidereal, b_date)

    return {
        "meta": {
            "ayanamsa_system": "Sri Yukteswar",
            "ayanamsa_value": decimal_to_dms(ayanamsa_val),
            "house_system": "Whole Sign"
        },
        "profile": {
            "name": name,
            "julian_day": jd,
            "ascendant_sign": SIGNS[asc_sign_index]
        },
        "houses": houses_data,
        "planets": planets_data,
        "vimshottari_dasha": dasha_data
    }