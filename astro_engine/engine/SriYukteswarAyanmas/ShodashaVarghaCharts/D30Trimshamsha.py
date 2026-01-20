import os
import swisseph as swe
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Path to Swiss Ephemeris files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def decimal_to_dms(deg):
    """Converts decimal degrees to formatted DMS string."""
    d = int(deg)
    m_float = (deg - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_julian_day(date_str, time_str, tz_offset):
    dt_str = f"{date_str} {time_str}"
    dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    decimal_hours_local = dt_obj.hour + (dt_obj.minute / 60.0) + (dt_obj.second / 3600.0)
    decimal_hours_utc = decimal_hours_local - float(tz_offset)
    return swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, decimal_hours_utc)

def get_nakshatra_pada(lon_deg):
    """Calculates Nakshatra and Pada from longitude."""
    # Normalize longitude 0-360
    lon_deg = lon_deg % 360
    nak_span = 13.0 + (20.0/60.0) # 13 degrees 20 minutes
    
    nak_index = int(lon_deg / nak_span)
    nak_name = NAKSHATRAS[nak_index % 27]
    
    # Calculate Pada (1-4)
    # Each Nakshatra has 4 padas.
    rem_deg = lon_deg - (nak_index * nak_span)
    pada_span = 3.0 + (20.0/60.0) # 3 degrees 20 minutes
    pada = int(rem_deg / pada_span) + 1
    
    return nak_name, pada

def calculate_d30_sign_index(lon_deg):
    """
    Core Logic: Calculates the D30 Sign Index based on Parashara Rules.
    """
    # 1. Get Rashi (D1) properties
    rashi_idx = int(lon_deg / 30) # 0=Aries, etc.
    deg_in_sign = lon_deg % 30
    
    # 2. Determine Odd or Even Sign
    # Aries(0) is Odd, Taurus(1) is Even...
    # In programming index: Even numbers (0,2,4) are ODD SIGNS (Aries, Gemini).
    # Odd numbers (1,3,5) are EVEN SIGNS (Taurus, Cancer).
    is_odd_sign_rashi = (rashi_idx % 2 == 0)
    
    d30_sign_id = 0
    
    if is_odd_sign_rashi:
        # Rules for ODD Signs (Aries, Gemini, Leo, Libra, Sag, Aqua)
        # 0-5: Mars (Aries-0)
        # 5-10: Saturn (Aquarius-10)
        # 10-18: Jupiter (Sagittarius-8)
        # 18-25: Mercury (Gemini-2)
        # 25-30: Venus (Libra-6)
        if deg_in_sign < 5:
            d30_sign_id = 0 # Aries
        elif deg_in_sign < 10:
            d30_sign_id = 10 # Aquarius
        elif deg_in_sign < 18:
            d30_sign_id = 8 # Sagittarius
        elif deg_in_sign < 25:
            d30_sign_id = 2 # Gemini
        else:
            d30_sign_id = 6 # Libra
            
    else:
        # Rules for EVEN Signs (Taurus, Cancer, Virgo, Scorpio, Cap, Pisces)
        # 0-5: Venus (Taurus-1)
        # 5-12: Mercury (Virgo-5)
        # 12-20: Jupiter (Pisces-11)
        # 20-25: Saturn (Capricorn-9)
        # 25-30: Mars (Scorpio-7)
        if deg_in_sign < 5:
            d30_sign_id = 1 # Taurus
        elif deg_in_sign < 12:
            d30_sign_id = 5 # Virgo
        elif deg_in_sign < 20:
            d30_sign_id = 11 # Pisces
        elif deg_in_sign < 25:
            d30_sign_id = 9 # Capricorn
        else:
            d30_sign_id = 7 # Scorpio
            
    return d30_sign_id

