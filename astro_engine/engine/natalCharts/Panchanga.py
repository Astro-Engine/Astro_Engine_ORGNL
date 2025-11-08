# """
# PANCHANGA CALCULATIONS MODULE
# All astronomical calculations for Panchanga using Skyfield and Swiss Ephemeris
# """

# import swisseph as swe
# import math
# import datetime
# import pytz
# from typing import Dict, Optional
# import os

# # Try to import Skyfield
# try:
#     from skyfield import api, almanac
#     SKYFIELD_AVAILABLE = True
#     print("✓ Skyfield available - EXACT calculations enabled")
# except ImportError:
#     SKYFIELD_AVAILABLE = False
#     print("⚠️ Skyfield not available - install with: pip install skyfield")

# # Configuration
# SWISS_EPHE_PATH = "astro_api/ephe"
# LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# # Initialize Skyfield (if available)
# if SKYFIELD_AVAILABLE:
#     try:
#         ts_global = api.load.timescale()
#         eph_global = api.load('de421.bsp')
#         print("✓ Skyfield ephemeris loaded (JPL DE421)")
#     except Exception as e:
#         print(f"⚠️ Skyfield load error: {e}")
#         SKYFIELD_AVAILABLE = False

# def calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str):
#     """
#     Calculate EXACT moon rise/set using Skyfield
    
#     Returns times matching Drik Panchang accuracy (±1-2 minutes)
#     """
#     if not SKYFIELD_AVAILABLE:
#         return None
    
#     try:
#         from datetime import datetime as dt, timedelta
        
#         # Parse datetime
#         tz = pytz.timezone(timezone_str)
#         dt_str = f"{date_str} {time_str}"
#         dt_local = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         dt_local = tz.localize(dt_local)
        
#         # Observer location
#         location = api.wgs84.latlon(latitude, longitude)
        
#         # Search window
#         dt_start = dt_local.replace(hour=0, minute=0, second=0)
#         dt_end = dt_start + timedelta(days=2)
        
#         t0 = ts_global.from_datetime(dt_start)
#         t1 = ts_global.from_datetime(dt_end)
        
#         # Calculate moon events
#         moon = eph_global['moon']
#         f = almanac.risings_and_settings(eph_global, moon, location)
#         times, events = almanac.find_discrete(t0, t1, f)
        
#         moonrise = None
#         moonset = None
#         target_date = dt_local.date()
        
#         for time, event in zip(times, events):
#             time_utc = time.utc_datetime()
#             time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
#             if time_local.date() == target_date:
#                 if event == 1 and moonrise is None:  # Rise
#                     moonrise = time_local
#                 elif event == 0 and moonset is None:  # Set
#                     moonset = time_local
#             elif time_local.date() == target_date + timedelta(days=1) and time_local.hour < 12:
#                 if event == 0 and moonset is None:
#                     moonset = time_local
        
#         if moonrise and moonset:
#             return {
#                 "moonrise": moonrise.strftime("%H:%M:%S"),
#                 "moonset": moonset.strftime("%H:%M:%S"),
#                 "method": "skyfield_exact"
#             }
        
#         return None
        
#     except Exception as e:
#         print(f"Skyfield moon error: {e}")
#         return None

# def calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str):
#     """Calculate EXACT sun rise/set using Skyfield"""
#     if not SKYFIELD_AVAILABLE:
#         return None
    
#     try:
#         from datetime import datetime as dt, timedelta
        
#         tz = pytz.timezone(timezone_str)
#         dt_str = f"{date_str} {time_str}"
#         dt_local = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         dt_local = tz.localize(dt_local)
        
#         location = api.wgs84.latlon(latitude, longitude)
        
#         dt_start = dt_local.replace(hour=0, minute=0, second=0)
#         dt_end = dt_start + timedelta(days=1)
        
#         t0 = ts_global.from_datetime(dt_start)
#         t1 = ts_global.from_datetime(dt_end)
        
#         sun = eph_global['sun']
#         f = almanac.risings_and_settings(eph_global, sun, location)
#         times, events = almanac.find_discrete(t0, t1, f)
        
#         sunrise = None
#         sunset = None
        
#         for time, event in zip(times, events):
#             time_utc = time.utc_datetime()
#             time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
#             if event == 1:  # Rise
#                 sunrise = time_local
#             elif event == 0:  # Set
#                 sunset = time_local
        
#         if sunrise and sunset:
#             return {
#                 "sunrise": sunrise.strftime("%H:%M:%S"),
#                 "sunset": sunset.strftime("%H:%M:%S"),
#                 "method": "skyfield_exact"
#             }
        
#         return None
        
