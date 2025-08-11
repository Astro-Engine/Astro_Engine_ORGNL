import os
import platform
import sys
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
    from .cache_manager import create_cache_manager
    from .metrics_manager import create_metrics_manager
    from .structured_logger import create_structured_logger
    from .celery_manager import create_celery_manager
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from .engine.routes.KpNew import kp
    from .engine.routes.LahairiAyanmasa import bp
    from .engine.routes.RamanAyanmasa import rl
    from astro_engine.engine.routes.WesternType import ws
    
    # Import performance enhancements
    from .cache_manager import create_cache_manager
    from .metrics_manager import create_metrics_manager
    from .structured_logger import create_structured_logger
    from .celery_manager import create_celery_manager

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
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[f"{os.getenv('RATE_LIMIT_REQUESTS', '1000')} per hour"]
    )
    
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
    # cache_manager = create_cache_manager(app)
    # app.logger.info(f"Cache manager initialized: {'✅ Redis available' if cache_manager.is_available() else '❌ Redis unavailable'}")
    
    # Initialize Prometheus metrics manager
    metrics_manager = create_metrics_manager(app)
    app.logger.info("✅ Prometheus metrics manager initialized")
    
    # Initialize structured logging manager
    structured_logger = create_structured_logger(app)
    app.logger.info("✅ Structured logging manager initialized")
    
    # Initialize Celery task queue manager (Phase 4.1)
    celery_manager = create_celery_manager(app)
    app.logger.info("✅ Celery task queue manager initialized")
    
    # Register blueprints
    app.register_blueprint(kp)  # KP System routes
    app.register_blueprint(bp)  # Lahiri Ayanamsa routes
    app.register_blueprint(rl)  # Raman Ayanamsa routes
    app.register_blueprint(ws)  # western Ayanamsa routes
    
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

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested endpoint does not exist',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests, please try again later',
            'status_code': 429
        }), 429
    
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