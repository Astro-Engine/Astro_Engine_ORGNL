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
YEAR_LENGTH = 365.2425  # Tropical year length

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
    base_ayanamsa = 22 + 22/60 + 43.86/3600  # for 1900 Jan 1
    base_jd = 2415020.5
    years_diff = (jd - base_jd) / YEAR_LENGTH
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
    nakshatra_size = 360 / 27  # 13.3333 degrees
    nakshatra_index = int(moon_longitude / nakshatra_size)
    deg_in_nakshatra = moon_longitude % nakshatra_size
    nakshatra_name = NAKSHATRAS[nakshatra_index]
    ruler = NAKSHATRA_RULERS[nakshatra_index]
    return nakshatra_name, ruler, deg_in_nakshatra, nakshatra_index

def get_vimshottari_sequence(start_planet):
    """Get the Vimshottari sequence starting from the given planet."""
    idx = DASHA_SEQUENCE.index(start_planet)
    return DASHA_SEQUENCE[idx:] + DASHA_SEQUENCE[:idx]

def calculate_sookshma_dasha(pratyantar_planet, pratyantar_start_jd, pratyantar_days, birth_jd):
    """Calculate Sookshma Dasha periods within a Pratyantardasha."""
    sookshma_sequence = get_vimshottari_sequence(pratyantar_planet)
    total_vimshottari_years = 120.0
    sookshma_timeline = []
    sookshma_current_jd = pratyantar_start_jd

    for sookshma_planet in sookshma_sequence:
        sookshma_days = (DASHA_YEARS[sookshma_planet] / total_vimshottari_years) * pratyantar_days
        sookshma_end_jd = sookshma_current_jd + sookshma_days
        if sookshma_end_jd > birth_jd:
            sookshma_timeline.append({
                'planet': sookshma_planet,
                'start': jd_to_datetime(max(sookshma_current_jd, birth_jd)).strftime('%Y-%m-%d %H:%M:%S'),
                'end': jd_to_datetime(sookshma_end_jd).strftime('%Y-%m-%d %H:%M:%S')
            })
        sookshma_current_jd = sookshma_end_jd
    return sookshma_timeline

def calculate_pratyantardashas(antar_planet, antar_start_jd, antar_days, birth_jd):
    """Calculate Pratyantardasha periods within an Antar Dasha."""
    pratyantar_sequence = get_vimshottari_sequence(antar_planet)
    total_vimshottari_years = 120.0
    pratyantar_timeline = []
    pratyantar_current_jd = antar_start_jd

    for pratyantar_planet in pratyantar_sequence:
        pratyantar_days = (DASHA_YEARS[pratyantar_planet] / total_vimshottari_years) * antar_days
        pratyantar_end_jd = pratyantar_current_jd + pratyantar_days
        if pratyantar_end_jd > birth_jd:
            sookshma_timeline = calculate_sookshma_dasha(pratyantar_planet, pratyantar_current_jd, pratyantar_days, birth_jd)
            pratyantar_timeline.append({
                'planet': pratyantar_planet,
                'start': jd_to_datetime(max(pratyantar_current_jd, birth_jd)).strftime('%Y-%m-%d %H:%M:%S'),
                'end': jd_to_datetime(pratyantar_end_jd).strftime('%Y-%m-%d %H:%M:%S'),
                'sookshma_dasha': sookshma_timeline
            })
        pratyantar_current_jd = pratyantar_end_jd
    return pratyantar_timeline

def calculate_maha_antar_pratyantar_sooksha_dashas(user_input):
    """Calculate Vimshottari Dasha periods including Sookshma Dasha."""
    birth_date = user_input['birth_date']
    birth_time = user_input['birth_time']
    timezone_offset = float(user_input['timezone_offset'])
    utc_dt = local_to_utc(birth_date, birth_time, timezone_offset)
    birth_jd = get_julian_day(utc_dt)
    moon_longitude = calculate_moon_longitude(birth_jd)
    nakshatra_name, ruler, deg_in_nakshatra, _ = get_nakshatra_details(moon_longitude)

    nakshatra_size = 360 / 27
    portion_traversed = deg_in_nakshatra / nakshatra_size
    maha_years = DASHA_YEARS[ruler]
    elapsed_years = maha_years * portion_traversed
    balance_years = maha_years - elapsed_years
    maha_start_jd = birth_jd - (elapsed_years * YEAR_LENGTH)
    maha_sequence = get_vimshottari_sequence(ruler)
    dasha_timeline = []
    current_jd = maha_start_jd

    for i, maha_planet in enumerate(maha_sequence):
        maha_days = DASHA_YEARS[maha_planet] * YEAR_LENGTH
        maha_end_jd = current_jd + maha_days
        antar_sequence = get_vimshottari_sequence(maha_planet)
        antar_timeline = []
        antar_current_jd = current_jd

        for antar_planet in antar_sequence:
            antar_days = (DASHA_YEARS[antar_planet] / 120.0) * DASHA_YEARS[maha_planet] * YEAR_LENGTH
            antar_end_jd = antar_current_jd + antar_days
            if antar_end_jd > birth_jd:
                pratyantar_timeline = calculate_pratyantardashas(antar_planet, antar_current_jd, antar_days, birth_jd)
                antar_timeline.append({
                    'planet': antar_planet,
                    'start': jd_to_datetime(max(antar_current_jd, birth_jd)).strftime('%Y-%m-%d %H:%M:%S'),
                    'end': jd_to_datetime(antar_end_jd).strftime('%Y-%m-%d %H:%M:%S'),
                    'pratyantardashas': pratyantar_timeline
                })
            antar_current_jd = antar_end_jd

        dasha_timeline.append({
            'planet': maha_planet,
            'start': jd_to_datetime(current_jd if i > 0 else birth_jd).strftime('%Y-%m-%d %H:%M:%S'),
            'end': jd_to_datetime(maha_end_jd).strftime('%Y-%m-%d %H:%M:%S'),
            'antardashas': antar_timeline
        })
        current_jd = maha_end_jd

    return {
        'user_name': user_input['user_name'],
        'nakshatra_at_birth': nakshatra_name,
        'nakshatra_ruler': ruler,
        'moon_longitude': round(moon_longitude, 6),
        'deg_in_nakshatra': round(deg_in_nakshatra, 6),
        'dasha_timeline': dasha_timeline
    }