#     except Exception as e:
#         print(f"Skyfield sun error: {e}")
#         return None

# def calculate_panchanga_elements(date_str, time_str, timezone_str):
#     """Calculate Panchanga elements using Swiss Ephemeris"""
    
#     # Initialize Swiss Ephemeris
#     if not os.path.exists(SWISS_EPHE_PATH):
#         os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
#     swe.set_ephe_path(SWISS_EPHE_PATH)
#     swe.set_sid_mode(LAHIRI_AYANAMSA)
    
#     # Parse datetime
#     tz = pytz.timezone(timezone_str)
#     dt_str = f"{date_str} {time_str}"
#     dt_naive = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#     dt_local = tz.localize(dt_naive)
#     dt_utc = dt_local.astimezone(pytz.UTC)
    
#     # Calculate Julian Day
#     jd = swe.julday(
#         dt_utc.year, dt_utc.month, dt_utc.day,
#         dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
#     )
    
#     # Get planetary positions
#     flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
#     sun_result = swe.calc_ut(jd, swe.SUN, flags)
#     moon_result = swe.calc_ut(jd, swe.MOON, flags)
    
#     sun_lon = sun_result[0][0] % 360.0
#     moon_lon = moon_result[0][0] % 360.0
    
#     # Calculate elements
#     phase_angle = (moon_lon - sun_lon) % 360.0
    
#     # Tithi
#     tithi_num = int(phase_angle / 12) + 1
#     tithi_progress = (phase_angle % 12) / 12 * 100
#     paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
#     # Nakshatra
#     nak_num = int(moon_lon / 13.333333) + 1
#     nak_progress = (moon_lon % 13.333333) / 13.333333
#     pada = int(nak_progress * 4) + 1
    
#     # Yoga
#     yoga_sum = (sun_lon + moon_lon) % 360.0
#     yoga_num = int(yoga_sum / 13.333333) + 1
    
#     # Karana
#     karana_num = int(phase_angle / 6) + 1
    
#     # Vara
#     weekday = dt_local.weekday()
#     vara_num = (weekday + 1) % 7 + 1
    
#     NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
#                   "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
#                   "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
#                   "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
#                   "Uttara Bhadrapada", "Revati"]
    
#     TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
#               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
#               "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
#               "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
#               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
#               "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
    
#     YOGAS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
#              "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
#              "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
#              "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    
#     KARANAS_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
#     KARANAS_FIX = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
    
#     VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
#     # Karana logic (corrected)
#     half_tithi_idx = int(phase_angle / 6)
#     if half_tithi_idx == 0:
#         karana_name = "Kimstughna"
#         karana_type = "fixed"
#     elif half_tithi_idx >= 57:
#         karana_name = KARANAS_FIX[min(2, half_tithi_idx - 57)]
#         karana_type = "fixed"
#     else:
#         karana_name = KARANAS_MOV[(half_tithi_idx - 1) % 7]
#         karana_type = "movable"
    
#     return {
#         "tithi": {
#             "number": tithi_num,
#             "name": TITHIS[tithi_num - 1],
#             "paksha": paksha,
#             "progress_percent": round(tithi_progress, 2)
#         },
#         "nakshatra": {
#             "number": nak_num,
#             "name": NAKSHATRAS[nak_num - 1] if nak_num <= 27 else "Revati",
#             "pada": pada,
#             "progress_percent": round(nak_progress * 100, 2)
#         },
#         "yoga": {
#             "number": yoga_num,
#             "name": YOGAS[yoga_num - 1] if yoga_num <= 27 else "Vaidhriti",
#             "progress_percent": round((yoga_sum % 13.333333) / 13.333333 * 100, 2)
#         },
#         "karana": {
#             "number": karana_num,
#             "name": karana_name,
#             "type": karana_type,
#             "progress_percent": round((phase_angle % 6) / 6 * 100, 2)
#         },
#         "vara": {
#             "number": vara_num,
#             "name": VARAS[vara_num - 1]
#         }
#     }





"""
PANCHANGA CALCULATIONS MODULE
==============================
All calculation functions for Panchanga, Muhurat, Murtha, and Varjyam

This module contains pure calculation logic without Flask dependencies.
Import this into your API file to use the functions.

Dependencies:
    pip install skyfield pyswisseph pytz
"""

import swisseph as swe
import datetime
import pytz
from typing import Dict, Optional, List, Tuple
from datetime import timedelta
import os

# Try to import Skyfield
try:
    from skyfield import api, almanac
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

# Configuration
SWISS_EPHE_PATH = "astro_api/ephe"
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Initialize Skyfield globals (if available)
ts_global = None
eph_global = None

