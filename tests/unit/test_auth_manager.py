"""
Unit Tests for API Key Authentication Manager
Module 1.1 Testing: API Key Infrastructure Setup

Tests all functionality of auth_manager.py including:
- API key generation
- API key validation
- Key format verification
- Manager initialization
- Statistics tracking
- Security features
"""

import pytest
import os
from unittest.mock import Mock, patch
from astro_engine.auth_manager import (
    generate_api_key,
    validate_api_key,
    get_api_key_from_request,
    APIKeyManager,
    create_api_key_manager
)


class TestAPIKeyGeneration:
    """Test API key generation functionality"""

    def test_generate_api_key_format(self):
        """Test that generated key follows correct format"""
        key = generate_api_key(service='test_service')

        # Check format: prefix_service_random
        assert key.startswith('astro_test_service_')
        assert len(key) > 40  # prefix + service + 32 char random

    def test_generate_api_key_custom_prefix(self):
        """Test key generation with custom prefix"""
        key = generate_api_key(service='custom', prefix='myapp')

        assert key.startswith('myapp_custom_')

    def test_generate_api_key_uniqueness(self):
        """Test that generated keys are unique"""
        keys = [generate_api_key(service='test') for _ in range(10)]

        # All keys should be unique
        assert len(keys) == len(set(keys))

    def test_generate_api_key_length(self):
        """Test that generated keys have sufficient entropy"""
        key = generate_api_key(service='test')

        # Should be long enough for security (>32 chars)
        assert len(key) >= 40

    def test_generate_api_key_for_known_services(self):
        """Test key generation for actual services"""
        services = ['corp_backend', 'astro_ratan', 'report_engine', 'testing']

        for service in services:
            key = generate_api_key(service=service)
            assert f'astro_{service}_' in key


class TestAPIKeyValidation:
    """Test API key validation functionality"""

    def test_validate_valid_key(self):
        """Test validation of a valid API key"""
        test_key = 'astro_test_abc123xyz'

        with patch.dict(os.environ, {'VALID_API_KEYS': test_key}):
            assert validate_api_key(test_key) == True

    def test_validate_invalid_key(self):
        """Test validation of an invalid API key"""
        with patch.dict(os.environ, {'VALID_API_KEYS': 'astro_valid_key'}):
            assert validate_api_key('astro_invalid_key') == False

    def test_validate_empty_key(self):
        """Test validation of empty key"""
        with patch.dict(os.environ, {'VALID_API_KEYS': 'astro_valid_key'}):
            assert validate_api_key('') == False

    def test_validate_none_key(self):
        """Test validation of None key"""
        with patch.dict(os.environ, {'VALID_API_KEYS': 'astro_valid_key'}):
            assert validate_api_key(None) == False

    def test_validate_multiple_valid_keys(self):
        """Test validation with multiple valid keys"""
        keys = 'astro_corp_abc,astro_ratan_xyz,astro_report_def'

        with patch.dict(os.environ, {'VALID_API_KEYS': keys}):
            assert validate_api_key('astro_corp_abc') == True
            assert validate_api_key('astro_ratan_xyz') == True
            assert validate_api_key('astro_report_def') == True
            assert validate_api_key('astro_invalid') == False

    def test_validate_when_no_keys_configured(self):
        """Test that validation passes when no keys configured (auth disabled)"""
        with patch.dict(os.environ, {'VALID_API_KEYS': ''}, clear=True):
            # When no keys configured, auth is disabled, all requests allowed
            assert validate_api_key('any_key') == True

    def test_validate_key_with_whitespace(self):
        """Test validation handles whitespace in environment config"""
        keys = ' astro_key1 , astro_key2 , astro_key3 '

        with patch.dict(os.environ, {'VALID_API_KEYS': keys}):
            assert validate_api_key('astro_key1') == True
            assert validate_api_key('astro_key2') == True


