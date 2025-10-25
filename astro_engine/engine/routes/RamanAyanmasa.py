
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger
import swisseph as swe
swe.set_ephe_path('astro_engine/ephe')

from astro_engine.engine.lagnaCharts.RamanHoraLagna import raman_hora_calculate_chart
from astro_engine.engine.lagnaCharts.RamanBavaLagna import PLANET_IDS, raman_bava_calculate_bhava_lagna, raman_bava_calculate_house, raman_bava_calculate_sunrise, raman_bava_get_julian_day, raman_bava_get_sign_and_degrees, raman_bava_nakshatra_and_pada
from astro_engine.engine.ashatakavargha.RamanVarghaSigns import CHARTS, SIGNS, raman_sign_get_sidereal_asc, raman_sign_get_sidereal_positions, raman_sign_julian_day, raman_sign_local_to_utc, raman_sign_varga_sign
from astro_engine.engine.ramanDivisionals.TrimshamshaD30 import raman_d30_assign_houses, raman_d30_calculate_sidereal_longitudes, raman_d30_format_degree, raman_d30_get_d30_sign_and_degree, raman_d30_get_julian_day, raman_d30_get_nakshatra_and_pada






from astro_engine.engine.ashatakavargha.RamanBinnastakvargha import raman_binnastakavargha
from astro_engine.engine.ashatakavargha.RamanSarvastakavargha import raman_sarvathakavargha
from astro_engine.engine.dashas.RamanAntarDasha import calculate_dasha_balance_raman_antar, calculate_mahadasha_periods_antar_raman, calculate_moon_sidereal_position_raman_antar, get_julian_day_antar_raman, get_nakshatra_and_lord_raman_antar
from astro_engine.engine.dashas.RamanPranDasha import calculate_dasha_balance_pran_raman, calculate_moon_sidereal_position_pran_raman, calculate_pran_raman_periods, get_julian_day_pran_raman, get_nakshatra_and_lord_pran_raman
from astro_engine.engine.dashas.RamanPratyantardashas import calculate_dasha_balance_prataythar_raman, calculate_moon_sidereal_position_prataythar_raman, calculate_prataythar_raman_periods, get_julian_day_prataythar_raman, get_nakshatra_and_lord_prataythar_raman
from astro_engine.engine.dashas.RamanSookshmaDasha import calculate_moon_sidereal_sookshma_raman, calculate_sookshma_dasha_balance_raman, calculate_sookshma_raman_periods, get_julian_day_sookshma_raman, get_nakshatra_and_lord_soo_raman
from astro_engine.engine.divisionalCharts.DreshkanaD3 import PLANET_NAMES, get_julian_day
from astro_engine.engine.lagnaCharts.MoonRaman import raman_moon_chart, validate_input
from astro_engine.engine.lagnaCharts.RamanArudha import raman_arudha_lagna
    
