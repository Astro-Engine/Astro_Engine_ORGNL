"""
HTTP Caching Headers for Astro Engine
Phase 16: HTTP Caching Headers

Implements browser and CDN caching through HTTP headers.

Benefits:
- Reduced server load (repeated requests cached by browser/CDN)
- Faster response times for cached data
- Lower bandwidth usage
- Better mobile performance

Caching Strategy:
- Natal charts: 24 hours (birth data doesn't change)
- Divisional charts: 24 hours (same reason)
- Transit charts: 1 hour (changes frequently)
- Dashas: 7 days (relatively static)
"""

import hashlib
import json
from typing import Optional, Dict, Any
from flask import request, make_response
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 16, MODULE 16.1: CACHE-CONTROL HEADER
# =============================================================================

# Cache duration by endpoint type (in seconds)
CACHE_DURATIONS = {
    'natal': 86400,          # 24 hours (birth data doesn't change)
    'navamsa': 86400,        # 24 hours
    'divisional': 86400,     # 24 hours
    'transit': 3600,         # 1 hour (changes frequently)
    'dasha': 604800,         # 7 days
    'yoga': 86400,           # 24 hours
    'dosha': 86400,          # 24 hours
    'default': 3600          # 1 hour default
}


def get_cache_duration(endpoint_path: str) -> int:
    """
    Get appropriate cache duration for endpoint

    Phase 16, Module 16.1: Cache duration strategy

    Args:
        endpoint_path: Request path (e.g., '/lahiri/natal')

    Returns:
        int: Cache duration in seconds
    """
    # Check endpoint type
    if 'natal' in endpoint_path and 'transit' not in endpoint_path:
        return CACHE_DURATIONS['natal']
    elif 'navamsa' in endpoint_path:
        return CACHE_DURATIONS['navamsa']
    elif 'transit' in endpoint_path:
        return CACHE_DURATIONS['transit']
    elif 'dasha' in endpoint_path:
        return CACHE_DURATIONS['dasha']
    elif any(d in endpoint_path for d in ['d2', 'd3', 'd4', 'd7', 'd9', 'd10', 'd12']):
        return CACHE_DURATIONS['divisional']
    elif 'yoga' in endpoint_path:
        return CACHE_DURATIONS['yoga']
    elif 'dosha' in endpoint_path:
        return CACHE_DURATIONS['dosha']
    else:
        return CACHE_DURATIONS['default']


def add_cache_control_header(response, endpoint_path: str):
    """
    Add Cache-Control header to response

    Phase 16, Module 16.1: Cache-Control implementation

    Args:
        response: Flask response object
        endpoint_path: Request path

    Returns:
        Response with Cache-Control header
    """
    duration = get_cache_duration(endpoint_path)

    # Public caching (can be cached by browsers and CDNs)
    response.headers['Cache-Control'] = f'public, max-age={duration}'

    # Also add Expires header for HTTP/1.0 compatibility
    from datetime import datetime, timedelta
    expires = datetime.utcnow() + timedelta(seconds=duration)
    response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response


# =============================================================================
# PHASE 16, MODULE 16.2: ETAG GENERATION
# =============================================================================

def generate_etag(data: Dict[str, Any]) -> str:
    """
    Generate ETag from request data

    Phase 16, Module 16.2: ETag generation

    Args:
        data: Request data (birth data)

    Returns:
        str: ETag value (MD5 hash)

    ETag is based on input data, so same input = same ETag.
    Enables 304 Not Modified responses for repeated requests.
    """
    try:
        # Normalize data for consistent ETag
        normalized = {
            'birth_date': data.get('birth_date', ''),
            'birth_time': data.get('birth_time', ''),
            'latitude': round(float(data.get('latitude', 0)), 6),
            'longitude': round(float(data.get('longitude', 0)), 6),
            'timezone_offset': float(data.get('timezone_offset', 0))
        }

        # Generate MD5 hash
        data_string = json.dumps(normalized, sort_keys=True)
        etag = hashlib.md5(data_string.encode()).hexdigest()

        return f'"{etag}"'  # ETags should be quoted

    except Exception as e:
        logger.error(f"Error generating ETag: {e}")
        return '"default-etag"'


