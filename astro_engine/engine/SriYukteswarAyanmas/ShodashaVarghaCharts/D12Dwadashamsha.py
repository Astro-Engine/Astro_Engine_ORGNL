import os
import math
import swisseph as swe

# ==========================================
# 1. SWISS EPHEMERIS CONFIGURATION
# ==========================================
# Ensure 'astro_api/ephe' folder exists with .se1 files
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# 2. CONSTANTS & MAPPINGS
# ==========================================
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

PLANET_MAPPING = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": "KETU_CALC"
}

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def decimal_to_dms(deg):
    """Converts decimal degrees to D° M' S" string."""
    d = int(deg)
    rem = (deg - d) * 60
    m = int(rem)
    s = (rem - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(lon):
    """Returns Nakshatra name and Pada for a given longitude."""
    nak_span = 360.0 / 27.0
    nak_index = int(lon / nak_span)
    deg_in_nak = lon - (nak_index * nak_span)
    pada_span = nak_span / 4.0
    pada = int(deg_in_nak / pada_span) + 1
    return NAKSHATRAS[nak_index % 27], pada

def get_sign_index(lon):
    """Returns the index (0-11) of the zodiac sign."""
    return int(lon / 30)

def get_d12_sign_index(d1_lon):
    """
    Calculates the D12 Sign Index (0-11) from D1 Longitude.
    Rule: Sign + (Degrees / 2.5)
    """
    d1_sign_idx = int(d1_lon / 30)
    deg_in_sign = d1_lon % 30
    part_idx = int(deg_in_sign / 2.5) # 0 to 11
    d12_sign_idx = (d1_sign_idx + part_idx) % 12
    return d12_sign_idx

def get_whole_sign_house(asc_sign_idx, planet_sign_idx):
    """Calculates House (1-12) based on Sign difference."""
    house = (planet_sign_idx - asc_sign_idx) + 1
    if house <= 0:
        house += 12
    return house

def perform_d12_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs D12 calculations, returns result dictionary.
    """
    # --- A. Parse Request ---
    user_name = data.get("user_name")
    birth_date = data.get("birth_date")
    birth_time = data.get("birth_time")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))

    # --- B. Time & Ephemeris Setup ---
    year, month, day = map(int, birth_date.split('-'))
    hour, minute, second = map(int, birth_time.split(':'))
    
    local_dec = hour + (minute / 60.0) + (second / 3600.0)
    utc_dec = local_dec - tz
    jul_day = swe.julday(year, month, day, utc_dec)

    # Set Sri Yukteswar Ayanamsa
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jul_day)

    # --- C. Calculate Ascendant (D12) ---
    # 1. Get Tropical Ascendant
    cusps, ascmc = swe.houses(jul_day, lat, lon, b'P')
    tropical_asc = ascmc[0]
    
    # 2. Convert to Sidereal D1 Ascendant
    d1_asc_deg = (tropical_asc - ayanamsa_val) % 360.0
    
    # 3. Calculate D12 Ascendant Sign
    d12_asc_sign_idx = get_d12_sign_index(d1_asc_deg)
    
    # Note: Nakshatra is typically based on D1 degrees, but for D12 specific query
    # we usually show the D1 degrees that generated this placement, or mapped degrees.
    # Following your request format, we show the D1 degrees but the D12 Sign.
    asc_nak, asc_pada = get_nakshatra(d1_asc_deg)
    
    ascendant_data = {
        "degrees": decimal_to_dms(d1_asc_deg % 30), # Degrees in D1 Sign
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": ZODIAC_SIGNS[d12_asc_sign_idx] # D12 Sign
    }

    # --- D. Calculate Planetary Positions (D12) ---
    planetary_positions = {}

    for p_name, p_code in PLANET_MAPPING.items():
        
        # 1. Get Sidereal D1 Longitude
        if p_name == "Ketu":
            res = swe.calc_ut(jul_day, swe.MEAN_NODE, swe.FLG_SIDEREAL)
            rahu_lon = res[0][0]
            planet_d1_lon = (rahu_lon + 180.0) % 360.0
            is_retro = "R"
        else:
            res = swe.calc_ut(jul_day, p_code, swe.FLG_SIDEREAL)
            coords = res[0]
            planet_d1_lon = coords[0]
            speed = coords[3]
            is_retro = "R" if speed < 0 else ""

        # 2. Calculate D12 Sign
        d12_planet_sign_idx = get_d12_sign_index(planet_d1_lon)
        
        # 3. Calculate D12 House (Relative to D12 Ascendant)
        d12_house = get_whole_sign_house(d12_asc_sign_idx, d12_planet_sign_idx)
        
        # 4. Get Nakshatra (based on D1 longitude as standard reference)
        nak, pada = get_nakshatra(planet_d1_lon)
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms(planet_d1_lon % 30), # D1 degrees context
            "house": d12_house, # D12 House
            "nakshatra": nak,
            "pada": pada,
            "retrograde": is_retro,
            "sign": ZODIAC_SIGNS[d12_planet_sign_idx] # D12 Sign
        }

    # --- E. Final Output ---
    response = {
        "user_name": user_name,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val:.6f}",
            "chart_type": "D12 (Dwadasamsa)",
            "house_system": "Whole Sign (D12)"
        },
        "ascendant": ascendant_data,
        "planetary_positions": planetary_positions
    }
    
    return response