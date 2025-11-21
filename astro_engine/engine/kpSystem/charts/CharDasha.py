"""
CHARA DASHA CALCULATIONS - JAIMINI ASTROLOGY SYSTEM
====================================================
Pure calculation functions - NO Flask imports
All calculations use KP New (Krishnamurti) Ayanamsa, Placidus Houses, Sidereal
Features:
- Complete Mahadasha calculations with correct dates (simple year addition)
- Complete Antardasha calculations with CORRECT FIXED directions per sign
- VALIDATED: Matches AstroSage across multiple charts
"""

from datetime import datetime, timedelta
import swisseph as swe
import os
import math

# Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# KP New Ayanamsa (Krishnamurti)
KP_AYANAMSA = swe.SIDM_KRISHNAMURTI

# Constants
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANET_NAMES = {
    swe.SUN: "Sun",
    swe.MOON: "Moon",
    swe.MARS: "Mars",
    swe.MERCURY: "Mercury",
    swe.JUPITER: "Jupiter",
    swe.VENUS: "Venus",
    swe.SATURN: "Saturn",
    swe.MEAN_NODE: "Rahu",
}

# Sign lordship mapping
SIGN_LORDS = {
    0: "Mars",      # Aries
    1: "Venus",     # Taurus
    2: "Mercury",   # Gemini
    3: "Moon",      # Cancer
    4: "Sun",       # Leo
    5: "Mercury",   # Virgo
    6: "Venus",     # Libra
    7: "Mars",      # Scorpio (also Ketu)
    8: "Jupiter",   # Sagittarius
    9: "Saturn",    # Capricorn
    10: "Saturn",   # Aquarius (also Rahu)
    11: "Jupiter"   # Pisces
}

# JAIMINI CLASSIFICATION
SAVYA_SIGNS = [0, 1, 2, 6, 7, 8]  # Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius
APASAVYA_SIGNS = [3, 4, 5, 9, 10, 11]  # Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces

# Movable, Fixed, Dual classification
MOVABLE_SIGNS = [0, 3, 6, 9]
FIXED_SIGNS = [1, 4, 7, 10]
DUAL_SIGNS = [2, 5, 8, 11]

# ANTARDASHA DIRECTION - FIXED FOR EACH SIGN (VALIDATED ACROSS MULTIPLE CHARTS)
# This is a universal rule in Jaimini Chara Dasha
# True = Forward direction, False = Backward direction
ANTARDASHA_DIRECTION = {
    0: True,   # Aries - FORWARD (starts with Taurus)
    1: False,  # Taurus - BACKWARD (starts with Aries)
    2: False,  # Gemini - BACKWARD (starts with Taurus)
    3: False,  # Cancer - BACKWARD (starts with Gemini)
    4: True,   # Leo - FORWARD (starts with Virgo)
    5: True,   # Virgo - FORWARD (starts with Libra)
    6: True,   # Libra - FORWARD (starts with Scorpio)
    7: False,  # Scorpio - BACKWARD (starts with Libra)
    8: False,  # Sagittarius - BACKWARD (starts with Scorpio)
    9: False,  # Capricorn - BACKWARD (starts with Sagittarius)
    10: True,  # Aquarius - FORWARD (starts with Pisces)
    11: True,  # Pisces - FORWARD (starts with Aries)
}