from astro_engine.engine.lagnaCharts.RamanEqualBava import raman_equal_bava_lagnas
from astro_engine.engine.lagnaCharts.RamanKarkamshaD1 import raman_karkamsha_D1
from astro_engine.engine.lagnaCharts.RamanKarkamshaD9 import raman_karkamsha_D9
from astro_engine.engine.lagnaCharts.RamanKpLagna import raman_kp_bava
from astro_engine.engine.lagnaCharts.RamanSripathi import raman_sripathi_bava
from astro_engine.engine.lagnaCharts.SunRaman import  raman_sun_chart, validate_input_sun
from astro_engine.engine.natalCharts.RamanChakara import raman_sudarshan_chakra
from astro_engine.engine.natalCharts.RamanNatal import raman_natal, format_dms
from astro_engine.engine.natalCharts.natal import longitude_to_sign
from astro_engine.engine.ramanDivisionals.AkshavedamshaD45 import raman_Akshavedamsha_D45
from astro_engine.engine.ramanDivisionals.ChaturthamshaD4 import raman_Chaturthamsha_D4
from astro_engine.engine.ramanDivisionals.ChaturvimshamshaD24 import raman_Chaturvimshamsha_D24
from astro_engine.engine.ramanDivisionals.DashamshaD10 import raman_Dashamsha_D10
from astro_engine.engine.ramanDivisionals.DreshkanaD3 import raman_drekshakana
from astro_engine.engine.ramanDivisionals.DwadashamshaD12 import raman_Dwadashamsha_D12
from astro_engine.engine.ramanDivisionals.HoraD2 import raman_hora_chart
from astro_engine.engine.ramanDivisionals.KhavedamshaD40 import raman_Khavedamsha_D40
from astro_engine.engine.ramanDivisionals.NavamsaD9 import raman_navamsa_D9
from astro_engine.engine.ramanDivisionals.SaptamshaD7 import raman_saptamsha
from astro_engine.engine.ramanDivisionals.SaptavimshamshaD27 import PLANET_CODES, ZODIAC_SIGNS_raman, raman_d27_calculate_ascendant, raman_d27_calculate_d27_longitude, raman_d27_calculate_house, raman_d27_calculate_sidereal_longitude, raman_d27_get_julian_day_utc, raman_d27_get_nakshatra_pada, raman_d27_get_sign_index
from astro_engine.engine.ramanDivisionals.ShashtiamshaD60 import raman_Shashtiamsha_D60
from astro_engine.engine.ramanDivisionals.ShodashamshaD16 import raman_Shodashamsha_D16
from astro_engine.engine.ramanDivisionals.VimshamshaD20 import raman_Vimshamsha_D20





rl = Blueprint('rl_routes', __name__)


#   Natal Chart 
@rl.route('/raman/natal', methods=['POST'])
def natal_chart():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Calculate chart data
        chart_data = raman_natal(birth_data)

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
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500






#  Moon Chart 
@rl.route('/raman/calculate_moon_chart', methods=['POST'])
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
        response = raman_moon_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500




# Sun Chart :
@rl.route('/raman/calculate_sun_chart', methods=['POST'])
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
        response = raman_sun_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500




