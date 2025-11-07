import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': -1
}

PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

# Shadbala minimum strength (in Rupas)
MINIMUM_SHADBALA = {
    'Sun': 390,
    'Moon': 360,
    'Mars': 300,
    'Mercury': 420,
    'Jupiter': 390,
    'Venus': 330,
    'Saturn': 300,
    'Rahu': 300,
    'Ketu': 300
}

# Naisargika Bala (Natural Strength) - in Rupas
NAISARGIKA_BALA = {
    'Sun': 60.0,
    'Moon': 51.43,
    'Venus': 42.86,
    'Jupiter': 34.29,
    'Mercury': 25.70,
    'Mars': 17.14,
    'Saturn': 8.57,
    'Rahu': 15.0,
    'Ketu': 15.0
}

# Exaltation and Debilitation
EXALTATION = {
    'Sun': {'sign': 'Aries', 'degree': 10},
    'Moon': {'sign': 'Taurus', 'degree': 3},
    'Mars': {'sign': 'Capricorn', 'degree': 28},
    'Mercury': {'sign': 'Virgo', 'degree': 15},
    'Jupiter': {'sign': 'Cancer', 'degree': 5},
    'Venus': {'sign': 'Pisces', 'degree': 27},
    'Saturn': {'sign': 'Libra', 'degree': 20},
    'Rahu': {'sign': 'Taurus', 'degree': 20},
    'Ketu': {'sign': 'Scorpio', 'degree': 20}
}

DEBILITATION = {
    'Sun': {'sign': 'Libra', 'degree': 10},
    'Moon': {'sign': 'Scorpio', 'degree': 3},
    'Mars': {'sign': 'Cancer', 'degree': 28},
    'Mercury': {'sign': 'Pisces', 'degree': 15},
    'Jupiter': {'sign': 'Capricorn', 'degree': 5},
    'Venus': {'sign': 'Virgo', 'degree': 27},
    'Saturn': {'sign': 'Aries', 'degree': 20},
    'Rahu': {'sign': 'Scorpio', 'degree': 20},
    'Ketu': {'sign': 'Taurus', 'degree': 20}
}

# Planet ownership
PLANET_HOUSES = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mars': ['Aries', 'Scorpio'],
    'Mercury': ['Gemini', 'Virgo'],
    'Jupiter': ['Sagittarius', 'Pisces'],
    'Venus': ['Taurus', 'Libra'],
    'Saturn': ['Capricorn', 'Aquarius'],
    'Rahu': [],
    'Ketu': []
}

# Moolatrikona signs and ranges
MOOLATRIKONA = {
    'Sun': {'sign': 'Leo', 'start': 0, 'end': 20},
    'Moon': {'sign': 'Taurus', 'start': 4, 'end': 20},
    'Mars': {'sign': 'Aries', 'start': 0, 'end': 12},
    'Mercury': {'sign': 'Virgo', 'start': 16, 'end': 20},
    'Jupiter': {'sign': 'Sagittarius', 'start': 0, 'end': 10},
    'Venus': {'sign': 'Libra', 'start': 0, 'end': 15},
    'Saturn': {'sign': 'Aquarius', 'start': 0, 'end': 20}
}

# Natural relationships
NATURAL_FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'],
    'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Mercury', 'Venus'],
    'Rahu': ['Mercury', 'Venus', 'Saturn'],
    'Ketu': ['Mercury', 'Venus', 'Saturn']
}

NATURAL_ENEMIES = {
    'Sun': ['Venus', 'Saturn'],
    'Moon': [],
    'Mars': ['Mercury'],
    'Mercury': ['Moon'],
    'Jupiter': ['Mercury', 'Venus'],
    'Venus': ['Sun', 'Moon'],
    'Saturn': ['Sun', 'Moon', 'Mars'],
    'Rahu': ['Sun', 'Moon', 'Mars'],
    'Ketu': ['Sun', 'Moon', 'Mars']
}

# Functional nature by ascendant
FUNCTIONAL_NATURE = {
    'Aries': {
        'yogakaraka': ['Sun'],
        'benefics': ['Sun', 'Moon', 'Mars', 'Jupiter'],
        'malefics': ['Mercury', 'Venus', 'Saturn'],
        'neutral': ['Rahu', 'Ketu']
    },
    'Taurus': {
        'yogakaraka': ['Saturn'],
        'benefics': ['Saturn', 'Venus', 'Mercury', 'Sun'],
        'malefics': ['Mars', 'Jupiter'],
        'neutral': ['Moon', 'Rahu', 'Ketu']
    },
    'Gemini': {
        'yogakaraka': ['Venus'],
        'benefics': ['Venus', 'Mercury', 'Saturn'],
        'malefics': ['Mars', 'Jupiter', 'Sun'],
        'neutral': ['Moon', 'Rahu', 'Ketu']
    },
    'Cancer': {
        'yogakaraka': ['Mars'],
        'benefics': ['Mars', 'Moon', 'Jupiter'],
        'malefics': ['Venus', 'Mercury', 'Saturn'],
        'neutral': ['Sun', 'Rahu', 'Ketu']
    },
    'Leo': {
        'yogakaraka': ['Mars'],
        'benefics': ['Mars', 'Sun', 'Jupiter'],
        'malefics': ['Venus', 'Mercury', 'Saturn'],
        'neutral': ['Moon', 'Rahu', 'Ketu']
    },
    'Virgo': {
        'yogakaraka': ['Venus'],
        'benefics': ['Venus', 'Mercury', 'Saturn'],
        'malefics': ['Mars', 'Jupiter', 'Sun'],
        'neutral': ['Moon', 'Rahu', 'Ketu']
    },
    'Libra': {
        'yogakaraka': ['Saturn'],
        'benefics': ['Saturn', 'Venus', 'Mercury', 'Moon'],
        'malefics': ['Sun', 'Mars', 'Jupiter'],
        'neutral': ['Rahu', 'Ketu']
    },
    'Scorpio': {
        'yogakaraka': ['Sun'],
        'benefics': ['Sun', 'Moon', 'Mars', 'Jupiter'],
        'malefics': ['Mercury', 'Venus', 'Saturn'],
        'neutral': ['Rahu', 'Ketu']
    },
    'Sagittarius': {
        'yogakaraka': [],
        'benefics': ['Mars', 'Jupiter', 'Sun', 'Moon'],
        'malefics': ['Mercury', 'Venus', 'Saturn'],
        'neutral': ['Rahu', 'Ketu']
    },
    'Capricorn': {
        'yogakaraka': ['Venus'],
        'benefics': ['Venus', 'Mercury', 'Saturn'],
        'malefics': ['Mars', 'Moon', 'Jupiter'],
        'neutral': ['Sun', 'Rahu', 'Ketu']
    },
    'Aquarius': {
        'yogakaraka': ['Venus'],
        'benefics': ['Venus', 'Saturn', 'Mercury', 'Sun'],
        'malefics': ['Moon', 'Mars', 'Jupiter'],
        'neutral': ['Rahu', 'Ketu']
    },
    'Pisces': {
        'yogakaraka': ['Mars'],
        'benefics': ['Mars', 'Moon', 'Jupiter'],
        'malefics': ['Mercury', 'Venus', 'Saturn', 'Sun'],
        'neutral': ['Rahu', 'Ketu']
    }
}

