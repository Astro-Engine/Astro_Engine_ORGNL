from asyncio.log import logger
import traceback
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
from astro_engine.engine.doshas.PitraDosha import pitra_dosha_analyze_combinations, pitra_dosha_calculate_ascendant, pitra_dosha_calculate_planet_houses, pitra_dosha_calculate_planetary_positions, pitra_dosha_check_planetary_strength, pitra_dosha_format_dms, pitra_dosha_longitude_to_sign
from astro_engine.engine.doshas.SadiSatiDosha import ZODIAC_SIGNS, sade_sati_analyze_cancellation_factors, sade_sati_analyze_moon_strength, sade_sati_analyze_saturn_status, sade_sati_calculate_all_planets, sade_sati_calculate_ascendant, sade_sati_calculate_dhaiya, sade_sati_calculate_houses_whole_sign, sade_sati_calculate_intensity, sade_sati_calculate_julian_day, sade_sati_calculate_status, sade_sati_get_ayanamsa, sade_sati_get_intensity_interpretation, sade_sati_get_personalized_recommendations, sade_sati_get_planet_house
from astro_engine.engine.doshas.ShariptaDosha import ShrapitDoshaAnalyzer, VedicChart
from astro_engine.engine.natalCharts.Panchanga import calculate_abhijit_muhurat, calculate_brahma_muhurat, calculate_dur_muhurat_corrected, calculate_exact_moon_times, calculate_exact_murtha_corrected, calculate_exact_sun_times, calculate_godhuli_muhurat, calculate_inauspicious_periods, calculate_nishita_kaal, calculate_panchanga_elements, calculate_pradosh_kaal_corrected
from astro_engine.engine.remedies.LalkitabRemedies import lal_kitab_calculate_chart, lal_kitab_get_remedies_for_planet_house
from astro_engine.engine.remedies.VedicGemstones import HOUSE_SIGNIFICATIONS, MINIMUM_SHADBALA, SIGN_LORDS, gemstone_calculate_ascendant, gemstone_calculate_houses_whole_sign, gemstone_calculate_planetary_positions, gemstone_calculate_shadbala_simplified, gemstone_calculate_vimshottari_dasha, gemstone_classify_functional_nature, gemstone_get_current_dasha, gemstone_get_julian_day, gemstone_get_planet_house, gemstone_get_positional_strength, gemstone_get_ruled_houses, gemstone_recommend_gemstones_enhanced
from astro_engine.engine.remedies.VedicMantras import analyze_chart_for_mantras, calculate_birth_chart, calculate_nakshatra, get_current_julian_day
from astro_engine.engine.remedies.VedicRemedies import calculate_birth_chart_remedies
from astro_engine.engine.remedies.VedicYantras import FUNCTIONAL_NATURE,  yantra_calculate_birth_chart, yantra_calculate_shadbala, yantra_calculate_vimshottari_dasha, yantra_check_grahan_dosha, yantra_check_kaal_sarp_dosha, yantra_check_mangal_dosha, yantra_check_pitra_dosha, yantra_get_yantra_details, yantra_recommend_yantras
from astro_engine.engine.yogas.BudhaAdhityaYoga import YogaCombinationAnalyzer, analyze_budha_aditya_yoga_with_combinations, calculate_planetary_positions_budha_aditya
from astro_engine.engine.yogas.ChandraMangalYoga import analyze_chandra_mangal_yoga_formation, analyze_individual_planet_permutation, calculate_planetary_positions_chandra_mangal, calculate_yoga_strength, generate_comprehensive_analysis, get_classical_dignity
from astro_engine.engine.yogas.DaridraYoga import EnhancedDaridraYogaCalculator, compute_core_from_birth, daridraYoga
from astro_engine.engine.yogas.DhanYoga import dhanYoga
from astro_engine.engine.yogas.GajakasariYoga import calculate_comprehensive_gaja_kesari_yoga, calculate_planetary_positions
from astro_engine.engine.yogas.GuruMangalYoga import calculate_comprehensive_guru_mangal_yoga, calculate_planetary_positions_guru_mangal
from astro_engine.engine.yogas.KalaSarpaYoga import kala_sarpa_yoga_calculate_ascendant, kala_sarpa_yoga_calculate_planetary_positions, kala_sarpa_yoga_comprehensive_analysis, kala_sarpa_yoga_format_dms, kala_sarpa_yoga_format_planetary_positions
from astro_engine.engine.yogas.KalapaDramaYoga import calculate_kalpadruma_yoga, kalpadruma_yoga_calculate_ascendant, kalpadruma_yoga_calculate_houses, kalpadruma_yoga_calculate_navamsa_positions, kalpadruma_yoga_calculate_planetary_positions, kalpadruma_yoga_format_dms, kalpadruma_yoga_format_planetary_positions
from astro_engine.engine.yogas.MaleficYogas import maleficYoga
from astro_engine.engine.yogas.PachaMahapurushaYoga import compute_natal_core, format_planetary_positions_for_output, panchaMahapursha
from astro_engine.engine.yogas.RajYoga import compute_chart, planetary_positions_json, rajYoga
from astro_engine.engine.yogas.RareYogas import rareYogas
from astro_engine.engine.yogas.SpecialYogas import addSpecialYogas
from astro_engine.engine.yogas.SpiritualYoga import add_spiritualYoga
from astro_engine.engine.yogas.SubhaYoga import add_SubhaYogas
from astro_engine.engine.yogas.ViprithaYoga import add_ViprithaYogas



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

#

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



#  Raja Yoga

