"""
Vedic Astrology Calculations Module
Complete calculation engine for birth chart analysis, dosha detection, and mantra recommendations
Version: 3.0 - CORRECTED & COMPLETE
"""

from datetime import datetime, timedelta
import swisseph as swe
import math

# ==================== CONSTANTS ====================

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE
}

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

WEEKDAY_LORDS = {0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 
                 4: 'Venus', 5: 'Saturn', 6: 'Sun'}

PLANET_DAYS = {
    'Sun': 'Sunday', 'Moon': 'Monday', 'Mars': 'Tuesday',
    'Mercury': 'Wednesday', 'Jupiter': 'Thursday',
    'Venus': 'Friday', 'Saturn': 'Saturday', 'Rahu': 'Saturday', 'Ketu': 'Tuesday'
}

BEEJ_MANTRAS = {
    'Sun': {
        'sanskrit': 'ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः',
        'transliteration': 'Om Hraam Hreem Hraum Sah Suryaya Namah',
        'meaning': 'Salutations to the Sun God'
    },
    'Moon': {
        'sanskrit': 'ॐ श्रां श्रीं श्रौं सः चन्द्राय नमः',
        'transliteration': 'Om Shraam Shreem Shraum Sah Chandraya Namah',
        'meaning': 'Salutations to the Moon God'
    },
    'Mars': {
        'sanskrit': 'ॐ क्रां क्रीं क्रौं सः भौमाय नमः',
        'transliteration': 'Om Kraam Kreem Kraum Sah Bhaumaya Namah',
        'meaning': 'Salutations to Mars'
    },
    'Mercury': {
        'sanskrit': 'ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः',
        'transliteration': 'Om Braam Breem Braum Sah Budhaya Namah',
        'meaning': 'Salutations to Mercury'
    },
    'Jupiter': {
        'sanskrit': 'ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः',
        'transliteration': 'Om Graam Greem Graum Sah Gurave Namah',
        'meaning': 'Salutations to Jupiter/Guru'
    },
    'Venus': {
        'sanskrit': 'ॐ द्रां द्रीं द्रौं सः शुक्राय नमः',
        'transliteration': 'Om Draam Dreem Draum Sah Shukraya Namah',
        'meaning': 'Salutations to Venus'
    },
    'Saturn': {
        'sanskrit': 'ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः',
        'transliteration': 'Om Praam Preem Praum Sah Shanaischaraya Namah',
        'meaning': 'Salutations to Saturn'
    },
    'Rahu': {
        'sanskrit': 'ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः',
        'transliteration': 'Om Bhraam Bhreem Bhraum Sah Rahave Namah',
        'meaning': 'Salutations to Rahu'
    },
    'Ketu': {
        'sanskrit': 'ॐ स्रां स्रीं स्रौं सः केतवे नमः',
        'transliteration': 'Om Sraam Sreem Sraum Sah Ketave Namah',
        'meaning': 'Salutations to Ketu'
    }
}

BASE_MANTRA_COUNTS = {
    'Sun': 7000, 'Moon': 11000, 'Mars': 10000,
    'Mercury': 9000, 'Jupiter': 19000, 'Venus': 16000,
    'Saturn': 23000, 'Rahu': 18000, 'Ketu': 17000
}

MINIMUM_SHADBALA = {
    'Sun': 390, 'Moon': 360, 'Mars': 300,
    'Mercury': 420, 'Jupiter': 390, 'Venus': 330, 'Saturn': 300
}

DEBILITATION_RULES = {
    'Sun': {'sign': 'Libra', 'degree': 10.0, 'sign_num': 6},
    'Moon': {'sign': 'Scorpio', 'degree': 3.0, 'sign_num': 7},
    'Mars': {'sign': 'Cancer', 'degree': 28.0, 'sign_num': 3},
    'Mercury': {'sign': 'Pisces', 'degree': 15.0, 'sign_num': 11},
    'Jupiter': {'sign': 'Capricorn', 'degree': 5.0, 'sign_num': 9},
    'Venus': {'sign': 'Virgo', 'degree': 27.0, 'sign_num': 5},
    'Saturn': {'sign': 'Aries', 'degree': 20.0, 'sign_num': 0}
}

EXALTATION_RULES = {
    'Sun': {'sign': 'Aries', 'degree': 10.0, 'sign_num': 0},
    'Moon': {'sign': 'Taurus', 'degree': 3.0, 'sign_num': 1},
    'Mars': {'sign': 'Capricorn', 'degree': 28.0, 'sign_num': 9},
    'Mercury': {'sign': 'Virgo', 'degree': 15.0, 'sign_num': 5},
    'Jupiter': {'sign': 'Cancer', 'degree': 5.0, 'sign_num': 3},
    'Venus': {'sign': 'Pisces', 'degree': 27.0, 'sign_num': 11},
    'Saturn': {'sign': 'Libra', 'degree': 20.0, 'sign_num': 6}
}

COMBUSTION_RULES = {
    'Moon': 12, 'Mars': 17, 'Mercury': 14,
    'Jupiter': 11, 'Venus': 10, 'Saturn': 15
}

DASHA_PERIODS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
    'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

HORA_SEQUENCE = ['Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter', 'Mars']

OWN_SIGNS = {
    'Sun': [4],  # Leo
    'Moon': [3],  # Cancer
    'Mars': [0, 7],  # Aries, Scorpio
    'Mercury': [2, 5],  # Gemini, Virgo
    'Jupiter': [8, 11],  # Sagittarius, Pisces
    'Venus': [1, 6],  # Taurus, Libra
    'Saturn': [9, 10]  # Capricorn, Aquarius
}

# Kaal Sarp Dosha Types
KAAL_SARP_TYPES = {
    (0, 6): 'Anant Kaal Sarp Dosha',
    (1, 7): 'Kulik Kaal Sarp Dosha',
    (2, 8): 'Vasuki Kaal Sarp Dosha',
    (3, 9): 'Shankhpal Kaal Sarp Dosha',
    (4, 10): 'Padam Kaal Sarp Dosha',
    (5, 11): 'Mahapadam Kaal Sarp Dosha',
    (6, 0): 'Takshak Kaal Sarp Dosha',
    (7, 1): 'Karkotak Kaal Sarp Dosha',
    (8, 2): 'Shankhachud Kaal Sarp Dosha',
    (9, 3): 'Ghatak Kaal Sarp Dosha',
    (10, 4): 'Vishdhar Kaal Sarp Dosha',
    (11, 5): 'Sheshnag Kaal Sarp Dosha'
}

