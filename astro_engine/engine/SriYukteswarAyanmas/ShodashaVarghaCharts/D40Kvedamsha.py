import os
import swisseph as swe

# --- CONFIGURATION ---
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# --- CONSTANTS ---
PLANETS_LIST = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
]

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
    "Ketu": None # Calculated from Rahu
}

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

def decimal_to_dms_str(deg):
    """Converts decimal degrees to string format: 8° 21' 6.44" """
    d = int(deg)
    rem = (deg - d) * 60
    m = int(rem)
    s = (rem - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def normalize_degree(deg):
    deg = deg % 360
    if deg < 0:
        deg += 360
    return deg

def get_nakshatra_pada(lon_deg):
    """Calculates Nakshatra and Pada based on absolute sidereal longitude."""
    # Each Nakshatra is 13° 20' = 13.3333 deg
    nak_len = 13.33333333
    nak_idx = int(lon_deg / nak_len)
    
    # Position within the nakshatra
    rem_deg = lon_deg - (nak_idx * nak_len)
    
    # Each Pada is 3° 20' = 3.3333 deg
    pada_len = 3.33333333
    pada = int(rem_deg / pada_len) + 1
    
    return NAKSHATRAS[nak_idx % 27], pada

def calculate_d40_components(lon_deg):
    """
    Calculates the D40 Sign and D40 specific degrees.
    """
    # 1. Get D1 Sign and Degree
    d1_rasi_idx = int(lon_deg / 30)
    d1_deg_in_sign = lon_deg % 30
    
    # 2. Determine Part Number (1 to 40)
    # Each part is 0.75 degrees
    part_num = int(d1_deg_in_sign / 0.75) + 1
    
    # 3. Determine D40 Sign Index
    # Rule: Odd Signs count from Aries, Even Signs count from Libra
    if d1_rasi_idx % 2 == 0: 
        # Even Index = Aries, Gemini, Leo... (Astrological Odd Signs)
        # Count from Aries (Index 0)
        d40_sign_idx = (part_num - 1) % 12
    else:
        # Odd Index = Taurus, Cancer... (Astrological Even Signs)
        # Count from Libra (Index 6)
        d40_sign_idx = (6 + (part_num - 1)) % 12
        
    # 4. Calculate Degrees within the D40 Sign (Harmonic Degree)
    # This expands the 0.75 degree segment back to 0-30 degrees
    # Formula: (D1_Degree_In_Sign * 40) % 30
    d40_deg_val = (d1_deg_in_sign * 40) % 30
    
    return d40_sign_idx, d40_deg_val

def perform_d40_calculation(data):
    """
    Main logic function. Receives input dictionary, 
    performs D40 calculations, and returns response dictionary.
    """
    # --- 1. Parse Input ---
    year, month, day = map(int, data['birth_date'].split('-'))
    hour, minute, second = map(int, data['birth_time'].split(':'))
    lat = float(data['latitude'])
    lon = float(data['longitude'])
    tz = float(data['timezone_offset'])

    # --- 2. Time Calculation ---
    decimal_time = hour + (minute / 60.0) + (second / 3600.0)
    utc_decimal = decimal_time - tz
    jd_ut = swe.julday(year, month, day, utc_decimal)
    swe.set_topo(lat, lon, 0)

    # --- 3. Ayanamsa (Sri Yukteswar) ---
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # --- 4. Calculate Ascendant (Lagna) ---
    # Calculate Tropical Placidus first to get accurate Ascendant degree
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    asc_tropical = ascmc[0]
    # Convert to Sidereal
    asc_sidereal = normalize_degree(asc_tropical - ayanamsa_val)
    
    # Calculate D40 Ascendant
    asc_d40_sign_idx, asc_d40_deg = calculate_d40_components(asc_sidereal)
    asc_nak, asc_pada = get_nakshatra_pada(asc_sidereal)

    asc_output = {
        "degrees": decimal_to_dms_str(asc_d40_deg),
        "nakshatra": asc_nak,
        "pada": asc_pada,
        "sign": ZODIAC_SIGNS[asc_d40_sign_idx]
    }

    # --- 5. Calculate Planets ---
    planetary_positions = {}
    flags = swe.FLG_SPEED | swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # First pass to store Rahu for Ketu calculation
    temp_calc = {}

    for p_name in PLANETS_LIST:
        if p_name == "Ketu":
            # Ketu is Rahu + 180
            rahu_lon = temp_calc.get("Rahu", {}).get("lon", 0)
            rahu_speed = temp_calc.get("Rahu", {}).get("speed", 0)
            lon_deg = normalize_degree(rahu_lon + 180)
            speed = rahu_speed
        else:
            p_id = PLANET_IDS[p_name]
            calc = swe.calc_ut(jd_ut, p_id, flags)
            lon_deg = calc[0][0]
            speed = calc[0][3]
            
            # Store for Ketu lookup
            if p_name == "Rahu":
                temp_calc["Rahu"] = {"lon": lon_deg, "speed": speed}

        # -- Nakshatra (Based on D1 Sidereal Longitude) --
        nak, pada = get_nakshatra_pada(lon_deg)

        # -- D40 Calculation --
        d40_sign_idx, d40_deg = calculate_d40_components(lon_deg)

        # -- House Calculation (Whole Sign D40) --
        # House relative to D40 Ascendant Sign
        # Formula: (Planet_D40_Sign - Asc_D40_Sign + 12) % 12 + 1
        house_num = ((d40_sign_idx - asc_d40_sign_idx + 12) % 12) + 1

        # -- Retrograde Status --
        retro_str = "R" if speed < 0 else ""

        planetary_positions[p_name] = {
            "degrees": decimal_to_dms_str(d40_deg),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": retro_str,
            "sign": ZODIAC_SIGNS[d40_sign_idx]
        }

    # --- 6. Construct Final Response ---
    response = {
        "ascendant": asc_output,
        "birth_details": {
            "birth_date": data['birth_date'],
            "birth_time": data['birth_time'],
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{ayanamsa_val}",
            "chart_type": "Kvedamsha (D40)",
            "house_system": "Whole Sign"
        },
        "planetary_positions": planetary_positions,
        "user_name": data.get("user_name", "Unknown")
    }

    return response