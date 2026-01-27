from asyncio.log import logger
import traceback
from flask import Blueprint, json, make_response, request, jsonify
from datetime import datetime, timedelta
import logging
# from venv import logger
import swisseph as swe

from astro_engine.engine.SriYukteswarAyanmas.Dashas.AntarDasha import maha_antar_dasha_cal
from astro_engine.engine.SriYukteswarAyanmas.Dashas.AshtottariAntarDasha import perform_ashtottari_antar_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.AshtottariPratyantardashas import ashtottari_pratyantardashas_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.DwadashottariDasha import perform_dwadashottari_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.DwisaptatisamaDasha import perform_Dwisaptatisama_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.PanchottariDasha import perform_panchottari_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.PrannaDasha import perform_dasha_calculation_pranna
from astro_engine.engine.SriYukteswarAyanmas.Dashas.PratyantardashasDasha import calcu_praPratyantardashas_yuktewar
from astro_engine.engine.SriYukteswarAyanmas.Dashas.SatabdikaDasha import perform_satabdika_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.ShastihayaniDasha import perform_shastihayani_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.ShattrimshatsamaDasha import perform_shattrimshatsama_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.ShodashottariDasha import shodashottari_dasha_calculation
from astro_engine.engine.SriYukteswarAyanmas.Dashas.SookshmaDasha import sookshma_dasha_data_cal
from astro_engine.engine.SriYukteswarAyanmas.Dashas.TribhagiDasha import tribhgi_dasha_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.ArudhaLagna import perform_arudha_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.BhavaLagna import perform_bhava_lagna_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.Binnastakavargha import perform_ashtakvarga_calculation_binna
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.EqualBhava import equal_bhava_chart
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.GatikaLagna import perform_gl_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.HoraLagna import perform_hora_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.KPBhava import perform_chart_calculation_kp
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.KarakamshaBirth import calculate_karakamsha_chart
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.KarkamshaD9 import perform_karkamsha_calculation_d9
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.MoonChart import perform_moon_chart_calculation
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.Sarvashtakvarga import  perform_sarvashtakavarga_calculation_cal
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.SripatiBhava import perform_astrology_calculation_sripathi
from astro_engine.engine.SriYukteswarAyanmas.LagnaCharts.SunChart import perform_sun_chart_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D10Dashamsha import perform_d10_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D12Dwadashamsha import perform_d12_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D16Shodashamsha import perform_d16_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D20Vimshamsha import perform_d20_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D24Chaturvimshamsha import perform_d24_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D27Saptavimshamsha import perform_d27_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D2Hora import perform_d2_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D30Trimshamsha import perform_d30_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D3Dreshkana import perform_d3_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D40Kvedamsha import perform_d40_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D45Akshavedamsha import perform_d45_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D4Chaturthamsha import perform_d4_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D60Shashtiamsha import perform_d60_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D7Saptamsha import perform_d7_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D9Navamsha import perform_d9_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.NatalD1 import natal_chart_calculation
swe.set_ephe_path('astro_engine/ephe')



sy = Blueprint('Sri_Yukteswar_Ayanamsa_routes', __name__)


# **********************************************************************************************************
#                Sri Yukteswar Ayanamsa - Shodasha Vargha Charts Routes
# **********************************************************************************************************


# D1 Calculation
@sy.route('/yukteswar/calculate_d1', methods=['POST'])
def calculate_chart_D1():
    try:
        data = request.json
        
        # Pass data to the calculation module
        response = natal_chart_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    

# D2 Calculation
@sy.route('/yukteswar/calculate_d2', methods=['POST'])
def calculate_d2():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d2_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# D3 Calculation 
@sy.route('/yukteswar/calculate_d3', methods=['POST'])
def calculate_chart_d3():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to the calculation module
        response = perform_d3_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  D4 Calculation
@sy.route('/yukteswar/calculate_d4', methods=['POST'])
def calculate_astrology_d4():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to the calculation module
        response = perform_d4_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# D7 Calculation
@sy.route('/yukteswar/calculate_d7', methods=['POST'])
def calculate_d7():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d7_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# D9 Calculation
@sy.route('/yukteswar/calculate_d9', methods=['POST'])
def calculate_chart_d9():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d9_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# # D10 Calculation
@sy.route('/yukteswar/calculate_d10', methods=['POST'])
def calculate_d10_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d10_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# D12 Calculation
@sy.route('/yukteswar/calculate_d12', methods=['POST'])
def calculate_chart_d12():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d12_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# D16 Calculation
@sy.route('/yukteswar/calculate_d16', methods=['POST'])
def calculate_chart_d16():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d16_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# D20 Calculation
@sy.route('/yukteswar/calculate_d20', methods=['POST'])
def calculate_d20_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d20_calculation(data)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# D24 Calculation
@sy.route('/yukteswar/calculate_d24', methods=['POST'])
def calculate_d24_chart():
    try:
        # Get JSON data from request
        data = request.json
        
        # Pass data to the calculation module
        response = perform_d24_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  D27 Calculation
