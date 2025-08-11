
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger

from astro_engine.engine.numerology.CompositeChart import composite
from astro_engine.engine.numerology.ProgressChart import progressed
from astro_engine.engine.numerology.SynatryChart import synastry






ws = Blueprint('ws_routes', __name__)




#  Synatry Chart
@ws.route('/western/synastry', methods=['POST'])
def synastry_endpoint():
    data = request.get_json()
    if not data or 'person_a' not in data or 'person_b' not in data:
        return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

    try:
        response = synastry(data['person_a'], data['person_b'])
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in synastry calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400




# Composite Chart

@ws.route('/western/composite', methods=['POST'])
def composite_chart():
    data = request.get_json()
    if not data or 'person_a' not in data or 'person_b' not in data:
        return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

    try:
        reference_date = data.get('reference_date')
        reference_time = data.get('reference_time')
        response = composite(data['person_a'], data['person_b'], reference_date, reference_time)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in composite chart calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400



# Progressed Chart

@ws.route('/western/progressed', methods=['POST'])
def progressed_chart():
    data = request.get_json()
    if not data or 'person' not in data:
        return jsonify({'error': 'Person data must be provided'}), 400

    try:
        response = progressed(data['person'])
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in progressed chart calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400



