

from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
swe.set_ephe_path('astro_engine/ephe')

# Constants
DASHA_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]
NAKSHATRA_RULERS = DASHA_SEQUENCE * 3
TOTAL_VIMSHOTTARI_DAYS = 120 * 365.2425  # Total Vimshottari cycle in days

def local_to_utc(birth_date, birth_time, timezone_offset):
    """Convert local birth time to UTC."""
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=float(timezone_offset))
    return utc_dt

def get_julian_day(dt):
    """Calculate Julian Day from UTC datetime."""
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)

def jd_to_datetime(jd):
    """Convert Julian Day to Gregorian datetime."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    return datetime(year, month, day, hour_int, minute, second)

def calculate_kp_ayanamsa(jd):
    """Calculate KP Ayanamsa for the given Julian Day."""
    base_ayanamsa = 22 + 22/60 + 43.86/3600  # Ayanamsa for 1900 Jan 1
    base_jd = 2415020.5
    years_diff = (jd - base_jd) / 365.2425
    precession_rate = 50.2388475 / 3600
    kp_ayanamsa = base_ayanamsa + years_diff * precession_rate
    return kp_ayanamsa

def calculate_moon_longitude(jd):
    """Calculate Moon's sidereal longitude using KP Ayanamsa."""
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    kp_ayanamsa = calculate_kp_ayanamsa(jd)
    moon_sidereal = (moon_tropical - kp_ayanamsa) % 360
    return moon_sidereal

def get_nakshatra_details(moon_longitude):
    """Determine Nakshatra, ruler, and degrees traversed."""
    nakshatra_size = 360 / 27  # 13.3333 degrees per Nakshatra
    nakshatra_index = int(moon_longitude / nakshatra_size)
    deg_in_nakshatra = moon_longitude % nakshatra_size
    nakshatra_name = NAKSHATRAS[nakshatra_index]
    ruler = NAKSHATRA_RULERS[nakshatra_index]
    return nakshatra_name, ruler, deg_in_nakshatra, nakshatra_index

def get_vimshottari_sequence(start_planet):
    """Get the Vimshottari sequence starting from the given planet."""
    idx = DASHA_SEQUENCE.index(start_planet)
    return DASHA_SEQUENCE[idx:] + DASHA_SEQUENCE[:idx]

def calculate_pratyantardashas(antar_planet, antar_start_jd, antar_days, birth_jd):
    """Calculate Pratyantardasha periods with precise timing."""
    pratyantar_sequence = get_vimshottari_sequence(antar_planet)
    pratyantar_timeline = []
    
    # Calculate total days for one full Vimshottari cycle (120 years)
    total_cycle_days = sum(DASHA_YEARS.values()) * 365.2425
    
    # Calculate Pratyantardasha durations proportional to Antar Dasha
    pratyantar_durations = [
        (DASHA_YEARS[planet] * 365.2425 * antar_days) / total_cycle_days
        for planet in pratyantar_sequence
    ]
    
    # Determine the Pratyantardasha active at birth
    elapsed_days = birth_jd - antar_start_jd if birth_jd >= antar_start_jd else 0
    cumulative_days = 0
    for i, duration in enumerate(pratyantar_durations):
        cumulative_days += duration
        if cumulative_days > elapsed_days:
            start_idx = i
            break
    else:
        start_idx = 0  # If birth_jd is after all durations, start from first

    # Calculate the start of the active Pratyantardasha
    pratyantar_start_jd = antar_start_jd + sum(pratyantar_durations[:start_idx])
    remaining_days = elapsed_days - sum(pratyantar_durations[:start_idx])
    
    # Adjust for the active Pratyantardasha at birth
    current_jd = pratyantar_start_jd
    if remaining_days > 0:
        first_duration = pratyantar_durations[start_idx] - remaining_days
        if birth_jd >= antar_start_jd:
            pratyantar_timeline.append({
                'planet': pratyantar_sequence[start_idx],
                'start': jd_to_datetime(birth_jd).strftime('%Y-%m-%d %H:%M:%S'),
                'end': jd_to_datetime(birth_jd + first_duration).strftime('%Y-%m-%d %H:%M:%S')
            })
            current_jd = birth_jd + first_duration
            start_idx += 1
    
    # Add subsequent Pratyantardashas
    for i in range(start_idx, len(pratyantar_sequence)):
        planet = pratyantar_sequence[i]
        duration = pratyantar_durations[i]
        end_jd = current_jd + duration
        pratyantar_timeline.append({
            'planet': planet,
            'start': jd_to_datetime(current_jd).strftime('%Y-%m-%d %H:%M:%S'),
            'end': jd_to_datetime(end_jd).strftime('%Y-%m-%d %H:%M:%S')
        })
        current_jd = end_jd
    
    return pratyantar_timeline

