import os
import math
from datetime import datetime, timedelta, timezone
import swisseph as swe
from skyfield.api import load, wgs84
from skyfield import almanac

# ==============================================================================
# 1. CONFIGURATION & LOADING
# ==============================================================================
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api/ephe')
swe.set_ephe_path(EPHE_PATH)
AYANAMSA_MODE = 7  # Sri Yukteswar (SIDM_YUKTESHWAR)

# Load Skyfield Data once
# Ensure 'de421.bsp' is present in your working directory or path
eph = load('de421.bsp')
ts = load.timescale()

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def decimal_to_dms(deg):
    """Formats degrees to D° M' S.SS" string."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = float(((deg - d) * 60 - m) * 60)
    return f"{d}° {m}' {s:.2f}\""

def normalize_degree(deg):
    """Normalizes angle to 0-360 range."""
    deg = deg % 360
    if deg < 0: deg += 360
    return deg

def get_sign_info(longitude):
    """Returns Sign Name and Sign ID (1-12)."""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    norm_lon = normalize_degree(longitude)
    sign_index = int(norm_lon / 30)
    if sign_index >= 12: sign_index = 0
    return sign_index + 1, signs[sign_index]

def get_nakshatra_info(longitude):
    """Returns Nakshatra Name and Pada (1-4)."""
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    norm_lon = normalize_degree(longitude)
    nak_index = int(norm_lon * 27 / 360)
    if nak_index >= 27: nak_index = 0
    
    nak_start_deg = nak_index * (360/27)
    degree_into_nak = norm_lon - nak_start_deg
    pada = int(degree_into_nak / 3.333333333) + 1
    if pada > 4: pada = 4
    
    return nakshatras[nak_index], pada

def get_house_number(planet_sign_id, asc_sign_id):
    """Calculates Whole Sign House number (1-12) relative to Ascendant."""
    house = (planet_sign_id - asc_sign_id) + 1
    if house <= 0: house += 12
    return house

def get_yukteswar_ayanamsa(jd_ut):
    swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
    return swe.get_ayanamsa_ut(jd_ut)

def perform_hora_calculation(data):
    """
    Main Logic Function.
    Receives input dictionary, performs all calculations, returns result dictionary.
    """
    name = data.get("user_name")
    lat = float(data.get("latitude"))
    lon = float(data.get("longitude"))
    tz = float(data.get("timezone_offset"))
    
    # 1. TIME SETUP
    local_dt = datetime.strptime(f"{data.get('birth_date')} {data.get('birth_time')}", "%Y-%m-%d %H:%M:%S")
    utc_dt = (local_dt - timedelta(hours=tz)).replace(tzinfo=timezone.utc)
    t_birth = ts.from_datetime(utc_dt)
    jd_ut = float(t_birth.ut1)

    # 2. SUNRISE CALCULATION
    location = wgs84.latlon(lat, lon)
    # Note: eph is loaded at module level
    observer = eph['earth'] + location
    
    # Search for Sunrise on the local day
    local_midnight = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_start = (local_midnight - timedelta(hours=tz)).replace(tzinfo=timezone.utc)
    utc_end = utc_start + timedelta(hours=24)
    
    t0 = ts.from_datetime(utc_start)
    t1 = ts.from_datetime(utc_end)
    
    t_events, y_events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, location))
    
    sunrise_t = None
    for i, code in enumerate(y_events):
        if code == 1: # 1 = Sunrise
            sunrise_t = t_events[i]
            break
    
    # Robust check for None
    if sunrise_t is None: 
        raise ValueError("Sunrise not found for this date/location.")

    # 3. HORA LAGNA (HL) CALCULATION [UPDATED PARASHARA RULE]
    # A. Sun Position at Sunrise (Sidereal)
    sun_sr_trop = observer.at(sunrise_t).observe(eph['sun']).apparent().ecliptic_latlon()[1].degrees
    aya_sr = get_yukteswar_ayanamsa(float(sunrise_t.ut1))
    sun_sr_sid = normalize_degree(sun_sr_trop - aya_sr)
    
    # B. HL Formula: Sun(SR) + (HoursFromSunrise * 30 deg)
    # Rule: Parashara/Jaimini speed is 30 degrees (1 Sign) per 1 Hour.
    diff_days = t_birth.ut1 - sunrise_t.ut1
    diff_hours = diff_days * 24.0
    
    # Using 30.0 degrees per hour
    hl_degrees = normalize_degree(sun_sr_sid + (diff_hours * 30.0))
    
    # C. HL Details (This is the Ascendant)
    hl_sign_id, hl_sign_name = get_sign_info(hl_degrees)
    hl_nak, hl_pada = get_nakshatra_info(hl_degrees)
    hl_deg_in_sign = hl_degrees % 30

    # 4. PLANETARY CALCULATIONS (Relative to HL)
    swe_bodies = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, 
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE
    }

    planetary_positions = {}

    for p_name, pid in swe_bodies.items():
        # A. Calculate Position
        swe.set_sid_mode(AYANAMSA_MODE, 0, 0)
        res = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon_val = res[0][0]
        speed = res[0][3]

        # B. Retrograde Logic
        is_retro = False
        if pid == swe.MEAN_NODE:
            is_retro = True
        elif pid in [swe.SUN, swe.MOON]:
            is_retro = False
        else:
            if speed < 0: is_retro = True
        
        retro_str = "R" if is_retro else ""

        # C. Map Relative to HL
        sign_id, sign_name = get_sign_info(lon_val)
        house_num = get_house_number(sign_id, hl_sign_id)
        nak, pada = get_nakshatra_info(lon_val)
        deg_in_sign = lon_val % 30
        
        planetary_positions[p_name] = {
            "degrees": decimal_to_dms(deg_in_sign),
            "house": house_num,
            "nakshatra": nak,
            "pada": pada,
            "retrograde": retro_str,
            "sign": sign_name
        }

        # D. Handle Ketu
        if p_name == "Rahu":
            ketu_lon = normalize_degree(lon_val + 180)
            k_sign_id, k_sign_name = get_sign_info(ketu_lon)
            k_house = get_house_number(k_sign_id, hl_sign_id)
            k_nak, k_pada = get_nakshatra_info(ketu_lon)
            k_deg_in_sign = ketu_lon % 30
            
            planetary_positions["Ketu"] = {
                "degrees": decimal_to_dms(k_deg_in_sign),
                "house": k_house,
                "nakshatra": k_nak,
                "pada": k_pada,
                "retrograde": "R",
                "sign": k_sign_name
            }

    # 5. CONSTRUCT FINAL RESPONSE
    aya_current = get_yukteswar_ayanamsa(jd_ut)
    
    response = {
        "ascendant": {
            "degrees": decimal_to_dms(hl_deg_in_sign),
            "nakshatra": hl_nak,
            "pada": hl_pada,
            "sign": hl_sign_name
        },
        "birth_details": {
            "birth_date": data.get("birth_date"),
            "birth_time": data.get("birth_time"),
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz
        },
        "notes": {
            "ayanamsa": "Sri Yukteswar",
            "ayanamsa_value": f"{aya_current:.6f}",
            "chart_type": "HL_Rotated_Chart",
            "calculation_rule": "Parashara Hora Lagna (1 Sign per Hour)",
            "house_system": "Whole Sign (HL as Asc)"
        },
        "planetary_positions": planetary_positions,
        "user_name": name
    }
    
    return response