def calculate_whole_sign_house(planet_sign_idx, asc_sign_idx):
    """Calculates House Number (1-12) based on Whole Sign system."""
    # (Planet - Asc + 12) % 12 + 1
    # Example: Asc=0 (Aries), Planet=1 (Taurus). (1-0+12)%12 + 1 = 2nd House
    h = (planet_sign_idx - asc_sign_idx + 12) % 12 + 1
    return h

def perform_d30_calculation(data):
    """
    Main logic function. Receives dictionary 'data', 
    performs calculations, returns response dictionary.
    """
    # 1. Julian Day
    jd_ut = get_julian_day(data['birth_date'], data['birth_time'], data['timezone_offset'])
    
    # 2. Set Sri Yukteswar Ayanamsa
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    
    # 3. Calculate Ascendant (D1) Longitude first to derive D30 Ascendant
    lat = float(data['latitude'])
    lon = float(data['longitude'])
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_deg_d1 = ascmc[0]
    
    # 4. Calculate D30 Ascendant Sign
    d30_asc_sign_idx = calculate_d30_sign_index(asc_deg_d1)
    d30_asc_sign_name = ZODIAC_SIGNS[d30_asc_sign_idx]
    
    # Get Nakshatra for Ascendant (based on D1 degree)
    asc_nak, asc_pada = get_nakshatra_pada(asc_deg_d1)
    
    # Format Ascendant Block
    ascendant_data = {
        "degrees": decimal_to_dms(asc_deg_d1 % 30), # Degree within sign
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": d30_asc_sign_name # THIS IS THE D30 SIGN
    }

    # 5. Calculate Planets
    # Map of swisseph IDs to names
    bodies = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    
    planetary_positions = {}
    
    # Store Rahu longitude to calculate Ketu
    rahu_lon_d1 = 0
    
    for name, pid in bodies.items():
        # Get D1 Sidereal Position
        res = swe.calc_ut(jd_ut, pid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon_d1 = res[0][0]
        speed = res[0][3]
        
        if name == "Rahu":
            rahu_lon_d1 = lon_d1
        
        # Calculate D30 Sign
        d30_sign_idx = calculate_d30_sign_index(lon_d1)
        
        # Calculate House in D30 (Relative to D30 Ascendant)
        d30_house = calculate_whole_sign_house(d30_sign_idx, d30_asc_sign_idx)
        
        # Get Nakshatra (based on source longitude)
        nak, pada = get_nakshatra_pada(lon_d1)
        
        # Retrograde check
        is_retro = "R" if speed < 0 else ""
        if name in ["Rahu", "Ketu"]: is_retro = "R" # Nodes always R (usually)
        
        planetary_positions[name] = {
            "degrees": decimal_to_dms(lon_d1 % 30),
            "house": d30_house,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": ZODIAC_SIGNS[d30_sign_idx] # D30 Sign
        }
        
    # Calculate Ketu (180 deg from Rahu)
    ketu_lon_d1 = (rahu_lon_d1 + 180.0) % 360.0
    ketu_d30_sign_idx = calculate_d30_sign_index(ketu_lon_d1)
    ketu_d30_house = calculate_whole_sign_house(ketu_d30_sign_idx, d30_asc_sign_idx)
    k_nak, k_pada = get_nakshatra_pada(ketu_lon_d1)
    
    planetary_positions["Ketu"] = {
        "degrees": decimal_to_dms(ketu_lon_d1 % 30),
        "house": ketu_d30_house,
        "nakshatra": k_nak,
        "pada": k_pada,
        "retrograde": "R",
        "sign": ZODIAC_SIGNS[ketu_d30_sign_idx] # D30 Sign
    }

    # 6. Build Final Response
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)
    
    response = {
        "ascendant": ascendant_data,
        "birth_details": {
            "birth_date": data['birth_date'],
            "birth_time": data['birth_time'],
            "latitude": data['latitude'],
            "longitude": data['longitude'],
            "timezone_offset": data['timezone_offset']
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(ayanamsa_val),
            "chart_type": "D30 (Trimshamsha)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": data.get("user_name", "User")
    }
    
    return response