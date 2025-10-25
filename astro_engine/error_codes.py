"""
Error Code System for Astro Engine
Phase 3, Module 3.1: Error Code System Design

Comprehensive error code registry with standardized codes for all error scenarios.

Error Code Ranges:
- 1000-1999: Input Validation Errors
- 2000-2999: Calculation Errors
- 3000-3999: Cache/Infrastructure Errors
- 4000-4999: Authentication/Authorization Errors
- 5000-5999: Internal Server Errors

Design Principles:
- Unique code for each error type
- Clear, descriptive error messages
- Appropriate HTTP status codes
- Helpful suggestions for resolution
- Consistent across all endpoints
"""

from typing import Dict


class ErrorCode:
    """
    Error code constants for Astro Engine

    Phase 3, Module 3.1: Centralized error code registry
    """

    # ============================================================================
    # INPUT VALIDATION ERRORS (1000-1999)
    # ============================================================================

    # General validation
    VALIDATION_ERROR = 1000
    NO_DATA = 1001
    INVALID_JSON = 1008

    # Field-specific validation
    INVALID_LATITUDE = 1010
    INVALID_LONGITUDE = 1011
    INVALID_DATE = 1012
    INVALID_TIME = 1013
    INVALID_TIMEZONE = 1014
    MISSING_REQUIRED_FIELD = 1015
    INVALID_DATA_TYPE = 1016
    INVALID_DATE_FORMAT = 1017
    INVALID_TIME_FORMAT = 1018

    # Range validation
    LATITUDE_OUT_OF_RANGE = 1020
    LONGITUDE_OUT_OF_RANGE = 1021
    TIMEZONE_OUT_OF_RANGE = 1022
    DATE_OUT_OF_RANGE = 1023
    FUTURE_DATE_NOT_ALLOWED = 1024

    # Format validation
    INVALID_USER_NAME = 1030
    USER_NAME_TOO_LONG = 1031
    USER_NAME_TOO_SHORT = 1032

    # ============================================================================
    # CALCULATION ERRORS (2000-2999)
    # ============================================================================

    # Swiss Ephemeris errors
    EPHEMERIS_ERROR = 2001
    EPHEMERIS_FILE_NOT_FOUND = 2002
    EPHEMERIS_DATA_CORRUPT = 2003

    # Calculation failures
    CALCULATION_FAILED = 2010
    CALCULATION_TIMEOUT = 2011
    INVALID_PLANETARY_POSITION = 2012
    INVALID_HOUSE_CALCULATION = 2013
    INVALID_DASHA_CALCULATION = 2014

    # Ayanamsa errors
    INVALID_AYANAMSA = 2020
    AYANAMSA_NOT_SUPPORTED = 2021

    # ============================================================================
    # CACHE/INFRASTRUCTURE ERRORS (3000-3999)
    # ============================================================================

    # Cache errors
    CACHE_ERROR = 3001
    CACHE_TIMEOUT = 3002
    CACHE_KEY_ERROR = 3003

    # Redis errors
    REDIS_UNAVAILABLE = 3010
    REDIS_CONNECTION_FAILED = 3011
    REDIS_TIMEOUT = 3012

    # Celery/Queue errors
    QUEUE_ERROR = 3020
    TASK_SUBMIT_FAILED = 3021
    TASK_NOT_FOUND = 3022
    TASK_TIMEOUT = 3023

    # ============================================================================
    # AUTHENTICATION/AUTHORIZATION ERRORS (4000-4999)
    # ============================================================================

    # Authentication
    UNAUTHORIZED = 4001
    INVALID_API_KEY = 4002
    API_KEY_EXPIRED = 4003
    API_KEY_REVOKED = 4004
    MISSING_API_KEY = 4005

    # Authorization
    FORBIDDEN = 4010
    INSUFFICIENT_PERMISSIONS = 4011

    # Rate limiting
    RATE_LIMIT_EXCEEDED = 4029

    # ============================================================================
    # INTERNAL SERVER ERRORS (5000-5999)
    # ============================================================================

    # General errors
    INTERNAL_ERROR = 5000
    NOT_IMPLEMENTED = 5001
    SERVICE_UNAVAILABLE = 5003

    # Configuration errors
    CONFIGURATION_ERROR = 5010
    MISSING_CONFIGURATION = 5011

    # Resource errors
    RESOURCE_EXHAUSTED = 5020
    MEMORY_ERROR = 5021
    DISK_FULL = 5022


