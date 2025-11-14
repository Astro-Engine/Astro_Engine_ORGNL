"""
Multi-Day Panchanga Calculations Module
Batch calculations for Vedic astrology with TRUE Drik Panchang moonrise/moonset logic
"""

import swisseph as swe
import math
import datetime
import pytz
from typing import Dict, Optional, Tuple, List
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import Skyfield
try:
    from skyfield import api, almanac
    SKYFIELD_AVAILABLE = True
    print("✓ Skyfield available")
except ImportError:
    SKYFIELD_AVAILABLE = False
    print("⚠️ Skyfield not available")

SWISS_EPHE_PATH = "astro_api/ephe"
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Initialize Skyfield globals
ts_global = None
eph_global = None

if SKYFIELD_AVAILABLE:
    try:
        ts_global = api.load.timescale()
        eph_global = api.load('de421.bsp')
        print("✓ Skyfield ephemeris loaded")
    except Exception as e:
        print(f"⚠️ Skyfield load error: {e}")
        SKYFIELD_AVAILABLE = False

# ============================================================================
# CONSTANTS
# ============================================================================

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

VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANAS = ["Kimstughna", "Shakuni", "Chatushpada", "Naga"]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_lunar_phase_angle(jd: float) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return (moon_lon - sun_lon) % 360.0

def get_moon_longitude(jd: float) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0

def get_yoga_sum(jd: float) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return (sun_lon + moon_lon) % 360.0

def get_sun_moon_longitudes(jd: float) -> Tuple[float, float]:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    return sun_lon, moon_lon

def jd_to_datetime(jd: float, timezone_str: str) -> datetime.datetime:
    year, month, day, hour = swe.revjul(jd, 1)
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    microseconds = int((((hour - hours) * 60 - minutes) * 60 - seconds) * 1000000)
    dt_utc = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds, tzinfo=pytz.UTC)
    tz = pytz.timezone(timezone_str)
    return dt_utc.astimezone(tz)

# ============================================================================
# TRUE DRIK PANCHANG MOONRISE LOGIC
# ============================================================================