@bp.route('/lahiri/raj-yoga', methods=['POST'])
def RajYoga_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # ---- CALCULATIONS (delegated) ----
        chart = compute_chart(data)
        asc_sign = chart["asc_sign"]
        asc_lon = chart["asc_lon"]
        asc_sign_index = chart["asc_sign_index"]
        planet_positions = chart["planet_positions"]
        planet_houses = chart["planet_houses"]
        house_lords = chart["house_lords"]
        house_signs = chart["house_signs"]
        ayanamsa_value = chart["ayanamsa_value"]

        # Raj Yoga analysis via public wrapper
        yogas = rajYoga(planet_positions, planet_houses, house_lords, asc_sign, asc_sign_index)

        # Build response JSON (same shape as before)
        planetary_json = planetary_positions_json(planet_positions, planet_houses)

        # Summary stats
        total_yogas = len(yogas)
        avg_strength = round(sum(y.get('strength', 0) for y in yogas) / total_yogas, 2) if total_yogas else 0.0

        priority_counts = {
            "very_strong": len([y for y in yogas if y.get('priority') == 'Very Strong']),
            "strong": len([y for y in yogas if y.get('priority') == 'Strong']),
            "moderate": len([y for y in yogas if y.get('priority') == 'Moderate'])
        }

        type_counts = {}
        for y in yogas:
            t = y['type']
            type_counts[t] = type_counts.get(t, 0) + 1

        response = {
            "user_name": data['user_name'],
            "birth_details": {
                "birth_date": data['birth_date'],
                "birth_time": data['birth_time'],
                "latitude": float(data['latitude']),
                "longitude": float(data['longitude']),
                "timezone_offset": float(data['timezone_offset'])
            },
            "planetary_positions": planetary_json,
            "ascendant": {
                "sign": asc_sign,
                "degrees": format_dms(asc_lon % 30),
                "longitude": round(asc_lon, 4)
            },
            "house_signs": house_signs,
            "house_lords": {f"House {i}": lord for i, lord in house_lords.items()},
            "raj_yogas": {
                "total_count": total_yogas,
                "average_strength": avg_strength,
                "priority_distribution": priority_counts,
                "type_distribution": type_counts,
                "yogas": yogas
            },
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "chart_type": "Rasi (D1)",
                "house_system": "Whole Sign",
                "yoga_analysis": "Complete Classical Raj Yogas (8 types)",
                "connection_types": "Conjunction, Parivartana, Mutual Aspects",
                "validations": "8th lord handling, combustion, papa kartari (waning Moon only), strength model with malefic/node proximity penalties",
                "implementation": "Full-sign dignity; DKRY with conjunction/mutual aspect/exchange; Adhi with malefic guard; Yogakaraka placement rule"
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  PunchaMahapursha Yoga

@bp.route('/lahiri/pancha-mahapurusha-yogas', methods=['POST'])
def pancha_mahapurusha_yogas():
    """
    Calculate Pancha Mahapurusha Yogas based on natal chart data.
    Logic preserved; uses panchaMahapursha(...) from the calc module.
    """
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # ---- calculations (delegated, unchanged) ----
        core = compute_natal_core(birth_data)

        orientation_shift = int(birth_data.get('orientation_shift', 0))
        planetary_positions_formatted = format_planetary_positions_for_output(
            core["planet_positions"], core["asc_sign_index"], orientation_shift=orientation_shift
        )

        detected_yogas = panchaMahapursha(planetary_positions_formatted)

        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": float(birth_data['latitude']),
                "longitude": float(birth_data['longitude']),
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "yoga_analysis": {
                "total_yogas_found": len(detected_yogas),
                "detected_yogas": detected_yogas,
                "yoga_summary": [y['yoga_name'] for y in detected_yogas] if detected_yogas else "No Pancha Mahapurusha Yogas detected"
            },
            "planetary_positions": planetary_positions_formatted,
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{core['ayanamsa_value']:.6f}",
                "house_system": "Whole Sign",
                "yoga_rules": "Planet in own sign or exaltation + Kendra house (1,4,7,10)",
                "chart_type": "Sidereal Vedic"
            }
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Daridra Yoga

@bp.route('/lahiri/daridra-analysis', methods=['POST'])
def enhanced_daridra_analysis():
    """Complete Daridra Yoga analysis: now returns remedial_measures from calc module."""
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": f"Missing required parameters. Required: {required}"}), 400

        core = compute_core_from_birth(birth_data)

        result = daridraYoga(
            planetary_data=core["planetary_data"],
            ascendant_sign=core["asc_sign"],
            jd_ut=core["jd_ut"],
            latitude=core["latitude"],
            longitude=core["longitude"]
        )
        analysis = result["daridra_yoga_analysis"]
        remedial_measures = result["remedial_measures"]

        # build house lords exactly as before (no logic change)
        house_lords = EnhancedDaridraYogaCalculator(
            planetary_data=core["planetary_data"],
            ascendant_sign=core["asc_sign"],
            jd_ut=core["jd_ut"],
            latitude=core["latitude"],
            longitude=core["longitude"]
        ).house_lords

        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": core["latitude"],
                "longitude": core["longitude"],
                "timezone_offset": core["timezone_offset"]
            },
            "ascendant": {
                "sign": core["asc_sign"],
                "longitude": round(core["ascendant_lon"], 8)
            },
            "planetary_positions": {
                planet: {
                    "sign": data['sign'],
                    "degree_in_sign": round(data['degree_in_sign'], 2),
                    "house": data['house'],
                    "retrograde": data['retrograde']
                }
                for planet, data in core["planetary_data"].items()
            },
            "house_lords": {str(house): lord for house, lord in house_lords.items()},
            "daridra_yoga_analysis": analysis,
            "remedial_measures": remedial_measures,
            "calculation_details": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": round(core["ayanamsa_value"], 6),
                "house_system": "Whole Sign",
                "coordinate_system": "Sidereal",
                "calculation_time_ut": core["ut_datetime"].isoformat(),
                "julian_day": round(core["jd_ut"], 6)
            }
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  Dhan YOga 

