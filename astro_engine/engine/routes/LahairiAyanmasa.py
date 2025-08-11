from asyncio.log import logger
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
# from venv import logger
import swisseph as swe



swe.set_ephe_path('astro_api/ephe')


from astro_engine.engine.lagnaCharts.LahiriHoraLagna import lahiri_hora_calculate_hora_lagna, lahiri_hora_calculate_house, lahiri_hora_calculate_sunrise_jd_and_asc, lahiri_hora_get_julian_day, lahiri_hora_get_sign_and_degrees, lahiri_hora_nakshatra_and_pada
from astro_engine.engine.lagnaCharts.LahiriBavaLagna import PLANET_IDS, bava_calculate_bhava_lagna, bava_calculate_house, bava_calculate_sunrise, bava_get_julian_day, bava_get_sign_and_degrees, bava_nakshatra_and_pada
from astro_engine.engine.ashatakavargha.LahiriVarghSigns import DCHARTS, lahiri_sign_get_sidereal_asc, lahiri_sign_get_sidereal_positions, lahiri_sign_julian_day, lahiri_sign_local_to_utc, lahiri_sign_varga_sign
from astro_engine.engine.ashatakavargha.Sarvasthakavargha import lahiri_sarvathakavargha
from astro_engine.engine.dashas.AntarDasha import calculate_dasha_antar_balance, calculate_mahadasha_periods, calculate_moon_sidereal_antar_position, get_julian_dasha_day, get_nakshatra_and_antar_lord
from astro_engine.engine.dashas.LahiriPranDasha import calculate_dasha_balance_pran, calculate_moon_sidereal_position_prana, calculate_pranaDasha_periods, get_julian_day_pran, get_nakshatra_and_lord_prana
from astro_engine.engine.dashas.Pratyantardashas import calculate_Pratythardasha_periods, calculate_moon_praty_sidereal_position, calculate_pratythar_dasha_balance, get_julian_pratyathar_day, get_nakshatra_party_and_lord
from astro_engine.engine.dashas.Sookashama import calculate_moon_sookshma_sidereal_position, calculate_sookshma_dasha_balance, calculate_sookshma_dasha_periods, get_julian_sookshma_day, get_nakshatra_and_lord_sookshma
from astro_engine.engine.divisionalCharts.ChathruthamshaD4 import  get_julian_day, lahairi_Chaturthamsha
from astro_engine.engine.divisionalCharts.ChaturvimshamshaD24 import  lahairi_Chaturvimshamsha
from astro_engine.engine.divisionalCharts.DashamshaD10 import  lahairi_Dashamsha
from astro_engine.engine.divisionalCharts.DreshkanaD3 import PLANET_NAMES, lahairi_drerkhana
from astro_engine.engine.divisionalCharts.DwadashamshaD12 import  lahairi_Dwadashamsha
from astro_engine.engine.divisionalCharts.HoraD2 import lahairi_hora_chart   
from astro_engine.engine.divisionalCharts.KvedamshaD40 import  lahairi_Khavedamsha
from astro_engine.engine.divisionalCharts.NavamshaD9 import  lahairi_navamsha_chart
from astro_engine.engine.divisionalCharts.SaptamshaD7 import  lahairi_saptamsha
from astro_engine.engine.divisionalCharts.SaptavimshamshaD27 import PLANET_CODES, ZODIAC_SIGNS_d27, d27_calculate_ascendant, d27_calculate_house, d27_calculate_longitude, d27_calculate_sidereal_longitude, d27_get_julian_day_utc, d27_get_nakshatra_pada, d27_get_sign_index
from astro_engine.engine.divisionalCharts.ShodasmasD16 import  lahairi_Shodashamsha

from astro_engine.engine.divisionalCharts.TrimshamshaD30 import lahiri_trimshamsha_D30
from astro_engine.engine.lagnaCharts.ArudhaLagna import lahairi_arudha_lagna
from astro_engine.engine.lagnaCharts.EqualLagan import SIGNS,  lahairi_equal_bava
from astro_engine.engine.lagnaCharts.KPLagna import  lahairi_kp_bava
from astro_engine.engine.lagnaCharts.LahiriKarkamshaD1 import lahiri_karkamsha_d1
from astro_engine.engine.lagnaCharts.LahiriKarkamshaD9 import lahiri_karkamsha_D9
from astro_engine.engine.lagnaCharts.Sripathi import calculate_ascendant_sri, get_nakshatra_pada_sri, get_planet_data_sri
from astro_engine.engine.natalCharts.natal import lahairi_natal,  longitude_to_sign, format_dms
from astro_engine.engine.natalCharts.transit import  lahairi_tranist
from astro_engine.engine.numerology.LoShuGridNumerology import calculate_lo_shu_grid
from astro_engine.engine.ashatakavargha.Binnastakavargha import  lahiri_binnastakavargha
from astro_engine.engine.numerology.NumerologyData import calculate_chaldean_numbers, calculate_date_numerology, get_sun_sign, get_element_from_number, get_sun_sign_element, get_elemental_compatibility, personal_interpretations, business_interpretations, ruling_planets, planet_insights, sun_sign_insights, number_colors, number_gemstones, planet_days
from astro_engine.engine.divisionalCharts.AkshavedamshaD45 import  lahairi_Akshavedamsha
from astro_engine.engine.divisionalCharts.ShashtiamshaD60 import  lahairi_Shashtiamsha
from astro_engine.engine.divisionalCharts.VimshamshaD20 import  lahairi_Vimshamsha
from astro_engine.engine.natalCharts.SudharashanaChakara import calculate_sidereal_positions, generate_chart, get_sign
from astro_engine.engine.natalCharts.SunChart import  lahrir_sun_chart,  validate_input_sun
from astro_engine.engine.natalCharts.MoonChart import  lahairi_moon_chart, validate_input

# Import caching decorators
try:
    from ...cache_manager import cache_calculation
    from ...metrics_manager import metrics_decorator
    from ...structured_logger import structured_log_decorator
except ImportError:
    # Fallback if import fails
    def cache_calculation(prefix, ttl=None):
        def decorator(func):
            return func
        return decorator
    
    def metrics_decorator(calculation_type):
        def decorator(func):
            return func
        return decorator
    
    def structured_log_decorator(calculation_type, log_inputs=True):
        def decorator(func):
            return func
        return decorator

