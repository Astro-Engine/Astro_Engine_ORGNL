# Redis Cache Manager for Astro Engine - DigitalOcean App Platform Ready
# Optimized for managed Redis on DigitalOcean with graceful degradation

import redis
import json
import hashlib
import logging
import os
from functools import wraps
from typing import Dict, Any, Optional, Union
from flask import request, current_app, jsonify, Response
import time
from datetime import datetime, timedelta

class AstroCacheManager:
    """
    Centralized cache management for Astro Engine calculations
    Implements Redis caching with performance monitoring and health checks
    Gracefully degrades if Redis is unavailable
    """

    def __init__(self, app=None):
        self.redis_client = None
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_errors': 0,
            'total_operations': 0
        }
        self.logger = logging.getLogger(__name__)

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize Redis connection with Flask app"""
        try:
            # Get Redis URL from environment (DigitalOcean sets this automatically)
            redis_url = os.getenv('REDIS_URL') or app.config.get('REDIS_URL')

            if not redis_url:
                self.logger.warning("⚠️  No REDIS_URL configured - caching disabled")
                self.redis_client = None
                return

            self.redis_client = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )

            # Test Redis connection
            self.redis_client.ping()
            self.logger.info(f"✅ Redis connected successfully")

            # Set default TTL from config
            self.default_ttl = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 86400))  # 24 hours default

        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
            self.logger.warning("⚠️  Continuing without cache - all calculations will be live")
            self.redis_client = None

    def is_available(self) -> bool:
        """Check if Redis is available and healthy"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception as e:
            self.logger.warning(f"Redis health check failed: {e}")
        return False

    def generate_cache_key(self, data: Dict[str, Any], prefix: str = "calc") -> str:
        """
        Generate consistent cache key from birth data
        Ensures same inputs always generate same key
        """
        try:
            # Normalize data for consistent key generation
            cache_data = {
                'birth_date': data.get('birth_date', ''),
                'birth_time': data.get('birth_time', ''),
                'latitude': round(float(data.get('latitude', 0)), 6),
                'longitude': round(float(data.get('longitude', 0)), 6),
                'timezone_offset': float(data.get('timezone_offset', 0)),
                'ayanamsa': data.get('ayanamsa', 'lahiri'),
                'calculation_type': data.get('calculation_type', 'natal')
            }

            # Create deterministic hash
            key_string = json.dumps(cache_data, sort_keys=True)
            hash_key = hashlib.md5(key_string.encode()).hexdigest()

            return f"{prefix}:{hash_key}"

        except Exception as e:
            self.logger.error(f"Cache key generation failed: {e}")
            # Fallback to timestamp-based key
            return f"{prefix}:fallback:{int(time.time())}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with metrics tracking"""
        start_time = time.time()

        if not self.is_available():
            self.stats['cache_errors'] += 1
            return None

        try:
            value = self.redis_client.get(key)
            duration = time.time() - start_time

            if value is not None:
                self.stats['cache_hits'] += 1
                self.logger.debug(f"🟢 Cache HIT: {key} ({duration:.3f}s)")
                # Record metrics
                if hasattr(current_app, 'metrics_manager'):
                    current_app.metrics_manager.record_cache_operation('get', 'hit')
                    current_app.metrics_manager.record_cache_performance('get', duration)
                return json.loads(value)
            else:
                self.stats['cache_misses'] += 1
                self.logger.debug(f"⚪ Cache MISS: {key} ({duration:.3f}s)")
                # Record metrics
                if hasattr(current_app, 'metrics_manager'):
                    current_app.metrics_manager.record_cache_operation('get', 'miss')
                    current_app.metrics_manager.record_cache_performance('get', duration)
                return None

        except Exception as e:
            duration = time.time() - start_time
            self.stats['cache_errors'] += 1
            self.logger.error(f"Cache get error for key {key}: {e}")
            # Record metrics
            if hasattr(current_app, 'metrics_manager'):
                current_app.metrics_manager.record_cache_operation('get', 'error')
                current_app.metrics_manager.record_cache_performance('get', duration)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with metrics tracking"""
        start_time = time.time()

        if not self.is_available():
            self.stats['cache_errors'] += 1
            return False

        try:
            # Serialize value
            serialized_value = json.dumps(value)

            # Set with TTL
            if ttl:
                success = self.redis_client.setex(key, ttl, serialized_value)
            else:
                success = self.redis_client.setex(key, self.default_ttl, serialized_value)

            duration = time.time() - start_time

            if success:
                self.logger.debug(f"🟢 Cache SET: {key} (TTL: {ttl or self.default_ttl}s, {duration:.3f}s)")
                # Record metrics
                if hasattr(current_app, 'metrics_manager'):
                    current_app.metrics_manager.record_cache_operation('set', 'success')
                    current_app.metrics_manager.record_cache_performance('set', duration)
                return True
            else:
                self.stats['cache_errors'] += 1
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.stats['cache_errors'] += 1
            self.logger.error(f"Cache set error for key {key}: {e}")
            # Record metrics
            if hasattr(current_app, 'metrics_manager'):
                current_app.metrics_manager.record_cache_operation('set', 'error')
                current_app.metrics_manager.record_cache_performance('set', duration)
            return False

    def delete(self, pattern: str) -> int:
        """Delete cache entries matching pattern"""
        if not self.is_available():
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.logger.info(f"🗑️ Deleted {deleted} cache entries: {pattern}")
                return deleted
            return 0

        except Exception as e:
            self.logger.error(f"Cache delete error for pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = self.stats.copy()

        # Calculate hit rate
        total_gets = stats['cache_hits'] + stats['cache_misses']
        stats['hit_rate'] = (stats['cache_hits'] / max(total_gets, 1)) * 100

        # Add Redis availability status
        stats['redis_available'] = self.is_available()

        # Get Redis info if available
        if self.is_available():
            try:
                redis_info = self.redis_client.info()
                stats['redis_info'] = {
                    'used_memory': redis_info.get('used_memory_human', 'N/A'),
                    'total_keys': redis_info.get('db0', {}).get('keys', 0) if 'db0' in redis_info else 0,
                    'hits': redis_info.get('keyspace_hits', 0),
                    'misses': redis_info.get('keyspace_misses', 0),
                    'connected_clients': redis_info.get('connected_clients', 0)
                }
            except Exception as e:
                stats['redis_info'] = {'error': str(e)}
        else:
            stats['redis_info'] = {'status': 'unavailable'}

        return stats

    def clear_all(self) -> bool:
        """Clear all cache entries (use with caution)"""
        if not self.is_available():
            return False

        try:
            self.redis_client.flushdb()
            self.logger.warning("🧹 All cache entries cleared")
            return True
        except Exception as e:
            self.logger.error(f"Cache clear all error: {e}")
            return False


def cache_calculation(cache_prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching expensive astrological calculations

    Args:
        cache_prefix: Prefix for cache keys (e.g., 'natal', 'navamsa')
        ttl: Time to live in seconds (optional, defaults to 24 hours)

    Usage:
        @cache_calculation('natal_chart', ttl=86400)
        def calculate_natal_chart():
            # expensive calculation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get cache manager from app context
                cache_manager = getattr(current_app, 'cache_manager', None)

                if not cache_manager or not cache_manager.is_available():
                    # Cache not available - calculate directly
                    return func(*args, **kwargs)

                # Get request data for cache key generation
                data = request.get_json() or {}
                cache_key = cache_manager.generate_cache_key(data, cache_prefix)

                # Try to get from cache first
                cached_result = cache_manager.get(cache_key)
                if cached_result:
                    current_app.logger.info(f"Cache HIT for {func.__name__}")
                    # Add cache metadata
                    if isinstance(cached_result, dict):
                        cached_result['_performance'] = {
                            'cached': True,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    return jsonify(cached_result)

                # Calculate result if not cached
                current_app.logger.info(f"Cache MISS for {func.__name__}, calculating...")
                start_time = time.time()
                result = func(*args, **kwargs)
                calculation_time = time.time() - start_time

                # Handle Flask Response objects
                if isinstance(result, Response):
                    try:
                        json_data = result.get_json()
                        if json_data and isinstance(json_data, dict):
                            # Add performance metadata
                            json_data['_performance'] = {
                                'calculation_time': round(calculation_time, 3),
                                'cached': False,
                                'timestamp': datetime.utcnow().isoformat()
                            }

                            # Store in cache
                            cache_manager.set(cache_key, json_data, ttl)

                            return jsonify(json_data)
                    except Exception as e:
                        current_app.logger.error(f"Error caching result for {func.__name__}: {e}")

                return result

            except Exception as e:
                current_app.logger.error(f"Cache decorator error in {func.__name__}: {e}")
                # Always return the function result, even if caching fails
                return func(*args, **kwargs)

        return wrapper
    return decorator


def create_cache_manager(app):
    """Factory function to create and configure cache manager"""
    cache_manager = AstroCacheManager(app)
    app.cache_manager = cache_manager
    return cache_manager