# Human-readable error messages for each code
ERROR_MESSAGES: Dict[int, str] = {
    # Validation errors (1000-1999)
    1000: "Invalid input data provided",
    1001: "No JSON data provided in request body",
    1008: "Invalid JSON format in request body",

    1010: "Invalid latitude value",
    1011: "Invalid longitude value",
    1012: "Invalid birth date",
    1013: "Invalid birth time",
    1014: "Invalid timezone offset",
    1015: "Missing required field",
    1016: "Invalid data type for field",
    1017: "Invalid date format (use YYYY-MM-DD)",
    1018: "Invalid time format (use HH:MM:SS)",

    1020: "Latitude must be between -90 and 90 degrees",
    1021: "Longitude must be between -180 and 180 degrees",
    1022: "Timezone offset must be between -12 and 14 hours",
    1023: "Date must be between year 1900 and 2100",
    1024: "Birth date cannot be in the future",

    1030: "Invalid user name",
    1031: "User name is too long (maximum 100 characters)",
    1032: "User name is too short (minimum 1 character)",

    # Calculation errors (2000-2999)
    2001: "Swiss Ephemeris calculation error",
    2002: "Ephemeris data files not found",
    2003: "Ephemeris data is corrupted or invalid",

    2010: "Astrological calculation failed",
    2011: "Calculation timeout (exceeded maximum processing time)",
    2012: "Invalid planetary position calculated",
    2013: "Invalid house calculation",
    2014: "Invalid dasha calculation",

    2020: "Invalid ayanamsa specified",
    2021: "Ayanamsa system not supported",

    # Cache errors (3000-3999)
    3001: "Cache operation failed",
    3002: "Cache operation timeout",
    3003: "Invalid cache key",

    3010: "Redis cache unavailable",
    3011: "Failed to connect to Redis",
    3012: "Redis operation timeout",

    3020: "Task queue error",
    3021: "Failed to submit task to queue",
    3022: "Task not found",
    3023: "Task execution timeout",

    # Auth errors (4000-4999)
    4001: "Authentication required - provide valid API key",
    4002: "Invalid API key provided",
    4003: "API key has expired",
    4004: "API key has been revoked",
    4005: "Missing API key in request headers",

    4010: "Access forbidden - insufficient permissions",
    4011: "You don't have permission to access this resource",

    4029: "Rate limit exceeded - too many requests",

    # Internal errors (5000-5999)
    5000: "Internal server error occurred",
    5001: "Feature not implemented",
    5003: "Service temporarily unavailable",

    5010: "Server configuration error",
    5011: "Required configuration missing",

    5020: "Server resources exhausted",
    5021: "Out of memory",
    5022: "Disk space full",
}


# Map error codes to HTTP status codes
HTTP_STATUS_CODES: Dict[int, int] = {
    # Validation errors → 400 Bad Request
    **{code: 400 for code in range(1000, 2000)},

    # Calculation errors → 500 Internal Server Error (or 422 Unprocessable Entity)
    **{code: 422 for code in range(2000, 2100)},  # 2000-2099

    # Some specific calculation errors → 500
    2001: 500,  # Ephemeris error
    2002: 500,  # File not found
    2003: 500,  # Data corrupt
    2011: 408,  # Timeout → 408 Request Timeout

    # Cache errors → 503 Service Unavailable (infrastructure issue)
    **{code: 503 for code in range(3000, 4000)},

    # Auth errors → 401 Unauthorized or 403 Forbidden
    4001: 401,  # Unauthorized
    4002: 401,  # Invalid key
    4003: 401,  # Expired
    4004: 401,  # Revoked
    4005: 401,  # Missing

    4010: 403,  # Forbidden
    4011: 403,  # Insufficient permissions

    4029: 429,  # Rate limit → 429 Too Many Requests

    # Internal errors → 500 Internal Server Error
    **{code: 500 for code in range(5000, 6000)},

    # Specific overrides
    5001: 501,  # Not Implemented → 501
    5003: 503,  # Service Unavailable → 503
}


def get_error_message(error_code: int) -> str:
    """
    Get human-readable error message for error code

    Args:
        error_code: Numeric error code

    Returns:
        str: Error message or default if code not found
    """
    return ERROR_MESSAGES.get(
        error_code,
        f"An error occurred (code: {error_code})"
    )


def get_http_status_code(error_code: int) -> int:
    """
    Get HTTP status code for error code

    Args:
        error_code: Numeric error code

    Returns:
        int: HTTP status code (defaults to 500)
    """
    return HTTP_STATUS_CODES.get(error_code, 500)


def get_error_category(error_code: int) -> str:
    """
    Get error category based on error code range

    Args:
        error_code: Numeric error code

    Returns:
        str: Error category name
    """
    if 1000 <= error_code < 2000:
        return "validation"
    elif 2000 <= error_code < 3000:
        return "calculation"
    elif 3000 <= error_code < 4000:
        return "infrastructure"
    elif 4000 <= error_code < 5000:
        return "authentication"
    elif 5000 <= error_code < 6000:
        return "internal"
    else:
        return "unknown"


# Critical Notes for Error Code System:
#
# 1. NEVER reuse error codes (maintain registry)
# 2. ALWAYS add new codes to appropriate range
# 3. UPDATE ERROR_MESSAGES when adding new codes
# 4. UPDATE HTTP_STATUS_CODES if default is wrong
# 5. DOCUMENT new error codes in API docs
# 6. USE consistent error response format
# 7. INCLUDE request_id in all error responses
# 8. LOG all errors for monitoring