bp = Blueprint('bp_routes', __name__)

# Natal Chart
@bp.route('/lahiri/natal', methods=['POST'])
@cache_calculation('natal_chart', ttl=86400)  # 24 hour cache
@metrics_decorator('natal_chart')
@structured_log_decorator('natal_chart', log_inputs=True)
def natal_chart():
    try:
        from flask import current_app
        import time
        
        # Get structured logger
        logger = None
        if hasattr(current_app, 'structured_logger'):
            logger = current_app.structured_logger.get_logger('natal_chart_endpoint')
        
        # Record user interaction
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_user_interaction('chart_request', 'natal_chart')
            current_app.metrics_manager.record_chart_request('natal', 'lahiri')
        
        birth_data = request.get_json()
        if not birth_data:
            if logger:
                logger.warning("No JSON data provided in request")
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        missing_fields = [field for field in required if field not in birth_data]
        if missing_fields:
            if logger:
                logger.warning("Missing required parameters", missing_fields=missing_fields)
            return jsonify({"error": "Missing required parameters"}), 400

        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            if logger:
                logger.warning("Invalid coordinates", latitude=latitude, longitude=longitude)
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        if logger:
            logger.info("Starting natal chart calculation",
                       user_name=birth_data['user_name'],
                       birth_date=birth_data['birth_date'],
                       coordinates=f"{latitude},{longitude}")

        # Record ephemeris access timing
        ephemeris_start = time.time()
        
        # Calculate chart data
        chart_data = lahairi_natal(birth_data)
        
        # Calculate complexity score (number of planets * aspects)
        complexity_score = len(chart_data.get('planet_positions', {})) * 12  # 12 houses
        
        # Record ephemeris calculation time
        ephemeris_duration = time.time() - ephemeris_start
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_ephemeris_calculation('natal_chart', ephemeris_duration)
            current_app.metrics_manager.record_ephemeris_file_read('seas_*.se1', 'success')
            current_app.metrics_manager.record_calculation_complexity('natal', complexity_score)

        if logger:
            logger.info("Natal chart calculation completed",
                       ephemeris_duration=ephemeris_duration,
                       planet_count=len(chart_data.get('planet_positions', {})),
                       complexity_score=complexity_score)

        # Format planetary positions
        planetary_positions_json = {}
        for planet, data in chart_data['planet_positions'].items():
            sign, sign_deg = longitude_to_sign(data['lon'])
            dms = format_dms(sign_deg)
            house = chart_data['planet_houses'][planet]
            planetary_positions_json[planet] = {
                "sign": sign,
                "degrees": dms,
                "retrograde": data['retro'],
                "house": house,
                "nakshatra": data['nakshatra'],
                "pada": data['pada']
            }

        # Format ascendant
        asc_sign, asc_deg = longitude_to_sign(chart_data['ascendant']['lon'])
        asc_dms = format_dms(asc_deg)
        ascendant_json = {
            "sign": asc_sign,
            "degrees": asc_dms,
            "nakshatra": chart_data['ascendant']['nakshatra'],
            "pada": chart_data['ascendant']['pada']
        }

        # Format house signs
        house_signs_json = {f"House {i+1}": {"sign": house["sign"], "start_longitude": format_dms(house["start_longitude"])}
                           for i, house in enumerate(chart_data['house_signs'])}

        # Construct response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": ascendant_json,
            # "house_signs": house_signs_json,
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{chart_data['ayanamsa_value']:.6f}",
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            }
        }
        
        if logger:
            logger.info("Natal chart response prepared",
                       response_size=len(str(response)),
                       ascendant_sign=asc_sign)
        
        return jsonify(response)

    except ValueError as ve:
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_error('ValueError', 'natal_chart')
        if hasattr(current_app, 'structured_logger'):
            current_app.structured_logger.log_error('ValueError', str(ve), 
                                                   {'endpoint': 'natal_chart'})
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_error('Exception', 'natal_chart')
        if hasattr(current_app, 'structured_logger'):
            current_app.structured_logger.log_error('Exception', str(e), 
                                                   {'endpoint': 'natal_chart'}, e)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Transit or Gochar Chart
