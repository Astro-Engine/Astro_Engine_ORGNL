from asyncio.log import logger
import traceback
from flask import Blueprint, json, make_response, request, jsonify
from datetime import datetime, timedelta
import logging
# from venv import logger
import swisseph as swe

from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.D2Hora import perform_d2_calculation
from astro_engine.engine.SriYukteswarAyanmas.ShodashaVarghaCharts.NatalD1 import natal_chart_calculation
swe.set_ephe_path('astro_engine/ephe')



sy = Blueprint('Sri_Yukteswar_Ayanamsa_routes', __name__)




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