# Planet aspects - CORRECTED DEFINITIONS
PLANET_ASPECTS = {
    'Sun': [7],           # 7th aspect only
    'Moon': [7],          # 7th aspect only
    'Mercury': [7],       # 7th aspect only
    'Venus': [7],         # 7th aspect only
    'Mars': [4, 7, 8],    # 4th, 7th, 8th aspects
    'Jupiter': [5, 7, 9], # 5th, 7th, 9th aspects
    'Saturn': [3, 7, 10], # 3rd, 7th, 10th aspects
    'Rahu': [5, 7, 9],    # Same as Jupiter (some traditions)
    'Ketu': [5, 7, 9]     # Same as Jupiter (some traditions)
}

# ==================== HELPER FUNCTIONS ====================

def get_julian_day(birth_date, birth_time, timezone_offset):
    """Convert datetime to Julian Day in UT"""
    try:
        dt_str = f"{birth_date} {birth_time}"
        dt_local = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_local - timedelta(hours=timezone_offset)
        
        year = dt_utc.year
        month = dt_utc.month
        day = dt_utc.day
        hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        
        jd = swe.julday(year, month, day, hour, swe.GREG_CAL)
        return jd
    except Exception as e:
        raise ValueError(f"Error calculating Julian Day: {str(e)}")

def get_current_julian_day():
    """Get current Julian Day in UT"""
    try:
        now_utc = datetime.utcnow()
        year = now_utc.year
        month = now_utc.month
        day = now_utc.day
        hour = now_utc.hour + now_utc.minute / 60.0 + now_utc.second / 3600.0
        
        jd = swe.julday(year, month, day, hour, swe.GREG_CAL)
        return jd
    except Exception as e:
        raise ValueError(f"Error getting current Julian Day: {str(e)}")

def get_ayanamsa(jd):
    """Get Lahiri Ayanamsa"""
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)
        return ayanamsa
    except Exception as e:
        raise ValueError(f"Error calculating Ayanamsa: {str(e)}")

def get_planet_position(jd, planet_id):
    """Get sidereal position of planet"""
    try:
        ayanamsa = get_ayanamsa(jd)
        result = swe.calc_ut(jd, planet_id)
        tropical_long = result[0][0]
        speed = result[0][3]
        sidereal_long = (tropical_long - ayanamsa) % 360
        return sidereal_long, speed
    except Exception as e:
        raise ValueError(f"Error calculating planet position: {str(e)}")

def get_ascendant(jd, lat, lon):
    """Calculate Ascendant"""
    try:
        ayanamsa = get_ayanamsa(jd)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        tropical_asc = ascmc[0]
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        return sidereal_asc
    except Exception as e:
        raise ValueError(f"Error calculating Ascendant: {str(e)}")

def get_sign_and_degree(longitude):
    """Convert longitude to sign and degree"""
    sign_num = int(longitude / 30)
    degree = longitude % 30
    return SIGNS[sign_num], degree, sign_num

def get_house_whole_sign(longitude, asc_sign_num):
    """Whole Sign House System"""
    planet_sign_num = int(longitude / 30)
    house = ((planet_sign_num - asc_sign_num) % 12) + 1
    return house

def normalize_angle(angle):
    """Normalize angle to 0-360"""
    return angle % 360

def calculate_angular_distance(long1, long2):
    """Calculate shortest angular distance between two longitudes"""
    distance = abs(long1 - long2)
    if distance > 180:
        distance = 360 - distance
    return distance

def get_sunrise_sunset(jd, lat, lon):
    """Calculate sunrise and sunset times"""
    try:
        geopos = [lon, lat, 0]
        
        result_rise = swe.rise_trans(jd - 1, swe.SUN, geopos, 
                                     rsmi=swe.CALC_RISE | swe.BIT_DISC_CENTER)
        if result_rise[0] >= 0:
            sunrise = result_rise[1][0]
        else:
            sunrise = jd
        
        result_set = swe.rise_trans(jd - 1, swe.SUN, geopos,
                                    rsmi=swe.CALC_SET | swe.BIT_DISC_CENTER)
        if result_set[0] >= 0:
            sunset = result_set[1][0]
        else:
            sunset = jd + 0.5
        
        return sunrise, sunset
    except Exception as e:
        return jd, jd + 0.5

# ==================== CORRECTED ASPECT CALCULATION ====================

def calculate_aspect_houses(from_house, aspect_numbers):
    """
    CORRECTED: Calculate which houses a planet aspects
    
    from_house: House number where planet is located (1-12)
    aspect_numbers: List of aspect positions [4, 7, 8] for Mars
    
    Returns: List of aspected house numbers
    
    FORMULA: target_house = ((from_house - 1) + (aspect_number - 1)) % 12 + 1
    
    Example 1:
    - Mars in house 1
    - 4th aspect: ((1-1) + (4-1)) % 12 + 1 = 3 % 12 + 1 = 4 ✓
    - 7th aspect: ((1-1) + (7-1)) % 12 + 1 = 6 % 12 + 1 = 7 ✓
    - 8th aspect: ((1-1) + (8-1)) % 12 + 1 = 7 % 12 + 1 = 8 ✓
    
    Example 2:
    - Jupiter in house 9
    - 5th aspect: ((9-1) + (5-1)) % 12 + 1 = 12 % 12 + 1 = 1 ✓
    - 7th aspect: ((9-1) + (7-1)) % 12 + 1 = 14 % 12 + 1 = 3 ✓
    - 9th aspect: ((9-1) + (9-1)) % 12 + 1 = 16 % 12 + 1 = 5 ✓
    """
    aspected_houses = []
    for aspect_num in aspect_numbers:
        # Correct formula: subtract 1, add, modulo, add 1
        target = ((from_house - 1) + (aspect_num - 1)) % 12 + 1
        aspected_houses.append(target)
    return aspected_houses

def is_planet_aspecting_house(planet_name, target_house, chart):
    """
    Check if a planet aspects a specific house
    
    planet_name: Name of the planet ('Jupiter', 'Saturn', etc.)
    target_house: House number to check (1-12)
    chart: Birth chart dictionary
    
    Returns: Boolean
    """
    planet_house = chart[planet_name]['house']
    aspect_numbers = PLANET_ASPECTS.get(planet_name, [7])  # Default 7th aspect
    aspected_houses = calculate_aspect_houses(planet_house, aspect_numbers)
    return target_house in aspected_houses

def is_planet_aspecting_planet(planet1, planet2, chart):
    """
    Check if planet1 aspects planet2
    
    Returns: dict with 'is_aspecting' and 'aspect_type'
    """
    planet1_house = chart[planet1]['house']
    planet2_house = chart[planet2]['house']
    aspect_numbers = PLANET_ASPECTS.get(planet1, [7])
    aspected_houses = calculate_aspect_houses(planet1_house, aspect_numbers)
    
    if planet2_house in aspected_houses:
        # Find which aspect type
        house_diff = ((planet2_house - planet1_house - 1) % 12) + 1
        return {
            'is_aspecting': True,
            'aspect_type': f'{house_diff}th aspect',
            'aspected_houses': aspected_houses
        }
    
    return {'is_aspecting': False}

