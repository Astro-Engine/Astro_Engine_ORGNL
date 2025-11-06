# raj_calculations.py
import swisseph as swe
from datetime import datetime, timedelta

# ----------------------------
# Swiss Ephemeris setup
# ----------------------------
swe.set_ephe_path('astro_api/ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ----------------------------
# Static tables
# ----------------------------
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANET_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

EXALTATION = {
    'Sun': ('Aries', 10), 'Moon': ('Taurus', 3), 'Mars': ('Capricorn', 28),
    'Mercury': ('Virgo', 15), 'Jupiter': ('Cancer', 5), 'Venus': ('Pisces', 27),
    'Saturn': ('Libra', 20), 'Rahu': ('Taurus', 3), 'Ketu': ('Scorpio', 3)
}

DEBILITATION = {
    'Sun': ('Libra', 10), 'Moon': ('Scorpio', 3), 'Mars': ('Cancer', 28),
    'Mercury': ('Pisces', 15), 'Jupiter': ('Capricorn', 5), 'Venus': ('Virgo', 27),
    'Saturn': ('Aries', 20), 'Rahu': ('Scorpio', 3), 'Ketu': ('Taurus', 3)
}

OWN_SIGNS = {
    'Sun': ['Leo'], 'Moon': ['Cancer'], 'Mars': ['Aries', 'Scorpio'],
    'Mercury': ['Gemini', 'Virgo'], 'Jupiter': ['Sagittarius', 'Pisces'],
    'Venus': ['Taurus', 'Libra'], 'Saturn': ['Capricorn', 'Aquarius'],
    'Rahu': [], 'Ketu': []
}

# Natural friendships (asymmetric; use planet->friends only)
NATURAL_FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'],
    'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Mercury', 'Venus'],
    'Rahu': ['Mercury', 'Venus', 'Saturn'],
    'Ketu': ['Mars', 'Jupiter']
}

NATURAL_BENEFICS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
NATURAL_MALEFICS = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}

# Combustion orbs from Sun (degrees)
COMBUSTION_ORBS = {'Moon': 12, 'Mars': 17, 'Mercury': 14, 'Jupiter': 11, 'Venus': 10, 'Saturn': 15}

# Marana Karaka Sthana
MARANA_KARAKA = {'Sun': 12, 'Moon': 8, 'Mars': 7, 'Mercury': 7, 'Jupiter': 3, 'Venus': 6, 'Saturn': 1}