def calculate_julian_day(date_str, time_str, timezone_offset):
    """Calculate Julian Day for given date, time and timezone"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        
        dt = datetime.combine(date_obj.date(), time_obj.time())
        dt_utc = dt - timedelta(hours=timezone_offset)
        
        jd = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        )
        return jd
    except Exception as e:
        raise ValueError(f"Date/Time calculation error: {str(e)}")


def get_ayanamsa(jd):
    """Get KP Ayanamsa value"""
    swe.set_sid_mode(KP_AYANAMSA)
    return swe.get_ayanamsa(jd)


def calculate_ascendant(jd, latitude, longitude):
    """Calculate Ascendant (Lagna) using Placidus house system"""
    try:
        houses, ascmc = swe.houses(jd, latitude, longitude, b'P')
        asc_tropical = ascmc[0]
        
        ayanamsa = get_ayanamsa(jd)
        asc_sidereal = (asc_tropical - ayanamsa) % 360
        
        sign = int(asc_sidereal / 30)
        degree_in_sign = asc_sidereal % 30
        
        return {
            "longitude": asc_sidereal,
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "degree": degree_in_sign
        }
    except Exception as e:
        raise ValueError(f"Ascendant calculation error: {str(e)}")


def calculate_planets(jd):
    """Calculate planetary positions with retrograde and nakshatra"""
    ayanamsa = get_ayanamsa(jd)
    planets = {}
    
    planet_ids = [
        swe.SUN, swe.MOON, swe.MARS, swe.MERCURY,
        swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE
    ]
    
    for planet_id in planet_ids:
        try:
            result, ret_flag = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
            
            tropical_long = result[0]
            speed = result[3]
            
            sidereal_long = (tropical_long - ayanamsa) % 360
            
            sign = int(sidereal_long / 30)
            degree_in_sign = sidereal_long % 30
            
            is_retrograde = False
            if planet_id != swe.MEAN_NODE:
                is_retrograde = speed < 0
            
            nakshatra_num = int(sidereal_long / (360/27))
            nakshatra_pada = int((sidereal_long % (360/27)) / ((360/27)/4)) + 1
            
            planet_name = PLANET_NAMES.get(planet_id, f"Planet_{planet_id}")
            
            planets[planet_name] = {
                "longitude": round(sidereal_long, 6),
                "sign": sign,
                "sign_name": SIGN_NAMES[sign],
                "degree": round(degree_in_sign, 6),
                "nakshatra": NAKSHATRA_NAMES[nakshatra_num],
                "nakshatra_pada": nakshatra_pada,
                "retrograde": is_retrograde,
                "speed": round(speed, 6)
            }
            
            if planet_id == swe.MEAN_NODE:
                ketu_long = (sidereal_long + 180) % 360
                ketu_sign = int(ketu_long / 30)
                ketu_degree = ketu_long % 30
                ketu_nakshatra_num = int(ketu_long / (360/27))
                ketu_nakshatra_pada = int((ketu_long % (360/27)) / ((360/27)/4)) + 1
                
                planets["Ketu"] = {
                    "longitude": round(ketu_long, 6),
                    "sign": ketu_sign,
                    "sign_name": SIGN_NAMES[ketu_sign],
                    "degree": round(ketu_degree, 6),
                    "nakshatra": NAKSHATRA_NAMES[ketu_nakshatra_num],
                    "nakshatra_pada": ketu_nakshatra_pada,
                    "retrograde": True,
                    "speed": round(-speed, 6)
                }
                
        except Exception as e:
            print(f"Error calculating planet {planet_id}: {str(e)}")
            continue
    
    return planets


def get_ninth_house_sign(lagna_sign):
    """Get 9th house sign from Lagna"""
    return (lagna_sign + 8) % 12


def is_savya_sign(sign):
    """Check if sign is Savya (odd quarter - forward direction)"""
    return sign in SAVYA_SIGNS


def determine_dasha_direction(lagna_sign):
    """Determine Chara Dasha direction based on 9th house from Lagna"""
    ninth_house = get_ninth_house_sign(lagna_sign)
    is_forward = is_savya_sign(ninth_house)
    
    return {
        "ninth_house": ninth_house,
        "ninth_house_name": SIGN_NAMES[ninth_house],
        "is_savya": is_forward,
        "direction": "Forward" if is_forward else "Backward"
    }


def select_lord_for_dual_rulership(sign, planets):
    """Select lord for Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu)"""
    if sign == 7:  # Scorpio
        lord1_name, lord2_name = "Mars", "Ketu"
    elif sign == 10:  # Aquarius
        lord1_name, lord2_name = "Saturn", "Rahu"
    else:
        return SIGN_LORDS[sign]
    
    lord1_pos = planets[lord1_name]["sign"]
    lord2_pos = planets[lord2_name]["sign"]
    
    if lord1_pos == lord2_pos:
        return lord1_name
    
    if lord1_pos == sign and lord2_pos != sign:
        return lord2_name
    if lord2_pos == sign and lord1_pos != sign:
        return lord1_name
    
    def count_companions(lord_name):
        lord_sign = planets[lord_name]["sign"]
        count = 0
        for p_name, p_data in planets.items():
            if p_data["sign"] == lord_sign and p_name != lord_name:
                count += 1
        return count
    
    companions1 = count_companions(lord1_name)
    companions2 = count_companions(lord2_name)
    
    if companions1 > companions2:
        return lord1_name
    if companions2 > companions1:
        return lord2_name
    
    if lord1_pos in DUAL_SIGNS and lord2_pos not in DUAL_SIGNS:
        return lord1_name
    if lord2_pos in DUAL_SIGNS and lord1_pos not in DUAL_SIGNS:
        return lord2_name
    
    if planets[lord1_name]["degree"] > planets[lord2_name]["degree"]:
        return lord1_name
    else:
        return lord2_name


def calculate_sign_dasha_duration(sign, planets, is_forward):
    """Calculate Chara Dasha duration for a sign"""
    if sign == 7 or sign == 10:
        lord_name = select_lord_for_dual_rulership(sign, planets)
    else:
        lord_name = SIGN_LORDS[sign]
    
    lord_position = planets[lord_name]["sign"]
    
    if lord_position == sign:
        return {
            "duration_years": 12,
            "lord": lord_name,
            "lord_position": lord_position,
            "count": 12,
            "rule": "Lord in own sign"
        }
    
    sign_is_savya = is_savya_sign(sign)
    
    if sign_is_savya:
        count = (lord_position - sign) % 12
        if count == 0:
            count = 12
    else:
        count = (sign - lord_position) % 12
        if count == 0:
            count = 12
    
    duration = count
    
    return {
        "duration_years": duration,
        "lord": lord_name,
        "lord_position": lord_position,
        "count": count,
        "rule": f"Count {'forward' if sign_is_savya else 'backward'}"
    }


def add_years_to_date(start_date, years):
    """
    Add years to a date, preserving the day and month
    
    This matches how traditional astrology software calculates periods.
    Uses simple year addition (NOT days calculation).
    """
    try:
        end_date = start_date.replace(year=start_date.year + years)
    except ValueError:
        # Handle Feb 29 on non-leap years
        if start_date.month == 2 and start_date.day == 29:
            end_date = start_date.replace(year=start_date.year + years, day=28)
        else:
            raise
    
    return end_date


def calculate_antardashas_with_dates(mahadasha_sign, mahadasha_start_date, mahadasha_years):
    """
    Calculate Antardasha (sub-periods) with complete dates
    
    CRITICAL: Uses FIXED direction for each sign based on the universal pattern
    validated across multiple charts. This direction is INDEPENDENT of:
    - Overall Mahadasha direction
    - SAVYA/APASAVYA classification
    - Position in sequence
    - Planetary positions
    
    Pattern: F, B, B, B, F, F, F, B, B, B, F, F
    (Aries=F, Taurus=B, Gemini=B, Cancer=B, Leo=F, Virgo=F, Libra=F,
     Scorpio=B, Sagittarius=B, Capricorn=B, Aquarius=F, Pisces=F)
    """
    antardashas = []
    
    # Calculate actual end date of Mahadasha using simple year addition
    mahadasha_end_date = add_years_to_date(mahadasha_start_date, mahadasha_years)
    
    # Calculate total days in this Mahadasha (actual days between dates)
    total_days = (mahadasha_end_date - mahadasha_start_date).days
    days_per_antardasha = total_days / 12
    months_per_antardasha = mahadasha_years * 12 / 12
    
    # CRITICAL FIX: Use FIXED direction from lookup table for this sign
    is_forward = ANTARDASHA_DIRECTION[mahadasha_sign]
    
    # Generate sequence starting from NEXT sign in the fixed direction
    signs_sequence = []
    for i in range(1, 13):
        if is_forward:
            sign = (mahadasha_sign + i) % 12
        else:
            sign = (mahadasha_sign - i) % 12
        signs_sequence.append(sign)
    
    # Remove mahadasha sign if it appears and add it at the end
    if mahadasha_sign in signs_sequence:
        signs_sequence.remove(mahadasha_sign)
    signs_sequence.append(mahadasha_sign)
    
    # Calculate dates for each Antardasha
    current_date = mahadasha_start_date
    
    for idx, sign in enumerate(signs_sequence):
        # For the last Antardasha, ensure it ends exactly on Mahadasha end date
        if idx == 11:
            end_date = mahadasha_end_date
        else:
            end_date = current_date + timedelta(days=days_per_antardasha)
        
        # Calculate actual duration
        actual_days = (end_date - current_date).days
        
        antardashas.append({
            "order": idx + 1,
            "sign": sign,
            "sign_name": SIGN_NAMES[sign],
            "duration_years": round(months_per_antardasha / 12, 4),
            "duration_months": round(months_per_antardasha, 2),
            "duration_days": round(actual_days, 2),
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        })
        
        current_date = end_date
    
    return antardashas


def calculate_chara_dasha_sequence(lagna_sign, planets, birth_date):
    """
    Calculate complete Chara Dasha sequence with all dates
    
    CORRECTED LOGIC:
    1. Determine OVERALL Mahadasha direction based on 9th house from Lagna
    2. Generate sequence of 12 Mahadasha signs in that direction
    3. For each Mahadasha sign:
       a. Calculate duration (years)
       b. Calculate end date using SIMPLE YEAR ADDITION
       c. Calculate all 12 Antardashas using FIXED direction for that sign
    4. Return complete structure with all dates
    """
    direction_info = determine_dasha_direction(lagna_sign)
    is_forward = direction_info["is_savya"]
    
    mahadashas = []
    current_date = birth_date
    
    # Generate sequence of 12 Mahadasha signs
    for i in range(12):
        if is_forward:
            current_sign = (lagna_sign + i) % 12
        else:
            current_sign = (lagna_sign - i) % 12
        
        # Calculate duration for this Mahadasha sign
        duration_info = calculate_sign_dasha_duration(current_sign, planets, is_forward)
        duration_years = duration_info["duration_years"]
        
        # Calculate end date using simple year addition
        end_date = add_years_to_date(current_date, duration_years)
        
        # Calculate all Antardashas using FIXED direction for this sign
        antardashas = calculate_antardashas_with_dates(
            current_sign,
            current_date,
            duration_years
        )
        
        mahadashas.append({
            "order": i + 1,
            "sign": current_sign,
            "sign_name": SIGN_NAMES[current_sign],
            "lord": duration_info["lord"],
            "lord_position_sign": SIGN_NAMES[duration_info["lord_position"]],
            "duration_years": duration_years,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "calculation_rule": duration_info["rule"],
            "antardashas": antardashas
        })
        
        current_date = end_date
    
    return {
        "direction": direction_info["direction"],
        "ninth_house": direction_info["ninth_house_name"],
        "is_savya": is_forward,
        "mahadashas": mahadashas,
        "total_cycle_years": sum(m["duration_years"] for m in mahadashas)
    }


def calculate_complete_chara_dasha(birth_date, birth_time, latitude, longitude, timezone_offset, user_name):
    """
    Main calculation function - calculates complete Chara Dasha system
    
    Args:
        birth_date: Birth date as string "YYYY-MM-DD"
        birth_time: Birth time as string "HH:MM:SS"
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone_offset: Timezone offset in hours (e.g., 5.5 for IST)
        user_name: Name of the user
    
    Returns:
        Dictionary with complete Chara Dasha calculations
    """
    jd = calculate_julian_day(birth_date, birth_time, timezone_offset)
    ascendant = calculate_ascendant(jd, latitude, longitude)
    lagna_sign = ascendant["sign"]
    planets = calculate_planets(jd)
    
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    chara_dasha = calculate_chara_dasha_sequence(lagna_sign, planets, birth_datetime)
    
    return {
        "user_name": user_name,
        "birth_details": {
            "date": birth_date,
            "time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "ayanamsa": {
            "name": "KP New (Krishnamurti)",
            "value": round(get_ayanamsa(jd), 6)
        },
        "ascendant": ascendant,
        "planets": planets,
        "chara_dasha": chara_dasha,
        "calculation_info": {
            "method": "Jaimini Chara Dasha (Production Version)",
            "direction_rule": "Based on 9th house from Lagna",
            "duration_formula": "Count from sign to lord (NO subtraction, except own sign = 12 years)",
            "antardasha_formula": "Mahadasha divided into 12 equal parts",
            "antardasha_direction": "Fixed per sign - validated pattern across multiple charts",
            "date_calculation": "Simple year addition for major periods (matches traditional software)",
            "note": "Dates aligned to birth date anniversary. Antardasha directions follow universal fixed pattern: F,B,B,B,F,F,F,B,B,B,F,F"
        }
    }