# Vimshottari Dasha years
DASHA_YEARS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17
}

DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# Nakshatra details
NAKSHATRAS = [
    {'name': 'Ashwini', 'lord': 'Ketu', 'start': 0.0, 'end': 13.333333},
    {'name': 'Bharani', 'lord': 'Venus', 'start': 13.333333, 'end': 26.666667},
    {'name': 'Krittika', 'lord': 'Sun', 'start': 26.666667, 'end': 40.0},
    {'name': 'Rohini', 'lord': 'Moon', 'start': 40.0, 'end': 53.333333},
    {'name': 'Mrigashira', 'lord': 'Mars', 'start': 53.333333, 'end': 66.666667},
    {'name': 'Ardra', 'lord': 'Rahu', 'start': 66.666667, 'end': 80.0},
    {'name': 'Punarvasu', 'lord': 'Jupiter', 'start': 80.0, 'end': 93.333333},
    {'name': 'Pushya', 'lord': 'Saturn', 'start': 93.333333, 'end': 106.666667},
    {'name': 'Ashlesha', 'lord': 'Mercury', 'start': 106.666667, 'end': 120.0},
    {'name': 'Magha', 'lord': 'Ketu', 'start': 120.0, 'end': 133.333333},
    {'name': 'Purva Phalguni', 'lord': 'Venus', 'start': 133.333333, 'end': 146.666667},
    {'name': 'Uttara Phalguni', 'lord': 'Sun', 'start': 146.666667, 'end': 160.0},
    {'name': 'Hasta', 'lord': 'Moon', 'start': 160.0, 'end': 173.333333},
    {'name': 'Chitra', 'lord': 'Mars', 'start': 173.333333, 'end': 186.666667},
    {'name': 'Swati', 'lord': 'Rahu', 'start': 186.666667, 'end': 200.0},
    {'name': 'Vishakha', 'lord': 'Jupiter', 'start': 200.0, 'end': 213.333333},
    {'name': 'Anuradha', 'lord': 'Saturn', 'start': 213.333333, 'end': 226.666667},
    {'name': 'Jyeshtha', 'lord': 'Mercury', 'start': 226.666667, 'end': 240.0},
    {'name': 'Mula', 'lord': 'Ketu', 'start': 240.0, 'end': 253.333333},
    {'name': 'Purva Ashadha', 'lord': 'Venus', 'start': 253.333333, 'end': 266.666667},
    {'name': 'Uttara Ashadha', 'lord': 'Sun', 'start': 266.666667, 'end': 280.0},
    {'name': 'Shravana', 'lord': 'Moon', 'start': 280.0, 'end': 293.333333},
    {'name': 'Dhanishta', 'lord': 'Mars', 'start': 293.333333, 'end': 306.666667},
    {'name': 'Shatabhisha', 'lord': 'Rahu', 'start': 306.666667, 'end': 320.0},
    {'name': 'Purva Bhadrapada', 'lord': 'Jupiter', 'start': 320.0, 'end': 333.333333},
    {'name': 'Uttara Bhadrapada', 'lord': 'Saturn', 'start': 333.333333, 'end': 346.666667},
    {'name': 'Revati', 'lord': 'Mercury', 'start': 346.666667, 'end': 360.0}
]


def yantra_get_julian_day(date_str, time_str, timezone_offset):
    """Calculate Julian Day for given date, time and timezone"""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=timezone_offset)
    
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    
    jd = swe.julday(year, month, day, hour)
    return jd


def yantra_normalize_angle(angle):
    """Normalize angle to 0-360 range"""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle


def yantra_get_ayanamsa(jd):
    """Get Lahiri Ayanamsa for given Julian Day"""
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    return swe.get_ayanamsa_ut(jd)


def yantra_calculate_planet_position(planet_id, jd, ayanamsa):
    """Calculate sidereal position of a planet"""
    if planet_id == -1:  # Ketu
        rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE)[0][0]
        ketu_pos = yantra_normalize_angle(rahu_pos + 180)
        return ketu_pos - ayanamsa
    
    result = swe.calc_ut(jd, planet_id)
    tropical_long = result[0][0]
    sidereal_long = yantra_normalize_angle(tropical_long - ayanamsa)
    return sidereal_long


def yantra_get_planet_speed(planet_id, jd):
    """Get planet's daily motion speed"""
    if planet_id == -1:  # Ketu
        rahu_result = swe.calc_ut(jd, swe.MEAN_NODE)
        return -rahu_result[0][3]
    
    result = swe.calc_ut(jd, planet_id)
    return result[0][3]


def yantra_get_ascendant(jd, lat, lon, ayanamsa):
    """Calculate Ascendant (Lagna)"""
    houses = swe.houses(jd, lat, lon, b'P')
    tropical_asc = houses[0][0]
    sidereal_asc = yantra_normalize_angle(tropical_asc - ayanamsa)
    return sidereal_asc


def yantra_get_sign_and_degree(longitude):
    """Convert longitude to sign and degree"""
    sign_num = int(longitude / 30)
    degree = longitude % 30
    return ZODIAC_SIGNS[sign_num], degree, sign_num


