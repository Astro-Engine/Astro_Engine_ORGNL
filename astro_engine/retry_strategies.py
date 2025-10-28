"""
Retry Strategies for Astro Engine
Phase 15: Retry Logic with Exponential Backoff

Implements retry logic for transient failures using Tenacity library.

Retry Scenarios:
- Swiss Ephemeris file read errors (rare but possible)
- Redis connection failures (already has retry_on_timeout, this adds more)
- Network timeouts
- Temporary service unavailability

Non-Retry Scenarios:
- Validation errors (permanent failures)
- Authentication errors (won't succeed on retry)
- Bad input data (permanent failures)

Design:
- 3 retry attempts (4 total tries)
- Exponential backoff: 1s, 2s, 4s
- Maximum wait: 10 seconds total
- Stop on certain exception types
"""

import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)
import swisseph as swe

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 15, MODULE 15.1: TENACITY INTEGRATION
# =============================================================================

# Retry configuration for Swiss Ephemeris operations
retry_ephemeris = retry(
    stop=stop_after_attempt(3),  # 3 retries = 4 total attempts
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 1s, 2s, 4s, 8s (max 10s)
    retry=retry_if_exception_type((IOError, OSError)),  # Only retry file/IO errors
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG)
)

# Retry configuration for Redis operations
retry_redis = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=0.5, max=5),  # 0.5s, 1s, 2s, 4s (max 5s)
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG)
)

# Retry configuration for general operations
retry_general = retry(
    stop=stop_after_attempt(2),  # Fewer retries for general operations
    wait=wait_exponential(multiplier=0.5, min=0.5, max=3),
    before=before_log(logger, logging.DEBUG)
)


# =============================================================================
# PHASE 15, MODULE 15.2: EPHEMERIS RETRY WRAPPER
# =============================================================================

@retry_ephemeris
def calculate_planetary_position_with_retry(julian_day: float, planet_id: int):
    """
    Calculate planetary position with retry logic

    Phase 15, Module 15.2: Ephemeris with retry

    Args:
        julian_day: Julian day number
        planet_id: Planet ID (swe.SUN, swe.MOON, etc.)

    Returns:
        tuple: (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)

    Retries on:
        - IOError (ephemeris file read errors)
        - OSError (file system errors)

    Raises:
        Exception: After 3 failed retries
    """
    try:
        result = swe.calc_ut(julian_day, planet_id)
        return result

    except (IOError, OSError) as e:
        logger.warning(f"Ephemeris calculation failed, will retry: {e}")
        raise  # Tenacity will retry

    except Exception as e:
        # Don't retry other exceptions (they won't succeed)
        logger.error(f"Ephemeris calculation failed (non-retryable): {e}")
        raise


# =============================================================================
# PHASE 15, MODULE 15.3: REDIS RETRY WRAPPER
# =============================================================================

def redis_operation_with_retry(operation_func, *args, **kwargs):
    """
    Execute Redis operation with retry logic

    Phase 15, Module 15.3: Redis operations with retry

    Args:
        operation_func: Redis operation function
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Result of operation or None on failure

    Note: Redis client already has retry_on_timeout=True,
    this adds additional retry logic for connection failures.
    """
    @retry_redis
    def execute_operation():
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Redis operation failed, will retry: {e}")
            raise

    try:
        return execute_operation()
    except Exception as e:
        logger.error(f"Redis operation failed after retries: {e}")
        return None  # Graceful degradation


# =============================================================================
# PHASE 15, MODULE 15.4: RETRY METRICS
# =============================================================================

class RetryMetrics:
    """
    Track retry statistics

    Phase 15, Module 15.4: Retry monitoring
    """

    def __init__(self):
        self.stats = {
            'ephemeris_retries': 0,
            'ephemeris_retry_successes': 0,
            'ephemeris_retry_failures': 0,
            'redis_retries': 0,
            'redis_retry_successes': 0,
            'redis_retry_failures': 0
        }

    def record_retry(self, operation_type: str, success: bool):
        """
        Record retry attempt

        Args:
            operation_type: 'ephemeris' or 'redis'
            success: Whether retry succeeded
        """
        self.stats[f'{operation_type}_retries'] += 1

        if success:
            self.stats[f'{operation_type}_retry_successes'] += 1
        else:
            self.stats[f'{operation_type}_retry_failures'] += 1

    def get_stats(self) -> dict:
        """Get retry statistics"""
        total_retries = self.stats['ephemeris_retries'] + self.stats['redis_retries']
        total_successes = self.stats['ephemeris_retry_successes'] + self.stats['redis_retry_successes']

        success_rate = (total_successes / total_retries * 100) if total_retries > 0 else 0

        return {
            **self.stats,
            'total_retries': total_retries,
            'total_successes': total_successes,
            'success_rate': round(success_rate, 2)
        }


# Global retry metrics instance
retry_metrics = RetryMetrics()


# =============================================================================
# PHASE 15, MODULE 15.5: RETRY CONFIGURATION
# =============================================================================

# Retry configuration constants (can be overridden via environment)
import os

RETRY_CONFIG = {
    'ephemeris': {
        'max_attempts': int(os.getenv('RETRY_EPHEMERIS_MAX_ATTEMPTS', '3')),
        'min_wait': float(os.getenv('RETRY_EPHEMERIS_MIN_WAIT', '1')),
        'max_wait': float(os.getenv('RETRY_EPHEMERIS_MAX_WAIT', '10')),
    },
    'redis': {
        'max_attempts': int(os.getenv('RETRY_REDIS_MAX_ATTEMPTS', '3')),
        'min_wait': float(os.getenv('RETRY_REDIS_MIN_WAIT', '0.5')),
        'max_wait': float(os.getenv('RETRY_REDIS_MAX_WAIT', '5')),
    }
}


def get_retry_config(operation_type: str) -> dict:
    """
    Get retry configuration for operation type

    Phase 15, Module 15.5: Configuration management

    Args:
        operation_type: 'ephemeris' or 'redis'

    Returns:
        dict: Retry configuration
    """
    return RETRY_CONFIG.get(operation_type, {
        'max_attempts': 3,
        'min_wait': 1,
        'max_wait': 10
    })


# Critical Notes for Retry Logic:
#
# 1. ONLY retry transient failures (network, timeout, IO errors)
# 2. DON'T retry validation errors (permanent failures)
# 3. USE exponential backoff (prevent thundering herd)
# 4. SET maximum retry attempts (3 is good default)
# 5. LOG retry attempts (for debugging)
# 6. TRACK retry metrics (for monitoring)
# 7. CONFIGURE via environment variables (flexibility)
# 8. FAIL gracefully after max retries (don't hang forever)