def add_etag_header(response, request_data: Optional[Dict] = None):
    """
    Add ETag header to response

    Phase 16, Module 16.2: ETag header

    Args:
        response: Flask response object
        request_data: Request data for ETag generation

    Returns:
        Response with ETag header
    """
    if request_data:
        etag = generate_etag(request_data)
        response.headers['ETag'] = etag

    return response


# =============================================================================
# PHASE 16, MODULE 16.3: CONDITIONAL REQUEST SUPPORT
# =============================================================================

def check_if_none_match(request_data: Dict[str, Any]) -> Optional[tuple]:
    """
    Check If-None-Match header for conditional requests

    Phase 16, Module 16.3: Conditional request (304 Not Modified)

    Args:
        request_data: Request data

    Returns:
        tuple: (304 response, headers) if matches, None otherwise

    If client's ETag matches current data, return 304 Not Modified
    instead of recalculating. Saves bandwidth and computation.
    """
    client_etag = request.headers.get('If-None-Match')

    if client_etag:
        # Generate ETag for current request
        current_etag = generate_etag(request_data)

        if client_etag == current_etag:
            # Data hasn't changed, return 304
            logger.info(f"✅ ETag match - returning 304 Not Modified")

            from flask import make_response
            response = make_response('', 304)
            response.headers['ETag'] = current_etag
            response.headers['Cache-Control'] = f'public, max-age={CACHE_DURATIONS["natal"]}'

            return response

    return None  # No match, proceed with calculation


# =============================================================================
# PHASE 16, MODULE 16.4: VARY HEADER
# =============================================================================

def add_vary_header(response):
    """
    Add Vary header to response

    Phase 16, Module 16.4: Vary header configuration

    Tells caches which request headers affect the response.

    Args:
        response: Flask response object

    Returns:
        Response with Vary header
    """
    # Response varies based on:
    # - Accept-Encoding (compression)
    # - X-API-Key (different services might get different rate limits)
    response.headers['Vary'] = 'Accept-Encoding, X-API-Key'

    return response


# =============================================================================
# PHASE 16, MODULE 16.5: CDN-READY HEADERS
# =============================================================================

def add_cdn_headers(response, endpoint_path: str, request_data: Optional[Dict] = None):
    """
    Add all CDN-ready caching headers

    Phase 16, Module 16.5: Complete CDN optimization

    Combines all caching headers for optimal CDN performance.

    Args:
        response: Flask response object
        endpoint_path: Request path
        request_data: Request data (for ETag)

    Returns:
        Response with all caching headers
    """
    # Add Cache-Control
    response = add_cache_control_header(response, endpoint_path)

    # Add ETag
    if request_data:
        response = add_etag_header(response, request_data)

    # Add Vary
    response = add_vary_header(response)

    return response


# Helper decorator for routes
def with_http_caching(func):
    """
    Decorator to add HTTP caching headers to route

    Phase 16: Complete HTTP caching

    Usage:
        @bp.route('/lahiri/natal', methods=['POST'])
        @with_http_caching
        def natal_chart():
            # ... calculation
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get request data
        request_data = request.get_json() if request.method == 'POST' else None

        # Check If-None-Match (conditional request)
        if request_data:
            conditional_response = check_if_none_match(request_data)
            if conditional_response:
                return conditional_response

        # Execute route function
        response = func(*args, **kwargs)

        # Add caching headers if response is successful
        if hasattr(response, 'status_code') and response.status_code == 200:
            response = add_cdn_headers(response, request.path, request_data)

        return response

    return wrapper


# Critical Notes:
#
# 1. USE appropriate cache durations (natal: 24h, transit: 1h)
# 2. GENERATE ETags from input data (deterministic)
# 3. SUPPORT If-None-Match (304 Not Modified)
# 4. ADD Vary header (tells CDN what affects response)
# 5. ONLY cache successful responses (200 OK)
# 6. DON'T cache errors or validation failures
# 7. TEST with actual HTTP clients (curl, browsers)
# 8. MONITOR cache hit rates (in CDN dashboard)