def yantra_calculate_houses_whole_sign(ascendant_sign_num):
    """Calculate houses using Whole Sign system"""
    houses = {}
    for i in range(12):
        house_sign = (ascendant_sign_num + i) % 12
        houses[i + 1] = ZODIAC_SIGNS[house_sign]
    return houses


def yantra_get_planet_house(planet_sign_num, ascendant_sign_num):
    """Get house number for a planet using whole sign system"""
    house = ((planet_sign_num - ascendant_sign_num) % 12) + 1
    return house


def yantra_get_nakshatra(longitude):
    """Get nakshatra for given longitude"""
    for nakshatra in NAKSHATRAS:
        if nakshatra['start'] <= longitude < nakshatra['end']:
            pada = int((longitude - nakshatra['start']) / (13.333333 / 4)) + 1
            return {
                'name': nakshatra['name'],
                'lord': nakshatra['lord'],
                'pada': pada
            }
    return None


def yantra_is_planet_retrograde(planet_id, jd):
    """Check if planet is retrograde"""
    if planet_id in [swe.SUN, swe.MOON, swe.MEAN_NODE, -1]:
        return False
    
    result = swe.calc_ut(jd, planet_id)
    speed = result[0][3]
    return speed < 0


def yantra_calculate_birth_chart(birth_data):
    """Calculate complete birth chart"""
    jd = yantra_get_julian_day(birth_data['birth_date'], birth_data['birth_time'], 
                        birth_data['timezone_offset'])
    ayanamsa = yantra_get_ayanamsa(jd)
    
    # Calculate Ascendant
    ascendant_long = yantra_get_ascendant(jd, birth_data['latitude'], birth_data['longitude'], ayanamsa)
    asc_sign, asc_degree, asc_sign_num = yantra_get_sign_and_degree(ascendant_long)
    
    # Calculate houses (whole sign)
    houses = yantra_calculate_houses_whole_sign(asc_sign_num)
    
    # Calculate planetary positions
    planets = {}
    for planet_name, planet_id in PLANETS.items():
        planet_long = yantra_calculate_planet_position(planet_id, jd, ayanamsa)
        sign, degree, sign_num = yantra_get_sign_and_degree(planet_long)
        house = yantra_get_planet_house(sign_num, asc_sign_num)
        nakshatra = yantra_get_nakshatra(planet_long)
        is_retro = yantra_is_planet_retrograde(planet_id, jd)
        speed = yantra_get_planet_speed(planet_id, jd)
        
        planets[planet_name] = {
            'longitude': round(planet_long, 6),
            'sign': sign,
            'sign_num': sign_num,
            'degree': round(degree, 6),
            'house': house,
            'nakshatra': nakshatra,
            'is_retrograde': is_retro,
            'speed': round(speed, 6)
        }
    
    return {
        'ascendant': {
            'sign': asc_sign,
            'degree': round(asc_degree, 6),
            'sign_num': asc_sign_num
        },
        'planets': planets,
        'houses': houses,
        'julian_day': jd,
        'ayanamsa': round(ayanamsa, 6),
        'birth_data': birth_data
    }


def yantra_calculate_uchcha_bala(planet, planet_data):
    """
    Calculate Uchcha Bala (Exaltation strength)
    Maximum: 60 Rupas when at exact exaltation point
    Minimum: 0 Rupas when at exact debilitation point
    """
    exalt_info = EXALTATION.get(planet)
    debil_info = DEBILITATION.get(planet)
    
    if not exalt_info or not debil_info:
        return 30.0
    
    exalt_sign_num = ZODIAC_SIGNS.index(exalt_info['sign'])
    exalt_abs_long = exalt_sign_num * 30 + exalt_info['degree']
    
    debil_sign_num = ZODIAC_SIGNS.index(debil_info['sign'])
    debil_abs_long = debil_sign_num * 30 + debil_info['degree']
    
    planet_abs_long = planet_data['sign_num'] * 30 + planet_data['degree']
    
    diff_from_exalt = abs(planet_abs_long - exalt_abs_long)
    if diff_from_exalt > 180:
        diff_from_exalt = 360 - diff_from_exalt
    
    uchcha_bala = 60.0 * (1.0 - (diff_from_exalt / 180.0))
    
    return max(0.0, uchcha_bala)


def yantra_calculate_saptavargaja_bala(planet, planet_data):
    """Calculate Saptavargaja Bala (Strength from 7 divisional charts)"""
    sign = planet_data['sign']
    bala = 0.0
    
    if sign in PLANET_HOUSES.get(planet, []):
        bala += 30.0
    else:
        bala += 15.0
    
    mool = MOOLATRIKONA.get(planet)
    if mool and mool['sign'] == sign:
        degree = planet_data['degree']
        if mool['start'] <= degree <= mool['end']:
            bala += 15.0
    
    return bala


def yantra_calculate_ojhayugma_bala(planet, planet_data):
    """Calculate Ojhayugmarasyamsa Bala (Odd-Even sign strength)"""
    sign_num = planet_data['sign_num']
    is_odd_sign = (sign_num % 2 == 0)
    
    if planet in ['Sun', 'Mars', 'Jupiter', 'Saturn']:
        return 15.0 if is_odd_sign else 0.0
    elif planet in ['Moon', 'Venus']:
        return 15.0 if not is_odd_sign else 0.0
    else:
        return 7.5


def yantra_calculate_kendra_bala(planet_data):
    """Calculate Kendra Bala (Angular house strength)"""
    house = planet_data['house']
    
    if house in [1, 4, 7, 10]:
        return 60.0
    elif house in [2, 5, 8, 11]:
        return 30.0
    else:
        return 15.0


def yantra_calculate_drekkana_bala(planet, planet_data):
    """Calculate Drekkana Bala (Decanate strength)"""
    degree = planet_data['degree']
    
    if degree < 10:
        return 15.0 if planet in ['Sun', 'Mars', 'Jupiter', 'Saturn'] else 5.0
    elif degree < 20:
        return 10.0
    else:
        return 15.0 if planet in ['Moon', 'Venus'] else 5.0