# Sudharasha Chakara 
@rl.route('/raman/calculate_sudarshan_chakra', methods=['POST'])
def calculate_sudarshan_chakra():
    """
    Flask endpoint to calculate the Sudarshan Chakra based on birth details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract and validate input
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Basic validation for latitude and longitude
        if not (-90 <= latitude <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90 degrees"}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180 degrees"}), 400

        # Call the calculation function
        result = raman_sudarshan_chakra(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500





#**************************************************************************************************************
#***********************************    Divisonal Charts        ***********************************************
#**************************************************************************************************************



#  Hora D2 :
@rl.route('/raman/calculate_d2_hora', methods=['POST'])
def calculate_d2_hora():
    """API endpoint to calculate the D2 Hora chart."""
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
        result = raman_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset)
        response = {
            'user_name': user_name,
            'd2_hora_chart': result,
            'metadata': {
                'ayanamsa': 'Raman',
                'house_system': 'Whole Sign',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# Dreshkana D3
@rl.route('/raman/calculate_d3_chart', methods=['POST'])
def calculate_d3_chart_endpoint():
    """API endpoint to calculate D3 chart with retrograde, nakshatra, and pada."""
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

        jd = get_julian_day(birth_date, birth_time, tz_offset)
        d3_data = raman_drekshakana(jd, latitude, longitude)

        response = {
            "ascendant": d3_data['Ascendant'],
            "planets": {planet: d3_data[planet] for planet in PLANET_NAMES}
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D3 chart calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500





#  Chaturthamsha-D4
@rl.route('/raman/calculate_d4', methods=['POST'])
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

        # Parse inputs
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        # Calculate D4 chart
        result = raman_Chaturthamsha_D4(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Saptamsha D7 
@rl.route('/raman/calculate_d7_chart', methods=['POST'])
def calculate_d7_chart_endpoint():
    """API endpoint to calculate D7 chart from birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Required fields (user_name is optional)
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day and D7 chart
        jd = get_julian_day(birth_date, birth_time, tz_offset)
        d7_data = raman_saptamsha(jd, latitude, longitude)

        # Prepare response
        response = {
            "ascendant": d7_data['Ascendant'],
            "planets": {planet: d7_data[planet] for planet in PLANET_NAMES}
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D7 calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Navamsa D9
@rl.route('/raman/navamsha_d9', methods=['POST'])
def navamsa_chart():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Check for required parameters
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Parse input data
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        # Call the calculation function
        result = raman_navamsa_D9(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





# Dashamsha D10
@rl.route('/raman/calculate_d10', methods=['POST'])
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

        # Calculate D10 chart
        result = raman_Dashamsha_D10(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Dwadashamsha D12

@rl.route('/raman/calculate_d12', methods=['POST'])
def calculate_d12():
    """
    Flask API endpoint to calculate the complete Dwadasamsa (D12) chart.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - D12 ascendant, planetary positions, house signs, and metadata
    """
    try:
        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Extract inputs
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        # Calculate D12 chart using the function from calculations.py
        result = raman_Dwadashamsha_D12(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Shodashamsha D16
@rl.route('/raman/calculate_d16', methods=['POST'])
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

        result = raman_Shodashamsha_D16(birth_date, birth_time, latitude, longitude, tz_offset, enforce_opposition)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Vimshamsha D20
@rl.route('/raman/calculate_d20', methods=['POST'])
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

        # Call the calculation function
        result = raman_Vimshamsha_D20(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Chaturvimshamsha D24

@rl.route('/raman/calculate_d24', methods=['POST'])
def calculate_d24():
    """API endpoint to calculate D24 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        result = raman_Chaturvimshamsha_D24(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Saptavimshamsha D27
@rl.route('/raman/calculate_d27_chart', methods=['POST'])
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

        jd_utc = raman_d27_get_julian_day_utc(birth_date, birth_time, tz_offset)
        natal_asc_lon = raman_d27_calculate_ascendant(jd_utc, latitude, longitude)
        d27_asc_lon = raman_d27_calculate_d27_longitude(natal_asc_lon)
        d27_asc_sign_index = raman_d27_get_sign_index(d27_asc_lon)
        d27_asc_deg = d27_asc_lon % 30

        natal_planet_lons = {}
        natal_planet_retro = {}

        # Rahu/Ketu
        natal_rahu_lon, _ = raman_d27_calculate_sidereal_longitude(jd_utc, swe.MEAN_NODE)
        natal_ketu_lon = (natal_rahu_lon + 180) % 360
        natal_planet_lons["Rahu"] = natal_rahu_lon
        natal_planet_lons["Ketu"] = natal_ketu_lon
        natal_planet_retro["Rahu"] = True
        natal_planet_retro["Ketu"] = True

        for planet, code in PLANET_CODES.items():
            if planet == "Rahu":
                continue  # Already handled
            lon, retro = raman_d27_calculate_sidereal_longitude(jd_utc, code)
            natal_planet_lons[planet] = lon
            natal_planet_retro[planet] = retro

        d27_chart = {}

        # Ascendant
        asc_nak, asc_lord, asc_pada = raman_d27_get_nakshatra_pada(d27_asc_lon)
        natal_asc_nak, natal_asc_lord, natal_asc_pada = raman_d27_get_nakshatra_pada(natal_asc_lon)
        d27_chart["Ascendant"] = {
            "d27_sign": ZODIAC_SIGNS_raman[d27_asc_sign_index],
            "degrees": round(d27_asc_deg, 4),
            "house": 1,
            "d27_nakshatra": asc_nak,
            "d27_nakshatra_lord": asc_lord,
            "d27_pada": asc_pada,
            # "natal_sign": ZODIAC_SIGNS_raman[raman_d27_get_sign_index(natal_asc_lon)],
            # "natal_nakshatra": natal_asc_nak,
            # "natal_nakshatra_lord": natal_asc_lord,
            # "natal_pada": natal_asc_pada,
            "retrograde": False
        }

        for planet in list(PLANET_CODES.keys()) + ["Ketu"]:
            natal_lon = natal_planet_lons[planet]
            d27_lon = raman_d27_calculate_d27_longitude(natal_lon)
            d27_sign_index = raman_d27_get_sign_index(d27_lon)
            d27_deg = d27_lon % 30
            house = raman_d27_calculate_house(d27_asc_sign_index, d27_sign_index)
            natal_sign = ZODIAC_SIGNS_raman[raman_d27_get_sign_index(natal_lon)]
            retro = natal_planet_retro[planet]

            d27_nakshatra, d27_nak_lord, d27_pada = raman_d27_get_nakshatra_pada(d27_lon)
            natal_nakshatra, natal_nak_lord, natal_pada = raman_d27_get_nakshatra_pada(natal_lon)

            d27_chart[planet] = {
                "d27_sign": ZODIAC_SIGNS_raman[d27_sign_index],
                "degrees": round(d27_deg, 4),
                "house": house,
                "d27_nakshatra": d27_nakshatra,
                "d27_nakshatra_lord": d27_nak_lord,
                "d27_pada": d27_pada,
                # "natal_sign": natal_sign,
                # "natal_nakshatra": natal_nakshatra,
                # "natal_nakshatra_lord": natal_nak_lord,
                # "natal_pada": natal_pada,
                "retrograde": retro
            }

        response = {
            "user_name": user_name,
            "d27_chart": d27_chart
        }
        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




#  Trimshamsha D30 


@rl.route('/raman/calculate_d30_chart', methods=['POST'])
def calculate_d30_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = data['latitude']
        longitude = data['longitude']
        tz_offset = float(data['timezone_offset'])

        jd = raman_d30_get_julian_day(birth_date, birth_time, tz_offset)
        natal_positions = raman_d30_calculate_sidereal_longitudes(jd, latitude, longitude)

        d30_positions = {}
        # First get the D30 sign and index for the Ascendant
        asc_sign, asc_deg, asc_sign_index, asc_natal_sign, asc_natal_deg = raman_d30_get_d30_sign_and_degree(
            natal_positions['Ascendant']['longitude']
        )

        for planet, pdata in natal_positions.items():
            longitude = pdata['longitude']
            sign, degree, d30_sign_index, natal_sign, natal_deg = raman_d30_get_d30_sign_and_degree(longitude)
            nak, nak_lord, pada = raman_d30_get_nakshatra_and_pada(longitude)
            d30_positions[planet] = {
                'sign': sign,
                'degree': raman_d30_format_degree(degree),
                'retrograde': pdata['retrograde'],
                'nakshatra': nak,
                # 'natal_sign': natal_sign,
                # 'natal_degree': raman_d30_format_degree(natal_deg),
                # 'natal_longitude': round(longitude, 4),
                'pada': pada,
                'd30_sign_index': d30_sign_index
            }

        # Now assign houses properly
        raman_d30_assign_houses(d30_positions, asc_sign_index)
        # Remove 'd30_sign_index' from output for clarity
        for planet in d30_positions:
            if 'd30_sign_index' in d30_positions[planet]:
                del d30_positions[planet]['d30_sign_index']

        response = {
            "user_name": data.get('user_name', 'Unknown'),
            # "natal_positions": {p: natal_positions[p]['longitude'] for p in natal_positions},
            "d30_chart": d30_positions
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Khavedamsha D40

@rl.route('/raman/calculate_d40', methods=['POST'])
def calculate_d40():
    """API endpoint to calculate the D40 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract input data
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        result = raman_Khavedamsha_D40(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Akshavedamsha D45

@rl.route('/raman/calculate_d45', methods=['POST'])
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

        result = raman_Akshavedamsha_D45(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




#  Shashtiamsha D60


@rl.route('/raman/calculate_d60', methods=['POST'])
def calculate_d60():
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

        chart_data = raman_Shashtiamsha_D60(birth_date, birth_time, latitude, longitude, tz_offset)

        response = {
            "user_name": user_name,
            **chart_data
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




#**************************************************************************************************************
#***********************************    Lagna Charts        ***********************************************
#**************************************************************************************************************

#  Bava Lagna 

@rl.route('/raman/calculate_bhava_lagna', methods=['POST'])
def raman_bava_calculate_bhava_lagna_chart():
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

        birth_jd = raman_bava_get_julian_day(birth_date, birth_time, tz_offset)
        sunrise_jd, sunrise_sun_lon = raman_bava_calculate_sunrise(birth_jd, lat, lon, tz_offset)
        bl_lon = raman_bava_calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon)
        bl_sign, bl_degrees = raman_bava_get_sign_and_degrees(bl_lon)
        bl_nak, bl_nak_lord, bl_pada = raman_bava_nakshatra_and_pada(bl_lon)

        positions = {}
        for planet, pid in PLANET_IDS.items():
            if planet == 'Ketu':
                continue
            pos_data = swe.calc_ut(birth_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
            lon = pos_data[0] % 360
            sign, degrees = raman_bava_get_sign_and_degrees(lon)
            retrograde = 'R' if pos_data[3] < 0 else ''
            house = raman_bava_calculate_house(sign, bl_sign)
            nak, nak_lord, pada = raman_bava_nakshatra_and_pada(lon)
            positions[planet] = {
                "degrees": round(degrees, 4), "sign": sign, "retrograde": retrograde,
                "house": house, "nakshatra": nak, "nakshatra_lord": nak_lord, "pada": pada
            }

        # Calculate Ketu
        rahu_lon = positions['Rahu']['degrees'] + (SIGNS.index(positions['Rahu']['sign']) * 30)
        ketu_lon = (rahu_lon + 180) % 360
        ketu_sign, ketu_degrees = raman_bava_get_sign_and_degrees(ketu_lon)
        ketu_nak, ketu_nak_lord, ketu_pada = raman_bava_nakshatra_and_pada(ketu_lon)
        positions['Ketu'] = {
            "degrees": round(ketu_degrees, 4), "sign": ketu_sign, "retrograde": "",
            "house": raman_bava_calculate_house(ketu_sign, bl_sign),
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
        logging.error(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500



#  Hora Lagna Chart .
@rl.route('/raman/calculate_hora_lagna', methods=['POST'])
def raman_hora_calculate_hora_lagna_chart():
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

        result = raman_hora_calculate_chart(birth_date, birth_time, lat, lon, tz_offset)
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Equal Bava lagna chart :
@rl.route('/raman/calculate_equal_bhava_lagna', methods=['POST'])
def calculate_equal_bhava_lagna():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        result = raman_equal_bava_lagnas(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500




#  KP Bava Lagna 

@rl.route('/raman/calculate_kp_bhava', methods=['POST'])
def calculate_kp_bhava():
    """API endpoint to calculate KP Bhava Chart from birth details."""
    data = request.get_json()
    try:
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        result = raman_kp_bava(user_name, birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(result), 200

    except KeyError as e:
        return jsonify({"error": f"Missing input field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid input value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sripathi Bava 
@rl.route('/raman/calculate_sripathi_bhava', methods=['POST'])
def calculate_sripathi_bhava():
    """Compute the Sripathi Bhava Chart and return JSON output."""
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

        logger.debug(f"Input: Date={birth_date}, Time={birth_time}, Lat={latitude}, Lon={longitude}, TZ Offset={tz_offset}")

        # Call the calculation function
        response = raman_sripathi_bava(birth_date, birth_time, latitude, longitude, tz_offset)
        logger.debug(f"Output JSON: {response}")
        return jsonify(response), 200

    except ValueError as ve:
        logger.error(f"Invalid input format: {str(ve)}")
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Arudha Lagna chart .
@rl.route('/raman/calculate_arudha_lagna', methods=['POST'])
def calculate_arudha_lagna():
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

        response = raman_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


#  Karkamsha Birth chart 
@rl.route('/raman/calculate_karkamsha_d1', methods=['POST'])
def calculate_d1_karkamsha_endpoint():
    """API endpoint to calculate the D1 Karkamsha chart."""
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
        results = raman_karkamsha_D1(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct response
        response = {
            "user_name": user_name,
            **results
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Karkamsha D9 chart 
@rl.route('/raman/calculate_d9_karkamsha', methods=['POST'])
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
        results = raman_karkamsha_D9(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct response
        response = {
            "user_name": user_name,
            **results
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




#**************************************************************************************************************
#***********************************    Ashatakavargha Raman       ***********************************************
#**************************************************************************************************************


# Binnastakavargha
@rl.route('/raman/calculate_bhinnashtakavarga', methods=['POST'])
def calculate_raman_ashtakvarga():
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
        results = raman_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

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


#  Sarvashakavargha 
@rl.route('/raman/calculate_sarvashtakavarga', methods=['POST'])
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
        results = raman_sarvathakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

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
@rl.route('/raman/shodasha_varga_signs', methods=['POST'])
def shodasha_varga_signs():
    try:
        data = request.get_json()
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        utc_dt = raman_sign_local_to_utc(birth_date, birth_time, timezone_offset)
        jd = raman_sign_julian_day(utc_dt)

        sid_positions = raman_sign_get_sidereal_positions(jd)
        sid_asc, asc_sign_idx, asc_deg_in_sign = raman_sign_get_sidereal_asc(jd, latitude, longitude)
        sid_positions['Ascendant'] = (sid_asc, asc_sign_idx, asc_deg_in_sign)

        summary = {}
        for pname in sid_positions.keys():
            summary[pname] = {}

        for chart in CHARTS:
            for pname, (lon, sign_idx, deg_in_sign) in sid_positions.items():
                varga_idx = raman_sign_varga_sign(sign_idx, deg_in_sign, chart)
                summary[pname][chart] = {"sign": SIGNS[varga_idx]}

        return jsonify({
            "ayanamsa": "Raman",
            "shodasha_varga_signs": summary,
            "user_name": user_name
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#**************************************************************************************************************
#***********************************    Vimshottari Dashas       ***********************************************
#**************************************************************************************************************



#  Vimshottari of mahaDasha and antar dasha :

@rl.route('/raman/calculate_maha_antar_dashas', methods=['POST'])
def calculate_antardasha_dasha():
    """Calculate Vimshottari Dasha based on birth details."""
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

        birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
        jd_birth = get_julian_day_antar_raman(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_position_raman_antar(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_raman_antar(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        balance_years, elapsed_years = calculate_dasha_balance_raman_antar(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_mahadasha_periods_antar_raman(birth_datetime, lord, balance_years, elapsed_years)

        response = {
            "user_name": user_name,
            "birth_date": birth_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



#  Vimshottari of antar dasha and Pratyantardashas Dasha 

@rl.route('/raman/calculate_maha_antar_pratyantar_dasha', methods=['POST'])
def calculate_prataytar_dasha():
    """Calculate Vimshottari Dasha based on birth details."""
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

        jd_birth = get_julian_day_prataythar_raman(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_position_prataythar_raman(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_prataythar_raman(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance_prataythar_raman(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_prataythar_raman_periods(jd_birth, remaining_time, lord, elapsed_time)

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





#  Vimshottari of  Pratyantardashas Dasha  and Sookshma dasha 
@rl.route('/raman/calculate_sookshma_dasha_raman', methods=['POST'])
def calculate_sookshmadasha_dasha():
    """API endpoint to calculate Vimshottari Dasha periods."""
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

        jd_birth = get_julian_day_sookshma_raman(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_sookshma_raman(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_soo_raman(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_sookshma_dasha_balance_raman(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_sookshma_raman_periods(jd_birth, lord, elapsed_time)

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



# Vimshottari of  Prana dasha with all dash sequence.
@rl.route('/raman/calculate_raman_prana_dasha', methods=['POST'])
def calculate_prana_dasha():
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
        jd_birth = get_julian_day_pran_raman(birth_date, birth_time, tz_offset)
        
        # Calculate Moon's sidereal position
        moon_longitude = calculate_moon_sidereal_position_pran_raman(jd_birth)
        
        # Determine Nakshatra and lord
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_pran_raman(moon_longitude)
        
        # Calculate dasha balance
        remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_pran_raman(moon_longitude, nakshatra_start, lord)
        
        # Calculate all Mahadasha periods
        mahadasha_periods = calculate_pran_raman_periods(jd_birth, lord, elapsed_days)

        response = {
            "user_name": data.get('user_name', 'Unknown'),
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