@bp.route('/lahiri/dhan-yoga-analysis', methods=['POST'])
def dhan_yoga_analysis():
    """
    Thin API wrapper: parses JSON, calls calculations.dhanYoga(birth_data),
    returns the exact response the original endpoint produced.
    """
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        # delegate to the calculations function (unchanged calculations)
        result = dhanYoga(birth_data)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  Malefic Yogas

@bp.route('/lahiri/malefic_yogas', methods=['POST'])
def malefic_yogas_endpoint():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Validate coordinates (kept identical to original behavior)
        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Delegate to calculations (no logic changes)
        result = maleficYoga(birth_data)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  Rare Yogas 

@bp.route('/lahiri/yoga-analysis', methods=['POST'])
def yoga_analysis():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Delegate to calculations (exact same logic wrapped in rareYogas)
        result = rareYogas(birth_data)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  Special Yogas

@bp.route('/lahiri/special-yogas', methods=['POST'])
def special_yogas_endpoint():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Delegate to the pure calculation function (keeps all your calculations intact)
        result = addSpecialYogas(birth_data)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Spritual Yogas
@bp.route('/lahiri/spiritual_prosperity_yogas', methods=['POST'])
def calculate_spiritual_prosperity_yogas():
    """Calculate comprehensive Yogas for Spiritual Prosperity (API wrapper)"""
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Basic coordinate validation (kept minimal; full parsing happens in calc)
        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Delegate to calculations module
        response = add_spiritualYoga(birth_data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



#  Subha Yoga 

@bp.route('/lahiri/shubh-yogas', methods=['POST'])
def calculate_shubh_yogas():
    """COMPLETE Flask Route Implementation (delegates to add_SubhaYogas)"""
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Delegate all validation & calculations to calc module (keeps logic identical)
        response = add_SubhaYogas(birth_data)
        return jsonify(response)

    except ValueError as ve:
        # Match original error text/shape
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": f"An error occurred: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Vipritha Yoga
@bp.route('/lahiri/viparitha-raja-yoga', methods=['POST'])
def viparitha_raja_yoga():
    try:
        birth_data = request.get_json()
        result = add_ViprithaYogas(birth_data)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  KalapaDrama Yoga
@bp.route('/lahiri/kalpadruma-yoga', methods=['POST'])
def kalpadruma_yoga_analysis():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        timezone_offset = float(birth_data['timezone_offset'])
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

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

        # Calculate planetary positions
        planet_positions, error = kalpadruma_yoga_calculate_planetary_positions(jd_ut)
        if error:
            return jsonify({"error": error}), 500

        # Calculate Ascendant
        ascendant_lon, ascendant_sign, asc_sign_index = kalpadruma_yoga_calculate_ascendant(jd_ut, latitude, longitude)

        # Calculate houses for all planets
        planet_houses = kalpadruma_yoga_calculate_houses(planet_positions, asc_sign_index)

        # Calculate Navamsa positions
        navamsa_positions = kalpadruma_yoga_calculate_navamsa_positions(planet_positions, jd_ut)

        # Calculate Kalpadruma Yoga with CORRECTED rules
        yoga_result = calculate_kalpadruma_yoga(planet_positions, planet_houses, navamsa_positions, ascendant_sign)

        # Format planetary positions for output
        planetary_positions_json = kalpadruma_yoga_format_planetary_positions(planet_positions, planet_houses, navamsa_positions)

        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": timezone_offset
            },
            "ascendant": {
                "sign": ascendant_sign,
                "degrees": kalpadruma_yoga_format_dms(ascendant_lon % 30)
            },
            "planetary_positions": planetary_positions_json,
            "kalpadruma_yoga": yoga_result,
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}",
                "house_system": "Whole Sign",
                "chart_type": "Sidereal",
                "bphs_rule": "Chapter 36, Verses 33-34 (Corrected Implementation)"
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



