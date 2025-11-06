# malefic_calculations.py
from datetime import datetime, timedelta
import swisseph as swe

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Define benefic and malefic planets
NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Moon']
NATURAL_MALEFICS = ['Mars', 'Saturn', 'Rahu', 'Ketu', 'Sun']  # Sun is mild malefic

def get_house(lon, asc_sign_index, orientation_shift=0):
    """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def get_sign_index(lon):
    """Get sign index (0-11) from longitude."""
    return int(lon // 30) % 12

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def is_mercury_benefic(planet_positions):
    """Determine if Mercury is benefic or malefic based on associations."""
    mercury_house = planet_positions['Mercury']['house']
    mercury_lon = planet_positions['Mercury']['longitude']
    
    # Check if Mercury is with benefics or malefics
    CONJUNCTION_ORB = 10
    
    benefic_association = False
    malefic_association = False
    
    for planet, data in planet_positions.items():
        if planet != 'Mercury':
            if data['house'] == mercury_house:
                # Check conjunction by longitude
                diff = abs(mercury_lon - data['longitude'])
                if diff > 180:
                    diff = 360 - diff
                
                if diff <= CONJUNCTION_ORB:
                    if planet in NATURAL_BENEFICS:
                        benefic_association = True
                    elif planet in NATURAL_MALEFICS:
                        malefic_association = True
    
    # If with benefics, Mercury is benefic; if with malefics, Mercury is malefic
    # If alone or neutral, Mercury is considered benefic by default
    return benefic_association or not malefic_association

def calculate_natal_chart(birth_data):
    """Calculate natal chart data."""
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    
    # Parse date and time
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)  # calculated but (as in original) not returned

    # Planetary positions
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planet_positions = {}
    
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = {
            'longitude': lon,
            'retrograde': retrograde,
            'speed': speed
        }

    # Calculate Ketu as 180° opposite Rahu
    rahu_lon = planet_positions['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = {
        'longitude': ketu_lon,
        'retrograde': '',
        'speed': 0
    }

    # Ascendant calculation
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)

    # Calculate houses for all planets
    planet_houses = {}
    for planet, data in planet_positions.items():
        house = get_house(data['longitude'], asc_sign_index)
        planet_houses[planet] = house
        planet_positions[planet]['house'] = house
        planet_positions[planet]['sign_index'] = get_sign_index(data['longitude'])

    return planet_positions, planet_houses, asc_sign_index, ascendant_lon

def check_paapa_kartari_yoga(planet_positions):
    """Check for Paapa Kartari Yoga - benefic hemmed between malefics in 2nd and 12th houses."""
    yogas = []
    
    # Determine Mercury's nature
    mercury_is_benefic = is_mercury_benefic(planet_positions)
    effective_benefics = NATURAL_BENEFICS.copy()
    effective_malefics = NATURAL_MALEFICS.copy()
    
    if mercury_is_benefic:
        effective_benefics.append('Mercury')
    else:
        effective_malefics.append('Mercury')
    
    for planet, data in planet_positions.items():
        if planet in effective_benefics:
            house = data['house']
            
            # Calculate 2nd and 12th houses from the benefic planet
            second_house = 1 if house == 12 else house + 1
            twelfth_house = 12 if house == 1 else house - 1
            
            # Find planets in 2nd and 12th houses
            planets_in_2nd = [p for p, d in planet_positions.items() if d['house'] == second_house]
            planets_in_12th = [p for p, d in planet_positions.items() if d['house'] == twelfth_house]
            
            # Check if malefics are present in both 2nd and 12th houses
            malefic_in_2nd = any(p in effective_malefics for p in planets_in_2nd)
            malefic_in_12th = any(p in effective_malefics for p in planets_in_12th)
            
            if malefic_in_2nd and malefic_in_12th:
                yogas.append({
                    'type': 'Paapa Kartari Yoga',
                    'affected_planet': planet,
                    'planet_house': house,
                    'description': f'{planet} in house {house} hemmed by malefics in 2nd house ({second_house}) and 12th house ({twelfth_house})',
                    'second_house': second_house,
                    'twelfth_house': twelfth_house,
                    'planets_in_2nd': planets_in_2nd,
                    'planets_in_12th': planets_in_12th,
                    'malefics_in_2nd': [p for p in planets_in_2nd if p in effective_malefics],
                    'malefics_in_12th': [p for p in planets_in_12th if p in effective_malefics]
                })
    
    return yogas

def check_kemadrum_yoga(planet_positions):
    """Check for Kemadrum Yoga - Moon without planets in 2nd and 12th houses from Moon."""
    yogas = []
    moon_house = planet_positions['Moon']['house']
    
    # Calculate 2nd and 12th houses from Moon
    second_house = 1 if moon_house == 12 else moon_house + 1
    twelfth_house = 12 if moon_house == 1 else moon_house - 1
    
    # Find planets in 2nd and 12th houses from Moon (excluding Sun as per classical rule)
    planets_in_2nd = [p for p, d in planet_positions.items() 
                      if d['house'] == second_house and p not in ['Sun', 'Moon']]
    planets_in_12th = [p for p, d in planet_positions.items() 
                       if d['house'] == twelfth_house and p not in ['Sun', 'Moon']]
    
    if not planets_in_2nd and not planets_in_12th:
        yogas.append({
            'type': 'Kemadrum Yoga',
            'affected_planet': 'Moon',
            'moon_house': moon_house,
            'description': f'Moon in house {moon_house} isolated with no planets in 2nd house ({second_house}) and 12th house ({twelfth_house})',
            'second_house': second_house,
            'twelfth_house': twelfth_house,
            'note': 'Sun is excluded from this calculation as per classical rule'
        })
    
    return yogas

def check_shakata_yoga(planet_positions):
    """Check for Shakata Yoga - Moon and Jupiter in 6th, 8th, or 12th from each other by sign position."""
    yogas = []
    moon_sign = planet_positions['Moon']['sign_index']
    jupiter_sign = planet_positions['Jupiter']['sign_index']
    
    # Calculate sign difference both ways
    diff1 = (jupiter_sign - moon_sign) % 12
    diff2 = (moon_sign - jupiter_sign) % 12
    
    # 6th position = 5 difference, 8th position = 7 difference, 12th position = 11 difference
    malefic_positions = [5, 7, 11]  # 6th, 8th, 12th positions (0-based)
    
    if diff1 in malefic_positions or diff2 in malefic_positions:
        # Exclude conjunction (same sign)
        if moon_sign != jupiter_sign:
            if diff1 == 5 or diff2 == 5:
                relation = "6th"
            elif diff1 == 7 or diff2 == 7:
                relation = "8th"
            else:
                relation = "12th"
            
            yogas.append({
                'type': 'Shakata Yoga',
                'affected_planets': ['Moon', 'Jupiter'],
                'description': f'Moon in {signs[moon_sign]} and Jupiter in {signs[jupiter_sign]} are in {relation} sign position',
                'moon_sign': signs[moon_sign],
                'jupiter_sign': signs[jupiter_sign],
                'relation': relation,
                'moon_house': planet_positions['Moon']['house'],
                'jupiter_house': planet_positions['Jupiter']['house']
            })
    
    return yogas

def check_kaal_sarpa_yoga(planet_positions):
    """Check for Kaal Sarpa Yoga - all planets between Rahu-Ketu axis by sign position."""
    yogas = []
    rahu_sign = planet_positions['Rahu']['sign_index']
    ketu_sign = planet_positions['Ketu']['sign_index']
    
    # Get all planets except Rahu and Ketu
    main_planets = [p for p in planet_positions.keys() if p not in ['Rahu', 'Ketu']]
    
    # Method 1: All planets between Rahu and Ketu (clockwise)
    if rahu_sign < ketu_sign:
        arc1_signs = list(range(rahu_sign, ketu_sign + 1))
    else:
        arc1_signs = list(range(rahu_sign, 12)) + list(range(0, ketu_sign + 1))
    
    # Method 2: All planets between Ketu and Rahu (clockwise)  
    if ketu_sign < rahu_sign:
        arc2_signs = list(range(ketu_sign, rahu_sign + 1))
    else:
        arc2_signs = list(range(ketu_sign, 12)) + list(range(0, rahu_sign + 1))
    
    # Check if all planets are in one arc
    planets_in_arc1 = all(planet_positions[p]['sign_index'] in arc1_signs for p in main_planets)
    planets_in_arc2 = all(planet_positions[p]['sign_index'] in arc2_signs for p in main_planets)
    
    if planets_in_arc1 or planets_in_arc2:
        active_arc = arc1_signs if planets_in_arc1 else arc2_signs
        arc_type = "Rahu to Ketu" if planets_in_arc1 else "Ketu to Rahu"
        
        yogas.append({
            'type': 'Kaal Sarpa Yoga',
            'description': f'All planets between {arc_type} axis in signs {[signs[i] for i in active_arc]}',
            'rahu_sign': signs[rahu_sign],
            'ketu_sign': signs[ketu_sign],
            'rahu_house': planet_positions['Rahu']['house'],
            'ketu_house': planet_positions['Ketu']['house'],
            'arc_type': arc_type,
            'planets_in_arc': {p: {'sign': signs[planet_positions[p]['sign_index']], 
                                  'house': planet_positions[p]['house']} for p in main_planets},
            'active_arc_signs': [signs[i] for i in active_arc]
        })
    
    return yogas

def check_conjunction_yogas(planet_positions):
    """Check for conjunction-based malefic yogas with accurate degree-based calculations."""
    yogas = []
    CONJUNCTION_ORB = 10  # degrees
    
    # Check all planetary pairs for conjunctions
    planet_list = list(planet_positions.keys())
    
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            planet1 = planet_list[i]
            planet2 = planet_list[j]
            
            lon1 = planet_positions[planet1]['longitude']
            lon2 = planet_positions[planet2]['longitude']
            
            # Calculate angular distance
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            if diff <= CONJUNCTION_ORB:
                # Check for specific yogas
                yoga_pair = sorted([planet1, planet2])
                house1 = planet_positions[planet1]['house']
                house2 = planet_positions[planet2]['house']
                
                # Use the house of the primary planet (first in alphabetical order)
                primary_house = house1 if planet1 < planet2 else house2
                
                if yoga_pair == ['Jupiter', 'Rahu']:
                    yogas.append({
                        'type': 'Guru Chandal Yoga',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Jupiter and Rahu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Jupiter', 'Ketu']:
                    yogas.append({
                        'type': 'Guru Chandal Yoga',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Jupiter and Ketu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Mars', 'Rahu']:
                    yogas.append({
                        'type': 'Angarak Yoga',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Mars and Rahu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Moon', 'Saturn']:
                    yogas.append({
                        'type': 'Vish Yoga',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Moon and Saturn conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Rahu', 'Sun']:
                    yogas.append({
                        'type': 'Grahan Yoga (Solar Eclipse)',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Sun and Rahu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Ketu', 'Sun']:
                    yogas.append({
                        'type': 'Grahan Yoga (Solar Eclipse)',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Sun and Ketu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Moon', 'Rahu']:
                    yogas.append({
                        'type': 'Grahan Yoga (Lunar Eclipse)',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Moon and Rahu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
                elif yoga_pair == ['Ketu', 'Moon']:
                    yogas.append({
                        'type': 'Grahan Yoga (Lunar Eclipse)',
                        'planets': yoga_pair,
                        'house': primary_house,
                        'orb': round(diff, 2),
                        'description': f'Moon and Ketu conjunct in house {primary_house} (orb: {diff:.2f}°)',
                        'longitudes': {planet1: round(lon1, 2), planet2: round(lon2, 2)}
                    })
    
    return yogas

def calculate_malefic_yogas(planet_positions, planet_houses):
    """Calculate all malefic yogas with corrected rules."""
    all_yogas = []
    all_yogas.extend(check_paapa_kartari_yoga(planet_positions))
    all_yogas.extend(check_kemadrum_yoga(planet_positions))
    all_yogas.extend(check_shakata_yoga(planet_positions))
    all_yogas.extend(check_kaal_sarpa_yoga(planet_positions))
    all_yogas.extend(check_conjunction_yogas(planet_positions))
    return all_yogas

def maleficYoga(birth_data):
    """
    Wrapper that runs the exact same calculations and returns the full response dict.
    (Added per request; logic unchanged.)
    """
    # Calculate natal chart
    planet_positions, planet_houses, asc_sign_index, ascendant_lon = calculate_natal_chart(birth_data)
    # Calculate malefic yogas with corrected rules
    malefic_yogas_found = calculate_malefic_yogas(planet_positions, planet_houses)
    # Determine Mercury's nature for reference
    mercury_is_benefic = is_mercury_benefic(planet_positions)

    # Format planetary positions for output
    planetary_positions_json = {}
    for planet_name, data in planet_positions.items():
        sign, sign_deg, sign_index = longitude_to_sign(data['longitude'])
        dms = format_dms(sign_deg)
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": data['retrograde'],
            "house": data['house'],
            "longitude": round(data['longitude'], 6)
        }

    asc_sign, asc_deg, _ = longitude_to_sign(ascendant_lon)
    ascendant_json = {"sign": asc_sign, "degrees": format_dms(asc_deg)}

    # Build response (identical to original endpoint’s structure)
    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "latitude": float(birth_data['latitude']),
            "longitude": float(birth_data['longitude']),
            "timezone_offset": birth_data['timezone_offset']
        },
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "malefic_yogas": {
            "total_count": len(malefic_yogas_found),
            "yogas_found": malefic_yogas_found
        },
        "yoga_summary": {
            yoga['type']: True for yoga in malefic_yogas_found
        },
        "calculation_details": {
            "mercury_nature": "Benefic" if mercury_is_benefic else "Malefic",
            "natural_benefics": NATURAL_BENEFICS,
            "natural_malefics": NATURAL_MALEFICS
        },
        "notes": {
            "ayanamsa": "Lahiri",
            "chart_type": "Rasi",
            "house_system": "Whole Sign",
            "conjunction_orb": "10 degrees",
            "calculation_method": "Sidereal",
            "paapa_kartari_rule": "Benefic hemmed by malefics in 2nd and 12th houses",
            "kemadrum_rule": "Moon without planets in 2nd and 12th houses (Sun excluded)",
            "shakata_rule": "Moon-Jupiter in 6th/8th/12th sign positions",
            "kaal_sarpa_rule": "All planets between Rahu-Ketu axis by sign position",
            "conjunction_rule": "Planets within 10 degrees longitude difference"
        }
    }
    return response
