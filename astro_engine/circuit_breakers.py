"""
Circuit Breaker Configuration for Astro Engine
Phase 6, Module 6.1-6.3: Circuit Breaker Implementation

Prevents cascading failures by failing fast when services are down.

Circuit Breaker Pattern:
- CLOSED: Normal operation, all calls go through
- OPEN: Service failing, all calls fail immediately (no waiting)
- HALF-OPEN: Testing if service recovered, limited calls allowed

Design Decisions:
- Fail threshold: 5 consecutive failures
- Recovery timeout: 60 seconds
- Swiss Ephemeris: Protected with circuit breaker
- Redis: Already has graceful degradation (circuit breaker optional)

Benefits:
- Prevents thread/resource exhaustion
- Fast-fail instead of waiting
- Automatic recovery
- Monitoring & visibility
"""

import logging
from pybreaker import CircuitBreaker, CircuitBreakerError
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 6, MODULE 6.1: CIRCUIT BREAKER CONFIGURATION
# =============================================================================

# Swiss Ephemeris Circuit Breaker
ephemeris_breaker = CircuitBreaker(
    fail_max=5,                    # Open circuit after 5 failures
    reset_timeout=60,              # Try again after 60 seconds
    name='swiss_ephemeris',
    exclude=[KeyboardInterrupt]    # Don't count interrupts as failures
)


# Redis Circuit Breaker (optional - Redis already has graceful degradation)
redis_breaker = CircuitBreaker(
    fail_max=3,                    # More sensitive (3 failures)
    reset_timeout=30,              # Faster recovery (30 seconds)
    name='redis_cache',
    exclude=[KeyboardInterrupt]
)


# =============================================================================
# PHASE 6, MODULE 6.2: CIRCUIT BREAKER UTILITIES
# =============================================================================

def get_breaker_state(breaker: CircuitBreaker) -> dict:
    """
    Get current state of a circuit breaker

    Args:
        breaker: CircuitBreaker instance

    Returns:
        dict: State information (state, fail_count, etc.)
    """
    return {
        'name': breaker.name,
        'state': str(breaker.current_state),  # CLOSED, OPEN, or HALF_OPEN
        'fail_counter': breaker.fail_counter,
        'fail_max': breaker.fail_max,
        'reset_timeout': breaker.reset_timeout,
        'is_closed': breaker.current_state == 'closed',
        'is_open': breaker.current_state == 'open',
        'is_half_open': breaker.current_state == 'half_open'
    }


def circuit_breaker_decorator(breaker: CircuitBreaker, fallback: Any = None):
    """
    Decorator to protect functions with circuit breaker

    Phase 6, Module 6.2: Circuit breaker decorator

    Args:
        breaker: CircuitBreaker instance to use
        fallback: Value to return when circuit is open (default: None)

    Returns:
        Decorated function

    Example:
        @circuit_breaker_decorator(ephemeris_breaker)
        def calculate_position(jd, planet):
            return swe.calc_ut(jd, planet)

    When circuit is OPEN:
        - Returns fallback value immediately
        - No actual call to wrapped function
        - Logs circuit open event
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Circuit breaker protects the call
                return breaker.call(func, *args, **kwargs)

            except CircuitBreakerError as e:
                # Circuit is OPEN - service is down
                logger.warning(
                    f"Circuit breaker OPEN for {breaker.name}: {func.__name__}",
                    extra={
                        'circuit': breaker.name,
                        'function': func.__name__,
                        'state': str(breaker.current_state),
                        'fail_count': breaker.fail_counter
                    }
                )

                # Return fallback value
                if fallback is not None:
                    return fallback

                # Re-raise as our custom exception
                from astro_engine.exceptions import ServiceUnavailableError
                raise ServiceUnavailableError(
                    message=f"{breaker.name} service is temporarily unavailable",
                    context={
                        'circuit': breaker.name,
                        'state': str(breaker.current_state),
                        'fail_count': breaker.fail_counter
                    }
                )

        return wrapper
    return decorator


# =============================================================================
# CIRCUIT BREAKER EVENT LISTENERS
# =============================================================================

# Event listeners are optional for now
# Circuit breaker will work without them
# Can add monitoring via get_breaker_state() function


# =============================================================================
# CIRCUIT BREAKER HEALTH CHECK
# =============================================================================

def get_all_breakers_status() -> dict:
    """
    Get status of all circuit breakers

    Phase 6, Module 6.4: Circuit breaker monitoring

    Returns:
        dict: Status of all configured circuit breakers
    """
    breakers = {
        'swiss_ephemeris': ephemeris_breaker,
        'redis_cache': redis_breaker
    }

    status = {}
    for name, breaker in breakers.items():
        status[name] = get_breaker_state(breaker)

    # Overall health
    all_closed = all(b['is_closed'] for b in status.values())

    return {
        'breakers': status,
        'healthy': all_closed,
        'total_breakers': len(breakers),
        'open_breakers': sum(1 for b in status.values() if b['is_open'])
    }


# Critical Notes for Circuit Breakers:
#
# 1. USE circuit breakers for external services (Swiss Ephemeris, Redis)
# 2. SET appropriate failure thresholds (don't open too quickly)
# 3. CONFIGURE reasonable reset timeouts (allow recovery)
# 4. LOG circuit state changes (for monitoring)
# 5. MONITOR circuit breaker status (dashboard, alerts)
# 6. PROVIDE fallback values when possible
# 7. TEST circuit breaker behavior (open, close, half-open)
# 8. DON'T use for every function (overhead)