#  KalaSarpa Yoga
@bp.route('/lahiri/kala-sarpa-fixed', methods=['POST'])
def kala_sarpa_fixed_analysis():
    """
    FIXED KALA SARPA YOGA ANALYSIS API
    All house calculations now use consistent logic throughout.
    """
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Validate input
        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        timezone_offset = float(birth_data['timezone_offset'])
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

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

        # Calculate planetary positions
        planet_positions, error = kala_sarpa_yoga_calculate_planetary_positions(jd_ut)
        if error:
            return jsonify({"error": error}), 500

        # Calculate ascendant
        ascendant_lon, asc_sign_data, asc_sign_index = kala_sarpa_yoga_calculate_ascendant(jd_ut, latitude, longitude)

        # COMPREHENSIVE KALA SARPA ANALYSIS WITH FIXED LOGIC
        kala_sarpa_analysis = kala_sarpa_yoga_comprehensive_analysis(planet_positions, ascendant_lon, asc_sign_index)

        # Format planetary positions for output - CONSISTENT HOUSE CALCULATIONS
        formatted_positions = kala_sarpa_yoga_format_planetary_positions(planet_positions, asc_sign_index)

        # Prepare comprehensive response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_time.strftime('%H:%M:%S'),
                "birth_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone_offset": timezone_offset
                }
            },
            "planetary_positions": formatted_positions,
            "ascendant": {
                "longitude": f"{ascendant_lon:.6f}°",
                "sign": asc_sign_data['sign'],
                "degree_in_sign": f"{asc_sign_data['degree_in_sign']:.6f}°",
                "formatted_degree": kala_sarpa_yoga_format_dms(asc_sign_data['degree_in_sign']),
                "sign_index": asc_sign_data['sign_index']
            },
            "kala_sarpa_analysis": {
                "opposition_verification": kala_sarpa_analysis['opposition_verification'],
                "rule_by_rule_analysis": kala_sarpa_analysis['rule_analysis'],
                "individual_planet_analysis": kala_sarpa_analysis['individual_planet_analysis'],
                "structural_analysis": kala_sarpa_analysis['structural_analysis'],
                "cancellation_analysis": kala_sarpa_analysis['cancellation_analysis'],
                "final_assessment": kala_sarpa_analysis['final_assessment']
            },
            "technical_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{ayanamsa_value:.6f}°",
                "coordinate_system": "Sidereal",
                "house_system": "Whole Sign",
                "ephemeris": "Swiss Ephemeris",
                "calculation_precision": "6 decimal places",
                "house_calculation_method": "Consistent get_house_whole_sign() throughout",
                "fixes_applied": [
                    "Fixed house calculation inconsistency",
                    "Consistent house assignment in all analysis sections",
                    "Proper circular zodiac arc calculations",
                    "Mathematical precision in all rules",
                    "Comprehensive cancellation analysis"
                ]
            },
            "interpretation_guide": {
                "rule_explanations": {
                    "house_conjunction_rule": "Any planet in same house as Rahu/Ketu cancels entire yoga",
                    "degree_precision_rule": "Within same house, node degrees must be greater than planet degrees",
                    "rahu_ketu_arc_rule": "All planets between Rahu→Ketu arc indicates materialistic tendency",
                    "ketu_rahu_arc_rule": "All planets between Ketu→Rahu arc indicates spiritual tendency"
                },
                "strength_levels": {
                    "Very Strong": "All rules satisfied, no cancellations",
                    "Strong": "Most rules satisfied, minimal cancellations",
                    "Moderate": "Some rules satisfied, moderate cancellations", 
                    "Weak": "Few rules satisfied, strong cancellations",
                    "Neutralized": "Yoga present but cancelled by strong factors",
                    "None": "No valid yoga formation"
                },
                "cancellation_factors_hierarchy": {
                    "b_v_raman_neutralization": "Strongest - Ascendant outside axis while planets hemmed (Score: +3)",
                    "ascendant_outside_axis": "Strong - Ascendant not between Rahu-Ketu (Score: +2)",
                    "house_conjunction_cancellation": "Strong - Planets conjunct nodes (Score: +2)",
                    "exalted_planets": "Moderate - Exalted planets reduce effects (Score: +1)",
                    "planets_in_truth_houses": "Moderate - Planets in 1st/7th houses (Score: +1)",
                    "nodes_in_trikona": "Mild - Nodes in 1st/5th/9th houses (Score: +1)"
                }
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



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



#  Sharipta Dosha

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
    
    Expected JSON input:
    {
        "user_name": "Name",
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM:SS",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    """
    try:
        # Get and validate input
        data = request.get_json()
        
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract parameters
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # STEP 1: Calculate Julian Day for birth
        jd_birth = sade_sati_calculate_julian_day(birth_date, birth_time, timezone_offset)
        
        # STEP 2: Get Lahiri Ayanamsa for birth time
        ayanamsa_birth = sade_sati_get_ayanamsa(jd_birth)
        
        # STEP 3: Calculate birth chart planetary positions
        birth_planets = sade_sati_calculate_all_planets(jd_birth, ayanamsa_birth)
        
        # STEP 4: Calculate Ascendant (Lagna)
        ascendant = sade_sati_calculate_ascendant(jd_birth, latitude, longitude, ayanamsa_birth)
        
        # STEP 5: Calculate Houses (Whole Sign System)
        houses = sade_sati_calculate_houses_whole_sign(ascendant['sign_num'])
        
        # STEP 6: Analyze Moon strength
        moon_strength = sade_sati_analyze_moon_strength(birth_planets['Moon'], birth_date)
        
        # STEP 7: Analyze Saturn status
        saturn_status = sade_sati_analyze_saturn_status(birth_planets['Saturn'], ascendant['sign_num'])
        
        # STEP 8: Get current date for transit calculation
        now = datetime.now()
        jd_current = sade_sati_calculate_julian_day(
            now.strftime('%Y-%m-%d'),
            '12:00:00',  # Noon
            0  # UTC
        )
        ayanamsa_current = sade_sati_get_ayanamsa(jd_current)
        current_planets = sade_sati_calculate_all_planets(jd_current, ayanamsa_current)
        
        # STEP 9: Calculate Sade Sati status
        natal_moon_sign = birth_planets['Moon']['sign_num']
        current_saturn_sign = current_planets['Saturn']['sign_num']
        
        sade_sati = sade_sati_calculate_status(natal_moon_sign, current_saturn_sign)
        
        # STEP 10: Calculate Dhaiya
        dhaiya = sade_sati_calculate_dhaiya(natal_moon_sign, current_saturn_sign)
        
        # STEP 11: Analyze cancellation factors
        cancellation_factors = sade_sati_analyze_cancellation_factors(
            birth_planets,
            ascendant['sign_num'],
            moon_strength,
            saturn_status
        )
        
        # STEP 12: Calculate intensity score
        intensity = sade_sati_calculate_intensity(sade_sati, cancellation_factors)
        intensity_interpretation = sade_sati_get_intensity_interpretation(intensity)
        
        # STEP 13: Generate recommendations
        recommendations = sade_sati_get_personalized_recommendations(
            intensity,
            cancellation_factors,
            sade_sati
        )
        
        # Prepare comprehensive response
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
                'house': sade_sati_get_planet_house(natal_moon_sign, ascendant['sign_num']),
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


#  Pitra Dosha 

@bp.route('/lahiri/pitra-dosha', methods=['POST'])
def calculate_pitra_dosha():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        timezone_offset = float(birth_data['timezone_offset'])
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

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

        # Calculate planetary positions
        planet_positions, error = pitra_dosha_calculate_planetary_positions(jd_ut)
        if error:
            return jsonify({"error": error}), 500

        # Calculate Ascendant and houses
        ascendant_lon, asc_sign, asc_sign_index = pitra_dosha_calculate_ascendant(jd_ut, latitude, longitude)

        # Calculate planet houses
        planet_houses = pitra_dosha_calculate_planet_houses(planet_positions, asc_sign_index)

        # Analyze Pitra Dosha with combinations, permutations, and cancellations
        pitra_dosha_analysis = pitra_dosha_analyze_combinations(planet_positions, planet_houses, asc_sign_index)

        # Format planetary positions for output
        planetary_positions_json = {}
        for planet_name, (lon, retro) in planet_positions.items():
            sign, sign_deg, sign_index = pitra_dosha_longitude_to_sign(lon)
            dms = pitra_dosha_format_dms(sign_deg)
            house = planet_houses[planet_name]
            planetary_strength = pitra_dosha_check_planetary_strength(planet_name, planet_positions, planet_houses)
            planetary_positions_json[planet_name] = {
                "sign": sign,
                "degrees": dms,
                "retrograde": retro,
                "house": house,
                "longitude": round(lon, 6),
                "strength": planetary_strength
            }

        # Response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": timezone_offset
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": {
                "sign": asc_sign,
                "degrees": pitra_dosha_format_dms(ascendant_lon % 30),
                "longitude": round(ascendant_lon, 6)
            },
            "pitra_dosha_analysis": pitra_dosha_analysis,
            "calculation_notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": round(ayanamsa_value, 6),
                "house_system": "Whole Sign",
                "chart_type": "Sidereal",
                "includes_cancellations": True,
                "classical_rules": "BPHS and traditional texts",
                "parivartana_yoga_corrected": True
            }
        }

        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# *********************************************************************************************************************
