import os
import platform
import sys
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress  # Phase 8, Module 8.1
import swisseph as swe
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import blueprints
try:
    # Try relative imports first (for when run as module)
    from .engine.routes.KpNew import kp
    from .engine.routes.LahairiAyanmasa import bp
    from .engine.routes.RamanAyanmasa import rl
    from .engine.routes.WesternType import ws

    # Import performance enhancements
    # Use Redis-enabled cache manager if REDIS_URL is set, otherwise use stub
    cache_enabled = os.getenv('CACHE_ENABLED', 'false').lower() == 'true'
    if cache_enabled and os.getenv('REDIS_URL'):
        from .cache_manager_redis import create_cache_manager
    else:
        from .cache_manager import create_cache_manager
    from .metrics_manager import create_metrics_manager
    from .structured_logger import create_structured_logger
    from .celery_manager import create_celery_manager
    from .auth_manager import create_api_key_manager, get_api_key_from_request
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from .engine.routes.KpNew import kp
    from .engine.routes.LahairiAyanmasa import bp
    from .engine.routes.RamanAyanmasa import rl
    from astro_engine.engine.routes.WesternType import ws

    # Import performance enhancements
    cache_enabled = os.getenv('CACHE_ENABLED', 'false').lower() == 'true'
    if cache_enabled and os.getenv('REDIS_URL'):
        from .cache_manager_redis import create_cache_manager
    else:
        from .cache_manager import create_cache_manager
    from .metrics_manager import create_metrics_manager
    from .structured_logger import create_structured_logger
    from .celery_manager import create_celery_manager
    from .auth_manager import create_api_key_manager, get_api_key_from_request

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = cors_origins.split(',')
    CORS(app, resources={r"/*": {"origins": cors_origins}})

    # =============================================================================
    # PHASE 8, MODULE 8.1-8.2: RESPONSE COMPRESSION
    # =============================================================================

    # Initialize compression
    compress = Compress()
    app.config['COMPRESS_MIMETYPES'] = [
        'application/json',
        'text/html',
        'text/css',
        'text/xml',
        'application/javascript',
        'text/plain'
    ]
    app.config['COMPRESS_LEVEL'] = 6  # Balance between speed and compression (1-9)
    app.config['COMPRESS_MIN_SIZE'] = 1024  # Only compress responses > 1KB
    app.config['COMPRESS_ALGORITHM'] = ['gzip', 'deflate', 'br']  # Support multiple algorithms
    compress.init_app(app)

    app.logger.info("✅ Response compression initialized (gzip, deflate, brotli)")
    app.logger.info(f"   Min size: 1KB, Compression level: 6")

    # =============================================================================
    # END RESPONSE COMPRESSION
    # =============================================================================

    # =============================================================================
    # PHASE 1, MODULE 1.4: RATE LIMITING PER API KEY
    # =============================================================================

    # Define rate limits per service type
    API_KEY_RATE_LIMITS = {
        'astro_corp_': os.getenv('RATE_LIMIT_CORP_BACKEND', '5000 per hour'),
        'astro_astro_ratan_': os.getenv('RATE_LIMIT_ASTRO_RATAN', '2000 per hour'),
        'astro_report_': os.getenv('RATE_LIMIT_REPORT_ENGINE', '1000 per hour'),
        'astro_testing_': os.getenv('RATE_LIMIT_TESTING', '100 per hour'),
    }

    def get_rate_limit_key():
        """
        Get rate limit key based on API key
        Falls back to IP address if no API key

        Phase 1, Module 1.4: Per-API-key rate limiting
        """
        # Try to get API key from request
        api_key = request.headers.get('X-API-Key')

        if api_key:
            # Use API key for rate limiting (allows per-service limits)
            return api_key

        # Fallback to IP address for unauthenticated requests
        return get_remote_address()

    def get_rate_limit_for_request():
        """
        Determine rate limit based on API key prefix

        Phase 1, Module 1.4: Dynamic rate limits per service
        """
        api_key = request.headers.get('X-API-Key', '')

        # Check which service this key belongs to
        for prefix, limit in API_KEY_RATE_LIMITS.items():
            if api_key.startswith(prefix):
                return limit

        # Default rate limit (for unknown keys or no auth)
        return os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')

    # Initialize rate limiter with per-API-key tracking
    limiter = Limiter(
        key_func=get_rate_limit_key,
        app=app,
        default_limits=[],  # Will use dynamic limits
        storage_uri=os.getenv('REDIS_URL') if os.getenv('REDIS_URL') else 'memory://'
    )

    # Apply rate limits globally with dynamic limits
    @app.before_request
    def apply_rate_limits():
        """
        Apply dynamic rate limits based on API key

        Phase 1, Module 1.4: Dynamic rate limit application
        """
        # Skip rate limiting for exempt routes
        if hasattr(app, 'api_key_manager') and app.api_key_manager.is_route_exempt(request.path):
            return None

        # Get the rate limit for this request
        rate_limit = get_rate_limit_for_request()

        # Check if limit exceeded
        try:
            # Parse limit (e.g., "5000 per hour")
            limit_parts = rate_limit.split()
            if len(limit_parts) >= 3:
                limit_value = int(limit_parts[0])

                # Get current usage
                api_key = request.headers.get('X-API-Key', get_remote_address())

                # This will be handled by Flask-Limiter's decorator
                # We'll add this to routes in next step
                pass

        except Exception as e:
            app.logger.error(f"Error applying rate limit: {e}")

        return None

    # Custom rate limit error handler
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """
        Handle rate limit exceeded errors

        Phase 1, Module 1.4: Rate limit error handling
        """
        api_key = request.headers.get('X-API-Key', 'unknown')
        api_key_masked = api_key[:12] + '***' if len(api_key) > 12 else api_key

        # Log rate limit exceeded
        if hasattr(app, 'structured_logger'):
            app.structured_logger.log_security_event(
                'rate_limit_exceeded',
                {
                    'message': 'API rate limit exceeded',
                    'api_key': api_key_masked,
                    'path': request.path,
                    'ip': request.remote_addr,
                    'request_id': g.get('request_id', 'unknown')
                }
            )

        # Get rate limit details
        rate_limit = get_rate_limit_for_request()

        return jsonify({
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'error_code': 4029,
                'message': f'Rate limit exceeded. Your limit: {rate_limit}',
                'rate_limit': rate_limit,
                'retry_after': '3600 seconds'  # 1 hour
            },
            'status': 'error',
            'request_id': g.get('request_id', 'unknown')
        }), 429

    # =============================================================================
    # END RATE LIMITING CONFIGURATION
    # =============================================================================
    
    # Logging configuration
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    # Ensure log directory exists
    log_file = os.getenv('LOG_FILE', '/app/logs/astro_engine.log')
    log_dir = os.path.dirname(log_file)
    # if log_dir and not os.path.exists(log_dir):
    #     os.makedirs(log_dir, exist_ok=True)
    log_dir = "/tmp/logs"
    os.makedirs(log_dir, exist_ok=True)

    handlers = []
    try:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
        print(f"Logging to file: {log_file}")
    except Exception as e:
        print(f"WARNING: Could not create log file handler at {log_file}: {e}\nLogging only to stdout.")

    handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Set Swiss Ephemeris path
    ephe_path = os.getenv('EPHEMERIS_PATH', 'astro_engine/ephe')
    swe.set_ephe_path(ephe_path)

    # Initialize Redis cache manager
    cache_manager = create_cache_manager(app)
    app.logger.info(f"Cache manager initialized: {'✅ Redis available' if cache_manager.is_available() else '❌ Redis unavailable (running without cache)'}")

    # Initialize Prometheus metrics manager
    metrics_manager = create_metrics_manager(app)
    app.logger.info("✅ Prometheus metrics manager initialized")
    
    # Initialize structured logging manager
    structured_logger = create_structured_logger(app)
    app.logger.info("✅ Structured logging manager initialized")
    
    # Initialize Celery task queue manager (Phase 4.1)
    celery_manager = create_celery_manager(app)
    app.logger.info("✅ Celery task queue manager initialized")

    # Initialize API Key Authentication Manager (Phase 1, Module 1.2)
    api_key_manager = create_api_key_manager(app)
    auth_required = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'
    if api_key_manager.is_enabled():
        app.logger.info(f"✅ API Key authentication initialized ({'ENFORCED' if auth_required else 'OPTIONAL'})")
    else:
        app.logger.warning("⚠️  API Key authentication DISABLED - no keys configured")

    # =============================================================================
    # PHASE 14, MODULE 14.1: GRACEFUL SHUTDOWN HANDLERS
    # =============================================================================

    # Register signal handlers for graceful shutdown
    try:
        from astro_engine.shutdown_handler import register_shutdown_handlers
        register_shutdown_handlers(app)
        app.logger.info("✅ Graceful shutdown handlers registered (SIGTERM, SIGINT)")
    except Exception as e:
        app.logger.warning(f"⚠️  Could not register shutdown handlers: {e}")

    # =============================================================================
    # END GRACEFUL SHUTDOWN HANDLERS
    # =============================================================================

    # Register blueprints
    app.register_blueprint(kp)  # KP System routes
    app.register_blueprint(bp)  # Lahiri Ayanamsa routes
    app.register_blueprint(rl)  # Raman Ayanamsa routes
    app.register_blueprint(ws)  # western Ayanamsa routes

    # =============================================================================
    # PHASE 1, MODULE 1.2: AUTHENTICATION MIDDLEWARE
    # =============================================================================

    @app.before_request
    def authenticate_request():
        """
        Global authentication middleware
        Validates API key for all requests except exempt routes

        Phase 1, Module 1.2: Flask Authentication Middleware
        """
        import uuid

        # Generate request ID for tracking
        if not hasattr(g, 'request_id'):
            g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

        # Check if route is exempt from authentication
        if hasattr(app, 'api_key_manager') and app.api_key_manager.is_route_exempt(request.path):
            app.api_key_manager.stats['exempt_requests'] += 1
            return None  # Allow request

        # Check if authentication is enforced
        auth_required = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'

        # If auth not enforced, allow all requests (transition period)
        if not auth_required:
            return None

        # Extract API key from request
        api_key = get_api_key_from_request(request)

        # Validate API key
        if not hasattr(app, 'api_key_manager'):
            # Auth manager not initialized, allow request
            app.logger.warning("⚠️  Auth manager not initialized")
            return None

        if not app.api_key_manager.validate_api_key(api_key):
            # Log failed authentication attempt
            if hasattr(app, 'structured_logger'):
                app.structured_logger.log_security_event(
                    'auth_failed',
                    {
                        'message': 'Invalid or missing API key',
                        'path': request.path,
                        'method': request.method,
                        'ip': request.remote_addr,
                        'request_id': g.request_id
                    }
                )

            # Return 401 Unauthorized
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'error_code': 4001,
                    'message': 'Valid API key required. Include X-API-Key header in your request.',
                    'documentation': 'https://github.com/Project-Corp-Astro/Astro_Engine#authentication'
                },
                'status': 'error',
                'request_id': g.request_id
            }), 401

        # Store API key metadata in request context
        g.api_key = api_key
        if hasattr(app, 'api_key_manager'):
            g.api_key_metadata = app.api_key_manager.get_key_metadata(api_key)

        # Log successful authentication
        if hasattr(app, 'structured_logger'):
            app.structured_logger.log_security_event(
                'auth_success',
                {
                    'message': 'Request authenticated',
                    'path': request.path,
                    'service': g.api_key_metadata.get('service', 'unknown'),
                    'request_id': g.request_id
                }
            )

        return None  # Continue with request

    @app.after_request
    def add_security_headers(response):
        """
        Add security headers and request ID to all responses

        Phase 1, Module 1.2 & 1.4: Response headers including rate limit info
        """
        # Add request ID header for tracing
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Add API version header
        response.headers['X-API-Version'] = '1.3.0'

        # Add rate limit headers (Phase 1, Module 1.4)
        rate_limit = get_rate_limit_for_request()
        if rate_limit:
            # Parse limit (e.g., "5000 per hour")
            try:
                limit_parts = rate_limit.split()
                if len(limit_parts) >= 3:
                    limit_value = limit_parts[0]
                    limit_period = limit_parts[2]  # hour, minute, etc.

                    response.headers['X-RateLimit-Limit'] = limit_value
                    response.headers['X-RateLimit-Period'] = limit_period

                    # Note: X-RateLimit-Remaining would require tracking
                    # Flask-Limiter provides this automatically via its decorator
            except Exception as e:
                app.logger.debug(f"Error adding rate limit headers: {e}")

        return response

    # =============================================================================
    # END AUTHENTICATION MIDDLEWARE
    # =============================================================================

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        try:
            # Test Swiss Ephemeris
            jd = swe.julday(2024, 1, 1)
            swe.calc_ut(jd, swe.SUN)
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.3.0',
                'services': {
                    'swiss_ephemeris': 'ok',
                    'api_endpoints': 'ok'
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 503
    
    # Prometheus metrics endpoint
    @app.route('/metrics')
    def prometheus_metrics():
        """Prometheus metrics endpoint"""
        if not hasattr(app, 'metrics_manager'):
            return "Metrics not configured", 404
        
        # Update system and Redis metrics before serving
        try:
            app.metrics_manager.update_system_metrics()
            if hasattr(app, 'cache_manager'):
                app.metrics_manager.update_redis_metrics(app.cache_manager)
        except Exception as e:
            app.logger.error(f"Error updating metrics: {e}")
        
        from prometheus_client import CONTENT_TYPE_LATEST
        metrics_data = app.metrics_manager.get_metrics()
        
        return metrics_data, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    # Enhanced metrics endpoint (JSON format for debugging)
    @app.route('/metrics/json')
    def metrics_json():
        """Enhanced metrics endpoint with JSON format for debugging"""
        if not hasattr(app, 'metrics_manager'):
            return jsonify({'error': 'Metrics not configured'}), 404
        
        try:
            # Update all metrics
            app.metrics_manager.update_system_metrics()
            app.metrics_manager.update_resource_utilization()
            app.metrics_manager.calculate_and_update_error_rate()
            
            if hasattr(app, 'cache_manager'):
                app.metrics_manager.update_redis_metrics(app.cache_manager)
            
            # Get cache stats
            cache_stats = {}
            if hasattr(app, 'cache_manager'):
                cache_stats = app.cache_manager.get_stats()
            
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'metrics_status': 'active',
                'cache_statistics': cache_stats,
                'prometheus_endpoint': '/metrics',
                'note': 'Full metrics available at /metrics endpoint in Prometheus format'
            })
        except Exception as e:
            return jsonify({'error': f'Metrics error: {str(e)}'}), 500
    
    # Performance summary endpoint (Phase 2.2)
    @app.route('/metrics/performance')
    def performance_summary():
        """Get comprehensive performance summary"""
        if not hasattr(app, 'metrics_manager'):
            return jsonify({'error': 'Metrics not configured'}), 404
        
        try:
            # Simple metrics update without resource-intensive calls
            if hasattr(app, 'cache_manager'):
                app.metrics_manager.update_redis_metrics(app.cache_manager)
            
            # Get basic performance summary
            performance_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'cache_hit_rate': 0,
                'active_requests': 0,
                'error_rate': 0,
                'status': 'operational'
            }
            
            # Add cache statistics if available
            if hasattr(app, 'cache_manager'):
                cache_stats = app.cache_manager.get_stats()
                performance_data['cache_details'] = cache_stats
                performance_data['cache_hit_rate'] = cache_stats.get('hit_rate', 0)
            
            # Log performance summary request
            if hasattr(app, 'structured_logger'):
                app.structured_logger.get_logger('performance_api').info(
                    "Performance summary requested",
                    cache_hit_rate=performance_data['cache_hit_rate']
                )
            
            return jsonify({
                'status': 'success',
                'performance_metrics': performance_data
            })
            
        except Exception as e:
            if hasattr(app, 'structured_logger'):
                app.structured_logger.log_error('PerformanceError', str(e), 
                                              {'endpoint': 'performance_summary'}, e)
            app.logger.error(f"Error generating performance summary: {e}")
            return jsonify({'error': f'Performance metrics error: {str(e)}'}), 500
    
    # Logging configuration endpoint (Phase 3.1)
    @app.route('/logging/status')
    def logging_status():
        """Get comprehensive logging configuration and status"""
        if not hasattr(app, 'structured_logger'):
            return jsonify({'error': 'Structured logging not configured'}), 404
        
        try:
            config = app.structured_logger.get_log_configuration()
            
            # Log the status request
            app.structured_logger.get_logger('logging_api').info(
                "Logging status requested",
                component="logging_api",
                **config
            )
            
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'operational',
                'configuration': config
            })
            
        except Exception as e:
            app.logger.error(f"Error getting logging status: {e}")
            return jsonify({'error': f'Logging status error: {str(e)}'}), 500
    
    @app.route('/logging/levels', methods=['GET', 'POST'])
    def manage_log_levels():
        """Get or set logging levels"""
        if not hasattr(app, 'structured_logger'):
            return jsonify({'error': 'Structured logging not configured'}), 404
        
        if request.method == 'GET':
            # Return current log levels
            levels = {
                'root': logging.getLevelName(logging.getLogger().level),
                'astro_engine': logging.getLevelName(logging.getLogger('astro_engine').level),
                'available_levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            }
            return jsonify(levels)
        
        elif request.method == 'POST':
            # Set new log level
            data = request.get_json()
            if not data or 'level' not in data:
                return jsonify({'error': 'Level parameter required'}), 400
            
            try:
                level = getattr(logging, data['level'].upper())
                logging.getLogger().setLevel(level)
                logging.getLogger('astro_engine').setLevel(level)
                
                app.structured_logger.get_logger('logging_api').info(
                    "Log level changed",
                    component="logging_management",
                    old_level=levels['root'],
                    new_level=data['level'].upper()
                )
                
                return jsonify({
                    'success': True,
                    'new_level': data['level'].upper(),
                    'message': f'Log level set to {data["level"].upper()}'
                })
                
            except AttributeError:
                return jsonify({'error': f'Invalid log level: {data["level"]}'}), 400
    
    @app.route('/logging/test')
    def test_logging():
        """Test all log levels and functionality"""
        if not hasattr(app, 'structured_logger'):
            return jsonify({'error': 'Structured logging not configured'}), 404
        
        logger = app.structured_logger.get_logger('logging_test')
        
        # Test all log levels
        logger.debug("🔍 DEBUG: This is a debug message", component="log_test", test_type="debug")
        logger.info("ℹ️ INFO: This is an info message", component="log_test", test_type="info")
        logger.warning("⚠️ WARNING: This is a warning message", component="log_test", test_type="warning")
        logger.error("❌ ERROR: This is an error message", component="log_test", test_type="error")
        
        # Test correlation ID
        correlation_id = getattr(g, 'correlation_id', 'no-correlation-id')
        
        # Test structured data
        logger.info("📊 Structured data test",
                   component="log_test",
                   test_metrics={
                       "response_time": 0.123,
                       "cache_hit": True,
                       "user_count": 42
                   },
                   correlation_id=correlation_id)
        
        return jsonify({
            'success': True,
            'message': 'Log test completed - check log files',
            'correlation_id': correlation_id,
            'tests_run': ['debug', 'info', 'warning', 'error', 'structured_data'],
            'log_files': {
                'main': 'astro_engine.log',
                'errors': 'astro_engine_errors.log',
                'performance': 'astro_engine_performance.log'
            }
        })
    
    @app.route('/logging/aggregation')
    def log_aggregation_test():
        """Test log aggregation and JSON output"""
        if not hasattr(app, 'structured_logger'):
            return jsonify({'error': 'Structured logging not configured'}), 404
        
        logger = app.structured_logger.get_logger('aggregation_test')
        
        # Generate sample aggregation data
        sample_logs = []
        for i in range(5):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'component': 'aggregation_test',
                'message': f'Sample log entry {i+1}',
                'metrics': {
                    'request_id': f'req_{i+1}',
                    'duration': round(0.1 + (i * 0.05), 3),
                    'status': 'success'
                }
            }
            sample_logs.append(log_entry)
            
            # Actually log each entry
            logger.info(log_entry['message'], 
                       component=log_entry['component'],
                       request_id=log_entry['metrics']['request_id'],
                       duration=log_entry['metrics']['duration'],
                       status=log_entry['metrics']['status'])
        
        return jsonify({
            'success': True,
            'message': 'Log aggregation test completed',
            'sample_logs_generated': len(sample_logs),
            'sample_logs': sample_logs,
            'aggregation_ready': True,
            'json_output': os.getenv('ENVIRONMENT', 'development') == 'production'
        })

    # Cache management endpoints
    @app.route('/cache/stats')
    def cache_stats():
        """Get detailed cache statistics"""
        if not hasattr(app, 'cache_manager'):
            return jsonify({'error': 'Cache not configured'}), 404
        
        return jsonify(app.cache_manager.get_stats())
    
    @app.route('/cache/clear', methods=['DELETE'])
    def clear_cache():
        """Clear all cache entries"""
        if not hasattr(app, 'cache_manager'):
            return jsonify({'error': 'Cache not configured'}), 404
        
        success = app.cache_manager.clear_all()
        return jsonify({
            'success': success,
            'message': 'Cache cleared successfully' if success else 'Failed to clear cache'
        })
    
    @app.route('/cache/clear/<pattern>', methods=['DELETE'])
    def clear_cache_pattern(pattern):
        """Clear cache entries matching pattern"""
        if not hasattr(app, 'cache_manager'):
            return jsonify({'error': 'Cache not configured'}), 404

        deleted = app.cache_manager.delete(f"*{pattern}*")
        return jsonify({
            'deleted': deleted,
            'pattern': pattern,
            'message': f'Deleted {deleted} cache entries'
        })

    # =============================================================================
    # PHASE 1, MODULE 1.5: AUTHENTICATION MONITORING ENDPOINTS
    # =============================================================================

    @app.route('/auth/stats')
    def auth_stats():
        """
        Get authentication statistics

        Phase 1, Module 1.5: Authentication monitoring
        Returns detailed statistics about API key usage and authentication attempts
        """
        if not hasattr(app, 'api_key_manager'):
            return jsonify({'error': 'Authentication not configured'}), 404

        stats = app.api_key_manager.get_stats()

        return jsonify({
            'authentication': stats,
            'timestamp': datetime.utcnow().isoformat(),
            'enabled': app.api_key_manager.is_enabled(),
            'enforced': os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'
        })

    @app.route('/auth/keys/info')
    def auth_keys_info():
        """
        Get information about configured API keys (without exposing actual keys)

        Phase 1, Module 1.5: API key registry information
        """
        if not hasattr(app, 'api_key_manager'):
            return jsonify({'error': 'Authentication not configured'}), 404

        # Return metadata about keys without exposing actual values
        keys_info = []

        for key in app.api_key_manager.valid_keys:
            metadata = app.api_key_manager.get_key_metadata(key)
            keys_info.append({
                'service': metadata.get('service'),
                'prefix': metadata.get('prefix'),
                'masked_key': metadata.get('masked_key'),
                'valid': True
            })

        return jsonify({
            'total_keys': len(app.api_key_manager.valid_keys),
            'keys': keys_info,
            'exempt_routes': app.api_key_manager.exempt_routes,
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/auth/health')
    def auth_health():
        """
        Check authentication system health

        Phase 1, Module 1.5: Authentication health check
        """
        if not hasattr(app, 'api_key_manager'):
            return jsonify({
                'status': 'not_configured',
                'healthy': False,
                'message': 'Authentication manager not initialized'
            }), 503

        is_enabled = app.api_key_manager.is_enabled()
        auth_enforced = os.getenv('AUTH_REQUIRED', 'false').lower() == 'true'

        # Determine health status
        if not is_enabled and auth_enforced:
            # Configuration error: enforcement enabled but no keys
            status = 'unhealthy'
            healthy = False
            message = 'AUTH_REQUIRED=true but no API keys configured'
        elif is_enabled:
            status = 'healthy'
            healthy = True
            message = f'Authentication active ({len(app.api_key_manager.valid_keys)} keys configured)'
        else:
            status = 'disabled'
            healthy = True
            message = 'Authentication disabled (no keys configured)'

        return jsonify({
            'status': status,
            'healthy': healthy,
            'message': message,
            'details': {
                'enabled': is_enabled,
                'enforced': auth_enforced,
                'total_keys': len(app.api_key_manager.valid_keys),
                'exempt_routes_count': len(app.api_key_manager.exempt_routes)
            },
            'timestamp': datetime.utcnow().isoformat()
        })

    # =============================================================================
    # END AUTHENTICATION MONITORING
    # =============================================================================

    # =============================================================================
    # PHASE 6, MODULE 6.4: CIRCUIT BREAKER MONITORING
    # =============================================================================

    @app.route('/circuit/status')
    def circuit_breaker_status():
        """
        Get status of all circuit breakers

        Phase 6, Module 6.4: Circuit breaker monitoring endpoint
        """
        try:
            from astro_engine.circuit_breakers import get_all_breakers_status

            status = get_all_breakers_status()

            return jsonify({
                'circuit_breakers': status,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            return jsonify({
                'error': 'Circuit breaker status unavailable',
                'message': str(e)
            }), 500

    # =============================================================================
    # END CIRCUIT BREAKER MONITORING
    # =============================================================================

    # =============================================================================
    # PHASE 12: REQUEST QUEUE MONITORING
    # =============================================================================

    @app.route('/queue/stats')
    def queue_stats():
        """
        Get queue statistics

        Phase 12, Module 12.3: Queue depth monitoring
        """
        try:
            from astro_engine.queue_manager import create_queue_manager

            queue_manager = create_queue_manager(app)
            stats = queue_manager.get_queue_stats()

            return jsonify({
                'queue_stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            return jsonify({
                'error': 'Queue stats unavailable',
                'message': str(e),
                'enabled': False
            }), 200  # Return 200 with disabled status

    # =============================================================================
    # END QUEUE MONITORING
    # =============================================================================

    # Celery task management endpoints (Phase 4.1)
    @app.route('/tasks/submit', methods=['POST'])
    def submit_task():
        """Submit a task to the Celery queue"""
        if not hasattr(app, 'celery_manager'):
            return jsonify({'error': 'Celery not configured'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task_name = data.get('task_name')
        task_args = data.get('args', [])
        task_kwargs = data.get('kwargs', {})
        priority = data.get('priority', 5)
        
        if not task_name:
            return jsonify({'error': 'task_name is required'}), 400
        
        # Submit task
        result = app.celery_manager.submit_task(
            task_name=task_name,
            task_args=task_args,
            task_kwargs=task_kwargs,
            priority=priority
        )
        
        if result.get('success'):
            # Log task submission
            app.structured_logger.get_logger('celery_api').info(
                "Task submitted successfully",
                component="task_submission",
                task_id=result['task_id'],
                task_name=task_name,
                priority=priority
            )
            return jsonify(result), 201
        else:
            return jsonify(result), 500
    
    @app.route('/tasks/status/<task_id>')
    def get_task_status(task_id):
        """Get the status of a specific task"""
        if not hasattr(app, 'celery_manager'):
            return jsonify({'error': 'Celery not configured'}), 404
        
        result = app.celery_manager.get_task_status(task_id)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404
    
    @app.route('/tasks/cancel/<task_id>', methods=['DELETE'])
    def cancel_task(task_id):
        """Cancel a pending or running task"""
        if not hasattr(app, 'celery_manager'):
            return jsonify({'error': 'Celery not configured'}), 404
        
        result = app.celery_manager.cancel_task(task_id)
        
        if result.get('success'):
            # Log task cancellation
            app.structured_logger.get_logger('celery_api').info(
                "Task cancelled successfully",
                component="task_cancellation",
                task_id=task_id
            )
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @app.route('/tasks/queue/stats')
    def get_queue_stats():
        """Get Celery queue statistics"""
        if not hasattr(app, 'celery_manager'):
            return jsonify({'error': 'Celery not configured'}), 404
        
        result = app.celery_manager.get_queue_stats()
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500
    
    @app.route('/tasks/available')
    def get_available_tasks():
        """Get list of available task types"""
        from .celery_tasks import get_available_tasks
        
        return jsonify({
            'success': True,
            'available_tasks': get_available_tasks(),
            'task_descriptions': {
                'natal_chart': 'Calculate natal chart for birth data',
                'divisional_chart': 'Calculate divisional charts (D2, D3, D9, etc.)',
                'bulk_charts': 'Calculate multiple charts in batch',
                'test_task': 'Simple test task for validation'
            }
        })
    
    @app.route('/tasks/cleanup', methods=['POST'])
    def cleanup_tasks():
        """Clean up completed task results"""
        if not hasattr(app, 'celery_manager'):
            return jsonify({'error': 'Celery not configured'}), 404
        
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        result = app.celery_manager.cleanup_completed_tasks(max_age_hours)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    # =============================================================================
    # PHASE 3, MODULE 3.3: GLOBAL ERROR HANDLERS
    # =============================================================================

    from astro_engine.exceptions import AstroEngineError

    @app.errorhandler(AstroEngineError)
    def handle_astro_engine_error(error: AstroEngineError):
        """Handle all Astro Engine custom exceptions - Phase 3, Module 3.3"""
        app.logger.error(
            f"AstroEngineError: {error.__class__.__name__}",
            exc_info=True,
            extra={'error_code': error.error_code, 'request_id': g.get('request_id')}
        )

        response_data = error.to_dict()
        response_data['status'] = 'error'
        response_data['request_id'] = g.get('request_id', 'unknown')

        return jsonify(response_data), error.http_status

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found - Phase 3, Module 3.3 (Standardized)"""
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'error_code': 404,
                'message': 'The requested endpoint does not exist',
                'path': request.path
            },
            'status': 'error',
            'request_id': g.get('request_id', 'unknown')
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error - Phase 3, Module 3.3 (Standardized)"""
        app.logger.critical(f"Internal Server Error: {error}", exc_info=True)

        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'error_code': 5000,
                'message': 'An unexpected error occurred',
                'suggestion': 'Please contact support with request_id'
            },
            'status': 'error',
            'request_id': g.get('request_id', 'unknown')
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Catch-all handler - Phase 3, Module 3.3"""
        app.logger.critical(
            f"Unexpected error: {error.__class__.__name__}: {error}",
            exc_info=True,
            extra={'request_id': g.get('request_id')}
        )

        return jsonify({
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'error_code': 5000,
                'message': 'An unexpected error occurred',
                'type': error.__class__.__name__
            },
            'status': 'error',
            'request_id': g.get('request_id', 'unknown')
        }), 500

    # Note: Duplicate 429 handler removed (Phase 1 handler at line 155 is the correct one)

    # =============================================================================
    # END GLOBAL ERROR HANDLERS
    # =============================================================================

    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        if platform.system() == 'Windows':
            # Use Waitress on Windows
            try:
                from waitress import serve
            except ImportError:
                print("Waitress is not installed. Please install it with 'pip install waitress'.")
                sys.exit(1)
            serve(app, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
        else:
            # Use Gunicorn on Unix-like systems
            try:
                from gunicorn.app.base import BaseApplication
            except ImportError:
                print("Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
                sys.exit(1)

            class StandaloneApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key, value)

                def load(self):
                    return self.application

            options = {
                'bind': f"0.0.0.0:{os.getenv('PORT', '5000')}",
                'workers': int(os.getenv('WORKERS', '2')),
                'worker_class': 'gthread',
                'threads': 4,
                'timeout': int(os.getenv('TIMEOUT', '120'))
            }
            StandaloneApplication(app, options).run()
    else:
        # Development mode
        app.run(
            debug=True, 
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', '5000'))
        )