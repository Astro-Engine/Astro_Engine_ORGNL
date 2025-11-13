"""
Panchanga Calculations Module
All astronomical calculations for Vedic astrology using Swiss Ephemeris and Skyfield
"""

import swisseph as swe
import math
import datetime
import pytz
from typing import Dict, Optional, Tuple, List
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
ts_global = None
eph_global = None

if SKYFIELD_AVAILABLE:
    try:
        ts_global = api.load.timescale()
        eph_global = api.load('de421.bsp')
        print("✓ Skyfield ephemeris loaded (JPL DE421)")
    except Exception as e:
        print(f"⚠️ Skyfield load error: {e}")
        SKYFIELD_AVAILABLE = False


# ============================================================================
# HELPER FUNCTIONS FOR ASTRONOMICAL CALCULATIONS
# ============================================================================

def get_lunar_phase_angle(jd: float) -> float:
    """Get Moon-Sun elongation (phase angle) at given Julian Day"""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return (moon_lon - sun_lon) % 360.0


def get_moon_longitude(jd: float) -> float:
    """Get Moon's sidereal longitude at given Julian Day"""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0


def get_yoga_sum(jd: float) -> float:
    """Get Sun + Moon longitude sum at given Julian Day"""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return (sun_lon + moon_lon) % 360.0


def jd_to_datetime(jd: float, timezone_str: str) -> datetime.datetime:
    """Convert Julian Day to datetime in specified timezone"""
    # Use swe.revjul with proper calendar flag (1 = Gregorian)
    year, month, day, hour = swe.revjul(jd, 1)  # 1 = Gregorian calendar
    
    # Extract hours, minutes, seconds from fractional hour
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    microseconds = int((((hour - hours) * 60 - minutes) * 60 - seconds) * 1000000)
    
    # Create UTC datetime
    dt_utc = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds, tzinfo=pytz.UTC)
    
    # Convert to target timezone
    tz = pytz.timezone(timezone_str)
    dt_local = dt_utc.astimezone(tz)
    
    return dt_local


# ============================================================================
# SUNRISE CALCULATION FOR PANCHANGA DAY
# ============================================================================

def get_sunrise_jd(date_str: str, latitude: float, longitude: float, timezone_str: str) -> float:
    """
    Calculate sunrise Julian Day for Panchanga calculations
    Panchanga day starts at SUNRISE, not midnight
    """
    if not SKYFIELD_AVAILABLE:
        # Fallback: approximate sunrise at 6 AM local time
        tz = pytz.timezone(timezone_str)
        dt_local = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        dt_local = tz.localize(dt_local.replace(hour=6, minute=0, second=0))
        dt_utc = dt_local.astimezone(pytz.UTC)
        
        jd = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0
        )
        return jd
    
    try:
        from datetime import datetime as dt, timedelta
        
        tz = pytz.timezone(timezone_str)
        dt_local = dt.strptime(date_str, '%Y-%m-%d')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        # Search for sunrise on target date
        dt_start = dt_local.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=6)
        dt_end = dt_start + timedelta(hours=18)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        target_date = dt_local.date()
        
        for time, event in zip(times, events):
            if event == 1:  # Sunrise
                time_utc = time.utc_datetime()
                time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
                
                if time_local.date() == target_date:
                    # Convert to Julian Day
                    dt_utc_sunrise = time_local.astimezone(pytz.UTC)
                    jd = swe.julday(
                        dt_utc_sunrise.year, dt_utc_sunrise.month, dt_utc_sunrise.day,
                        dt_utc_sunrise.hour + dt_utc_sunrise.minute/60.0 + dt_utc_sunrise.second/3600.0
                    )
                    return jd
        
        # Fallback if no sunrise found
        dt_local = tz.localize(dt_local.replace(hour=6, minute=0, second=0))
        dt_utc = dt_local.astimezone(pytz.UTC)
        jd = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0
        )
        return jd
        
    except Exception as e:
        print(f"ERROR in get_sunrise_jd: {e}")
        # Fallback
        tz = pytz.timezone(timezone_str)
        dt_local = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        dt_local = tz.localize(dt_local.replace(hour=6, minute=0, second=0))
        dt_utc = dt_local.astimezone(pytz.UTC)
        
        jd = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0
        )
        return jd