@bp.route('/lahiri/transit', methods=['POST'])
@cache_calculation('transit_chart', ttl=3600)  # 1 hour cache (shorter for dynamic data)
@metrics_decorator('transit_chart')
def transit_chart():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Required fields for natal calculations
        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_tranist(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Sun Chart

@bp.route('/lahiri/calculate_sun_chart', methods=['POST'])
def calculate_sun_chart():
    """
    API endpoint to calculate Sun Chart (sidereal) with Whole Sign house system.
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input_sun(data)
        
        # Call the calculation function
        response = lahrir_sun_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Moon Chart

@bp.route('/lahiri/calculate_moon_chart', methods=['POST'])
def calculate_moon_chart():
    """
    API endpoint to calculate Moon Chart (sidereal) with Whole Sign house system.
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        # Call the calculation function
        response = lahairi_moon_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sudarshan Chakra
@bp.route('/lahiri/calculate_sudarshan_chakra', methods=['POST'])
def calculate_sudarshan_chakra():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd_birth = get_julian_day(birth_date, birth_time, tz_offset)
        positions = calculate_sidereal_positions(jd_birth, latitude, longitude)
        asc_sign, _ = get_sign(positions["Ascendant"])
        moon_sign, _ = get_sign(positions["Moon"])
        sun_sign, _ = get_sign(positions["Sun"])
        asc_sign_idx = SIGNS.index(asc_sign)
        moon_sign_idx = SIGNS.index(moon_sign)
        sun_sign_idx = SIGNS.index(sun_sign)
        lagna_chart = generate_chart(positions, asc_sign_idx)
        chandra_chart = generate_chart(positions, moon_sign_idx)
        surya_chart = generate_chart(positions, sun_sign_idx)

        response = {
            "user_name": user_name,
            "sudarshan_chakra": {"lagna_chart": lagna_chart, "chandra_chart": chandra_chart, "surya_chart": surya_chart}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Hora (D-2)

# @bp.route('/lahiri/calculate_d2_hora', methods=['POST'])
# def calculate_d2_hora():
#     """API endpoint to calculate the D2 Hora chart."""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(field in data for field in required_fields):
#             return jsonify({"error": "Missing required fields"}), 400

#         user_name = data.get('user_name', 'Unknown')
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         # Call the calculation function
#         result = lahairi_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset)
#         response = {
#             'user_name': user_name,
#             'd2_hora_chart': result,
#             'metadata': {
#                 'ayanamsa': 'Lahiri',
#                 'house_system': 'Whole Sign',
#                 'calculation_time': datetime.utcnow().isoformat(),
#                 'input': data
#             }
#         }
#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500


@bp.route('/lahiri/calculate_d2_hora', methods=['POST'])
def calculate_d2_hora():
    """API endpoint to calculate the D2 Hora chart in natal-style response."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', '')

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call calculation
        result = lahairi_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset)

        # Wrap calculation for natal-style response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": result.get("planets", {}),  # rename 'planets' to 'planetary_positions'
            "ascendant": {
                "sign": result["ascendant"].get("d2_sign", ""),
                "degrees": str(round(result["ascendant"].get("d2_degree", 0), 2)),
                "nakshatra": result["ascendant"].get("nakshatra", ""),
                "pada": result["ascendant"].get("pada", "")
            },
            "notes": {
                "ayanamsa": "Lahiri",
                "chart_type": "Hora (D2)",
                "house_system": "Whole Sign"
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# Dreshkana (D-3)

@cache_calculation('d3_chart', ttl=86400)  # 24 hour cache
@metrics_decorator('d3_chart')
@bp.route('/lahiri/calculate_d3', methods=['POST'])
def calculate_d3_chart_endpoint():
    """API endpoint to calculate D3 chart with structured response like natal chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', '')

        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # --- Use the updated function ---
        d3_data = lahairi_drerkhana(
            data['birth_date'],
            data['birth_time'],
            latitude,
            longitude,
            float(data['timezone_offset'])
        )

        # Assemble notes block
        notes = {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{d3_data['ayanamsa_value']:.6f}",
            "chart_type": "D3 (Drerkhana)",
            "house_system": "Whole Sign"
        }

        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": data['birth_date'],
                "birth_time": data['birth_time'],
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": float(data['timezone_offset'])
            },
            "planetary_positions": d3_data["planetary_positions"],
            "ascendant": d3_data["ascendant"],
            "notes": notes
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Error in D3 chart calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Chaturthamsha (D-4)
@bp.route('/lahiri/calculate_d4', methods=['POST'])
def calculate_d4():
    """API endpoint to calculate the Chaturthamsha (D4) chart."""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_Chaturthamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Saptamsha (D-7)

@bp.route('/lahiri/calculate_d7_chart', methods=['POST'])
def calculate_d7_chart_endpoint():
    """API endpoint to calculate D7 chart from birth details in natal-style response."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', '')

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate D7 chart using lahairi_saptamsha
        d7_data = lahairi_saptamsha(birth_date, birth_time, latitude, longitude, tz_offset)

        # Prepare natal-style response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": {planet: d7_data[planet] for planet in PLANET_NAMES},
            "ascendant": {
                "sign": d7_data["Ascendant"].get("sign", ""),
                "degrees": str(d7_data["Ascendant"].get("degrees", "")),
                "nakshatra": d7_data["Ascendant"].get("nakshatra", ""),
                "pada": d7_data["Ascendant"].get("pada", "")
            },
            "notes": {
                "ayanamsa": "Lahiri",
                "chart_type": "Saptamsa (D7)",
                "house_system": "Whole Sign"
            }
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D7 calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500





# Dashamsha (D-10)

@bp.route('/lahiri/calculate_d10', methods=['POST'])
def calculate_d10():
    """
    Flask API endpoint to calculate the Dashamsha (D10) chart accurately.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - Planetary positions, ascendant with conjunctions, house signs, and metadata
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in data for key in required):
        return jsonify({"error": "Missing required parameters"}), 400

    response = lahairi_Dashamsha(data)
    return jsonify(response)



# Dwadashamsha (D-12)
@bp.route('/lahiri/calculate_d12', methods=['POST'])
def calculate_d12():
    """
    Flask API endpoint to calculate the Dwadasamsa (D12) chart.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - D12 ascendant, planetary positions with retrograde, nakshatras, padas, house signs, and metadata
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        # Call the calculation function
        response = lahairi_Dwadashamsha(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Shodashamsha (D-16)

@bp.route('/lahiri/calculate_d16', methods=['POST'])
def calculate_d16():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        enforce_opposition = data.get('enforce_opposition', False)

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180) or not (-12 <= tz_offset <= 14):
            return jsonify({"error": "Invalid geographic or timezone data"}), 400

        # Call the calculation function
        response = lahairi_Shodashamsha(birth_date, birth_time, latitude, longitude, tz_offset, enforce_opposition)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Vimshamsha (D-20)
@bp.route('/lahiri/calculate_d20', methods=['POST'])
def calculate_d20():
    """
    API endpoint to calculate the D20 (Vimsamsa) chart.
    
    Expects JSON input:
    {
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone_offset": float,
        "user_name": str (optional)
    }
    
    Returns:
        JSON response with D20 chart details or error message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Call the calculation function
        response = lahairi_Vimshamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




# Chaturvimshamsha (D-24)