@sy.route('/yukteswar/calculate_d27', methods=['POST'])
def calculate_d27_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to the calculation module
        response = perform_d27_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  D30 Calculation
@sy.route('/yukteswar/calculate_d30', methods=['POST'])
def calculate_d30_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d30_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500




#  D40 Calculation
@sy.route('/yukteswar/calculate_d40', methods=['POST'])
def handle_calc_D40():
    try:
        data = request.json
        # Call the calculation logic
        response = perform_d40_calculation(data)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



#  D45 Calculation
@sy.route('/yukteswar/calculate_d45', methods=['POST'])
def calculate_d45_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d45_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  D60 Calculation
@sy.route('/yukteswar/calculate_d60', methods=['POST'])
def calculate_d60_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_d60_calculation(data)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# **********************************************************************************************************
#                Sri Yukteswar Ayanamsa - Lagna Charts Routes   
# **********************************************************************************************************



#  Sunya Lagna (Sun Chart) Calculation
@sy.route('/yukteswar/calculate_sun_chart', methods=['POST'])
def calculate_sun_chart():
    try:
        # 1. Parse Input
        data = request.get_json()
        
        # 2. Perform Calculation via Logic Module
        response = perform_sun_chart_calculation(data)
        
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Moon Chart Calculation
@sy.route('/yukteswar/calculate_moon_chart', methods=['POST'])
def calculate_moon_chart():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_moon_chart_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Sripathi Bhava Calculation
@sy.route('/yukteswar/calculate_Sripati_Bhava', methods=['POST'])
def calculate_astrology_sripathi():
    try:
        # Get JSON data
        data = request.get_json()
        
        # Pass data to the calculation module
        response = perform_astrology_calculation_sripathi(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#  Equal Bhava Calculation
@sy.route('/yukteswar/calculate_equal_chart', methods=['POST'])
def calculate_chart_route_Equal():
    try:
        data = request.json
        
        # Parse Input
        user_name = data.get("user_name")
        birth_date = data.get("birth_date")
        birth_time = data.get("birth_time")
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        tz = float(data.get("timezone_offset"))
        
        # Call calculation function
        result = equal_bhava_chart(user_name, birth_date, birth_time, lat, lon, tz)
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  KP Bhava Calculation
@sy.route('/yukteswar/calculate_kp_bhava', methods=['POST'])
def calculate_chart_kp():
    try:
        data = request.get_json()
        
        # Call the calculation logic from the other file
        response = perform_chart_calculation_kp(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500


# Arudha Lagna Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_arudha_lagna', methods=['POST'])
def calculate_arudha_lagna():
    try:
        data = request.get_json()
        
        # Call the calculation logic from the other file
        response = perform_arudha_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Karakamsha Birth Chart Calculation
@sy.route('/yukteswar/calculate_karakamsha_birth', methods=['POST'])
def calculate_karakamsha():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No input data"}), 400
        
        # Pass data to the calculation module
        result = calculate_karakamsha_chart(data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# Karkamsha D9 Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_karkamsha_d9', methods=['POST'])
def calculate_karkamsha_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Pass data to the calculation module
        result = perform_karkamsha_calculation_d9(data)
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Bhava Lagna Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_bhava_lagna', methods=['POST'])
def calculate_bhava_lagna():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_bhava_lagna_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Hora Lagna Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_hora_lagna', methods=['POST'])
def calculate_hora_lagna():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_hora_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


#  Gatika Lagna Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_gl_chart', methods=['POST'])
def calculate_gl_chart():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Call the calculation logic
        response = perform_gl_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# *****************************************************************************************************************
#                Sri Yukteswar Ayanamsa - Ashtakvarga Charts Routes
# *****************************************************************************************************************


# Binnastana Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_binnashtakvarga_chart', methods=['POST'])
def calculate_binnashtakvarga_cal():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Pass data to calculation module
        response = perform_ashtakvarga_calculation_binna(data)
        
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Sarvashtakvarga Calculation Logic (Used by multiple charts)
@sy.route('/yukteswar/calculate_sarvashtakvarga_chart', methods=['POST'])
def calculate_sarvashtakvarga_cal():
    """API endpoint to calculate Sarvashtakvarga with matrix table based on birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Pass data to calculation module
        response = perform_sarvashtakavarga_calculation_cal(data)
        
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# **********************************************************************************************************
#  Vimshottari Dasa Calculation Route for Sri Yukteswar Ayanamsa
# **********************************************************************************************************


# Anatara Dasa Calculation Route
@sy.route('/yukteswar/calculate_mahaantar_dasha', methods=['POST'])
def calculate_chart_antar_dasha():
    try:
        data = request.json
        
        # Extract inputs from request
        name = data.get('user_name')
        b_date = data.get('birth_date')
        b_time = data.get('birth_time')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        tz = float(data.get('timezone_offset'))
        
        # Pass inputs to the calculation engine
        response_data = maha_antar_dasha_cal(name, b_date, b_time, lat, lon, tz)
        
        # Return the result
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Pratyantardashas Dasha Calculation Logic
@sy.route('/yukteswar/calculate_pratyantar_dasha', methods=['POST'])
def calculate_Pratyantardashas_cal():
    try:
        data = request.json
        
        # Extract inputs
        user_name = data.get("user_name")
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        tz_offset = float(data.get("timezone_offset"))
        date_str = data.get("birth_date")
        time_str = data.get("birth_time")
        
        # Call the separated engine
        response_data = calcu_praPratyantardashas_yuktewar(
            user_name, lat, lon, tz_offset, date_str, time_str
        )
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Sookshma Dasha Calculation Logic
@sy.route('/yukteswar/calculate_sookshma_dasha', methods=['POST'])
def calculate_sookshma_dasha():
    try:
        data = request.json
        
        # Extract inputs
        user_name = data.get("user_name")
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
        tz_offset = float(data.get("timezone_offset"))
        
        date_str = data.get("birth_date")
        time_str = data.get("birth_time")
        
        # Call the separated engine
        # Now calls the function that includes Sookshma dasha logic
        response_data = sookshma_dasha_data_cal(
            user_name, lat, lon, tz_offset, date_str, time_str
        )
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Prana dasha Calculation Logic
@sy.route('/yukteswar/calculate_prana_dasha', methods=['POST'])
def calculate_prana_dasha():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_dasha_calculation_pranna(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#  Ashtottari antar dasha calculation logic
@sy.route('/yukteswar/calculate_ashtottari_antar', methods=['POST'])
def calculate_ashtottari_antar():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON"}), 400

        # Pass data to calculation module
        response = perform_ashtottari_antar_calculation(data)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Ashtottari pratyantardasha calculation logic
@sy.route('/yukteswar/calculate_ashtottari_pratyantardasha', methods=['POST'])
def calculate_ashtottari_pratyantardashas():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON"}), 400

        # Pass data to calculation module
        response = ashtottari_pratyantardashas_calculation(data)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# Tribhgina Dasha Calculation Logic
@sy.route('/yukteswar/calculate_tribhgi_dasha', methods=['POST'])
def calculate_tribhgi_dasha():
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = tribhgi_dasha_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        # Return exact python error for debugging
        return jsonify({"error": str(e)}), 500



#  Shodashottari Dasha Calculation Logic
@sy.route('/yukteswar/calculate_shodashottari_dasha', methods=['POST'])
def calculate_shodashottari_dasha():
    try:
        data = request.json
        
        # Pass data to calculation module
        response = shodashottari_dasha_calculation(data)
        
        return jsonify(response)
        
    except Exception as e:
        # It's good practice to print the error to server logs for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


#  Dwadashottari Dasha Calculation Logic
@sy.route('/yukteswar/calculate_dwadashottari', methods=['POST'])
def calculate_dwadashottari_dasha():
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = perform_dwadashottari_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        # Return error details for debugging
        return jsonify({"error": str(e)}), 500


# Dwisaptatisama Dasha Calculation Logic
@sy.route('/yukteswar/calculate_dwisaptatisama', methods=['POST'])
def calculate_dwisaptatisama():
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = perform_Dwisaptatisama_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        # Return exact python error for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# Shastihayani Dasha Calculation Logic
@sy.route('/yukteswar/calculate_shastihayani', methods=['POST'])
def calculate_shastihayani():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = perform_shastihayani_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


#  Shattrimshatsama Dasha Calculation Logic
@sy.route('/yukteswar/calculate_shattrimshatsama', methods=['POST'])
def calculate_dasha_shattrimshatsama():
    try:
        # Get JSON data
        data = request.json
        
        # Pass data to calculation module
        response = perform_shattrimshatsama_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500


# Panchottari Dasha Calculation Logic
@sy.route('/yukteswar/calculate_panchottari', methods=['POST'])
def calculate_panchottari_dasha():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = perform_panchottari_calculation(data)
        
        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# Satabdika Dasha Calculation Logic
@sy.route('/yukteswar/calculate_satabdika', methods=['POST'])
def calculate_satabdika_dasha():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Pass data to calculation module
        response = perform_satabdika_calculation(data)
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