# ==================== LONGITUDE-BASED HEMMING CHECK ====================

def is_between_longitudes(test_long, start_long, end_long):
    """
    Check if test_long is between start_long and end_long (clockwise direction)
    
    This handles the circular nature of zodiac (0° = 360°)
    
    Example 1:
    - Rahu at 30°, Ketu at 210°
    - Planet at 120° → between 30° and 210° clockwise ✓
    
    Example 2:
    - Rahu at 300°, Ketu at 120°
    - Planet at 30° → between 300° and 120° (crossing 0°) ✓
    - Planet at 200° → NOT between 300° and 120° ✗
    """
    # Normalize all angles to 0-360
    test_long = test_long % 360
    start_long = start_long % 360
    end_long = end_long % 360
    
    if start_long < end_long:
        # Normal case: no wrap around 0°
        return start_long < test_long < end_long
    else:
        # Wrap around case: crosses 0°/360°
        return test_long > start_long or test_long < end_long

# ==================== CHART CALCULATIONS ====================

def calculate_birth_chart(jd, lat, lon):
    """Calculate complete birth chart"""
    try:
        chart = {}
        ayanamsa = get_ayanamsa(jd)
        
        asc_longitude = get_ascendant(jd, lat, lon)
        asc_sign, asc_degree, asc_sign_num = get_sign_and_degree(asc_longitude)
        
        chart['Ascendant'] = {
            'longitude': round(asc_longitude, 6),
            'sign': asc_sign,
            'degree': round(asc_degree, 6),
            'sign_num': asc_sign_num
        }
        
        for planet_name, planet_id in PLANETS.items():
            longitude, speed = get_planet_position(jd, planet_id)
            
            if planet_name == 'Ketu':
                longitude = (longitude + 180) % 360
                speed = -speed
            
            sign, degree, sign_num = get_sign_and_degree(longitude)
            house = get_house_whole_sign(longitude, asc_sign_num)
            
            if planet_name not in ['Sun', 'Moon', 'Rahu', 'Ketu']:
                is_retrograde = speed < 0
            else:
                is_retrograde = False
            
            chart[planet_name] = {
                'longitude': round(longitude, 6),
                'sign': sign,
                'degree': round(degree, 6),
                'sign_num': sign_num,
                'house': house,
                'retrograde': is_retrograde,
                'speed': round(speed, 6)
            }
        
        return chart, ayanamsa
    except Exception as e:
        raise ValueError(f"Error calculating birth chart: {str(e)}")