# ============================================================================
# TRANSITION TIME CALCULATION FUNCTIONS
# ============================================================================

def find_transition_time(jd_start: float, current_value: float, 
                         target_value: float, value_function, 
                         max_days: float = 2.0) -> Optional[float]:
    """
    Binary search to find exact transition time
    
    Args:
        jd_start: Starting Julian Day
        current_value: Current value (e.g., current tithi angle)
        target_value: Target value to reach (e.g., next tithi boundary)
        value_function: Function that returns value at given JD
        max_days: Maximum search window
    
    Returns:
        Julian Day of transition, or None if not found
    """
    
    # Handle wraparound at 360 degrees
    if target_value < current_value:
        target_value += 360.0
    
    jd_low = jd_start
    jd_high = jd_start + max_days
    
    # Binary search with precision to ~1 second
    precision = 1.0 / 86400.0  # 1 second in days
    max_iterations = 50
    
    for iteration in range(max_iterations):
        jd_mid = (jd_low + jd_high) / 2.0
        
        value = value_function(jd_mid) % 360.0
        
        # Adjust for wraparound
        if value < current_value - 180:
            value += 360.0
        
        # Check if we're close enough
        if abs(value - target_value) < 0.001:  # Very close
            return jd_mid
        
        # Adjust search bounds
        if value < target_value:
            jd_low = jd_mid
        else:
            jd_high = jd_mid
        
        # Check if we've converged
        if abs(jd_high - jd_low) < precision:
            return jd_mid
    
    return jd_mid