def batch_calculate_sun_moon_times(start_date_str: str, end_date_str: str,
                                   latitude: float, longitude: float,
                                   timezone_str: str) -> Dict[str, Dict]:
    """
    TRUE DRIK PANCHANG LOGIC:
    
    For each date, show:
    1. FIRST moonrise that occurs on that calendar date (00:00 to 23:59)
    2. FIRST moonset that occurs on that calendar date
    3. If NO moonrise on that date, find next available and show in 24+ format
    
    This is NOT about "moonrise after moonset" - it's simply showing
    what happens on each calendar date!
    """
    
    if not SKYFIELD_AVAILABLE:
        result = {}
        tz = pytz.timezone(timezone_str)
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        
        current = start_date
        while current <= end_date:
            dt_local = tz.localize(current.replace(hour=6, minute=0, second=0))
            dt_utc = dt_local.astimezone(pytz.UTC)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0)
            
            date_str = current.strftime('%Y-%m-%d')
            result[date_str] = {
                'sunrise_jd': jd, 'sunrise': '06:00:00', 'sunset': '18:00:00',
                'moonrise': None, 'moonset': None,
                'moonrise_date': date_str, 'moonset_date': date_str
            }
            current += datetime.timedelta(days=1)
        return result
    
    try:
        from datetime import datetime as dt, timedelta
        
        tz = pytz.timezone(timezone_str)
        start_dt = dt.strptime(start_date_str, '%Y-%m-%d')
        end_dt = dt.strptime(end_date_str, '%Y-%m-%d')
        
        search_start = tz.localize(start_dt) - timedelta(days=1)
        search_end = tz.localize(end_dt) + timedelta(days=2)
        
        location = api.wgs84.latlon(latitude, longitude)
        
        t0 = ts_global.from_datetime(search_start)
        t1 = ts_global.from_datetime(search_end)
        
        # Get SUN events
        sun = eph_global['sun']
        f_sun = almanac.risings_and_settings(eph_global, sun, location)
        sun_times, sun_events = almanac.find_discrete(t0, t1, f_sun)
        
        # Get MOON events
        moon = eph_global['moon']
        f_moon = almanac.risings_and_settings(eph_global, moon, location)
        moon_times, moon_events = almanac.find_discrete(t0, t1, f_moon)
        
        # Process SUN
        sun_data = {}
        for time, event in zip(sun_times, sun_events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            date_str = time_local.strftime('%Y-%m-%d')
            
            if date_str not in sun_data:
                sun_data[date_str] = {}
            
            if event == 1:
                sun_data[date_str]['sunrise'] = time_local.strftime("%H:%M:%S")
                dt_utc = time_local.astimezone(pytz.UTC)
                jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                               dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
                sun_data[date_str]['sunrise_jd'] = jd
            elif event == 0:
                sun_data[date_str]['sunset'] = time_local.strftime("%H:%M:%S")
        
        # Process MOON - organize by date
        moon_by_date = {}
        for time, event in zip(moon_times, moon_events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            date_key = time_local.date()
            
            if date_key not in moon_by_date:
                moon_by_date[date_key] = {'rises': [], 'sets': []}
            
            event_data = {
                'datetime': time_local,
                'time_str': time_local.strftime("%H:%M:%S")
            }
            
            if event == 1:  # Rise
                moon_by_date[date_key]['rises'].append(event_data)
            else:  # Set
                moon_by_date[date_key]['sets'].append(event_data)
        
        # Sort events within each date
        for date_key in moon_by_date:
            moon_by_date[date_key]['rises'].sort(key=lambda x: x['datetime'])
            moon_by_date[date_key]['sets'].sort(key=lambda x: x['datetime'])
        
        # Build result for each date
        result = {}
        current = start_dt
        
        while current <= end_dt:
            date_str = current.strftime('%Y-%m-%d')
            target_date = current.date()
            
            # Get sun times
            if date_str in sun_data:
                result[date_str] = sun_data[date_str].copy()
            else:
                dt_local = tz.localize(current.replace(hour=6, minute=0))
                dt_utc = dt_local.astimezone(pytz.UTC)
                jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                               dt_utc.hour + dt_utc.minute/60.0)
                result[date_str] = {
                    'sunrise_jd': jd, 'sunrise': '06:00:00', 'sunset': '18:00:00'
                }
            
            # ================================================================
            # TRUE DRIK PANCHANG LOGIC - SIMPLE!
            # Just show what happens on each calendar date
            # ================================================================
            
            # MOONRISE: First rise on this date
            if target_date in moon_by_date and moon_by_date[target_date]['rises']:
                moonrise = moon_by_date[target_date]['rises'][0]
                result[date_str]['moonrise'] = moonrise['time_str']
                result[date_str]['moonrise_date'] = moonrise['datetime'].strftime('%Y-%m-%d')
                result[date_str]['moonrise_note'] = "Moonrise on same day"
            else:
                # No moonrise on this date - find next available
                moonrise = None
                search_date = target_date + timedelta(days=1)
                for i in range(5):  # Search next 5 days
                    if search_date in moon_by_date and moon_by_date[search_date]['rises']:
                        moonrise = moon_by_date[search_date]['rises'][0]
                        break
                    search_date += timedelta(days=1)
                
                if moonrise:
                    # Calculate 24+ hour format
                    days_diff = (moonrise['datetime'].date() - target_date).days
                    hours_24plus = moonrise['datetime'].hour + (days_diff * 24)
                    result[date_str]['moonrise_24plus'] = f"{hours_24plus:02d}:{moonrise['datetime'].minute:02d}:{moonrise['datetime'].second:02d}"
                    result[date_str]['moonrise'] = moonrise['time_str']
                    result[date_str]['moonrise_date'] = moonrise['datetime'].strftime('%Y-%m-%d')
                    result[date_str]['moonrise_note'] = "Moonrise occurs on next day"
                else:
                    result[date_str]['moonrise'] = None
                    result[date_str]['moonrise_date'] = None
                    result[date_str]['moonrise_note'] = "No moonrise found"
            
            # MOONSET: First set on this date
            if target_date in moon_by_date and moon_by_date[target_date]['sets']:
                moonset = moon_by_date[target_date]['sets'][0]
                result[date_str]['moonset'] = moonset['time_str']
                result[date_str]['moonset_date'] = moonset['datetime'].strftime('%Y-%m-%d')
            else:
                result[date_str]['moonset'] = None
                result[date_str]['moonset_date'] = None
            
            current += timedelta(days=1)
        
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}

# ============================================================================
# TRANSITION CALCULATIONS
# ============================================================================

def find_transition_time(jd_start: float, current_value: float, target_value: float, 
                         value_function, max_days: float = 2.0) -> Optional[float]:
    if target_value < current_value:
        target_value += 360.0
    
    jd_low, jd_high = jd_start, jd_start + max_days
    precision, max_iter = 1.0 / 86400.0, 50
    
    for _ in range(max_iter):
        jd_mid = (jd_low + jd_high) / 2.0
        value = value_function(jd_mid) % 360.0
        
        if value < current_value - 180:
            value += 360.0
        
        if abs(value - target_value) < 0.001:
            return jd_mid
        
        if value < target_value:
            jd_low = jd_mid
        else:
            jd_high = jd_mid
        
        if abs(jd_high - jd_low) < precision:
            return jd_mid
    
    return jd_mid

