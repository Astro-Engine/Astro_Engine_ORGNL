"""
Custom Exception Classes for Astro Engine
Phase 3, Module 3.2: Domain-Specific Exceptions

Provides structured exception hierarchy for all error scenarios with:
- Error codes from centralized registry
- Automatic HTTP status code mapping
- Context preservation for debugging
- JSON serialization for API responses
- Integration with error handlers

Design:
- Base exception class (AstroEngineError)
- Category-specific exceptions
- Context data for debugging
- Automatic error code mapping
"""

from typing import Dict, Any, Optional
from astro_engine.error_codes import (
    ErrorCode, get_error_message, get_http_status_code, get_error_category
)


class AstroEngineError(Exception):
    """
    Base exception for all Astro Engine errors

    Phase 3, Module 3.2: Base exception class

    All custom exceptions inherit from this base class.
    Provides automatic error code mapping, HTTP status codes,
    and JSON serialization for API responses.

    Attributes:
        error_code: Numeric error code from ErrorCode class
        message: Human-readable error message
        context: Additional context data (dict)
        http_status: HTTP status code for this error

    Example:
        raise AstroEngineError(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Something went wrong",
            context={'details': 'additional info'}
        )
    """

    # Default error code (can be overridden in subclasses)
    default_error_code = ErrorCode.INTERNAL_ERROR

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception

        Args:
            message: Custom error message (optional, uses default if not provided)
            error_code: Specific error code (optional, uses class default)
            context: Additional context data (optional)
        """
        self.error_code = error_code or self.default_error_code
        self.message = message or get_error_message(self.error_code)
        self.context = context or {}

        # Call parent constructor
        super().__init__(self.message)

    @property
    def http_status(self) -> int:
        """Get HTTP status code for this error"""
        return get_http_status_code(self.error_code)

    @property
    def category(self) -> str:
        """Get error category"""
        return get_error_category(self.error_code)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response

        Returns:
            dict: Structured error data for API response
        """
        return {
            'error': {
                'code': self.__class__.__name__.replace('Error', '').upper(),
                'error_code': self.error_code,
                'message': self.message,
                'category': self.category,
                **self.context
            }
        }


# =============================================================================
# VALIDATION ERRORS (1000-1999)
# =============================================================================

class ValidationError(AstroEngineError):
    """Input validation error"""
    default_error_code = ErrorCode.VALIDATION_ERROR

    def __init__(self, field: str, value: Any, message: Optional[str] = None):
        super().__init__(
            message=message or f"Invalid {field}",
            error_code=self.default_error_code,
            context={'field': field, 'value': value}
        )


class MissingFieldError(AstroEngineError):
    """Required field missing"""
    default_error_code = ErrorCode.MISSING_REQUIRED_FIELD

    def __init__(self, field: str):
        super().__init__(
            message=f"Required field '{field}' is missing",
            context={'field': field}
        )


class InvalidLatitudeError(AstroEngineError):
    """Invalid latitude value"""
    default_error_code = ErrorCode.INVALID_LATITUDE


class InvalidLongitudeError(AstroEngineError):
    """Invalid longitude value"""
    default_error_code = ErrorCode.INVALID_LONGITUDE


class InvalidDateError(AstroEngineError):
    """Invalid birth date"""
    default_error_code = ErrorCode.INVALID_DATE


class InvalidTimeError(AstroEngineError):
    """Invalid birth time"""
    default_error_code = ErrorCode.INVALID_TIME


class FutureDateError(AstroEngineError):
    """Future date not allowed"""
    default_error_code = ErrorCode.FUTURE_DATE_NOT_ALLOWED


# =============================================================================
# CALCULATION ERRORS (2000-2999)
# =============================================================================

class CalculationError(AstroEngineError):
    """Base class for calculation errors"""
    default_error_code = ErrorCode.CALCULATION_FAILED


class EphemerisError(AstroEngineError):
    """Swiss Ephemeris error"""
    default_error_code = ErrorCode.EPHEMERIS_ERROR


class EphemerisFileNotFoundError(AstroEngineError):
    """Ephemeris data files not found"""
    default_error_code = ErrorCode.EPHEMERIS_FILE_NOT_FOUND


class CalculationTimeoutError(AstroEngineError):
    """Calculation exceeded timeout"""
    default_error_code = ErrorCode.CALCULATION_TIMEOUT


class InvalidAyanamsaError(AstroEngineError):
    """Invalid ayanamsa specified"""
    default_error_code = ErrorCode.INVALID_AYANAMSA


# =============================================================================
# CACHE/INFRASTRUCTURE ERRORS (3000-3999)
# =============================================================================

class CacheError(AstroEngineError):
    """Cache operation error"""
    default_error_code = ErrorCode.CACHE_ERROR


class RedisUnavailableError(AstroEngineError):
    """Redis cache unavailable"""
    default_error_code = ErrorCode.REDIS_UNAVAILABLE


class QueueError(AstroEngineError):
    """Task queue error"""
    default_error_code = ErrorCode.QUEUE_ERROR


# =============================================================================
# AUTHENTICATION/AUTHORIZATION ERRORS (4000-4999)
# =============================================================================

class AuthenticationError(AstroEngineError):
    """Authentication failed"""
    default_error_code = ErrorCode.UNAUTHORIZED


class InvalidAPIKeyError(AstroEngineError):
    """Invalid API key provided"""
    default_error_code = ErrorCode.INVALID_API_KEY


class MissingAPIKeyError(AstroEngineError):
    """API key missing from request"""
    default_error_code = ErrorCode.MISSING_API_KEY


class RateLimitExceededError(AstroEngineError):
    """Rate limit exceeded"""
    default_error_code = ErrorCode.RATE_LIMIT_EXCEEDED


class ForbiddenError(AstroEngineError):
    """Access forbidden"""
    default_error_code = ErrorCode.FORBIDDEN


# =============================================================================
# INTERNAL SERVER ERRORS (5000-5999)
# =============================================================================

class InternalServerError(AstroEngineError):
    """Internal server error"""
    default_error_code = ErrorCode.INTERNAL_ERROR


class ConfigurationError(AstroEngineError):
    """Configuration error"""
    default_error_code = ErrorCode.CONFIGURATION_ERROR


class ServiceUnavailableError(AstroEngineError):
    """Service temporarily unavailable"""
    default_error_code = ErrorCode.SERVICE_UNAVAILABLE


# Critical Usage Notes:
#
# 1. ALWAYS use specific exception classes (not generic Exception)
# 2. PROVIDE context data for debugging
# 3. USE to_dict() method for API responses
# 4. CATCH exceptions in error handlers
# 5. LOG exceptions with full context
# 6. INCLUDE request_id when available
# 7. DON'T expose sensitive data in error messages
# 8. TEST all exception scenarios