def yantra_calculate_sthana_bala(planet, planet_data):
    """Calculate complete Sthana Bala (Positional Strength)"""
    uchcha_bala = yantra_calculate_uchcha_bala(planet, planet_data)
    saptavargaja_bala = yantra_calculate_saptavargaja_bala(planet, planet_data)
    ojhayugma_bala = yantra_calculate_ojhayugma_bala(planet, planet_data)
    kendra_bala = yantra_calculate_kendra_bala(planet_data)
    drekkana_bala = yantra_calculate_drekkana_bala(planet, planet_data)
    
    total = uchcha_bala + saptavargaja_bala + ojhayugma_bala + kendra_bala + drekkana_bala
    
    return {
        'total': total,
        'uchcha_bala': uchcha_bala,
        'saptavargaja_bala': saptavargaja_bala,
        'ojhayugma_bala': ojhayugma_bala,
        'kendra_bala': kendra_bala,
        'drekkana_bala': drekkana_bala
    }


def yantra_calculate_dig_bala(planet, house):
    """Calculate Dig Bala (Directional strength)"""
    best_directions = {
        'Sun': 10,
        'Mars': 10,
        'Moon': 4,
        'Venus': 4,
        'Mercury': 1,
        'Jupiter': 1,
        'Saturn': 7
    }
    
    if planet not in best_directions:
        return 30.0
    
    best_house = best_directions[planet]
    distance = min(abs(house - best_house), 12 - abs(house - best_house))
    dig_bala = 60.0 * (1.0 - (distance / 6.0))
    
    return max(0.0, dig_bala)


def yantra_calculate_nathonnatha_bala(planet, chart):
    """Calculate Nathonnatha Bala (Day/Night strength)"""
    sun_house = chart['planets']['Sun']['house']
    is_day = sun_house in [7, 8, 9, 10, 11, 12]
    
    if planet in ['Sun', 'Jupiter', 'Venus']:
        return 60.0 if is_day else 0.0
    elif planet in ['Moon', 'Mars', 'Saturn']:
        return 60.0 if not is_day else 0.0
    else:
        return 30.0


def yantra_calculate_paksha_bala(chart):
    """Calculate Paksha Bala (Lunar fortnight strength)"""
    sun_long = chart['planets']['Sun']['longitude']
    moon_long = chart['planets']['Moon']['longitude']
    
    diff = yantra_normalize_angle(moon_long - sun_long)
    is_waxing = diff < 180
    
    return is_waxing, diff


def yantra_calculate_tribhaga_bala(planet, chart):
    """Calculate Tribhaga Bala (1/3rd of day/night strength)"""
    sun_house = chart['planets']['Sun']['house']
    is_day = sun_house in [7, 8, 9, 10, 11, 12]
    
    if is_day and planet == 'Jupiter':
        return 60.0
    elif not is_day and planet == 'Moon':
        return 60.0
    else:
        return 30.0


def yantra_calculate_abda_masa_dina_hora_bala(planet):
    """Calculate Varsha-Masa-Dina-Hora Bala (Time lord strengths)"""
    return 30.0


def yantra_calculate_ayana_bala(planet, planet_data):
    """Calculate Ayana Bala (Declination strength)"""
    sign_num = planet_data['sign_num']
    
    if sign_num < 6:
        return 30.0 if planet in ['Sun', 'Mars', 'Jupiter'] else 15.0
    else:
        return 30.0 if planet in ['Moon', 'Venus', 'Saturn'] else 15.0


def yantra_calculate_kala_bala(planet, planet_data, chart):
    """Calculate complete Kala Bala (Temporal Strength)"""
    nathonnatha_bala = yantra_calculate_nathonnatha_bala(planet, chart)
    
    paksha_bala = 0.0
    if planet == 'Moon':
        is_waxing, diff = yantra_calculate_paksha_bala(chart)
        paksha_bala = (diff / 180.0) * 60.0 if is_waxing else (1.0 - (diff - 180.0) / 180.0) * 60.0
    
    tribhaga_bala = yantra_calculate_tribhaga_bala(planet, chart)
    abda_bala = yantra_calculate_abda_masa_dina_hora_bala(planet)
    ayana_bala = yantra_calculate_ayana_bala(planet, planet_data)
    
    total = nathonnatha_bala + paksha_bala + tribhaga_bala + abda_bala + ayana_bala
    
    return {
        'total': total,
        'nathonnatha_bala': nathonnatha_bala,
        'paksha_bala': paksha_bala,
        'tribhaga_bala': tribhaga_bala,
        'abda_bala': abda_bala,
        'ayana_bala': ayana_bala
    }


def yantra_calculate_cheshta_bala(planet, planet_data, chart):
    """Calculate Cheshta Bala (Motional strength)"""
    if planet in ['Sun', 'Moon']:
        return {'total': 0.0, 'is_retrograde': False, 'is_combust': False}
    
    if planet in ['Rahu', 'Ketu']:
        return {'total': 30.0, 'is_retrograde': False, 'is_combust': False}
    
    cheshta_bala = 0.0
    
    if planet_data.get('is_retrograde', False):
        cheshta_bala = 60.0
    else:
        cheshta_bala = 30.0
    
    sun_long = chart['planets']['Sun']['longitude']
    planet_long = planet_data['longitude']
    diff = abs(sun_long - planet_long)
    diff = min(diff, 360 - diff)
    
    is_combust = diff < 10 and planet not in ['Sun', 'Moon', 'Rahu', 'Ketu']
    
    if is_combust:
        cheshta_bala *= 0.5
    
    return {
        'total': cheshta_bala,
        'is_retrograde': planet_data.get('is_retrograde', False),
        'is_combust': is_combust
    }


