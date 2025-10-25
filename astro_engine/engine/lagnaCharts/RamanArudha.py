import swisseph as swe
from datetime import datetime, timedelta

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

def get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Raman Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    return houses[0][0]  # Ascendant longitude

def calculate_planet_data(jd, planet_code):
    """Calculate sidereal longitude and retrograde status of a planet."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if ret < 0:
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    longitude = pos[0]
    speed = pos[3]  # Speed in longitude
    is_retrograde = speed < 0
    return longitude, is_retrograde

def get_sign(longitude):
    """Determine zodiac sign from sidereal longitude."""
    sign_index = int(longitude // 30) % 12
    return ZODIAC_SIGNS[sign_index]

def get_nakshatra_pada(longitude):
    """Determine nakshatra and pada from sidereal longitude."""
    longitude = longitude % 360
    nakshatra_index = int(longitude / 13.3333)
    nakshatra_start = nakshatra_index * 13.3333
    position_in_nakshatra = longitude - nakshatra_start
    pada = min(int(position_in_nakshatra / 3.3333) + 1, 4)  # Ensure pada <= 4
    nakshatra_name = NAKSHATRAS[nakshatra_index % 27]
    return nakshatra_name, pada

def get_arudha_lagna(asc_sign, lord_sign):
    """Calculate Arudha Lagna based on Ascendant and Lagna lord's sign."""
    asc_index = ZODIAC_SIGNS.index(asc_sign)
    lord_index = ZODIAC_SIGNS.index(lord_sign)
    if asc_sign == lord_sign:
        al_index = (asc_index + 9) % 12  # 10th house from Ascendant
    elif (lord_index - asc_index) % 12 == 6:
        al_index = (asc_index + 3) % 12  # 4th house from Ascendant
    else:
        count = (lord_index - asc_index) % 12 + 1
        al_index = (lord_index + count - 1) % 12
    return ZODIAC_SIGNS[al_index]

def raman_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """Calculate Arudha Lagna chart with retrograde status, nakshatras, and padas."""
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate sidereal Ascendant and its sign
    asc_lon = calculate_ascendant(jd, latitude, longitude)
    asc_sign = get_sign(asc_lon)
    asc_nakshatra, asc_pada = get_nakshatra_pada(asc_lon)

    # Calculate planetary positions
    planet_data = {}
    for planet, code in zip(PLANETS, SWE_PLANETS):
        if planet == 'Ketu':
            rahu_lon, rahu_retro = planet_data['Rahu']['longitude'], planet_data['Rahu']['retrograde']
            ketu_lon = (rahu_lon + 180) % 360
            ketu_retro = rahu_retro
            lon = ketu_lon
            retro = ketu_retro
        else:
            lon, retro = calculate_planet_data(jd, code)
        sign = get_sign(lon)
        nakshatra, pada = get_nakshatra_pada(lon)
        planet_data[planet] = {
            'longitude': lon,
            'sign': sign,
            'nakshatra': nakshatra,
            'pada': pada,
            'retrograde': retro
        }

    # Determine Lagna lord and its sign
    lagna_lord = LORDS[asc_sign]
    lord_sign = planet_data[lagna_lord]['sign']

    # Calculate Arudha Lagna
    al_sign = get_arudha_lagna(asc_sign, lord_sign)
    al_index = ZODIAC_SIGNS.index(al_sign)

    # Calculate houses relative to Arudha Lagna
    for planet in planet_data:
        sign_index = ZODIAC_SIGNS.index(planet_data[planet]['sign'])
        house = (sign_index - al_index) % 12 + 1
        planet_data[planet]['house'] = house

    # Construct response
    response = {
        'user_name': user_name,
        'ascendant': {
            'sign': asc_sign,
            'longitude': asc_lon,
            'nakshatra': asc_nakshatra,
            'pada': asc_pada
        },
        'arudha_lagna': al_sign,
        'planets': {
            planet: {
                'longitude': data['longitude'],
                'sign': data['sign'],
                'nakshatra': data['nakshatra'],
                'pada': data['pada'],
                'house': data['house'],
                'retrograde': data['retrograde']
            } for planet, data in planet_data.items()
        },
        'metadata': {
            'ayanamsa': 'Raman',
            'calculation_time': datetime.utcnow().isoformat(),
            'input': {
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': tz_offset
            }
        }
    }
    return response