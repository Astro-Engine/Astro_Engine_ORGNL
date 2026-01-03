from datetime import datetime, timedelta
import swisseph as swe
import os

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.getcwd(), 'astro_api', 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Panchottari Dasha System - Standard Years
# Total Cycle: 105 years
PANCHOTTARI_PLANETS = [
    {'name': 'Sun', 'years': 12},
    {'name': 'Mercury', 'years': 13},
    {'name': 'Saturn', 'years': 14},
    {'name': 'Mars', 'years': 15},
    {'name': 'Venus', 'years': 16},
    {'name': 'Moon', 'years': 17},
    {'name': 'Jupiter', 'years': 18}
]

TOTAL_CYCLE_YEARS = 105
NAKSHATRA_SPAN_DEGREES = 13.333333333333334  # 360° / 27 = 13°20'

# 27 Nakshatras (index 0-26)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]


def get_panchottari_nakshatra_lord(nakshatra_index):
    """
    Correct Nakshatra Lord Assignment for Panchottari Dasha
    
    Logic: Count Nakshatras from Anuradha (index 16) to birth Nakshatra, inclusive, zodiacally.
    - If index >= 16: count = index - 16 + 1
    - Else: count = (26 - 16 + 1) + (nakshatra_index + 1) = nakshatra_index + 12
    - Remainder = count % 7 (if 0, set to 7)
    - Map: 1=Sun, 2=Mercury, 3=Saturn, 4=Mars, 5=Venus, 6=Moon, 7=Jupiter
    
    This gives distributed assignment (not consecutive proportional):
    - Sun (4): Anuradha, Shatabhisha, Rohini, Purva Phalguni
    - Mercury (4): Jyeshtha, Purva Bhadrapada, Mrigashira, Uttara Phalguni
    - Saturn (4): Mula, Uttara Bhadrapada, Ardra, Hasta
    - Mars (4): Purva Ashadha, Revati, Punarvasu, Chitra
    - Venus (4): Uttara Ashadha, Ashwini, Pushya, Swati
    - Moon (4): Shravana, Bharani, Ashlesha, Vishakha
    - Jupiter (3): Dhanishta, Krittika, Magha
    """
    seed_index = 16  # Anuradha
    if nakshatra_index >= seed_index:
        count = nakshatra_index - seed_index + 1
    else:
        count = (26 - seed_index + 1) + (nakshatra_index + 1)  # Wrap around
    remainder = count % 7
    if remainder == 0:
        remainder = 7
    lords = ['Sun', 'Mercury', 'Saturn', 'Mars', 'Venus', 'Moon', 'Jupiter']
    return lords[remainder - 1]


def calculate_julian_day_utc(date_str, time_str, timezone_offset):
    """Calculate Julian Day in UTC"""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=timezone_offset)
    hour_decimal = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    julian_day = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    return julian_day