def yantra_calculate_drik_bala(planet, chart):
    """Calculate Drik Bala (Aspectual strength)"""
    drik_bala = 0.0
    planet_house = chart['planets'][planet]['house']
    
    benefics = ['Jupiter', 'Venus', 'Mercury']
    malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
    
    for other_planet, other_data in chart['planets'].items():
        if other_planet == planet:
            continue
        
        other_house = other_data['house']
        
        # 7th house aspect
        if (other_house - planet_house) % 12 == 6 or (planet_house - other_house) % 12 == 6:
            if other_planet in benefics:
                drik_bala += 15.0
            elif other_planet in malefics:
                drik_bala -= 10.0
        
        # Jupiter's special aspects
        if other_planet == 'Jupiter':
            house_diff = (planet_house - other_house) % 12
            if house_diff in [4, 8]:
                drik_bala += 20.0
        
        # Saturn's special aspects
        if other_planet == 'Saturn':
            house_diff = (planet_house - other_house) % 12
            if house_diff in [2, 9]:
                drik_bala -= 15.0
        
        # Mars's special aspects
        if other_planet == 'Mars':
            house_diff = (planet_house - other_house) % 12
            if house_diff in [3, 7]:
                drik_bala -= 12.0
        
        # Conjunction
        if other_house == planet_house:
            if other_planet in benefics:
                drik_bala += 10.0
            elif other_planet in malefics:
                drik_bala -= 8.0
    
    drik_bala = max(-60.0, min(60.0, drik_bala))
    
    return drik_bala


def yantra_calculate_shadbala(chart):
    """Calculate complete Shadbala (Six-fold Strength) for all planets"""
    shadbala_scores = {}
    
    for planet in PLANET_NAMES:
        if planet not in chart['planets']:
            continue
        
        planet_data = chart['planets'][planet]
        
        sthana_bala_data = yantra_calculate_sthana_bala(planet, planet_data)
        sthana_bala = sthana_bala_data['total']
        
        dig_bala = yantra_calculate_dig_bala(planet, planet_data['house'])
        
        kala_bala_data = yantra_calculate_kala_bala(planet, planet_data, chart)
        kala_bala = kala_bala_data['total']
        
        cheshta_bala_data = yantra_calculate_cheshta_bala(planet, planet_data, chart)
        cheshta_bala = cheshta_bala_data['total']
        
        naisargika_bala = NAISARGIKA_BALA.get(planet, 20.0)
        
        drik_bala = yantra_calculate_drik_bala(planet, chart)
        
        total_shadbala = (sthana_bala + dig_bala + kala_bala + 
                         cheshta_bala + naisargika_bala + drik_bala)
        
        minimum_required = MINIMUM_SHADBALA.get(planet, 300)
        is_weak = total_shadbala < minimum_required
        
        shadbala_scores[planet] = {
            'total_rupas': round(total_shadbala, 2),
            'minimum_required': minimum_required,
            'is_weak': is_weak,
            'percentage_of_required': round((total_shadbala / minimum_required) * 100, 2),
            'strength_category': (
                'Very Strong' if total_shadbala >= minimum_required * 1.3 else
                'Strong' if total_shadbala >= minimum_required else
                'Average' if total_shadbala >= minimum_required * 0.8 else
                'Weak' if total_shadbala >= minimum_required * 0.6 else
                'Very Weak'
            ),
            'components': {
                'sthana_bala': round(sthana_bala, 2),
                'dig_bala': round(dig_bala, 2),
                'kala_bala': round(kala_bala, 2),
                'cheshta_bala': round(cheshta_bala, 2),
                'naisargika_bala': round(naisargika_bala, 2),
                'drik_bala': round(drik_bala, 2)
            },
            'detailed_breakdown': {
                'sthana_bala_details': {
                    'uchcha_bala': round(sthana_bala_data['uchcha_bala'], 2),
                    'saptavargaja_bala': round(sthana_bala_data['saptavargaja_bala'], 2),
                    'ojhayugma_bala': round(sthana_bala_data['ojhayugma_bala'], 2),
                    'kendra_bala': round(sthana_bala_data['kendra_bala'], 2),
                    'drekkana_bala': round(sthana_bala_data['drekkana_bala'], 2)
                },
                'kala_bala_details': {
                    'nathonnatha_bala': round(kala_bala_data['nathonnatha_bala'], 2),
                    'paksha_bala': round(kala_bala_data.get('paksha_bala', 0), 2),
                    'tribhaga_bala': round(kala_bala_data['tribhaga_bala'], 2),
                    'abda_bala': round(kala_bala_data['abda_bala'], 2),
                    'ayana_bala': round(kala_bala_data['ayana_bala'], 2)
                },
                'cheshta_bala_details': {
                    'is_retrograde': cheshta_bala_data.get('is_retrograde', False),
                    'is_combust': cheshta_bala_data.get('is_combust', False)
                }
            }
        }
    
    return shadbala_scores


def yantra_check_debilitation(planet, planet_data):
    """Check if planet is debilitated"""
    debil_info = DEBILITATION.get(planet)
    if not debil_info:
        return False
    return planet_data['sign'] == debil_info['sign']


def yantra_check_exaltation(planet, planet_data):
    """Check if planet is exalted"""
    exalt_info = EXALTATION.get(planet)
    if not exalt_info:
        return False
    return planet_data['sign'] == exalt_info['sign']


def yantra_check_mangal_dosha(chart):
    """Check for Mangal Dosha"""
    mars = chart['planets']['Mars']
    mars_house = mars['house']
    
    dosha_houses = [1, 2, 4, 7, 8, 12]
    has_dosha = mars_house in dosha_houses
    
    cancellations = []
    if yantra_check_exaltation('Mars', mars):
        cancellations.append('Mars is exalted')
    if mars['sign'] in ['Aries', 'Scorpio']:
        cancellations.append('Mars in own sign')
    
    return {
        'present': has_dosha and len(cancellations) == 0,
        'mars_house': mars_house,
        'cancellations': cancellations
    }


def yantra_check_kaal_sarp_dosha(chart):
    """Check for Kaal Sarp Dosha"""
    rahu_house = chart['planets']['Rahu']['house']
    ketu_house = chart['planets']['Ketu']['house']
    
    planets_between = 0
    planets_outside = 0
    
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        planet_house = chart['planets'][planet]['house']
        
        if rahu_house < ketu_house:
            if rahu_house < planet_house < ketu_house:
                planets_between += 1
            else:
                planets_outside += 1
        else:
            if planet_house > rahu_house or planet_house < ketu_house:
                planets_between += 1
            else:
                planets_outside += 1
    
    return {
        'present': planets_outside == 0,
        'planets_hemmed': planets_between
    }


