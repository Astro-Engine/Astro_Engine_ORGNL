
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger

from astro_engine.engine.kpSystem.charts.Fortuna import calculate_part_of_fortune

from ..ashatakavargha.KpShodashVargha import CHARTS_kp, SIGNS_kp, get_sidereal_asc_kp, get_sidereal_positions_kp, julian_day_kp, local_to_utc_kp, varga_sign_kp
from ..dashas.KpAntar import calculate_maha_antar_dasha
from ..dashas.KpPran import calculate_maha_antar_pratyantar_pran_dasha
from ..dashas.KpPratyantar import calculate_maha_antar_pratyantar_dasha
from ..dashas.KpSookshma import calculate_maha_antar_pratyantar_sooksha_dashas
from ..kpSystem.KpHorary import KP_NEW_AYANAMSA, calc_vimshottari_dasha_path, check_radicality, check_void_of_course_moon, get_asc_from_horary_num, get_nakshatra_chain, get_ruling_planets, get_sign_lord, get_significators_expanded, house_cusps, julday_from_date_time, kp_timing_by_dasha_layers, planet_chain, planet_house_assignment, sign_deg, sub_lord_chain_judgment
from ..kpSystem.charts.BhavaHouses import calculate_bhava_houses_details
from ..kpSystem.charts.CupsalChart import ZODIAC_SIGNS, cupsal_assign_nakshatra_and_lords, cupsal_assign_planet_to_house, cupsal_calculate_ascendant_and_cusps, cupsal_calculate_kp_new_ayanamsa, cupsal_calculate_planet_positions, cupsal_calculate_significators, cupsal_format_dms, cupsal_get_julian_day
from ..kpSystem.charts.RulingPlanets import ruling_calculate_ascendant_and_cusps, ruling_calculate_balance_of_dasha, ruling_calculate_fortuna, ruling_calculate_jd, ruling_calculate_planet_positions, ruling_check_rahu_ketu, ruling_compile_core_rp, ruling_get_day_lord, ruling_get_details
from ..kpSystem.charts.SignificatorHouse import calculate_planets_significations




kp = Blueprint('kp_routes', __name__)