def calculate_tithi_end_time(jd: float, tz_str: str) -> Optional[Dict]:
    try:
        phase_angle = get_lunar_phase_angle(jd)
        current_tithi = int(phase_angle / 12)
        next_boundary = (current_tithi + 1) * 12.0
        if next_boundary >= 360:
            next_boundary %= 360
        jd_end = find_transition_time(jd, phase_angle, next_boundary, get_lunar_phase_angle)
        if jd_end:
            dt = jd_to_datetime(jd_end, tz_str)
            return {"end_time": dt.strftime("%H:%M:%S"), "end_date": dt.strftime("%Y-%m-%d")}
        return None
    except:
        return None

def calculate_nakshatra_end_time(jd: float, tz_str: str) -> Optional[Dict]:
    try:
        moon_lon = get_moon_longitude(jd)
        current_nak = int(moon_lon / (360.0 / 27))
        next_boundary = (current_nak + 1) * (360.0 / 27)
        if next_boundary >= 360:
            next_boundary %= 360
        jd_end = find_transition_time(jd, moon_lon, next_boundary, get_moon_longitude, 3.0)
        if jd_end:
            dt = jd_to_datetime(jd_end, tz_str)
            return {"end_time": dt.strftime("%H:%M:%S"), "end_date": dt.strftime("%Y-%m-%d")}
        return None
    except:
        return None

def calculate_yoga_end_time(jd: float, tz_str: str) -> Optional[Dict]:
    try:
        yoga_sum = get_yoga_sum(jd)
        current_yoga = int(yoga_sum / (360.0 / 27))
        next_boundary = (current_yoga + 1) * (360.0 / 27)
        if next_boundary >= 360:
            next_boundary %= 360
        jd_end = find_transition_time(jd, yoga_sum, next_boundary, get_yoga_sum, 1.5)
        if jd_end:
            dt = jd_to_datetime(jd_end, tz_str)
            return {"end_time": dt.strftime("%H:%M:%S"), "end_date": dt.strftime("%Y-%m-%d")}
        return None
    except:
        return None

def calculate_karana_end_time(jd: float, tz_str: str) -> Optional[Dict]:
    try:
        phase_angle = get_lunar_phase_angle(jd)
        current_karana = int(phase_angle / 6)
        next_boundary = (current_karana + 1) * 6.0
        if next_boundary >= 360:
            next_boundary %= 360
        jd_end = find_transition_time(jd, phase_angle, next_boundary, get_lunar_phase_angle)
        if jd_end:
            dt = jd_to_datetime(jd_end, tz_str)
            return {"end_time": dt.strftime("%H:%M:%S"), "end_date": dt.strftime("%Y-%m-%d")}
        return None
    except:
        return None

def calculate_next_sunrise_time(date_str: str, sun_moon_data: Dict) -> Dict:
    try:
        current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        next_date = current_date + datetime.timedelta(days=1)
        next_date_str = next_date.strftime('%Y-%m-%d')
        
        if next_date_str in sun_moon_data:
            return {"end_time": sun_moon_data[next_date_str]['sunrise'], "end_date": next_date_str}
        return {"end_time": "06:00:00", "end_date": next_date_str}
    except:
        current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        next_date = current_date + datetime.timedelta(days=1)
        return {"end_time": "06:00:00", "end_date": next_date.strftime("%Y-%m-%d")}

# ============================================================================
# PANCHANGA CALCULATION
# ============================================================================