def yantra_check_pitra_dosha(chart):
    """Check for Pitra Dosha"""
    sun = chart['planets']['Sun']
    rahu = chart['planets']['Rahu']
    ketu = chart['planets']['Ketu']
    
    sun_rahu_conj = abs(sun['longitude'] - rahu['longitude']) < 10
    sun_ketu_conj = abs(sun['longitude'] - ketu['longitude']) < 10
    
    ninth_house_afflicted = False
    ninth_house_sign_num = (chart['ascendant']['sign_num'] + 8) % 12
    
    for planet in ['Rahu', 'Ketu', 'Saturn']:
        if chart['planets'][planet]['sign_num'] == ninth_house_sign_num:
            ninth_house_afflicted = True
            break
    
    return {
        'present': sun_rahu_conj or sun_ketu_conj or ninth_house_afflicted,
        'sun_rahu_conjunction': sun_rahu_conj,
        'sun_ketu_conjunction': sun_ketu_conj,
        'ninth_house_afflicted': ninth_house_afflicted
    }


def yantra_check_grahan_dosha(chart):
    """Check for Grahan Dosha"""
    sun = chart['planets']['Sun']
    moon = chart['planets']['Moon']
    rahu = chart['planets']['Rahu']
    ketu = chart['planets']['Ketu']
    
    sun_rahu = abs(sun['longitude'] - rahu['longitude'])
    sun_ketu = abs(sun['longitude'] - ketu['longitude'])
    moon_rahu = abs(moon['longitude'] - rahu['longitude'])
    moon_ketu = abs(moon['longitude'] - ketu['longitude'])
    
    sun_rahu = min(sun_rahu, 360 - sun_rahu)
    sun_ketu = min(sun_ketu, 360 - sun_ketu)
    moon_rahu = min(moon_rahu, 360 - moon_rahu)
    moon_ketu = min(moon_ketu, 360 - moon_ketu)
    
    return {
        'present': any([sun_rahu < 12, sun_ketu < 12, moon_rahu < 12, moon_ketu < 12]),
        'sun_afflicted': sun_rahu < 12 or sun_ketu < 12,
        'moon_afflicted': moon_rahu < 12 or moon_ketu < 12
    }


def yantra_calculate_vimshottari_dasha(chart, birth_date):
    """Calculate Vimshottari Dasha"""
    moon_longitude = chart['planets']['Moon']['longitude']
    moon_nakshatra = yantra_get_nakshatra(moon_longitude)
    
    if not moon_nakshatra:
        return None
    
    starting_lord = moon_nakshatra['lord']
    
    nakshatra_span = 13.333333
    nakshatra_start = None
    for nak in NAKSHATRAS:
        if nak['name'] == moon_nakshatra['name']:
            nakshatra_start = nak['start']
            break
    
    if nakshatra_start is None:
        return None
    
    passed = moon_longitude - nakshatra_start
    remaining = nakshatra_span - passed
    
    total_years = DASHA_YEARS[starting_lord]
    balance_years = (remaining / nakshatra_span) * total_years
    
    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    
    dasha_periods = []
    current_date = birth_dt
    
    start_idx = DASHA_ORDER.index(starting_lord)
    
    dasha_periods.append({
        'planet': starting_lord,
        'start_date': current_date.strftime("%Y-%m-%d"),
        'duration_years': round(balance_years, 2)
    })
    current_date = current_date + timedelta(days=balance_years * 365.25)
    
    for i in range(1, len(DASHA_ORDER)):
        planet = DASHA_ORDER[(start_idx + i) % len(DASHA_ORDER)]
        duration = DASHA_YEARS[planet]
        
        dasha_periods.append({
            'planet': planet,
            'start_date': current_date.strftime("%Y-%m-%d"),
            'duration_years': duration
        })
        current_date = current_date + timedelta(days=duration * 365.25)
    
    today = datetime.now()
    current_mahadasha = None
    
    for period in dasha_periods:
        period_start = datetime.strptime(period['start_date'], "%Y-%m-%d")
        period_end = period_start + timedelta(days=period['duration_years'] * 365.25)
        
        if period_start <= today < period_end:
            current_mahadasha = period['planet']
            break
    
    return {
        'moon_nakshatra': moon_nakshatra['name'],
        'starting_dasha_lord': starting_lord,
        'balance_at_birth': round(balance_years, 2),
        'current_mahadasha': current_mahadasha,
        'dasha_sequence': dasha_periods[:9]
    }


def yantra_get_house_lords(ascendant_sign_num):
    """Get lords of all 12 houses"""
    house_lords = {}
    
    for house_num in range(1, 13):
        house_sign_num = (ascendant_sign_num + house_num - 1) % 12
        house_sign = ZODIAC_SIGNS[house_sign_num]
        
        for planet, signs in PLANET_HOUSES.items():
            if house_sign in signs:
                if house_num not in house_lords:
                    house_lords[house_num] = []
                house_lords[house_num].append(planet)
    
    return house_lords


