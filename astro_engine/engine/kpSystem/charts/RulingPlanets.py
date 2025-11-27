# import swisseph as swe
# from datetime import datetime, timedelta

# # Constants
# ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# SIGN_RULERS = {
#     'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 
#     'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 
#     'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
# }
# NAKSHATRAS = [
#     'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 
#     'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 
#     'Vishakha', 'Anuradha', 'Jyeshta', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 
#     'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
# ]
# NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3  # 27 Nakshatras
# DASHA_YEARS = {
#     'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 
#     'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
# }
# NAKSHATRA_SPAN = 360 / 27  # 13.3333 degrees per Nakshatra

# def ruling_get_sign(degree):
#     """Determine the zodiac sign from a given longitude (0-360 degrees)."""
#     sign_index = int(degree / 30) % 12
#     return ZODIAC_SIGNS[sign_index]

# def ruling_get_nakshatra_and_lord(degree):
#     """Determine the Nakshatra and its lord from a given longitude."""
#     nak_index = int(degree / NAKSHATRA_SPAN) % 27
#     nakshatra = NAKSHATRAS[nak_index]
#     lord = NAKSHATRA_LORDS[nak_index]
#     return nakshatra, lord

# def ruling_get_sub_lord(degree):
#     """Calculate the Sub-Lord for a given longitude based on Vimshottari Dasha proportions."""
#     lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
#     dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
#     nak_span = NAKSHATRA_SPAN
#     nak_index = int(degree / nak_span) % 27
#     nak_lord = NAKSHATRA_LORDS[nak_index]
#     start_index = lords.index(nak_lord)
#     sub_lord_sequence = (lords * 2)[start_index:start_index + 9]
#     sub_spans = [(dasha_years[(start_index + i) % 9] / 120 * nak_span) for i in range(9)]
#     cumulative_spans = [0] + [sum(sub_spans[:i + 1]) for i in range(9)]
#     position_in_nak = degree % nak_span
#     for i in range(9):
#         if cumulative_spans[i] <= position_in_nak < cumulative_spans[i + 1]:
#             return sub_lord_sequence[i]
#     return sub_lord_sequence[-1]  # Fallback for edge case

# def ruling_calculate_jd(birth_date, birth_time, timezone_offset):
#     """Calculate Julian Day from birth date, time, and timezone offset."""
#     local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
#     utc_dt = local_dt - timedelta(hours=timezone_offset)
#     hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
#     jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
#     return jd, utc_dt

# def ruling_calculate_ascendant_and_cusps(jd, latitude, longitude):
#     """Calculate Ascendant and house cusps using Placidus system."""
#     swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
#     cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
#     ascendant = cusps[0]  # Ascendant longitude (float)
#     return ascendant, cusps

# def ruling_calculate_planet_positions(jd):
#     """Calculate sidereal planetary positions."""
#     sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
#     moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
#     rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
#     ketu_pos = (rahu_pos + 180) % 360  # Ketu is 180° opposite Rahu (float)
#     return sun_pos, moon_pos, rahu_pos, ketu_pos

# def ruling_get_day_lord(utc_dt):
#     """Determine the Day Lord based on UTC date."""
#     day_of_week = utc_dt.weekday()  # 0 = Monday, 6 = Sunday
#     day_lord = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun'][day_of_week]
#     return day_lord

# def ruling_get_details(longitude):
#     """Get sign, rashi lord, nakshatra, star lord, sub lord for a longitude."""
#     sign = ruling_get_sign(longitude)
#     rashi_lord = SIGN_RULERS[sign]
#     nakshatra, star_lord = ruling_get_nakshatra_and_lord(longitude)
#     sub_lord = ruling_get_sub_lord(longitude)
#     return sign, rashi_lord, nakshatra, star_lord, sub_lord

# def ruling_compile_core_rp(lagna_details, moon_details, day_lord):
#     """Compile core Ruling Planets."""
#     core_rp = set([
#         lagna_details['rashi_lord'], lagna_details['star_lord'], lagna_details['sub_lord'],
#         moon_details['rashi_lord'], moon_details['star_lord'], moon_details['sub_lord'],
#         day_lord
#     ])
#     return core_rp