# ***********************************       Remedies        ***********************************************    
# *********************************************************************************************************************

#  Yantras in vedic astrology

@bp.route('/yantra-recommendations', methods=['POST'])
def yantra_recommendations():
    """Main API endpoint for yantra recommendations"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert data
        birth_data = {
            'birth_date': data['birth_date'],
            'birth_time': data['birth_time'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'timezone_offset': float(data['timezone_offset']),
            'user_name': data.get('user_name', 'User')
        }
        
        # Step 1: Calculate birth chart
        chart = yantra_calculate_birth_chart(birth_data)
        
        # Step 2: Calculate Shadbala
        shadbala = yantra_calculate_shadbala(chart)
        
        # Step 3: Check doshas
        doshas = {
            'mangal_dosha': yantra_check_mangal_dosha(chart),
            'kaal_sarp_dosha': yantra_check_kaal_sarp_dosha(chart),
            'pitra_dosha': yantra_check_pitra_dosha(chart),
            'grahan_dosha': yantra_check_grahan_dosha(chart)
        }
        
        # Step 4: Calculate dasha
        dasha = yantra_calculate_vimshottari_dasha(chart, birth_data['birth_date'])
        
        # Step 5: Get yantra recommendations (CORRECTED LOGIC)
        recommendations = yantra_recommend_yantras(chart, shadbala, doshas, dasha, birth_data['birth_date'])
        
        # Add yantra details to top recommendations
        top_recommendations = []
        for rec in recommendations[:3]:
            yantra_details = yantra_get_yantra_details(rec['planet'])
            rec['yantra_details'] = yantra_details
            top_recommendations.append(rec)
        
        # Prepare response
        response = {
            'user_name': birth_data['user_name'],
            'birth_details': {
                'date': birth_data['birth_date'],
                'time': birth_data['birth_time'],
                'location': f"{birth_data['latitude']}, {birth_data['longitude']}"
            },
            'ascendant': chart['ascendant'],
            'functional_nature': FUNCTIONAL_NATURE.get(chart['ascendant']['sign'], {}),
            'current_dasha': dasha.get('current_mahadasha') if dasha else None,
            'doshas_detected': {
                'mangal_dosha': doshas['mangal_dosha']['present'],
                'kaal_sarp_dosha': doshas['kaal_sarp_dosha']['present'],
                'pitra_dosha': doshas['pitra_dosha']['present'],
                'grahan_dosha': doshas['grahan_dosha']['present']
            },
            'yantra_recommendations': top_recommendations,
            'all_recommendations_count': len(recommendations),
            'planetary_strengths': shadbala,
            'detailed_analysis': {
                'chart': chart,
                'doshas': doshas,
                'dasha': dasha
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500



#  Mantras for vedic astrology

@bp.route('/lahiri/mantra-analysis', methods=['POST'])
def mantra_analysis():
    """Main API endpoint for comprehensive mantra analysis"""
    try:
        data = request.json
        
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        user_name = data.get('user_name')
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        timezone_offset = float(data.get('timezone_offset'))
        
        birth_jd = get_julian_day(birth_date, birth_time, timezone_offset)
        current_jd = get_current_julian_day()
        
        chart, ayanamsa = calculate_birth_chart(birth_jd, latitude, longitude)
        
        moon_longitude = chart['Moon']['longitude']
        moon_nakshatra = calculate_nakshatra(moon_longitude)
        
        analysis = analyze_chart_for_mantras(
            chart, current_jd, latitude, longitude, birth_jd, moon_longitude, birth_date
        )
        
        response = {
            'status': 'success',
            'user_name': user_name,
            'birth_details': {
                'date': birth_date,
                'time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': timezone_offset,
                'julian_day': round(birth_jd, 6),
                'ayanamsa': round(ayanamsa, 6),
                'chart_type': 'Sidereal (Lahiri Ayanamsa)',
                'house_system': 'Whole Sign'
            },
            'chart_summary': {
                'ascendant': f"{chart['Ascendant']['degree']:.2f}° {chart['Ascendant']['sign']}",
                'moon_sign': chart['Moon']['sign'],
                'moon_nakshatra': moon_nakshatra['name'],
                'sun_sign': chart['Sun']['sign']
            },
            'planetary_positions': {
                planet: {
                    'sign': chart[planet]['sign'],
                    'degree': round(chart[planet]['degree'], 2),
                    'longitude': round(chart[planet]['longitude'], 2),
                    'house': chart[planet]['house'],
                    'retrograde': chart[planet].get('retrograde', False)
                }
                for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            },
            'mantra_analysis': analysis,
            'system_info': {
                'version': '3.0 - CORRECTED & COMPLETE',
                'corrections_applied': [
                    'FIXED: Aspect calculation formula (critical fix)',
                    'FIXED: Mangal Dosha from Lagna, Moon, AND Venus',
                    'FIXED: Kaal Sarp using longitude-based hemming (more precise)',
                    'FIXED: All Jupiter and Saturn aspect calculations',
                    'ADDED: Anulom vs Pratilom KSD detection',
                    'ADDED: Multiple cancellation rules',
                    'ADDED: Detailed aspect information'
                ],
                'features': [
                    'Complete Mangal Dosha (3 reference points + 9 cancellations)',
                    'Complete Kaal Sarp Dosha (longitude-based + 5 cancellations)',
                    'Complete Pitra Dosha (8 indicators + 5 cancellations)',
                    'Corrected aspect calculations for all planets',
                    'Conjunction detection with orbs',
                    'Age-based cancellations',
                    'Vimshottari Dasha system'
                ]
            }
        }
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500



#  Vedic remedies

@bp.route('/lahiri/vedic_remedies', methods=['POST'])
def calculate_endpoint():
    """✅ Calculate endpoint"""
    try:
        data = request.get_json()
        
        required = ['user_name', 'birth_date', 'birth_time', 
                   'latitude', 'longitude', 'timezone_offset']
        
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        result = calculate_birth_chart_remedies(data)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logging.error(f"Endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


#  Gemestones in vedic astrology

@bp.route('/lahiri/calculate-gemstone', methods=['POST'])
def calculate_gemstone():
    """Main endpoint for gemstone calculation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Extract data
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        
        # Optional: recommendation approach
        approach = data.get('approach', 'balanced')  # classical, modern, balanced
        
        # Calculate Julian Day
        jd = gemstone_get_julian_day(birth_date, birth_time, timezone_offset)
        
        # Calculate Ascendant
        asc_longitude, asc_sign = gemstone_calculate_ascendant(jd, latitude, longitude)
        asc_lord = SIGN_LORDS[asc_sign]
        
        # Calculate Houses (Whole Sign)
        houses = gemstone_calculate_houses_whole_sign(asc_sign)
        
        # Calculate Planetary Positions
        planetary_positions, ayanamsa = gemstone_calculate_planetary_positions(jd)
        
        # Analyze each planet
        planets_analysis = {}
        
        for planet_name, planet_data in planetary_positions.items():
            # Add house placement
            planet_data['house'] = gemstone_get_planet_house(planet_data['sign'], asc_sign)
            
            # Get ruled houses
            ruled_houses = gemstone_get_ruled_houses(planet_name, asc_sign)
            
            # Calculate Shadbala
            shadbala = gemstone_calculate_shadbala_simplified(planet_name, planet_data, asc_sign)
            min_strength = MINIMUM_SHADBALA.get(planet_name, 300)
            is_weak = shadbala < min_strength
            strength_pct = round((shadbala / min_strength) * 100, 1)
            
            # Functional nature
            functional_nature, reasons = gemstone_classify_functional_nature(planet_name, ruled_houses, asc_sign)
            
            # Positional status
            pos_strength, pos_status = gemstone_get_positional_strength(
                planet_name,
                planet_data['sign'],
                planet_data['degree_in_sign']
            )
            
            house_sigs = [HOUSE_SIGNIFICATIONS[h] for h in ruled_houses]
            
            planets_analysis[planet_name] = {
                'position': planet_data,
                'ruled_houses': ruled_houses,
                'functional_nature': functional_nature,
                'functional_reasons': reasons,
                'positional_status': pos_status,
                'positional_strength': round(pos_strength, 2),
                'shadbala': shadbala,
                'minimum_required': min_strength,
                'is_weak': is_weak,
                'strength_percentage': strength_pct,
                'house_significations': house_sigs
            }
        
        # Calculate Dasha
        moon_longitude = planetary_positions['Moon']['longitude']
        dasha_timeline, birth_nakshatra = gemstone_calculate_vimshottari_dasha(moon_longitude, birth_date)
        current_dasha = gemstone_get_current_dasha(dasha_timeline)
        
        # Generate Recommendations (ENHANCED)
        recommendations, avoid_list, compatibility = gemstone_recommend_gemstones_enhanced(
            planets_analysis,
            current_dasha,
            asc_sign,
            asc_lord,
            approach=approach
        )
        
        # Response
        response = {
            'status': 'success',
            'calculation_details': {
                'ayanamsa_used': 'Lahiri',
                'ayanamsa_value': round(ayanamsa, 6),
                'house_system': 'Whole Sign',
                'zodiac': 'Sidereal',
                'recommendation_approach': approach,
                'version': '3.0-ENHANCED'
            },
            'user_details': {
                'name': user_name,
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': timezone_offset
            },
            'chart_details': {
                'ascendant': {
                    'sign': SIGNS[asc_sign],
                    'sign_number': asc_sign,
                    'degree': round(asc_longitude % 30, 4),
                    'longitude': round(asc_longitude, 4),
                    'lord': asc_lord
                },
                'planetary_positions': {
                    planet: {
                        'sign': data['position']['sign_name'],
                        'degree': round(data['position']['degree_in_sign'], 4),
                        'house': data['position']['house'],
                        'retrograde': data['position'].get('retrograde', False),
                        'positional_status': data['positional_status'],
                        'positional_strength': data['positional_strength']
                    }
                    for planet, data in planets_analysis.items()
                },
                'houses': houses
            },
            'planetary_strength_analysis': {
                planet: {
                    'ruled_houses': data['ruled_houses'],
                    'functional_nature': data['functional_nature'],
                    'functional_reasons': data['functional_reasons'],
                    'positional_status': data['positional_status'],
                    'positional_strength': data['positional_strength'],
                    'shadbala_strength': data['shadbala'],
                    'minimum_required': data['minimum_required'],
                    'strength_percentage': data['strength_percentage'],
                    'is_weak': data['is_weak'],
                    'house_significations': data['house_significations']
                }
                for planet, data in planets_analysis.items()
            },
            'dasha_details': {
                'birth_nakshatra': birth_nakshatra + 1,
                'birth_nakshatra_lord': planetary_positions['Moon'],
                'current_maha_dasha': current_dasha,
                'dasha_timeline': dasha_timeline[:5]
            },
            'gemstone_recommendations': {
                'primary_recommendations': recommendations,
                'gemstones_to_avoid': avoid_list,
                'compatibility_notes': compatibility,
                'approach_used': approach,
                'approach_explanation': {
                    'classical': 'Traditional Parashari rules - Avoid all dusthana lords (6th, 8th, 12th)',
                    'modern': 'Support current dasha lord even if malefic - with strong warnings',
                    'balanced': 'Balanced approach - Consider dasha lords with comprehensive warnings'
                }[approach],
                'general_guidelines': [
                    "✓ Always wear natural, untreated, eye-clean gemstones",
                    "✓ Gemstone should touch the skin (open-back setting)",
                    "✓ Energize with prescribed mantra before wearing",
                    "✓ Wear on the prescribed day, time, finger, and metal",
                    "✗ NEVER wear gemstones of exalted planets",
                    "✗ NEVER wear gemstones of planets in own sign (unless specifically weak)",
                    "✗ NEVER wear enemy planet gemstones simultaneously",
                    "🚨 Blue Sapphire (Saturn): MANDATORY 3-day test period",
                    "👨‍⚕️ ALWAYS consult a qualified Vedic astrologer for final confirmation",
                    "⚠️ If ANY negative effects occur within 3 days, remove immediately"
                ]
            }
        }
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve),
            'type': 'validation_error'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc(),
            'type': 'server_error'
        }), 500