def yantra_recommend_yantras(chart, shadbala, doshas, dasha, birth_date):
    """
    Recommend yantras based on comprehensive analysis
    
    CORRECTED LOGIC - Key Principles:
    1. ONLY recommend for functional benefics or yogakarakas
    2. Planet must be WEAK (below required Shadbala) OR debilitated
    3. Dusthana placement alone is NOT enough - planet must also be weak
    4. Strong planets are NEVER recommended (even in dusthanas)
    5. Malefics are NEVER recommended (even if weak or in dasha)
    """
    ascendant_sign = chart['ascendant']['sign']
    functional_nature = FUNCTIONAL_NATURE.get(ascendant_sign, {})
    
    recommendations = []
    
    for planet in PLANET_NAMES:
        if planet not in chart['planets']:
            continue
        
        score = 0
        reasons = []
        planet_data = chart['planets'][planet]
        
        # Determine functional nature
        is_yogakaraka = planet in functional_nature.get('yogakaraka', [])
        is_benefic = planet in functional_nature.get('benefics', [])
        is_malefic = planet in functional_nature.get('malefics', [])
        
        # CRITICAL: Skip all malefics immediately
        if is_malefic:
            continue
        
        # Only proceed for benefics or yogakarakas
        if not (is_benefic or is_yogakaraka):
            continue
        
        # Get house lordships
        house_lords = yantra_get_house_lords(chart['ascendant']['sign_num'])
        important_houses = [1, 4, 5, 7, 9, 10]  # Kendra + Trikona
        rules_important_house = False
        
        for house_num, lords in house_lords.items():
            if house_num in important_houses and planet in lords:
                rules_important_house = True
                break
        
        # Get weakness status
        is_weak = shadbala[planet]['is_weak']
        percentage = shadbala[planet]['percentage_of_required']
        is_debilitated = yantra_check_debilitation(planet, planet_data)
        is_exalted = yantra_check_exaltation(planet, planet_data)
        
        # =================================================================
        # RULE 1: YOGAKARAKA PLANETS (HIGHEST PRIORITY)
        # =================================================================
        if is_yogakaraka:
            # Weak Yogakaraka
            if is_weak:
                score += 100
                reasons.append(f"Yogakaraka planet is weak - Shadbala: {shadbala[planet]['total_rupas']} Rupas ({percentage}% of required {shadbala[planet]['minimum_required']} Rupas)")
            
            # Debilitated Yogakaraka (CRITICAL)
            if is_debilitated:
                score += 100
                reasons.append("Yogakaraka planet is debilitated - yantra will strengthen it")
            
            # Yogakaraka in dusthana (only if also weak)
            if planet_data['house'] in [6, 8, 12] and is_weak:
                score += 60
                reasons.append(f"Yogakaraka in dusthana house ({planet_data['house']}th) and weak - needs strengthening")
            
            # Exalted Yogakaraka (enhancement bonus)
            if is_exalted and not is_weak:
                score += 20
                reasons.append("Exalted Yogakaraka - yantra will enhance already strong results")
        
        # =================================================================
        # RULE 2: FUNCTIONAL BENEFICS RULING IMPORTANT HOUSES
        # =================================================================
        elif is_benefic and rules_important_house:
            # Weak important house lord
            if is_weak:
                score += 80
                reasons.append(f"Important house lord ({planet}) is weak - Shadbala: {shadbala[planet]['total_rupas']} Rupas ({percentage}%)")
            
            # Debilitated benefic ruling important house
            if is_debilitated:
                score += 90
                reasons.append("Functional benefic ruling important house is debilitated")
            
            # Benefic in dusthana AND weak
            if planet_data['house'] in [6, 8, 12] and is_weak:
                score += 50
                reasons.append(f"Important house lord in dusthana ({planet_data['house']}th house) and weak")
            
            # Very weak (below 70%)
            if percentage < 70:
                score += 30
                reasons.append(f"Significantly weak strength at {percentage}% of required")
        
        # =================================================================
        # RULE 3: OTHER FUNCTIONAL BENEFICS (NOT RULING IMPORTANT HOUSES)
        # =================================================================
        elif is_benefic and not rules_important_house:
            # Very weak benefic (below 60%)
            if percentage < 60:
                score += 40
                reasons.append(f"Functional benefic is very weak - {shadbala[planet]['total_rupas']} Rupas ({percentage}%)")
            
            # Debilitated benefic
            if is_debilitated:
                score += 50
                reasons.append("Debilitated functional benefic needs strengthening")
        
        # =================================================================
        # RULE 4: DOSHA-SPECIFIC CONSIDERATIONS (Only for benefics)
        # =================================================================
        if is_benefic or is_yogakaraka:
            # Venus for Mangal Dosha (only if Venus is weak or average)
            if planet == 'Venus' and doshas.get('mangal_dosha', {}).get('present'):
                if is_weak or percentage < 90:
                    score += 30
                    reasons.append("Venus yantra recommended to mitigate Mangal Dosha effects on marriage")
            
            # Jupiter for Kaal Sarp Dosha (only if Jupiter is weak or average)
            if planet == 'Jupiter' and doshas.get('kaal_sarp_dosha', {}).get('present'):
                if is_weak or percentage < 90:
                    score += 40
                    reasons.append("Jupiter yantra provides protection from Kaal Sarp Dosha")
            
            # Sun for Pitra Dosha (only if Sun is benefic and weak)
            if planet == 'Sun' and doshas.get('pitra_dosha', {}).get('present'):
                if (is_benefic or is_yogakaraka) and is_weak:
                    score += 50
                    reasons.append("Sun yantra helps address Pitra Dosha")
        
        # =================================================================
        # RULE 5: CURRENT DASHA (Only for benefics/yogakarakas who are weak)
        # =================================================================
        if dasha and planet == dasha.get('current_mahadasha'):
            if (is_benefic or is_yogakaraka) and is_weak:
                score += 30
                reasons.append(f"Current Mahadasha lord - strengthening will enhance current period results")
        
        # =================================================================
        # RULE 6: EXALTED BENEFICS (Enhancement only if not strong)
        # =================================================================
        if is_exalted and (is_benefic or is_yogakaraka):
            if is_weak or percentage < 90:
                score += 15
                reasons.append("Exalted benefic - yantra can enhance positive results")
        
        # =================================================================
        # ADD RECOMMENDATION IF SCORE IS SIGNIFICANT
        # =================================================================
        if score >= 30:
            recommendations.append({
                'planet': planet,
                'priority_score': score,
                'reasons': reasons,
                'functional_nature': (
                    'Yogakaraka' if is_yogakaraka else
                    'Functional Benefic' if is_benefic else
                    'Neutral'
                ),
                'shadbala_status': {
                    'current_rupas': shadbala[planet]['total_rupas'],
                    'required_rupas': shadbala[planet]['minimum_required'],
                    'percentage': shadbala[planet]['percentage_of_required'],
                    'strength_category': shadbala[planet]['strength_category'],
                    'is_weak': shadbala[planet]['is_weak']
                },
                'planetary_info': {
                    'house': planet_data['house'],
                    'sign': planet_data['sign'],
                    'degree': round(planet_data['degree'], 2),
                    'nakshatra': planet_data['nakshatra']['name'],
                    'is_debilitated': is_debilitated,
                    'is_exalted': is_exalted,
                    'is_retrograde': planet_data.get('is_retrograde', False)
                },
                'rules_important_houses': rules_important_house
            })
    
    # Sort by priority
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return recommendations