# def ruling_check_rahu_ketu(rahu_pos, ketu_pos, core_rp):
#     """Include Rahu/Ketu if their nakshatra lords are in core RP."""
#     rahu_nak_lord = ruling_get_nakshatra_and_lord(rahu_pos)[1]
#     ketu_nak_lord = ruling_get_nakshatra_and_lord(ketu_pos)[1]
#     if rahu_nak_lord in core_rp:
#         core_rp.add('Rahu')
#     if ketu_nak_lord in core_rp:
#         core_rp.add('Ketu')
#     return core_rp

# def ruling_calculate_fortuna(ascendant, moon_pos, sun_pos):
#     """Calculate Fortuna (Part of Fortune)."""
#     return (ascendant + moon_pos - sun_pos) % 360

# def ruling_calculate_balance_of_dasha(moon_pos, moon_star_lord):
#     """Calculate Balance of Dasha based on Moon's position."""
#     nak_start = int(moon_pos / NAKSHATRA_SPAN) * NAKSHATRA_SPAN
#     position_in_nak = moon_pos - nak_start
#     fraction_passed = position_in_nak / NAKSHATRA_SPAN
#     fraction_remaining = 1 - fraction_passed
#     dasha_lord = moon_star_lord
#     balance_years = fraction_remaining * DASHA_YEARS[dasha_lord]
#     return dasha_lord, balance_years




"""
KP Ruling Planets - Calculation Module
Contains all calculation functions for KP astrology ruling planets analysis
"""

from datetime import datetime
import swisseph as swe
import math

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

SIGN_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
              'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashirsha', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

NAK_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3

PLANET_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

DASA_PERIODS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DAY_LORDS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']

PLANET_IDS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE  # Ketu is 180° opposite to Rahu
}

def get_kp_ayanamsa(jd):
    """
    Calculate KP New Ayanamsa (KP Ayanamsa)
    KP uses a slightly different ayanamsa than Lahiri
    """
    # KP Old Ayanamsa: swe.SIDM_KRISHNAMURTI
    # KP New Ayanamsa is a variation
    # For precise KP calculations, we use Krishnamurti ayanamsa
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return ayanamsa

def get_julian_day(birth_date, birth_time, timezone_offset):
    """Convert date, time and timezone to Julian Day (UT)"""
    date_parts = birth_date.split('-')
    time_parts = birth_time.split(':')
    
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    second = int(time_parts[2])
    
    # Convert to decimal hours
    decimal_hour = hour + minute/60.0 + second/3600.0
    
    # Subtract timezone offset to get UTC
    decimal_hour_ut = decimal_hour - timezone_offset
    
    # Calculate Julian Day
    jd = swe.julday(year, month, day, decimal_hour_ut)
    
    return jd

def get_planet_position(jd, planet_id, is_ketu=False):
    """Get sidereal position of a planet"""
    if is_ketu:
        # Ketu is 180° opposite to Rahu
        result = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
        longitude = (result[0][0] + 180) % 360
        speed = -result[0][3]  # Ketu moves opposite to Rahu
    else:
        result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
        longitude = result[0][0]
        speed = result[0][3]
    
    is_retrograde = speed < 0
    
    return longitude, is_retrograde

def get_ascendant(jd, latitude, longitude):
    """Calculate Ascendant using Placidus house system"""
    # Placidus house system (P)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
    
    # Get tropical ascendant
    asc_tropical = ascmc[0]
    
    # Convert to sidereal
    ayanamsa = get_kp_ayanamsa(jd)
    asc_sidereal = (asc_tropical - ayanamsa) % 360
    
    return asc_sidereal

def get_sign_info(longitude):
    """Get sign number and sign name from longitude"""
    sign_num = int(longitude / 30)
    sign_name = SIGNS[sign_num % 12]
    sign_lord = SIGN_LORDS[sign_num % 12]
    degree_in_sign = longitude % 30
    
    return sign_num, sign_name, sign_lord, degree_in_sign

