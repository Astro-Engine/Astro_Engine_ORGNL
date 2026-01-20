import os
import datetime
import swisseph as swe

# --- Configuration ---
# Path to your Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- Constants ---
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

# --- Core Logic Functions ---

def decimal_to_dms(deg_float):
    """Converts decimal degrees to formatted D° M' S" string."""
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_pada(longitude):
    """Calculates Nakshatra and Pada for a given 0-360 longitude."""
    # Nakshatra = 13° 20' (13.3333...)
    nak_len = 13.333333333333334
    nak_index = int(longitude / nak_len)
    nak_name = NAKSHATRAS[nak_index % 27]
    
    # Pada = 3° 20' (3.3333...)
    rem_deg = longitude % nak_len
    pada_len = 3.3333333333333335
    pada = int(rem_deg / pada_len) + 1
    
    return nak_name, pada

def get_whole_sign_house(planet_sign_index, asc_sign_index):
    """Calculates House number (1-12) relative to Ascendant."""
    h = (planet_sign_index - asc_sign_index) + 1
    if h <= 0: h += 12
    return h

def calculate_d20_position(d1_longitude):
    """
    Converts D1 Longitude to D20 (Vimshamsha) Sign and Degree.
    
    Rules:
    1. Movable (Ari, Can, Lib, Cap): Start count from Aries.
    2. Fixed (Tau, Leo, Sco, Aqu): Start count from Sagittarius.
    3. Dual (Gem, Vir, Sag, Pis): Start count from Leo.
    4. Each D20 part is 1° 30' (1.5 degrees).
    """
    # Normalize
    d1_longitude = d1_longitude % 360
    
    d1_sign_idx = int(d1_longitude / 30)
    d1_deg_in_sign = d1_longitude % 30
    
    # Determine Modality: 0=Movable, 1=Fixed, 2=Dual
    modality = d1_sign_idx % 3
    
    if modality == 0:   # Movable -> Starts Aries (0)
        start_offset = 0
    elif modality == 1: # Fixed -> Starts Sagittarius (8)
        start_offset = 8
    else:               # Dual -> Starts Leo (4)
        start_offset = 4
        
    # Calculate Part Index (0-19)
    part_idx = int(d1_deg_in_sign / 1.5)
    
    # Determine D20 Sign
    d20_sign_idx = (start_offset + part_idx) % 12
    
    # Calculate exact degree within that D20 sign
    # We map the 1.5 degree slice to a full 30 degree slice
    deg_in_slice = d1_deg_in_sign % 1.5
    d20_deg_projected = (deg_in_slice / 1.5) * 30
    
    # Absolute longitude in D20 (for Nakshatra calc)
    d20_total_long = (d20_sign_idx * 30) + d20_deg_projected
    
    return {
        "sign_idx": d20_sign_idx,
        "sign_name": ZODIAC_SIGNS[d20_sign_idx],
        "degrees_dms": decimal_to_dms(d20_deg_projected),
        "total_long": d20_total_long
    }

def perform_d20_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all D20 calculations, returns result dictionary.
    """
    # 1. Input Parsing
    user_name = data.get('user_name')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))
    
    # 2. Time Calculation (UT)
    dt_str = f"{birth_date} {birth_time}"
    local_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - datetime.timedelta(hours=tz)
    
    hour_dec = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
    
    # 3. Set Ayanamsa (Sri Yukteswar)
    # ID 7 = SE_SIDM_YUKTESHWAR
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd)
    
    # 4. Calculate Ascendant (CRITICAL FIX HERE)
    # swe.houses returns TROPICAL cusps by default unless we handle flags carefully.
    # To be 100% safe, we calculate Tropical Ascendant and manually subtract Ayanamsa.
    
    # Calculate Tropical Ascendant first
    # h_sys='W' (Whole) or 'P' (Placidus) doesn't affect the Ascendant degree (ascmc[0])
    cusps, ascmc = swe.houses(jd, lat, lon, b'W') 
    tropical_asc_deg = ascmc[0]
    
    # Convert to Sidereal (Sri Yukteswar)
    sidereal_asc_deg = (tropical_asc_deg - ayanamsa_val) % 360
    
    # Convert Sidereal Ascendant to D20
    d20_asc = calculate_d20_position(sidereal_asc_deg)
    d20_lagna_idx = d20_asc['sign_idx'] # Store this to calculate houses
    
    # Ascendant Response Object
    asc_nak, asc_pada = get_nakshatra_pada(d20_asc['total_long'])
    asc_obj = {
        "degrees": d20_asc['degrees_dms'],
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": d20_asc['sign_name']
    }
    
    # 5. Calculate Planets
    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE # Standard for Vedic
    }
    
    positions = {}
    
    # Flags: Swiss Ephemeris + Sidereal + Speed (for retro check)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    for name, pid in planets_map.items():
        # Calculate Sidereal Position
        xx, _ = swe.calc_ut(jd, pid, flags)
        d1_long = xx[0]
        speed = xx[3]
        
        # Check Retrograde
        is_retro = "R" if (speed < 0 or name in ["Rahu", "Ketu"]) else ""
        if name == "Rahu": is_retro = "R" # Force R for Nodes
        
        # Convert D1 -> D20
        d20_p = calculate_d20_position(d1_long)
        
        # Calculate House (Relative to D20 Ascendant)
        house_num = get_whole_sign_house(d20_p['sign_idx'], d20_lagna_idx)
        
        # Nakshatra
        nak, pada = get_nakshatra_pada(d20_p['total_long'])
        
        positions[name] = {
            "degrees": d20_p['degrees_dms'],
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": d20_p['sign_name']
        }
        
        # Handle Ketu (Opposite Rahu)
        if name == "Rahu":
            d1_ketu_long = (d1_long + 180) % 360
            d20_k = calculate_d20_position(d1_ketu_long)
            k_house = get_whole_sign_house(d20_k['sign_idx'], d20_lagna_idx)
            k_nak, k_pada = get_nakshatra_pada(d20_k['total_long'])
            
            positions["Ketu"] = {
                "degrees": d20_k['degrees_dms'],
                "house": k_house,
                "nakshatra": k_nak,
                "pada": k_pada,
                "retrograde": "R",
                "sign": d20_k['sign_name']
            }

    # 6. Final JSON Response
    response = {
        "ascendant": asc_obj,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "Vimshamsha (D20)",
            "house_system": "Whole Sign (D20 Lagna)"
        },
        "planetary_positions": dict(sorted(positions.items())),
        "user_name": user_name
    }
    
    return response