def get_moon_sidereal_longitude(julian_day):
    """
    Calculate Moon's Sidereal Longitude using Lahiri Ayanamsa
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    calc_result = swe.calc_ut(julian_day, swe.MOON)
    position_array = calc_result[0]
    tropical_longitude = position_array[0]
    ayanamsa = swe.get_ayanamsa_ut(julian_day)
    sidereal_longitude = (tropical_longitude - ayanamsa) % 360
    return sidereal_longitude


def get_nakshatra_details(sidereal_longitude):
    """
    Get Nakshatra details from Moon's sidereal longitude
    """
    nakshatra_index = int(sidereal_longitude / NAKSHATRA_SPAN_DEGREES) % 27
    nakshatra_name = NAKSHATRAS[nakshatra_index]
    degrees_traversed = sidereal_longitude % NAKSHATRA_SPAN_DEGREES
    degrees_remaining = NAKSHATRA_SPAN_DEGREES - degrees_traversed
    return {
        'index': nakshatra_index,
        'name': nakshatra_name,
        'degrees_traversed': degrees_traversed,
        'degrees_remaining': degrees_remaining
    }


def get_planet_data(planet_name):
    """Get planet data from list"""
    for planet in PANCHOTTARI_PLANETS:
        if planet['name'] == planet_name:
            return planet
    return None


def get_planet_index(planet_name):
    """Get planet index in the sequence"""
    for i, planet in enumerate(PANCHOTTARI_PLANETS):
        if planet['name'] == planet_name:
            return i
    return 0


def calculate_dasha_balance(planet_name, degrees_traversed):
    """
    Calculate balance of starting dasha
    FORMULA: Balance = Total_Years × (1 - degrees_traversed/13.333)
    """
    planet_data = get_planet_data(planet_name)
    total_years = planet_data['years']
    fraction_traversed = degrees_traversed / NAKSHATRA_SPAN_DEGREES
    balance_years = total_years * (1.0 - fraction_traversed)
    return balance_years


def years_to_ymd(years):
    """Convert decimal years to Years, Months, Days"""
    total_days = years * 365.25
    y = int(years)
    remaining_days = total_days - (y * 365.25)
    m = int(remaining_days / 30.4375)
    d = int(remaining_days - (m * 30.4375))
    return y, m, d


def add_years_to_date(start_date, years):
    """Add decimal years to a date"""
    days = years * 365.25
    return start_date + timedelta(days=days)


def calculate_mahadashas(birth_datetime, starting_planet, balance_years):
    """
    Calculate all Mahadashas
    - First: From birth, with balance years
    - Subsequent: Full years
    """
    mahadashas = []
    current_date = birth_datetime
    starting_index = get_planet_index(starting_planet)
    planet_data = get_planet_data(starting_planet)
    full_years = planet_data['years']
    passed_years = full_years - balance_years
    passed_days = passed_years * 365.25
    maha_start_date = birth_datetime - timedelta(days=passed_days)
    
    # First Mahadasha (display from birth)
    end_date = add_years_to_date(current_date, balance_years)
    y, m, d = years_to_ymd(balance_years)
    mahadashas.append({
        'planet': starting_planet,
        'start_date': current_date.strftime('%d-%m-%Y'),
        'end_date': end_date.strftime('%d-%m-%Y'),
        'years': round(balance_years, 4),
        'display': f"{y}y {m}m {d}d"
    })
    
    current_date = end_date
    current_planet_index = starting_index
    years_covered = balance_years
    
    # Subsequent mahadashas
    while years_covered < TOTAL_CYCLE_YEARS + 20:
        current_planet_index = (current_planet_index + 1) % 7
        planet_data = PANCHOTTARI_PLANETS[current_planet_index]
        planet_years = planet_data['years']
        end_date = add_years_to_date(current_date, planet_years)
        y, m, d = years_to_ymd(planet_years)
        mahadashas.append({
            'planet': planet_data['name'],
            'start_date': current_date.strftime('%d-%m-%Y'),
            'end_date': end_date.strftime('%d-%m-%Y'),
            'years': planet_years,
            'display': f"{y}y {m}m {d}d"
        })
        current_date = end_date
        years_covered += planet_years
    
    return mahadashas, maha_start_date  # Return maha_start_date for first antar calc


def calculate_antardashas(mahadasha_planet, full_maha_years, maha_start_date_str, passed_years=0):
    """
    Calculate Antardashas for a Mahadasha over FULL years
    - Sequence: Starts from mahadasha planet
    - For first maha: Prorate/skip based on passed_years
    """
    antardashas = []
    starting_index = get_planet_index(mahadasha_planet)
    current_date = datetime.strptime(maha_start_date_str, '%d-%m-%Y')
    cumulative_passed = 0.0
    
    for i in range(7):
        planet_index = (starting_index + i) % 7
        planet_data = PANCHOTTARI_PLANETS[planet_index]
        antardasha_full_years = (full_maha_years * planet_data['years']) / TOTAL_CYCLE_YEARS
        
        antar_start = current_date
        antar_end = add_years_to_date(current_date, antardasha_full_years)
        
        if passed_years > 0:
            if cumulative_passed + antardasha_full_years <= passed_years:
                # Fully passed
                cumulative_passed += antardasha_full_years
                current_date = antar_end
                continue
            else:
                # Partial pass
                remaining_passed = passed_years - cumulative_passed
                antar_start = add_years_to_date(antar_start, remaining_passed)
                antardasha_years = antardasha_full_years - remaining_passed
                antar_end = add_years_to_date(antar_start, antardasha_years)
                passed_years = 0  # Done passing
        else:
            antardasha_years = antardasha_full_years
        
        y, m, d = years_to_ymd(antardasha_years)
        antardashas.append({
            'planet': planet_data['name'],
            'start_date': antar_start.strftime('%d-%m-%Y'),
            'end_date': antar_end.strftime('%d-%m-%Y'),
            'years': round(antardasha_years, 4),
            'display': f"{y}y {m}m {d}d"
        })
        current_date = antar_end
    
    return antardashas


def calculate_panchottari_dasha(user_name, birth_date, birth_time, latitude, longitude, timezone_offset):
    """
    Main calculation function for Panchottari Dasha
    
    Args:
        user_name: User's name
        birth_date: Date of birth (YYYY-MM-DD)
        birth_time: Time of birth (HH:MM:SS)
        latitude: Latitude
        longitude: Longitude
        timezone_offset: Timezone offset
        
    Returns:
        Dictionary with user info and panchottari dasha periods
    """
    # Julian Day
    jd = calculate_julian_day_utc(birth_date, birth_time, timezone_offset)
    
    # Moon position
    moon_longitude = get_moon_sidereal_longitude(jd)
    
    # Nakshatra
    nakshatra_info = get_nakshatra_details(moon_longitude)
    
    # Starting planet (correct method)
    starting_planet = get_panchottari_nakshatra_lord(nakshatra_info['index'])
    
    # Balance
    balance_years = calculate_dasha_balance(starting_planet, nakshatra_info['degrees_traversed'])
    balance_y, balance_m, balance_d = years_to_ymd(balance_years)
    
    # Birth datetime
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    
    # Mahadashas (also gets first maha_start_date)
    mahadashas, first_maha_start_date = calculate_mahadashas(birth_datetime, starting_planet, balance_years)
    
    # Antardashas
    for idx, maha in enumerate(mahadashas):
        full_years = get_planet_data(maha['planet'])['years']
        if idx == 0:
            planet_data = get_planet_data(starting_planet)
            passed_years = planet_data['years'] - balance_years
            maha_start_date_str = first_maha_start_date.strftime('%d-%m-%Y')
            maha['antardashas'] = calculate_antardashas(maha['planet'], full_years, maha_start_date_str, passed_years)
        else:
            maha['antardashas'] = calculate_antardashas(maha['planet'], full_years, maha['start_date'])
    
    # Moon sign
    moon_sign_index = int(moon_longitude / 30)
    moon_sign = ZODIAC_SIGNS[moon_sign_index]
    
    # Dasha sequence
    start_idx = get_planet_index(starting_planet)
    dasha_seq = []
    for i in range(7):
        idx = (start_idx + i) % 7
        dasha_seq.append(PANCHOTTARI_PLANETS[idx]['name'][:2])
    dasha_sequence = "-".join(dasha_seq)
    
    # Response
    return {
        'user_name': user_name,
        'birth_details': {
            'date': birth_date,
            'time': birth_time,
            'latitude': latitude,
            'longitude': longitude,
            'timezone_offset': timezone_offset
        },
        'moon_details': {
            'longitude': round(moon_longitude, 4),
            'sign': moon_sign,
            'nakshatra': nakshatra_info['name'],
            'nakshatra_number': nakshatra_info['index'] + 1,
            'nakshatra_lord': starting_planet,
            'degrees_traversed': round(nakshatra_info['degrees_traversed'], 4),
            'degrees_remaining': round(nakshatra_info['degrees_remaining'], 4)
        },
        'panchottari_dasha': {
            'system': 'Panchottari (Moon-based, Standard Years)',
            'total_cycle_years': TOTAL_CYCLE_YEARS,
            'starting_planet': starting_planet,
            'balance_at_birth': {
                'years': round(balance_years, 4),
                'display': f"{balance_y}y {balance_m}m {balance_d}d"
            },
            'dasha_sequence': dasha_sequence,
            'planet_years': {p['name']: p['years'] for p in PANCHOTTARI_PLANETS},
            'mahadashas': mahadashas[:15]
        },
        'calculation_method': {
            'ayanamsa': 'Lahiri',
            'zodiac': 'Sidereal',
            'based_on': 'Moon Nakshatra',
            'house_system': 'Whole Sign',
            'nakshatra_distribution': 'Distributed from Anuradha (4-4-4-4-4-4-3=27)',
            'balance_formula': 'Planet_Years × (1 - degrees_traversed/13.333)',
            'antardasha_formula': '(Full_Maha_Years × Antar_Years) / 105'
        }
    }