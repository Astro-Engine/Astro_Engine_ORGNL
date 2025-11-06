# pmp_calculations.py
import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path (ensure ephemeris files are present)
swe.set_ephe_path('astro_api/ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_house(lon, asc_sign_index, orientation_shift=0):
    """
    Calculate house number based on planet longitude and ascendant sign index for Whole Sign system.
    """
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_strength_level(score):
    """Convert numerical strength score to descriptive level."""
    if score >= 140:
        return "Exceptionally Strong"
    elif score >= 125:
        return "Very Strong"
    elif score >= 110:
        return "Strong"
    elif score >= 100:
        return "Moderate"
    else:
        return "Weak"

def check_pancha_mahapurusha_yogas(planetary_positions):
    """
    Check for Pancha Mahapurusha Yogas based on precise Vedic astrology rules.
    NOTE: This logic is preserved exactly from your script.
    """
    yogas = []

    # Define planetary dignities (own signs and exaltation signs)
    planet_dignities = {
        'Mars': {
            'own': ['Aries', 'Scorpio'],
            'exaltation': ['Capricorn'],
            'yoga_name': 'Ruchaka Yoga',
            'results': 'Physical strength, courage, leadership, military success, athletic abilities'
        },
        'Mercury': {
            'own': ['Gemini', 'Virgo'],
            'exaltation': ['Virgo'],
            'yoga_name': 'Bhadra Yoga',
            'results': 'Intelligence, communication skills, business acumen, scholarly achievements'
        },
        'Jupiter': {
            'own': ['Sagittarius', 'Pisces'],
            'exaltation': ['Cancer'],
            'yoga_name': 'Hamsa Yoga',
            'results': 'Wisdom, spirituality, teaching abilities, good fortune, respect in society'
        },
        'Venus': {
            'own': ['Taurus', 'Libra'],
            'exaltation': ['Pisces'],
            'yoga_name': 'Malavya Yoga',
            'results': 'Beauty, artistic talents, luxury, harmonious relationships, material comforts'
        },
        'Saturn': {
            'own': ['Capricorn', 'Aquarius'],
            'exaltation': ['Libra'],
            'yoga_name': 'Shasha Yoga',
            'results': 'Discipline, hard work, organizational skills, longevity, success through perseverance'
        }
    }

    # Kendra houses (angular houses)
    kendra_houses = [1, 4, 7, 10]

    for planet, dignities in planet_dignities.items():
        if planet in planetary_positions:
            planet_data = planetary_positions[planet]
            planet_sign = planet_data['sign']
            planet_house = planet_data['house']
            planet_retrograde = planet_data['retrograde']

            # Dignity checks
            is_in_own_sign = planet_sign in dignities['own']
            is_in_exaltation = planet_sign in dignities['exaltation']
            is_dignified = is_in_own_sign or is_in_exaltation

            # Kendra placement
            is_in_kendra = planet_house in kendra_houses

            # Simplified conditions from your code (left unchanged)
            is_not_combust = True
            is_not_heavily_afflicted = True

            # Yoga formation
            if is_dignified and is_in_kendra and is_not_combust and is_not_heavily_afflicted:
                # Dignity type
                if is_in_own_sign and is_in_exaltation:
                    dignity_type = "Own Sign & Exaltation"  # For Mercury in Virgo
                elif is_in_own_sign:
                    dignity_type = "Own Sign"
                else:
                    dignity_type = "Exaltation"

                # Strength (unchanged)
                strength_score = 100
                if planet_house == 1:
                    strength_score += 20
                elif planet_house == 10:
                    strength_score += 15
                elif planet_house in [4, 7]:
                    strength_score += 10

                if is_in_exaltation:
                    strength_score += 25
                elif is_in_own_sign:
                    strength_score += 20

                if planet_retrograde == 'R':
                    strength_score -= 10

                yoga_info = {
                    'yoga_name': dignities['yoga_name'],
                    'planet': planet,
                    'sign': planet_sign,
                    'house': planet_house,
                    'dignity_type': dignity_type,
                    'retrograde': planet_retrograde,
                    'strength_score': strength_score,
                    'strength_level': get_strength_level(strength_score),
                    'results': dignities['results'],
                    'formation_details': {
                        'is_in_own_sign': is_in_own_sign,
                        'is_in_exaltation': is_in_exaltation,
                        'is_in_kendra': is_in_kendra,
                        'kendra_house': planet_house
                    }
                }
                yogas.append(yoga_info)

    return yogas

# -------------------------
# Public wrapper as requested
# -------------------------
def panchaMahapursha(planetary_positions):
    """
    Public function (name required by user): returns detected Pancha Mahapurusha yogas.
    It simply delegates to check_pancha_mahapurusha_yogas without any changes.
    """
    return check_pancha_mahapurusha_yogas(planetary_positions)

# -------------------------
# Chart/natal helpers used by API (logic preserved)
# -------------------------
def compute_natal_core(birth_data):
    """
    Shared natal core computation (positions, houses, signs).
    Returns:
      {
        'planet_positions': dict[name] = (lon, 'R'|''),
        'ascendant_lon': float,
        'asc_sign_index': int,
        'asc_sign': str,
        'house_signs_list': [{'sign', 'start_longitude'}, ...],
        'ayanamsa_value': float,
        'jd_ut': float
      }
    """
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])

    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # ayanamsa (Lahiri already set)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Planetary positions (as in your original code)
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
            raise RuntimeError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Ketu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Ascendant & houses (Whole Sign)
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # House signs (list like your original loop)
    house_signs = []
    for i in range(12):
        sign_index = (asc_sign_index + i) % 12
        sign_start_lon = (sign_index * 30)
        house_signs.append({"sign": signs[sign_index], "start_longitude": sign_start_lon})

    return {
        "planet_positions": planet_positions,
        "ascendant_lon": ascendant_lon,
        "asc_sign_index": asc_sign_index,
        "asc_sign": asc_sign,
        "house_signs_list": house_signs,
        "ayanamsa_value": ayanamsa_value,
        "jd_ut": jd_ut
    }

def format_planetary_positions_for_output(planet_positions, asc_sign_index, orientation_shift=0):
    """
    Produces the same structure you return in both endpoints.
    """
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        house = get_house(lon, asc_sign_index, orientation_shift=orientation_shift)
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": format_dms(sign_deg),
            "retrograde": retro,
            "house": house,
            "longitude": lon  # keep raw lon for /pancha-mahapurusha-yogas usage
        }
    return planetary_positions_json

def format_house_signs_dict(house_signs_list):
    return {
        f"House {i+1}": {
            "sign": house["sign"],
            "start_longitude": format_dms(house["start_longitude"])
        }
        for i, house in enumerate(house_signs_list)
    }