# KP Planets and Cusps
@kp.route('/kp/calculate_kp_planets_cusps', methods=['POST'])
def calculate_kp_planets_cusps():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = cupsal_get_julian_day(birth_date, birth_time, tz_offset)
        kp_new_ayanamsa = cupsal_calculate_kp_new_ayanamsa(jd)
        ascendant, house_cusps = cupsal_calculate_ascendant_and_cusps(jd, latitude, longitude, kp_new_ayanamsa)
        planets = cupsal_calculate_planet_positions(jd, kp_new_ayanamsa)

        planet_details = {
            planet: {
                "longitude": cupsal_format_dms(lon),
                "sign": ZODIAC_SIGNS[int(lon // 30)],
                "nakshatra": cupsal_assign_nakshatra_and_lords(lon)[0],
                "star_lord": cupsal_assign_nakshatra_and_lords(lon)[1],
                "sub_lord": cupsal_assign_nakshatra_and_lords(lon)[2],
                "house": cupsal_assign_planet_to_house(lon, house_cusps)
            }
            for planet, lon in planets.items()
        }
        cusp_details = {
            str(i + 1): {
                "longitude": cupsal_format_dms(cusp),
                "sign": ZODIAC_SIGNS[int(cusp // 30)],
                "nakshatra": cupsal_assign_nakshatra_and_lords(cusp)[0],
                "star_lord": cupsal_assign_nakshatra_and_lords(cusp)[1],
                "sub_lord": cupsal_assign_nakshatra_and_lords(cusp)[2]
            }
            for i, cusp in enumerate(house_cusps)
        }
        significators = cupsal_calculate_significators(planets, house_cusps)

        response = {
            "user_name": user_name,
            "ascendant": {"longitude": cupsal_format_dms(ascendant), "sign": ZODIAC_SIGNS[int(ascendant // 30)]},
            "house_cusps": cusp_details,
            "planets": planet_details,
            "significators": significators,
            "metadata": {"ayanamsa": "KP New", "house_system": "Placidus", "calculation_time": datetime.utcnow().isoformat(), "input": data}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500
    




# Ruling Planets
@kp.route('/kp/calculate_ruling_planets', methods=['POST'])
def calculate_ruling_planets():
    try:
        data = request.get_json()
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        jd, utc_dt = ruling_calculate_jd(birth_date, birth_time, timezone_offset)
        ascendant, cusps = ruling_calculate_ascendant_and_cusps(jd, latitude, longitude)
        sun_pos, moon_pos, rahu_pos, ketu_pos = ruling_calculate_planet_positions(jd)
        day_lord = ruling_get_day_lord(utc_dt)
        lagna_sign, lagna_rashi_lord, lagna_nakshatra, lagna_star_lord, lagna_sub_lord = ruling_get_details(ascendant)
        moon_sign, moon_rashi_lord, moon_nakshatra, moon_star_lord, moon_sub_lord = ruling_get_details(moon_pos)
        lagna_details = {'rashi_lord': lagna_rashi_lord, 'star_lord': lagna_star_lord, 'sub_lord': lagna_sub_lord}
        moon_details = {'rashi_lord': moon_rashi_lord, 'star_lord': moon_star_lord, 'sub_lord': moon_sub_lord}
        core_rp = ruling_compile_core_rp(lagna_details, moon_details, day_lord)
        core_rp = ruling_check_rahu_ketu(rahu_pos, ketu_pos, core_rp)
        fortuna = ruling_calculate_fortuna(ascendant, moon_pos, sun_pos)
        dasha_lord, balance_years = ruling_calculate_balance_of_dasha(moon_pos, moon_star_lord)

        response = {
            "ruling_planets": list(core_rp),
            "details": {
                "day_lord": day_lord,
                "lagna_lord": lagna_rashi_lord,
                "lagna_nakshatra_lord": lagna_star_lord,
                "lagna_sub_lord": lagna_sub_lord,
                "moon_rashi_lord": moon_rashi_lord,
                "moon_nakshatra_lord": moon_star_lord,
                "moon_sub_lord": moon_sub_lord,
                "fortuna": round(fortuna, 4),
                "balance_of_dasha": {"dasha_lord": dasha_lord, "balance_years": round(balance_years, 4)}
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400




# Bhava Details
@kp.route('/kp/calculate_bhava_details', methods=['POST'])
def calculate_bhava_details():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        bhava_details = calculate_bhava_houses_details(birth_date, birth_time, latitude, longitude, timezone_offset)
        response = {
            'user_name': user_name,
            'bhava_details': bhava_details
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400






# House Significations
@kp.route('/kp/calculate_significations', methods=['POST'])
def calculate_significations():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        significators = calculate_planets_significations(birth_date, birth_time, latitude, longitude, timezone_offset)
        response = {
            'user_name': user_name,
            'house_significations': significators
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    


#  Forutna API

@kp.route('/kp/fortuna', methods=['POST'])
def fortuna():
    try:
        data = request.get_json()
        user_name = data["user_name"]
        birth_date = data["birth_date"]
        birth_time = data["birth_time"]
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        tz_offset = float(data["timezone_offset"])

        # Calculate Part of Fortune
        result = calculate_part_of_fortune(
            birth_date, 
            birth_time, 
            latitude, 
            longitude, 
            tz_offset, 
            user_name
        )

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400



#**************************************************************************************************************
#***********************************    Vimshottari Dashas       ***********************************************
#**************************************************************************************************************

#  Antar Dasha :
@kp.route('/kp/calculate_maha_antar_dasha', methods=['POST'])
def calculate_maha_antar_dasha_api():
    try:
        data = request.get_json()
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        response = calculate_maha_antar_dasha(data)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  Pratynatar Dasha 
@kp.route('/kp/calculate_maha_antar_pratyantar_dasha', methods=['POST'])
def calculate_maha_antar_pratyantar_dasha_api():
    """API endpoint to calculate Vimshottari Dasha periods."""
    try:
        data = request.get_json()
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        response = calculate_maha_antar_pratyantar_dasha(data)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  Sookshma Dasha 

@kp.route('/kp/calculate_maha_antar_pratyantar_sooksha_dasha', methods=['POST'])
def calculate_maha_antar_pratyantar_sookshma_dasha():
    """API endpoint to calculate Vimshottari Dasha periods including Sookshma Dasha."""
    try:
        data = request.get_json()
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        response = calculate_maha_antar_pratyantar_sooksha_dashas(data)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  Prana Dasha :
@kp.route('/kp/calculate_maha_antar_pratyantar_pran_dasha', methods=['POST'])
def calculate_maha_antar_pratyantar_dasha_pran():
    """API endpoint to calculate Vimshottari Dasha periods including Sookshma and Pran Dasha."""
    try:
        data = request.get_json()
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        response = calculate_maha_antar_pratyantar_pran_dasha(data)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500






#**************************************************************************************************************
#***********************************    Shodamsha Summary       ***********************************************
#**************************************************************************************************************

@kp.route('/kp/shodasha_varga_signs', methods=['POST'])
def shodasha_varga_signs():
    try:
        data = request.get_json()
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        utc_dt = local_to_utc_kp(birth_date, birth_time, timezone_offset)
        jd = julian_day_kp(utc_dt)

        # Sidereal positions of all planets
        sid_positions = get_sidereal_positions_kp(jd)
        sid_asc, asc_sign_idx, asc_deg_in_sign = get_sidereal_asc_kp(jd, latitude, longitude)
        sid_positions['Ascendant'] = (sid_asc, asc_sign_idx, asc_deg_in_sign)

        summary = {}
        for pname in sid_positions.keys():
            summary[pname] = {}

        for chart in CHARTS_kp:
            for pname, (lon, sign_idx, deg_in_sign) in sid_positions.items():
                varga_idx = varga_sign_kp(sign_idx, deg_in_sign, chart)
                summary[pname][chart] = {"sign": SIGNS_kp[varga_idx]}

        return jsonify({
            "ayanamsa": "KP New",
            "house_system": "Placidus",
            "shodasha_varga_signs": summary,
            "user_name": user_name
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  KP Horary 
@kp.route('/kp/kp_horary', methods=['POST'])
def kp_horary():
    try:
        data = request.get_json()
        horary_num = int(data["horary_number"])
        date_str = data["date"]
        time_str = data["time"]
        tz_offset = float(data.get("tz_offset", 5.5))
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        question = data["question"]
        jd = julday_from_date_time(date_str, time_str, tz_offset)
        question_lower = question.lower()
        if "house" in question_lower or "property" in question_lower or "buy" in question_lower:
            main_house = 4
            good_houses = [4,11]
            bad_houses = [3,6,12]
        elif "job" in question_lower or "career" in question_lower or "work" in question_lower:
            main_house = 10
            good_houses = [6,10,11]
            bad_houses = [5,8,12]
        elif "marriage" in question_lower or "spouse" in question_lower or "partner" in question_lower:
            main_house = 7
            good_houses = [2,7,11]
            bad_houses = [1,6,10]
        else:
            main_house = int(data.get("main_house", 10))
            good_houses = [6,10,11]
            bad_houses = [5,8,12]
    except Exception as e:
        return jsonify({"error": "Invalid input, error: %s" % str(e)}), 400

    asc_long = get_asc_from_horary_num(horary_num)
    sign, sign_name, asc_deg_in_sign = sign_deg(asc_long)
    chain = get_nakshatra_chain(asc_long, 4)
    ascendant = {
        "longitude": round(asc_long, 6),
        "sign": sign_name,
        "deg_in_sign": round(asc_deg_in_sign, 6),
        "rasi_lord": get_sign_lord(sign_name),
        "nakshatra_lord": chain[0],
        "sub_lord": chain[1],
        "sub_sub_lord": chain[2],
        "sub_sub_sub_lord": chain[3]
    }

    cusps = house_cusps(jd, lat, lon, asc_long, KP_NEW_AYANAMSA)
    planets = planet_chain(jd, KP_NEW_AYANAMSA)
    planets_in_houses, planets = planet_house_assignment(planets, cusps)
    moon = next(p for p in planets if p["name"] == "Moon")
    radicality = check_radicality(asc_long)
    moon_voc = check_void_of_course_moon(planets, cusps)
    dasha_path = calc_vimshottari_dasha_path(jd, moon["longitude"])
    lagna_planets = planets_in_houses[0]

    ruling_planets = get_ruling_planets(ascendant, moon, date_str)
    significators = get_significators_expanded(main_house, cusps, planets)
    sub_lord_chain = sub_lord_chain_judgment(main_house, cusps, planets, good_houses, bad_houses)
    kp_timing = kp_timing_by_dasha_layers(dasha_path, planets, cusps, good_houses)

    verdict = sub_lord_chain["verdict"]
    confidence = sub_lord_chain["confidence"]
    rationale = f"Sub-lord chain verdict: {sub_lord_chain['rationale']}. "
    if kp_timing:
        event_timing = kp_timing[0]
        rationale += f"Event window: {event_timing['event_estimate']}."
        verdict += " (with dasha support)"
    else:
        rationale += "No clear Dasha timing for event."
    final_judgment = {
        "yes_no": verdict,
        "confidence": confidence,
        "rationale": rationale,
        "timing_estimate": kp_timing[0] if kp_timing else None
    }

    output = {
        "question": question,
        "horary_number": horary_num,
        "date": date_str,
        "time": time_str,
        "tz_offset": tz_offset,
        "latitude": lat,
        "longitude": lon,
        "ascendant": ascendant,
        "house_cusps": cusps,
        "planets": planets,
        "planets_in_houses": planets_in_houses,
        "lagna_planets": lagna_planets,
        "vimshottari_dasha": dasha_path,
        "kp_timing": kp_timing,
        "chart_radicality": radicality,
        "moon_void_of_course": moon_voc,
        "ruling_planets": ruling_planets,
        "significators": significators,
        "sub_lord_chain_judgment": sub_lord_chain,
        "main_house": main_house,
        "final_judgment": final_judgment
    }
    return jsonify(output)