if SKYFIELD_AVAILABLE:
    try:
        ts_global = api.load.timescale()
        eph_global = api.load('de421.bsp')
    except Exception as e:
        print(f"⚠️ Skyfield load error: {e}")
        SKYFIELD_AVAILABLE = False

# ============================================================================
# MURTHA DATABASE - Complete 30 Murthas with Deities and Nature
# ============================================================================

MURTHA_DATABASE = {
    1: {"name": "Rudra", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    2: {"name": "Mahendra", "deity": "Indra", "nature": "Shubha", "quality": "Auspicious"},
    3: {"name": "Dhata", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    4: {"name": "Raudra", "deity": "Rudra", "nature": "Ashubha", "quality": "Inauspicious"},
    5: {"name": "Kala", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    6: {"name": "Vaivasvata", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    7: {"name": "Ghora", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    8: {"name": "Sarpa", "deity": "Serpents", "nature": "Ashubha", "quality": "Inauspicious"},
    9: {"name": "Amrita", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
    10: {"name": "Maitra", "deity": "Mitra", "nature": "Shubha", "quality": "Auspicious"},
    11: {"name": "Pitri", "deity": "Ancestors", "nature": "Ashubha", "quality": "Inauspicious"},
    12: {"name": "Kala", "deity": "Kali", "nature": "Ashubha", "quality": "Inauspicious"},
    13: {"name": "Sarva", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    14: {"name": "Bhaga", "deity": "Bhaga Deva", "nature": "Shubha", "quality": "Auspicious"},
    15: {"name": "Aryaman", "deity": "Aryaman", "nature": "Shubha", "quality": "Auspicious"},
    16: {"name": "Girisha", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    17: {"name": "Ajapada", "deity": "Ajapada", "nature": "Ashubha", "quality": "Inauspicious"},
    18: {"name": "Ahirbudhnya", "deity": "Ahirbudhnya", "nature": "Ashubha", "quality": "Inauspicious"},
    19: {"name": "Pushya", "deity": "Brihaspati", "nature": "Shubha", "quality": "Most Auspicious"},
    20: {"name": "Ashvini", "deity": "Ashvini Kumaras", "nature": "Shubha", "quality": "Auspicious"},
    21: {"name": "Yama", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    22: {"name": "Agni", "deity": "Agni", "nature": "Ashubha", "quality": "Inauspicious"},
    23: {"name": "Vidhatr", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    24: {"name": "Kanda", "deity": "Kanda", "nature": "Ashubha", "quality": "Inauspicious"},
    25: {"name": "Aditi", "deity": "Aditi", "nature": "Shubha", "quality": "Auspicious"},
    26: {"name": "Jiva", "deity": "Brihaspati", "nature": "Shubha", "quality": "Auspicious"},
    27: {"name": "Vishnu", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
    28: {"name": "Dyumani", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    29: {"name": "Dhatri", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    30: {"name": "Tvastr", "deity": "Tvashta", "nature": "Ashubha", "quality": "Inauspicious"}
}

# ============================================================================
# CORRECTED PERIOD MAPPINGS
# ============================================================================

RAHU_KAAL_PERIODS = {
    0: 1, 1: 2, 2: 6, 3: 4, 4: 5, 5: 2, 6: 3
}

YAMAGANDA_PERIODS = {
    0: 4, 1: 3, 2: 1, 3: 2, 4: 0, 5: 5, 6: 6
}

GULIKA_PERIODS = {
    0: 6, 1: 4, 2: 5, 3: 3, 4: 2, 5: 0, 6: 1
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_murtha_details(murtha_number: int) -> Dict:
    """Get deity, nature, and quality for given Murtha number (1-30)"""
    return MURTHA_DATABASE.get(murtha_number, {
        "name": "Unknown",
        "deity": "Unknown",
        "nature": "Unknown",
        "quality": "Unknown"
    })

def format_time(dt: datetime.datetime) -> str:
    """Format datetime to HH:MM:SS string"""
    return dt.strftime("%H:%M:%S")

def add_minutes(dt: datetime.datetime, minutes: float) -> datetime.datetime:
    """Add minutes to datetime"""
    return dt + timedelta(minutes=minutes)

def jd_to_datetime(jd: float, timezone_str: str) -> datetime.datetime:
    """Convert Julian Day to datetime in specified timezone"""
    year, month, day, hour_fraction = swe.revjul(jd)
    hour = int(hour_fraction)
    minute_fraction = (hour_fraction - hour) * 60
    minute = int(minute_fraction)
    second = int((minute_fraction - minute) * 60)
    dt_utc = datetime.datetime(int(year), int(month), int(day), hour, minute, second)
    dt_utc = pytz.UTC.localize(dt_utc)
    tz = pytz.timezone(timezone_str)
    dt_local = dt_utc.astimezone(tz)
    return dt_local

# ============================================================================
# NAKSHATRA END TIME CALCULATION
# ============================================================================

def calculate_nakshatra_end_time(jd_start: float, current_nak_num: int, 
                                 current_moon_lon: float) -> Optional[float]:
    """Calculate EXACT time when current nakshatra ends"""
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    nakshatra_start_lon = (current_nak_num - 1) * 13.33333333
    nakshatra_end_lon = current_nak_num * 13.33333333
    
    if current_nak_num == 27:
        nakshatra_end_lon = 360.0
    
    print(f"\n🔍 Searching for Nakshatra #{current_nak_num} end time...")
    print(f"   Current Moon: {current_moon_lon:.4f}°")
    print(f"   Nakshatra range: {nakshatra_start_lon:.4f}° - {nakshatra_end_lon:.4f}°")
    print(f"   Looking for Moon to reach: {nakshatra_end_lon:.4f}°")
    
    degrees_remaining = nakshatra_end_lon - current_moon_lon
    if degrees_remaining < 0:
        degrees_remaining += 360.0
    
    moon_speed_per_day = 13.176
    approx_days_remaining = degrees_remaining / moon_speed_per_day
    
    print(f"   Degrees remaining: {degrees_remaining:.4f}°")
    print(f"   Estimated time: {approx_days_remaining:.2f} days ({approx_days_remaining * 24:.1f} hours)")
    
    search_jd = jd_start + (approx_days_remaining * 0.8)
    max_search_jd = jd_start + 2.0
    increment = 0.0005
    
    prev_nak = current_nak_num
    
    while search_jd < max_search_jd:
        moon_result = swe.calc_ut(search_jd, swe.MOON, flags)
        moon_lon = moon_result[0][0] % 360.0
        
        moon_nak_num = int(moon_lon / 13.33333333) + 1
        if moon_nak_num > 27:
            moon_nak_num = 1
        
        if moon_nak_num != prev_nak:
            expected_next_nak = (current_nak_num % 27) + 1
            
            if moon_nak_num == expected_next_nak:
                print(f"   ✓ Found! Moon entered Nakshatra #{moon_nak_num} at JD {search_jd:.6f}")
                print(f"   Moon longitude: {moon_lon:.4f}°")
                print(f"   Time from now: {(search_jd - jd_start) * 24:.2f} hours")
                return search_jd
            else:
                print(f"   ⚠️ Unexpected nakshatra transition: {prev_nak} → {moon_nak_num}")
        
        prev_nak = moon_nak_num
        search_jd += increment
    
    print(f"   ⚠️ Could not find nakshatra end within 2 days")
    return None

# ============================================================================
# VARJYAM CALCULATION
# ============================================================================

def calculate_varjyam_exact(nakshatra_number: int, jd_current: float, 
                           timezone_str: str, moon_longitude: float) -> Dict:
    """Calculate Varjyam with ACTUAL nakshatra end time"""
    
    NAKSHATRA_VARJYAM_GHATIS = {
        1: 4, 2: 3, 3: 2, 4: 6, 5: 5, 6: 7, 7: 4, 8: 5, 9: 7,
        10: 6, 11: 3, 12: 4, 13: 2, 14: 5, 15: 3, 16: 4, 17: 6,
        18: 7, 19: 4, 20: 5, 21: 3, 22: 4, 23: 6, 24: 5, 25: 7,
        26: 4, 27: 2
    }
    
    varjyam_ghatis = NAKSHATRA_VARJYAM_GHATIS.get(nakshatra_number, 4)
    varjyam_minutes = varjyam_ghatis * 24
    varjyam_hours = varjyam_minutes / 60.0
    varjyam_days = varjyam_hours / 24.0
    
    print(f"\n📊 Calculating Varjyam for Nakshatra #{nakshatra_number}")
    print(f"   Varjyam duration: {varjyam_ghatis} Ghatis = {varjyam_minutes} minutes")
    print(f"   Current Moon longitude: {moon_longitude:.4f}°")
    
    nakshatra_end_jd = calculate_nakshatra_end_time(jd_current, nakshatra_number, moon_longitude)
    
    if not nakshatra_end_jd:
        print(f"   ⚠️ Using approximate nakshatra end time")
        nak_start_lon = (nakshatra_number - 1) * 13.33333333
        nak_end_lon = nakshatra_number * 13.33333333
        degrees_remaining = nak_end_lon - moon_longitude
        
        if degrees_remaining < 0:
            degrees_remaining += 360.0
        
        hours_remaining = (degrees_remaining / 13.176) * 24
        approx_nak_end_jd = jd_current + (hours_remaining / 24.0)
        nakshatra_end_jd = approx_nak_end_jd
        
        print(f"   Estimated end: {hours_remaining:.2f} hours from now")
    
    varjyam_start_jd = nakshatra_end_jd - varjyam_days
    
    varjyam_start_dt = jd_to_datetime(varjyam_start_jd, timezone_str)
    varjyam_end_dt = jd_to_datetime(nakshatra_end_jd, timezone_str)
    
    tz = pytz.timezone(timezone_str)
    current_dt = jd_to_datetime(jd_current, timezone_str)
    current_date = current_dt.date()
    
    print(f"   Nakshatra ends: {format_time(varjyam_end_dt)} on {varjyam_end_dt.date()}")
    print(f"   Varjyam period: {format_time(varjyam_start_dt)} - {format_time(varjyam_end_dt)}")
    
    time_display_note = None
    if varjyam_start_dt.date() != current_date:
        days_diff = (varjyam_start_dt.date() - current_date).days
        if days_diff == 1:
            time_display_note = "Occurs after midnight of current day (next day)"
        elif days_diff > 1:
            time_display_note = f"Occurs {days_diff} days from now"
    
    return {
        "varjyam": {
            "start": format_time(varjyam_start_dt),
            "end": format_time(varjyam_end_dt),
            "start_date": varjyam_start_dt.strftime("%Y-%m-%d"),
            "end_date": varjyam_end_dt.strftime("%Y-%m-%d"),
            "duration_minutes": varjyam_minutes,
            "ghatis": varjyam_ghatis,
            "nakshatra_number": nakshatra_number,
            "description": f"Nakshatra-specific inauspicious period for Nakshatra #{nakshatra_number}",
            "avoid": "Important ceremonies, new beginnings, travel, marriage",
            "time_note": time_display_note,
            "calculation_method": "exact_nakshatra_end" if nakshatra_end_jd else "approximate"
        }
    }

# ============================================================================
# PRADOSH KAAL CALCULATION
# ============================================================================

def calculate_pradosh_kaal_corrected(sunset: datetime.datetime) -> Dict:
    """Calculate Pradosh Kaal - Evening auspicious period"""
    
    pradosh_duration_minutes = 144
    
    pradosh_start = sunset
    pradosh_end = sunset + timedelta(minutes=pradosh_duration_minutes)
    
    print(f"\n🌅 Pradosh Kaal Calculation:")
    print(f"   Sunset: {format_time(sunset)}")
    print(f"   Duration: {pradosh_duration_minutes} minutes (3 Muhurtas)")
    print(f"   Period: {format_time(pradosh_start)} - {format_time(pradosh_end)}")
    
    return {
        "pradosh_kaal": {
            "start": format_time(pradosh_start),
            "end": format_time(pradosh_end),
            "duration_minutes": pradosh_duration_minutes,
            "muhurtas": 3,
            "description": "Evening auspicious period for Lord Shiva worship (first part of night)",
            "best_for": "Shiva puja, evening prayers, spiritual activities, meditation",
            "special_notes": "Especially auspicious on Trayodashi (13th) tithi",
            "calculation_method": "fixed_duration_classical"
        }
    }

# ============================================================================
# MURTHA CALCULATION
# ============================================================================

def calculate_exact_murtha_corrected(date_str: str, time_str: str, latitude: float, 
                                    longitude: float, timezone_str: str,
                                    sunset_dt: Optional[datetime.datetime] = None) -> Optional[Dict]:
    """Calculate current Murtha with CORRECTED day length display"""
    
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        dt_start = (dt_local - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        dt_end = (dt_local + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        sunrise_times = []
        for time, event in zip(times, events):
            if event == 1:
                time_utc = time.utc_datetime()
                time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
                sunrise_times.append(time_local)
        
        if len(sunrise_times) < 2:
            return None
        
        sunrise_times.sort()
        
        current_sunrise = None
        next_sunrise = None
        
        for i in range(len(sunrise_times) - 1):
            if sunrise_times[i] <= dt_local < sunrise_times[i + 1]:
                current_sunrise = sunrise_times[i]
                next_sunrise = sunrise_times[i + 1]
                break
        
        if not current_sunrise and dt_local < sunrise_times[0]:
            if len(sunrise_times) >= 2:
                current_sunrise = sunrise_times[0]
                next_sunrise = sunrise_times[1]
        
        if not current_sunrise and dt_local >= sunrise_times[-1]:
            if len(sunrise_times) >= 2:
                current_sunrise = sunrise_times[-2]
                next_sunrise = sunrise_times[-1]
        
        if not current_sunrise or not next_sunrise:
            return None
        
        murtha_cycle_seconds = (next_sunrise - current_sunrise).total_seconds()
        murtha_cycle_hours = murtha_cycle_seconds / 3600.0
        
        daylight_hours = None
        if sunset_dt:
            daylight_seconds = (sunset_dt - current_sunrise).total_seconds()
            daylight_hours = daylight_seconds / 3600.0
            print(f"\n☀️ Day Length Calculation:")
            print(f"   Sunrise: {format_time(current_sunrise)}")
            print(f"   Sunset: {format_time(sunset_dt)}")
            print(f"   Daylight: {daylight_hours:.2f} hours")
        
        murtha_duration_seconds = murtha_cycle_seconds / 30.0
        elapsed_seconds = (dt_local - current_sunrise).total_seconds()
        
        if elapsed_seconds < 0:
            murtha_number = 30
        else:
            murtha_number = min(int(elapsed_seconds / murtha_duration_seconds) + 1, 30)
        
        murtha_data = get_murtha_details(murtha_number)
        
        murtha_start = current_sunrise + timedelta(seconds=(murtha_number - 1) * murtha_duration_seconds)
        murtha_end = current_sunrise + timedelta(seconds=murtha_number * murtha_duration_seconds)
        
        remaining_seconds = (murtha_end - dt_local).total_seconds()
        elapsed_in_murtha = (dt_local - murtha_start).total_seconds()
        
        print(f"\n🕉️ Murtha Calculation:")
        print(f"   Current Murtha: #{murtha_number} ({murtha_data['name']})")
        print(f"   Deity: {murtha_data['deity']}")
        print(f"   Period: {format_time(murtha_start)} - {format_time(murtha_end)}")
        
        return {
            "murtha_number": murtha_number,
            "murtha_name": murtha_data["name"],
            "deity": murtha_data["deity"],
            "nature": murtha_data["nature"],
            "quality": murtha_data["quality"],
            "start_time": format_time(murtha_start),
            "end_time": format_time(murtha_end),
            "duration_minutes": round(murtha_duration_seconds / 60.0, 2),
            "elapsed_minutes": round(elapsed_in_murtha / 60.0, 2),
            "remaining_minutes": round(remaining_seconds / 60.0, 2),
            "progress_percent": round((elapsed_in_murtha / murtha_duration_seconds) * 100, 2),
            "day_info": {
                "sunrise": format_time(current_sunrise),
                "next_sunrise": format_time(next_sunrise),
                "murtha_cycle_hours": round(murtha_cycle_hours, 2),
                "daylight_hours": round(daylight_hours, 2) if daylight_hours else None,
                "explanation": "Murtha uses sunrise-to-sunrise cycle; daylight shows actual sun hours"
            },
            "method": "skyfield_exact"
        }
        
    except Exception as e:
        print(f"Murtha calculation error: {e}")
        return None

# ============================================================================
# MUHURAT TIMING CALCULATIONS
# ============================================================================

def calculate_inauspicious_periods(sunrise: datetime.datetime, 
                                   sunset: datetime.datetime,
                                   weekday: int) -> Dict:
    """Calculate Rahu Kaal, Yamaganda, and Gulika Kaal"""
    
    day_length_seconds = (sunset - sunrise).total_seconds()
    period_duration_seconds = day_length_seconds / 8.0
    
    rahu_period = RAHU_KAAL_PERIODS[weekday]
    yama_period = YAMAGANDA_PERIODS[weekday]
    gulika_period = GULIKA_PERIODS[weekday]
    
    rahu_start = sunrise + timedelta(seconds=rahu_period * period_duration_seconds)
    rahu_end = sunrise + timedelta(seconds=(rahu_period + 1) * period_duration_seconds)
    
    yama_start = sunrise + timedelta(seconds=yama_period * period_duration_seconds)
    yama_end = sunrise + timedelta(seconds=(yama_period + 1) * period_duration_seconds)
    
    gulika_start = sunrise + timedelta(seconds=gulika_period * period_duration_seconds)
    gulika_end = sunrise + timedelta(seconds=(gulika_period + 1) * period_duration_seconds)
    
    return {
        "rahu_kaal": {
            "start": format_time(rahu_start),
            "end": format_time(rahu_end),
            "duration_minutes": round(period_duration_seconds / 60, 2),
            "description": "Inauspicious for all important activities",
            "avoid": "New beginnings, travel, important meetings, ceremonies"
        },
        "yamaganda": {
            "start": format_time(yama_start),
            "end": format_time(yama_end),
            "duration_minutes": round(period_duration_seconds / 60, 2),
            "description": "Death-related inauspicious period",
            "avoid": "Travel, important work, health-related activities"
        },
        "gulika_kaal": {
            "start": format_time(gulika_start),
            "end": format_time(gulika_end),
            "duration_minutes": round(period_duration_seconds / 60, 2),
            "description": "Saturn period - inauspicious",
            "avoid": "Auspicious ceremonies, new ventures"
        }
    }

def calculate_abhijit_muhurat(sunrise: datetime.datetime, 
                               sunset: datetime.datetime) -> Dict:
    """Calculate Abhijit Muhurat"""
    
    day_length_seconds = (sunset - sunrise).total_seconds()
    midday = sunrise + timedelta(seconds=day_length_seconds / 2.0)
    
    abhijit_start = midday - timedelta(minutes=22)
    abhijit_end = midday + timedelta(minutes=22)
    
    return {
        "abhijit_muhurat": {
            "start": format_time(abhijit_start),
            "end": format_time(abhijit_end),
            "duration_minutes": 44,
            "description": "Most auspicious period at midday - good for all activities",
            "best_for": "Marriage, new business, property purchase, important meetings, travel"
        }
    }

def calculate_brahma_muhurat(sunrise: datetime.datetime) -> Dict:
    """Calculate Brahma Muhurat"""
    
    brahma_start = sunrise - timedelta(minutes=96)
    brahma_end = sunrise
    
    return {
        "brahma_muhurat": {
            "start": format_time(brahma_start),
            "end": format_time(brahma_end),
            "duration_minutes": 96,
            "description": "Most auspicious for spiritual practices, meditation, yoga",
            "best_for": "Meditation, yoga, mantras, spiritual study, prayers"
        }
    }

def calculate_godhuli_muhurat(sunset: datetime.datetime) -> Dict:
    """Calculate Godhuli Muhurat"""
    
    godhuli_start = sunset - timedelta(minutes=24)
    godhuli_end = sunset + timedelta(minutes=24)
    
    return {
        "godhuli_muhurat": {
            "start": format_time(godhuli_start),
            "end": format_time(godhuli_end),
            "duration_minutes": 48,
            "description": "Twilight period - auspicious for prayers and rituals",
            "best_for": "Evening prayers, lighting lamps, spiritual activities"
        }
    }

def calculate_dur_muhurat_corrected(sunrise: datetime.datetime, 
                                    sunset: datetime.datetime,
                                    weekday: int) -> List[Dict]:
    """Calculate Dur Muhurat"""
    
    day_length_seconds = (sunset - sunrise).total_seconds()
    muhurta_duration_seconds = day_length_seconds / 15.0
    
    DUR_MUHURAT_POSITIONS = {
        0: [10], 1: [9], 2: [8], 3: [7], 4: [6], 5: [3], 6: [2]
    }
    
    positions = DUR_MUHURAT_POSITIONS.get(weekday, [3])
    dur_muhurats = []
    
    for i, pos in enumerate(positions, 1):
        start = sunrise + timedelta(seconds=(pos - 1) * muhurta_duration_seconds)
        end = sunrise + timedelta(seconds=pos * muhurta_duration_seconds)
        
        dur_muhurats.append({
            "number": i,
            "muhurta_position": pos,
            "start": format_time(start),
            "end": format_time(end),
            "duration_minutes": round(muhurta_duration_seconds / 60, 2)
        })
    
    return dur_muhurats

def calculate_nishita_kaal(prev_sunset: datetime.datetime,
                           current_sunrise: datetime.datetime) -> Dict:
    """Calculate Nishita Kaal"""
    
    night_duration_seconds = (current_sunrise - prev_sunset).total_seconds()
    midnight = prev_sunset + timedelta(seconds=night_duration_seconds / 2.0)
    
    nishita_start = midnight - timedelta(minutes=24)
    nishita_end = midnight + timedelta(minutes=24)
    
    return {
        "nishita_kaal": {
            "start": format_time(nishita_start),
            "end": format_time(nishita_end),
            "duration_minutes": 48,
            "description": "Midnight period - powerful for tantric practices",
            "best_for": "Tantric rituals, advanced spiritual practices (not for general public)"
        }
    }

# ============================================================================
# PANCHANGA FUNCTIONS
# ============================================================================

def calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str):
    """Calculate EXACT moon rise/set using Skyfield"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        dt_start = dt_local.replace(hour=0, minute=0, second=0)
        dt_end = dt_start + timedelta(days=2)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        moon = eph_global['moon']
        f = almanac.risings_and_settings(eph_global, moon, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        moonrise = None
        moonset = None
        target_date = dt_local.date()
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if time_local.date() == target_date:
                if event == 1 and moonrise is None:
                    moonrise = time_local
                elif event == 0 and moonset is None:
                    moonset = time_local
            elif time_local.date() == target_date + timedelta(days=1) and time_local.hour < 12:
                if event == 0 and moonset is None:
                    moonset = time_local
        
        if moonrise and moonset:
            return {
                "moonrise": format_time(moonrise),
                "moonset": format_time(moonset),
                "method": "skyfield_exact"
            }
        
        return None
        
    except Exception as e:
        print(f"Moon calculation error: {e}")
        return None

def calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str):
    """Calculate EXACT sun rise/set using Skyfield"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        dt_start = dt_local.replace(hour=0, minute=0, second=0)
        dt_end = dt_start + timedelta(days=1)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        sunrise = None
        sunset = None
        sunrise_dt = None
        sunset_dt = None
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if event == 1:
                sunrise = format_time(time_local)
                sunrise_dt = time_local
            elif event == 0:
                sunset = format_time(time_local)
                sunset_dt = time_local
        
        if sunrise and sunset:
            return {
                "sunrise": sunrise,
                "sunset": sunset,
                "sunrise_dt": sunrise_dt,
                "sunset_dt": sunset_dt,
                "method": "skyfield_exact"
            }
        
        return None
        
    except Exception as e:
        print(f"Sun calculation error: {e}")
        return None

def calculate_panchanga_elements(date_str, time_str, timezone_str):
    """Calculate Panchanga elements using Swiss Ephemeris"""
    
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    tz = pytz.timezone(timezone_str)
    dt_str = f"{date_str} {time_str}"
    dt_naive = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt_local = tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    
    sun_lon = sun_result[0][0] % 360.0
    moon_lon = moon_result[0][0] % 360.0
    
    phase_angle = (moon_lon - sun_lon) % 360.0
    
    tithi_num = int(phase_angle / 12) + 1
    tithi_progress = (phase_angle % 12) / 12 * 100
    paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
    nak_num = int(moon_lon / 13.333333) + 1
    nak_progress = (moon_lon % 13.333333) / 13.333333
    pada = int(nak_progress * 4) + 1
    
    yoga_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = int(yoga_sum / 13.333333) + 1
    
    karana_num = int(phase_angle / 6) + 1
    
    weekday = dt_local.weekday()
    vara_num = (weekday + 1) % 7 + 1
    
    NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
                  "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
                  "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
                  "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
                  "Uttara Bhadrapada", "Revati"]
    
    TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
              "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
              "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
              "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
              "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
              "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
    
    YOGAS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
             "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
             "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
             "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    
    KARANAS_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
    KARANAS_FIX = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
    
    VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    half_tithi_idx = int(phase_angle / 6)
    if half_tithi_idx == 0:
        karana_name = "Kimstughna"
        karana_type = "fixed"
    elif half_tithi_idx >= 57:
        karana_name = KARANAS_FIX[min(2, half_tithi_idx - 57)]
        karana_type = "fixed"
    else:
        karana_name = KARANAS_MOV[(half_tithi_idx - 1) % 7]
        karana_type = "movable"
    
    return {
        "tithi": {
            "number": tithi_num,
            "name": TITHIS[tithi_num - 1],
            "paksha": paksha,
            "progress_percent": round(tithi_progress, 2)
        },
        "nakshatra": {
            "number": nak_num,
            "name": NAKSHATRAS[nak_num - 1] if nak_num <= 27 else "Revati",
            "pada": pada,
            "progress_percent": round(nak_progress * 100, 2)
        },
        "yoga": {
            "number": yoga_num,
            "name": YOGAS[yoga_num - 1] if yoga_num <= 27 else "Vaidhriti",
            "progress_percent": round((yoga_sum % 13.333333) / 13.333333 * 100, 2)
        },
        "karana": {
            "number": karana_num,
            "name": karana_name,
            "type": karana_type,
            "progress_percent": round((phase_angle % 6) / 6 * 100, 2)
        },
        "vara": {
            "number": vara_num,
            "name": VARAS[vara_num - 1]
        },
        "weekday": weekday,
        "julian_day": jd
    }

# ============================================================================
# MODULE STATUS
# ============================================================================

def get_calculation_status():
    """Get status of calculation module"""
    return {
        "skyfield_available": SKYFIELD_AVAILABLE,
        "swiss_ephemeris_path": SWISS_EPHE_PATH,
        "module": "panchanga_calculations",
        "version": "1.0"
    }


