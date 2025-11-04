from asyncio.log import logger
from flask import Blueprint, json, make_response, request, jsonify
from datetime import datetime, timedelta
import logging
# from venv import logger
import swisseph as swe

from astro_engine.engine.dashas.DashaOneThreeYears import calculate_complete_dasha_report_one_year, filter_dasha_report_by_date_range_one_year
from astro_engine.engine.dashas.DashaReportOne import  calculate_dasha_balance_daily_report, calculate_mahadasha_periods_daily_report,  calculate_moon_sidereal_position_daily_report,  date_str_to_jd_daily_report,  find_dasha_levels_at_date_daily_report,  get_julian_day_daily_report,   get_nakshatra_and_lord_daily_report
from astro_engine.engine.dashas.DashaThreeSixReport import calculate_dasha_balance_three_months, calculate_mahadasha_periods_three_months, calculate_moon_sidereal_position_three_months, filter_mahadashas_three_months, get_julian_day_three_months, get_nakshatra_and_lord_three_months
from astro_engine.engine.doshas.AgarakDosha import calculate_ascendant, calculate_chart_data
from astro_engine.engine.doshas.GuruChandalDosha import analyze_guru_chandal_dosha, calculate_chart
from astro_engine.engine.doshas.SadiSatiDosha import ZODIAC_SIGNS, analyze_cancellation_factors, analyze_moon_strength, analyze_saturn_status, calculate_all_planets, calculate_dhaiya, calculate_houses_whole_sign, calculate_intensity, calculate_julian_day, calculate_sade_sati_status, get_ayanamsa, get_intensity_interpretation, get_personalized_recommendations, get_planet_house
from astro_engine.engine.doshas.ShariptaDosha import ShrapitDoshaAnalyzer, VedicChart
from astro_engine.engine.yogas.BudhaAdhityaYoga import YogaCombinationAnalyzer, analyze_budha_aditya_yoga_with_combinations, calculate_planetary_positions_budha_aditya
from astro_engine.engine.yogas.ChandraMangalYoga import analyze_chandra_mangal_yoga_formation, analyze_individual_planet_permutation, calculate_planetary_positions_chandra_mangal, calculate_yoga_strength, generate_comprehensive_analysis, get_classical_dignity
from astro_engine.engine.yogas.GajakasariYoga import calculate_comprehensive_gaja_kesari_yoga, calculate_planetary_positions
from astro_engine.engine.yogas.GuruMangalYoga import calculate_comprehensive_guru_mangal_yoga, calculate_planetary_positions_guru_mangal



swe.set_ephe_path('astro_engine/ephe')


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
    from ...schemas import validate_schema  # Phase 2, Module 2.2
    from ...schemas.birth_data import BirthDataSchema  # Phase 2, Module 2.2
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

    # Fallback for validation decorator
    def validate_schema(schema_class):
        def decorator(func):
            return func
        return decorator

    BirthDataSchema = None

bp = Blueprint('bp_routes', __name__)

# Natal Chart
@bp.route('/lahiri/natal', methods=['POST'])
@validate_schema(BirthDataSchema)  # Phase 2, Module 2.2: Input validation FIRST
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

        # Phase 2, Module 2.2: Get validated data from request context
        # Data is already validated by @validate_schema decorator
        birth_data = request.validated_data.to_dict() if hasattr(request, 'validated_data') else request.get_json()

        # Legacy validation (kept for backward compatibility / fallback)
        # This code will not execute if validate_schema decorator worked
        # But provides safety net if decorator is disabled
        if not hasattr(request, 'validated_data'):
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
        else:
            # Data already validated - just extract for logging
            latitude = birth_data['latitude']
            longitude = birth_data['longitude']

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


#  Hora (D-2)
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
            "planetary_positions": natal_positions
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


# **********************************************************************************************************
#           Vimshottari Mahadasha and Antardashas
# **********************************************************************************************************


