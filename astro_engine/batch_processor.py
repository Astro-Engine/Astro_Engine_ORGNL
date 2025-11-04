"""
Batch Request Processor for Astro Engine
Phase 20: Batch Request Support

Allows multiple calculations in a single request.

Benefits:
- Reduced HTTP overhead (one request instead of many)
- Transactional processing (all or partial success)
- Better for mobile clients (fewer round trips)

Limitations:
- Maximum 10 requests per batch
- Total batch size under 1 MB
- Synchronous processing (not queued)
"""

import logging
from typing import List, Dict, Any
from flask import current_app, jsonify, request

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 20, MODULE 20.1 & 20.2: BATCH PROCESSING
# =============================================================================

def process_batch_requests(requests: List[Dict[str, Any]], max_batch_size: int = 10) -> Dict[str, Any]:
    """
    Process multiple calculation requests in batch

    Phase 20, Module 20.1-20.2: Batch endpoint implementation

    Args:
        requests: List of request objects
        max_batch_size: Maximum requests per batch

    Returns:
        dict: Batch results with individual statuses

    Request Format:
        [
            {
                "type": "natal",
                "data": {birth_data}
            },
            {
                "type": "navamsa",
                "data": {birth_data}
            }
        ]

    Response Format:
        {
            "batch_id": "abc-123",
            "total_requests": 2,
            "successful": 2,
            "failed": 0,
            "results": [
                {"status": "success", "type": "natal", "data": {...}},
                {"status": "success", "type": "navamsa", "data": {...}}
            ]
        }
    """
    import uuid

    # Phase 20, Module 20.4: Batch size validation
    if len(requests) > max_batch_size:
        raise ValueError(f"Batch size exceeds limit. Maximum: {max_batch_size}, Requested: {len(requests)}")

    if len(requests) == 0:
        raise ValueError("Batch cannot be empty")

    batch_id = str(uuid.uuid4())
    results = []
    successful_count = 0
    failed_count = 0

    logger.info(f"Processing batch request: {batch_id} ({len(requests)} items)")

    # Phase 20, Module 20.2: Process each request
    for index, req in enumerate(requests):
        # FIX: Handle null items
        if req is None:
            logger.warning(f"Batch item {index} is null")
            results.append({
                'index': index,
                'type': 'unknown',
                'status': 'failed',
                'error': {'message': 'Batch item is null', 'type': 'ValueError'}
            })
            failed_count += 1
            continue

        req_type = req.get('type', 'unknown')
        req_data = req.get('data', {})

        try:
            # CRITICAL: Validate each batch item's data before processing
            from astro_engine.schemas.birth_data import BirthDataSchema
            from pydantic import ValidationError

            try:
                # Validate birth data
                validated_data = BirthDataSchema(**req_data)
                req_data = validated_data.to_dict()

            except ValidationError as e:
                # Validation failed for this batch item
                raise ValueError(f"Validation error: {e.errors()[0]['msg']}")

            # Process based on type
            result_data = process_single_calculation(req_type, req_data)

            # Phase 20, Module 20.3: Partial success handling
            results.append({
                'index': index,
                'type': req_type,
                'status': 'success',
                'data': result_data
            })
            successful_count += 1

        except Exception as e:
            # Phase 20, Module 20.3: Handle individual failures
            logger.warning(f"Batch item {index} failed: {e}")

            results.append({
                'index': index,
                'type': req_type,
                'status': 'failed',
                'error': {
                    'message': str(e),
                    'type': e.__class__.__name__
                }
            })
            failed_count += 1

    # Return batch results
    return {
        'batch_id': batch_id,
        'total_requests': len(requests),
        'successful': successful_count,
        'failed': failed_count,
        'results': results,
        'processing_time': 'synchronous'  # Could add timing
    }


