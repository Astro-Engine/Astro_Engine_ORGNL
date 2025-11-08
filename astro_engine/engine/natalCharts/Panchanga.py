"""
PANCHANGA CALCULATIONS MODULE
All astronomical calculations for Panchanga using Skyfield and Swiss Ephemeris
"""

import swisseph as swe
import math
import datetime
import pytz
from typing import Dict, Optional
import os

# Try to import Skyfield
try:
    from skyfield import api, almanac
    SKYFIELD_AVAILABLE = True
    print("✓ Skyfield available - EXACT calculations enabled")
except ImportError:
    SKYFIELD_AVAILABLE = False
    print("⚠️ Skyfield not available - install with: pip install skyfield")

# Configuration
SWISS_EPHE_PATH = "astro_api/ephe"
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Initialize Skyfield (if available)
if SKYFIELD_AVAILABLE:
    try:
        ts_global = api.load.timescale()
        eph_global = api.load('de421.bsp')
        print("✓ Skyfield ephemeris loaded (JPL DE421)")
    except Exception as e:
        print(f"⚠️ Skyfield load error: {e}")
        SKYFIELD_AVAILABLE = False

def calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str):
    """
    Calculate EXACT moon rise/set using Skyfield
    
    Returns times matching Drik Panchang accuracy (±1-2 minutes)
    """
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        from datetime import datetime as dt, timedelta
        
        # Parse datetime
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        # Observer location
        location = api.wgs84.latlon(latitude, longitude)
        
        # Search window
        dt_start = dt_local.replace(hour=0, minute=0, second=0)
        dt_end = dt_start + timedelta(days=2)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        # Calculate moon events
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
                if event == 1 and moonrise is None:  # Rise
                    moonrise = time_local
                elif event == 0 and moonset is None:  # Set
                    moonset = time_local
            elif time_local.date() == target_date + timedelta(days=1) and time_local.hour < 12:
                if event == 0 and moonset is None:
                    moonset = time_local
        
        if moonrise and moonset:
            return {
                "moonrise": moonrise.strftime("%H:%M:%S"),
                "moonset": moonset.strftime("%H:%M:%S"),
                "method": "skyfield_exact"
            }
        
        return None
        
    except Exception as e:
        print(f"Skyfield moon error: {e}")
        return None

def calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str):
    """Calculate EXACT sun rise/set using Skyfield"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        from datetime import datetime as dt, timedelta
        
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
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
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if event == 1:  # Rise
                sunrise = time_local
            elif event == 0:  # Set
                sunset = time_local
        
        if sunrise and sunset:
            return {
                "sunrise": sunrise.strftime("%H:%M:%S"),
                "sunset": sunset.strftime("%H:%M:%S"),
                "method": "skyfield_exact"
            }
        
        return None
        
    except Exception as e:
        print(f"Skyfield sun error: {e}")
        return None

def calculate_panchanga_elements(date_str, time_str, timezone_str):
    """Calculate Panchanga elements using Swiss Ephemeris"""
    
    # Initialize Swiss Ephemeris
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    # Parse datetime
    tz = pytz.timezone(timezone_str)
    dt_str = f"{date_str} {time_str}"
    dt_naive = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt_local = tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    # Calculate Julian Day
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )
    
    # Get planetary positions
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    
    sun_lon = sun_result[0][0] % 360.0
    moon_lon = moon_result[0][0] % 360.0
    
    # Calculate elements
    phase_angle = (moon_lon - sun_lon) % 360.0
    
    # Tithi
    tithi_num = int(phase_angle / 12) + 1
    tithi_progress = (phase_angle % 12) / 12 * 100
    paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
    # Nakshatra
    nak_num = int(moon_lon / 13.333333) + 1
    nak_progress = (moon_lon % 13.333333) / 13.333333
    pada = int(nak_progress * 4) + 1
    
    # Yoga
    yoga_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = int(yoga_sum / 13.333333) + 1
    
    # Karana
    karana_num = int(phase_angle / 6) + 1
    
    # Vara
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
    
    # Karana logic (corrected)
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
        }
    }