def calculate_maha_antar_pratyantar_dasha(user_input):
    """Calculate Vimshottari Dasha periods with precise dates."""
    birth_date = user_input['birth_date']
    birth_time = user_input['birth_time']
    timezone_offset = float(user_input['timezone_offset'])
    utc_dt = local_to_utc(birth_date, birth_time, timezone_offset)
    birth_jd = get_julian_day(utc_dt)
    moon_longitude = calculate_moon_longitude(birth_jd)
    nakshatra_name, ruler, deg_in_nakshatra, _ = get_nakshatra_details(moon_longitude)

    # Calculate Maha Dasha start
    nakshatra_size = 360 / 27
    portion_traversed = deg_in_nakshatra / nakshatra_size
    maha_days_total = DASHA_YEARS[ruler] * 365.2425
    elapsed_maha_days = maha_days_total * portion_traversed
    maha_start_jd = birth_jd - elapsed_maha_days
    maha_sequence = get_vimshottari_sequence(ruler)
    dasha_timeline = []
    current_maha_jd = maha_start_jd

    for maha_planet in maha_sequence:
        maha_days = DASHA_YEARS[maha_planet] * 365.2425
        maha_end_jd = current_maha_jd + maha_days
        if maha_end_jd <= birth_jd:
            current_maha_jd = maha_end_jd
            continue
        
        antar_sequence = get_vimshottari_sequence(maha_planet)
        antar_timeline = []
        current_antar_jd = current_maha_jd

        for antar_planet in antar_sequence:
            antar_days = (DASHA_YEARS[antar_planet] / 120.0) * maha_days
            antar_end_jd = current_antar_jd + antar_days
            if antar_end_jd <= birth_jd:
                current_antar_jd = antar_end_jd
                continue

            pratyantar_timeline = calculate_pratyantardashas(
                antar_planet, current_antar_jd, antar_days, birth_jd
            )
            antar_timeline.append({
                'planet': antar_planet,
                'start': jd_to_datetime(max(current_antar_jd, birth_jd)).strftime('%Y-%m-%d %H:%M:%S'),
                'end': jd_to_datetime(antar_end_jd).strftime('%Y-%m-%d %H:%M:%S'),
                'pratyantardashas': pratyantar_timeline
            })
            current_antar_jd = antar_end_jd

        dasha_timeline.append({
            'planet': maha_planet,
            'start': jd_to_datetime(max(current_maha_jd, birth_jd)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': jd_to_datetime(maha_end_jd).strftime('%Y-%m-%d %H:%M:%S'),
            'antardashas': antar_timeline
        })
        current_maha_jd = maha_end_jd

    return {
        'user_name': user_input['user_name'],
        'nakshatra_at_birth': nakshatra_name,
        'nakshatra_ruler': ruler,
        'moon_longitude': round(moon_longitude, 6),
        'deg_in_nakshatra': round(deg_in_nakshatra, 6),
        'dasha_timeline': dasha_timeline
    }