# Functional malefics by ascendant (configurable per your parampara)
FUNCTIONAL_MALEFICS = {
    'Aries': ['Mercury', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
    'Taurus': ['Mars', 'Jupiter', 'Rahu', 'Ketu'],
    'Gemini': ['Jupiter', 'Mars', 'Rahu', 'Ketu'],
    'Cancer': ['Mercury', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
    'Leo': ['Mercury', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
    'Virgo': ['Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu'],
    'Libra': ['Mars', 'Jupiter', 'Rahu', 'Ketu'],
    'Scorpio': ['Mercury', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
    'Sagittarius': ['Mercury', 'Venus', 'Rahu', 'Ketu'],
    'Capricorn': ['Mars', 'Jupiter', 'Sun', 'Moon', 'Rahu', 'Ketu'],
    'Aquarius': ['Mars', 'Jupiter', 'Sun', 'Moon', 'Rahu', 'Ketu'],
    'Pisces': ['Mercury', 'Venus', 'Sun', 'Saturn', 'Rahu', 'Ketu']
}

# ----------------------------
# Helpers
# ----------------------------
def norm360(x): return x % 360.0

def longitude_to_sign(deg):
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = SIGNS[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index

def format_dms(deg):
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_house(lon, asc_sign_index, orientation_shift=0):
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def get_house_lords(asc_sign_index):
    house_lords = {}
    for i in range(12):
        house_num = i + 1
        sign_index = (asc_sign_index + i) % 12
        sign_name = SIGNS[sign_index]
        lord = PLANET_RULERS[sign_name]
        house_lords[house_num] = lord
    return house_lords

def get_planet_house(planet_name, planet_houses):
    return planet_houses.get(planet_name, 0)

def angular_sep(d1, d2):
    return abs((d1 - d2 + 180) % 360 - 180)

def is_waxing(planet_positions):
    if 'Moon' not in planet_positions or 'Sun' not in planet_positions:
        return True
    moon = planet_positions['Moon'][0]
    sun = planet_positions['Sun'][0]
    delta = (moon - sun) % 360
    return 0 < delta < 180

# ----------------------------
# Dignity & conditions
# ----------------------------
def get_planet_dignity(planet, longitude):
    sign, _, _ = longitude_to_sign(longitude)

    if planet in EXALTATION:
        exalt_sign, _ = EXALTATION[planet]
        if sign == exalt_sign:
            return 'exalted', True

    if planet in DEBILITATION:
        debil_sign, _ = DEBILITATION[planet]
        if sign == debil_sign:
            return 'debilitated', False

    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 'own', True

    sign_lord = PLANET_RULERS[sign]
    if sign_lord in NATURAL_FRIENDS.get(planet, []):
        return 'friendly', True

    if sign_lord in NATURAL_MALEFICS and planet in NATURAL_BENEFICS:
        return 'enemy', False

    return 'neutral', True

def is_combust(planet, planet_positions):
    if planet in ['Sun', 'Rahu', 'Ketu']:
        return False
    if planet not in planet_positions or 'Sun' not in planet_positions:
        return False
    p_lon = planet_positions[planet][0]
    s_lon = planet_positions['Sun'][0]
    distance = angular_sep(p_lon, s_lon)
    if planet == 'Mercury' and distance <= 12:
        return False
    orb = COMBUSTION_ORBS.get(planet, 10)
    return distance <= orb

def is_in_papa_kartari(house, planet_houses, planet_positions):
    prev_house = ((house - 2) % 12) + 1
    next_house = (house % 12) + 1
    malefics = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}
    if not is_waxing(planet_positions):
        malefics.add('Moon')
    return any(planet_houses.get(p) == prev_house for p in malefics) and \
           any(planet_houses.get(p) == next_house for p in malefics)

def is_in_marana_karaka(planet, planet_house):
    if planet not in MARANA_KARAKA:
        return False
    return planet_house == MARANA_KARAKA[planet]

# ----------------------------
# Aspects & Exchanges
# ----------------------------
def planet_aspects_house(planet, from_house, to_house):
    if not from_house or not to_house:
        return False
    aspects = [7]
    if planet == 'Mars':
        aspects = [4, 7, 8]
    elif planet == 'Jupiter':
        aspects = [5, 7, 9]
    elif planet == 'Saturn':
        aspects = [3, 7, 10]
    elif planet in ['Rahu', 'Ketu']:
        aspects = [5, 7, 9]

    for a in aspects:
        aspected_house = ((from_house - 1 + a - 1) % 12) + 1
        if aspected_house == to_house:
            return True
    return False

def find_planetary_conjunctions(planet_houses):
    conj = {}
    for planet, house in planet_houses.items():
        conj.setdefault(house, []).append(planet)
    return {h: ps for h, ps in conj.items() if len(ps) >= 2}

def check_parivartana(planet1, planet2, planet_positions, house_lords, asc_sign_index):
    if planet1 not in planet_positions or planet2 not in planet_positions:
        return False, None

    p1_rules = [h for h, lord in house_lords.items() if lord == planet1]
    p2_rules = [h for h, lord in house_lords.items() if lord == planet2]
    if not p1_rules or not p2_rules:
        return False, None

    p1_lon = planet_positions[planet1][0]
    p2_lon = planet_positions[planet2][0]
    p1_sign_index = int(p1_lon // 30) % 12
    p2_sign_index = int(p2_lon // 30) % 12

    pairs = []
    for h1 in p1_rules:
        s1 = (asc_sign_index + h1 - 1) % 12
        for h2 in p2_rules:
            s2 = (asc_sign_index + h2 - 1) % 12
            if p1_sign_index == s2 and p2_sign_index == s1:
                pairs.append((h1, h2))

    if not pairs:
        return False, None

    kendras = {1, 4, 7, 10}
    trikonas = {1, 5, 9}
    dusthanas = {6, 8, 12}
    good = kendras | trikonas

    h1, h2 = pairs[0]
    if h1 in good and h2 in good:
        return True, 'Maha Parivartana'
    if h1 in dusthanas and h2 in dusthanas:
        return True, 'Dainya Parivartana'
    return True, 'Kahala Parivartana'

# ----------------------------
# Strength model
# ----------------------------
def calculate_planet_strength(planet, planet_positions, planet_houses, asc_sign):
    if planet not in planet_positions or planet not in planet_houses:
        return 0

    strength = 50

    lon = planet_positions[planet][0]
    dignity, _ = get_planet_dignity(planet, lon)
    dignity_scores = {'exalted': 30, 'own': 25, 'friendly': 15, 'neutral': 5, 'enemy': -10, 'debilitated': -30}
    strength += dignity_scores.get(dignity, 0)

    house = planet_houses[planet]
    house_scores = {
        1: 30, 4: 25, 5: 30, 7: 25, 9: 30, 10: 30,
        2: 12, 11: 10, 3: 8, 6: -15, 8: -20, 12: -10
    }
    strength += house_scores.get(house, 0)

    if is_combust(planet, planet_positions):
        strength -= 30

    if is_in_papa_kartari(house, planet_houses, planet_positions):
        strength -= 20

    if is_in_marana_karaka(planet, house):
        strength -= 25

    if planet in FUNCTIONAL_MALEFICS.get(asc_sign, []):
        strength -= 15

    p_lon = planet_positions[planet][0]
    for other, (o_lon, _) in planet_positions.items():
        if other == planet:
            continue
        sep = angular_sep(p_lon, o_lon)
        if sep <= 6:
            if other in {'Rahu', 'Ketu'}:
                strength -= 22
            elif other in {'Mars', 'Saturn', 'Sun'}:
                strength -= 12
            elif other in {'Jupiter', 'Venus', 'Mercury', 'Moon'}:
                strength += 6
        elif sep <= 8:
            if other in {'Rahu', 'Ketu'}:
                strength -= 15
            elif other in {'Mars', 'Saturn', 'Sun'}:
                strength -= 8
            elif other in {'Jupiter', 'Venus', 'Mercury', 'Moon'}:
                strength += 4

    return max(0, min(100, strength))

def check_cancellations(planet, planet_positions, planet_houses, asc_sign):
    cancellations = []
    if planet not in planet_positions or planet not in planet_houses:
        return cancellations
    if is_combust(planet, planet_positions):
        cancellations.append(f"{planet}_combust")
    lon = planet_positions[planet][0]
    dignity, _ = get_planet_dignity(planet, lon)
    if dignity == 'debilitated':
        cancellations.append(f"{planet}_debilitated")
    house = planet_houses[planet]
    if is_in_papa_kartari(house, planet_houses, planet_positions):
        cancellations.append(f"{planet}_papa_kartari")
    if is_in_marana_karaka(planet, house):
        cancellations.append(f"{planet}_marana_karaka")
    if house in [6, 8, 12]:
        cancellations.append(f"{planet}_in_dusthana")
    if planet in FUNCTIONAL_MALEFICS.get(asc_sign, []):
        cancellations.append(f"{planet}_functional_malefic")
    return cancellations

def validate_yoga_strength(planets_involved, planet_positions, planet_houses, asc_sign):
    if not planets_involved:
        return 0, []
    total = 0
    cancels = []
    for p in planets_involved:
        total += calculate_planet_strength(p, planet_positions, planet_houses, asc_sign)
        cancels.extend(check_cancellations(p, planet_positions, planet_houses, asc_sign))
    avg = total / len(planets_involved)
    return avg, cancels

# ----------------------------
# Yoga detectors
# ----------------------------
def check_kendra_trikona_raj_yoga(planet_houses, house_lords, planet_positions, asc_sign, asc_sign_index):
    kendras = [1, 4, 7, 10]
    trikonas = [1, 5, 9]
    raj_yogas = []
    processed = set()

    conjunctions = find_planetary_conjunctions(planet_houses)
    eighth_lord = house_lords[8]

    lord_to_houses = {}
    for h, l in house_lords.items():
        lord_to_houses.setdefault(l, []).append(h)
    for planet, houses in lord_to_houses.items():
        if planet == eighth_lord:
            continue
        ks = [h for h in houses if h in kendras]
        ts = [h for h in houses if h in trikonas]
        for k in ks:
            for t in ts:
                if k == t:
                    continue
                key = f"kt_dual_{planet}_{min(k,t)}_{max(k,t)}"
                if key in processed:
                    continue
                processed.add(key)
                strength, canc = validate_yoga_strength([planet], planet_positions, planet_houses, asc_sign)
                if strength >= 30:
                    raj_yogas.append({
                        "type": "Kendra-Trikona Raj Yoga",
                        "subtype": "Same Planet Rules Both",
                        "description": f"{planet} rules {k}H (Kendra) and {t}H (Trikona)",
                        "houses": sorted([k, t]),
                        "planets": [planet],
                        "formation": "dual_rulership",
                        "strength": round(strength, 2),
                        "cancellations": canc,
                        "priority": "Very Strong"
                    })

    for house, planets_in_house in conjunctions.items():
        if len(planets_in_house) < 2:
            continue
        k_lords, t_lords = [], []
        for p in planets_in_house:
            if p == eighth_lord:
                continue
            rules = [h for h, lord in house_lords.items() if lord == p]
            for rh in rules:
                if rh in kendras:
                    k_lords.append((p, rh))
                if rh in trikonas:
                    t_lords.append((p, rh))
        combos = []
        for kp, kh in k_lords:
            for tp, th in t_lords:
                if kp != tp and kh != th:
                    combos.append((kp, kh, tp, th))
        if combos:
            all_p = sorted({kp for kp,_,_,_ in combos} | {tp for *_, tp, _ in combos})
            all_h = sorted({kh for _,kh,_,_ in combos} | {th for *_, th in combos})
            key = f"kt_conj_{'-'.join(all_p)}_{'-'.join(map(str,all_h))}_{house}"
            if key not in processed:
                processed.add(key)
                strength, canc = validate_yoga_strength(all_p, planet_positions, planet_houses, asc_sign)
                if strength >= 30:
                    desc_parts = []
                    for p in all_p:
                        ruled = sorted({h for h,l in house_lords.items() if l == p and h in (kendras+trikonas)})
                        if ruled:
                            desc_parts.append(f"{'/'.join(f'{r}H' for r in ruled)} lord {p}")
                    desc = f"Conjunction of {' and '.join(desc_parts)} in {house}H"
                    raj_yogas.append({
                        "type": "Kendra-Trikona Raj Yoga",
                        "subtype": "Conjunction",
                        "description": desc,
                        "houses": all_h,
                        "planets": all_p,
                        "formation": "conjunction",
                        "strength": round(strength, 2),
                        "cancellations": canc,
                        "priority": "Strong"
                    })

    for k in kendras:
        for t in trikonas:
            if k == t:
                continue
            kl = house_lords[k]
            tl = house_lords[t]
            if kl == tl:
                continue
            if kl == house_lords[8] or tl == house_lords[8]:
                continue
            is_pv, pv_type = check_parivartana(kl, tl, planet_positions, house_lords, asc_sign_index)
            if is_pv:
                key = f"kt_pv_{min(k,t)}_{max(k,t)}"
                if key in processed:
                    continue
                processed.add(key)
                strength, canc = validate_yoga_strength([kl, tl], planet_positions, planet_houses, asc_sign)
                strength += 15
                if strength >= 30:
                    raj_yogas.append({
                        "type": "Kendra-Trikona Raj Yoga",
                        "subtype": f"Parivartana ({pv_type})",
                        "description": f"{kl} and {tl} exchange between {k}H and {t}H",
                        "houses": [k, t],
                        "planets": sorted([kl, tl]),
                        "formation": "parivartana",
                        "strength": round(strength, 2),
                        "cancellations": canc,
                        "priority": "Very Strong"
                    })

    for k in kendras:
        for t in trikonas:
            if k == t:
                continue
            kl = house_lords[k]
            tl = house_lords[t]
            if kl == tl:
                continue
            k_house = planet_houses.get(kl)
            t_house = planet_houses.get(tl)
            if not k_house or not t_house:
                continue
            if planet_aspects_house(kl, k_house, t_house) and planet_aspects_house(tl, t_house, k_house):
                key = f"kt_aspect_{min(k,t)}_{max(k,t)}"
                if key in processed:
                    continue
                processed.add(key)
                strength, canc = validate_yoga_strength([kl, tl], planet_positions, planet_houses, asc_sign)
                if strength >= 30:
                    raj_yogas.append({
                        "type": "Kendra-Trikona Raj Yoga",
                        "subtype": "Mutual Aspect",
                        "description": f"{kl} ({k}H lord) and {tl} ({t}H lord) in mutual aspect",
                        "houses": [k, t],
                        "planets": sorted([kl, tl]),
                        "formation": "mutual_aspect",
                        "strength": round(strength, 2),
                        "cancellations": canc,
                        "priority": "Strong"
                    })

    return raj_yogas

def check_dharma_karmadhipati_yoga(planet_houses, house_lords, planet_positions, asc_sign, asc_sign_index):
    raj_yogas = []
    dh_lord = house_lords[9]
    km_lord = house_lords[10]

    if dh_lord == km_lord:
        strength, canc = validate_yoga_strength([dh_lord], planet_positions, planet_houses, asc_sign)
        if strength >= 30:
            raj_yogas.append({
                "type": "Dharma-Karmadhipati Raj Yoga",
                "subtype": "Dual Rulership",
                "description": f"{dh_lord} rules both 9H (Dharma) and 10H (Karma)",
                "houses": [9, 10],
                "planets": [dh_lord],
                "formation": "dual_rulership",
                "strength": round(strength, 2),
                "cancellations": canc,
                "priority": "Very Strong"
            })
    else:
        dh = get_planet_house(dh_lord, planet_houses)
        km = get_planet_house(km_lord, planet_houses)
        if dh and km and dh == km:
            strength, canc = validate_yoga_strength([dh_lord, km_lord], planet_positions, planet_houses, asc_sign)
            if strength >= 30:
                raj_yogas.append({
                    "type": "Dharma-Karmadhipati Raj Yoga",
                    "subtype": "Conjunction",
                    "description": f"9H lord {dh_lord} conjunct 10H lord {km_lord} in {dh}H",
                    "houses": [9, 10],
                    "planets": sorted([dh_lord, km_lord]),
                    "formation": "conjunction",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "priority": "Very Strong"
                })
        if dh and km and planet_aspects_house(dh_lord, dh, km) and planet_aspects_house(km_lord, km, dh):
            strength, canc = validate_yoga_strength([dh_lord, km_lord], planet_positions, planet_houses, asc_sign)
            if strength >= 30:
                raj_yogas.append({
                    "type": "Dharma-Karmadhipati Raj Yoga",
                    "subtype": "Mutual Aspect",
                    "description": f"9H lord {dh_lord} and 10H lord {km_lord} in mutual aspect",
                    "houses": [9, 10],
                    "planets": sorted([dh_lord, km_lord]),
                    "formation": "mutual_aspect",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "priority": "Very Strong"
                })
        is_pv, pv_type = check_parivartana(dh_lord, km_lord, planet_positions, house_lords, asc_sign_index)
        if is_pv:
            strength, canc = validate_yoga_strength([dh_lord, km_lord], planet_positions, planet_houses, asc_sign)
            strength += 15
            if strength >= 30:
                raj_yogas.append({
                    "type": "Dharma-Karmadhipati Raj Yoga",
                    "subtype": f"Parivartana ({pv_type})",
                    "description": f"9H lord {dh_lord} and 10H lord {km_lord} in mutual exchange",
                    "houses": [9, 10],
                    "planets": sorted([dh_lord, km_lord]),
                    "formation": "parivartana",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "priority": "Very Strong"
                })
    return raj_yogas

def check_viparita_raj_yoga(planet_houses, house_lords, planet_positions, asc_sign):
    raj_yogas = []
    dusthanas = [6, 8, 12]
    yoga_names = {6: ("Harsha Yoga", "Victory over enemies"),
                  8: ("Sarala Yoga", "Protection from dangers"),
                  12: ("Vimala Yoga", "Financial gains through struggle")}
    for h in dusthanas:
        lord = house_lords[h]
        lord_house = get_planet_house(lord, planet_houses)
        if lord_house and lord_house in dusthanas and lord_house != h:
            strength, canc = validate_yoga_strength([lord], planet_positions, planet_houses, asc_sign)
            strength = max(40, strength)
            if strength >= 30:
                raj_yogas.append({
                    "type": "Viparita Raj Yoga",
                    "subtype": yoga_names[h][0],
                    "description": f"{h}H lord {lord} in {lord_house}H - {yoga_names[h][1]}",
                    "houses": [h, lord_house],
                    "planets": [lord],
                    "formation": "dusthana_exchange",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "priority": "Moderate"
                })
    return raj_yogas

def check_yogakaraka_raj_yoga(asc_sign, planet_houses, planet_positions, house_lords):
    raj_yogas = []
    ymap = {
        'Taurus': ('Saturn', [9, 10]),
        'Libra': ('Saturn', [4, 5]),
        'Cancer': ('Mars', [5, 10]),
        'Leo': ('Mars', [4, 9]),
        'Capricorn': ('Venus', [5, 10]),
        'Aquarius': ('Venus', [4, 9])
    }
    if asc_sign not in ymap:
        return raj_yogas
    planet, houses = ymap[asc_sign]
    ph = get_planet_house(planet, planet_houses)
    if not ph:
        return raj_yogas
    strength, canc = validate_yoga_strength([planet], planet_positions, planet_houses, asc_sign)
    if (ph in {1,4,5,7,9,10} and strength + 20 >= 50) or (strength + 20 >= 60):
        raj_yogas.append({
            "type": "Yogakaraka Raj Yoga",
            "subtype": None,
            "description": f"Yogakaraka {planet} for {asc_sign} ascendant in {ph}H (rules {houses[0]}H and {houses[1]}H)",
            "houses": houses,
            "planets": [planet],
            "formation": "yogakaraka",
            "strength": round(min(100, strength + 20), 2),
            "cancellations": canc,
            "priority": "Very Strong"
        })
    return raj_yogas

def check_neecha_bhanga_raj_yoga(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index):
    raj_yogas = []
    debilitation_map = {
        'Sun': ('Libra', 'Aries', 'Mars'),
        'Moon': ('Scorpio', 'Taurus', 'Venus'),
        'Mars': ('Cancer', 'Capricorn', 'Saturn'),
        'Mercury': ('Pisces', 'Virgo', 'Mercury'),
        'Jupiter': ('Capricorn', 'Cancer', 'Moon'),
        'Venus': ('Virgo', 'Pisces', 'Jupiter'),
        'Saturn': ('Aries', 'Libra', 'Venus')
    }
    kendras = {1, 4, 7, 10}

    for planet, (debil_sign, exalt_sign, exalt_lord) in debilitation_map.items():
        if planet not in planet_positions:
            continue
        lon = planet_positions[planet][0]
        p_sign, _, _ = longitude_to_sign(lon)
        if p_sign != debil_sign:
            continue

        planet_house = get_planet_house(planet, planet_houses)
        dispositor = PLANET_RULERS[debil_sign]
        disp_house = get_planet_house(dispositor, planet_houses)
        exalt_house = get_planet_house(exalt_lord, planet_houses)

        cancelled = False
        rules = []

        if disp_house in kendras:
            cancelled = True; rules.append(f"Rule 1: Dispositor {dispositor} in Kendra ({disp_house}H)")
        if exalt_house in kendras:
            cancelled = True; rules.append(f"Rule 2: Exaltation lord {exalt_lord} in Kendra ({exalt_house}H)")
        if exalt_house and planet_house and exalt_house == planet_house:
            cancelled = True; rules.append(f"Rule 3: Conjunct with exaltation lord {exalt_lord}")

        moon_house = get_planet_house('Moon', planet_houses)
        if moon_house:
            kendras_from_moon = {
                moon_house,
                ((moon_house - 1 + 3) % 12) + 1,
                ((moon_house - 1 + 6) % 12) + 1,
                ((moon_house - 1 + 9) % 12) + 1
            }
            if disp_house in kendras_from_moon:
                cancelled = True; rules.append(f"Rule 4: Dispositor {dispositor} in Kendra from Moon")
            if exalt_house in kendras_from_moon:
                cancelled = True; rules.append(f"Rule 5: Exaltation lord {exalt_lord} in Kendra from Moon")

        if planet_house in kendras:
            for chk, (c_lon, _) in planet_positions.items():
                c_sign, _, _ = longitude_to_sign(c_lon)
                if chk in EXALTATION and c_sign == EXALTATION[chk][0]:
                    c_house = get_planet_house(chk, planet_houses)
                    if c_house in kendras:
                        cancelled = True; rules.append(f"Rule 7: {chk} exalted in Kendra with debilitated {planet}")
                        break

        if cancelled:
            strength, canc = validate_yoga_strength([planet], planet_positions, planet_houses, asc_sign)
            strength = min(100, strength + 40)
            canc = [c for c in canc if 'debilitated' not in c]
            if strength >= 30:
                raj_yogas.append({
                    "type": "Neecha Bhanga Raj Yoga",
                    "subtype": None,
                    "description": f"{planet} debilitated in {debil_sign} but cancelled by: {'; '.join(rules)}",
                    "houses": [planet_house] if planet_house else [],
                    "planets": [planet],
                    "formation": "neecha_bhanga",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "cancellation_rules": rules,
                    "priority": "Very Strong"
                })
    return raj_yogas

def check_gaja_kesari_yoga(planet_houses, planet_positions, asc_sign):
    raj_yogas = []
    jh = planet_houses.get('Jupiter')
    mh = planet_houses.get('Moon')
    if not jh or not mh:
        return raj_yogas
    diff = (jh - mh) % 12
    if diff in {0, 3, 6, 9}:
        strength, canc = validate_yoga_strength(['Jupiter', 'Moon'], planet_positions, planet_houses, asc_sign)
        if strength >= 30:
            raj_yogas.append({
                "type": "Gaja Kesari Raj Yoga",
                "subtype": None,
                "description": f"Jupiter in {jh}H in Kendra from Moon in {mh}H",
                "houses": [jh, mh],
                "planets": ['Jupiter', 'Moon'],
                "formation": "kendra_from_moon",
                "strength": round(strength, 2),
                "cancellations": canc,
                "priority": "Very Strong"
            })
    return raj_yogas

def check_pancha_mahapurusha_yogas(planet_positions, planet_houses, asc_sign):
    raj_yogas = []
    kendras = {1, 4, 7, 10}
    pancha = {
        'Mars': ('Ruchaka', ['Aries', 'Scorpio', 'Capricorn']),
        'Mercury': ('Bhadra', ['Gemini', 'Virgo']),
        'Jupiter': ('Hamsa', ['Sagittarius', 'Pisces', 'Cancer']),
        'Venus': ('Malavya', ['Taurus', 'Libra', 'Pisces']),
        'Saturn': ('Sasa', ['Capricorn', 'Aquarius', 'Libra'])
    }
    for planet, (yoga_name, good_signs) in pancha.items():
        if planet not in planet_positions or planet not in planet_houses:
            continue
        lon = planet_positions[planet][0]
        sign, _, _ = longitude_to_sign(lon)
        house = planet_houses[planet]
        if sign in good_signs and house in kendras:
            strength, canc = validate_yoga_strength([planet], planet_positions, planet_houses, asc_sign)
            strength = min(100, strength + 15)
            if strength >= 40:
                raj_yogas.append({
                    "type": "Pancha Mahapurusha Raj Yoga",
                    "subtype": f"{yoga_name} Yoga",
                    "description": f"{planet} in {sign} in Kendra ({house}H)",
                    "houses": [house],
                    "planets": [planet],
                    "formation": "mahapurusha",
                    "strength": round(strength, 2),
                    "cancellations": canc,
                    "priority": "Very Strong"
                })
    return raj_yogas

def check_adhi_yoga(planet_houses, planet_positions, asc_sign):
    raj_yogas = []
    mh = planet_houses.get('Moon')
    if not mh:
        return raj_yogas

    target_houses = [
        ((mh - 1 + 5) % 12) + 1,
        ((mh - 1 + 6) % 12) + 1,
        ((mh - 1 + 7) % 12) + 1
    ]

    if any(planet_houses.get(m) in target_houses for m in NATURAL_MALEFICS):
        return raj_yogas

    benefics = []
    if planet_houses.get('Mercury') in target_houses and not is_combust('Mercury', planet_positions):
        benefics.append('Mercury')
    if planet_houses.get('Jupiter') in target_houses:
        benefics.append('Jupiter')
    if planet_houses.get('Venus') in target_houses:
        benefics.append('Venus')

    if len(benefics) >= 1:
        strength, canc = validate_yoga_strength(benefics, planet_positions, planet_houses, asc_sign)
        strength += len(benefics) * 10
        if strength >= 30:
            placements = [f"{b}:{planet_houses[b]}H" for b in benefics]
            raj_yogas.append({
                "type": "Adhi Raj Yoga",
                "subtype": None,
                "description": f"Benefics in 6/7/8 from Moon ({mh}H): " + ", ".join(placements),
                "houses": target_houses,
                "planets": benefics,
                "formation": "benefics_from_moon",
                "strength": round(strength, 2),
                "cancellations": canc,
                "priority": "Strong" if len(benefics) == 1 else "Very Strong"
            })
    return raj_yogas

# ----------------------------
# Post-processing & main analysis
# ----------------------------
def remove_duplicate_yogas(all_yogas):
    if not all_yogas:
        return []
    final = []
    seen = set()
    type_priority = {
        "Dharma-Karmadhipati Raj Yoga": 1,
        "Yogakaraka Raj Yoga": 2,
        "Kendra-Trikona Raj Yoga": 3,
        "Gaja Kesari Raj Yoga": 4,
        "Pancha Mahapurusha Raj Yoga": 5,
        "Neecha Bhanga Raj Yoga": 6,
        "Viparita Raj Yoga": 7,
        "Adhi Raj Yoga": 8
    }
    formation_priority = {"parivartana": 1, "dual_rulership": 2, "conjunction": 3, "mutual_aspect": 4}
    def sort_key(y):
        return (type_priority.get(y['type'], 99),
                formation_priority.get(y.get('formation', ''), 99),
                -y.get('strength', 0))
    for y in sorted(all_yogas, key=sort_key):
        sig = (tuple(sorted(y['planets'])), tuple(sorted(y['houses'])), y['type'], y.get('subtype'))
        if sig in seen:
            continue
        seen.add(sig)
        final.append(y)
    return final

def analyze_raj_yogas(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index):
    all_ry = []
    all_ry.extend(check_kendra_trikona_raj_yoga(planet_houses, house_lords, planet_positions, asc_sign, asc_sign_index))
    all_ry.extend(check_dharma_karmadhipati_yoga(planet_houses, house_lords, planet_positions, asc_sign, asc_sign_index))
    all_ry.extend(check_viparita_raj_yoga(planet_houses, house_lords, planet_positions, asc_sign))
    all_ry.extend(check_yogakaraka_raj_yoga(asc_sign, planet_houses, planet_positions, house_lords))
    all_ry.extend(check_neecha_bhanga_raj_yoga(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index))
    all_ry.extend(check_gaja_kesari_yoga(planet_houses, planet_positions, asc_sign))
    all_ry.extend(check_pancha_mahapurusha_yogas(planet_positions, planet_houses, asc_sign))
    all_ry.extend(check_adhi_yoga(planet_houses, planet_positions, asc_sign))
    final = remove_duplicate_yogas(all_ry)
    final.sort(key=lambda x: x.get('strength', 0), reverse=True)
    return final

# ------------- PUBLIC ENTRYPOINT -------------
def rajYoga(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index):
    """
    Public wrapper: returns the final Raj Yoga list using all detectors.
    """
    return analyze_raj_yogas(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index)

# ------------- CHART COMPUTATION (used by API) -------------
def compute_chart(payload):
    """
    Compute ascendant, house lords, planet positions/houses, house signs, and notes.
    Returns: dict with keys:
      asc_sign, asc_lon, asc_sign_index, planet_positions, planet_houses, house_lords, house_signs, ayanamsa_value
    """
    latitude = float(payload['latitude'])
    longitude = float(payload['longitude'])
    tz_off = float(payload['timezone_offset'])
    birth_date = datetime.strptime(payload['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(payload['birth_time'], '%H:%M:%S').time()
    local_dt = datetime.combine(birth_date, birth_time)
    ut_dt = local_dt - timedelta(hours=tz_off)
    hour_decimal = ut_dt.hour + ut_dt.minute/60.0 + ut_dt.second/3600.0
    jd_ut = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]

    planet_positions = {}
    for pid, name in planets:
        pos, ret = swe.calc_ut(jd_ut, pid, flag)
        if ret < 0:
            raise RuntimeError(f"Error calculating {name}")
        lon = pos[0] % 360
        speed = pos[3]
        planet_positions[name] = (lon, 'R' if speed < 0 else '')

    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    asc_sign_index = int(asc_lon // 30)
    asc_sign = SIGNS[asc_sign_index]

    orientation_shift = int(payload.get('orientation_shift', 0))
    planet_houses = {}
    for p, (lon, _) in planet_positions.items():
        planet_houses[p] = get_house(lon, asc_sign_index, orientation_shift=orientation_shift)

    house_lords = get_house_lords(asc_sign_index)

    house_signs = {}
    for i in range(12):
        sidx = (asc_sign_index + i) % 12
        house_signs[f"House {i+1}"] = {
            "sign": SIGNS[sidx],
            "start_longitude": format_dms(sidx * 30.0)
        }

    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    return {
        "asc_sign": asc_sign,
        "asc_lon": asc_lon,
        "asc_sign_index": asc_sign_index,
        "planet_positions": planet_positions,
        "planet_houses": planet_houses,
        "house_lords": house_lords,
        "house_signs": house_signs,
        "ayanamsa_value": ayanamsa_value,
        "jd_ut": jd_ut
    }

def planetary_positions_json(planet_positions, planet_houses):
    out = {}
    for name, (lon, retro) in planet_positions.items():
        sign, sign_deg, _ = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = planet_houses[name]
        dignity, _ = get_planet_dignity(name, lon)
        out[name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "dignity": dignity,
            "longitude": round(lon, 4)
        }
    return out
