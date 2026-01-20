import os
import swisseph as swe

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# -------------------------------------------------------------------------
# DATA & CONSTANTS
# -------------------------------------------------------------------------
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------

def format_dms_string(deg_float):
    """
    Formats degrees to exactly match sample: 6° 41' 40.86"
    """
    d = int(deg_float)
    mins = (deg_float - d) * 60
    m = int(mins)
    secs = (mins - m) * 60
    # Format seconds to 2 decimal places
    return f"{d}° {m}' {secs:.2f}\""

def get_nakshatra_pada(lon_deg):
    """
    Calculates Nakshatra and Pada from total longitude (0-360).
    Nakshatra span = 13° 20' (13.3333...)
    Pada span = 3° 20' (3.3333...)
    """
    # Normalize to 0-360
    lon_deg = lon_deg % 360
    
    nak_span = 360.0 / 27.0
    
    nak_index = int(lon_deg / nak_span)
    nak_name = NAKSHATRAS[nak_index]
    
    # Pada calculation (1-4)
    # Get longitude within the nakshatra
    rem_deg = lon_deg - (nak_index * nak_span)
    pada = int(rem_deg / (nak_span / 4)) + 1
    
    return nak_name, pada

def get_julian_day(date_str, time_str, tz_offset):
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    
    dec_time_local = hour + (minute / 60.0) + (second / 3600.0)
    dec_time_ut = dec_time_local - tz_offset
    
    return swe.julday(year, month, day, dec_time_ut)

def calculate_d45_sign(longitude, sign_idx):
    """
    Calculates the Sign in the D45 (Akshavedamsha) chart.
    """
    # 1. Division Number (0-44)
    # 30 degrees / 45 divisions = 0.6666666667 deg per division
    div_length = 30.0 / 45.0
    div_num = int(longitude / div_length)
    if div_num >= 45: div_num = 44

    # 2. Start Sign logic (Parashara)
    # Movable (1,4,7,10) -> Start Aries (0)
    # Fixed   (2,5,8,11) -> Start Leo (4)
    # Dual    (3,6,9,12) -> Start Sagittarius (8)
    
    triplicity = (sign_idx + 1) % 3
    start_offset = 0
    
    if triplicity == 1:   # Movable
        start_offset = 0
    elif triplicity == 2: # Fixed
        start_offset = 4
    else:                 # Dual
        start_offset = 8

    # 3. Final D45 Sign Index
    d45_sign_idx = (start_offset + div_num) % 12
    
    return d45_sign_idx

def perform_d45_calculation(data):
    """
    Main logic function. Receives input dictionary, 
    performs D45 calculations, and returns response dictionary.
    """
    # 1. Parse Input
    user_name = data.get("user_name", "User")
    birth_date = data.get("birth_date")
    birth_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))

    # 2. Time Setup
    jd_ut = get_julian_day(birth_date, birth_time, tz)

    # 3. Ayanamsa Setup (Sri Yukteswar)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)
    
    calc_flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED

    # 4. Planets Mapping
    planet_ids = {
        "Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2,
        "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11
    }

    # ---------------------------------------------------------
    # A. CALCULATE ASCENDANT (D45)
    # ---------------------------------------------------------
    # Get Tropical Ascendant
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'W')
    asc_tropical = ascmc[0]
    
    # Convert to Sidereal
    asc_sidereal = (asc_tropical - ayanamsa_val) % 360.0
    
    # Basic Metrics
    asc_sign_idx = int(asc_sidereal / 30)
    asc_deg_rem = asc_sidereal % 30
    asc_nak, asc_pada = get_nakshatra_pada(asc_sidereal)
    
    # D45 Calculation
    d45_asc_sign_idx = calculate_d45_sign(asc_deg_rem, asc_sign_idx)
    
    ascendant_data = {
        "degrees": format_dms_string(asc_deg_rem),
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": ZODIAC_SIGNS[d45_asc_sign_idx] # D45 Sign
    }

    # ---------------------------------------------------------
    # B. CALCULATE PLANETS
    # ---------------------------------------------------------
    planetary_positions = {}
    
    # Temporary storage to calculate Houses later
    temp_planet_data = []

    for p_name, p_id in planet_ids.items():
        # Get Position
        res_tuple, flags = swe.calc_ut(jd_ut, p_id, calc_flags)
        long_full = res_tuple[0]
        speed = res_tuple[3]
        
        # Retrograde String ("R" or "")
        is_retro = "R" if speed < 0 else ""
        
        # Metrics
        sign_idx = int(long_full / 30)
        deg_rem = long_full % 30
        nak, pada = get_nakshatra_pada(long_full)
        
        # D45 Calculation
        d45_sign_idx = calculate_d45_sign(deg_rem, sign_idx)
        
        p_data = {
            "name": p_name,
            "degrees": format_dms_string(deg_rem), # D1 Degree (Reference)
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": ZODIAC_SIGNS[d45_sign_idx], # D45 Sign
            "d45_sign_idx": d45_sign_idx # For House calc
        }
        temp_planet_data.append(p_data)

    # ---------------------------------------------------------
    # C. CALCULATE KETU (Opposite Rahu)
    # ---------------------------------------------------------
    # Recalculate Rahu Full Longitude
    rahu_res, _ = swe.calc_ut(jd_ut, 11, calc_flags)
    rahu_full = rahu_res[0]
    
    ketu_full = (rahu_full + 180.0) % 360.0
    ketu_sign_idx = int(ketu_full / 30)
    ketu_deg_rem = ketu_full % 30
    ketu_nak, ketu_pada = get_nakshatra_pada(ketu_full)
    
    d45_ketu_sign_idx = calculate_d45_sign(ketu_deg_rem, ketu_sign_idx)
    
    ketu_data = {
        "name": "Ketu",
        "degrees": format_dms_string(ketu_deg_rem),
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "retrograde": "", 
        "sign": ZODIAC_SIGNS[d45_ketu_sign_idx],
        "d45_sign_idx": d45_ketu_sign_idx
    }
    
    temp_planet_data.append(ketu_data)

    # ---------------------------------------------------------
    # D. ASSIGN D45 HOUSES & FORMAT FINAL DICT
    # ---------------------------------------------------------
    for p in temp_planet_data:
        # House = (Planet Sign - Asc Sign) + 1
        house_num = (p["d45_sign_idx"] - d45_asc_sign_idx) + 1
        if house_num <= 0:
            house_num += 12
        
        # Construct Final Object for this planet
        planetary_positions[p["name"]] = {
            "degrees": p["degrees"],
            "house": house_num,
            "nakshatra": p["nakshatra"],
            "pada": p["pada"],
            "retrograde": p["retrograde"],
            "sign": p["sign"]
        }

    # ---------------------------------------------------------
    # E. CONSTRUCT RESPONSE
    # ---------------------------------------------------------
    response = {
        "ascendant": ascendant_data,
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
            "chart_type": "D45 (Akshavedamsha)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": user_name
    }

    return response