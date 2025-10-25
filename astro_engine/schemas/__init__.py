"""
Pydantic Schema Models for Astro Engine
Phase 2, Module 2.1: Input Validation Schemas

Provides comprehensive input validation using Pydantic v2
for all API endpoints in Astro Engine.

Design Principles:
- Fail fast with clear error messages
- Validate ALL inputs before processing
- Provide helpful suggestions in error messages
- Handle edge cases gracefully
- Maintain backward compatibility with existing routes

Usage:
    from astro_engine.schemas import BirthDataSchema, validate_schema

    @bp.route('/lahiri/natal', methods=['POST'])
    @validate_schema(BirthDataSchema)
    def natal_chart():
        data = request.validated_data  # Already validated!
        # Process...
"""

from functools import wraps
from flask import request, jsonify, g
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)


def validate_schema(schema_class):
    """
    Decorator to validate request data against Pydantic schema

    Phase 2, Module 2.2: Route-level validation integration

    Args:
        schema_class: Pydantic model class to validate against

    Returns:
        Decorated function with automatic validation

    Example:
        @bp.route('/lahiri/natal', methods=['POST'])
        @validate_schema(BirthDataSchema)
        def natal_chart():
            data = request.validated_data  # Guaranteed valid
            # ... process

    Error Response Format:
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": [
                    {
                        "field": "latitude",
                        "error": "Latitude must be between -90 and 90",
                        "input": 9999
                    }
                ]
            },
            "status": "error",
            "request_id": "abc-123"
        }
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get JSON data from request
                # This may raise BadRequest if JSON is malformed
                data = request.get_json()

                if not data:
                    return jsonify({
                        'error': {
                            'code': 'NO_DATA',
                            'error_code': 1000,
                            'message': 'No JSON data provided in request body',
                            'suggestion': 'Send JSON data with Content-Type: application/json'
                        },
                        'status': 'error',
                        'request_id': g.get('request_id', 'unknown')
                    }), 400

                # Validate against schema
                validated_data = schema_class(**data)

                # Store validated data in request context
                request.validated_data = validated_data

                # Call the actual route function
                return func(*args, **kwargs)

            except BadRequest as e:
                # Flask raised BadRequest (malformed JSON, etc.)
                logger.warning(f"Bad request in {func.__name__}: {e}")

                return jsonify({
                    'error': {
                        'code': 'INVALID_JSON',
                        'error_code': 1008,
                        'message': 'Invalid JSON in request body',
                        'details': str(e),
                        'suggestion': 'Ensure request body contains valid JSON'
                    },
                    'status': 'error',
                    'request_id': g.get('request_id', 'unknown')
                }), 400

            except ValidationError as e:
                # Pydantic validation failed
                logger.warning(f"Validation error in {func.__name__}: {e}")

                # Format validation errors for user-friendly response
                error_details = []
                for error in e.errors():
                    field = '.'.join(str(x) for x in error['loc'])
                    error_details.append({
                        'field': field,
                        'error': error['msg'],
                        'input': error.get('input'),
                        'type': error['type']
                    })

                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'error_code': 1000,
                        'message': 'Invalid input data provided',
                        'details': error_details,
                        'suggestion': 'Check the field requirements and try again'
                    },
                    'status': 'error',
                    'request_id': g.get('request_id', 'unknown')
                }), 400

            except ValueError as e:
                # Type conversion errors
                logger.warning(f"Value error in {func.__name__}: {e}")

                return jsonify({
                    'error': {
                        'code': 'INVALID_VALUE',
                        'error_code': 1007,
                        'message': str(e),
                        'suggestion': 'Check data types (strings, numbers, etc.)'
                    },
                    'status': 'error',
                    'request_id': g.get('request_id', 'unknown')
                }), 400

            except Exception as e:
                # Unexpected errors
                logger.error(f"Unexpected error in validation: {e}", exc_info=True)

                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'error_code': 5000,
                        'message': 'An error occurred during validation',
                        'suggestion': 'Contact support with request_id'
                    },
                    'status': 'error',
                    'request_id': g.get('request_id', 'unknown')
                }), 500

        return wrapper
    return decorator


# Export commonly used items
__all__ = [
    'validate_schema',
    # Schemas will be added as we create them
]
