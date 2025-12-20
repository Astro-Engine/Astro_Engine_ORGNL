"""
D40 Khavedamsa - Calculation Module
====================================
Vedic Astrology Divisional Chart Calculator - The Chart of Auspicious/Inauspicious Effects

Features:
- Precise D40 calculations using Classical Parashara method
- Original Document implementation (Aquarius as ODD sign)
- Lahiri Ayanamsa
- Whole Sign house system
- 12 Deities cycle assignment
- Maternal lineage karma analysis
"""

from datetime import datetime, timedelta
import swisseph as swe

# ==============================================================================
# CONSTANTS
# ==============================================================================

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# 12 Deities for D40
DEITIES = [
    "Vishnu", "Chandra", "Marichi", "Twashta", "Dhata", "Shiva",
    "Ravi", "Yama", "Yaksha", "Gandharva", "Kala", "Varuna"
]

DEITY_DESCRIPTIONS = {
    "Vishnu": "The Preserver. Gives stability, protection, and sustainment.",
    "Chandra": "The Moon. Gives nourishment, emotional depth, and maternal blessings.",
    "Marichi": "A Sage (Son of Brahma). Gives light, wisdom, and creative power.",
    "Twashta": "The Celestial Architect. Gives skill, craftsmanship, and ability to build.",
    "Dhata": "The Creator. Gives the ability to create progeny, ideas, or wealth.",
    "Shiva": "The Destroyer. Gives transformation, detachment, and removal of ignorance.",
    "Ravi": "The Sun. Gives brilliance, authority, and vitality.",
    "Yama": "The God of Death/Dharma. Gives discipline, judgment, and sometimes separation.",
    "Yaksha": "Nature Spirit. Gives wealth protection and earthly desires.",
    "Gandharva": "Celestial Musician. Gives artistic talent, charm, and love for luxury.",
    "Kala": "Time/Death. Indicates karmic timing, delays, or destiny that cannot be changed.",
    "Varuna": "God of Oceans. Gives emotional wisdom, adaptability, and vastness."
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def decimal_to_dms(decimal_deg):
    """Convert decimal degrees to degrees, minutes, seconds"""
    degrees = int(decimal_deg)
    minutes_decimal = (decimal_deg - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    return degrees, minutes, seconds


def format_degrees(decimal_deg):
    """Format decimal degrees as string"""
    deg, min, sec = decimal_to_dms(decimal_deg)
    return f"{deg}° {min}' {sec:.2f}\""


def get_julian_day(date_str, time_str, timezone_offset):
    """
    Calculate Julian Day from local time
    
    EXACT LOGIC:
    1. Parse: "1997-07-22" + "22:00:00" → datetime object
    2. Convert timezone: 5.5 hours = 5h 30m → timedelta(hours=5, minutes=30)
    3. Get UTC: local_time - timezone_offset
    4. Calculate JD: Use Swiss Ephemeris julday() function
    
    Example:
    Local: 1997-07-22 22:00:00 IST (+5.5)
    UTC: 1997-07-22 16:30:00
    JD: 2450650.1875
    """
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    
    hours = int(timezone_offset)
    minutes = int((timezone_offset - hours) * 60)
    tz_delta = timedelta(hours=hours, minutes=minutes)
    
    utc_dt = local_dt - tz_delta
    hour_decimal = utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    
    return jd


def get_sidereal_position(jd, planet):
    """Get sidereal planetary position using Lahiri ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.calc_ut(jd, planet, swe.FLG_SIDEREAL)
    return result[0]


def get_ascendant(jd, latitude, longitude):
    """Calculate Ascendant using whole sign house system"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_SIDEREAL)
    return ascmc[0]


def get_sign_and_degree(longitude):
    """
    Convert longitude to sign and degree
    
    EXACT LOGIC:
    - Longitude range: 0° to 360°
    - Each sign: 30°
    - Sign number = floor(longitude / 30) + 1
    - Degree in sign = longitude mod 30
    
    Example:
    185.5° → sign = floor(185.5/30)+1 = 6+1 = 7 (Libra)
           → degree = 185.5 mod 30 = 5.5°
    """
    longitude = longitude % 360
    sign_number = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    return sign_number, degree_in_sign


def get_nakshatra_and_pada(longitude):
    """
    Calculate nakshatra and pada
    
    EXACT LOGIC:
    - 360° ÷ 27 nakshatras = 13.333333° per nakshatra
    - Each nakshatra ÷ 4 padas = 3.333333° per pada
    - Nakshatra number = floor(longitude / 13.333333)
    - Pada = floor((longitude mod 13.333333) / 3.333333) + 1
    """
    longitude = longitude % 360
    nakshatra_length = 360.0 / 27.0
    pada_length = nakshatra_length / 4.0
    
    nakshatra_num = int(longitude / nakshatra_length)
    nakshatra_name = NAKSHATRAS[nakshatra_num]
    
    position_in_nakshatra = longitude % nakshatra_length
    pada = int(position_in_nakshatra / pada_length) + 1
    
    return nakshatra_name, pada


def calculate_house_from_ascendant(planet_sign, asc_sign):
    """Calculate house number from ascendant (whole sign system)"""
    house = ((planet_sign - asc_sign) % 12) + 1
    return house


# ==============================================================================
# CORE D40 CALCULATION
# ==============================================================================

def calculate_d40_classical(longitude_in_sign, sign_number):
    """
    Calculate D40 (Khavedamsa) - EXACT IMPLEMENTATION FROM DOCUMENT
    
    ============================================================================
    COMPLETE MATHEMATICAL LOGIC - FOLLOWING ORIGINAL DOCUMENT EXACTLY
    ============================================================================
    
    SOURCE: User-provided document on D40 calculation
    
    STEP 1: DIVISION CALCULATION
    ============================================================================
    
    Formula from document:
    "Span of one D40 part = 30° / 40 = 0°45' (45 minutes of arc)"
    
    This means:
    - Each sign (30°) is divided into 40 equal parts
    - Each part = 0.75° = 0°45' (45 arc minutes)
    
    To find which division a planet falls in:
    division_number = floor(longitude_in_sign / 0.75) + 1
    
    Division boundaries:
    Division 1:  0°00'00" to 0°45'00" (0.000 to 0.750)
    Division 2:  0°45'00" to 1°30'00" (0.750 to 1.500)
    Division 3:  1°30'00" to 2°15'00" (1.500 to 2.250)
    ...
    Division 38: 27°45'00" to 28°30'00" (27.750 to 28.500)
    Division 39: 28°30'00" to 29°15'00" (28.500 to 29.250)
    Division 40: 29°15'00" to 30°00'00" (29.250 to 30.000)
    
    Example: Planet at 1°00' (1.0°)
    - 1.0 / 0.75 = 1.333
    - floor(1.333) = 1
    - 1 + 1 = 2
    - Result: Division 2 ✓
    
    Example: Planet at 28°29'57" (28.499355°)
    - 28.499355 / 0.75 = 37.999
    - floor(37.999) = 37
    - 37 + 1 = 38
    - Result: Division 38 ✓
    
    STEP 2: POLARITY RULE (EXACT FROM DOCUMENT)
    ============================================================================
    
    From document table:
    
    Sign Polarity | Starting Point | Logic
    --------------|----------------|-------
    Odd Signs     | Aries          | The 1st part falls in Aries, 2nd in Taurus, etc.
    Even Signs    | Libra          | The 1st part falls in Libra, 2nd in Scorpio, etc.
    
    Odd Signs (Ar, Ge, Le, Li, Sa, Aq):
    - Aries (1), Gemini (3), Leo (5), Libra (7), Sagittarius (9), Aquarius (11)
    
    Even Signs (Ta, Ca, Vi, Sc, Ca, Pi):
    - Taurus (2), Cancer (4), Virgo (6), Scorpio (8), Capricorn (10), Pisces (12)
    
    CRITICAL: The document explicitly lists Aquarius (Aq) as an ODD sign!
    
    STEP 3: D40 SIGN CALCULATION
    ============================================================================
    
    For ODD signs (starting from Aries = sign 1):
    - Division 1 → Aries (1)
    - Division 2 → Taurus (2)
    - Division 3 → Gemini (3)
    - ...
    - Division 12 → Pisces (12)
    - Division 13 → Aries (1) [cycle repeats]
    - Division 14 → Taurus (2)
    - ...
    
    Formula: d40_sign = ((division - 1) mod 12) + 1
    
    For EVEN signs (starting from Libra = sign 7):
    - Division 1 → Libra (7)
    - Division 2 → Scorpio (8)
    - Division 3 → Sagittarius (9)
    - ...
    - Division 6 → Pisces (12)
    - Division 7 → Aries (1)
    - Division 8 → Taurus (2)
    - ...
    
    Formula: d40_sign = (((division - 1) + 6) mod 12) + 1
    
    Why +6? Because Libra is the 7th sign:
    - To start from Libra instead of Aries, we shift by 6 positions
    - Aries (1) + 6 = Libra (7)
    
    STEP 4: WORKED EXAMPLES
    ============================================================================
    
    Example A: Sun at 1°00' in Aries (Odd sign, #1)
    - Division: floor(1.0/0.75) + 1 = 1 + 1 = 2
    - Aries is ODD → start from Aries
    - D40 sign: ((2-1) mod 12) + 1 = (1 mod 12) + 1 = 1 + 1 = 2
    - Result: Taurus (2) ✓ [Matches document example!]
    
    Example B: Ketu at 28°29'57" in Aquarius (Odd sign, #11)
    - Division: floor(28.499/0.75) + 1 = 37 + 1 = 38
    - Aquarius is ODD → start from Aries
    - D40 sign: ((38-1) mod 12) + 1 = (37 mod 12) + 1 = 1 + 1 = 2
    - Result: Taurus (2)
    
    Example C: Moon at 11°25'52" in Aquarius (Odd sign, #11)
    - Degree: 11.431212°
    - Division: floor(11.431/0.75) + 1 = 15 + 1 = 16
    - Aquarius is ODD → start from Aries
    - D40 sign: ((16-1) mod 12) + 1 = (15 mod 12) + 1 = 3 + 1 = 4
    - Result: Cancer (4)
    
    Example D: Planet in Cancer (Even sign, #4) at division 16
    - Cancer is EVEN → start from Libra
    - D40 sign: (((16-1) + 6) mod 12) + 1 = (21 mod 12) + 1 = 9 + 1 = 10
    - Result: Capricorn (10)
    
    STEP 5: DEITY ASSIGNMENT
    ============================================================================
    
    From document: "The 40 divisions are ruled by 12 Deities who repeat in a cycle"
    
    Cycle pattern:
    - Divisions 1-12: Vishnu, Chandra, Marichi, Twashta, Dhata, Shiva, 
                      Ravi, Yama, Yaksha, Gandharva, Kala, Varuna
    - Divisions 13-24: [Same 12 deities repeat]
    - Divisions 25-36: [Same 12 deities repeat]
    - Divisions 37-40: Vishnu, Chandra, Marichi, Twashta
    
    Formula: deity_number = ((division - 1) mod 12) + 1
    
    Example: Division 38
    - (38 - 1) mod 12 + 1 = 37 mod 12 + 1 = 1 + 1 = 2
    - Deity #2 = Chandra ✓
    
    STEP 6: DEGREE WITHIN D40 SIGN
    ============================================================================
    
    Each 0.75° division in D1 maps to a full 30° sign in D40.
    
    Formula:
    1. Find division start: division_start = (division - 1) × 0.75
    2. Find offset into division: offset = longitude_in_sign - division_start
    3. Scale to D40 sign: degree_in_d40 = (offset / 0.75) × 30
    
    Example: 28°30' in division 38
    - Division starts: (38-1) × 0.75 = 27.75°
    - Offset: 28.5 - 27.75 = 0.75°
    - D40 degree: (0.75 / 0.75) × 30 = 30.0°
    
    ============================================================================
    """
    
    # STEP 1: Calculate division number (1-40)
    division_size = 0.75
    division_number = int(longitude_in_sign / division_size) + 1
    
    if division_number > 40:
        division_number = 40
    
    # STEP 2: Determine polarity (EXACT from document)
    # Odd Signs: Aries (1), Gemini (3), Leo (5), Libra (7), Sagittarius (9), Aquarius (11)
    # Even Signs: Taurus (2), Cancer (4), Virgo (6), Scorpio (8), Capricorn (10), Pisces (12)
    odd_signs = [1, 3, 5, 7, 9, 11]  # As per document - includes Aquarius!
    
    # STEP 3: Apply polarity rule
    if sign_number in odd_signs:
        # ODD SIGNS: Start from Aries (sign 1)
        d40_sign_number = ((division_number - 1) % 12) + 1
    else:
        # EVEN SIGNS: Start from Libra (sign 7)
        d40_sign_number = (((division_number - 1) + 6) % 12) + 1
    
    # STEP 4: Calculate deity
    deity_number = ((division_number - 1) % 12) + 1
    deity_name = DEITIES[deity_number - 1]
    
    # STEP 5: Calculate exact degree within D40 sign
    division_start = (division_number - 1) * division_size
    offset_in_division = longitude_in_sign - division_start
    degree_in_d40 = (offset_in_division / division_size) * 30.0
    
    if degree_in_d40 >= 30.0:
        degree_in_d40 = 29.999999
    
    return {
        'sign_number': d40_sign_number,
        'sign_name': ZODIAC_SIGNS[d40_sign_number - 1],
        'degree': degree_in_d40,
        'division': division_number,
        'deity': deity_name,
        'deity_description': DEITY_DESCRIPTIONS[deity_name]
    }


# ==============================================================================
# PLANETARY CALCULATIONS
# ==============================================================================

def calculate_d1_positions(jd, asc_sign_num):
    """Calculate D1 (Rasi) planetary positions"""
    planets_to_calculate = [
        (swe.SUN, "Sun"),
        (swe.MOON, "Moon"),
        (swe.MERCURY, "Mercury"),
        (swe.VENUS, "Venus"),
        (swe.MARS, "Mars"),
        (swe.JUPITER, "Jupiter"),
        (swe.SATURN, "Saturn"),
        (swe.MEAN_NODE, "Rahu")
    ]
    
    d1_planets = {}
    
    for planet_id, planet_name in planets_to_calculate:
        position_data = get_sidereal_position(jd, planet_id)
        planet_longitude = position_data[0]
        planet_speed = position_data[3]
        is_retrograde = "R" if planet_speed < 0 else ""
        
        # D1
        sign_num, degree = get_sign_and_degree(planet_longitude)
        nakshatra, pada = get_nakshatra_and_pada(planet_longitude)
        house = calculate_house_from_ascendant(sign_num, asc_sign_num)
        
        d1_planets[planet_name] = {
            "sign": ZODIAC_SIGNS[sign_num - 1],
            "degrees": format_degrees(degree),
            "nakshatra": nakshatra,
            "pada": pada,
            "house": house,
            "retrograde": is_retrograde,
            "sign_number": sign_num,
            "degree_in_sign": degree
        }
    
    # Ketu
    rahu_position_data = get_sidereal_position(jd, swe.MEAN_NODE)
    rahu_longitude = rahu_position_data[0]
    ketu_longitude = (rahu_longitude + 180) % 360
    
    ketu_sign_num, ketu_degree = get_sign_and_degree(ketu_longitude)
    ketu_nakshatra, ketu_pada = get_nakshatra_and_pada(ketu_longitude)
    ketu_house = calculate_house_from_ascendant(ketu_sign_num, asc_sign_num)
    
    d1_planets["Ketu"] = {
        "sign": ZODIAC_SIGNS[ketu_sign_num - 1],
        "degrees": format_degrees(ketu_degree),
        "nakshatra": ketu_nakshatra,
        "pada": ketu_pada,
        "house": ketu_house,
        "retrograde": "",
        "sign_number": ketu_sign_num,
        "degree_in_sign": ketu_degree
    }
    
    return d1_planets


def calculate_d40_positions(d1_planets, asc_d40_sign_num):
    """Calculate D40 (Khavedamsa) planetary positions from D1 positions"""
    d40_planets = {}
    
    for planet_name, planet_data in d1_planets.items():
        degree = planet_data['degree_in_sign']
        sign_num = planet_data['sign_number']
        
        # D40
        d40_data = calculate_d40_classical(degree, sign_num)
        d40_longitude = (d40_data['sign_number'] - 1) * 30 + d40_data['degree']
        d40_nakshatra, d40_pada = get_nakshatra_and_pada(d40_longitude)
        d40_house = calculate_house_from_ascendant(d40_data['sign_number'], asc_d40_sign_num)
        
        d40_planets[planet_name] = {
            "sign": d40_data['sign_name'],
            "degrees": format_degrees(d40_data['degree']),
            "nakshatra": d40_nakshatra,
            "pada": d40_pada,
            "house": d40_house,
            "retrograde": planet_data['retrograde'],
            "division": d40_data['division'],
            "deity": d40_data['deity'],
            "deity_description": d40_data['deity_description']
        }
    
    return d40_planets


# ==============================================================================
# MAIN CALCULATION ORCHESTRATION
# ==============================================================================

def calculate_d40_chart(data):
    """
    Main function to calculate D40 Khavedamsa chart
    
    Parameters:
    -----------
    data : dict
        Dictionary containing:
        - user_name: str (optional)
        - birth_date: str (YYYY-MM-DD)
        - birth_time: str (HH:MM:SS)
        - latitude: float
        - longitude: float
        - timezone_offset: float
    
    Returns:
    --------
    dict: Complete D40 Khavedamsa chart (D1 removed from response)
    """
    user_name = data.get('user_name', '')
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    latitude = float(data.get('latitude'))
    longitude = float(data.get('longitude'))
    timezone_offset = float(data.get('timezone_offset'))
    
    if not all([birth_date, birth_time]):
        raise ValueError('Missing required fields: birth_date and birth_time')
    
    jd = get_julian_day(birth_date, birth_time, timezone_offset)
    ayanamsa_value = swe.get_ayanamsa_ut(jd)
    
    # Ascendant
    asc_longitude = get_ascendant(jd, latitude, longitude)
    asc_sign_num, asc_degree = get_sign_and_degree(asc_longitude)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(asc_longitude)
    
    # D40 Ascendant
    asc_d40 = calculate_d40_classical(asc_degree, asc_sign_num)
    asc_d40_longitude = (asc_d40['sign_number'] - 1) * 30 + asc_d40['degree']
    asc_d40_nakshatra, asc_d40_pada = get_nakshatra_and_pada(asc_d40_longitude)
    
    # Calculate D1 positions (needed for D40 calculation)
    d1_planets = calculate_d1_positions(jd, asc_sign_num)
    
    # Calculate D40 positions from D1
    d40_planets = calculate_d40_positions(d1_planets, asc_d40['sign_number'])
    
    # Prepare response (D1 removed as requested)
    response = {
        "user_name": user_name,
        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset
        },
        "d40_chart": {
            "ascendant": {
                "sign": asc_d40['sign_name'],
                "degrees": format_degrees(asc_d40['degree']),
                "nakshatra": asc_d40_nakshatra,
                "pada": asc_d40_pada,
                "division": asc_d40['division'],
                "deity": asc_d40['deity'],
                "deity_description": asc_d40['deity_description']
            },
            "planetary_positions": d40_planets,
            "notes": {
                "chart_type": "Khavedamsa (D40)",
                "purpose": "Auspicious/Inauspicious effects, Maternal lineage karma",
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "house_system": "Whole Sign",
                "calculation_method": "Classical Parashara - Original Document"
            }
        }
    }
    
    return response