def calculate_tithi_end_time(jd: float, timezone_str: str) -> Optional[Dict]:
    """Calculate exact Tithi ending time"""
    try:
        phase_angle = get_lunar_phase_angle(jd)
        current_tithi = int(phase_angle / 12)
        
        # Next tithi boundary (every 12 degrees)
        next_boundary = (current_tithi + 1) * 12.0
        
        # Handle wraparound at 360
        if next_boundary >= 360:
            next_boundary = next_boundary % 360
        
        # Find transition time
        jd_end = find_transition_time(jd, phase_angle, next_boundary, get_lunar_phase_angle)
        
        if jd_end:
            dt_local = jd_to_datetime(jd_end, timezone_str)
            
            return {
                "end_time": dt_local.strftime("%H:%M:%S"),
                "end_date": dt_local.strftime("%Y-%m-%d"),
                "jd": jd_end
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR in calculate_tithi_end_time: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_nakshatra_end_time(jd: float, timezone_str: str) -> Optional[Dict]:
    """Calculate exact Nakshatra ending time"""
    try:
        moon_lon = get_moon_longitude(jd)
        current_nak = int(moon_lon / (360.0 / 27))
        
        # Next nakshatra boundary (each = 13.333... degrees)
        next_boundary = (current_nak + 1) * (360.0 / 27)
        
        # Handle wraparound
        if next_boundary >= 360:
            next_boundary = next_boundary % 360
        
        # Find transition time
        jd_end = find_transition_time(jd, moon_lon, next_boundary, get_moon_longitude, max_days=3.0)
        
        if jd_end:
            dt_local = jd_to_datetime(jd_end, timezone_str)
            
            return {
                "end_time": dt_local.strftime("%H:%M:%S"),
                "end_date": dt_local.strftime("%Y-%m-%d"),
                "jd": jd_end
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR in calculate_nakshatra_end_time: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_yoga_end_time(jd: float, timezone_str: str) -> Optional[Dict]:
    """Calculate exact Yoga ending time"""
    try:
        yoga_sum = get_yoga_sum(jd)
        current_yoga = int(yoga_sum / (360.0 / 27))
        
        # Next yoga boundary (each = 13.333... degrees)
        next_boundary = (current_yoga + 1) * (360.0 / 27)
        
        # Handle wraparound
        if next_boundary >= 360:
            next_boundary = next_boundary % 360
        
        # Find transition time
        jd_end = find_transition_time(jd, yoga_sum, next_boundary, get_yoga_sum, max_days=1.5)
        
        if jd_end:
            dt_local = jd_to_datetime(jd_end, timezone_str)
            
            return {
                "end_time": dt_local.strftime("%H:%M:%S"),
                "end_date": dt_local.strftime("%Y-%m-%d"),
                "jd": jd_end
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR in calculate_yoga_end_time: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_karana_end_time(jd: float, timezone_str: str) -> Optional[Dict]:
    """Calculate exact Karana ending time (half-tithi)"""
    try:
        phase_angle = get_lunar_phase_angle(jd)
        current_karana = int(phase_angle / 6)
        
        # Next karana boundary (every 6 degrees - half of tithi)
        next_boundary = (current_karana + 1) * 6.0
        
        # Handle wraparound
        if next_boundary >= 360:
            next_boundary = next_boundary % 360
        
        # Find transition time
        jd_end = find_transition_time(jd, phase_angle, next_boundary, get_lunar_phase_angle)
        
        if jd_end:
            dt_local = jd_to_datetime(jd_end, timezone_str)
            
            return {
                "end_time": dt_local.strftime("%H:%M:%S"),
                "end_date": dt_local.strftime("%Y-%m-%d"),
                "jd": jd_end
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR in calculate_karana_end_time: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_next_sunrise_time(date_str: str, latitude: float, longitude: float, timezone_str: str) -> Dict:
    """
    Calculate next sunrise time (Vara/day changes at sunrise in Vedic system)
    """
    try:
        # Get next day's date
        current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        next_date = current_date + datetime.timedelta(days=1)
        next_date_str = next_date.strftime('%Y-%m-%d')
        
        # Get sunrise JD for next day
        next_sunrise_jd = get_sunrise_jd(next_date_str, latitude, longitude, timezone_str)
        
        # Convert to local time
        dt_local = jd_to_datetime(next_sunrise_jd, timezone_str)
        
        return {
            "end_time": dt_local.strftime("%H:%M:%S"),
            "end_date": dt_local.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        print(f"ERROR in calculate_next_sunrise_time: {e}")
        # Fallback to next day at 6 AM
        current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        next_date = current_date + datetime.timedelta(days=1)
        return {
            "end_time": "06:00:00",
            "end_date": next_date.strftime("%Y-%m-%d")
        }


# ============================================================================
# SKYFIELD FUNCTIONS (Sun/Moon Rise/Set)
# ============================================================================

def calculate_exact_moon_times_one(date_str: str, time_str: str, latitude: float, 
                                longitude: float, timezone_str: str) -> Optional[Dict]:
    """Calculate EXACT moon rise/set using Skyfield - DRIK PANCHANG LOGIC"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        from datetime import datetime as dt, timedelta
        
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        target_date = dt_local.date()
        dt_start = dt_local.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        dt_end = dt_start + timedelta(days=3)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        moon = eph_global['moon']
        f = almanac.risings_and_settings(eph_global, moon, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        all_events = []
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            all_events.append({
                'datetime': time_local,
                'date': time_local.date(),
                'time_str': time_local.strftime("%H:%M:%S"),
                'type': 'rise' if event == 1 else 'set',
                'event_code': event
            })
        
        all_events.sort(key=lambda x: x['datetime'])
        
        moonset = None
        moonset_index = -1
        
        for i, evt in enumerate(all_events):
            if evt['date'] == target_date and evt['type'] == 'set':
                moonset = evt['datetime']
                moonset_index = i
                break
        
        moonrise = None
        moonrise_on_next_day = False
        
        if moonset_index >= 0:
            for i in range(moonset_index + 1, len(all_events)):
                evt = all_events[i]
                if evt['type'] == 'rise':
                    moonrise = evt['datetime']
                    moonrise_on_next_day = (evt['date'] > target_date)
                    break
        else:
            for evt in all_events:
                if evt['date'] >= target_date and evt['type'] == 'rise':
                    moonrise = evt['datetime']
                    moonrise_on_next_day = (evt['date'] > target_date)
                    break
        
        if moonrise and moonset:
            response = {
                "moonrise": moonrise.strftime("%H:%M:%S"),
                "moonrise_date": moonrise.strftime("%Y-%m-%d"),
                "moonset": moonset.strftime("%H:%M:%S"),
                "moonset_date": moonset.strftime("%Y-%m-%d"),
                "method": "skyfield_exact_drik",
                "on_target_date": not moonrise_on_next_day
            }
            
            if moonrise_on_next_day:
                hours_24plus = 24 + moonrise.hour
                response["moonrise_24plus"] = f"{hours_24plus:02d}:{moonrise.minute:02d}:{moonrise.second:02d}"
                response["note"] = "Moonrise occurs on next day"
            
            return response
            
        elif moonrise:
            response = {
                "moonrise": moonrise.strftime("%H:%M:%S"),
                "moonrise_date": moonrise.strftime("%Y-%m-%d"),
                "moonset": None,
                "moonset_date": None,
                "method": "skyfield_exact_partial",
                "on_target_date": not moonrise_on_next_day,
                "note": "No moonset on target date"
            }
            if moonrise_on_next_day:
                hours_24plus = 24 + moonrise.hour
                response["moonrise_24plus"] = f"{hours_24plus:02d}:{moonrise.minute:02d}:{moonrise.second:02d}"
            return response
            
        elif moonset:
            return {
                "moonrise": None,
                "moonrise_date": None,
                "moonset": moonset.strftime("%H:%M:%S"),
                "moonset_date": moonset.strftime("%Y-%m-%d"),
                "method": "skyfield_exact_partial",
                "on_target_date": False,
                "note": "No moonrise found after moonset"
            }
        else:
            return None
        
    except Exception as e:
        print(f"ERROR in calculate_exact_moon_times: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_exact_sun_times_one(date_str: str, time_str: str, latitude: float, 
                               longitude: float, timezone_str: str) -> Optional[Dict]:
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
        
        dt_start = dt_local.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=6)
        dt_end = dt_start + timedelta(hours=36)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        sunrise = None
        sunset = None
        target_date = dt_local.date()
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if time_local.date() == target_date:
                if event == 1 and sunrise is None:
                    sunrise = time_local
                elif event == 0 and sunset is None:
                    sunset = time_local
        
        if sunrise and sunset:
            return {
                "sunrise": sunrise.strftime("%H:%M:%S"),
                "sunset": sunset.strftime("%H:%M:%S"),
                "method": "skyfield_exact"
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR in calculate_exact_sun_times: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# PANCHANGA CALCULATION FUNCTION
# ============================================================================

def calculate_panchanga_elements_one(date_str: str, time_str: str, latitude: float, 
                                 longitude: float, timezone_str: str) -> Dict:
    """
    Calculate Panchanga elements with EXACT ending times
    
    CRITICAL: Panchanga is calculated at SUNRISE, not at the input time!
    This ensures consistent results regardless of what time user queries.
    """
    
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    # CRITICAL FIX: Calculate Panchanga at SUNRISE of the given date
    # This ensures Yoga and other elements don't change with location
    sunrise_jd = get_sunrise_jd(date_str, latitude, longitude, timezone_str)
    
    print(f"\n🌅 Using SUNRISE as reference point for Panchanga")
    print(f"   Date: {date_str}")
    print(f"   Sunrise JD: {sunrise_jd}")
    
    # Get planetary positions AT SUNRISE
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_result = swe.calc_ut(sunrise_jd, swe.SUN, flags)
    moon_result = swe.calc_ut(sunrise_jd, swe.MOON, flags)
    
    sun_lon = sun_result[0][0] % 360.0
    moon_lon = moon_result[0][0] % 360.0
    phase_angle = (moon_lon - sun_lon) % 360.0
    
    # ========== TITHI ==========
    tithi_num = int(phase_angle / 12) + 1
    if tithi_num > 30:
        tithi_num = 30
    tithi_progress = (phase_angle % 12) / 12 * 100
    paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
    # Calculate Tithi end time
    tithi_end = calculate_tithi_end_time(sunrise_jd, timezone_str)
    
    # ========== NAKSHATRA ==========
    nak_num = int(moon_lon / 13.333333) + 1
    if nak_num > 27:
        nak_num = 27
    nak_progress = (moon_lon % 13.333333) / 13.333333
    pada = int(nak_progress * 4) + 1
    if pada > 4:
        pada = 4
    
    # Calculate Nakshatra end time
    nak_end = calculate_nakshatra_end_time(sunrise_jd, timezone_str)
    
    # ========== YOGA ==========
    yoga_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = int(yoga_sum / 13.333333) + 1
    if yoga_num > 27:
        yoga_num = 27
    yoga_progress = (yoga_sum % 13.333333) / 13.333333 * 100
    
    print(f"   Sun Longitude: {sun_lon:.4f}°")
    print(f"   Moon Longitude: {moon_lon:.4f}°")
    print(f"   Yoga Sum: {yoga_sum:.4f}°")
    print(f"   Yoga Number: {yoga_num}")
    
    # Calculate Yoga end time
    yoga_end = calculate_yoga_end_time(sunrise_jd, timezone_str)
    
    # ========== KARANA ==========
    half_tithi_idx = int(phase_angle / 6)
    karana_progress = (phase_angle % 6) / 6 * 100
    
    if half_tithi_idx == 0:
        karana_name = "Kimstughna"
        karana_type = "fixed"
        karana_num = 1
    elif half_tithi_idx >= 57:
        fixed_karanas = ["Shakuni", "Chatushpada", "Naga"]
        idx = min(half_tithi_idx - 57, 2)
        karana_name = fixed_karanas[idx]
        karana_type = "fixed"
        karana_num = 58 + idx
    else:
        movable_karanas = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
        karana_name = movable_karanas[(half_tithi_idx - 1) % 7]
        karana_type = "movable"
        karana_num = half_tithi_idx + 1
    
    # Calculate Karana end time
    karana_end = calculate_karana_end_time(sunrise_jd, timezone_str)
    
    # ========== VARA ==========
    # Parse the input date to get weekday
    tz = pytz.timezone(timezone_str)
    dt_input = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    dt_input = tz.localize(dt_input)
    
    weekday = dt_input.weekday()
    vara_num = (weekday + 2) % 7
    if vara_num == 0:
        vara_num = 7
    
    # Vara changes at next sunrise (Vedic day starts at sunrise)
    vara_end = calculate_next_sunrise_time(date_str, latitude, longitude, timezone_str)
    
    # Name arrays
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
        "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
        "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]
    
    TITHIS = [
        "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
        "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ]
    
    YOGAS = [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
        "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
        "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
        "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
    ]
    
    VARAS = [
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    ]
    
    return {
        "tithi": {
            "number": tithi_num,
            "name": TITHIS[tithi_num - 1],
            "paksha": paksha,
            "progress_percent": round(tithi_progress, 2),
            "degrees": round(phase_angle, 4),
            "end_time": tithi_end["end_time"] if tithi_end else None,
            "end_date": tithi_end["end_date"] if tithi_end else None
        },
        "nakshatra": {
            "number": nak_num,
            "name": NAKSHATRAS[nak_num - 1],
            "pada": pada,
            "progress_percent": round(nak_progress * 100, 2),
            "degrees": round(moon_lon, 4),
            "end_time": nak_end["end_time"] if nak_end else None,
            "end_date": nak_end["end_date"] if nak_end else None
        },
        "yoga": {
            "number": yoga_num,
            "name": YOGAS[yoga_num - 1],
            "progress_percent": round(yoga_progress, 2),
            "degrees": round(yoga_sum, 4),
            "end_time": yoga_end["end_time"] if yoga_end else None,
            "end_date": yoga_end["end_date"] if yoga_end else None
        },
        "karana": {
            "number": karana_num,
            "name": karana_name,
            "type": karana_type,
            "progress_percent": round(karana_progress, 2),
            "end_time": karana_end["end_time"] if karana_end else None,
            "end_date": karana_end["end_date"] if karana_end else None
        },
        "vara": {
            "number": vara_num,
            "name": VARAS[vara_num - 1],
            "end_time": vara_end["end_time"],
            "end_date": vara_end["end_date"]
        },
        "planetary_positions": {
            "sun_longitude": round(sun_lon, 4),
            "moon_longitude": round(moon_lon, 4),
            "phase_angle": round(phase_angle, 4)
        }
    }