def process_single_calculation(calc_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single calculation

    Args:
        calc_type: Type of calculation (natal, navamsa, etc.)
        data: Birth data

    Returns:
        dict: Calculation result

    Supported types:
        - natal
        - navamsa
        - transit
        - (can be extended)
    """
    # Import core calculation functions and helpers
    # Use the underlying calculation functions (not Flask view wrappers)
    from astro_engine.engine.natalCharts.natal import lahairi_natal, longitude_to_sign, format_dms
    from astro_engine.engine.divisionalCharts.NavamshaD9 import lahairi_navamsha_chart

    # Helper: unify formatting for natal-style responses
    def _format_natal_style(chart_data: Dict[str, Any], input_data: Dict[str, Any], chart_type_name: str) -> Dict[str, Any]:
        """Return a natal-style JSON for chart_data coming from various calculation functions.

        - chart_data may contain either 'planet_positions' (natal) or 'planets' (divisional) keys.
        - If individual planet entries include 'lon' we convert to sign/DMS using longitude_to_sign/format_dms.
        - If entries already include 'sign' and 'degree' we map those to the same output shape.
        """
        # Normalize common return shapes: some divisional calculators return
        # a dict, others return tuples like (natal_positions, divisional_positions)
        if not isinstance(chart_data, dict) and isinstance(chart_data, (list, tuple)):
            # prefer the second element if it looks like divisional positions
            if len(chart_data) >= 2 and isinstance(chart_data[1], dict):
                chart_data = chart_data[1]
            elif len(chart_data) >= 1 and isinstance(chart_data[0], dict):
                chart_data = chart_data[0]
            else:
                # fallback: wrap raw in a dict
                chart_data = {'planets': chart_data}

        # decide where planets live
        # Some divisional calculators return the planets dict directly (keys = 'Sun','Moon',...,'Ascendant')
        possible_planet_container = None
        if isinstance(chart_data, dict):
            if 'planet_positions' in chart_data or 'planetary_positions' in chart_data or 'planets' in chart_data:
                possible_planet_container = chart_data.get('planet_positions') or chart_data.get('planetary_positions') or chart_data.get('planets')
            else:
                # Heuristic: if top-level keys look like planet names, treat chart_data as the planets mapping
                sample_keys = set(chart_data.keys())
                known_planets = {'Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu','Ascendant'}
                if sample_keys & known_planets:
                    possible_planet_container = chart_data

        raw_planets = possible_planet_container or {}

        # If ascendant was included inside the planets mapping (e.g., calculators that return planets dict),
        # extract it here so ascendant handling below can process it uniformly.
        asc_from_planets = None
        if isinstance(raw_planets, dict):
            # prefer 'Ascendant' then 'ascendant'
            if 'Ascendant' in raw_planets:
                asc_from_planets = raw_planets.pop('Ascendant')
            elif 'ascendant' in raw_planets:
                asc_from_planets = raw_planets.pop('ascendant')

        # Decide if this is a D2/Hora-style divisional where positions use d2_* keys
        is_d2 = chart_type_name and isinstance(chart_type_name, str) and chart_type_name.lower() in ('hora', 'd2')
        # Some calculators don't set chart_type_name; also detect from data presence
        if not is_d2:
            # if any planet entry contains a d2_degree or the ascendant has d2_ keys, treat as D2
            sample_planet = next(iter(raw_planets.values()), None)
            if sample_planet and (sample_planet.get('d2_degree') is not None or sample_planet.get('d2_sign') is not None):
                is_d2 = True

        planetary_positions_json = {}
        for planet, pdata in raw_planets.items():
            if not isinstance(pdata, dict):
                planetary_positions_json[planet] = {'raw': pdata}
            #     continue

            # if is_d2:
            #     # D2/Hora divisional outputs typically include d2_sign/d2_degree or already 'sign'/'degree' mapped to D2
            #     sign = pdata.get('sign') or pdata.get('d2_sign') or pdata.get('natal_sign')
            #     deg = (pdata.get('degree') or pdata.get('degrees') or pdata.get('deg') or
            #               pdata.get('natal_degree') or pdata.get('natal_degrees') or pdata.get('natal_deg') or
            #               pdata.get('d2_degree') or pdata.get('d2_degrees') or pdata.get('d2_deg') or
            #               pdata.get('decimal_degree') or pdata.get('degree_decimal') or
            #               pdata.get('longitude_decimal') or pdata.get('decimal_longitude') or
            #               pdata.get('longitude_degrees') or pdata.get('degree_longitude'))
            #     # D2 does not calculate houses per-planet in this implementation; keep None unless provided
            #     house_val = pdata.get('house') if pdata.get('house') is not None else None
            
            else:
                # Natal-style: prefer absolute sign/degree or convert from longitude when available
                sign = pdata.get('sign') or pdata.get('natal_sign') or pdata.get('d2_sign')
                deg = (pdata.get('degree') or pdata.get('degrees') or pdata.get('deg') or
                          pdata.get('natal_degree') or pdata.get('natal_degrees') or pdata.get('natal_deg') or
                          pdata.get('d2_degree') or pdata.get('d2_degrees') or pdata.get('d2_deg') or
                          pdata.get('decimal_degree') or pdata.get('degree_decimal') or
                          pdata.get('longitude_decimal') or pdata.get('decimal_longitude') or
                          pdata.get('longitude_degrees') or pdata.get('degree_longitude'))
                # Natal charts may include houses mapping at top-level
                house_val = pdata.get('house') if pdata.get('house') is not None else chart_data.get('planet_houses', {}).get(planet)

            # Robust degree handling:
            # - If degree is numeric (int/float) or numeric string -> convert and format
            # - If degree is already a formatted DMS string (contains ° or ' or \"), keep as-is
            # - If degree missing but 'lon' exists, derive sign/deg via longitude_to_sign
            deg_val = None
            dms = None
            if deg is not None:
                if isinstance(deg, (int, float)):
                    deg_val = float(deg)
                    dms = format_dms(deg_val)
                elif isinstance(deg, str):
                    # already formatted DMS (e.g. "6° 41' 41.06\"")?
                    if '°' in deg or "'" in deg or '"' in deg:
                        dms = deg
                    else:
                        try:
                            deg_val = float(deg)
                            dms = format_dms(deg_val)
                        except Exception:
                            # leave dms None (we'll try lon fallback below)
                            dms = None

            # If no degree found yet, but absolute longitude available, derive sign/deg
            if dms is None:
                lon_val = pdata.get('lon') or pdata.get('longitude') or pdata.get('longitude_deg')
                if lon_val is not None:
                        lon_val = (pdata.get('lon') or pdata.get('longitude') or pdata.get('longitude_deg') or
                                  pdata.get('long') or pdata.get('lng') or
                                  pdata.get('absolute_longitude') or pdata.get('total_longitude') or
                                  pdata.get('longitude_absolute') or pdata.get('longitude_total') or
                                  pdata.get('longitude_decimal') or pdata.get('decimal_longitude') or
                                  pdata.get('longitude_degrees') or pdata.get('degrees_longitude') or
                                  pdata.get('degree_longitude') or pdata.get('degree_absolute'))
                        if lon_val is not None:
                            try:
                                # longitude_to_sign returns (sign, deg_within_sign)
                                derived_sign, derived_deg = longitude_to_sign(float(lon_val))
                                # if sign wasn't set earlier, prefer derived_sign
                                if not sign:
                                    sign = derived_sign
                                dms = format_dms(derived_deg)
                            except Exception:
                                dms = None

            planetary_positions_json[planet] = {
                'sign': sign,
                'degrees': dms,
                'retrograde': pdata.get('retrograde') or pdata.get('retro') or pdata.get('retrograde', ''),
                'house': house_val,
                'nakshatra': pdata.get('nakshatra'),
                'pada': pdata.get('pada')
            }

        # Ascendant handling (outside planet loop)
        asc = asc_from_planets or chart_data.get('ascendant') or {}
        if is_d2:
            asc_sign = asc.get('d2_sign') or asc.get('sign') or asc.get('natal_sign')
            asc_deg_val = asc.get('d2_degree') or asc.get('degree') or asc.get('degrees') or asc.get('natal_degree') or asc.get('lon') or asc.get('longitude')
            # If no degree available, try longitude aliases; otherwise format numeric degree
            if asc_deg_val is None:
                lon_val = asc.get('lon') or asc.get('longitude') or asc.get('longitude_deg')
                if lon_val is not None:
                    try:
                        asc_sign, asc_deg = longitude_to_sign(lon_val)
                        asc_dms = format_dms(asc_deg) if asc_deg is not None else None
                    except Exception:
                        asc_dms = None
                else:
                    asc_dms = None
            else:
                try:
                    asc_deg_val = float(asc_deg_val)
                    asc_dms = format_dms(asc_deg_val)
                except Exception:
                    asc_dms = None
            ascendant_json = {
                'sign': asc_sign,
                'degrees': asc_dms,
                'nakshatra': asc.get('nakshatra'),
                'pada': asc.get('pada'),
                'house': asc.get('house', 1)
            }
        else:
            lon_val = (asc.get('lon') or asc.get('longitude') or asc.get('longitude_deg') or
                      asc.get('long') or asc.get('lng') or
                      asc.get('absolute_longitude') or asc.get('total_longitude') or
                      asc.get('longitude_absolute') or asc.get('longitude_total') or
                      asc.get('longitude_decimal') or asc.get('decimal_longitude') or
                      asc.get('longitude_degrees') or asc.get('degrees_longitude'))
            if lon_val is not None:
                asc_sign, asc_deg = longitude_to_sign(lon_val)
                asc_dms = format_dms(asc_deg) if asc_deg is not None else None
                ascendant_json = {
                    'sign': asc_sign,
                    'degrees': asc_dms,
                    'nakshatra': asc.get('nakshatra'),
                    'pada': asc.get('pada'),
                    'house': asc.get('house', 1)
                }
            else:
                asc_sign = (asc.get('sign') or asc.get('natal_sign') or asc.get('d2_sign') or
                           asc.get('rasi') or asc.get('natal_rasi') or asc.get('d2_rasi'))
                asc_deg_val = (asc.get('degree') or asc.get('degrees') or asc.get('deg') or
                              asc.get('natal_degree') or asc.get('natal_degrees') or asc.get('natal_deg') or
                              asc.get('d2_degree') or asc.get('d2_degrees') or asc.get('d2_deg') or
                              asc.get('decimal_degree') or asc.get('degree_decimal') or
                              asc.get('longitude_decimal') or asc.get('decimal_longitude'))
                try:
                    asc_deg_val = float(asc_deg_val) if asc_deg_val is not None else None
                    asc_dms = format_dms(asc_deg_val) if asc_deg_val is not None else None
                except Exception:
                    asc_dms = None
                ascendant_json = {
                    'sign': asc_sign,
                    'degrees': asc_dms,
                    'nakshatra': asc.get('nakshatra'),
                    'pada': asc.get('pada'),
                    'house': asc.get('house', 1)
                }

        response = {
            'user_name': input_data.get('user_name'),
            'birth_details': {
                'birth_date': input_data.get('birth_date'),
                'birth_time': input_data.get('birth_time'),
                'latitude': float(input_data.get('latitude')) if input_data.get('latitude') is not None else None,
                'longitude': float(input_data.get('longitude')) if input_data.get('longitude') is not None else None,
                'timezone_offset': float(input_data.get('timezone_offset')) if input_data.get('timezone_offset') is not None else None
            },
            'planetary_positions': planetary_positions_json,
            'ascendant': ascendant_json,
            'notes': {
                'ayanamsa': 'Lahiri',
                'ayanamsa_value': f"{chart_data.get('ayanamsa_value', 0):.6f}" if chart_data.get('ayanamsa_value') is not None else None,
                'chart_type': chart_type_name,
                'house_system': 'Whole Sign'
            }
        }

        return response


    # Route to appropriate calculation
    if calc_type == 'natal':
        # Calculate raw chart data
        chart_data = lahairi_natal(data)

        # Format planetary positions exactly like the `/lahiri/natal` endpoint
        planetary_positions_json = {}
        for planet, pdata in chart_data.get('planet_positions', {}).items():
            lon = pdata.get('lon')
            retro = pdata.get('retro')
            nak = pdata.get('nakshatra')
            pada = pdata.get('pada')

            sign, sign_deg = longitude_to_sign(lon)
            dms = format_dms(sign_deg)
            house = chart_data.get('planet_houses', {}).get(planet)

            planetary_positions_json[planet] = {
                'sign': sign,
                'degrees': dms,
                'retrograde': retro,
                'house': house,
                'nakshatra': nak,
                'pada': pada
            }

        # Ascendant formatting
        asc = chart_data.get('ascendant', {})
        asc_sign, asc_deg = longitude_to_sign(asc.get('lon', 0))
        asc_dms = format_dms(asc_deg)
        ascendant_json = {
            'sign': asc_sign,
            'degrees': asc_dms,
            'nakshatra': asc.get('nakshatra'),
            'pada': asc.get('pada')
        }

        # Build the final response matching the route's structure
        response = {
            'user_name': data.get('user_name'),
            'birth_details': {
                'birth_date': data.get('birth_date'),
                'birth_time': data.get('birth_time'),
                'latitude': float(data.get('latitude')) if data.get('latitude') is not None else None,
                'longitude': float(data.get('longitude')) if data.get('longitude') is not None else None,
                'timezone_offset': float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else None
            },
            'planetary_positions': planetary_positions_json,
            'ascendant': ascendant_json,
            'notes': {
                'ayanamsa': 'Lahiri',
                'ayanamsa_value': f"{chart_data.get('ayanamsa_value', 0):.6f}",
                'chart_type': 'Rasi',
                'house_system': 'Whole Sign'
            }
        }

        return response


    # D2 Hora (divisional example)
    if calc_type == 'd2' or calc_type == 'hora':
        from astro_engine.engine.divisionalCharts.HoraD2 import lahairi_hora_chart
        try:
            # First try with explicit parameters
            chart_data = lahairi_hora_chart(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )

            # Convert Response object to dict if necessary
            if hasattr(chart_data, 'get_json'):
                chart_data = chart_data.get_json()
            elif hasattr(chart_data, 'json'):
                chart_data = chart_data.json
                
            # Ensure chart_data is a dictionary
            if not isinstance(chart_data, dict):
                if isinstance(chart_data, (list, tuple)) and len(chart_data) >= 2:
                    chart_data = chart_data[1]  # Use the second element which typically contains D2 positions
                else:
                    chart_data = {'planets': chart_data}

        except Exception as e1:
            try:
                # Fall back to standard interface
                chart_data = lahairi_hora_chart(data)
                
                # Convert Response object to dict if necessary
                if hasattr(chart_data, 'get_json'):
                    chart_data = chart_data.get_json()
                elif hasattr(chart_data, 'json'):
                    chart_data = chart_data.json
                    
            except Exception as e2:
                # If both attempts fail, return structured error response
                chart_data = {
                    'planetary_positions': {},
                    'planets': {},
                    'error': f"D2 calculation failed: {str(e2)}",
                    'ayanamsa_value': None
                }

        # Format response using the same structure as natal chart
        response = {
            'user_name': data.get('user_name'),
            'birth_details': {
                'birth_date': data.get('birth_date'),
                'birth_time': data.get('birth_time'),
                'latitude': float(data.get('latitude')) if data.get('latitude') is not None else None,
                'longitude': float(data.get('longitude')) if data.get('longitude') is not None else None,
                'timezone_offset': float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else None
            },
            'planetary_positions': chart_data.get('planetary_positions', {}) or chart_data.get('planets', {}),
            'ascendant': chart_data.get('ascendant', {}) if isinstance(chart_data.get('ascendant'), dict) else {},
            'notes': {
                'ayanamsa': 'Lahiri',
                'ayanamsa_value': f"{chart_data.get('ayanamsa_value', 0):.6f}" if chart_data.get('ayanamsa_value') is not None else None,
                'chart_type': 'Hora (D2)',
                'house_system': 'Whole Sign',
                'error': chart_data.get('error')
            }
        }
        return response


    # NAVAMSA (divisional D9)
    if calc_type == 'navamsa' or calc_type == 'd9':
        chart_data = lahairi_navamsha_chart(data)
        return _format_natal_style(chart_data, data, 'Navamsa')

    # D3 Dreshkana
    if calc_type == 'd3' or calc_type == 'dreshkana':
        from astro_engine.engine.divisionalCharts.DreshkanaD3 import lahairi_drerkhana
        try:
            chart_data = lahairi_drerkhana(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_drerkhana(data)
        return _format_natal_style(chart_data, data, 'Dreshkana')

    # D4 Chathruthamsha
    if calc_type == 'd4' or calc_type == 'chathruthamsha':
        from astro_engine.engine.divisionalCharts.ChathruthamshaD4 import lahairi_Chaturthamsha
        try:
            chart_data = lahairi_Chaturthamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Chaturthamsha(data)
        return _format_natal_style(chart_data, data, 'Chathruthamsha')

    # D7 Saptamsha
    if calc_type == 'd7' or calc_type == 'saptamsha':
        from astro_engine.engine.divisionalCharts.SaptamshaD7 import lahairi_saptamsha
        try:
            chart_data = lahairi_saptamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_saptamsha(data)
        return _format_natal_style(chart_data, data, 'Saptamsha')

    # D10 Dashamsha
    if calc_type == 'd10' or calc_type == 'dashamsha':
        from astro_engine.engine.divisionalCharts.DashamshaD10 import lahairi_Dashamsha
        try:
            chart_data = lahairi_Dashamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Dashamsha(data)
        return _format_natal_style(chart_data, data, 'Dashamsha')

    # D12 Dwadasamsa
    if calc_type == 'd12' or calc_type == 'dwadashamsha':
        from astro_engine.engine.divisionalCharts.DwadashamshaD12 import lahairi_Dwadashamsha
        try:
            chart_data = lahairi_Dwadashamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Dwadashamsha(data)
        return _format_natal_style(chart_data, data, 'Dwadasamsa')

    # D16 Shodasamsa
    if calc_type == 'd16' or calc_type == 'shodasamsa' or calc_type == 'shodashamsha':
        from astro_engine.engine.divisionalCharts.ShodasmasD16 import lahairi_Shodashamsha
        try:
            chart_data = lahairi_Shodashamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Shodashamsha(data)
        return _format_natal_style(chart_data, data, 'Shodasamsa')

    # D24 Chaturvimshamsha
    if calc_type == 'd24' or calc_type == 'chaturvimshamsha' or calc_type == 'chaturthamsha':
        from astro_engine.engine.divisionalCharts.ChaturvimshamshaD24 import lahairi_Chaturvimshamsha
        try:
            chart_data = lahairi_Chaturvimshamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Chaturvimshamsha(data)
        return _format_natal_style(chart_data, data, 'Chaturvimshamsha')

    # # D27 Saptavimshamsha
    if calc_type == 'd27' or calc_type == 'saptavimshamsha':
        from astro_engine.engine.divisionalCharts.SaptavimshamshaD27 import lahairi_d27
        try:
            chart_data = lahairi_d27(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_d27(data)
        return _format_natal_style(chart_data, data, 'Dreshkana')

    # D30 Trimshamsha
    if calc_type == 'd30' or calc_type == 'trimshamsha':
        try:
            from astro_engine.engine.divisionalCharts.TrimshamshaD30 import lahiri_trimshamsha_D30
            # some implementations return (natal, d30) or (positions, d30)
            chart_data = lahiri_trimshamsha_D30(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except Exception:
            try:
                from astro_engine.engine.divisionalCharts.TrimshamshaD30 import lahiri_trimshamsha_D30
                chart_data = lahiri_trimshamsha_D30(data)
            except Exception:
                chart_data = {'planetary_positions': {}}
        return _format_natal_style(chart_data, data, 'Trimshamsha')

    # D40 Kvedamsha/Khavedamsha
    if calc_type == 'd40' or calc_type == 'kvedamsha' or calc_type == 'khavedamsha':
        from astro_engine.engine.divisionalCharts.KvedamshaD40 import lahairi_Khavedamsha
        try:
            chart_data = lahairi_Khavedamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0
            )
        except TypeError:
            chart_data = lahairi_Khavedamsha(data)
        return _format_natal_style(chart_data, data, 'Kvedamsha')

    # D20 Vimshamsha
    if calc_type == 'd20' or calc_type == 'vimshamsha' or calc_type == 'vimsamsa':
        from astro_engine.engine.divisionalCharts.VimshamshaD20 import lahairi_Vimshamsha
        try:
            chart_data = lahairi_Vimshamsha(
                data.get('birth_date'),
                data.get('birth_time'),
                float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0,
                data.get('user_name', 'Unknown')
            )
            return _format_natal_style(chart_data, data, 'Vimshamsha')
        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate D20 chart: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }

    # D45 Akshavedamsha
    if calc_type == 'd45' or calc_type == 'akshavedamsha':
        from astro_engine.engine.divisionalCharts.AkshavedamshaD45 import lahairi_Akshavedamsha
        try:
            chart_data = lahairi_Akshavedamsha(
                birth_date=data.get('birth_date'),
                birth_time=data.get('birth_time'),
                latitude=float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                longitude=float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                tz_offset=float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0,
                user_name=data.get('user_name', 'Unknown')
            )
            return _format_natal_style(chart_data, data, 'Akshavedamsha')
        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate D45 chart: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }

    # D60 Shashtiamsha
    if calc_type == 'd60' or calc_type == 'shashtiamsha':
        from astro_engine.engine.divisionalCharts.ShashtiamshaD60 import lahairi_Shashtiamsha
        try:
            chart_data = lahairi_Shashtiamsha(
                birth_date=data.get('birth_date'),
                birth_time=data.get('birth_time'),
                latitude=float(data.get('latitude')) if data.get('latitude') is not None else 0.0,
                longitude=float(data.get('longitude')) if data.get('longitude') is not None else 0.0,
                tz_offset=float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else 0.0,
                user_name=data.get('user_name', 'Unknown')
            )
            return _format_natal_style(chart_data, data, 'Shashtiamsha')
        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate D60 chart: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }

    # Transit calculation
    if calc_type == 'transit':
        from astro_engine.engine.natalCharts.transit import lahairi_tranist
        from datetime import datetime, timezone
        try:
            # Ensure required fields exist
            required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValueError(f"Missing required field: {field}")
            
            chart_data = lahairi_tranist(data)
            
            # Check if we got a valid response with positions
            if not isinstance(chart_data, dict):
                raise ValueError("Invalid transit calculation result")
                
            if 'transit_positions' in chart_data:
                # Normalize transit_positions to match natal format
                positions = {}
                for planet, pos in chart_data['transit_positions'].items():
                    positions[planet] = {
                        'sign': pos.get('sign'),
                        'degrees': pos.get('degrees'),
                        'retrograde': pos.get('retrograde', ''),
                        'house': pos.get('house'),
                        'nakshatra': pos.get('nakshatra'),
                        'pada': pos.get('pada')
                    }
                    
                # Build natal-style response
                response = {
                    'user_name': data.get('user_name'),
                    'birth_details': {
                        'birth_date': data.get('birth_date'),
                        'birth_time': data.get('birth_time'),
                        'latitude': float(data.get('latitude')),
                        'longitude': float(data.get('longitude')),
                        'timezone_offset': float(data.get('timezone_offset'))
                    },
                    'planetary_positions': positions,
                    'ascendant': chart_data.get('natal_ascendant', {}),
                    'notes': {
                        'ayanamsa': 'Lahiri',
                        'ayanamsa_value_birth': chart_data.get('notes', {}).get('ayanamsa_value_birth'),
                        'ayanamsa_value_transit': chart_data.get('notes', {}).get('ayanamsa_value_transit'),
                        'chart_type': 'Transit',
                        'house_system': 'Whole Sign',
                        'transit_time': chart_data.get('transit_time')
                    }
                }
                return response
            
            return _format_natal_style(chart_data, data, 'Transit')
            
        except Exception as e:
            # Return empty response with error
            current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            error_data = {
                'planetary_positions': {},
                'ascendant': {},
                'notes': {
                    'ayanamsa': 'Lahiri',
                    'chart_type': 'Transit',
                    'house_system': 'Whole Sign',
                    'transit_time': current_time,
                    'error': f"Transit calculation failed: {str(e)}"
                }
            }
            return _format_natal_style(error_data, data, 'Transit')


    # Sarvashtakavarga (match /lahiri/calculate_sarvashtakavarga response)
    if calc_type in ('sarvashtakavarga', 'sarvathakavargha', 'sarvashtakavargha'):
        try:
            from astro_engine.engine.ashatakavargha.Sarvasthakavargha import lahiri_sarvathakavargha

            user_name = data.get('user_name', 'Unknown')
            birth_date = data.get('birth_date')
            birth_time = data.get('birth_time')
            latitude = float(data.get('latitude')) if data.get('latitude') is not None else None
            longitude = float(data.get('longitude')) if data.get('longitude') is not None else None
            tz_offset = float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else None

            # Call the calculation function
            results = lahiri_sarvathakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

            response = {
                'user_name': user_name,
                'birth_details': {
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone_offset': tz_offset
                },
                'planetary_positions': results.get('planetary_positions', {}),
                'ascendant': results.get('ascendant', {}),
                # 'bhinnashtakavarga': results.get('bhinnashtakavarga', {}),
                'sarvashtakavarga': results.get('sarvashtakavarga', {}),
                'notes': {
                    'ayanamsa': 'Lahiri',
                    'ayanamsa_value': f"{results.get('ayanamsa', 0):.6f}" if results.get('ayanamsa') is not None else None,
                    'chart_type': 'Rasi',
                    'house_system': 'Whole Sign'
                },
                'debug': {
                    'julian_day': results.get('julian_day'),
                    'ayanamsa': f"{results.get('ayanamsa', 0):.6f}" if results.get('ayanamsa') is not None else None
                }
            }
            return response

        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate Sarvashtakavarga: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }


    # Binnashtakavarga (match /lahiri/calculate_binnatakvarga response)
    if calc_type in ('binnastakavargha', 'binnashtakavargha', 'binnatakvarga'):
        try:
            from astro_engine.engine.ashatakavargha.Binnastakavargha import lahiri_binnastakavargha

            user_name = data.get('user_name', 'Unknown')
            birth_date = data.get('birth_date')
            birth_time = data.get('birth_time')
            latitude = float(data.get('latitude')) if data.get('latitude') is not None else None
            longitude = float(data.get('longitude')) if data.get('longitude') is not None else None
            tz_offset = float(data.get('timezone_offset')) if data.get('timezone_offset') is not None else None

            # Call the calculation function (the route calls lahiri_binnastakavargha)
            results = lahiri_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

            response = {
                'user_name': user_name,
                'birth_details': {
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone_offset': tz_offset
                },
                'planetary_positions': results.get('planetary_positions', {}),
                'ascendant': results.get('ascendant', {}),
                'ashtakvarga': results.get('ashtakvarga', {}),
                'notes': results.get('notes', {})
            }
            return response

        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate Binnashtakavarga: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }


    # Prana / Vimshottari Dasha (match /lahiri/calculate_sookshma_prana_dashas response)
    if calc_type in ('prana', 'pranadasha', 'prana_dasha', 'vimshottari_prana', 'sookshma_prana'):
        try:
            from astro_engine.engine.dashas.LahiriPranDasha import (
                calculate_pranaDasha_periods,
                calculate_moon_sidereal_position_prana,
                get_julian_day_pran,
                get_nakshatra_and_lord_prana,
                calculate_dasha_balance_pran
            )

            # Validate required input fields
            required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
            if not all(field in data for field in required_fields):
                missing = [f for f in required_fields if f not in data]
                raise ValueError(f"Missing required field(s): {', '.join(missing)}")

            user_name = data.get('user_name', 'Unknown')
            birth_date = data['birth_date']
            birth_time = data['birth_time']
            tz_offset = float(data['timezone_offset'])

            # Calculate Julian Day for birth (prana-specific)
            jd_birth = get_julian_day_pran(birth_date, birth_time, tz_offset)

            # Calculate Moon's sidereal position
            moon_longitude = calculate_moon_sidereal_position_prana(jd_birth)

            # Determine Nakshatra and lord
            nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_prana(moon_longitude)
            if not nakshatra:
                raise ValueError("Unable to determine Nakshatra")

            # Calculate dasha balance and mahadasha periods
            remaining_days, mahadasha_duration_days, elapsed_days = calculate_dasha_balance_pran(moon_longitude, nakshatra_start, lord)
            mahadasha_periods = calculate_pranaDasha_periods(jd_birth, lord, elapsed_days)

            response = {
                'user_name': user_name,
                'nakshatra_at_birth': nakshatra,
                'moon_longitude': round(moon_longitude, 4) if isinstance(moon_longitude, (int, float)) else moon_longitude,
                'mahadashas': mahadasha_periods
            }
            return response

        except Exception as e:
            return {
                'error': {
                    'message': f'Failed to calculate Prana Dasha: {str(e)}',
                    'type': type(e).__name__
                },
                'status': 'error'
            }




    # fallback
    raise ValueError(f"Unsupported calculation type: {calc_type}")


# Critical Notes:
#
# 1. LIMIT batch size (10 requests max)
# 2. VALIDATE each request in batch
# 3. HANDLE partial failures gracefully
# 4. RETURN status for each item
# 5. LOG batch processing (with batch_id)
# 6. CONSIDER timeout (batch might take longer)
# 7. TEST with various batch sizes
# 8. MONITOR batch request patterns
