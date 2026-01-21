import os
import math
import swisseph as swe

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = 'astro_api/ephe'
swe.set_ephe_path(EPHE_PATH)

# ==========================================
# DATA CONSTANTS
# ==========================================
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def format_dms_string(deg_float):
    """Formats decimal degrees to 332° 35' 13.13" string"""
    d = int(deg_float)
    m_full = (deg_float - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def normalize(deg):
    """Normalize angle to 0-360 range"""
    while deg < 0: deg += 360
    while deg >= 360: deg -= 360
    return deg

def get_distance(start, end):
    """Calculate distance between two points on the circle"""
    if end >= start: return end - start
    return (end + 360) - start

def get_sign_name(lon):
    """Get Zodiac Sign name from longitude"""
    idx = int(lon / 30)
    if idx >= 12: idx = 0
    return ZODIAC_SIGNS[idx]

def get_nakshatra_details(lon_deg):
    """Calculates Nakshatra name and Pada (1-4)"""
    # 360 / 27 = 13.3333... degrees per Nakshatra
    nak_span = 360.0 / 27.0
    nak_index = int(lon_deg / nak_span)
    
    # Remainder for Pada
    rem_deg = lon_deg - (nak_index * nak_span)
    pada_span = nak_span / 4.0
    pada = int(rem_deg / pada_span) + 1
    
    if nak_index >= 27: nak_index = 0
    
    return {
        "name": NAKSHATRAS[nak_index],
        "pada": pada
    }

def perform_astrology_calculation_sripathi(data):
    """
    Main Logic Function.
    Receives input dictionary, performs Bhava Chalit calculations, returns result dictionary.
    """
    # 1. Parsing Inputs
    name = data.get('user_name', 'User')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    tz = float(data.get('timezone_offset'))

    y, m, d = map(int, birth_date.split('-'))
    h, min_, s = map(int, birth_time.split(':'))

    # 2. Julian Day Calculation (UT)
    dec_hour_local = h + (min_/60.0) + (s/3600.0)
    dec_hour_ut = dec_hour_local - tz
    jd_ut = swe.julday(y, m, d, dec_hour_ut)

    # 3. Ayanamsa: Sri Yukteswar (Strict)
    swe.set_sid_mode(swe.SIDM_YUKTESHWAR, 0, 0)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    # 4. Calculate Angles (Ascendant/MC)
    # We use 'P' (Porphyry) just to get the Sidereal Asc/MC degrees strictly.
    cusps_raw, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    asc_deg = ascmc[0]
    mc_deg = ascmc[1]
    
    ic_deg = normalize(mc_deg + 180)
    desc_deg = normalize(asc_deg + 180)

    # 5. Sripathi House Calculation (Trisection Logic)
    # We manually trisect the quadrants to find the Bhava Midpoints.
    midpoints = {}
    
    # Q1: MC(10) to Asc(1)
    d1 = get_distance(mc_deg, asc_deg)
    midpoints[10] = mc_deg
    midpoints[11] = normalize(mc_deg + d1/3)
    midpoints[12] = normalize(mc_deg + (d1/3)*2)
    midpoints[1]  = asc_deg
    
    # Q2: Asc(1) to IC(4)
    d2 = get_distance(asc_deg, ic_deg)
    midpoints[2] = normalize(asc_deg + d2/3)
    midpoints[3] = normalize(asc_deg + (d2/3)*2)
    midpoints[4] = ic_deg
    
    # Q3: IC(4) to Desc(7)
    d3 = get_distance(ic_deg, desc_deg)
    midpoints[5] = normalize(ic_deg + d3/3)
    midpoints[6] = normalize(ic_deg + (d3/3)*2)
    midpoints[7] = desc_deg
    
    # Q4: Desc(7) to MC(10)
    d4 = get_distance(desc_deg, mc_deg)
    midpoints[8] = normalize(desc_deg + d4/3)
    midpoints[9] = normalize(desc_deg + (d4/3)*2)

    # Calculate House Boundaries (Sandhis)
    # House Start = Average of (Prev Midpoint) and (Curr Midpoint)
    house_starts = {}
    for i in range(1, 13):
        prev = 12 if i == 1 else i - 1
        mp_curr = midpoints[i]
        mp_prev = midpoints[prev]
        
        dist = get_distance(mp_prev, mp_curr)
        sandhi = normalize(mp_prev + dist/2.0)
        house_starts[i] = sandhi

    # 6. Calculate Planets
    p_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN, 
        "Rahu": swe.MEAN_NODE
    }
    
    planets_output = {}

    for p_name, p_id in p_map.items():
        # Calculate Sidereal Position
        # FLG_SPEED is crucial for Retrograde accuracy
        out = swe.calc_ut(jd_ut, p_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        p_lon = out[0][0]
        p_speed = out[0][3]
        
        # Retrograde Logic
        retro_str = "R" if p_speed < 0 else ""
        
        # Determine Sripathi House
        p_house = -1
        for h_num in range(1, 13):
            start = house_starts[h_num]
            next_h = 1 if h_num == 12 else h_num + 1
            end = house_starts[next_h]
            
            # Check if planet is within the House Start -> House End range
            if start < end:
                if start <= p_lon < end: p_house = h_num; break
            else: # Wraps over 360
                if p_lon >= start or p_lon < end: p_house = h_num; break
        
        # Determine the "Visual Sign" on the Chart (The Sign of the House)
        # This helps match the output to the visual diagram
        # Logic: If Asc is Pisces (12), House 1=Pisces, House 2=Aries...
        # This is a simplistic mapping for the North Indian chart layout
        asc_sign_idx = int(asc_deg / 30) # 0=Aries... 11=Pisces
        house_offset = p_house - 1
        visual_sign_idx = (asc_sign_idx + house_offset) % 12
        visual_sign_name = ZODIAC_SIGNS[visual_sign_idx]

        nak_data = get_nakshatra_details(p_lon)
        
        planets_output[p_name] = {
            "degrees": format_dms_string(p_lon),
            "house": p_house,
            "sign": get_sign_name(p_lon),   # The ACTUAL Astronomical Sign
            "bhava_sign": visual_sign_name, # The Visual Sign in the House Chart
            "nakshatra": nak_data["name"],
            "pada": nak_data["pada"],
            "retrograde": retro_str
        }
        
        # Add Ketu
        if p_name == "Rahu":
            k_lon = normalize(p_lon + 180)
            
            # Ketu House
            k_house = -1
            for h_num in range(1, 13):
                start = house_starts[h_num]
                next_h = 1 if h_num == 12 else h_num + 1
                end = house_starts[next_h]
                if start < end:
                    if start <= k_lon < end: k_house = h_num; break
                else:
                    if k_lon >= start or k_lon < end: k_house = h_num; break
            
            # Ketu Visual Sign
            k_house_offset = k_house - 1
            k_visual_idx = (asc_sign_idx + k_house_offset) % 12
            k_visual_name = ZODIAC_SIGNS[k_visual_idx]
            
            k_nak = get_nakshatra_details(k_lon)
            
            planets_output["Ketu"] = {
                "degrees": format_dms_string(k_lon),
                "house": k_house,
                "sign": get_sign_name(k_lon),
                "bhava_sign": k_visual_name,
                "nakshatra": k_nak["name"],
                "pada": k_nak["pada"],
                "retrograde": "R"
            }

    # 7. Construct Response
    asc_nak = get_nakshatra_details(asc_deg)
    
    response = {
        "ascendant": {
            "degrees": format_dms_string(asc_deg),
            "sign": get_sign_name(asc_deg),
            "nakshatra": asc_nak["name"],
            "pada": asc_nak["pada"]
        },
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": str(round(ayanamsa_val, 6)),
            "chart_type": "Bhava Chalit",
            "system": "Sripathi",
            "explanation": "Visual Sign = The sign overlapping the House slot in the diagram."
        },
        "planetary_positions": dict(sorted(planets_output.items())),
        "user_name": name
    }
    
    return response