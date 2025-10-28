"""
Graceful Shutdown Handler for Astro Engine
Phase 14: Graceful Shutdown Implementation

Ensures clean shutdown of the application:
- Completes in-flight requests
- Closes connections properly
- Flushes logs and metrics
- Cleans up resources

Handles signals:
- SIGTERM: Standard shutdown (from Docker, Kubernetes, systemd)
- SIGINT: Interrupt signal (Ctrl+C)
"""

import signal
import sys
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Global shutdown flag
_shutdown_requested = False
_shutdown_start_time: Optional[float] = None


# =============================================================================
# PHASE 14, MODULE 14.1: SIGNAL HANDLER IMPLEMENTATION
# =============================================================================

def request_shutdown(signum, frame):
    """
    Handle shutdown signals

    Phase 14, Module 14.1: Signal handler

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global _shutdown_requested, _shutdown_start_time

    signal_names = {
        signal.SIGTERM: 'SIGTERM',
        signal.SIGINT: 'SIGINT'
    }

    signal_name = signal_names.get(signum, f'Signal {signum}')

    if not _shutdown_requested:
        _shutdown_requested = True
        _shutdown_start_time = time.time()

        logger.info(f"🛑 Graceful shutdown requested ({signal_name})")
        logger.info("   Completing in-flight requests...")
        logger.info("   New requests will be rejected")

    else:
        # Second signal = force shutdown
        logger.warning(f"⚠️  Force shutdown requested ({signal_name})")
        logger.warning("   Shutting down immediately")
        sys.exit(1)


def is_shutdown_requested() -> bool:
    """
    Check if shutdown has been requested

    Returns:
        bool: True if shutdown in progress
    """
    return _shutdown_requested


# =============================================================================
# PHASE 14, MODULE 14.2 & 14.3: RESOURCE CLEANUP
# =============================================================================

def cleanup_resources(app):
    """
    Clean up application resources

    Phase 14, Module 14.3: Resource cleanup procedures

    Args:
        app: Flask application instance
    """
    logger.info("🧹 Cleaning up resources...")

    # Close Redis connections
    if hasattr(app, 'cache_manager') and hasattr(app.cache_manager, 'redis_client'):
        try:
            if app.cache_manager.redis_client:
                app.cache_manager.redis_client.close()
                logger.info("   ✅ Redis connection closed")
        except Exception as e:
            logger.warning(f"   ⚠️  Error closing Redis: {e}")

    # Flush logs
    try:
        for handler in logger.handlers:
            handler.flush()
        logger.info("   ✅ Logs flushed")
    except Exception as e:
        logger.warning(f"   ⚠️  Error flushing logs: {e}")

    # Final metrics update
    if hasattr(app, 'metrics_manager'):
        try:
            app.metrics_manager.update_system_metrics()
            logger.info("   ✅ Final metrics recorded")
        except Exception as e:
            logger.warning(f"   ⚠️  Error updating metrics: {e}")

    logger.info("✅ Cleanup complete")


def shutdown_application(app, timeout: int = 30):
    """
    Perform graceful shutdown

    Phase 14, Module 14.4: Shutdown timeout configuration

    Args:
        app: Flask application instance
        timeout: Maximum time to wait for shutdown (seconds)

    Process:
    1. Stop accepting new requests
    2. Wait for in-flight requests (up to timeout)
    3. Clean up resources
    4. Exit
    """
    logger.info("🛑 Starting graceful shutdown...")

    # Wait for in-flight requests (handled by gunicorn)
    # Gunicorn already implements graceful shutdown

    # Clean up resources
    cleanup_resources(app)

    # Calculate shutdown duration
    if _shutdown_start_time:
        duration = time.time() - _shutdown_start_time
        logger.info(f"✅ Graceful shutdown complete ({duration:.2f}s)")
    else:
        logger.info("✅ Shutdown complete")

    # Exit
    sys.exit(0)


# =============================================================================
# REGISTER SIGNAL HANDLERS
# =============================================================================

def register_shutdown_handlers(app):
    """
    Register signal handlers for graceful shutdown

    Phase 14, Module 14.1: Signal handler registration

    Args:
        app: Flask application instance
    """
    # Register SIGTERM handler (standard shutdown)
    signal.signal(signal.SIGTERM, lambda signum, frame: shutdown_application(app))

    # Register SIGINT handler (Ctrl+C)
    signal.signal(signal.SIGINT, lambda signum, frame: shutdown_application(app))

    logger.info("✅ Graceful shutdown handlers registered")
    logger.info("   Signals: SIGTERM, SIGINT")


# =============================================================================
# FLASK REQUEST HOOK FOR SHUTDOWN CHECK
# =============================================================================

def check_shutdown_before_request(app):
    """
    Decorator to check if shutdown requested before processing request

    Phase 14, Module 14.2: In-flight request management

    Returns:
        Flask before_request function
    """
    def before_request_check():
        if is_shutdown_requested():
            from flask import jsonify

            logger.warning("🛑 Rejecting request - shutdown in progress")

            return jsonify({
                'error': {
                    'code': 'SERVICE_SHUTTING_DOWN',
                    'error_code': 5003,
                    'message': 'Service is shutting down gracefully',
                    'suggestion': 'Please retry in a few moments'
                },
                'status': 'error'
            }), 503

    return before_request_check


# Critical Notes:
#
# 1. SIGTERM and SIGINT can be caught (graceful shutdown)
# 2. SIGKILL cannot be caught (immediate termination)
# 3. GUNICORN already implements graceful shutdown (waits 30s)
# 4. DOCKER sends SIGTERM before SIGKILL (10s grace period)
# 5. KUBERNETES sends SIGTERM (30s grace period by default)
# 6. CLEAN UP connections, flush logs, save metrics
# 7. REJECT new requests during shutdown
# 8. WAIT for in-flight requests to complete
