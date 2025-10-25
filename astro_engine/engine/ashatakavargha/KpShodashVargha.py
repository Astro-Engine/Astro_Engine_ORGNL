from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
swe.set_ephe_path('astro_engine/ephe')
swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)  # KP New ayanamsa

SIGNS_kp = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
ELEMENTS = {
    0: 'fire', 1: 'earth', 2: 'air', 3: 'water',
    4: 'fire', 5: 'earth', 6: 'air', 7: 'water',
    8: 'fire', 9: 'earth', 10: 'air', 11: 'water'
}
MOVABLE = [0, 3, 6, 9]
FIXED = [1, 4, 7, 10]
DUAL = [2, 5, 8, 11]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}
CHARTS_kp = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10",
    "D12", "D16", "D20", "D24", "D27", "D30", "D40",
    "D45", "D60"
]

def local_to_utc_kp(birth_date, birth_time, timezone_offset):
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    return dt - timedelta(hours=float(timezone_offset))

def julian_day_kp(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)

def get_sidereal_positions_kp(jd):
    positions = {}
    for pname, code in PLANETS.items():
        pos, _ = swe.calc_ut(jd, code, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        lon = pos[0] % 360
        sign_idx = int(lon // 30)
        deg_in_sign = lon % 30
        positions[pname] = (lon, sign_idx, deg_in_sign)
    # Ketu: always 180° from Rahu
    positions['Ketu'] = (
        (positions['Rahu'][0] + 180) % 360,
        int(((positions['Rahu'][0] + 180) % 360) // 30),
        (positions['Rahu'][0] + 180) % 30
    )
    return positions

def get_sidereal_asc_kp(jd, lat, lon):
    house_cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus house system
    ayanamsa = swe.get_ayanamsa_ut(jd)
    tropical_asc = ascmc[0]
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    sign_idx = int(sidereal_asc // 30)
    deg_in_sign = sidereal_asc % 30
    return sidereal_asc, sign_idx, deg_in_sign

def varga_sign_kp(natal_sign, deg_in_sign, chart):
    # Implements exact BPHS/standard rules for all Vargas
    if chart == "D1":
        return natal_sign
    if chart == "D2":
        if natal_sign % 2 == 0:
            return 4 if deg_in_sign < 15 else 3
        else:
            return 3 if deg_in_sign < 15 else 4
    if chart == "D3":
        if deg_in_sign < 10:
            return natal_sign
        elif deg_in_sign < 20:
            return (natal_sign + 4) % 12
        else:
            return (natal_sign + 8) % 12
    if chart == "D4":
        if deg_in_sign < 7.5:
            return natal_sign
        elif deg_in_sign < 15:
            return (natal_sign + 3) % 12
        elif deg_in_sign < 22.5:
            return (natal_sign + 6) % 12
        else:
            return (natal_sign + 9) % 12
    if chart == "D7":
        part = int(deg_in_sign * 7 // 30)
        start = natal_sign if natal_sign % 2 == 0 else (natal_sign + 6) % 12
        return (start + part) % 12
    if chart == "D9":
        part = int(deg_in_sign * 9 // 30)
        element = ELEMENTS[natal_sign]
        start = {'fire': 0, 'earth': 9, 'air': 6, 'water': 3}[element]
        return (start + part) % 12
    if chart == "D10":
        part = int(deg_in_sign * 10 // 30)
        start = natal_sign if natal_sign % 2 == 0 else (natal_sign + 8) % 12
        return (start + part) % 12
    if chart == "D12":
        part = int(deg_in_sign * 12 // 30)
        return (natal_sign + part) % 12
    if chart == "D16":
        part = int(deg_in_sign * 16 // 30)
        if natal_sign in MOVABLE:
            start = 0
        elif natal_sign in FIXED:
            start = 4
        else:
            start = 8
        return (start + part) % 12
    if chart == "D20":
        part = int(deg_in_sign * 20 // 30)
        element = ELEMENTS[natal_sign]
        start = {'fire': 0, 'earth': 8, 'air': 4, 'water': 2}[element]
        return (start + part) % 12
    if chart == "D24":
        part = int(deg_in_sign * 24 // 30)
        start = 4 if natal_sign % 2 == 0 else 3
        return (start + part) % 12
    if chart == "D27":
        part = int(deg_in_sign * 27 // 30)
        element = ELEMENTS[natal_sign]
        start = {'fire': 0, 'earth': 3, 'air': 6, 'water': 9}[element]
        return (start + part) % 12
    if chart == "D30":
        odd = natal_sign % 2 == 0
        if odd:
            if deg_in_sign < 5:
                return 0
            elif deg_in_sign < 10:
                return 10
            elif deg_in_sign < 18:
                return 2
            elif deg_in_sign < 25:
                return 6
            else:
                return 8
        else:
            if deg_in_sign < 5:
                return 1
            elif deg_in_sign < 12:
                return 5
            elif deg_in_sign < 20:
                return 11
            elif deg_in_sign < 25:
                return 9
            else:
                return 7
    if chart == "D40":
        part = int(deg_in_sign * 40 // 30)
        start = 0 if natal_sign % 2 == 0 else 6
        return (start + part) % 12
    if chart == "D45":
        part = int(deg_in_sign * 45 // 30)
        start = 0 if natal_sign % 2 == 0 else 8
        return (start + part) % 12
    if chart == "D60":
        part = int(deg_in_sign * 60 // 30)
        return (natal_sign + part) % 12
    raise ValueError("Unknown Varga chart: %s" % chart)