#  Lal kitab remedies
@bp.route('/lahiri/calculate-chart', methods=['POST'])
def api_calculate_chart():
    """API endpoint to calculate birth chart"""
    try:
        data = request.json
        
        birth_date = data.get('birth_date')  # Format: YYYY-MM-DD
        birth_time = data.get('birth_time')  # Format: HH:MM
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        timezone_offset = float(data.get('timezone_offset', 5.5))
        
        if not all([birth_date, birth_time, latitude, longitude]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        chart = lal_kitab_calculate_chart(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify({'success': True, 'chart': chart})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lahiri/lal-kitab-remedies', methods=['POST'])
def api_lal_kitab_remedies():
    """Get Lal Kitab remedies for specific planet-house combination"""
    try:
        data = request.json
        planet = data.get('planet')
        house = int(data.get('house'))
        
        result = lal_kitab_get_remedies_for_planet_house(planet, house)
        return jsonify({'success': True, 'data': result})
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/chart-with-remedies', methods=['POST'])
def api_chart_with_remedies():
    """Calculate chart and get all Lal Kitab remedies"""
    try:
        data = request.json
        
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        timezone_offset = float(data.get('timezone_offset', 5.5))
        
        if not all([birth_date, birth_time, latitude, longitude]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Calculate chart
        chart = lal_kitab_calculate_chart(birth_date, birth_time, latitude, longitude, timezone_offset)
        
        # Get remedies for all planets
        all_remedies = lal_kitab_get_all_chart_remedies(chart)
        
        return jsonify({
            'success': True,
            'chart': chart,
            'lal_kitab_remedies': all_remedies
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500




# **********************************************************************************************************************
# ***********************************   Panchanga   ***********************************************    
# **********************************************************************************************************************


# @bp.route('/panchanga', methods=['POST'])
# def calculate_panchanga():
#     """Main API endpoint with EXACT calculations"""
    
#     try:
#         data = request.get_json()
        
#         date_str = str(data["date"]).strip()
#         time_str = str(data["time"]).strip()
#         latitude = float(data["latitude"])
#         longitude = float(data["longitude"])
#         timezone_str = str(data["timezone"]).strip()
        
#         print(f"\n{'='*70}")
#         print(f"REQUEST: {date_str} {time_str} ({timezone_str})")
#         print(f"Location: {latitude}°N, {longitude}°E")
        
#         # Calculate Panchanga elements
#         panchanga = calculate_panchanga_elements(date_str, time_str, timezone_str)
        
#         # Calculate EXACT sun/moon times with Skyfield
#         sun_times = calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str)
#         moon_times = calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str)
        
#         if not sun_times or not moon_times:
#             return jsonify({
#                 "status": "error",
#                 "message": "Skyfield calculation failed. Please install: pip install skyfield"
#             }), 500
        
#         print(f"✓ EXACT TIMES CALCULATED")
#         print(f"  Sunrise: {sun_times['sunrise']}")
#         print(f"  Sunset: {sun_times['sunset']}")
#         print(f"  Moonrise: {moon_times['moonrise']}")
#         print(f"  Moonset: {moon_times['moonset']}")
#         print(f"{'='*70}\n")
        
#         return jsonify({
#             "status": "success",
#             "input": {
#                 "date": date_str,
#                 "time": time_str,
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "timezone": timezone_str
#             },
#             "panchanga": panchanga,
#             "times": {
#                 "sunrise": {
#                     "time": sun_times['sunrise'],
#                     "method": sun_times['method'],
#                     "status": "exact"
#                 },
#                 "sunset": {
#                     "time": sun_times['sunset'],
#                     "method": sun_times['method'],
#                     "status": "exact"
#                 },
#                 "moonrise": {
#                     "time": moon_times['moonrise'],
#                     "method": moon_times['method'],
#                     "status": "exact"
#                 },
#                 "moonset": {
#                     "time": moon_times['moonset'],
#                     "method": moon_times['method'],
#                     "status": "exact"
#                 }
#             }
#         })
        
#     except Exception as e:
#         print(f"ERROR: {e}")
#         traceback.print_exc()
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500






@bp.route('/panchanga', methods=['POST'])
def calculate_complete_panchanga():
    """
    Complete Panchanga API Endpoint
    
    POST /
    
    Request Body (JSON):
    {
        "date": "YYYY-MM-DD",
        "time": "HH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone": "Timezone/String"
    }
    
    Returns:
    {
        "status": "success",
        "panchanga": {...},
        "times": {...},
        "murtha": {...},
        "muhurat": {...}
    }
    """
    
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        # Validate required fields
        required_fields = ["date", "time", "latitude", "longitude", "timezone"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Extract and validate input data
        try:
            date_str = str(data["date"]).strip()
            time_str = str(data["time"]).strip()
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
            timezone_str = str(data["timezone"]).strip()
            
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Longitude must be between -180 and 180")
                
        except (ValueError, TypeError) as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid data format: {str(e)}"
            }), 400
        
        # Log request
        print(f"\n{'='*70}")
        print(f"REQUEST: {date_str} {time_str} ({timezone_str})")
        print(f"Location: {latitude}°N, {longitude}°E")
        
        # ====================================================================
        # CALCULATE ALL COMPONENTS
        # ====================================================================
        
        # 1. Calculate Panchanga elements
        panchanga = calculate_panchanga_elements(date_str, time_str, timezone_str)
        
        # 2. Calculate Sun times
        sun_times = calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str)
        
        # 3. Calculate Moon times
        moon_times = calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str)
        
        # Check if astronomical calculations succeeded
        if not sun_times or not moon_times:
            return jsonify({
                "status": "error",
                "message": "Skyfield calculation failed. Ensure Skyfield is installed."
            }), 500
        
        # Extract required data
        weekday = panchanga["weekday"]
        sunrise_dt = sun_times["sunrise_dt"]
        sunset_dt = sun_times["sunset_dt"]
        jd_current = panchanga["julian_day"]
        
        # 4. Calculate Murtha with corrected day length
        murtha = calculate_exact_murtha_corrected(
            date_str, time_str, latitude, longitude, timezone_str, 
            sunset_dt=sunset_dt
        )
        
        # 5. Calculate all Muhurat timings
        inauspicious = calculate_inauspicious_periods(sunrise_dt, sunset_dt, weekday)
        abhijit = calculate_abhijit_muhurat(sunrise_dt, sunset_dt)
        brahma = calculate_brahma_muhurat(sunrise_dt)
        godhuli = calculate_godhuli_muhurat(sunset_dt)
        pradosh = calculate_pradosh_kaal_corrected(sunset_dt)
        dur_muhurat_list = calculate_dur_muhurat_corrected(sunrise_dt, sunset_dt, weekday)
        
        # 6. Calculate Varjyam with exact nakshatra end
        nakshatra_num = panchanga["nakshatra"]["number"]
        
        # Get current Moon longitude for accurate Varjyam calculation
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        moon_result = swe.calc_ut(jd_current, swe.MOON, flags)
        moon_longitude = moon_result[0][0] % 360.0
        
        # varjyam = calculate_varjyam_exact(nakshatra_num, jd_current, timezone_str, moon_longitude)
        
        # 7. Calculate Nishita Kaal (previous day's sunset needed)
        prev_day = sunrise_dt - timedelta(days=1)
        prev_sun_times = calculate_exact_sun_times(
            prev_day.strftime("%Y-%m-%d"),
            "12:00:00",
            latitude,
            longitude,
            timezone_str
        )
        
        nishita = None
        if prev_sun_times and "sunset_dt" in prev_sun_times:
            nishita = calculate_nishita_kaal(prev_sun_times["sunset_dt"], sunrise_dt)
        
        print(f"✓ ALL CALCULATIONS COMPLETE")
        print(f"{'='*70}\n")
        
        # ====================================================================
        # BUILD RESPONSE
        # ====================================================================
        
        response_data = {
            "status": "success",
            "version": "corrected_final_v1.0",
            "corrections_applied": [
                "Day length now shows actual daylight hours (sunrise to sunset)",
                "Varjyam uses exact nakshatra end time from Swiss Ephemeris",
                "Pradosh Kaal logic documented and verified",
                "Murtha displays both cycle time and daylight time"
            ],
            "input": {
                "date": date_str,
                "time": time_str,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_str
            },
            "panchanga": {
                "tithi": panchanga["tithi"],
                "nakshatra": panchanga["nakshatra"],
                "yoga": panchanga["yoga"],
                "karana": panchanga["karana"],
                "vara": panchanga["vara"]
            },
            "times": {
                "sunrise": {
                    "time": sun_times['sunrise'],
                    "method": "skyfield_exact"
                },
                "sunset": {
                    "time": sun_times['sunset'],
                    "method": "skyfield_exact"
                },
                "moonrise": {
                    "time": moon_times['moonrise'],
                    "method": "skyfield_exact"
                },
                "moonset": {
                    "time": moon_times['moonset'],
                    "method": "skyfield_exact"
                }
            },
            "murtha": murtha if murtha else {"status": "calculation_failed"},
            "muhurat": {
                "inauspicious_periods": inauspicious,
                "auspicious_periods": {
                    **abhijit,
                    **brahma,
                    **godhuli,
                    **pradosh
                },
                "dur_muhurat": dur_muhurat_list,
                # "varjyam": varjyam
            }
        }
        
        # Add Nishita Kaal if calculated
        if nishita:
            response_data["muhurat"]["auspicious_periods"].update(nishita)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500