def get_nakshatra_info(longitude):
    """Get nakshatra information from longitude"""
    # Each nakshatra is 13°20' = 13.333...°
    nak_span = 360 / 27
    nak_num = int(longitude / nak_span)
    nak_name = NAKSHATRAS[nak_num % 27]
    nak_lord = NAK_LORDS[nak_num % 27]
    
    # Position within nakshatra
    degree_in_nak = longitude % nak_span
    
    # Nakshatra pada (each nakshatra has 4 padas)
    pada_num = int(degree_in_nak / (nak_span / 4)) + 1
    
    return nak_num, nak_name, nak_lord, pada_num, degree_in_nak

def get_sub_lord(longitude):
    """
    Calculate KP Sub-Lord using precise method
    Each nakshatra (13°20' = 800 arcminutes) is divided into 9 subs
    proportional to Vimshottari Dasa periods
    """
    nak_span_deg = 360 / 27  # 13.333... degrees
    nak_span_arcmin = nak_span_deg * 60  # 800 arcminutes
    
    # Get nakshatra number and position within nakshatra
    nak_num = int(longitude / nak_span_deg)
    position_in_nak_deg = longitude % nak_span_deg
    position_in_nak_arcmin = position_in_nak_deg * 60
    
    # Get nakshatra lord (starting sub-lord)
    nak_lord = NAK_LORDS[nak_num % 27]
    
    # Create sub-lord sequence starting from nakshatra lord
    start_idx = PLANET_ORDER.index(nak_lord)
    sub_lord_sequence = PLANET_ORDER[start_idx:] + PLANET_ORDER[:start_idx]
    
    # Calculate cumulative boundaries for each sub
    cumulative_arcmin = 0
    sub_lord = None
    
    for planet in sub_lord_sequence:
        # Calculate sub length in arcminutes
        sub_length_arcmin = (DASA_PERIODS[planet] / 120) * nak_span_arcmin
        
        if position_in_nak_arcmin < cumulative_arcmin + sub_length_arcmin:
            sub_lord = planet
            break
        
        cumulative_arcmin += sub_length_arcmin
    
    # Fallback (should never reach here)
    if sub_lord is None:
        sub_lord = sub_lord_sequence[-1]
    
    return sub_lord

def get_day_lord(jd):
    """Get day lord based on weekday"""
    # Convert JD to datetime
    year, month, day, hour = swe.revjul(jd)
    dt = datetime(year, month, day, int(hour))
    weekday = dt.weekday()  # Monday=0, Sunday=6
    
    return DAY_LORDS[weekday]

def format_longitude(longitude):
    """Format longitude as Sign DD°MM'SS\""""
    sign_num = int(longitude / 30)
    degree_in_sign = longitude % 30
    
    degrees = int(degree_in_sign)
    minutes = int((degree_in_sign - degrees) * 60)
    seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
    
    return f"{SIGNS[sign_num]} {degrees:02d}°{minutes:02d}'{seconds:02d}\""