class TestAPIKeyManager:
    """Test APIKeyManager class functionality"""

    def test_manager_initialization(self):
        """Test manager initialization without app"""
        manager = APIKeyManager()

        assert manager.valid_keys == []
        assert manager.exempt_routes == []
        assert manager.stats['total_validations'] == 0

    def test_manager_initialization_with_app(self):
        """Test manager initialization with Flask app"""
        mock_app = Mock()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'key1,key2'}):
            manager = APIKeyManager(mock_app)

            assert len(manager.valid_keys) == 2
            assert 'key1' in manager.valid_keys
            assert 'key2' in manager.valid_keys

    def test_manager_is_enabled_true(self):
        """Test is_enabled returns True when keys configured"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'test_key'}):
            manager.init_app(Mock())
            assert manager.is_enabled() == True

    def test_manager_is_enabled_false(self):
        """Test is_enabled returns False when no keys configured"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {}, clear=True):
            manager.init_app(Mock())
            assert manager.is_enabled() == False

    def test_manager_is_route_exempt(self):
        """Test route exemption checking"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'AUTH_EXEMPT_ROUTES': '/health,/metrics'}):
            manager.init_app(Mock())

            assert manager.is_route_exempt('/health') == True
            assert manager.is_route_exempt('/metrics') == True
            assert manager.is_route_exempt('/lahiri/natal') == False

    def test_manager_is_route_exempt_prefix_match(self):
        """Test route exemption with prefix matching"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'AUTH_EXEMPT_ROUTES': '/health,/metrics'}):
            manager.init_app(Mock())

            # Should match /metrics and /metrics/*
            assert manager.is_route_exempt('/metrics') == True
            assert manager.is_route_exempt('/metrics/json') == True
            assert manager.is_route_exempt('/metrics/performance') == True

    def test_manager_validate_api_key(self):
        """Test manager's validate_api_key method"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'valid_key'}):
            manager.init_app(Mock())

            assert manager.validate_api_key('valid_key') == True
            assert manager.validate_api_key('invalid_key') == False

    def test_manager_statistics_tracking(self):
        """Test that manager tracks validation statistics"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'valid_key'}):
            manager.init_app(Mock())

            # Initial stats
            assert manager.stats['total_validations'] == 0
            assert manager.stats['successful_validations'] == 0
            assert manager.stats['failed_validations'] == 0

            # Valid validation
            manager.validate_api_key('valid_key')
            assert manager.stats['total_validations'] == 1
            assert manager.stats['successful_validations'] == 1
            assert manager.stats['failed_validations'] == 0

            # Invalid validation
            manager.validate_api_key('invalid_key')
            assert manager.stats['total_validations'] == 2
            assert manager.stats['successful_validations'] == 1
            assert manager.stats['failed_validations'] == 1

    def test_manager_get_stats(self):
        """Test get_stats returns complete statistics"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'key1,key2'}):
            manager.init_app(Mock())

            manager.validate_api_key('key1')
            manager.validate_api_key('invalid')

            stats = manager.get_stats()

            assert 'total_validations' in stats
            assert 'successful_validations' in stats
            assert 'failed_validations' in stats
            assert 'success_rate' in stats
            assert 'authentication_enabled' in stats
            assert 'total_valid_keys' in stats

            assert stats['total_validations'] == 2
            assert stats['successful_validations'] == 1
            assert stats['failed_validations'] == 1
            assert stats['success_rate'] == 50.0
            assert stats['total_valid_keys'] == 2

    def test_manager_get_key_metadata(self):
        """Test getting metadata about an API key"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'astro_corp_abc123'}):
            manager.init_app(Mock())

            metadata = manager.get_key_metadata('astro_corp_abc123')

            assert metadata['valid'] == True
            assert metadata['service'] == 'corp'
            assert metadata['prefix'] == 'astro'
            assert 'masked_key' in metadata

    def test_manager_mask_key(self):
        """Test API key masking for security"""
        manager = APIKeyManager()

        # Long key
        masked = manager._mask_key('astro_corp_backend_abc123xyz789')
        assert masked == 'astro_corp_b***'
        assert 'abc123xyz789' not in masked

        # Short key
        masked = manager._mask_key('short')
        assert masked == 'shor***'

        # None key
        masked = manager._mask_key(None)
        assert masked == 'None'


