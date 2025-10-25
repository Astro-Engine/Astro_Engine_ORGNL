"""
API Key Authentication Manager for Astro Engine
Module 1.1: API Key Infrastructure Setup

Provides secure API key generation, validation, and management
for service-to-service authentication.

Security Design:
- Environment-based key storage (no database)
- Simple comparison for service-to-service auth
- Support for multiple API keys
- Configurable exempt routes
- Detailed logging and monitoring

Usage:
    from auth_manager import generate_api_key, validate_api_key

    # Generate new key
    key = generate_api_key(service='corp_backend')

    # Validate incoming request
    is_valid = validate_api_key('astro_corp_abc123...')
"""

import secrets
import os
import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages API key generation, validation, and lifecycle.

    Designed for service-to-service authentication in Astro Engine.
    Keys are stored in environment variables for simplicity and security.
    """

    def __init__(self, app=None):
        """
        Initialize API Key Manager

        Args:
            app: Flask application instance (optional)
        """
        self.valid_keys: List[str] = []
        self.exempt_routes: List[str] = []
        self.stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'exempt_requests': 0
        }

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize with Flask app

        Loads valid API keys from environment variables and
        configures exempt routes.

        Args:
            app: Flask application instance
        """
        # Load valid API keys from environment
        # Format: VALID_API_KEYS=key1,key2,key3
        keys_env = os.getenv('VALID_API_KEYS', '')

        if keys_env:
            self.valid_keys = [key.strip() for key in keys_env.split(',') if key.strip()]
            logger.info(f"✅ Loaded {len(self.valid_keys)} valid API keys")
        else:
            logger.warning("⚠️  No VALID_API_KEYS configured - authentication disabled")

        # Configure exempt routes (no authentication required)
        exempt_routes_env = os.getenv('AUTH_EXEMPT_ROUTES', '/health,/metrics')
        self.exempt_routes = [route.strip() for route in exempt_routes_env.split(',') if route.strip()]
        logger.info(f"📋 Exempt routes: {', '.join(self.exempt_routes)}")

        # Store in app for access
        app.api_key_manager = self

    def is_enabled(self) -> bool:
        """
        Check if API key authentication is enabled

        Returns:
            bool: True if at least one valid key is configured
        """
        enabled = len(self.valid_keys) > 0
        return enabled

    def is_route_exempt(self, path: str) -> bool:
        """
        Check if a route is exempt from authentication

        Args:
            path: Request path (e.g., '/health', '/lahiri/natal')

        Returns:
            bool: True if route is exempt
        """
        # Check exact match
        if path in self.exempt_routes:
            return True

        # Check prefix match (for /metrics/*, /health/*, etc.)
        for exempt_route in self.exempt_routes:
            if path.startswith(exempt_route):
                return True

        return False

    def validate_api_key(self, api_key: Optional[str]) -> bool:
        """
        Validate an API key

        Args:
            api_key: The API key to validate (from X-API-Key header)

        Returns:
            bool: True if valid, False otherwise
        """
        self.stats['total_validations'] += 1

        # If authentication not enabled, allow all requests
        if not self.is_enabled():
            logger.debug("Authentication not enabled, allowing request")
            self.stats['successful_validations'] += 1
            return True

        # Check if key is valid
        if api_key and api_key in self.valid_keys:
            self.stats['successful_validations'] += 1
            logger.debug(f"✅ Valid API key: {self._mask_key(api_key)}")
            return True
        else:
            self.stats['failed_validations'] += 1
            logger.warning(f"❌ Invalid API key attempt: {self._mask_key(api_key)}")
            return False

    def get_key_metadata(self, api_key: str) -> Dict:
        """
        Get metadata about an API key

        Args:
            api_key: The API key to analyze

        Returns:
            dict: Metadata including prefix, service, masked key
        """
        if not api_key:
            return {'valid': False}

        # Extract service from key prefix
        parts = api_key.split('_')
        service = parts[1] if len(parts) > 1 else 'unknown'

        return {
            'valid': api_key in self.valid_keys,
            'service': service,
            'prefix': parts[0] if parts else '',
            'masked_key': self._mask_key(api_key)
        }

    def get_stats(self) -> Dict:
        """
        Get authentication statistics

        Returns:
            dict: Statistics about API key validations
        """
        total = self.stats['total_validations']
        success_rate = (self.stats['successful_validations'] / max(total, 1)) * 100

        return {
            **self.stats,
            'success_rate': round(success_rate, 2),
            'authentication_enabled': self.is_enabled(),
            'total_valid_keys': len(self.valid_keys),
            'exempt_routes_count': len(self.exempt_routes)
        }

    @staticmethod
    def _mask_key(api_key: Optional[str]) -> str:
        """
        Mask API key for logging (show first 12 chars only)

        Args:
            api_key: API key to mask

        Returns:
            str: Masked key (e.g., "astro_corp_a...***")
        """
        if not api_key:
            return 'None'

        if len(api_key) <= 12:
            return api_key[:4] + '***'

        return api_key[:12] + '***'


