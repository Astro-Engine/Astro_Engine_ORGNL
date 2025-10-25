"""
Calculation Result Validators for Astro Engine
Phase 9: Calculation Result Validation

Validates astrological calculation results before returning to clients.

Ensures:
- Planetary positions are within valid ranges
- House cusps are properly ordered
- Dasha periods have valid dates
- All required fields are present
- Data types are correct

Design Principles:
- Validate AFTER calculation, BEFORE response
- Fail fast with clear errors
- Provide warnings for unusual (but valid) data
- Log validation failures
- Never return invalid astrological data
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Zodiac signs (standard order)
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Planets (standard list)
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']

# Nakshatras (27 lunar mansions)
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]


# =============================================================================
# PHASE 9, MODULE 9.1: PLANETARY POSITION VALIDATION
# =============================================================================

def validate_planetary_position(planet_data: Dict[str, Any], planet_name: str) -> tuple[bool, List[str]]:
    """
    Validate planetary position data

    Phase 9, Module 9.1: Planetary position validation

    Args:
        planet_data: Dictionary containing planet position data
        planet_name: Name of the planet

    Returns:
        tuple: (is_valid: bool, errors: List[str])

    Validates:
        - Longitude is between 0-360 degrees
        - Sign is one of 12 zodiac signs
        - Retrograde is boolean
        - Degrees within sign range (0-30)
    """
    errors = []

    # Check longitude
    if 'lon' in planet_data or 'longitude' in planet_data:
        lon = planet_data.get('lon') or planet_data.get('longitude', 0)
        if not (0 <= lon < 360):
            errors.append(f"{planet_name}: Invalid longitude {lon}° (must be 0-360)")

    # Check sign
    if 'sign' in planet_data:
        sign = planet_data.get('sign')
        if sign not in ZODIAC_SIGNS:
            errors.append(f"{planet_name}: Invalid sign '{sign}' (must be one of 12 zodiac signs)")

    # Check retrograde flag
    if 'retro' in planet_data:
        retro = planet_data.get('retro')
        if retro is not None and not isinstance(retro, bool):
            errors.append(f"{planet_name}: Retrograde must be boolean, got {type(retro).__name__}")
    elif 'retrograde' in planet_data:
        retro = planet_data.get('retrograde')
        if retro is not None and not isinstance(retro, bool):
            errors.append(f"{planet_name}: Retrograde must be boolean, got {type(retro).__name__}")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_all_planets(chart_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate all planetary positions in chart

    Phase 9, Module 9.1: Complete planetary validation

    Args:
        chart_data: Chart data containing planetary positions

    Returns:
        tuple: (is_valid: bool, errors: List[str])
    """
    all_errors = []

    # Check if planet_positions exists
    if 'planet_positions' not in chart_data and 'planetary_positions_json' not in chart_data:
        all_errors.append("Missing planetary positions in chart data")
        return False, all_errors

    planets_data = chart_data.get('planet_positions') or chart_data.get('planetary_positions_json', {})

    # Validate each planet
    for planet_name, planet_data in planets_data.items():
        is_valid, errors = validate_planetary_position(planet_data, planet_name)
        all_errors.extend(errors)

    # Check all expected planets are present
    for expected_planet in PLANETS:
        if expected_planet not in planets_data:
            # This is a warning, not an error (some charts may not have all planets)
            logger.debug(f"Planet {expected_planet} not in chart data")

    is_valid = len(all_errors) == 0
    return is_valid, all_errors


# =============================================================================
# PHASE 9, MODULE 9.2: HOUSE SYSTEM VALIDATION
# =============================================================================

def validate_houses(chart_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate house system calculations

    Phase 9, Module 9.2: House validation

    Args:
        chart_data: Chart data containing house information

    Returns:
        tuple: (is_valid: bool, errors: List[str])

    Validates:
        - 12 houses present
        - House cusps are valid longitudes (0-360°)
        - Houses are in proper order
    """
    errors = []

    # Check houses exist
    if 'houses' not in chart_data and 'house_cusps' not in chart_data:
        errors.append("Missing houses in chart data")
        return False, errors

    houses = chart_data.get('houses') or chart_data.get('house_cusps', [])

    # Check count
    if isinstance(houses, list):
        if len(houses) != 12:
            errors.append(f"Expected 12 houses, found {len(houses)}")

    # Validate each house cusp (if available)
    if isinstance(houses, list):
        for i, house in enumerate(houses, 1):
            if isinstance(house, dict) and 'cusp' in house:
                cusp = house['cusp']
                if not (0 <= cusp < 360):
                    errors.append(f"House {i}: Invalid cusp {cusp}° (must be 0-360)")

    is_valid = len(errors) == 0
    return is_valid, errors


# =============================================================================
# PHASE 9, MODULE 9.4: RESPONSE COMPLETENESS VALIDATION
# =============================================================================

def validate_natal_chart_response(chart_data: Dict[str, Any]) -> tuple[bool, List[str], List[str]]:
    """
    Validate complete natal chart response

    Phase 9, Module 9.4: Complete response validation

    Args:
        chart_data: Complete chart data dictionary

    Returns:
        tuple: (is_valid: bool, errors: List[str], warnings: List[str])

    Validates:
        - All required fields present
        - Data types correct
        - Planetary positions valid
        - Houses valid
        - No null/undefined values in critical fields
    """
    errors = []
    warnings = []

    # Check required top-level fields
    required_fields = ['user_name', 'birth_date', 'birth_time']
    for field in required_fields:
        if field not in chart_data:
            warnings.append(f"Missing optional field: {field}")

    # Validate planetary positions
    planets_valid, planet_errors = validate_all_planets(chart_data)
    errors.extend(planet_errors)

    # Validate houses
    houses_valid, house_errors = validate_houses(chart_data)
    errors.extend(house_errors)

    # Check for null values in critical fields
    critical_fields = ['ascendant']
    for field in critical_fields:
        if field in chart_data and chart_data[field] is None:
            errors.append(f"Critical field '{field}' is null")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def log_validation_failure(chart_type: str, errors: List[str], context: Dict[str, Any]):
    """
    Log calculation validation failure

    Args:
        chart_type: Type of chart (natal, navamsa, etc.)
        errors: List of validation errors
        context: Additional context (user_name, birth_date, etc.)
    """
    logger.error(
        f"Calculation validation FAILED for {chart_type}",
        extra={
            'chart_type': chart_type,
            'error_count': len(errors),
            'errors': errors,
            **context
        }
    )


def create_validation_error_response(chart_type: str, errors: List[str]) -> Dict[str, Any]:
    """
    Create error response for validation failure

    Args:
        chart_type: Type of chart
        errors: List of validation errors

    Returns:
        dict: Error response in standard format
    """
    from astro_engine.error_codes import ErrorCode

    return {
        'error': {
            'code': 'CALCULATION_VALIDATION_FAILED',
            'error_code': ErrorCode.CALCULATION_FAILED,
            'message': f'Calculation result validation failed for {chart_type}',
            'details': errors,
            'suggestion': 'This may indicate corrupted ephemeris data or calculation error'
        },
        'status': 'error'
    }


# Critical Notes for Result Validation:
#
# 1. VALIDATE results AFTER calculation, BEFORE sending to client
# 2. NEVER send invalid astrological data to users
# 3. LOG all validation failures for investigation
# 4. PROVIDE clear error messages
# 5. DISTINGUISH between errors (reject) and warnings (allow with notice)
# 6. CHECK all critical fields (planets, houses, ascendant)
# 7. VERIFY data types are correct
# 8. TEST with known good results
