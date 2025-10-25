import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

# Constants for Vimshottari Dasha system
PLANET_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
MAHADASHA_DURATIONS = {
    'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16,
    'Saturn': 19, 'Mercury': 17, 'Ketu': 7, 'Venus': 20
}
TOTAL_VIMSHOTTARI_CYCLE = 120  # Total years in Vimshottari cycle
DEGREES_PER_NAKSHATRA = 13 + (20 / 60.0)  # 13 degrees 20 minutes
SIDEREAL_YEAR = 365.2563  # Days in a sidereal year for precise date calculations

# ==================== HELPER FUNCTIONS ====================

def get_julian_day_one_year(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day, adjusting for timezone offset."""
    date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
    time_obj = datetime.strptime(birth_time, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)  # Convert to UT
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)


def calculate_moon_sidereal_longitude_one_year(jd):
    """Calculate the Moon's sidereal longitude at birth using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
    moon_pos, ret = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    if ret < 0:
        raise ValueError("Error in Moon position calculation")
    return moon_pos[0] % 360.0  # Normalize to 0-360 degrees


def determine_birth_mahadasha_planet_one_year(moon_longitude):
    """Determine the ruling planet based on the Moon's nakshatra position."""
    nakshatra_index = int(moon_longitude // DEGREES_PER_NAKSHATRA)
    return PLANET_ORDER[nakshatra_index % 9]


def calculate_remaining_mahadasha_duration_one_year(moon_longitude, ruling_planet):
    """Calculate the remaining days of the starting Mahadasha."""
    degrees_traversed = moon_longitude % DEGREES_PER_NAKSHATRA
    proportion_traversed = degrees_traversed / DEGREES_PER_NAKSHATRA
    total_years = MAHADASHA_DURATIONS[ruling_planet]
    remaining_years = total_years * (1 - proportion_traversed)
    return remaining_years * SIDEREAL_YEAR  # Convert to days


def jd_to_datetime_one_year(jd):
    """Convert Julian Day to a formatted date-time string (YYYY-MM-DD HH:MM:SS)."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    dt = datetime(year, month, day, int(hour), int((hour % 1) * 60), int(((hour % 1) * 60) % 1 * 60))
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_antardasha_distribution_one_year(mahadasha_planet, mahadasha_duration_years):
    """Calculate durations of all Antardashas within a Mahadasha in years."""
    antardasha_durations = []
    start_index = PLANET_ORDER.index(mahadasha_planet)
    for i in range(9):
        planet = PLANET_ORDER[(start_index + i) % 9]
        duration = (mahadasha_duration_years * MAHADASHA_DURATIONS[planet]) / TOTAL_VIMSHOTTARI_CYCLE
        antardasha_durations.append((planet, duration))
    return antardasha_durations


def calculate_pratyantardasha_distribution_one_year(antardasha_planet, antardasha_duration_years):
    """Calculate durations of all Pratyantardashas within an Antardasha in years."""
    pratyantardasha_durations = []
    start_index = PLANET_ORDER.index(antardasha_planet)
    for i in range(9):
        planet = PLANET_ORDER[(start_index + i) % 9]
        duration = (antardasha_duration_years * MAHADASHA_DURATIONS[planet]) / TOTAL_VIMSHOTTARI_CYCLE
        pratyantardasha_durations.append((planet, duration))
    return pratyantardasha_durations


# ==================== REPORT GENERATION FUNCTIONS ====================

def generate_mahadasha_report_one_year(start_jd, ruling_planet, remaining_days):
    """Generate the full Mahadasha timeline starting from birth."""
    timeline = []
    current_jd = start_jd
    start_index = PLANET_ORDER.index(ruling_planet)

    # First Mahadasha (remaining duration)
    end_jd = current_jd + remaining_days
    timeline.append({
        'planet': ruling_planet,
        'start': jd_to_datetime_one_year(current_jd),
        'end': jd_to_datetime_one_year(end_jd),
        'duration_years': remaining_days / SIDEREAL_YEAR,
        'start_jd': current_jd,
        'end_jd': end_jd
    })
    current_jd = end_jd

    # Subsequent Mahadashas (full durations)
    for i in range(1, 9):
        planet_index = (start_index + i) % 9
        planet = PLANET_ORDER[planet_index]
        duration_years = MAHADASHA_DURATIONS[planet]
        duration_days = duration_years * SIDEREAL_YEAR
        end_jd = current_jd + duration_days
        timeline.append({
            'planet': planet,
            'start': jd_to_datetime_one_year(current_jd),
            'end': jd_to_datetime_one_year(end_jd),
            'duration_years': duration_years,
            'start_jd': current_jd,
            'end_jd': end_jd
        })
        current_jd = end_jd

    return timeline


def generate_antardasha_report_one_year(mahadasha_start_jd, antardasha_durations):
    """Generate the Antardasha timeline within a Mahadasha."""
    timeline = []
    current_jd = mahadasha_start_jd
    for planet, duration_years in antardasha_durations:
        duration_days = duration_years * SIDEREAL_YEAR
        end_jd = current_jd + duration_days
        timeline.append({
            'planet': planet,
            'start': jd_to_datetime_one_year(current_jd),
            'end': jd_to_datetime_one_year(end_jd),
            'start_jd': current_jd,
            'end_jd': end_jd
        })
        current_jd = end_jd
    return timeline


def generate_pratyantardasha_report_one_year(antardasha_start_jd, pratyantardasha_durations):
    """Generate the Pratyantardasha timeline within an Antardasha."""
    timeline = []
    current_jd = antardasha_start_jd
    for planet, duration_years in pratyantardasha_durations:
        duration_days = duration_years * SIDEREAL_YEAR
        end_jd = current_jd + duration_days
        timeline.append({
            'planet': planet,
            'start': jd_to_datetime_one_year(current_jd),
            'end': jd_to_datetime_one_year(end_jd)
        })
        current_jd = end_jd
    return timeline


# ==================== CORE CALCULATION FUNCTION ====================

def calculate_complete_dasha_report_one_year(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """Calculate complete Vimshottari Dasha report with all levels."""
    
    # Step 1: Calculate Julian Day from birth details
    jd = get_julian_day_one_year(birth_date, birth_time, tz_offset)

    # Step 2: Calculate Moon's sidereal longitude
    moon_longitude = calculate_moon_sidereal_longitude_one_year(jd)

    # Step 3: Determine starting Mahadasha planet
    ruling_planet = determine_birth_mahadasha_planet_one_year(moon_longitude)

    # Step 4: Calculate remaining Mahadasha duration
    remaining_days = calculate_remaining_mahadasha_duration_one_year(moon_longitude, ruling_planet)

    # Step 5: Generate Mahadasha timeline
    mahadasha_timeline = generate_mahadasha_report_one_year(jd, ruling_planet, remaining_days)

    # Step 6: Calculate Antardashas and Pratyantardashas for each Mahadasha
    for maha in mahadasha_timeline:
        # Calculate Antardasha durations
        antardasha_durations = calculate_antardasha_distribution_one_year(maha['planet'], maha['duration_years'])
        
        # Validate Antardasha durations
        total_antardasha_years = sum(duration for _, duration in antardasha_durations)
        if abs(total_antardasha_years - maha['duration_years']) > 0.01:
            raise ValueError(f"Antardasha durations do not sum to Mahadasha duration for {maha['planet']}")

        # Generate Antardasha timeline
        antardasha_timeline = generate_antardasha_report_one_year(maha['start_jd'], antardasha_durations)
        maha['antardashas'] = antardasha_timeline

        # Calculate Pratyantardashas for each Antardasha
        for antar in maha['antardashas']:
            pratyantardasha_durations = calculate_pratyantardasha_distribution_one_year(
                antar['planet'], 
                (antar['end_jd'] - antar['start_jd']) / SIDEREAL_YEAR
            )
            pratyantardasha_timeline = generate_pratyantardasha_report_one_year(
                antar['start_jd'], 
                pratyantardasha_durations
            )
            antar['pratyantardashas'] = pratyantardasha_timeline

    # Remove start_jd and end_jd for cleaner output
    for maha in mahadasha_timeline:
        maha.pop('start_jd', None)
        maha.pop('end_jd', None)
        for antar in maha.get('antardashas', []):
            antar.pop('start_jd', None)
            antar.pop('end_jd', None)

    return mahadasha_timeline


# ==================== FILTERING FUNCTIONS ====================

def filter_dasha_report_by_date_range_one_year(mahadasha_timeline, start_date, end_date):
    """
    Filter the complete dasha report to include only periods within the specified date range.
    
    Args:
        mahadasha_timeline: Complete Mahadasha timeline
        start_date: Start date of the filter range (datetime object)
        end_date: End date of the filter range (datetime object)
    
    Returns:
        Filtered Mahadasha timeline
    """
    filtered_timeline = []
    
    for maha in mahadasha_timeline:
        maha_start = datetime.strptime(maha['start'], '%Y-%m-%d %H:%M:%S')
        maha_end = datetime.strptime(maha['end'], '%Y-%m-%d %H:%M:%S')
        
        # Check if Mahadasha overlaps with the date range
        if maha_end < start_date or maha_start > end_date:
            continue  # Skip this Mahadasha entirely
        
        # Create a copy of Mahadasha for filtered result
        filtered_maha = {
            'planet': maha['planet'],
            'start': maha['start'],
            'end': maha['end'],
            'duration_years': maha['duration_years'],
            'antardashas': []
        }
        
        # Filter Antardashas
        for antar in maha.get('antardashas', []):
            antar_start = datetime.strptime(antar['start'], '%Y-%m-%d %H:%M:%S')
            antar_end = datetime.strptime(antar['end'], '%Y-%m-%d %H:%M:%S')
            
            # Check if Antardasha overlaps with the date range
            if antar_end < start_date or antar_start > end_date:
                continue
            
            # Create a copy of Antardasha for filtered result
            filtered_antar = {
                'planet': antar['planet'],
                'start': antar['start'],
                'end': antar['end'],
                'pratyantardashas': []
            }
            
            # Filter Pratyantardashas
            for pratya in antar.get('pratyantardashas', []):
                pratya_start = datetime.strptime(pratya['start'], '%Y-%m-%d %H:%M:%S')
                pratya_end = datetime.strptime(pratya['end'], '%Y-%m-%d %H:%M:%S')
                
                # Check if Pratyantardasha overlaps with the date range
                if pratya_end < start_date or pratya_start > end_date:
                    continue
                
                # Add Pratyantardasha to filtered result
                filtered_antar['pratyantardashas'].append({
                    'planet': pratya['planet'],
                    'start': pratya['start'],
                    'end': pratya['end']
                })
            
            # Only add Antardasha if it has Pratyantardashas
            if filtered_antar['pratyantardashas']:
                filtered_maha['antardashas'].append(filtered_antar)
        
        # Only add Mahadasha if it has Antardashas
        if filtered_maha['antardashas']:
            filtered_timeline.append(filtered_maha)
    
    return filtered_timeline