def calculate_panchanga_for_date(date_str: str, sun_moon_data: Dict, lat: float, lon: float,
                                 tz_str: str, incl_trans: bool = True) -> Dict:
    sunrise_jd = sun_moon_data[date_str]['sunrise_jd']
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon, moon_lon = get_sun_moon_longitudes(sunrise_jd)
    phase_angle = (moon_lon - sun_lon) % 360.0
    
    # TITHI
    tithi_num = min(int(phase_angle / 12) + 1, 30)
    tithi_progress = (phase_angle % 12) / 12 * 100
    paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    tithi_data = {"number": tithi_num, "name": TITHIS[tithi_num - 1], 
                  "paksha": paksha, "progress_percent": round(tithi_progress, 2)}
    if incl_trans:
        tithi_end = calculate_tithi_end_time(sunrise_jd, tz_str)
        if tithi_end:
            tithi_data.update(tithi_end)
    
    # NAKSHATRA
    nak_num = min(int(moon_lon / 13.333333) + 1, 27)
    nak_progress = (moon_lon % 13.333333) / 13.333333
    pada = min(int(nak_progress * 4) + 1, 4)
    nak_data = {"number": nak_num, "name": NAKSHATRAS[nak_num - 1],
                "pada": pada, "progress_percent": round(nak_progress * 100, 2)}
    if incl_trans:
        nak_end = calculate_nakshatra_end_time(sunrise_jd, tz_str)
        if nak_end:
            nak_data.update(nak_end)
    
    # YOGA
    yoga_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = min(int(yoga_sum / 13.333333) + 1, 27)
    yoga_progress = (yoga_sum % 13.333333) / 13.333333 * 100
    yoga_data = {"number": yoga_num, "name": YOGAS[yoga_num - 1],
                 "progress_percent": round(yoga_progress, 2)}
    if incl_trans:
        yoga_end = calculate_yoga_end_time(sunrise_jd, tz_str)
        if yoga_end:
            yoga_data.update(yoga_end)
    
    # KARANA
    half_tithi_idx = int(phase_angle / 6)
    karana_progress = (phase_angle % 6) / 6 * 100
    
    if half_tithi_idx == 0:
        karana_name, karana_type, karana_num = "Kimstughna", "fixed", 1
    elif half_tithi_idx >= 57:
        idx = min(half_tithi_idx - 57, 2)
        karana_name, karana_type = FIXED_KARANAS[idx + 1], "fixed"
        karana_num = 58 + idx
    else:
        karana_name = MOVABLE_KARANAS[(half_tithi_idx - 1) % 7]
        karana_type, karana_num = "movable", half_tithi_idx + 1
    
    karana_data = {"number": karana_num, "name": karana_name, 
                   "type": karana_type, "progress_percent": round(karana_progress, 2)}
    if incl_trans:
        karana_end = calculate_karana_end_time(sunrise_jd, tz_str)
        if karana_end:
            karana_data.update(karana_end)
    
    # VARA
    tz = pytz.timezone(tz_str)
    dt_input = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    dt_input = tz.localize(dt_input)
    weekday = dt_input.weekday()
    vara_num = (weekday + 2) % 7
    if vara_num == 0:
        vara_num = 7
    vara_data = {"number": vara_num, "name": VARAS[vara_num - 1]}
    if incl_trans:
        vara_end = calculate_next_sunrise_time(date_str, sun_moon_data)
        vara_data.update(vara_end)
    
    # Build response
    response = {
        "date": date_str,
        "sunrise": sun_moon_data[date_str]['sunrise'],
        "sunset": sun_moon_data[date_str]['sunset'],
        "moonrise": sun_moon_data[date_str].get('moonrise'),
        "moonset": sun_moon_data[date_str].get('moonset'),
        "tithi": tithi_data,
        "nakshatra": nak_data,
        "yoga": yoga_data,
        "karana": karana_data,
        "vara": vara_data
    }
    
    if sun_moon_data[date_str].get('moonrise_24plus'):
        response['moonrise_24plus'] = sun_moon_data[date_str]['moonrise_24plus']
    if sun_moon_data[date_str].get('moonrise_date'):
        response['moonrise_date'] = sun_moon_data[date_str]['moonrise_date']
    if sun_moon_data[date_str].get('moonset_date'):
        response['moonset_date'] = sun_moon_data[date_str]['moonset_date']
    if sun_moon_data[date_str].get('moonrise_note'):
        response['moonrise_note'] = sun_moon_data[date_str]['moonrise_note']
    
    return response

def calculate_days_panchanga(start_date_str: str, num_days: int, lat: float, lon: float,
                             tz_str: str, incl_trans: bool = True, parallel: bool = True) -> List[Dict]:
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    if start_date_str.lower() == "current":
        start_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = start_date + datetime.timedelta(days=num_days - 1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\n{'='*70}")
    print(f"PANCHANGA - {num_days} DAYS")
    print(f"Range: {start_date_str} to {end_date_str}")
    print(f"{'='*70}\n")
    
    print("⏳ Calculating...")
    sun_moon_data = batch_calculate_sun_moon_times(start_date_str, end_date_str, lat, lon, tz_str)
    
    results = []
    
    if parallel and len(sun_moon_data) > 5:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for date_str in sun_moon_data.keys():
                future = executor.submit(calculate_panchanga_for_date, date_str, sun_moon_data, 
                                        lat, lon, tz_str, incl_trans)
                futures[future] = date_str
            
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"ERROR {futures[future]}: {e}")
    else:
        for date_str in sun_moon_data.keys():
            try:
                results.append(calculate_panchanga_for_date(date_str, sun_moon_data, 
                                                            lat, lon, tz_str, incl_trans))
            except Exception as e:
                print(f"ERROR {date_str}: {e}")
    
    results.sort(key=lambda x: x['date'])
    print(f"✓ Done\n")
    return results