class TestGetAPIKeyFromRequest:
    """Test extracting API key from Flask request"""

    def test_get_key_from_x_api_key_header(self):
        """Test extracting key from X-API-Key header (recommended method)"""
        mock_request = Mock()
        mock_request.headers.get.return_value = 'astro_test_key'
        mock_request.args.get.return_value = None

        key = get_api_key_from_request(mock_request)

        assert key == 'astro_test_key'
        mock_request.headers.get.assert_called()

    def test_get_key_from_bearer_token(self):
        """Test extracting key from Authorization: Bearer header"""
        mock_request = Mock()
        mock_request.headers.get.side_effect = lambda h: {
            'X-API-Key': None,
            'Authorization': 'Bearer astro_bearer_key'
        }.get(h)
        mock_request.args.get.return_value = None

        key = get_api_key_from_request(mock_request)

        assert key == 'astro_bearer_key'

    def test_get_key_from_query_param_in_dev(self):
        """Test extracting key from query parameter (dev only)"""
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        mock_request.args.get.return_value = 'astro_query_key'

        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            key = get_api_key_from_request(mock_request)
            assert key == 'astro_query_key'

    def test_get_key_query_param_blocked_in_production(self):
        """Test that query param method is blocked in production"""
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        mock_request.args.get.return_value = 'astro_query_key'

        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            key = get_api_key_from_request(mock_request)
            assert key is None  # Query param not allowed in production

    def test_get_key_when_none_present(self):
        """Test returns None when no API key found"""
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        mock_request.args.get.return_value = None

        key = get_api_key_from_request(mock_request)

        assert key is None

    def test_get_key_strips_whitespace(self):
        """Test that extracted keys have whitespace stripped"""
        mock_request = Mock()
        mock_request.headers.get.return_value = '  astro_test_key  '

        key = get_api_key_from_request(mock_request)

        assert key == 'astro_test_key'
        assert key == key.strip()


class TestCreateAPIKeyManager:
    """Test factory function for creating manager"""

    def test_create_manager_returns_instance(self):
        """Test factory creates APIKeyManager instance"""
        mock_app = Mock()

        manager = create_api_key_manager(mock_app)

        assert isinstance(manager, APIKeyManager)

    def test_create_manager_initializes_app(self):
        """Test factory initializes with app"""
        mock_app = Mock()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'key1'}):
            manager = create_api_key_manager(mock_app)

            assert len(manager.valid_keys) == 1
            assert 'key1' in manager.valid_keys


