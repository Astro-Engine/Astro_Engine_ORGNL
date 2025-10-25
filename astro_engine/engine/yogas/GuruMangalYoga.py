import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Planet ownership and exaltation data
planet_rulership = {
   'Sun': {'own': ['Leo'], 'exaltation': 'Aries', 'debilitation': 'Libra'},
   'Moon': {'own': ['Cancer'], 'exaltation': 'Taurus', 'debilitation': 'Scorpio'},
   'Mars': {'own': ['Aries', 'Scorpio'], 'exaltation': 'Capricorn', 'debilitation': 'Cancer'},
   'Mercury': {'own': ['Gemini', 'Virgo'], 'exaltation': 'Virgo', 'debilitation': 'Pisces'},
   'Jupiter': {'own': ['Sagittarius', 'Pisces'], 'exaltation': 'Cancer', 'debilitation': 'Capricorn'},
   'Venus': {'own': ['Taurus', 'Libra'], 'exaltation': 'Pisces', 'debilitation': 'Virgo'},
   'Saturn': {'own': ['Capricorn', 'Aquarius'], 'exaltation': 'Libra', 'debilitation': 'Aries'}
}

# Friendship matrix
planet_friendship = {
   'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 'enemies': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
   'Moon': {'friends': ['Sun', 'Mercury'], 'enemies': [], 'neutral': ['Mars', 'Jupiter', 'Venus', 'Saturn']},
   'Mars': {'friends': ['Sun', 'Moon', 'Jupiter'], 'enemies': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
   'Mercury': {'friends': ['Sun', 'Venus'], 'enemies': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
   'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 'enemies': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
   'Venus': {'friends': ['Mercury', 'Saturn'], 'enemies': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
   'Saturn': {'friends': ['Mercury', 'Venus'], 'enemies': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
}

# Aspects in Vedic astrology
planet_aspects = {
   'Sun': [7],
   'Moon': [7],
   'Mars': [4, 7, 8],
   'Mercury': [7],
   'Jupiter': [5, 7, 9],
   'Venus': [7],
   'Saturn': [3, 7, 10]
}

# Functional benefic/malefic for each ascendant
functional_nature = {
   'Aries': {
       'Jupiter': 'benefic',  # 9th & 12th lord
       'Mars': 'benefic'      # 1st & 8th lord
   },
   'Taurus': {
       'Jupiter': 'malefic',  # 8th & 11th lord
       'Mars': 'malefic'      # 7th & 12th lord
   },
   'Gemini': {
       'Jupiter': 'malefic',  # 7th & 10th lord
       'Mars': 'benefic'      # 6th & 11th lord
   },
   'Cancer': {
       'Jupiter': 'benefic',  # 6th & 9th lord
       'Mars': 'benefic'      # 5th & 10th lord
   },
   'Leo': {
       'Jupiter': 'benefic',  # 5th & 8th lord
       'Mars': 'benefic'      # 4th & 9th lord
   },
   'Virgo': {
       'Jupiter': 'malefic',  # 4th & 7th lord
       'Mars': 'neutral'      # 3rd & 8th lord
   },
   'Libra': {
       'Jupiter': 'benefic',  # 3rd & 6th lord
       'Mars': 'malefic'      # 2nd & 7th lord
   },
   'Scorpio': {
       'Jupiter': 'benefic',  # 2nd & 5th lord
       'Mars': 'benefic'      # 1st & 6th lord
   },
   'Sagittarius': {
       'Jupiter': 'benefic',  # 1st & 4th lord
       'Mars': 'benefic'      # 5th & 12th lord
   },
   'Capricorn': {
       'Jupiter': 'benefic',  # 3rd & 12th lord
       'Mars': 'malefic'      # 4th & 11th lord
   },
   'Aquarius': {
       'Jupiter': 'neutral',  # 2nd & 11th lord
       'Mars': 'benefic'      # 3rd & 10th lord
   },
   'Pisces': {
       'Jupiter': 'benefic',  # 1st & 10th lord
       'Mars': 'neutral'      # 2nd & 9th lord
   }
}

def get_house(lon, asc_sign_index, orientation_shift=0):
   """Calculate house number based on planet longitude and ascendant sign index for Whole Sign system."""
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

def get_planet_strength(planet, sign):
   """Determine planet's strength in a given sign."""
   if planet not in planet_rulership:
       return "neutral"
   
   rulership = planet_rulership[planet]
   
   if sign in rulership['own']:
       return "own_sign"
   elif sign == rulership['exaltation']:
       return "exaltation"
   elif sign == rulership['debilitation']:
       return "debilitation"
   else:
       # Check friendship
       sign_rulers = []
       for p, data in planet_rulership.items():
           if sign in data['own']:
               sign_rulers.append(p)
       
       if sign_rulers:
           ruler = sign_rulers[0]  # Primary ruler
           if planet in planet_friendship and ruler in planet_friendship[planet]['friends']:
               return "friend_sign"
           elif planet in planet_friendship and ruler in planet_friendship[planet]['enemies']:
               return "enemy_sign"
       
       return "neutral"

def calculate_conjunction_orb(lon1, lon2):
   """Calculate the orb between two planetary longitudes."""
   diff = abs(lon1 - lon2)
   if diff > 180:
       diff = 360 - diff
   return diff

def check_mutual_aspect(jupiter_house, mars_house, jupiter_sign, mars_sign):
   """Check if Jupiter and Mars have mutual aspect."""
   # Calculate house difference
   house_diff = abs(jupiter_house - mars_house)
   if house_diff > 6:
       house_diff = 12 - house_diff
   
   # Check Jupiter's aspects on Mars
   jupiter_aspects_mars = False
   if house_diff in planet_aspects['Jupiter']:
       jupiter_aspects_mars = True
   
   # Check Mars's aspects on Jupiter  
   mars_aspects_jupiter = False
   if house_diff in planet_aspects['Mars']:
       mars_aspects_jupiter = True
   
   return jupiter_aspects_mars and mars_aspects_jupiter

def check_parivartana_yoga(jupiter_sign, mars_sign):
   """Check for Parivartana (exchange) yoga between Jupiter and Mars."""
   jupiter_owns = planet_rulership['Jupiter']['own']
   mars_owns = planet_rulership['Mars']['own']
   
   # Check if Jupiter is in Mars's sign and Mars is in Jupiter's sign
   jupiter_in_mars_sign = jupiter_sign in mars_owns
   mars_in_jupiter_sign = mars_sign in jupiter_owns
   
   if jupiter_in_mars_sign and mars_in_jupiter_sign:
       return True, "complete_exchange"
   elif jupiter_in_mars_sign or mars_in_jupiter_sign:
       return True, "partial_exchange"
   
   return False, None

def check_neecha_bhanga(jupiter_data, mars_data, all_planets):
   """Check for Neecha Bhanga (debilitation cancellation)."""
   jupiter_sign = jupiter_data['sign']
   mars_sign = mars_data['sign']
   jupiter_debilitated = get_planet_strength('Jupiter', jupiter_sign) == "debilitation"
   mars_debilitated = get_planet_strength('Mars', mars_sign) == "debilitation"
   
   neecha_bhanga_factors = []
   
   if jupiter_debilitated:
       # Check if Mars is exalted
       if get_planet_strength('Mars', mars_sign) == "exaltation":
           neecha_bhanga_factors.append("mars_exalted_with_jupiter_debilitated")
       
       # Check if debilitation lord is strong
       jupiter_debil_lord = None
       for planet, data in planet_rulership.items():
           if jupiter_sign in data['own']:
               jupiter_debil_lord = planet
               break
       
       if jupiter_debil_lord and jupiter_debil_lord in all_planets:
           debil_lord_strength = get_planet_strength(jupiter_debil_lord, all_planets[jupiter_debil_lord]['sign'])
           if debil_lord_strength in ["own_sign", "exaltation"]:
               neecha_bhanga_factors.append("debilitation_lord_strong")
   
   if mars_debilitated:
       # Check if Jupiter is exalted
       if get_planet_strength('Jupiter', jupiter_sign) == "exaltation":
           neecha_bhanga_factors.append("jupiter_exalted_with_mars_debilitated")
       
       # Check if debilitation lord is strong
       mars_debil_lord = None
       for planet, data in planet_rulership.items():
           if mars_sign in data['own']:
               mars_debil_lord = planet
               break
       
       if mars_debil_lord and mars_debil_lord in all_planets:
           debil_lord_strength = get_planet_strength(mars_debil_lord, all_planets[mars_debil_lord]['sign'])
           if debil_lord_strength in ["own_sign", "exaltation"]:
               neecha_bhanga_factors.append("debilitation_lord_strong")
   
   return len(neecha_bhanga_factors) > 0, neecha_bhanga_factors

def get_house_strength_category(house):
   """Categorize house strength."""
   if house in [1, 4, 7, 10]:
       return "kendra", "excellent"
   elif house in [1, 5, 9]:
       return "trikona", "very_good" 
   elif house in [3, 6, 10, 11]:
       return "upachaya", "good"
   elif house in [2, 8, 12]:
       return "dusthana", "challenging"
   else:
       return "other", "neutral"

def calculate_comprehensive_guru_mangal_yoga(jupiter_data, mars_data, ascendant_sign, all_planets):
   """
   Comprehensive analysis of all Guru Mangal Yoga combinations and permutations.
   """
   jupiter_sign = jupiter_data['sign']
   mars_sign = mars_data['sign']
   jupiter_house = jupiter_data['house']
   mars_house = mars_data['house']
   jupiter_lon = jupiter_data['longitude']
   mars_lon = mars_data['longitude']
   
   # Initialize result structure
   yoga_result = {
       "yoga_combinations": [],
       "overall_yoga_present": False,
       "strongest_combination": None,
       "total_strength_score": 0,
       "detailed_analysis": "",
       "functional_status": {},
       "special_features": []
   }
   
   # Get functional nature for ascendant
   jupiter_functional = functional_nature.get(ascendant_sign, {}).get('Jupiter', 'neutral')
   mars_functional = functional_nature.get(ascendant_sign, {}).get('Mars', 'neutral')
   
   yoga_result["functional_status"] = {
       "jupiter": jupiter_functional,
       "mars": mars_functional,
       "combined": "beneficial" if jupiter_functional == "benefic" and mars_functional == "benefic" else 
                  "malefic" if jupiter_functional == "malefic" or mars_functional == "malefic" else "mixed"
   }
   
   # 1. DIRECT CONJUNCTION ANALYSIS
   if jupiter_sign == mars_sign:
       orb = calculate_conjunction_orb(jupiter_lon, mars_lon)
       
       if orb <= 15:  # Allow wider orb for detection
           conjunction_strength = 0
           
           # Orb-based strength
           if orb <= 3:
               orb_strength = "excellent"
               conjunction_strength += 5
           elif orb <= 6:
               orb_strength = "very_good"
               conjunction_strength += 4
           elif orb <= 10:
               orb_strength = "good"
               conjunction_strength += 3
           elif orb <= 15:
               orb_strength = "moderate"
               conjunction_strength += 2
           else:
               orb_strength = "weak"
               conjunction_strength += 1
           
           # Sign strength analysis
           jupiter_strength = get_planet_strength('Jupiter', jupiter_sign)
           mars_strength = get_planet_strength('Mars', mars_sign)
           
           # Strength points for planets
           strength_points = {
               "exaltation": 5,
               "own_sign": 4,
               "friend_sign": 3,
               "neutral": 2,
               "enemy_sign": 1,
               "debilitation": 0
           }
           
           conjunction_strength += strength_points.get(jupiter_strength, 2)
           conjunction_strength += strength_points.get(mars_strength, 2)
           
           # House strength
           house_category, house_strength = get_house_strength_category(jupiter_house)
           house_points = {
               "excellent": 4,
               "very_good": 3,
               "good": 2,
               "neutral": 1,
               "challenging": 0
           }
           conjunction_strength += house_points.get(house_strength, 1)
           
           # Determine overall conjunction strength
           if conjunction_strength >= 15:
               overall_strength = "excellent"
           elif conjunction_strength >= 12:
               overall_strength = "very_good"
           elif conjunction_strength >= 9:
               overall_strength = "good"
           elif conjunction_strength >= 6:
               overall_strength = "moderate"
           else:
               overall_strength = "weak"
           
           conjunction_combo = {
               "type": "direct_conjunction",
               "present": True,
               "sign": jupiter_sign,
               "house": jupiter_house,
               "orb_degrees": round(orb, 2),
               "orb_strength": orb_strength,
               "jupiter_strength": jupiter_strength,
               "mars_strength": mars_strength,
               "house_category": house_category,
               "house_strength": house_strength,
               "overall_strength": overall_strength,
               "strength_score": conjunction_strength,
               "effects": []
           }
           
           # Add specific effects based on placement
           if house_category == "kendra":
               conjunction_combo["effects"].extend(["leadership", "authority", "recognition"])
           elif house_category == "trikona":
               conjunction_combo["effects"].extend(["wisdom", "dharma", "fortune"])
           elif house_category == "upachaya":
               conjunction_combo["effects"].extend(["growth", "achievement", "competition"])
           
           if jupiter_strength in ["exaltation", "own_sign"] and mars_strength in ["exaltation", "own_sign"]:
               conjunction_combo["effects"].append("exceptional_success")
           
           yoga_result["yoga_combinations"].append(conjunction_combo)
           yoga_result["total_strength_score"] += conjunction_strength
   
   # 2. PARIVARTANA YOGA ANALYSIS
   parivartana_present, parivartana_type = check_parivartana_yoga(jupiter_sign, mars_sign)
   if parivartana_present:
       parivartana_strength = 8 if parivartana_type == "complete_exchange" else 5
       
       # Analyze both placements
       jupiter_in_mars_house_strength = get_planet_strength('Jupiter', jupiter_sign)
       mars_in_jupiter_house_strength = get_planet_strength('Mars', mars_sign)
       
       if jupiter_in_mars_house_strength in ["own_sign", "exaltation"]:
           parivartana_strength += 3
       if mars_in_jupiter_house_strength in ["own_sign", "exaltation"]:
           parivartana_strength += 3
       
       parivartana_combo = {
           "type": "parivartana_yoga",
           "present": True,
           "exchange_type": parivartana_type,
           "jupiter_in": jupiter_sign,
           "mars_in": mars_sign,
           "jupiter_house": jupiter_house,
           "mars_house": mars_house,
           "strength_score": parivartana_strength,
           "overall_strength": "excellent" if parivartana_strength >= 12 else "very_good" if parivartana_strength >= 8 else "good",
           "effects": ["mutual_empowerment", "exchange_benefits", "dual_house_activation"]
       }
       
       yoga_result["yoga_combinations"].append(parivartana_combo)
       yoga_result["total_strength_score"] += parivartana_strength
   
   # 3. MUTUAL ASPECT ANALYSIS
   mutual_aspect = check_mutual_aspect(jupiter_house, mars_house, jupiter_sign, mars_sign)
   if mutual_aspect and jupiter_sign != mars_sign:  # Don't double count conjunction
       aspect_strength = 6  # Base strength for mutual aspect
       
       # Check if both are in friendly signs
       jupiter_strength = get_planet_strength('Jupiter', jupiter_sign)
       mars_strength = get_planet_strength('Mars', mars_sign)
       
       if jupiter_strength in ["own_sign", "exaltation", "friend_sign"]:
           aspect_strength += 2
       if mars_strength in ["own_sign", "exaltation", "friend_sign"]:
           aspect_strength += 2
       
       # House considerations
       jupiter_house_cat, jupiter_house_str = get_house_strength_category(jupiter_house)
       mars_house_cat, mars_house_str = get_house_strength_category(mars_house)
       
       if jupiter_house_str in ["excellent", "very_good"]:
           aspect_strength += 1
       if mars_house_str in ["excellent", "very_good"]:
           aspect_strength += 1
       
       aspect_combo = {
           "type": "mutual_aspect",
           "present": True,
           "jupiter_aspects_mars": True,
           "mars_aspects_jupiter": True,
           "jupiter_sign": jupiter_sign,
           "mars_sign": mars_sign,
           "jupiter_house": jupiter_house,
           "mars_house": mars_house,
           "strength_score": aspect_strength,
           "overall_strength": "good" if aspect_strength >= 8 else "moderate",
           "effects": ["mutual_influence", "aspect_connection", "distant_cooperation"]
       }
       
       yoga_result["yoga_combinations"].append(aspect_combo)
       yoga_result["total_strength_score"] += aspect_strength
   
   # 4. NEECHA BHANGA ANALYSIS
   neecha_bhanga_present, neecha_factors = check_neecha_bhanga(jupiter_data, mars_data, all_planets)
   if neecha_bhanga_present:
       neecha_strength = len(neecha_factors) * 4
       
       neecha_combo = {
           "type": "neecha_bhanga_raja_yoga",
           "present": True,
           "cancellation_factors": neecha_factors,
           "strength_score": neecha_strength,
           "overall_strength": "excellent" if neecha_strength >= 8 else "very_good",
           "effects": ["debilitation_cancellation", "unexpected_rise", "transformation"]
       }
       
       yoga_result["yoga_combinations"].append(neecha_combo)
       yoga_result["total_strength_score"] += neecha_strength
       yoga_result["special_features"].append("neecha_bhanga_present")
   
   # 5. SPECIAL COMBINATIONS
   
   # Same Nakshatra check (advanced)
   jupiter_nakshatra = int(jupiter_lon * 3 / 40) % 27
   mars_nakshatra = int(mars_lon * 3 / 40) % 27
   
   if jupiter_nakshatra == mars_nakshatra:
       nakshatra_combo = {
           "type": "same_nakshatra",
           "present": True,
           "nakshatra_number": jupiter_nakshatra,
           "strength_score": 3,
           "overall_strength": "good",
           "effects": ["deep_connection", "similar_karma"]
       }
       yoga_result["yoga_combinations"].append(nakshatra_combo)
       yoga_result["total_strength_score"] += 3
       yoga_result["special_features"].append("same_nakshatra")
   
   # Determine if any yoga is present
   yoga_result["overall_yoga_present"] = len(yoga_result["yoga_combinations"]) > 0
   
   # Find strongest combination
   if yoga_result["yoga_combinations"]:
       strongest = max(yoga_result["yoga_combinations"], key=lambda x: x["strength_score"])
       yoga_result["strongest_combination"] = strongest
   
   # Generate detailed analysis
   if yoga_result["overall_yoga_present"]:
       analysis_parts = []
       analysis_parts.append(f"Guru Mangal Yoga analysis reveals {len(yoga_result['yoga_combinations'])} active combination(s).")
       
       for combo in yoga_result["yoga_combinations"]:
           if combo["type"] == "direct_conjunction":
               analysis_parts.append(f"Direct conjunction in {combo['sign']} sign, {combo['house']} house with {combo['orb_degrees']}° orb - {combo['overall_strength']} strength.")
           elif combo["type"] == "parivartana_yoga":
               analysis_parts.append(f"Parivartana yoga with {combo['exchange_type']} exchange - {combo['overall_strength']} strength.")
           elif combo["type"] == "mutual_aspect":
               analysis_parts.append(f"Mutual aspect between houses {combo['jupiter_house']} and {combo['mars_house']} - {combo['overall_strength']} strength.")
           elif combo["type"] == "neecha_bhanga_raja_yoga":
               analysis_parts.append(f"Neecha Bhanga Raja Yoga with factors: {', '.join(combo['cancellation_factors'])} - {combo['overall_strength']} strength.")
       
       analysis_parts.append(f"Total strength score: {yoga_result['total_strength_score']}.")
       analysis_parts.append(f"Functional status for {ascendant_sign} ascendant: {yoga_result['functional_status']['combined']}.")
       
       if yoga_result["special_features"]:
           analysis_parts.append(f"Special features: {', '.join(yoga_result['special_features'])}.")
       
       yoga_result["detailed_analysis"] = " ".join(analysis_parts)
   else:
       yoga_result["detailed_analysis"] = "No Guru Mangal Yoga combinations detected in this chart."
   
   return yoga_result

def calculate_planetary_positions_guru_mangal(birth_data):
    """Calculate all planetary positions for Guru Mangal analysis."""
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude")

    # Parse date and time
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

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
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Ascendant calculation
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # House signs
    house_signs = []
    for i in range(12):
        sign_index = (asc_sign_index + i) % 12
        sign_start_lon = (sign_index * 30)
        house_signs.append({"sign": signs[sign_index], "start_longitude": sign_start_lon})

    # Calculate house positions
    orientation_shift = int(birth_data.get('orientation_shift', 0))
    planet_houses = {planet: get_house(lon, asc_sign_index, orientation_shift=orientation_shift) 
                     for planet, (lon, _) in planet_positions.items()}

    # Format planetary positions
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = planet_houses[planet_name]
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "longitude": lon
        }

    # Prepare response data
    ascendant_json = {"sign": asc_sign, "degrees": format_dms(ascendant_lon % 30)}
    house_signs_json = {f"House {i+1}": {"sign": house["sign"], "start_longitude": format_dms(house["start_longitude"])} 
                       for i, house in enumerate(house_signs)}

    return planetary_positions_json, ascendant_json, house_signs_json, asc_sign, ayanamsa_value