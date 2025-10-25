
from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

swe.set_ephe_path('astro_engine/ephe')

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

def local_to_utc(birth_date, birth_time, timezone_offset):
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=float(timezone_offset))
    return utc_dt

def get_julian_day(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)

def calculate_kp_ayanamsa(jd):
    base_ayanamsa = 22 + 22/60 + 43.86/3600  # for 1900 Jan 1
    base_jd = 2415020.5
    years_diff = (jd - base_jd) / 365.2425
    precession_rate = 50.2388475 / 3600
    kp_ayanamsa = base_ayanamsa + years_diff * precession_rate
    return kp_ayanamsa

def calculate_moon_longitude(jd):
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    kp_ayanamsa = calculate_kp_ayanamsa(jd)
    moon_sidereal = (moon_tropical - kp_ayanamsa) % 360
    return moon_sidereal

def get_nakshatra_details(moon_longitude):
    nakshatra_size = 360 / 27
    nakshatra_index = int(moon_longitude / nakshatra_size)
    deg_in_nakshatra = moon_longitude % nakshatra_size
    nakshatra_name = NAKSHATRAS[nakshatra_index]
    ruler = NAKSHATRA_RULERS[nakshatra_index]
    return nakshatra_name, ruler, deg_in_nakshatra, nakshatra_index

def add_years_to_date(start_date, years):
    total_days = years * 365.2425
    whole_days = int(total_days)
    seconds = int((total_days - whole_days) * 86400)
    return start_date + timedelta(days=whole_days, seconds=seconds)

def get_dasha_sequence(start_planet):
    start_idx = DASHA_SEQUENCE.index(start_planet)
    return DASHA_SEQUENCE[start_idx:] + DASHA_SEQUENCE[:start_idx]

def calculate_maha_antar_dasha(user_input):
    birth_date = user_input['birth_date']
    birth_time = user_input['birth_time']
    timezone_offset = float(user_input['timezone_offset'])
    utc_dt = local_to_utc(birth_date, birth_time, timezone_offset)
    jd = get_julian_day(utc_dt)
    current_date = utc_dt
    moon_longitude = calculate_moon_longitude(jd)
    nakshatra_name, ruler, deg_in_nakshatra, nakshatra_index = get_nakshatra_details(moon_longitude)
    nakshatra_size = 360 / 27
    portion_traversed = deg_in_nakshatra / nakshatra_size
    balance_years = DASHA_YEARS[ruler] * (1 - portion_traversed)
    maha_sequence = get_dasha_sequence(ruler)
    dasha_timeline = []

    for i, maha_planet in enumerate(maha_sequence):
        if i == 0:
            maha_years = balance_years
            maha_start_date = current_date
            maha_end_date = add_years_to_date(maha_start_date, maha_years)
            antar_sequence = get_dasha_sequence(maha_planet)
            antar_timeline = []
            antar_date = maha_start_date

            # --- Key Fix: Correct Antar Dasha date chaining for partial Maha Dasha ---
            total_maha_years = DASHA_YEARS[maha_planet]
            elapsed_in_maha = total_maha_years * portion_traversed
            antar_sequence_full = [total_maha_years * DASHA_YEARS[p] / 120.0 for p in antar_sequence]
            cumulative = 0
            found = False
            for j, antar_planet in enumerate(antar_sequence):
                antar_years_full = antar_sequence_full[j]
                if not found and cumulative + antar_years_full > elapsed_in_maha:
                    # This is the running antar at birth
                    elapsed_in_this_antar = elapsed_in_maha - cumulative
                    remaining_years = antar_years_full - elapsed_in_this_antar
                    antar_end = add_years_to_date(antar_date, remaining_years)
                    antar_timeline.append({
                        'planet': antar_planet,
                        'start': antar_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'end': antar_end.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    antar_date = antar_end
                    found = True
                elif found:
                    antar_end = add_years_to_date(antar_date, antar_years_full)
                    antar_timeline.append({
                        'planet': antar_planet,
                        'start': antar_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'end': antar_end.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    antar_date = antar_end
                cumulative += antar_years_full

        else:
            maha_years = DASHA_YEARS[maha_planet]
            maha_start_date = current_date
            maha_end_date = add_years_to_date(maha_start_date, maha_years)
            antar_sequence = get_dasha_sequence(maha_planet)
            antar_durations = [maha_years * DASHA_YEARS[p] / 120.0 for p in antar_sequence]
            antar_timeline = []
            antar_date = maha_start_date
            for j, antar_planet in enumerate(antar_sequence):
                antar_years = antar_durations[j]
                antar_end = add_years_to_date(antar_date, antar_years)
                antar_timeline.append({
                    'planet': antar_planet,
                    'start': antar_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': antar_end.strftime('%Y-%m-%d %H:%M:%S')
                })
                antar_date = antar_end

        dasha_timeline.append({
            'planet': maha_planet,
            'start': maha_start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end': maha_end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'antardashas': antar_timeline
        })
        current_date = maha_end_date
    return {
        'user_name': user_input['user_name'],
        'nakshatra_at_birth': nakshatra_name,
        'nakshatra_ruler': ruler,
        'moon_longitude': round(moon_longitude, 6),
        'deg_in_nakshatra': round(deg_in_nakshatra, 6),
        'dasha_timeline': dasha_timeline
    }