@bp.route('/lahiri/calculate_d24', methods=['POST'])
def calculate_d24():
    """API endpoint to calculate D24 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        birth_date = data['birth_date']  # e.g., '1990-01-01'
        birth_time = data['birth_time']  # e.g., '12:00:00'
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])  # e.g., 5.5 for IST

        # Call the calculation function
        response = lahairi_Chaturvimshamsha(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Saptavimshamsha (D-27)

@bp.route('/lahiri/calculate_d27', methods=['POST'])
def calculate_d27_chart():
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        def format_dms(degrees):
            """Format degrees as DMS (degrees, minutes, seconds)."""
            deg = int(degrees)
            minutes = int((degrees - deg) * 60)
            seconds = int(((degrees - deg) * 60 - minutes) * 60)
            return f"{deg}°{minutes:02d}'{seconds:02d}\""

        jd_utc = d27_get_julian_day_utc(birth_date, birth_time, tz_offset)
        natal_asc_lon = d27_calculate_ascendant(jd_utc, latitude, longitude)
        d27_asc_lon = d27_calculate_longitude(natal_asc_lon)
        d27_asc_sign_index = d27_get_sign_index(d27_asc_lon)
        d27_asc_deg = d27_asc_lon % 30

        natal_planet_lons = {}
        natal_planet_retro = {}

        # Rahu/Ketu
        natal_rahu_lon, _ = d27_calculate_sidereal_longitude(jd_utc, swe.MEAN_NODE)
        natal_ketu_lon = (natal_rahu_lon + 180) % 360
        natal_planet_lons["Rahu"] = natal_rahu_lon
        natal_planet_lons["Ketu"] = natal_ketu_lon
        natal_planet_retro["Rahu"] = True
        natal_planet_retro["Ketu"] = True

        for planet, code in PLANET_CODES.items():
            if planet == "Rahu":
                continue  # Already handled
            lon, retro = d27_calculate_sidereal_longitude(jd_utc, code)
            natal_planet_lons[planet] = lon
            natal_planet_retro[planet] = retro

        # Format ascendant
        asc_nak, asc_lord, asc_pada = d27_get_nakshatra_pada(d27_asc_lon)
        ascendant_json = {
            "sign": ZODIAC_SIGNS_d27[d27_asc_sign_index],
            "degrees": format_dms(d27_asc_deg),
            "nakshatra": asc_nak,
            "pada": asc_pada
        }

        # Format planetary positions
        planetary_positions_json = {}
        for planet in list(PLANET_CODES.keys()) + ["Ketu"]:
            natal_lon = natal_planet_lons[planet]
            d27_lon = d27_calculate_longitude(natal_lon)
            d27_sign_index = d27_get_sign_index(d27_lon)
            d27_deg = d27_lon % 30
            house = d27_calculate_house(d27_asc_sign_index, d27_sign_index)
            retro = natal_planet_retro[planet]
            d27_nakshatra, d27_nak_lord, d27_pada = d27_get_nakshatra_pada(d27_lon)

            planetary_positions_json[planet] = {
                "sign": ZODIAC_SIGNS_d27[d27_sign_index],
                "degrees": format_dms(d27_deg),
                "retrograde": retro,
                "house": house,
                "nakshatra": d27_nakshatra,
                "pada": d27_pada
            }

        # Construct response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": ascendant_json,
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": "N/A",  # Update if ayanamsa value is available
                "chart_type": "D27",
                "house_system": "Whole Sign"
            }
        }
        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




#  Trimshamsha D-30 

@bp.route('/lahiri/calculate_d30', methods=['POST'])
def calculate_d30_chart():
    """API endpoint to calculate D30 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        def format_dms(degrees):
            """Format degrees as DMS (degrees, minutes, seconds)."""
            deg = int(degrees)
            minutes = int((degrees - deg) * 60)
            seconds = int(((degrees - deg) * 60 - minutes) * 60)
            return f"{deg}°{minutes:02d}'{seconds:02d}\""

        # Assume ZODIAC_SIGNS_d30 is defined similarly to ZODIAC_SIGNS_d27
        ZODIAC_SIGNS_d30 = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        # Perform D30 calculations (unchanged)
        natal_positions, d30_positions = lahiri_trimshamsha_D30(birth_date, birth_time, latitude, longitude, tz_offset)

        # Helper function to get sign index (assuming d27_get_sign_index is available)
        def get_sign_index(longitude_or_sign):
            if isinstance(longitude_or_sign, (int, float)):
                return int(longitude_or_sign // 30) % 12
            try:
                return ZODIAC_SIGNS_d30.index(longitude_or_sign.capitalize())
            except ValueError:
                return 0  # Default to Aries

        # Helper function to calculate house (assuming d27_calculate_house is available)
        def calculate_house(asc_sign_index, planet_sign_index):
            return ((planet_sign_index - asc_sign_index) % 12) + 1

        # Helper function for nakshatra and pada (assuming d27_get_nakshatra_pada is available)
        def get_nakshatra_pada(longitude):
            # Placeholder: Replace with actual nakshatra calculation if not provided
            return "Unknown", "Unknown", 1

        # Format ascendant
        asc_data = d30_positions.get("Ascendant", {})
        asc_sign = asc_data.get("sign") or ZODIAC_SIGNS_d30[get_sign_index(asc_data.get("longitude", 0))]
        asc_deg = asc_data.get("longitude", 0) % 30 if isinstance(asc_data.get("longitude"), (int, float)) else 0
        asc_nak = asc_data.get("nakshatra", "Unknown")
        asc_pada = asc_data.get("pada", 1)
        if asc_nak == "Unknown":
            asc_nak, asc_lord, asc_pada = get_nakshatra_pada(asc_data.get("longitude", 0))
        ascendant_json = {
            "sign": asc_sign,
            "degrees": format_dms(asc_deg),
            "nakshatra": asc_nak,
            "pada": asc_pada
        }
        asc_sign_index = get_sign_index(asc_sign)

        # Format planetary positions
        planetary_positions_json = {}
        for planet in d30_positions:
            if planet == "Ascendant":
                continue
            planet_data = d30_positions[planet]
            planet_sign = planet_data.get("sign") or ZODIAC_SIGNS_d30[get_sign_index(planet_data.get("longitude", 0))]
            planet_deg = planet_data.get("longitude", 0) % 30 if isinstance(planet_data.get("longitude"), (int, float)) else 0
            house = calculate_house(asc_sign_index, get_sign_index(planet_sign))
            retro = planet_data.get("retrograde", False)
            nakshatra = planet_data.get("nakshatra", "Unknown")
            pada = planet_data.get("pada", 1)
            if nakshatra == "Unknown":
                nakshatra, nak_lord, pada = get_nakshatra_pada(planet_data.get("longitude", 0))

            planetary_positions_json[planet] = {
                "sign": planet_sign,
                "degrees": format_dms(planet_deg),
                "retrograde": retro,
                "house": house,
                "nakshatra": nakshatra,
                "pada": pada
            }

        # Construct response
        response = {
            "user_name": data.get('user_name', 'Unknown'),
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": ascendant_json,
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": "N/A",  # Update if available
                "chart_type": "D30",
                "house_system": "Whole Sign"
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




# Khavedamsha (D-40)
@bp.route('/lahiri/calculate_d40', methods=['POST'])
def calculate_d40():
    """API endpoint to calculate the D40 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract input data
        birth_date = data['birth_date']  # e.g., '1990-01-01'
        birth_time = data['birth_time']  # e.g., '12:00:00'
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])  # e.g., 5.5 for IST

        # Call the calculation function
        response = lahairi_Khavedamsha(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500





# Akshavedamsha (D-45)
@bp.route('/lahiri/calculate_d45', methods=['POST'])
def calculate_d45():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Call the calculation function
        response = lahairi_Akshavedamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Shashtiamsha (D-60)

@bp.route('/lahiri/calculate_d60', methods=['POST'])
def calculate_d60():
    """API endpoint to calculate the D60 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract input data
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate D60 chart using lahairi_Shashtiamsha
        response = lahairi_Shashtiamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Navamsa Chart D9
@bp.route('/lahiri/navamsa', methods=['POST'])
@cache_calculation('navamsa_chart', ttl=86400)  # 24 hour cache
@metrics_decorator('navamsa_chart')
def navamsa_chart():
    """API endpoint to calculate Navamsa (D9) chart with retrograde, nakshatras, and padas."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Check for required parameters
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_navamsha_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Sripathi Bhava
# @bp.route('/lahiri/calculate_sripathi_bhava', methods=['POST'])
# def calculate_sripathi_bhava():
#     """Compute the Sripathi Bhava Chart and return JSON output."""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400
        
#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in data for key in required_fields):
#             return jsonify({"error": "Missing required parameters"}), 400

#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         # logger.debug(f"Input: Date={birth_date}, Time={birth_time}, Lat={latitude}, Lon={longitude}, TZ Offset={tz_offset}")

#         # Call the calculation function
#         response = lahairi_sripathi_bava(birth_date, birth_time, latitude, longitude, tz_offset)
#         # logger.debug(f"Output JSON: {response}")
#         return jsonify(response), 200

#     except ValueError as ve:
#         # logger.error(f"Invalid input format: {str(ve)}")
#         return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
#     except Exception as e:
#         # logger.error(f"Calculation error: {str(e)}")
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500



@bp.route('/lahiri/calculate_sripathi_bhava', methods=['POST'])
def calculate_sripathi_bhava():
    """Compute the Sripathi Bhava Chart and return JSON output with nakshatra and pada."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # logger.debug(f"Input: Date={birth_date}, Time={birth_time}, Lat={latitude}, Lon={longitude}, TZ Offset={tz_offset}")

        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
        asc_lon, asc_sign_index, cusps = calculate_ascendant_sri(jd_ut, latitude, longitude)
        asc_sign = SIGNS[asc_sign_index]
        asc_degrees = asc_lon % 30
        asc_nakshatra, asc_pada = get_nakshatra_pada_sri(asc_lon)

        natal_positions = get_planet_data_sri(jd_ut, asc_lon, cusps)

        response = {
            "ascendant": {
                "sign": asc_sign,
                "degrees": round(asc_degrees, 4),
                "nakshatra": asc_nakshatra,
                "pada": asc_pada
            },
            "planets": natal_positions
        }
        # logger.debug(f"Output JSON: {response}")
        return jsonify(response), 200

    except ValueError as ve:
        # logger.error(f"Invalid input format: {str(ve)}")
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        # logger.error(f"Calculation error: {str(e)}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


# KP Bhava
@bp.route('/lahiri/calculate_kp_bhava', methods=['POST'])
def calculate_kp_bhava():
    """API endpoint to calculate KP Bhava chart."""
    data = request.get_json()
    try:
        # Extract and validate input
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        result = lahairi_kp_bava(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result), 200

    except KeyError as e:
        return jsonify({"error": f"Missing input field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid input value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500





# Bhava Lagna


@bp.route('/lahiri/calculate_bhava_lagna', methods=['POST'])
def bava_calculate_bhava_lagna_chart():
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        birth_jd = bava_get_julian_day(birth_date, birth_time, tz_offset)
        sunrise_jd, sunrise_sun_lon = bava_calculate_sunrise(birth_jd, lat, lon, tz_offset)
        bl_lon = bava_calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon)
        bl_sign, bl_degrees = bava_get_sign_and_degrees(bl_lon)
        bl_nak, bl_nak_lord, bl_pada = bava_nakshatra_and_pada(bl_lon)

        positions = {}
        for planet, pid in PLANET_IDS.items():
            if planet == 'Ketu':
                continue
            pos_data = swe.calc_ut(birth_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
            lon = pos_data[0] % 360
            sign, degrees = bava_get_sign_and_degrees(lon)
            retrograde = 'R' if pos_data[3] < 0 else ''
            house = bava_calculate_house(sign, bl_sign)
            nak, nak_lord, pada = bava_nakshatra_and_pada(lon)
            positions[planet] = {
                "degrees": round(degrees, 4), "sign": sign, "retrograde": retrograde,
                "house": house, "nakshatra": nak, "nakshatra_lord": nak_lord, "pada": pada
            }

        # Calculate Ketu
        rahu_lon = positions['Rahu']['degrees'] + (SIGNS.index(positions['Rahu']['sign']) * 30)
        ketu_lon = (rahu_lon + 180) % 360
        ketu_sign, ketu_degrees = bava_get_sign_and_degrees(ketu_lon)
        ketu_nak, ketu_nak_lord, ketu_pada = bava_nakshatra_and_pada(ketu_lon)
        positions['Ketu'] = {
            "degrees": round(ketu_degrees, 4), "sign": ketu_sign, "retrograde": "",
            "house": bava_calculate_house(ketu_sign, bl_sign),
            "nakshatra": ketu_nak, "nakshatra_lord": ketu_nak_lord, "pada": ketu_pada
        }

        response = {
            "bhava_lagna": {
                "sign": bl_sign, "degrees": round(bl_degrees, 4),
                "nakshatra": bl_nak, "nakshatra_lord": bl_nak_lord, "pada": bl_pada
            },
            "planets": positions
        }
        return jsonify(response), 200

    except Exception as e:
        # logging.error(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Equal Bhava Lagna
@bp.route('/lahiri/calculate_equal_bhava_lagna', methods=['POST'])
def calculate_equal_bhava_lagna():
    """API endpoint to calculate Equal Bhava Lagna, house cusps, and planetary positions."""
    try:
        # Parse and validate JSON input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        response = lahairi_equal_bava(birth_date, birth_time, latitude, longitude, tz_offset)
        response["user_name"] = user_name
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Arudha lagna

@bp.route('/lahiri/calculate_arudha_lagna', methods=['POST'])
# def calculate_arudha_lagna():
#     """API endpoint to calculate Arudha Lagna chart with retrograde, nakshatras, and padas."""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(field in data for field in required_fields):
#             return jsonify({"error": "Missing required fields"}), 400

#         user_name = data.get('user_name', 'Unknown')
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         # Call the calculation function
#         result = lahairi_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset)
#         response = {
#             'user_name': user_name,
#             'arudha_lagna': result['arudha_lagna'],
#             'planets': result['planets'],
#             'metadata': {
#                 'ayanamsa': 'Lahiri',
#                 'calculation_time': datetime.utcnow().isoformat(),
#                 'input': data
#             }
#         }
#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500


def calculate_arudha_lagna():
    """API endpoint to calculate Arudha Lagna chart with retrograde, nakshatras, and padas."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Compute chart data
        result = lahairi_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset)

        response = {
            "ascendant": result["ascendant"],
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": "",  # You may add real value if you want, else leave as empty string
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            },
            "planetary_positions": result["planetary_positions"],
            "user_name": user_name
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Karkamsha Birth chart 

@bp.route('/lahiri/calculate_d1_karkamsha', methods=['POST'])
def calculate_d1_karkamsha_endpoint():
    """Calculate the D1 Karkamsha chart based on birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        results = lahiri_karkamsha_d1(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct response
        response = {
            "user_name": user_name,
            "d1_ascendant": results['d1_ascendant'],
            "atmakaraka": results['atmakaraka'],
            "karkamsha_ascendant": results['karkamsha_ascendant'],
            "d1_karkamsha_chart": results['d1_karkamsha_chart']
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  KarKamsha D9 Chart 
@bp.route('/lahiri/calculate_karkamsha_d9', methods=['POST'])
def calculate_karkamsha_endpoint():
    """API endpoint to calculate the Karkamsha chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        results = lahiri_karkamsha_D9(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct response
        response = {
            "user_name": user_name,
            "atmakaraka": results['atmakaraka'],
            "karkamsha_sign": results['karkamsha_sign'],
            "karkamsha_chart": results['karkamsha_chart']
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Hora Lagna Chart :

@bp.route('/lahiri/calculate_hora_lagna', methods=['POST'])
def lahiri_hora_calculate_hora_lagna_chart():
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        global tz_offset
        tz_offset = float(data['timezone_offset'])

        birth_jd = lahiri_hora_get_julian_day(birth_date, birth_time, tz_offset)
        sunrise_jd, sunrise_asc = lahiri_hora_calculate_sunrise_jd_and_asc(birth_jd, lat, lon, tz_offset)
        hl_lon = lahiri_hora_calculate_hora_lagna(birth_jd, sunrise_jd, sunrise_asc)
        hl_sign, hl_degrees = lahiri_hora_get_sign_and_degrees(hl_lon)
        hl_nak, hl_nak_lord, hl_pada = lahiri_hora_nakshatra_and_pada(hl_lon)

        positions = {}
        for planet, pid in PLANET_IDS.items():
            if planet == 'Ketu':
                continue
            pos_data = swe.calc_ut(birth_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
            lon = pos_data[0] % 360
            sign, degrees = lahiri_hora_get_sign_and_degrees(lon)
            retrograde = 'R' if pos_data[3] < 0 else ''
            house = lahiri_hora_calculate_house(sign, hl_sign)
            nak, nak_lord, pada = lahiri_hora_nakshatra_and_pada(lon)
            positions[planet] = {
                "degrees": round(degrees, 4), "sign": sign, "retrograde": retrograde,
                "house": house, "nakshatra": nak, "nakshatra_lord": nak_lord, "pada": pada
            }

        rahu_lon = positions['Rahu']['degrees'] + (SIGNS.index(positions['Rahu']['sign']) * 30)
        ketu_lon = (rahu_lon + 180) % 360
        ketu_sign, ketu_degrees = lahiri_hora_get_sign_and_degrees(ketu_lon)
        ketu_nak, ketu_nak_lord, ketu_pada = lahiri_hora_nakshatra_and_pada(ketu_lon)
        positions['Ketu'] = {
            "degrees": round(ketu_degrees, 4), "sign": ketu_sign, "retrograde": "",
            "house": lahiri_hora_calculate_house(ketu_sign, hl_sign),
            "nakshatra": ketu_nak, "nakshatra_lord": ketu_nak_lord, "pada": ketu_pada
        }

        response = {
            "hora_lagna": {
                "sign": hl_sign, "degrees": round(hl_degrees, 4),
                "nakshatra": hl_nak, "nakshatra_lord": hl_nak_lord, "pada": hl_pada
            },
            "planets": positions
        }
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Synastry

# @bp.route('/lahiri/synastry', methods=['POST'])
# def synastry():
#     data = request.get_json()
#     if not data or 'person_a' not in data or 'person_b' not in data:
#         return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

#     valid_a, error_a = validate_person_data(data['person_a'], 'person_a')
#     if not valid_a:
#         return jsonify({'error': error_a}), 400
#     valid_b, error_b = validate_person_data(data['person_b'], 'person_b')
#     if not valid_b:
#         return jsonify({'error': error_b}), 400

#     try:
#         # Calculate chart data for both persons
#         chart_a = lahairi_synastry(data['person_a'])
#         chart_b = lahairi_synastry(data['person_b'])

#         # Prepare positions with ascendant for aspects
#         pos_a_with_asc = {**chart_a['positions'], 'Ascendant': chart_a['ascendant']}
#         pos_b_with_asc = {**chart_b['positions'], 'Ascendant': chart_b['ascendant']}

#         # Synastry analysis
#         aspects = calculate_aspects(pos_a_with_asc, pos_b_with_asc)
#         overlays_a_in_b = analyze_house_overlays(chart_a['positions'], chart_b['asc_sign_idx'])
#         overlays_b_in_a = analyze_house_overlays(chart_b['positions'], chart_a['asc_sign_idx'])
#         nodal_a = evaluate_nodal_connections(chart_a['positions'], chart_b['positions'])
#         nodal_b = evaluate_nodal_connections(chart_b['positions'], chart_a['positions'])
#         interpretation = interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b)

#         # Response
#         response = {
#             'person_a': {
#                 'name': chart_a['name'],
#                 'birth_details': data['person_a'],
#                 'ascendant': {
#                     'sign': chart_a['ascendant']['sign'],
#                     'degree': chart_a['ascendant']['degree']
#                 },
#                 'planets': {k: {**v, 'house': chart_a['houses'][k]} for k, v in chart_a['positions'].items()}
#             },
#             'person_b': {
#                 'name': chart_b['name'],
#                 'birth_details': data['person_b'],
#                 'ascendant': {
#                     'sign': chart_b['ascendant']['sign'],
#                     'degree': chart_b['ascendant']['degree']
#                 },
#                 'planets': {k: {**v, 'house': chart_b['houses'][k]} for k, v in chart_b['positions'].items()}
#             },
#             'synastry': {
#                 'aspects': aspects,
#                 'house_overlays': {'a_in_b': overlays_a_in_b, 'b_in_a': overlays_b_in_a},
#                 'nodal_connections': {'person_a': nodal_a, 'person_b': nodal_b},
#                 'interpretation': interpretation
#             }
#         }
#         return jsonify(response), 200
#     except Exception as e:
#         logging.error(f"Error in synastry calculation: {str(e)}")
#         return jsonify({'error': str(e)}), 400


# @bp.route('/synastry', methods=['POST'])
# def synastry_endpoint():
#     data = request.get_json()
#     if not data or 'person_a' not in data or 'person_b' not in data:
#         return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

#     try:
#         response = synastry(data['person_a'], data['person_b'])
#         return jsonify(response), 200
#     except Exception as e:
#         logger.error(f"Error in synastry calculation: {str(e)}")
#         return jsonify({'error': str(e)}), 400





# # Composite Chart

# @bp.route('/composite', methods=['POST'])
# def composite_chart():
#     data = request.get_json()
#     if not data or 'person_a' not in data or 'person_b' not in data:
#         return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

#     try:
#         reference_date = data.get('reference_date')
#         reference_time = data.get('reference_time')
#         response = composite(data['person_a'], data['person_b'], reference_date, reference_time)
#         return jsonify(response), 200
#     except Exception as e:
#         logger.error(f"Error in composite chart calculation: {str(e)}")
#         return jsonify({'error': str(e)}), 400



# # Progressed Chart

# @bp.route('/lahiri/progressed', methods=['POST'])
# def progressed_chart():
#     data = request.get_json()
#     if not data or 'person' not in data:
#         return jsonify({'error': 'Person data must be provided'}), 400

#     try:
#         response = progressed(data['person'])
#         return jsonify(response), 200
#     except Exception as e:
#         logger.error(f"Error in progressed chart calculation: {str(e)}")
#         return jsonify({'error': str(e)}), 400






# Chaldean Numerology
@bp.route('/lahiri/chaldean_numerology', methods=['POST'])
def numerology():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Missing 'name' in JSON data"}), 400
        name = data['name']
        if not isinstance(name, str):
            return jsonify({"error": "'name' must be a string"}), 400

        numbers = calculate_chaldean_numbers(name)
        compound_number = numbers['compound_number']
        root_number = numbers['root_number']
        element = get_element_from_number(root_number)
        personal_interpretation = personal_interpretations.get(root_number, "No interpretation available.")
        ruling_planet = ruling_planets.get(root_number, "Unknown")
        insight = planet_insights.get(ruling_planet, {"positive": "N/A", "challenge": "N/A", "business_tip": "N/A"})
        colors = number_colors.get(root_number, [])
        gemstone = number_gemstones.get(root_number, "N/A")
        day = planet_days.get(ruling_planet, "N/A")

        response = {
            "original_name": name,
            "compound_number": compound_number,
            "root_number": root_number,
            "element": element,
            "ruling_planet": ruling_planet,
            "personal_interpretation": personal_interpretation,
            "astrological_insight": {"positive": insight["positive"], "challenge": insight["challenge"]},
            "recommendations": {"colors": colors, "gemstone": gemstone, "auspicious_day": day}
        }

        if 'tagline' in data and isinstance(data['tagline'], str):
            tagline = data['tagline']
            tagline_numbers = calculate_chaldean_numbers(tagline)
            tagline_compound = tagline_numbers['compound_number']
            tagline_root = tagline_numbers['root_number']
            tagline_element = get_element_from_number(tagline_root)
            business_interpretation = business_interpretations.get(tagline_root, "No interpretation available.")
            tagline_planet = ruling_planets.get(tagline_root, "Unknown")
            tagline_insight = planet_insights.get(tagline_planet, {"positive": "N/A", "challenge": "N/A", "business_tip": "N/A"})
            compatibility = get_elemental_compatibility(element, tagline_element)
            response["business_tagline"] = {
                "original": tagline,
                "compound_number": tagline_compound,
                "root_number": tagline_root,
                "element": tagline_element,
                "ruling_planet": tagline_planet,
                "business_interpretation": business_interpretation,
                "astrological_insight": {"positive": tagline_insight["positive"], "challenge": tagline_insight["challenge"], "business_tip": tagline_insight["business_tip"]},
                "compatibility_with_personal": f"Personal ({element}) vs. Business ({tagline_element}): {compatibility}",
                "recommendations": {"colors": number_colors.get(tagline_root, []), "gemstone": number_gemstones.get(tagline_root, "N/A"), "auspicious_day": planet_days.get(tagline_planet, "N/A")}
            }

        if 'founding_date' in data:
            founding_date = data['founding_date']
            date_numerology = calculate_date_numerology(founding_date)
            sun_sign = get_sun_sign(founding_date)
            if date_numerology is not None and sun_sign is not None:
                date_element = get_element_from_number(date_numerology)
                sun_sign_element = get_sun_sign_element(sun_sign)
                numerology_compatibility = get_elemental_compatibility(response["business_tagline"]["element"] if 'business_tagline' in response else element, date_element)
                sun_sign_influence = f"Sun in {sun_sign} ({sun_sign_element}): {sun_sign_insights.get(sun_sign, 'N/A')}"
                response["founding_date"] = {
                    "date": founding_date,
                    "numerology": date_numerology,
                    "element": date_element,
                    "sun_sign": sun_sign,
                    "sun_sign_element": sun_sign_element,
                    "compatibility": f"Founding ({date_element}) vs. Reference ({response['business_tagline']['element'] if 'business_tagline' in response else element}): {numerology_compatibility}",
                    "sun_sign_influence": sun_sign_influence
                }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Lo Shu Grid Numerology
@bp.route('/lahiri/lo_shu_grid_numerology', methods=['POST'])
def lo_shu():
    data = request.get_json()
    birth_date = data.get('birth_date')
    gender = data.get('gender')
    
    if not birth_date or not gender:
        return jsonify({"error": "Missing birth_date or gender"}), 400
    
    if gender.lower() not in ["male", "female"]:
        return jsonify({"error": "Gender must be 'male' or 'female'"}), 400
    
    result = calculate_lo_shu_grid(birth_date, gender)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

# Vimshottari Mahadasha and Antardashas


@bp.route('/lahiri/calculate_antar_dasha', methods=['POST'])
def calculate_vimshottari_antar_dasha():
    """
    Calculate Vimshottari Mahadasha and Antardashas based on birth details.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Mahadasha and Antardasha details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Step 1: Convert birth date and time to Julian Day in UT
        jd_birth = get_julian_dasha_day(birth_date, birth_time, tz_offset)

        # Step 2: Calculate Moon's sidereal position with Lahiri Ayanamsa
        moon_longitude = calculate_moon_sidereal_antar_position(jd_birth)

        # Step 3: Determine Nakshatra and ruling planet
        nakshatra, lord, nakshatra_start = get_nakshatra_and_antar_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        # Step 4: Calculate remaining Mahadasha time and elapsed time
        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_antar_balance(moon_longitude, nakshatra_start, lord)

        # Step 5: Calculate Mahadasha periods with Antardashas
        mahadasha_periods = calculate_mahadasha_periods(birth_date, remaining_time, lord, elapsed_time)

        # Step 6: Construct response
        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# # Vimshottari Antardasha and Pratyantardashas
@bp.route('/lahiri/calculate_maha_antar_pratyantar_dasha', methods=['POST'])
def calculate_vimshottari_pratyantar_dasha():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd_birth = get_julian_pratyathar_day(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_praty_sidereal_position(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_party_and_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_pratythar_dasha_balance(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_Pratythardasha_periods(jd_birth, remaining_time, lord, elapsed_time)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": moon_longitude,
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# # Vimshottari Pratyantardasha and Sookshma Dasha

@bp.route('/lahiri/calculate_antar_pratyantar_sookshma_dasha', methods=['POST'])
def calculate_vimshottari_sookshma_dasha():
    """
    Calculate Vimshottari Dasha periods including Sookshma Dashas.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Mahadasha, Antardasha, Pratyantardasha, and Sookshma Dasha details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd_birth = get_julian_sookshma_day(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sookshma_sidereal_position(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_sookshma(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_sookshma_dasha_balance(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_sookshma_dasha_periods(birth_date, remaining_time, lord, elapsed_time)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# # Vimshottari Sookshma Dasha and Prana Dasha :

@bp.route('/lahiri/calculate_sookshma_prana_dashas', methods=['POST'])
def calculate_vimshottari_dasha():
    """API endpoint to calculate Vimshottari Dasha."""
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day for birth
        jd_birth = get_julian_day_pran(birth_date, birth_time, tz_offset)
        
        # Calculate Moon's sidereal position
        moon_longitude = calculate_moon_sidereal_position_prana(jd_birth)
        
        # Determine Nakshatra and lord
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_prana(moon_longitude)
        
        # Calculate dasha balance
        remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_pran(moon_longitude, nakshatra_start, lord)
        
        # Calculate all Mahadasha periods
        mahadasha_periods = calculate_pranaDasha_periods(jd_birth, lord, elapsed_days)

        response = {
            "user_name": data.get('user_name', 'Unknown'),
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Binnashtakavarga

@bp.route('/lahiri/calculate_binnatakvarga', methods=['POST'])
def calculate_lahiri_binnashtakvarga():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Call the calculation function
        results = lahiri_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct JSON response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": results["planetary_positions"],
            "ascendant": results["ascendant"],
            "ashtakvarga": results["ashtakvarga"],
            "notes": results["notes"]
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Sarvathakavargha 
@bp.route('/lahiri/calculate_sarvashtakavarga', methods=['POST'])
def calculate_sarvashtakavarga_endpoint():
    """API endpoint to calculate Sarvashtakvarga with matrix table based on birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Call the calculation function
        results = lahiri_sarvathakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct JSON response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": results["planetary_positions"],
            "ascendant": results["ascendant"],
            "bhinnashtakavarga": results["bhinnashtakavarga"],
            "sarvashtakavarga": results["sarvashtakavarga"],
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{results['ayanamsa']:.6f}",
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            },
            "debug": {
                "julian_day": results["julian_day"],
                "ayanamsa": f"{results['ayanamsa']:.6f}"
            }
        }
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




#  Shodamsha Vargha sumary Sings.
@bp.route('/lahiri/shodasha_varga_summary', methods=['POST'])
def shodasha_varga_summary():
    try:
        data = request.get_json()
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        utc_dt = lahiri_sign_local_to_utc(birth_date, birth_time, timezone_offset)
        jd = lahiri_sign_julian_day(utc_dt)

        sid_positions = lahiri_sign_get_sidereal_positions(jd)
        sid_asc, asc_sign_idx, asc_deg_in_sign = lahiri_sign_get_sidereal_asc(jd, latitude, longitude)
        sid_positions['Ascendant'] = (sid_asc, asc_sign_idx, asc_deg_in_sign)

        summary = {}
        for pname in list(sid_positions.keys()):
            summary[pname] = {}

        for chart, _ in DCHARTS:
            for pname, (lon, sign_idx, deg_in_sign) in sid_positions.items():
                sign_result = lahiri_sign_varga_sign(
                    pname,
                    deg_in_sign,
                    sign_idx,
                    chart,
                    asc=(pname == "Ascendant")
                )
                summary[pname][chart] = SIGNS[sign_result]

        return jsonify({
            "user_name": user_name,
            "shodasha_varga_summary": summary
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

