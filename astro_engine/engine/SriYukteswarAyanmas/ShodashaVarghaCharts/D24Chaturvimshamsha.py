import os
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# CONSTANTS
# ==========================================
ZODIAC_SIGNS = {
    0: "Aries", 1: "Taurus", 2: "Gemini", 3: "Cancer",
    4: "Leo", 5: "Virgo", 6: "Libra", 7: "Scorpio",
    8: "Sagittarius", 9: "Capricorn", 10: "Aquarius", 11: "Pisces"
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# D24 Deities
D24_DEITIES_ODD = [
    "Skanda", "Parshudhara", "Anala", "Vishwakarma", "Bhaga", "Mitra",
    "Maya", "Antaka", "Vrishadhwaja", "Govinda", "Madana", "Bhima"
]
D24_DEITIES_EVEN = list(reversed(D24_DEITIES_ODD))

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def decimal_to_dms(deg):
    """
    Converts decimal degrees to formatted string: 8° 21' 6.44"
    """
    d = int(deg)
    mins = (deg - d) * 60
    m = int(mins)
    s = (mins - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_pada(lon_deg):
    """
    Calculates Nakshatra and Pada from Longitude.
    Note: Standard Nakshatra is based on D1 Longitude.
    """
    # Normalize longitude
    lon_deg = lon_deg % 360
    
    # One Nakshatra = 13 degrees 20 minutes = 13.3333 deg
    nak_index = int(lon_deg / 13.333333333333334)
    nak_name = NAKSHATRAS[nak_index]
    
    # One Pada = 3 degrees 20 minutes = 3.3333 deg
    # Find position within the Nakshatra
    pos_in_nak = lon_deg % 13.333333333333334
    pada = int(pos_in_nak / 3.3333333333333335) + 1
    
    return nak_name, pada

def get_julian_day(date_str, time_str, tz_offset):
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    decimal_hour_local = hour + (minute / 60.0) + (second / 3600.0)
    decimal_hour_utc = decimal_hour_local - float(tz_offset)
    return swe.julday(year, month, day, decimal_hour_utc)

def calculate_d24_logic(lon_deg):
    """
    Core D24 Algorithm (Sri Yukteswar / Parashara).
    """
    lon_deg = lon_deg % 360
    d1_sign_index = int(lon_deg / 30)
    d1_pos_in_sign = lon_deg % 30
    
    # 1. Calculate Part Index (0-23)
    part_index = int(d1_pos_in_sign / 1.25)
    
    # 2. Odd/Even Sign Logic
    # Aries(0)=Odd, Taurus(1)=Even. Formula: (Index + 1) % 2
    is_astrological_odd = ((d1_sign_index + 1) % 2 != 0)
    
    if is_astrological_odd:
        # Odd Signs start counting from Leo (Index 4)
        d24_sign_index = (4 + part_index) % 12
        deity = D24_DEITIES_ODD[part_index % 12]
    else:
        # Even Signs start counting from Cancer (Index 3)
        d24_sign_index = (3 + part_index) % 12
        deity = D24_DEITIES_EVEN[part_index % 12]

    # 3. Precise Longitude within the D24 Sign (0-30 range)
    # The remainder of the division scaled up
    remainder = d1_pos_in_sign % 1.25
    d24_deg_precise = (remainder / 1.25) * 30.0
    
    return d24_sign_index, ZODIAC_SIGNS[d24_sign_index], d24_deg_precise, deity

def perform_d24_calculation(data):
    """
    Main logic function. Receives input dictionary, 
    performs D24 calculations, and returns the response dictionary.
    """
    # 1. Parse Input
    user_name = data.get("user_name")
    b_date = data.get("birth_date")
    b_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    
    # 2. Set Ayanamsa (Sri Yukteswar)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 3. Calculate Julian Day
    jd = get_julian_day(b_date, b_time, tz)
    
    # 4. Get Ayanamsa Value (For Notes)
    ayanamsa_val = swe.get_ayanamsa_ut(jd)
    
    # Initialize Response Structure
    response = {
        "ascendant": {},
        "birth_details": {
            "birth_date": b_date,
            "birth_time": b_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "D24 (Chaturvimshamsha)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": {},
        "user_name": user_name
    }
    
    # =========================================================
    # A. CALCULATE ASCENDANT (Sidereal D24)
    # =========================================================
    # SwissEph houses() returns Tropical. We subtract Ayanamsa.
    cusps_trop, ascmc_trop = swe.houses(jd, lat, lon, b'W')
    asc_tropical = ascmc_trop[0]
    asc_sidereal = (asc_tropical - ayanamsa_val) % 360
    
    # D24 Calculation for Ascendant
    asc_d24_idx, asc_d24_name, asc_d24_deg, asc_deity = calculate_d24_logic(asc_sidereal)
    
    # Nakshatra is based on D1 Longitude (Standard Practice)
    asc_nak, asc_pada = get_nakshatra_pada(asc_sidereal)
    
    response["ascendant"] = {
        "degrees": decimal_to_dms(asc_d24_deg), # D24 Degrees
        "nakshatra": asc_nak, # D1 Nakshatra
        "pada": asc_pada,     # D1 Pada
        "sign": asc_d24_name, # D24 Sign
        "deity": asc_deity    # D24 Specific Field
    }
    
    # Store D24 Asc Index for House Calculation
    d24_asc_index = asc_d24_idx

    # =========================================================
    # B. CALCULATE PLANETS
    # =========================================================
    # Using True Node for High Precision
    planets_list = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN), ("Rahu", swe.TRUE_NODE)
    ]
    
    for p_name, p_id in planets_list:
        # 1. Get D1 Sidereal Position & Speed
        xx, ret = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        d1_lon = xx[0]
        speed = xx[3]
        
        # Retrograde Logic
        is_retro = "R" if speed < 0 else ""
        if p_name in ["Rahu", "Ketu"]: is_retro = "R" # Nodes always R
        
        # 2. Get Nakshatra (from D1)
        nak_name, nak_pada = get_nakshatra_pada(d1_lon)
        
        # 3. Get D24 Properties
        d24_idx, d24_sign, d24_deg, d24_deity = calculate_d24_logic(d1_lon)
        
        # 4. Calculate D24 House (Whole Sign relative to D24 Asc)
        house_num = (d24_idx - d24_asc_index + 12) % 12 + 1
        
        # Populate Response
        response["planetary_positions"][p_name] = {
            "degrees": decimal_to_dms(d24_deg),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": nak_pada,
            "retrograde": is_retro,
            "sign": d24_sign,
            "deity": d24_deity # Added for D24 context
        }
        
        # 5. Handle Ketu (Opposite Rahu)
        if p_name == "Rahu":
            ketu_lon = (d1_lon + 180.0) % 360.0
            k_nak, k_pada = get_nakshatra_pada(ketu_lon)
            
            # D24 Calc for Ketu
            k_d24_idx, k_d24_sign, k_d24_deg, k_d24_deity = calculate_d24_logic(ketu_lon)
            k_house = (k_d24_idx - d24_asc_index + 12) % 12 + 1
            
            response["planetary_positions"]["Ketu"] = {
                "degrees": decimal_to_dms(k_d24_deg),
                "house": k_house,
                "nakshatra": k_nak,
                "pada": k_pada,
                "retrograde": "R",
                "sign": k_d24_sign,
                "deity": k_d24_deity
            }
            
    return response