def calculate_nakshatra(longitude):
    """Calculate nakshatra from longitude"""
    nakshatra_span = 360 / 27
    nakshatra_num = int(longitude / nakshatra_span)
    pada = int((longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
    
    return {
        'name': NAKSHATRAS[nakshatra_num],
        'number': nakshatra_num + 1,
        'pada': pada,
        'lord': NAKSHATRA_LORDS[nakshatra_num % 9]
    }

def calculate_tithi(jd, lat, lon):
    """Calculate tithi"""
    try:
        ayanamsa = get_ayanamsa(jd)
        sun_long, _ = get_planet_position(jd, swe.SUN)
        moon_long, _ = get_planet_position(jd, swe.MOON)
        
        diff = normalize_angle(moon_long - sun_long)
        tithi_num = int(diff / 12) + 1
        
        if tithi_num > 30:
            tithi_num = 30
        
        TITHI_NAMES = [
            'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
            'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
            'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Purnima'
        ]
        
        paksha = 'Shukla' if tithi_num <= 15 else 'Krishna'
        tithi_name = TITHI_NAMES[(tithi_num - 1) % 15]
        
        is_purnima = (tithi_num == 15)
        is_amavasya = (tithi_num == 30)
        is_ekadashi = (tithi_num == 11 or tithi_num == 26)
        
        return {
            'number': tithi_num,
            'name': tithi_name,
            'paksha': paksha,
            'is_purnima': is_purnima,
            'is_amavasya': is_amavasya,
            'is_ekadashi': is_ekadashi
        }
    except Exception as e:
        return {'number': 1, 'name': 'Unknown', 'paksha': 'Unknown'}

def calculate_hora(jd, lat, lon):
    """Calculate planetary hora"""
    try:
        sunrise_jd, sunset_jd = get_sunrise_sunset(jd, lat, lon)
        next_sunrise_jd, _ = get_sunrise_sunset(jd + 1, lat, lon)
        
        is_day = sunrise_jd <= jd < sunset_jd
        
        if is_day:
            day_duration = (sunset_jd - sunrise_jd) * 24
            hora_length = day_duration / 12
            elapsed = (jd - sunrise_jd) * 24
            hora_num = int(elapsed / hora_length)
        else:
            night_duration = (next_sunrise_jd - sunset_jd) * 24
            hora_length = night_duration / 12
            elapsed = (jd - sunset_jd) * 24
            hora_num = int(elapsed / hora_length) + 12
        
        if hora_num < 0:
            hora_num = 0
        if hora_num > 23:
            hora_num = 23
        
        weekday = int((jd + 0.5) % 7)
        day_lord = WEEKDAY_LORDS[weekday]
        
        day_lord_index = HORA_SEQUENCE.index(day_lord)
        current_hora_lord = HORA_SEQUENCE[(day_lord_index + hora_num) % 7]
        
        return {
            'hora_number': hora_num + 1,
            'hora_lord': current_hora_lord,
            'is_day': is_day,
            'day_lord': day_lord
        }
    except Exception as e:
        return {'hora_number': 1, 'hora_lord': 'Sun', 'is_day': True, 'day_lord': 'Sun'}

def calculate_rahu_kaal(jd, lat, lon):
    """Calculate Rahu Kaal timing"""
    try:
        sunrise_jd, sunset_jd = get_sunrise_sunset(jd, lat, lon)
        day_duration = (sunset_jd - sunrise_jd) * 24
        one_part = day_duration / 8
        
        weekday = int((jd + 0.5) % 7)
        RAHU_KAAL_POSITION = {6: 7, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        
        position = RAHU_KAAL_POSITION[weekday]
        start_jd = sunrise_jd + ((position - 1) * one_part / 24)
        end_jd = start_jd + (one_part / 24)
        
        return {
            'start_jd': start_jd,
            'end_jd': end_jd,
            'duration_minutes': round(one_part * 60, 2)
        }
    except Exception as e:
        return {'duration_minutes': 90}

# ==================== PLANETARY STRENGTH ====================

def check_debilitation(planet, chart):
    """Check if planet is debilitated"""
    if planet not in DEBILITATION_RULES:
        return {'is_debilitated': False}
    
    rules = DEBILITATION_RULES[planet]
    planet_data = chart[planet]
    
    is_debilitated = (planet_data['sign_num'] == rules['sign_num'])
    
    if is_debilitated:
        exact_degree = rules['degree']
        distance = abs(planet_data['degree'] - exact_degree)
        severity = 'high' if distance < 5 else 'moderate'
        
        return {
            'is_debilitated': True,
            'severity': severity,
            'distance_from_exact': round(distance, 2)
        }
    
    return {'is_debilitated': False}

def check_exaltation(planet, chart):
    """Check if planet is exalted"""
    if planet not in EXALTATION_RULES:
        return {'is_exalted': False}
    
    rules = EXALTATION_RULES[planet]
    planet_data = chart[planet]
    
    is_exalted = (planet_data['sign_num'] == rules['sign_num'])
    
    if is_exalted:
        exact_degree = rules['degree']
        distance = abs(planet_data['degree'] - exact_degree)
        strength = 'high' if distance < 5 else 'moderate'
        
        return {
            'is_exalted': True,
            'strength': strength,
            'distance_from_exact': round(distance, 2)
        }
    
    return {'is_exalted': False}

def check_combustion(planet, chart):
    """Check if planet is combust"""
    if planet in ['Sun', 'Rahu', 'Ketu']:
        return {'is_combust': False}
    
    if planet not in COMBUSTION_RULES:
        return {'is_combust': False}
    
    planet_long = chart[planet]['longitude']
    sun_long = chart['Sun']['longitude']
    
    distance = calculate_angular_distance(planet_long, sun_long)
    combustion_limit = COMBUSTION_RULES[planet]
    
    if distance < combustion_limit:
        return {
            'is_combust': True,
            'distance_from_sun': round(distance, 2),
            'multiplier': 2
        }
    
    return {'is_combust': False}

def check_conjunction(planet1, planet2, chart, orb=10):
    """Check if two planets are in conjunction"""
    long1 = chart[planet1]['longitude']
    long2 = chart[planet2]['longitude']
    
    distance = calculate_angular_distance(long1, long2)
    
    if distance <= orb:
        return {
            'in_conjunction': True,
            'distance': round(distance, 2)
        }
    
    return {'in_conjunction': False}

def calculate_simplified_strength(planet, chart):
    """Calculate simplified planetary strength"""
    score = 300
    
    planet_data = chart[planet]
    sign_num = planet_data['sign_num']
    
    if planet in OWN_SIGNS and sign_num in OWN_SIGNS[planet]:
        score += 100
    
    exalt_status = check_exaltation(planet, chart)
    if exalt_status['is_exalted']:
        score += 150
    
    deb_status = check_debilitation(planet, chart)
    if deb_status['is_debilitated']:
        score -= 200
    
    comb_status = check_combustion(planet, chart)
    if comb_status['is_combust']:
        score -= 100
    
    if planet_data.get('retrograde', False):
        score += 30
    
    return max(0, score)

# ==================== CORRECTED MANGAL DOSHA DETECTION ====================

def detect_mangal_dosha_complete(chart, birth_date):
    """
    COMPLETE CORRECTED Mangal Dosha detection from THREE reference points:
    1. Lagna (Ascendant)
    2. Moon
    3. Venus
    
    Traditional rule: Mars in houses 1, 2, 4, 7, 8, 12 from ANY of these three
    creates Mangal Dosha. Severity increases if present in multiple charts.
    """
    # Dosha houses
    DOSHA_HOUSES = [1, 2, 4, 7, 8, 12]
    
    # Get Mars data
    mars_sign_num = chart['Mars']['sign_num']
    mars_house = chart['Mars']['house']  # From Lagna
    
    # Calculate Mars position from Moon (Chandra Lagna)
    moon_sign_num = chart['Moon']['sign_num']
    mars_from_moon = ((mars_sign_num - moon_sign_num) % 12) + 1
    
    # Calculate Mars position from Venus
    venus_sign_num = chart['Venus']['sign_num']
    mars_from_venus = ((mars_sign_num - venus_sign_num) % 12) + 1
    
    # Check dosha from each reference point
    dosha_from_lagna = mars_house in DOSHA_HOUSES
    dosha_from_moon = mars_from_moon in DOSHA_HOUSES
    dosha_from_venus = mars_from_venus in DOSHA_HOUSES
    
    # Count how many charts show dosha
    dosha_count = sum([dosha_from_lagna, dosha_from_moon, dosha_from_venus])
    
    # If no dosha in any chart
    if dosha_count == 0:
        return {
            'has_dosha': False,
            'reason': 'Mars not in dosha houses from Lagna, Moon, or Venus',
            'mars_from_lagna': mars_house,
            'mars_from_moon': mars_from_moon,
            'mars_from_venus': mars_from_venus
        }
    
    # Mars IS in dosha house(s) - now check for cancellations
    cancellations = []
    
    # Base severity scoring based on houses and count
    house_severity = {1: 30, 2: 25, 4: 20, 7: 40, 8: 35, 12: 25}
    
    # Calculate base severity (use highest house severity)
    severity_score = 0
    if dosha_from_lagna:
        severity_score = max(severity_score, house_severity[mars_house])
    if dosha_from_moon:
        severity_score = max(severity_score, house_severity[mars_from_moon])
    if dosha_from_venus:
        severity_score = max(severity_score, house_severity[mars_from_venus])
    
    # Increase severity if present in multiple charts
    if dosha_count == 2:
        severity_score += 15
        cancellations.append(f'Dosha present in 2 out of 3 charts (increased severity)')
    elif dosha_count == 3:
        severity_score += 30
        cancellations.append(f'Dosha present in ALL 3 charts (high severity)')
    
    dosha_details = {
        'from_lagna': dosha_from_lagna,
        'lagna_house': mars_house if dosha_from_lagna else 'N/A',
        'from_moon': dosha_from_moon,
        'moon_house': mars_from_moon if dosha_from_moon else 'N/A',
        'from_venus': dosha_from_venus,
        'venus_house': mars_from_venus if dosha_from_venus else 'N/A',
        'count': dosha_count
    }
    
    # CANCELLATION 1: Mars in own sign (Aries=0, Scorpio=7)
    if mars_sign_num in [0, 7]:
        cancellations.append('Mars in own sign (Aries/Scorpio)')
        severity_score -= 20
    
    # CANCELLATION 2: Mars exalted (Capricorn=9)
    if mars_sign_num == 9:
        cancellations.append('Mars exalted in Capricorn')
        severity_score -= 30
    
    # CANCELLATION 3: Mars debilitated (Cancer=3) - INCREASES severity
    if mars_sign_num == 3:
        cancellations.append('Mars debilitated in Cancer (increases severity)')
        severity_score += 20
    
    # CANCELLATION 4: Jupiter aspect on Mars - CORRECTED
    jupiter_aspects_mars = is_planet_aspecting_planet('Jupiter', 'Mars', chart)
    if jupiter_aspects_mars['is_aspecting']:
        cancellations.append(f"Jupiter aspecting Mars ({jupiter_aspects_mars['aspect_type']})")
        severity_score -= 25
    
    # CANCELLATION 5: Mars in 2nd/12th for Aries/Scorpio ascendant
    asc_sign_num = chart['Ascendant']['sign_num']
    if asc_sign_num in [0, 7] and mars_house in [2, 12]:
        cancellations.append(f'Mars in {mars_house}th house for Aries/Scorpio ascendant')
        severity_score -= 15
    
    # CANCELLATION 6: Age-based cancellation (after 28 years)
    try:
        birth_year = int(birth_date.split('-')[0])
        current_year = datetime.utcnow().year
        age = current_year - birth_year
        
        if age >= 28:
            cancellations.append(f'Age-based cancellation (age: {age})')
            severity_score -= 10
    except:
        pass
    
    # CANCELLATION 7: Mars with benefics (Venus, Jupiter, Mercury)
    for benefic in ['Venus', 'Jupiter', 'Mercury']:
        conj = check_conjunction('Mars', benefic, chart, orb=10)
        if conj['in_conjunction']:
            cancellations.append(f"Mars conjunct {benefic} ({conj['distance']}°)")
            severity_score -= 10
    
    # CANCELLATION 8: Both partners have Mangal Dosha (mutual cancellation)
    # This would need partner's chart - just note it
    cancellations.append('Note: Check partner chart - mutual Mangal Dosha cancels')
    
    # CANCELLATION 9: Mars in 3rd or 6th house from Venus (some texts)
    if mars_from_venus in [3, 6]:
        cancellations.append(f'Mars in {mars_from_venus}th house from Venus (beneficial)')
        severity_score -= 10
    
    # Determine final severity after cancellations
    severity_score = max(0, severity_score)
    
    if severity_score == 0:
        return {
            'has_dosha': False,
            'original_dosha': True,
            'cancellation_status': 'Fully Cancelled',
            'cancellations': cancellations,
            'dosha_details': dosha_details,
            'mars_sign': chart['Mars']['sign']
        }
    
    # Determine severity level
    if severity_score < 25:
        severity = 'mild'
        total_count = 10000
        duration = 40
    elif severity_score < 50:
        severity = 'moderate'
        total_count = 20000
        duration = 60
    else:
        severity = 'severe'
        total_count = 40000
        duration = 90
    
    return {
        'has_dosha': True,
        'severity': severity,
        'severity_score': severity_score,
        'dosha_details': dosha_details,
        'mars_sign': chart['Mars']['sign'],
        'cancellations': cancellations,
        'cancellation_status': 'Partially Cancelled' if len([c for c in cancellations if 'Note' not in c]) > 0 else 'Active',
        'main_mantra': 'Hanuman Chalisa + Mars Beej Mantra',
        'total_count': total_count,
        'daily_count': 108,
        'duration_days': duration,
        'additional_remedies': [
            'Visit Hanuman temple on Tuesdays',
            'Fast on Tuesdays',
            'Donate red items (clothes, lentils) on Tuesdays',
            'Wear red coral (consult astrologer first)',
            'Recite Mars Beej Mantra 10,000 times'
        ]
    }

# ==================== CORRECTED KAAL SARP DOSHA (LONGITUDE-BASED) ====================

def detect_kaal_sarp_dosha_complete(chart):
    """
    COMPLETE CORRECTED Kaal Sarp Dosha detection using LONGITUDES (more precise)
    
    Traditional Rule: All 7 planets hemmed between Rahu-Ketu axis
    - Full Dosha: All 7 planets in one hemisphere
    - Partial Dosha: 6 planets in one hemisphere
    
    This version uses actual longitudes for precise hemming check
    """
    rahu_long = chart['Rahu']['longitude']
    ketu_long = chart['Ketu']['longitude']
    rahu_house = chart['Rahu']['house']
    ketu_house = chart['Ketu']['house']
    
    planets_to_check = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    # Check each planet: which hemisphere?
    # Hemisphere 1: From Rahu to Ketu (clockwise)
    # Hemisphere 2: From Ketu to Rahu (clockwise)
    
    planets_hemisphere1 = []
    planets_hemisphere2 = []
    
    for planet in planets_to_check:
        planet_long = chart[planet]['longitude']
        
        # Check if planet is between Rahu and Ketu (clockwise)
        if is_between_longitudes(planet_long, rahu_long, ketu_long):
            planets_hemisphere1.append(planet)
        else:
            planets_hemisphere2.append(planet)
    
    count_h1 = len(planets_hemisphere1)
    count_h2 = len(planets_hemisphere2)
    
    # Check for full Kaal Sarp Dosha (all 7 in one hemisphere)
    has_full_dosha = (count_h1 == 7 or count_h2 == 7)
    
    # Check for partial Kaal Sarp Dosha (6 in one hemisphere)
    has_partial_dosha = (count_h1 == 6 or count_h2 == 6)
    
    if not has_full_dosha and not has_partial_dosha:
        return {
            'has_dosha': False,
            'type': 'None',
            'planets_in_h1': count_h1,
            'planets_in_h2': count_h2,
            'hemming_status': f'{max(count_h1, count_h2)}/7 planets on one side'
        }
    
    # Determine which hemisphere has more planets
    if count_h1 >= count_h2:
        hemmed_planets = planets_hemisphere1
        hemisphere_used = 'Rahu to Ketu'
    else:
        hemmed_planets = planets_hemisphere2
        hemisphere_used = 'Ketu to Rahu'
    
    # Identify Kaal Sarp type based on house positions
    dosha_key = (rahu_house, ketu_house)
    dosha_type = KAAL_SARP_TYPES.get(dosha_key, 'Kaal Sarp Dosha (Mixed Type)')
    
    # Determine if Anulom or Pratilom
    # Anulom: Rahu ahead, planets follow
    # Pratilom: Ketu ahead, planets follow (considered more severe)
    dosha_direction = 'Anulom' if count_h1 >= count_h2 else 'Pratilom'
    
    # Check for CANCELLATIONS
    cancellations = []
    severity_score = 100 if has_full_dosha else 60
    
    # Increase severity for Pratilom
    if dosha_direction == 'Pratilom':
        severity_score += 10
        cancellations.append('Pratilom KSD (reverse direction - more severe)')
    
    # CANCELLATION 1: Jupiter aspect on Rahu or Ketu - CORRECTED
    jupiter_aspects_rahu = is_planet_aspecting_planet('Jupiter', 'Rahu', chart)
    jupiter_aspects_ketu = is_planet_aspecting_planet('Jupiter', 'Ketu', chart)
    
    if jupiter_aspects_rahu['is_aspecting'] or jupiter_aspects_ketu['is_aspecting']:
        aspect_info = []
        if jupiter_aspects_rahu['is_aspecting']:
            aspect_info.append(f"Rahu ({jupiter_aspects_rahu['aspect_type']})")
        if jupiter_aspects_ketu['is_aspecting']:
            aspect_info.append(f"Ketu ({jupiter_aspects_ketu['aspect_type']})")
        cancellations.append(f"Jupiter aspecting {', '.join(aspect_info)}")
        severity_score -= 30
    
    # CANCELLATION 2: Moon not hemmed (Moon outside the hemmed arc)
    if 'Moon' not in hemmed_planets:
        cancellations.append('Moon not hemmed between Rahu-Ketu (significant cancellation)')
        severity_score -= 25
    
    # CANCELLATION 3: Benefic conjunction with Rahu or Ketu
    for benefic in ['Venus', 'Jupiter', 'Mercury']:
        rahu_conj = check_conjunction('Rahu', benefic, chart, orb=10)
        ketu_conj = check_conjunction('Ketu', benefic, chart, orb=10)
        
        if rahu_conj['in_conjunction']:
            cancellations.append(f"{benefic} conjunct Rahu ({rahu_conj['distance']}°)")
            severity_score -= 15
        if ketu_conj['in_conjunction']:
            cancellations.append(f"{benefic} conjunct Ketu ({ketu_conj['distance']}°)")
            severity_score -= 15
    
    # CANCELLATION 4: Rahu/Ketu in Upachaya houses (3rd, 6th, 11th - growth houses)
    if rahu_house in [3, 6, 11] or ketu_house in [3, 6, 11]:
        upachaya_info = []
        if rahu_house in [3, 6, 11]:
            upachaya_info.append(f'Rahu in {rahu_house}th')
        if ketu_house in [3, 6, 11]:
            upachaya_info.append(f'Ketu in {ketu_house}th')
        cancellations.append(f"{', '.join(upachaya_info)} - Upachaya houses")
        severity_score -= 20
    
    # CANCELLATION 5: One planet outside the arc (partial dosha has inherent reduction)
    if has_partial_dosha:
        outside_planet = list(set(planets_to_check) - set(hemmed_planets))[0]
        cancellations.append(f'{outside_planet} outside Rahu-Ketu axis (partial dosha)')
    
    severity_score = max(0, severity_score)
    
    if severity_score < 30:
        return {
            'has_dosha': False,
            'original_dosha': True,
            'type': dosha_type,
            'cancellation_status': 'Fully Cancelled',
            'cancellations': cancellations,
            'rahu_house': rahu_house,
            'ketu_house': ketu_house,
            'rahu_longitude': round(rahu_long, 2),
            'ketu_longitude': round(ketu_long, 2)
        }
    
    # Determine final severity
    if has_partial_dosha:
        severity = 'mild'
        total_count = 60000
        duration = 45
    elif severity_score < 50:
        severity = 'moderate'
        total_count = 90000
        duration = 60
    else:
        severity = 'severe'
        total_count = 125000
        duration = 90
    
    return {
        'has_dosha': True,
        'type': dosha_type,
        'direction': dosha_direction,
        'is_partial': has_partial_dosha,
        'severity': severity,
        'severity_score': severity_score,
        'rahu_house': rahu_house,
        'ketu_house': ketu_house,
        'rahu_longitude': round(rahu_long, 2),
        'ketu_longitude': round(ketu_long, 2),
        'hemisphere_used': hemisphere_used,
        'hemmed_planets': hemmed_planets,
        'cancellations': cancellations,
        'cancellation_status': 'Partially Cancelled' if cancellations else 'Active',
        'main_mantra': 'Om Namah Shivaya',
        'total_count': total_count,
        'daily_count': 108,
        'duration_days': duration,
        'additional_mantras': [
            'Mahamrityunjaya Mantra (108 times daily)',
            'Rahu Beej Mantra (18,000 times total)',
            'Ketu Beej Mantra (17,000 times total)'
        ],
        'special_remedies': [
            'Rudrabhishek on Mondays',
            'Visit Trimbakeshwar, Ujjain, or Rameswaram',
            'Kaal Sarp Dosh Nivaran Puja by qualified priest',
            'Feed snakes on Nag Panchami',
            'Donate black items on Saturdays',
            'Keep fast on Nag Panchami'
        ]
    }

# ==================== CORRECTED PITRA DOSHA DETECTION ====================

def detect_pitra_dosha_complete(chart):
    """
    COMPLETE Pitra Dosha detection with corrected aspect calculations
    
    8 Indicators checked with proper aspects
    """
    indicators = []
    severity_score = 0
    
    sun_house = chart['Sun']['house']
    sun_sign_num = chart['Sun']['sign_num']
    sun_long = chart['Sun']['longitude']
    
    rahu_house = chart['Rahu']['house']
    rahu_long = chart['Rahu']['longitude']
    
    ketu_house = chart['Ketu']['house']
    ketu_long = chart['Ketu']['longitude']
    
    # INDICATOR 1: Sun debilitated in 9th house
    deb_status = check_debilitation('Sun', chart)
    if sun_house == 9 and deb_status['is_debilitated']:
        indicators.append('Sun debilitated in 9th house (most severe)')
        severity_score += 40
    
    # INDICATOR 2: Rahu in 9th house
    if rahu_house == 9:
        indicators.append('Rahu in 9th house')
        severity_score += 35
    
    # INDICATOR 3: Ketu in 9th house
    if ketu_house == 9:
        indicators.append('Ketu in 9th house')
        severity_score += 35
    
    # INDICATOR 4: Sun conjunct Rahu (within 12 degrees)
    sun_rahu_dist = calculate_angular_distance(sun_long, rahu_long)
    if sun_rahu_dist <= 12:
        indicators.append(f'Sun conjunct Rahu ({sun_rahu_dist:.2f}°)')
        severity_score += 30
    
    # INDICATOR 5: Sun conjunct Ketu (within 12 degrees)
    sun_ketu_dist = calculate_angular_distance(sun_long, ketu_long)
    if sun_ketu_dist <= 12:
        indicators.append(f'Sun conjunct Ketu ({sun_ketu_dist:.2f}°)')
        severity_score += 30
    
    # INDICATOR 6: Sun in 5th house afflicted by malefics
    if sun_house == 5:
        for malefic in ['Saturn', 'Mars', 'Rahu', 'Ketu']:
            conj = check_conjunction('Sun', malefic, chart, orb=10)
            if conj['in_conjunction']:
                indicators.append(f"Sun in 5th house conjunct {malefic} ({conj['distance']}°)")
                severity_score += 25
                break
    
    # INDICATOR 7: Saturn aspect on Sun - CORRECTED
    saturn_aspects_sun = is_planet_aspecting_planet('Saturn', 'Sun', chart)
    if saturn_aspects_sun['is_aspecting']:
        indicators.append(f"Saturn aspecting Sun ({saturn_aspects_sun['aspect_type']})")
        severity_score += 20
    
    # INDICATOR 8: Malefics in 9th house or 9th sign
    ninth_house_planets = [p for p in ['Saturn', 'Mars', 'Rahu', 'Ketu'] if chart[p]['house'] == 9]
    if ninth_house_planets:
        indicators.append(f"{', '.join(ninth_house_planets)} in 9th house")
        severity_score += 15 * len(ninth_house_planets)
    
    # No indicators found
    if not indicators:
        return {
            'has_dosha': False,
            'indicators_found': 0
        }
    
    # Check for CANCELLATIONS - CORRECTED
    cancellations = []
    
    # CANCELLATION 1: Jupiter aspect on Sun - CORRECTED
    jupiter_aspects_sun = is_planet_aspecting_planet('Jupiter', 'Sun', chart)
    if jupiter_aspects_sun['is_aspecting']:
        cancellations.append(f"Jupiter aspecting Sun ({jupiter_aspects_sun['aspect_type']})")
        severity_score -= 25
    
    # CANCELLATION 2: Jupiter aspect on 9th house - CORRECTED
    jupiter_aspects_9th = is_planet_aspecting_house('Jupiter', 9, chart)
    if jupiter_aspects_9th:
        jupiter_house = chart['Jupiter']['house']
        aspect_nums = PLANET_ASPECTS['Jupiter']
        aspected = calculate_aspect_houses(jupiter_house, aspect_nums)
        cancellations.append(f'Jupiter in {jupiter_house}th aspecting 9th house')
        severity_score -= 20
    
    # CANCELLATION 3: Strong 9th house (benefics in 9th)
    benefics_in_9th = [p for p in ['Jupiter', 'Venus', 'Mercury'] if chart[p]['house'] == 9]
    if benefics_in_9th:
        cancellations.append(f"{', '.join(benefics_in_9th)} strengthening 9th house")
        severity_score -= 15 * len(benefics_in_9th)
    
    # CANCELLATION 4: Sun exalted
    exalt_status = check_exaltation('Sun', chart)
    if exalt_status['is_exalted']:
        cancellations.append('Sun exalted in Aries')
        severity_score -= 20
    
    # CANCELLATION 5: Jupiter in Kendra (1, 4, 7, 10)
    jupiter_house = chart['Jupiter']['house']
    if jupiter_house in [1, 4, 7, 10]:
        cancellations.append(f'Jupiter in Kendra (house {jupiter_house})')
        severity_score -= 15
    
    severity_score = max(0, severity_score)
    
    if severity_score < 20:
        return {
            'has_dosha': False,
            'original_dosha': True,
            'cancellation_status': 'Fully Cancelled',
            'indicators': indicators,
            'cancellations': cancellations
        }
    
    # Determine severity
    if severity_score < 40:
        severity = 'mild'
        total_count = 43200  # 108 × 400 days
        duration = 48
    elif severity_score < 70:
        severity = 'moderate'
        total_count = 86400  # 108 × 800 days
        duration = 80
    else:
        severity = 'severe'
        total_count = 129600  # 108 × 1200 days
        duration = 120
    
    return {
        'has_dosha': True,
        'severity': severity,
        'severity_score': severity_score,
        'indicators': indicators,
        'indicators_count': len(indicators),
        'cancellations': cancellations,
        'cancellation_status': 'Partially Cancelled' if cancellations else 'Active',
        'main_mantra': 'Om Sarva Pitra Devatabhyo Namah',
        'total_count': total_count,
        'daily_count': 108,
        'duration_days': duration,
        'special_observances': [
            'Perform Tarpan on every Amavasya (new moon)',
            'Feed Brahmins during Pitru Paksha (15 days)',
            'Perform annual Shradh ceremonies on death anniversaries',
            'Donate on Saturdays (black sesame, iron items)',
            'Visit Gaya, Haridwar, or Trimbakeshwar for Pind Daan',
            'Recite Pitra Suktam daily',
            'Light lamp under peepal tree on Saturdays'
        ],
        'additional_mantras': [
            'Gayatri Mantra (108 times daily)',
            'Mahamrityunjaya Mantra (108 times)',
            'Sun Beej Mantra',
            'Pitra Gayatri: Om Pitrudevaya Vidmahe Jagat Dharinyai Dhimahi Tanno Pitrah Prachodayat'
        ]
    }

# ==================== VIMSHOTTARI DASHA ====================

def calculate_vimshottari_dasha(birth_jd, moon_longitude, current_jd):
    """Calculate Vimshottari Dasha - most widely used dasha system"""
    try:
        nakshatra_span = 360 / 27  # 13.333° per nakshatra
        nakshatra_num = int(moon_longitude / nakshatra_span)
        nakshatra_lord = NAKSHATRA_LORDS[nakshatra_num % 9]
        
        # Calculate how much of birth nakshatra has elapsed
        nakshatra_start = nakshatra_num * nakshatra_span
        degrees_elapsed = moon_longitude - nakshatra_start
        fraction_elapsed = degrees_elapsed / nakshatra_span
        
        # Birth dasha balance (years remaining at birth)
        birth_dasha_lord = nakshatra_lord
        birth_dasha_balance = DASHA_PERIODS[birth_dasha_lord] * (1 - fraction_elapsed)
        
        # Convert to days
        birth_balance_days = birth_dasha_balance * 365.25
        days_since_birth = current_jd - birth_jd
        
        # Navigate through dashas
        remaining_days = days_since_birth
        current_lord_index = DASHA_ORDER.index(birth_dasha_lord)
        
        # Find current Mahadasha
        if remaining_days < birth_balance_days:
            # Still in birth dasha
            mahadasha_lord = birth_dasha_lord
            mahadasha_elapsed = remaining_days
            mahadasha_total = birth_balance_days
        else:
            # Move to subsequent dashas
            remaining_days -= birth_balance_days
            current_lord_index = (current_lord_index + 1) % 9
            
            while True:
                dasha_lord = DASHA_ORDER[current_lord_index]
                dasha_days = DASHA_PERIODS[dasha_lord] * 365.25
                
                if remaining_days < dasha_days:
                    mahadasha_lord = dasha_lord
                    mahadasha_elapsed = remaining_days
                    mahadasha_total = dasha_days
                    break
                
                remaining_days -= dasha_days
                current_lord_index = (current_lord_index + 1) % 9
        
        # Find current Antardasha
        # Antardasha cycle starts with Mahadasha lord
        antardasha_elapsed = mahadasha_elapsed
        antardasha_start_index = DASHA_ORDER.index(mahadasha_lord)
        
        for i in range(9):
            antardasha_lord_index = (antardasha_start_index + i) % 9
            antardasha_lord = DASHA_ORDER[antardasha_lord_index]
            
            # Antardasha duration = (MD period × AD period × 365.25) / 120
            antardasha_days = (DASHA_PERIODS[mahadasha_lord] * 
                              DASHA_PERIODS[antardasha_lord] * 365.25) / 120
            
            if antardasha_elapsed < antardasha_days:
                break
            
            antardasha_elapsed -= antardasha_days
        
        return {
            'birth_nakshatra': NAKSHATRAS[nakshatra_num],
            'birth_dasha_lord': birth_dasha_lord,
            'mahadasha_lord': mahadasha_lord,
            'mahadasha_remaining_years': round((mahadasha_total - mahadasha_elapsed) / 365.25, 2),
            'antardasha_lord': antardasha_lord,
            'antardasha_remaining_years': round((antardasha_days - antardasha_elapsed) / 365.25, 2)
        }
    except Exception as e:
        return {
            'mahadasha_lord': 'Unknown',
            'mahadasha_remaining_years': 0,
            'antardasha_lord': 'Unknown',
            'antardasha_remaining_years': 0,
            'error': str(e)
        }

# ==================== MANTRA COUNT CALCULATION ====================

def calculate_mantra_count(planet, severity):
    """Calculate mantra count based on severity and traditional rules"""
    base_count = BASE_MANTRA_COUNTS[planet]
    
    # Multiplier based on severity
    multiplier = {'mild': 1, 'moderate': 2, 'severe': 5, 'critical': 10}[severity]
    total = base_count * multiplier
    
    # Round to nearest 108 (one mala)
    total = round(total / 108) * 108
    
    # Calculate duration and daily count
    duration_days = 40 if severity == 'mild' else 60 if severity == 'moderate' else 90
    daily_count = max(108, round((total / duration_days) / 108) * 108)
    
    return {
        'total_count': int(total),
        'daily_count': int(daily_count),
        'duration_days': duration_days,
        'mala_rounds': int(daily_count / 108),
        'base_count': base_count,
        'multiplier': multiplier
    }

# ==================== MAIN ANALYSIS ====================

def analyze_chart_for_mantras(chart, jd, lat, lon, birth_jd, moon_longitude, birth_date):
    """Main analysis function with corrected dosha detection"""
    result = {
        'weak_planets': [],
        'doshas': [],
        'dasha_mantras': [],
        'current_timing': {},
        'recommendations': []
    }
    
    # 1. Planetary strength analysis
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        strength = calculate_simplified_strength(planet, chart)
        deb_status = check_debilitation(planet, chart)
        comb_status = check_combustion(planet, chart)
        exalt_status = check_exaltation(planet, chart)
        
        needs_remedy = False
        severity = 'mild'
        reasons = []
        
        if deb_status['is_debilitated']:
            needs_remedy = True
            severity = 'severe'
            reasons.append(f"Debilitated in {chart[planet]['sign']}")
        elif comb_status['is_combust']:
            needs_remedy = True
            severity = 'moderate'
            reasons.append(f"Combust (within {comb_status['distance_from_sun']:.2f}° of Sun)")
        elif strength < MINIMUM_SHADBALA.get(planet, 300):
            needs_remedy = True
            severity = 'mild'
            reasons.append(f"Low strength score: {strength}")
        
        if needs_remedy:
            count_info = calculate_mantra_count(planet, severity)
            result['weak_planets'].append({
                'planet': planet,
                'severity': severity,
                'reasons': reasons,
                'mantra': BEEJ_MANTRAS[planet],
                'count': count_info,
                'best_day': PLANET_DAYS[planet],
                'current_position': f"{chart[planet]['degree']:.2f}° {chart[planet]['sign']}",
                'house': chart[planet]['house']
            })
    
    # 2. CORRECTED Comprehensive dosha detection
    mangal = detect_mangal_dosha_complete(chart, birth_date)
    if mangal['has_dosha']:
        result['doshas'].append({
            'type': 'Mangal Dosha (Complete - from Lagna, Moon, Venus)',
            'severity': mangal['severity'],
            'details': mangal
        })
    
    kaal_sarp = detect_kaal_sarp_dosha_complete(chart)
    if kaal_sarp['has_dosha']:
        result['doshas'].append({
            'type': f"{kaal_sarp['type']} ({kaal_sarp['direction']})",
            'severity': kaal_sarp['severity'],
            'details': kaal_sarp
        })
    
    pitra = detect_pitra_dosha_complete(chart)
    if pitra['has_dosha']:
        result['doshas'].append({
            'type': 'Pitra Dosha',
            'severity': pitra['severity'],
            'details': pitra
        })
    
    # 3. Dasha mantras
    dasha_info = calculate_vimshottari_dasha(birth_jd, moon_longitude, jd)
    
    result['dasha_mantras'].append({
        'type': 'Mahadasha',
        'planet': dasha_info['mahadasha_lord'],
        'mantra': BEEJ_MANTRAS.get(dasha_info['mahadasha_lord'], {}),
        'daily_count': 108,
        'remaining_years': dasha_info['mahadasha_remaining_years'],
        'priority': 'Highest - Current major period'
    })
    
    result['dasha_mantras'].append({
        'type': 'Antardasha',
        'planet': dasha_info['antardasha_lord'],
        'mantra': BEEJ_MANTRAS.get(dasha_info['antardasha_lord'], {}),
        'daily_count': 108,
        'remaining_years': dasha_info['antardasha_remaining_years'],
        'priority': 'High - Current sub-period'
    })
    
    # 4. Current timing
    hora = calculate_hora(jd, lat, lon)
    tithi = calculate_tithi(jd, lat, lon)
    rahu_kaal = calculate_rahu_kaal(jd, lat, lon)
    
    result['current_timing'] = {
        'hora': hora,
        'tithi': tithi,
        'rahu_kaal': {
            'duration_minutes': rahu_kaal['duration_minutes'],
            'recommendation': 'Good for Rahu/Saturn mantras only, avoid other activities'
        }
    }
    
    # 5. Priority recommendations
    if result['doshas']:
        result['recommendations'].append({
            'priority': 1,
            'category': 'Dosha Remedies (Most Important)',
            'action': 'Address doshas first as they have life-long karmic effects',
            'note': 'Review cancellation status of each dosha carefully'
        })
    
    if result['dasha_mantras']:
        result['recommendations'].append({
            'priority': 2,
            'category': 'Current Dasha Periods',
            'action': f"Daily chanting of {dasha_info['mahadasha_lord']} and {dasha_info['antardasha_lord']} mantras",
            'note': 'These planetary periods are currently active and influencing your life'
        })
    
    if result['weak_planets']:
        result['recommendations'].append({
            'priority': 3,
            'category': 'Planetary Strengthening',
            'action': 'Strengthen weak/debilitated planets based on severity',
            'note': 'Start with severe cases (debilitation) before mild cases'
        })
    
    return result