def calculate_ruling_planets(data):
    """Main calculation function for Ruling Planets"""
    try:
        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # Calculate Julian Day
        jd = get_julian_day(birth_date, birth_time, timezone_offset)
        
        # Set sidereal mode with KP Ayanamsa
        ayanamsa = get_kp_ayanamsa(jd)
        
        # Get Day Lord
        day_lord = get_day_lord(jd)
        
        # Get Moon position
        moon_longitude, moon_retrograde = get_planet_position(jd, swe.MOON)
        moon_sign_num, moon_sign_name, moon_sign_lord, moon_deg_in_sign = get_sign_info(moon_longitude)
        moon_nak_num, moon_nak_name, moon_nak_lord, moon_pada, moon_deg_in_nak = get_nakshatra_info(moon_longitude)
        moon_sub_lord = get_sub_lord(moon_longitude)
        
        # Get Ascendant (Lagna)
        lagna_longitude = get_ascendant(jd, latitude, longitude)
        lagna_sign_num, lagna_sign_name, lagna_sign_lord, lagna_deg_in_sign = get_sign_info(lagna_longitude)
        lagna_nak_num, lagna_nak_name, lagna_nak_lord, lagna_pada, lagna_deg_in_nak = get_nakshatra_info(lagna_longitude)
        lagna_sub_lord = get_sub_lord(lagna_longitude)
        
        # Get all planets positions with retrograde status
        planets_data = {}
        for planet_name, planet_id in PLANET_IDS.items():
            if planet_name == 'Ketu':
                planet_long, planet_retro = get_planet_position(jd, planet_id, is_ketu=True)
            else:
                planet_long, planet_retro = get_planet_position(jd, planet_id)
            
            p_sign_num, p_sign_name, p_sign_lord, p_deg_in_sign = get_sign_info(planet_long)
            p_nak_num, p_nak_name, p_nak_lord, p_pada, p_deg_in_nak = get_nakshatra_info(planet_long)
            p_sub_lord = get_sub_lord(planet_long)
            
            planets_data[planet_name] = {
                'longitude': round(planet_long, 6),
                'formatted_longitude': format_longitude(planet_long),
                'sign': p_sign_name,
                'sign_lord': p_sign_lord,
                'nakshatra': p_nak_name,
                'nakshatra_lord': p_nak_lord,
                'nakshatra_pada': p_pada,
                'sub_lord': p_sub_lord,
                'is_retrograde': planet_retro
            }
        
        # Compile Ruling Planets (7 components)
        ruling_planets_components = {
            '1_day_lord': day_lord,
            '2_lagna_sign_lord': lagna_sign_lord,
            '3_lagna_star_lord': lagna_nak_lord,
            '4_lagna_sub_lord': lagna_sub_lord,
            '5_moon_sign_lord': moon_sign_lord,
            '6_moon_star_lord': moon_nak_lord,
            '7_moon_sub_lord': moon_sub_lord
        }
        
        # Strength order (strongest to weakest)
        strength_order = [
            lagna_sub_lord,      # Strongest
            lagna_nak_lord,
            lagna_sign_lord,
            moon_sub_lord,
            moon_nak_lord,
            moon_sign_lord,
            day_lord             # Weakest
        ]
        
        # Remove duplicates while preserving order
        unique_ruling_planets = []
        seen = set()
        for planet in strength_order:
            if planet not in seen:
                unique_ruling_planets.append(planet)
                seen.add(planet)
        
        # Prepare response
        result = {
            'status': 'success',
            'user_name': user_name,
            'input': {
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': timezone_offset
            },
            'ayanamsa': {
                'type': 'KP New Ayanamsa (Krishnamurti)',
                'value': round(ayanamsa, 6)
            },
            'julian_day': round(jd, 6),
            'lagna': {
                'longitude': round(lagna_longitude, 6),
                'formatted_longitude': format_longitude(lagna_longitude),
                'sign': lagna_sign_name,
                'sign_lord': lagna_sign_lord,
                'nakshatra': lagna_nak_name,
                'nakshatra_lord': lagna_nak_lord,
                'nakshatra_pada': lagna_pada,
                'sub_lord': lagna_sub_lord
            },
            'moon': {
                'longitude': round(moon_longitude, 6),
                'formatted_longitude': format_longitude(moon_longitude),
                'sign': moon_sign_name,
                'sign_lord': moon_sign_lord,
                'nakshatra': moon_nak_name,
                'nakshatra_lord': moon_nak_lord,
                'nakshatra_pada': moon_pada,
                'sub_lord': moon_sub_lord,
                'is_retrograde': moon_retrograde
            },
            'ruling_planets': {
                'components': ruling_planets_components,
                'unique_planets_by_strength': unique_ruling_planets,
                'strength_order_explanation': {
                    '1_strongest': 'Lagna Sub Lord',
                    '2': 'Lagna Star Lord',
                    '3': 'Lagna Sign Lord',
                    '4': 'Moon Sub Lord',
                    '5': 'Moon Star Lord',
                    '6': 'Moon Sign Lord',
                    '7_weakest': 'Day Lord'
                }
            },
            'all_planets': planets_data
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