@bp.route('/lahiri/calculate_antar_dasha', methods=['POST'])
def calculate_vimshottari_antar_dasha():
    """
    Calculate Vimshottari Mahadasha and Antardashas based on birth details.
    Expected JSON Input:
    {
        "user_name": "user name",
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


#  Dasha reports wise dates segregation 

# @bp.route('/dasha_for_day', methods=['POST'])
# def dasha_for_day():
#     """API endpoint to get dasha sequence for previous day and current day."""
#     try:
#         data = request.get_json()
#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not data or not all(field in data for field in required_fields):
#             return create_json_response({"error": "Missing required fields"}, 400)

#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         tz_offset = float(data['timezone_offset'])
        
#         # Get target date (default to current date if not provided)
#         target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
#         target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        
#         # Calculate previous day
#         previous_date = target_date - timedelta(days=1)

#         # Get complete dasha calculation
#         dasha_data = get_complete_vimshottari_dasha(birth_date, birth_time, tz_offset)
        
#         # Get dasha for previous day
#         previous_jd = date_str_to_jd(previous_date.strftime('%Y-%m-%d'))
#         previous_day_dashas = find_dasha_levels_at_date(dasha_data['mahadasha_periods'], previous_jd)
        
#         # Get dasha for current day
#         current_jd = date_str_to_jd(target_date.strftime('%Y-%m-%d'))
#         current_day_dashas = find_dasha_levels_at_date(dasha_data['mahadasha_periods'], current_jd)

#         # Build previous_day dict
#         previous_day = [
#             ('date', previous_date.strftime('%Y-%m-%d')),
#             ('dasha_sequence', previous_day_dashas['dasha_sequence'] if previous_day_dashas else None),
#             ('levels', dict(previous_day_dashas['levels']) if previous_day_dashas else None)
#         ]
        
#         # Build current_day dict
#         current_day = [
#             ('date', target_date.strftime('%Y-%m-%d')),
#             ('dasha_sequence', current_day_dashas['dasha_sequence'] if current_day_dashas else None),
#             ('levels', dict(current_day_dashas['levels']) if current_day_dashas else None)
#         ]
        
#         # Build response in exact order
#         response = [
#             ('user_name', data.get('user_name', 'Unknown')),
#             ('birth_date', birth_date),
#             ('birth_time', birth_time),
#             ('nakshatra_at_birth', dasha_data['nakshatra']),
#             ('moon_longitude', dasha_data['moon_longitude']),
#             ('previous_day', dict(previous_day)),
#             ('current_day', dict(current_day))
#         ]
        
#         return create_json_response(dict(response), 200)
#     except Exception as e:
#         return create_json_response({"error": str(e)}, 500)


# @bp.route('/dasha_for_week', methods=['POST'])
# def dasha_for_week():
#     """API endpoint to get dasha sequence for current week (7 days)."""
#     try:
#         data = request.get_json()
#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not data or not all(field in data for field in required_fields):
#             return create_json_response({"error": "Missing required fields"}, 400)

#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         tz_offset = float(data['timezone_offset'])
        
#         # Get target date (default to current date if not provided)
#         target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
#         target_date = datetime.strptime(target_date_str, '%Y-%m-%d')

#         # Get complete dasha calculation
#         dasha_data = get_complete_vimshottari_dasha(birth_date, birth_time, tz_offset)
        
#         # Get dasha for each day of the week
#         week_dashas = []
#         for i in range(7):
#             day_date = target_date + timedelta(days=i)
#             day_jd = date_str_to_jd(day_date.strftime('%Y-%m-%d'))
#             day_dasha_info = find_dasha_levels_at_date(dasha_data['mahadasha_periods'], day_jd)
            
#             day_data = [
#                 ('date', day_date.strftime('%Y-%m-%d')),
#                 ('day_name', day_date.strftime('%A')),
#                 ('dasha_sequence', day_dasha_info['dasha_sequence'] if day_dasha_info else None),
#                 ('levels', dict(day_dasha_info['levels']) if day_dasha_info else None)
#             ]
            
#             week_dashas.append(dict(day_data))

#         # Build response in exact order
#         response = [
#             ('user_name', data.get('user_name', 'Unknown')),
#             ('birth_date', birth_date),
#             ('birth_time', birth_time),
#             ('nakshatra_at_birth', dasha_data['nakshatra']),
#             ('moon_longitude', dasha_data['moon_longitude']),
#             ('week_start_date', target_date.strftime('%Y-%m-%d')),
#             ('week_end_date', (target_date + timedelta(days=6)).strftime('%Y-%m-%d')),
#             ('total_days', 7),
#             ('week_dashas', week_dashas)
#         ]
        
#         return create_json_response(dict(response), 200)
#     except Exception as e:
#         return create_json_response({"error": str(e)}, 500)


# @bp.route('/dasha_for_month', methods=['POST'])
# def dasha_for_month():
#     """API endpoint to get dasha sequence for current month (30 days)."""
#     try:
#         data = request.get_json()
#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not data or not all(field in data for field in required_fields):
#             return create_json_response({"error": "Missing required fields"}, 400)

#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         tz_offset = float(data['timezone_offset'])
        
#         # Get target date (default to current date if not provided)
#         target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
#         target_date = datetime.strptime(target_date_str, '%Y-%m-%d')

#         # Get complete dasha calculation
#         dasha_data = get_complete_vimshottari_dasha(birth_date, birth_time, tz_offset)
        
#         # Get dasha for each day of the month (30 days)
#         month_dashas = []
#         for i in range(30):
#             day_date = target_date + timedelta(days=i)
#             day_jd = date_str_to_jd(day_date.strftime('%Y-%m-%d'))
#             day_dasha_info = find_dasha_levels_at_date(dasha_data['mahadasha_periods'], day_jd)
            
#             day_data = [
#                 ('date', day_date.strftime('%Y-%m-%d')),
#                 ('day_name', day_date.strftime('%A')),
#                 ('dasha_sequence', day_dasha_info['dasha_sequence'] if day_dasha_info else None),
#                 ('levels', dict(day_dasha_info['levels']) if day_dasha_info else None)
#             ]
            
#             month_dashas.append(dict(day_data))

#         # Build response in exact order
#         response = [
#             ('user_name', data.get('user_name', 'Unknown')),
#             ('birth_date', birth_date),
#             ('birth_time', birth_time),
#             ('nakshatra_at_birth', dasha_data['nakshatra']),
#             ('moon_longitude', dasha_data['moon_longitude']),
#             ('month_start_date', target_date.strftime('%Y-%m-%d')),
#             ('month_end_date', (target_date + timedelta(days=29)).strftime('%Y-%m-%d')),
#             ('total_days', 30),
#             ('month_dashas', month_dashas)
#         ]
        
#         return create_json_response(dict(response), 200)
#     except Exception as e:
#         return create_json_response({"error": str(e)}, 500)


def create_json_response(data, status_code=200):
    """Create JSON response with preserved key order."""
    response = make_response(json.dumps(data, ensure_ascii=False, indent=4))
    response.headers['Content-Type'] = 'application/json'
    return response, status_code

@bp.route('/lahiri/dasha_for_day', methods=['POST'])
def dasha_for_day():
    """API endpoint to get dasha sequence for previous day and current day."""
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(field in data for field in required_fields):
            return create_json_response({"error": "Missing required fields"}, 400)

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        tz_offset = float(data['timezone_offset'])
        
        # Get target date (default to current date if not provided)
        target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        
        # Calculate previous day
        previous_date = target_date - timedelta(days=1)

        # Calculate Julian Day for birth
        jd_birth = get_julian_day_daily_report(birth_date, birth_time, tz_offset)
        
        # Calculate Moon's sidereal position
        moon_longitude = calculate_moon_sidereal_position_daily_report(jd_birth)
        
        # Determine Nakshatra and lord
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_daily_report(moon_longitude)
        
        # Calculate dasha balance
        remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_daily_report(moon_longitude, nakshatra_start, lord)
        
        # Calculate all Mahadasha periods
        mahadasha_periods = calculate_mahadasha_periods_daily_report(jd_birth, lord, elapsed_days)
        
        # Get dasha for previous day
        previous_jd = date_str_to_jd_daily_report(previous_date.strftime('%Y-%m-%d'))
        previous_day_dashas = find_dasha_levels_at_date_daily_report(mahadasha_periods, previous_jd)
        
        # Get dasha for current day
        current_jd = date_str_to_jd_daily_report(target_date.strftime('%Y-%m-%d'))
        current_day_dashas = find_dasha_levels_at_date_daily_report(mahadasha_periods, current_jd)

        # Build previous_day dict
        previous_day = [
            ('date', previous_date.strftime('%Y-%m-%d')),
            ('dasha_sequence', previous_day_dashas['dasha_sequence'] if previous_day_dashas else None),
            ('levels', dict(previous_day_dashas['levels']) if previous_day_dashas else None)
        ]
        
        # Build current_day dict
        current_day = [
            ('date', target_date.strftime('%Y-%m-%d')),
            ('dasha_sequence', current_day_dashas['dasha_sequence'] if current_day_dashas else None),
            ('levels', dict(current_day_dashas['levels']) if current_day_dashas else None)
        ]
        
        # Build response in exact order
        response = [
            ('user_name', data.get('user_name', 'Unknown')),
            ('birth_date', birth_date),
            ('birth_time', birth_time),
            ('nakshatra_at_birth', nakshatra),
            ('moon_longitude', round(moon_longitude, 4)),
            ('previous_day', dict(previous_day)),
            ('current_day', dict(current_day))
        ]
        
        return create_json_response(dict(response), 200)
    except Exception as e:
        return create_json_response({"error": str(e)}, 500)

@bp.route('/lahiri/dasha_for_week', methods=['POST'])
def dasha_for_week():
    """API endpoint to get dasha sequence for current week (7 days)."""
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(field in data for field in required_fields):
            return create_json_response({"error": "Missing required fields"}, 400)

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        tz_offset = float(data['timezone_offset'])
        
        # Get target date (default to current date if not provided)
        target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')

        # Calculate Julian Day for birth
        jd_birth = get_julian_day_daily_report(birth_date, birth_time, tz_offset)
        
        # Calculate Moon's sidereal position
        moon_longitude = calculate_moon_sidereal_position_daily_report(jd_birth)
        
        # Determine Nakshatra and lord
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_daily_report(moon_longitude)
        
        # Calculate dasha balance
        remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_daily_report(moon_longitude, nakshatra_start, lord)
        
        # Calculate all Mahadasha periods
        mahadasha_periods = calculate_mahadasha_periods_daily_report(jd_birth, lord, elapsed_days)
        
        # Get dasha for each day of the week
        week_dashas = []
        for i in range(7):
            day_date = target_date + timedelta(days=i)
            day_jd = date_str_to_jd_daily_report(day_date.strftime('%Y-%m-%d'))
            day_dasha_info = find_dasha_levels_at_date_daily_report(mahadasha_periods, day_jd)
            
            day_data = [
                ('date', day_date.strftime('%Y-%m-%d')),
                ('day_name', day_date.strftime('%A')),
                ('dasha_sequence', day_dasha_info['dasha_sequence'] if day_dasha_info else None),
                ('levels', dict(day_dasha_info['levels']) if day_dasha_info else None)
            ]
            
            week_dashas.append(dict(day_data))

        response = [
            ('user_name', data.get('user_name', 'Unknown')),
            ('birth_date', birth_date),
            ('birth_time', birth_time),
            ('nakshatra_at_birth', nakshatra),
            ('moon_longitude', round(moon_longitude, 4)),
            ('week_start_date', target_date.strftime('%Y-%m-%d')),
            ('week_end_date', (target_date + timedelta(days=6)).strftime('%Y-%m-%d')),
            ('total_days', 7),
            ('week_dashas', week_dashas)
        ]
        
        return create_json_response(dict(response), 200)
    except Exception as e:
        return create_json_response({"error": str(e)}, 500)

@bp.route('/lahiri/dasha_for_month', methods=['POST'])
def dasha_for_month():
    """API endpoint to get dasha sequence for current month (30 days)."""
    try:
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(field in data for field in required_fields):
            return create_json_response({"error": "Missing required fields"}, 400)

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        tz_offset = float(data['timezone_offset'])
        
        # Get target date (default to current date if not provided)
        target_date_str = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')

        # Calculate Julian Day for birth
        jd_birth = get_julian_day_daily_report(birth_date, birth_time, tz_offset)
        
        # Calculate Moon's sidereal position
        moon_longitude = calculate_moon_sidereal_position_daily_report(jd_birth)
        
        # Determine Nakshatra and lord
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_daily_report(moon_longitude)
        
        # Calculate dasha balance
        remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_daily_report(moon_longitude, nakshatra_start, lord)
        
        # Calculate all Mahadasha periods
        mahadasha_periods = calculate_mahadasha_periods_daily_report(jd_birth, lord, elapsed_days)
        
        # Get dasha for each day of the month (30 days)
        month_dashas = []
        for i in range(30):
            day_date = target_date + timedelta(days=i)
            day_jd = date_str_to_jd_daily_report(day_date.strftime('%Y-%m-%d'))
            day_dasha_info = find_dasha_levels_at_date_daily_report(mahadasha_periods, day_jd)
            
            day_data = [
                ('date', day_date.strftime('%Y-%m-%d')),
                ('day_name', day_date.strftime('%A')),
                ('dasha_sequence', day_dasha_info['dasha_sequence'] if day_dasha_info else None),
                ('levels', dict(day_dasha_info['levels']) if day_dasha_info else None)
            ]
            
            month_dashas.append(dict(day_data))

        response = [
            ('user_name', data.get('user_name', 'Unknown')),
            ('birth_date', birth_date),
            ('birth_time', birth_time),
            ('nakshatra_at_birth', nakshatra),
            ('moon_longitude', round(moon_longitude, 4)),
            ('month_start_date', target_date.strftime('%Y-%m-%d')),
            ('month_end_date', (target_date + timedelta(days=29)).strftime('%Y-%m-%d')),
            ('total_days', 30),
            ('month_dashas', month_dashas)
        ]
        
        return create_json_response(dict(response), 200)
    except Exception as e:
        return create_json_response({"error": str(e)}, 500)


#  Dasha dates of three months and six months

@bp.route('/lahiri/calculate_vimshottari_dasha_3months', methods=['POST'])
def calculate_vimshottari_dasha_3months():
    """
    Calculate Vimshottari Dasha periods for the next 3 months from current date.
    
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
        JSON response with filtered Mahadasha, Antardasha, Pratyantardasha, and Sookshma Dasha details
        for the next 3 months from today.
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

        # Calculate full dasha periods
        jd_birth = get_julian_day_three_months(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_position_three_months(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_three_months(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance_three_months(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_mahadasha_periods_three_months(birth_date, remaining_time, lord, elapsed_time)

        # Filter for 3 months from current date
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = current_date + timedelta(days=90)  # 3 months = 90 days
        
        filtered_mahadashas = filter_mahadashas_three_months(mahadasha_periods, current_date, end_date)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "filter_period": "3_months",
            "filter_start_date": current_date.strftime("%Y-%m-%d"),
            "filter_end_date": end_date.strftime("%Y-%m-%d"),
            "mahadashas": filtered_mahadashas
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


@bp.route('/lahiri/calculate_vimshottari_dasha_6months', methods=['POST'])
def calculate_vimshottari_dasha_6months():
    """
    Calculate Vimshottari Dasha periods for the next 6 months from current date.
    
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
        JSON response with filtered Mahadasha, Antardasha, Pratyantardasha, and Sookshma Dasha details
        for the next 6 months from today.
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

        # Calculate full dasha periods
        jd_birth = get_julian_day_three_months(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_position_three_months(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_three_months(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance_three_months(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_mahadasha_periods_three_months(birth_date, remaining_time, lord, elapsed_time)

        # Filter for 6 months from current date
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = current_date + timedelta(days=180)  # 6 months = 180 days
        
        filtered_mahadashas = filter_mahadashas_three_months(mahadasha_periods, current_date, end_date)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "filter_period": "6_months",
            "filter_start_date": current_date.strftime("%Y-%m-%d"),
            "filter_end_date": end_date.strftime("%Y-%m-%d"),
            "mahadashas": filtered_mahadashas
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



#   Dasha dates of one year, two years & three years

@bp.route('/lahiri/dasha_report_1year', methods=['POST'])
def dasha_report_1year():
    """Calculate Vimshottari Dasha report for 1 year from current date."""
    try:
        # Parse and validate input JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate complete dasha report
        mahadasha_timeline = calculate_complete_dasha_report_one_year(
            birth_date, birth_time, latitude, longitude, tz_offset, user_name
        )

        # Filter for 1 year from current date
        current_date = datetime.now()
        end_date = current_date + timedelta(days=365)
        
        filtered_timeline = filter_dasha_report_by_date_range_one_year(
            mahadasha_timeline, current_date, end_date
        )

        # Construct response
        response = {
            'user_name': user_name,
            'mahadashas': filtered_timeline,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'report_type': '1_year',
                'report_start_date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'report_end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                'input': data
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


@bp.route('/lahiri/dasha_report_2years', methods=['POST'])
def dasha_report_2years():
    """Calculate Vimshottari Dasha report for 2 years from current date."""
    try:
        # Parse and validate input JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate complete dasha report
        mahadasha_timeline = calculate_complete_dasha_report_one_year(
            birth_date, birth_time, latitude, longitude, tz_offset, user_name
        )

        # Filter for 2 years from current date
        current_date = datetime.now()
        end_date = current_date + timedelta(days=730)  # 2 years
        
        filtered_timeline = filter_dasha_report_by_date_range_one_year(
            mahadasha_timeline, current_date, end_date
        )

        # Construct response
        response = {
            'user_name': user_name,
            'mahadashas': filtered_timeline,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'report_type': '2_years',
                'report_start_date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'report_end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                'input': data
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


@bp.route('/lahiri/dasha_report_3years', methods=['POST'])
def dasha_report_3years():
    """Calculate Vimshottari Dasha report for 3 years from current date."""
    try:
        # Parse and validate input JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate complete dasha report
        mahadasha_timeline = calculate_complete_dasha_report_one_year(
            birth_date, birth_time, latitude, longitude, tz_offset, user_name
        )

        # Filter for 3 years from current date
        current_date = datetime.now()
        end_date = current_date + timedelta(days=1095)  # 3 years
        
        filtered_timeline = filter_dasha_report_by_date_range_one_year(
            mahadasha_timeline, current_date, end_date
        )

        # Construct response
        response = {
            'user_name': user_name,
            'mahadashas': filtered_timeline,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'report_type': '3_years',
                'report_start_date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'report_end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                'input': data
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


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






# *********************************************************************************************************************
# ***********************************       Yogas        ***********************************************
# *********************************************************************************************************************



#  Gaja Kasari Yoga
@bp.route('/lahiri/comprehensive_gaja_kesari', methods=['POST'])
def comprehensive_gaja_kesari_analysis():
    """COMPLETELY CORRECTED: Comprehensive Gaja Kesari Yoga analysis with perfect calculations."""
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate planetary positions using the calculations module
        planet_positions, ascendant_sign, ascendant_lon, ayanamsa_value = calculate_planetary_positions(birth_data)

        # CORRECTED: Comprehensive Gaja Kesari analysis with accurate calculations
        comprehensive_analysis = calculate_comprehensive_gaja_kesari_yoga(planet_positions, ascendant_sign)

        # Parse birth time for response
        birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()

        # Prepare response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_time.strftime('%H:%M:%S'),
                "latitude": float(birth_data['latitude']),
                "longitude": float(birth_data['longitude']),
                "timezone_offset": float(birth_data['timezone_offset']),
                "ascendant": {
                    "sign": ascendant_sign,
                    "degrees": format_dms(ascendant_lon % 30)
                }
            },
            "comprehensive_gaja_kesari_analysis": comprehensive_analysis,
            "all_planetary_positions": {
                planet: {
                    "sign": data['sign'],
                    "house": data['house'],
                    "degrees": data['degrees'],
                    "retrograde": data['retrograde']
                } for planet, data in planet_positions.items()
            },
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}°",
                "house_system": "Whole Sign",
                "chart_type": "Sidereal (Vedic)",
                "analysis_type": "Perfectly Corrected Analysis",
                "critical_fixes": [
                    "Fixed malefic conjunction detection (Saturn with both Jupiter and Moon)",
                    "Corrected malefic penalty calculation for triple conjunction",
                    "Enhanced yoga strength classification for debilitated planets",
                    "Improved ascendant-specific interpretations",
                    "Added comprehensive remedial measures"
                ]
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Guru Mangal Yoga
@bp.route('/lahiri/comprehensive_guru_mangal', methods=['POST'])
def guru_mangal_yoga():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate planetary positions using the calculations module
        planetary_positions_json, ascendant_json, house_signs_json, asc_sign, ayanamsa_value = calculate_planetary_positions_guru_mangal(birth_data)

        # Comprehensive Guru Mangal Yoga analysis
        jupiter_data = planetary_positions_json['Jupiter']
        mars_data = planetary_positions_json['Mars']
        guru_mangal_analysis = calculate_comprehensive_guru_mangal_yoga(
            jupiter_data, mars_data, asc_sign, planetary_positions_json
        )

        # Parse birth time for response
        birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()

        # Prepare response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_time.strftime('%H:%M:%S'),
                "latitude": float(birth_data['latitude']),
                "longitude": float(birth_data['longitude']),
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": ascendant_json,
            "house_signs": house_signs_json,
            "guru_mangal_yoga_comprehensive": guru_mangal_analysis,
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@bp.route('/lahiri/guru-mangal-only', methods=['POST'])
def guru_mangal_yoga_only():
    """Get only Guru Mangal Yoga analysis without full chart details"""
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate planetary positions
        planetary_positions_json, _, _, asc_sign, _ = calculate_planetary_positions_guru_mangal(birth_data)

        # Guru Mangal Yoga analysis only
        jupiter_data = planetary_positions_json['Jupiter']
        mars_data = planetary_positions_json['Mars']
        guru_mangal_analysis = calculate_comprehensive_guru_mangal_yoga(
            jupiter_data, mars_data, asc_sign, planetary_positions_json
        )

        response = {
            "ascendant_sign": asc_sign,
            "jupiter_details": {
                "sign": jupiter_data['sign'],
                "house": jupiter_data['house'],
                "degrees": jupiter_data['degrees']
            },
            "mars_details": {
                "sign": mars_data['sign'], 
                "house": mars_data['house'],
                "degrees": mars_data['degrees']
            },
            "guru_mangal_yoga_analysis": guru_mangal_analysis
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  Budha Aditya Yoga 
@bp.route('/lahiri/budha-aditya-yoga', methods=['POST'])
def budha_aditya_yoga():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate planetary positions using the calculations module
        sun_data, mercury_data, ascendant_data, ayanamsa_value = calculate_planetary_positions_budha_aditya(birth_data)

        # Initialize combination analyzer
        analyzer = YogaCombinationAnalyzer()
        
        # Analyze Budha Aditya Yoga with mathematical precision
        yoga_analysis = analyze_budha_aditya_yoga_with_combinations(sun_data, mercury_data, analyzer)

        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": float(birth_data['latitude']),
                "longitude": float(birth_data['longitude']),
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "planetary_positions": {
                "Sun": sun_data,
                "Mercury": mercury_data
            },
            "ascendant": ascendant_data,
            "budha_aditya_yoga_analysis": yoga_analysis,
            "mathematical_framework": {
                "combination_principle": "C(n,r) = n!/[r!(n-r)!] - Order doesn't matter for basic formation",
                "permutation_principle": "P(n,r) = n!/(n-r)! - Order matters for strength analysis",
                "application": "Yoga formation uses combinations, strength analysis uses permutations"
            },
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "house_system": "Whole Sign",
                "combustion_limit": "8.5 degrees",
                "mathematical_precision": "Applied exact permutation and combination rules"
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# @bp.route('/budha-aditya-quick', methods=['POST'])
# def budha_aditya_quick_check():
#     """Quick check for Budha Aditya Yoga presence without detailed analysis"""
#     try:
#         birth_data = request.get_json()
#         if not birth_data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in birth_data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         # Calculate planetary positions
#         sun_data, mercury_data, ascendant_data, _ = calculate_planetary_positions_budha_aditya(birth_data)

#         # Quick check for yoga presence
#         yoga_present = sun_data['sign'] == mercury_data['sign']
        
#         from budha_aditya_calculations import calculate_separation
#         separation = calculate_separation(sun_data['longitude'], mercury_data['longitude'])
#         is_combust = separation <= 8.5

#         response = {
#             "yoga_present": yoga_present,
#             "sun_sign": sun_data['sign'],
#             "mercury_sign": mercury_data['sign'],
#             "same_sign": yoga_present,
#             "sun_house": sun_data['house'],
#             "mercury_house": mercury_data['house'],
#             "separation_degrees": round(separation, 2),
#             "mercury_combust": is_combust,
#             "ascendant_sign": ascendant_data['sign'],
#             "quick_assessment": "Yoga present but Mercury combust" if yoga_present and is_combust else
#                               "Yoga present and Mercury not combust" if yoga_present and not is_combust else
#                               "Yoga not present"
#         }

#         return jsonify(response)

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# @app.route('/combustion-analysis', methods=['POST'])
# def combustion_analysis_only():
#     """Detailed combustion analysis between Sun and Mercury"""
#     try:
#         birth_data = request.get_json()
#         if not birth_data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in birth_data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         # Calculate planetary positions
#         sun_data, mercury_data, _, _ = calculate_planetary_positions_budha_aditya(birth_data)

#         from budha_aditya_calculations import analyze_combustion_permutations
        
#         # Detailed combustion analysis
#         combustion_analysis = analyze_combustion_permutations(
#             sun_data['longitude'], 
#             mercury_data['longitude']
#         )

#         response = {
#             "sun_position": {
#                 "sign": sun_data['sign'],
#                 "degrees": sun_data['degrees'],
#                 "longitude": sun_data['longitude']
#             },
#             "mercury_position": {
#                 "sign": mercury_data['sign'],
#                 "degrees": mercury_data['degrees'],
#                 "longitude": mercury_data['longitude'],
#                 "retrograde": mercury_data['retrograde']
#             },
#             "combustion_analysis": combustion_analysis,
#             "interpretation": {
#                 "effect_on_mercury": f"Mercury's strength reduced by {combustion_analysis['strength_reduction_percent']}%" if combustion_analysis['is_combust'] else "Mercury retains full strength",
#                 "communication_impact": "Impaired communication and analytical abilities" if combustion_analysis['is_combust'] else "Clear communication and sharp intellect",
#                 "remedial_suggestion": "Perform Mercury remedies on Wednesdays" if combustion_analysis['is_combust'] else "No special remedies needed for combustion"
#             }
#         }

#         return jsonify(response)

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Chandra Mangala Yoga


@bp.route('/lahiri/chandra-mangal-yoga', methods=['POST'])
def chandra_mangal_yoga():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate planetary positions using the calculations module
        planetary_positions_json, asc_sign, ascendant_lon, ayanamsa_value = calculate_planetary_positions_chandra_mangal(birth_data)

        # COMPLETE PERMUTATION & COMBINATION ANALYSIS
        # Step 1: Analyze individual planet permutations (regardless of yoga presence)
        moon_lon = planetary_positions_json['Moon']['longitude']
        mars_lon = planetary_positions_json['Mars']['longitude']
        moon_house = planetary_positions_json['Moon']['house']
        mars_house = planetary_positions_json['Mars']['house']
        
        moon_analysis = analyze_individual_planet_permutation('Moon', moon_lon, moon_house, planetary_positions_json)
        mars_analysis = analyze_individual_planet_permutation('Mars', mars_lon, mars_house, planetary_positions_json)
        
        # Step 2: Check yoga formation
        formation_analysis = analyze_chandra_mangal_yoga_formation(moon_analysis, mars_analysis)
        
        # Step 3: Calculate strength if yoga is present
        strength_data = None
        if formation_analysis['yoga_present']:
            moon_dignity = get_classical_dignity(moon_lon, 'Moon')
            mars_dignity = get_classical_dignity(mars_lon, 'Mars')
            strength_data = calculate_yoga_strength(moon_lon, mars_lon, moon_dignity, mars_dignity)
        
        # Step 4: Generate comprehensive analysis
        comprehensive_analysis = generate_comprehensive_analysis(
            formation_analysis, moon_analysis, mars_analysis, strength_data
        )

        # Parse birth time for response
        birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()

        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_time.strftime('%H:%M:%S'),
                "latitude": float(birth_data['latitude']),
                "longitude": float(birth_data['longitude']),
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "traditional_permutation_combination_analysis": comprehensive_analysis,
            "planetary_positions": {
                "Moon": planetary_positions_json["Moon"],
                "Mars": planetary_positions_json["Mars"]
            },
            "all_planetary_positions": planetary_positions_json,
            "ascendant": {
                "sign": asc_sign,
                "degrees": format_dms(ascendant_lon % 30)
            },
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "house_system": "Whole Sign",
                "analysis_methodology": "Complete Traditional Permutation & Combination Analysis",
                "combinations_analyzed": "144 per planet (12 signs × 12 houses)",
                "classical_rules_applied": [
                    "Brihat Parashara Hora Shastra formation rules",
                    "Traditional 3-state dignity system (Own/Exalted/Debilitated)",
                    "Classical angular separation classifications",
                    "Authentic house and sign significations",
                    "Traditional strength calculation (40% separation + 30% Moon + 30% Mars)"
                ],
                "sidereal_zodiac": True,
                "comprehensive_scope": "Analysis provided regardless of yoga presence - individual permutations always calculated"
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# @app.route('/chandra-mangal-only', methods=['POST'])
# def chandra_mangal_yoga_only():
#     """Get only Chandra Mangal Yoga analysis without full planetary positions"""
#     try:
#         birth_data = request.get_json()
#         if not birth_data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in birth_data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         # Calculate planetary positions
#         planetary_positions_json, asc_sign, _, _ = calculate_planetary_positions_chandra_mangal(birth_data)

#         # Analyze only Moon and Mars
#         moon_lon = planetary_positions_json['Moon']['longitude']
#         mars_lon = planetary_positions_json['Mars']['longitude']
#         moon_house = planetary_positions_json['Moon']['house']
#         mars_house = planetary_positions_json['Mars']['house']
        
#         moon_analysis = analyze_individual_planet_permutation('Moon', moon_lon, moon_house, planetary_positions_json)
#         mars_analysis = analyze_individual_planet_permutation('Mars', mars_lon, mars_house, planetary_positions_json)
        
#         # Check yoga formation
#         formation_analysis = analyze_chandra_mangal_yoga_formation(moon_analysis, mars_analysis)
        
#         # Calculate strength if yoga is present
#         strength_data = None
#         if formation_analysis['yoga_present']:
#             moon_dignity = get_classical_dignity(moon_lon, 'Moon')
#             mars_dignity = get_classical_dignity(mars_lon, 'Mars')
#             strength_data = calculate_yoga_strength(moon_lon, mars_lon, moon_dignity, mars_dignity)
        
#         # Generate comprehensive analysis
#         comprehensive_analysis = generate_comprehensive_analysis(
#             formation_analysis, moon_analysis, mars_analysis, strength_data
#         )

#         response = {
#             "ascendant_sign": asc_sign,
#             "moon_details": {
#                 "sign": planetary_positions_json['Moon']['sign'],
#                 "house": planetary_positions_json['Moon']['house'],
#                 "degrees": planetary_positions_json['Moon']['degrees'],
#                 "dignity": planetary_positions_json['Moon']['dignity']
#             },
#             "mars_details": {
#                 "sign": planetary_positions_json['Mars']['sign'], 
#                 "house": planetary_positions_json['Mars']['house'],
#                 "degrees": planetary_positions_json['Mars']['degrees'],
#                 "dignity": planetary_positions_json['Mars']['dignity']
#             },
#             "chandra_mangal_yoga_analysis": comprehensive_analysis
#         }

#         return jsonify(response)

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# @app.route('/planetary-positions', methods=['POST'])
# def get_planetary_positions_only():
#     """Get basic planetary positions without yoga analysis"""
#     try:
#         birth_data = request.get_json()
#         if not birth_data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in birth_data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         # Calculate planetary positions
#         planetary_positions_json, asc_sign, ascendant_lon, ayanamsa_value = calculate_planetary_positions_chandra_mangal(birth_data)

#         # Parse birth time for response
#         birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()

#         response = {
#             "birth_details": {
#                 "birth_date": birth_data['birth_date'],
#                 "birth_time": birth_time.strftime('%H:%M:%S'),
#                 "latitude": float(birth_data['latitude']),
#                 "longitude": float(birth_data['longitude']),
#                 "timezone_offset": float(birth_data['timezone_offset'])
#             },
#             "planetary_positions": planetary_positions_json,
#             "ascendant": {
#                 "sign": asc_sign,
#                 "degrees": format_dms(ascendant_lon % 30)
#             },
#             "calculation_notes": {
#                 "ayanamsa": "Lahiri",
#                 "ayanamsa_value": f"{ayanamsa_value:.6f}",
#                 "house_system": "Whole Sign",
#                 "dignity_system": "Classical 3-state system (Own/Exalted/Debilitated for Moon & Mars)",
#                 "sidereal_zodiac": True
#             }
#         }

#         return jsonify(response)

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500






# *********************************************************************************************************************
# ***********************************       Doshas        ***********************************************
# *********************************************************************************************************************


#  Agaraka Dosha

@bp.route('/lahiri/calculate-angarak-dosha', methods=['POST'])
def calculate_angarak_dosha():
    """
    Main API endpoint for Angarak Dosha calculation
    """
    try:
        # Get input data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # Calculate chart data using imported function
        chart_data = calculate_chart_data(
            birth_date,
            birth_time,
            latitude,
            longitude,
            timezone_offset
        )
        
        # Prepare response
        response = {
            'user_info': {
                'name': user_name,
                'birth_date': birth_date,
                'birth_time': birth_time,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'timezone_offset': timezone_offset
            },
            'calculation_details': {
                'ayanamsa': 'Lahiri',
                'house_system': 'Whole Sign',
                'zodiac': 'Sidereal',
                'calculation_date': datetime.now().isoformat()
            },
            'ascendant': chart_data['ascendant'],
            'houses': chart_data['houses'],
            'planetary_positions': chart_data['planetary_positions'],
            'angarak_dosha_analysis': chart_data['angarak_dosha_analysis']
        }
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500



#  Guru Chandal Dosha

@bp.route('/lahiri/guru-chandal-analysis', methods=['POST'])
def guru_chandal_analysis():
    """
    Main API endpoint for Guru Chandal Dosha analysis
    
    Expected JSON input:
    {
        "user_name": "Full Name",
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM:SS",
        "latitude": "DD.DDDD",
        "longitude": "DD.DDDD",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with complete dosha analysis
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract input data
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # Calculate complete birth chart
        chart_data = calculate_chart(
            birth_date, 
            birth_time, 
            latitude, 
            longitude, 
            timezone_offset
        )
        
        # Perform Guru Chandal Dosha analysis
        dosha_analysis =analyze_guru_chandal_dosha(
            chart_data['planets'], 
            chart_data['ascendant_longitude']
        )
        
        # Prepare response
        response = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'user_name': user_name,
            'birth_details': {
                'date': birth_date,
                'time': birth_time,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone_offset': timezone_offset
                }
            },
            'calculation_system': {
                'ayanamsa': 'Lahiri',
                'ayanamsa_value': round(chart_data['ayanamsa'], 6),
                'house_system': 'Whole Sign',
                'zodiac': 'Sidereal',
                'julian_day': round(chart_data['julian_day'], 6)
            },
            'ascendant': {
                'longitude': round(chart_data['ascendant_longitude'], 4),
                'sign': chart_data['ascendant_sign'],
                'degree_in_sign': round(chart_data['ascendant_degree'], 4)
            },
            'planets': chart_data['planets'],
            'guru_chandal_dosha_analysis': dosha_analysis
        }
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': 'Invalid input data',
            'message': str(ve)
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500



#  Shaipta Dosha

@bp.route('/lahiri/calculate-shrapit-dosha', methods=['POST'])
def calculate_shrapit_dosha():
    """API endpoint to calculate Shrapit Dosha"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'status': 'error'
                }), 400
        
        # Create Vedic chart
        chart = VedicChart(
            birth_date=data['birth_date'],
            birth_time=data['birth_time'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            timezone_offset=data['timezone_offset']
        )
        
        # Calculate planetary positions
        planets = chart.get_planetary_positions()
        
        # Analyze Shrapit Dosha
        analyzer = ShrapitDoshaAnalyzer(chart)
        dosha_result = analyzer.analyze()
        
        # Prepare response
        response = {
            'status': 'success',
            'user_name': data['user_name'],
            'birth_details': {
                'date': data['birth_date'],
                'time': data['birth_time'],
                'location': {
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'timezone_offset': data['timezone_offset']
                }
            },
            'chart_details': {
                'ayanamsa': 'Lahiri',
                'house_system': 'Whole Sign',
                'zodiac': 'Sidereal (Vedic)'
            },
            'planetary_positions': {
                planet: {
                    'longitude': round(info['longitude'], 4),
                    'sign': info['sign_name'],
                    'degree_in_sign': round(info['degree_in_sign'], 2),
                    'house': info['house']
                }
                for planet, info in planets.items()
            },
            'shrapit_dosha_analysis': dosha_result
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500  
    



#  Sadi Sati dosha

@bp.route('/lahiri/calculate-sade-sati', methods=['POST'])
def calculate_sade_sati_endpoint():
    """
    Main endpoint to calculate complete Sade Sati analysis
    
    Request Body (JSON):
        {
            "user_name": "Name",
            "birth_date": "YYYY-MM-DD",
            "birth_time": "HH:MM:SS",
            "latitude": "17.3850",
            "longitude": "78.4867",
            "timezone_offset": 5.5
        }
    
    Returns:
        JSON response with complete Sade Sati analysis
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract input parameters
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # Set ephemeris path
        
        
        # STEP 1: Calculate Julian Day for birth
        jd_birth = calculate_julian_day(birth_date, birth_time, timezone_offset)
        
        # STEP 2: Get Lahiri Ayanamsa
        ayanamsa_birth = get_ayanamsa(jd_birth)
        
        # STEP 3: Calculate planetary positions
        birth_planets = calculate_all_planets(jd_birth, ayanamsa_birth)
        
        # STEP 4: Calculate Ascendant
        ascendant = calculate_ascendant(jd_birth, latitude, longitude, ayanamsa_birth)
        
        # STEP 5: Calculate Houses
        houses = calculate_houses_whole_sign(ascendant['sign_num'])
        
        # STEP 6: Analyze Moon strength
        moon_strength = analyze_moon_strength(birth_planets['Moon'], birth_date)
        
        # STEP 7: Analyze Saturn status
        saturn_status = analyze_saturn_status(birth_planets['Saturn'], ascendant['sign_num'])
        
        # STEP 8: Calculate current planetary positions
        now = datetime.now()
        jd_current = calculate_julian_day(now.strftime('%Y-%m-%d'), '12:00:00', 0)
        ayanamsa_current = get_ayanamsa(jd_current)
        current_planets = calculate_all_planets(jd_current, ayanamsa_current)
        
        # STEP 9: Calculate Sade Sati status
        natal_moon_sign = birth_planets['Moon']['sign_num']
        current_saturn_sign = current_planets['Saturn']['sign_num']
        sade_sati = calculate_sade_sati_status(natal_moon_sign, current_saturn_sign)
        
        # STEP 10: Calculate Dhaiya
        dhaiya = calculate_dhaiya(natal_moon_sign, current_saturn_sign)
        
        # STEP 11: Analyze cancellation factors
        cancellation_factors = analyze_cancellation_factors(
            birth_planets,
            ascendant['sign_num'],
            moon_strength,
            saturn_status
        )
        
        # STEP 12: Calculate intensity
        intensity = calculate_intensity(sade_sati, cancellation_factors)
        intensity_interpretation = get_intensity_interpretation(intensity)
        
        # STEP 13: Get recommendations
        recommendations = get_personalized_recommendations(
            intensity,
            cancellation_factors,
            sade_sati
        )
        
        # Build response
        response = {
            'success': True,
            'user_info': {
                'name': user_name,
                'birth_date': birth_date,
                'birth_time': birth_time,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone_offset': timezone_offset
                }
            },
            'calculation_details': {
                'julian_day_birth': round(jd_birth, 6),
                'ayanamsa_birth': round(ayanamsa_birth, 6),
                'ayanamsa_type': 'Lahiri (Chitrapaksha)',
                'house_system': 'Whole Sign',
                'coordinate_system': 'Sidereal'
            },
            'birth_chart': {
                'ascendant': ascendant,
                'planets': birth_planets,
                'houses': houses
            },
            'moon_analysis': {
                'sign': ZODIAC_SIGNS[natal_moon_sign],
                'sign_number': natal_moon_sign,
                'house': get_planet_house(natal_moon_sign, ascendant['sign_num']),
                'strength': moon_strength
            },
            'saturn_analysis': {
                'natal': saturn_status,
                'current_transit': {
                    'sign': ZODIAC_SIGNS[current_saturn_sign],
                    'sign_number': current_saturn_sign,
                    'position': current_planets['Saturn']
                }
            },
            'sade_sati': {
                'status': sade_sati,
                'intensity_score': intensity,
                'intensity_interpretation': intensity_interpretation
            },
            'dhaiya': dhaiya,
            'cancellation_factors': cancellation_factors,
            'recommendations': recommendations,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'details': str(ve)
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Calculation Failed',
            'details': str(e)
        }), 500