def yantra_get_yantra_details(planet):
    """Get detailed yantra information"""
    yantra_info = {
        'Sun': {
            'sanskrit_name': 'Surya Yantra',
            'metal': 'Gold or Copper',
            'mantra': 'Om Hraam Hreem Hraum Sah Suryaya Namah',
            'beej_mantra': 'Om Hraam Hreem Hraum Sah Suryaya Namah',
            'day': 'Sunday',
            'time': 'Sunrise (within 1 hour)',
            'direction': 'East',
            'benefits': 'Leadership, authority, father relations, government favor, health, vitality, confidence, fame',
            'gemstone': 'Ruby (Manik)',
            'deity': 'Lord Surya',
            'wearing': 'Can be worn as pendant or kept in puja room facing East'
        },
        'Moon': {
            'sanskrit_name': 'Chandra Yantra',
            'metal': 'Silver',
            'mantra': 'Om Shraam Shreem Shraum Sah Chandraya Namah',
            'beej_mantra': 'Om Shraam Shreem Shraum Sah Chandraya Namah',
            'day': 'Monday',
            'time': 'Evening after moonrise',
            'direction': 'Northwest',
            'benefits': 'Mental peace, emotional balance, mother relations, intuition, memory, public image',
            'gemstone': 'Pearl (Moti)',
            'deity': 'Lord Chandra',
            'wearing': 'Can be worn as pendant or kept in puja room facing Northwest'
        },
        'Mars': {
            'sanskrit_name': 'Mangal Yantra',
            'metal': 'Copper',
            'mantra': 'Om Kraam Kreem Kraum Sah Bhaumaya Namah',
            'beej_mantra': 'Om Kraam Kreem Kraum Sah Bhaumaya Namah',
            'day': 'Tuesday',
            'time': 'Morning or noon',
            'direction': 'South',
            'benefits': 'Courage, energy, property matters, sibling relations, surgery success, competitive edge',
            'gemstone': 'Red Coral (Moonga)',
            'deity': 'Lord Mangal',
            'wearing': 'Can be worn as pendant or kept in puja room facing South'
        },
        'Mercury': {
            'sanskrit_name': 'Budh Yantra',
            'metal': 'Bronze or mixed metal',
            'mantra': 'Om Braam Breem Braum Sah Budhaya Namah',
            'beej_mantra': 'Om Braam Breem Braum Sah Budhaya Namah',
            'day': 'Wednesday',
            'time': 'Morning',
            'direction': 'North',
            'benefits': 'Intelligence, communication skills, business acumen, education, analytical ability',
            'gemstone': 'Emerald (Panna)',
            'deity': 'Lord Budha',
            'wearing': 'Can be worn as pendant or kept in puja room facing North'
        },
        'Jupiter': {
            'sanskrit_name': 'Guru Yantra / Brihaspati Yantra',
            'metal': 'Gold',
            'mantra': 'Om Graam Greem Graum Sah Gurave Namah',
            'beej_mantra': 'Om Graam Greem Graum Sah Gurave Namah',
            'day': 'Thursday',
            'time': 'Morning during sunrise',
            'direction': 'Northeast',
            'benefits': 'Wisdom, children, wealth, spirituality, fortune, knowledge, teaching ability, marriage',
            'gemstone': 'Yellow Sapphire (Pukhraj)',
            'deity': 'Lord Brihaspati',
            'wearing': 'Can be worn as pendant or kept in puja room facing Northeast'
        },
        'Venus': {
            'sanskrit_name': 'Shukra Yantra',
            'metal': 'Silver',
            'mantra': 'Om Draam Dreem Draum Sah Shukraya Namah',
            'beej_mantra': 'Om Draam Dreem Draum Sah Shukraya Namah',
            'day': 'Friday',
            'time': 'Morning or evening',
            'direction': 'Southeast',
            'benefits': 'Marriage, love, luxury, arts, beauty, vehicles, material comforts, creativity',
            'gemstone': 'Diamond (Heera)',
            'deity': 'Goddess Lakshmi',
            'wearing': 'Can be worn as pendant or kept in puja room facing Southeast'
        },
        'Saturn': {
            'sanskrit_name': 'Shani Yantra',
            'metal': 'Iron or mixed metal (Ashtadhatu)',
            'mantra': 'Om Praam Preem Praum Sah Shanaye Namah',
            'beej_mantra': 'Om Praam Preem Praum Sah Shanaye Namah',
            'day': 'Saturday',
            'time': 'Evening during sunset',
            'direction': 'West',
            'benefits': 'Discipline, longevity, career stability, karma resolution, patience, obstacles removal',
            'gemstone': 'Blue Sapphire (Neelam)',
            'deity': 'Lord Shani',
            'wearing': 'Generally worshipped, not worn. Consult astrologer before wearing.'
        },
        'Rahu': {
            'sanskrit_name': 'Rahu Yantra',
            'metal': 'Mixed metal (Ashtadhatu)',
            'mantra': 'Om Bhraam Bhreem Bhraum Sah Rahave Namah',
            'beej_mantra': 'Om Bhraam Bhreem Bhraum Sah Rahave Namah',
            'day': 'Saturday',
            'time': 'Evening or Rahu Kaal',
            'direction': 'Southwest',
            'benefits': 'Foreign connections, sudden gains, material success, technology, innovation',
            'gemstone': 'Hessonite (Gomed)',
            'deity': 'Goddess Durga',
            'wearing': 'Generally worshipped only, not worn as pendant'
        },
        'Ketu': {
            'sanskrit_name': 'Ketu Yantra',
            'metal': 'Mixed metal (Ashtadhatu)',
            'mantra': 'Om Sraam Sreem Sraum Sah Ketave Namah',
            'beej_mantra': 'Om Sraam Sreem Sraum Sah Ketave Namah',
            'day': 'Tuesday or Thursday',
            'time': 'Morning',
            'direction': 'Northwest',
            'benefits': 'Spirituality, moksha, occult knowledge, detachment, enlightenment, past life wisdom',
            'gemstone': "Cat's Eye (Lehsunia)",
            'deity': 'Lord Ganesha',
            'wearing': 'Generally worshipped only, not worn as pendant'
        }
    }
    
    return yantra_info.get(planet, {})