# Standalone utility functions

def generate_api_key(service: str = 'service', prefix: str = 'astro') -> str:
    """
    Generate a secure API key

    Format: {prefix}_{service}_{random_32_chars}
    Example: astro_corp_backend_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

    Args:
        service: Service name (e.g., 'corp_backend', 'astro_ratan', 'report')
        prefix: Key prefix (default: 'astro')

    Returns:
        str: Secure API key (64 characters)

    Example:
        >>> key = generate_api_key(service='corp_backend')
        >>> print(key)
        astro_corp_backend_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    """
    # Generate cryptographically secure random string
    random_part = secrets.token_urlsafe(32)[:32]  # 32 chars

    # Format: prefix_service_random
    api_key = f"{prefix}_{service}_{random_part}"

    logger.info(f"🔑 Generated API key for service: {service}")
    logger.info(f"   Key prefix: {prefix}_{service}_")
    logger.info(f"   Full key length: {len(api_key)} characters")

    return api_key


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate an API key against environment configuration

    This is a standalone function for quick validation without
    requiring the full APIKeyManager instance.

    Args:
        api_key: The API key to validate (can be None)

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> os.environ['VALID_API_KEYS'] = 'astro_corp_abc,astro_ratan_xyz'
        >>> validate_api_key('astro_corp_abc')
        True
        >>> validate_api_key('invalid_key')
        False
    """
    # Get valid keys from environment
    keys_env = os.getenv('VALID_API_KEYS', '')

    # If no keys configured, authentication is disabled
    if not keys_env:
        logger.warning("⚠️  VALID_API_KEYS not configured - authentication disabled")
        return True  # Allow all requests when auth not configured

    # If no API key provided, reject
    if not api_key:
        logger.warning("❌ No API key provided")
        return False

    valid_keys = [key.strip() for key in keys_env.split(',') if key.strip()]

    # Check if provided key is in valid keys
    is_valid = api_key in valid_keys

    if not is_valid:
        logger.warning(f"❌ Invalid API key attempt: {api_key[:12] if len(api_key) >= 12 else api_key}***")

    return is_valid


def get_api_key_from_request(request) -> Optional[str]:
    """
    Extract API key from Flask request

    Checks multiple sources in order:
    1. X-API-Key header (recommended)
    2. Authorization: Bearer <key> header
    3. api_key query parameter (not recommended for production)

    Args:
        request: Flask request object

    Returns:
        str: API key if found, None otherwise

    Example:
        >>> api_key = get_api_key_from_request(request)
        >>> if not api_key:
        ...     return jsonify({'error': 'API key required'}), 401
    """
    # Method 1: X-API-Key header (recommended)
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return api_key.strip()

    # Method 2: Authorization: Bearer header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.replace('Bearer ', '').strip()

    # Method 3: Query parameter (for testing only, not recommended)
    # Only allow in development
    if os.getenv('FLASK_ENV') == 'development':
        api_key = request.args.get('api_key')
        if api_key:
            logger.warning("⚠️  API key sent via query parameter (not secure for production)")
            return api_key.strip()

    return None


def create_api_key_manager(app):
    """
    Factory function to create and configure API key manager

    Args:
        app: Flask application instance

    Returns:
        APIKeyManager: Configured manager instance
    """
    manager = APIKeyManager(app)
    return manager


# Critical Security Notes:
#
# 1. NEVER log full API keys - always use _mask_key()
# 2. NEVER commit API keys to git - use environment variables
# 3. NEVER send API keys in URLs (query params) in production
# 4. ALWAYS use HTTPS in production
# 5. ROTATE keys regularly (every 90 days recommended)
# 6. REVOKE compromised keys immediately
# 7. USE separate keys for each service (never share)
# 8. MONITOR failed authentication attempts (potential attacks)