class TestSecurityFeatures:
    """Test security-related features"""

    def test_key_masking_hides_sensitive_data(self):
        """Test that key masking prevents key exposure in logs"""
        manager = APIKeyManager()

        key = 'astro_corp_backend_secretkey123456'
        masked = manager._mask_key(key)

        # Should not contain the secret part
        assert 'secretkey123456' not in masked
        # Should contain prefix only
        assert masked.startswith('astro_corp_b')
        assert masked.endswith('***')

    def test_validation_logs_failures(self):
        """Test that failed validations are logged"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'valid_key'}):
            manager.init_app(Mock())

            # This should log a warning
            with patch('astro_engine.auth_manager.logger') as mock_logger:
                manager.validate_api_key('invalid_key')
                mock_logger.warning.assert_called()

    def test_no_api_keys_in_stats_output(self):
        """Test that stats don't expose actual API keys"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {'VALID_API_KEYS': 'secret_key_123'}):
            manager.init_app(Mock())
            stats = manager.get_stats()

            # Stats should not contain actual keys
            stats_str = str(stats)
            assert 'secret_key_123' not in stats_str

            # Should only show count
            assert stats['total_valid_keys'] == 1


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_valid_keys_disables_auth(self):
        """Test that empty VALID_API_KEYS disables authentication"""
        with patch.dict(os.environ, {'VALID_API_KEYS': ''}, clear=True):
            # Should allow any request (auth disabled)
            assert validate_api_key('any_key') == True

    def test_validate_with_special_characters(self):
        """Test validation with special characters in key"""
        special_key = 'astro_test_!@#$%^&*()'

        with patch.dict(os.environ, {'VALID_API_KEYS': special_key}):
            assert validate_api_key(special_key) == True

    def test_validate_case_sensitive(self):
        """Test that validation is case-sensitive"""
        with patch.dict(os.environ, {'VALID_API_KEYS': 'astro_Key_ABC'}):
            assert validate_api_key('astro_Key_ABC') == True
            assert validate_api_key('astro_key_abc') == False
            assert validate_api_key('ASTRO_KEY_ABC') == False

    def test_manager_handles_missing_env_vars(self):
        """Test manager handles missing environment variables gracefully"""
        manager = APIKeyManager()

        # Remove all auth-related env vars
        with patch.dict(os.environ, {}, clear=True):
            manager.init_app(Mock())

            # Should initialize without errors
            assert manager.is_enabled() == False
            # Default exempt routes should be set (health, metrics)
            assert isinstance(manager.exempt_routes, list)


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_authentication_flow(self):
        """Test complete authentication flow from generation to validation"""
        # 1. Generate keys for services
        corp_key = generate_api_key(service='corp_backend')
        ratan_key = generate_api_key(service='astro_ratan')
        report_key = generate_api_key(service='report_engine')

        # 2. Configure environment
        all_keys = f'{corp_key},{ratan_key},{report_key}'

        with patch.dict(os.environ, {'VALID_API_KEYS': all_keys}):
            # 3. Create manager
            manager = APIKeyManager()
            manager.init_app(Mock())

            # 4. Validate all keys work
            assert manager.validate_api_key(corp_key) == True
            assert manager.validate_api_key(ratan_key) == True
            assert manager.validate_api_key(report_key) == True

            # 5. Validate invalid key fails
            assert manager.validate_api_key('fake_key') == False

            # 6. Check statistics
            stats = manager.get_stats()
            assert stats['total_validations'] == 4
            assert stats['successful_validations'] == 3
            assert stats['failed_validations'] == 1
            assert stats['success_rate'] == 75.0

    def test_exempt_routes_bypass_validation(self):
        """Test that exempt routes don't require validation"""
        manager = APIKeyManager()

        with patch.dict(os.environ, {
            'VALID_API_KEYS': 'test_key',
            'AUTH_EXEMPT_ROUTES': '/health,/metrics'
        }):
            manager.init_app(Mock())

            # These routes are exempt
            assert manager.is_route_exempt('/health') == True
            assert manager.is_route_exempt('/metrics') == True
            assert manager.is_route_exempt('/metrics/json') == True

            # These routes need auth
            assert manager.is_route_exempt('/lahiri/natal') == False
            assert manager.is_route_exempt('/kp/calculate') == False


# Pytest fixtures
@pytest.fixture
def mock_app():
    """Create a mock Flask app for testing"""
    app = Mock()
    app.logger = Mock()
    return app


@pytest.fixture
def valid_api_keys():
    """Provide valid test API keys"""
    return {
        'corp': 'astro_corp_backend_test123',
        'ratan': 'astro_ratan_test456',
        'report': 'astro_report_test789'
    }


@pytest.fixture
def api_key_manager(mock_app, valid_api_keys):
    """Create configured APIKeyManager for testing"""
    keys_str = ','.join(valid_api_keys.values())

    with patch.dict(os.environ, {'VALID_API_KEYS': keys_str}):
        manager = APIKeyManager(mock_app)
        return manager


# Performance tests
class TestPerformance:
    """Test performance characteristics"""

    def test_validation_is_fast(self):
        """Test that validation completes quickly"""
        import time

        manager = APIKeyManager()
        with patch.dict(os.environ, {'VALID_API_KEYS': 'test_key'}):
            manager.init_app(Mock())

            start = time.time()
            for _ in range(1000):
                manager.validate_api_key('test_key')
            duration = time.time() - start

            # Should complete 1000 validations in < 100ms
            assert duration < 0.1

    def test_key_generation_is_secure(self):
        """Test that generated keys have high entropy"""
        keys = [generate_api_key() for _ in range(100)]

        # All should be unique (no collisions)
        assert len(keys) == len(set(keys))

        # All should have good length
        assert all(len(k) >= 40 for k in keys)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
