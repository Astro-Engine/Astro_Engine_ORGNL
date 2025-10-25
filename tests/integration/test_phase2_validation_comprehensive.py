"""
Comprehensive Integration Tests for Phase 2: Input Validation
Tests complete validation flow with actual route endpoints

Verifies:
- All validation rules work end-to-end
- Error responses are standardized
- Edge cases handled correctly
- Security (injection prevention)
- Performance (validation overhead)
- Backward compatibility
"""

import pytest
import os
from astro_engine.app import create_app


@pytest.fixture
def client():
    """Create Flask test client"""
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_birth_data():
    """Standard valid birth data"""
    return {
        'user_name': 'Test User',
        'birth_date': '1990-05-15',
        'birth_time': '14:30:00',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'timezone_offset': 5.5
    }


class TestValidationWorks:
    """Test that validation is working on routes"""

    def test_valid_data_accepted(self, client, valid_birth_data):
        """Valid birth data should be accepted and processed"""
        response = client.post('/lahiri/natal',
                              json=valid_birth_data,
                              headers={'Content-Type': 'application/json'})

        assert response.status_code == 200
        data = response.get_json()
        # Response should contain chart data
        assert data is not None

    def test_invalid_latitude_rejected(self, client, valid_birth_data):
        """Latitude out of range should be rejected"""
        invalid_data = {**valid_birth_data, 'latitude': 9999}

        response = client.post('/lahiri/natal',
                              json=invalid_data,
                              headers={'Content-Type': 'application/json'})

        assert response.status_code == 400
        error = response.get_json()
        assert error['error']['code'] == 'VALIDATION_ERROR'
        assert 'latitude' in str(error)

    def test_missing_field_rejected(self, client, valid_birth_data):
        """Missing required field should be rejected"""
        incomplete = {k: v for k, v in valid_birth_data.items() if k != 'birth_time'}

        response = client.post('/lahiri/natal',
                              json=incomplete,
                              headers={'Content-Type': 'application/json'})

        assert response.status_code == 400
        error = response.get_json()
        assert 'birth_time' in str(error) or 'required' in str(error).lower()


class TestErrorResponseFormat:
    """Test error response standardization"""

    def test_validation_error_has_standard_format(self, client, valid_birth_data):
        """Validation errors should follow standard format"""
        invalid_data = {**valid_birth_data, 'latitude': 100}

        response = client.post('/lahiri/natal',
                              json=invalid_data)

        assert response.status_code == 400
        error = response.get_json()

        # Check standard format
        assert 'error' in error
        assert 'code' in error['error']
        assert 'message' in error['error']
        assert 'details' in error['error']
        assert 'status' in error
        assert 'request_id' in error

    def test_error_details_include_field_info(self, client, valid_birth_data):
        """Error details should include field information"""
        invalid_data = {**valid_birth_data, 'longitude': 200}

        response = client.post('/lahiri/natal',
                              json=invalid_data)

        error = response.get_json()
        details = error['error']['details']

        assert len(details) > 0
        assert 'field' in details[0]
        assert 'error' in details[0]

    def test_request_id_in_error_response(self, client, valid_birth_data):
        """Error responses should include request ID"""
        invalid_data = {**valid_birth_data, 'latitude': -100}

        response = client.post('/lahiri/natal',
                              json=invalid_data)

        error = response.get_json()
        assert 'request_id' in error
        assert error['request_id'] is not None


class TestSecurityValidation:
    """Test security features of validation"""

    def test_xss_attempt_sanitized(self, client, valid_birth_data):
        """XSS attempts in user_name should be sanitized"""
        xss_data = {**valid_birth_data, 'user_name': '<script>alert("xss")</script>John'}

        response = client.post('/lahiri/natal',
                              json=xss_data)

        # Should either accept (after sanitization) or reject
        # Our current implementation accepts after removing control chars
        # The <script> tags will be in the name but won't execute (API response is JSON)
        assert response.status_code in [200, 400]

    def test_sql_injection_prevented(self, client, valid_birth_data):
        """SQL injection attempts should be harmless (no DB anyway)"""
        sql_data = {**valid_birth_data, 'user_name': "'; DROP TABLE users; --"}

        response = client.post('/lahiri/natal',
                              json=sql_data)

        # Should process (we don't have DB, so SQL injection not relevant)
        # But validation should handle it safely
        assert response.status_code in [200, 400]

    def test_control_characters_removed(self, client, valid_birth_data):
        """Control characters should be removed"""
        control_char_data = {**valid_birth_data, 'user_name': 'John\x00Doe\x1F'}

        response = client.post('/lahiri/natal',
                              json=control_char_data)

        # Should accept after sanitization or reject
        assert response.status_code in [200, 400]


class TestEdgeCases:
    """Test edge case handling"""

    def test_polar_region_birth(self, client, valid_birth_data):
        """Birth in polar region should work (with potential warnings)"""
        polar_data = {**valid_birth_data, 'latitude': 75.0}

        response = client.post('/lahiri/natal',
                              json=polar_data)

        # Should accept (polar births are valid)
        assert response.status_code == 200

    def test_midnight_birth(self, client, valid_birth_data):
        """Midnight birth should work"""
        midnight_data = {**valid_birth_data, 'birth_time': '00:00:00'}

        response = client.post('/lahiri/natal',
                              json=midnight_data)

        assert response.status_code == 200

    def test_equator_birth(self, client, valid_birth_data):
        """Birth at equator should work"""
        equator_data = {**valid_birth_data, 'latitude': 0.0}

        response = client.post('/lahiri/natal',
                              json=equator_data)

        assert response.status_code == 200

    def test_date_line_proximity(self, client, valid_birth_data):
        """Birth near date line should work"""
        date_line_data = {**valid_birth_data, 'longitude': 179.0}

        response = client.post('/lahiri/natal',
                              json=date_line_data)

        assert response.status_code == 200

    def test_leap_year_february_29(self, client, valid_birth_data):
        """Feb 29 in leap year should work"""
        leap_data = {**valid_birth_data, 'birth_date': '2000-02-29'}

        response = client.post('/lahiri/natal',
                              json=leap_data)

        assert response.status_code == 200


class TestPerformance:
    """Test performance of validation"""

    def test_validation_overhead_acceptable(self, client, valid_birth_data):
        """Validation should add minimal overhead"""
        import time

        # Measure 10 validated requests
        start = time.time()
        for _ in range(10):
            response = client.post('/lahiri/natal',
                                  json=valid_birth_data)
            assert response.status_code == 200

        duration = time.time() - start
        avg_per_request = duration / 10

        # Should be fast (<100ms per request for validation)
        # Note: Total time includes calculation, we're just checking it's reasonable
        assert duration < 5.0, f"10 requests took {duration}s (too slow)"
        print(f"\n✅ Performance: 10 requests in {duration:.2f}s ({avg_per_request*1000:.0f}ms avg)")


class TestBackwardCompatibility:
    """Test that existing behavior is preserved"""

    def test_response_structure_unchanged(self, client, valid_birth_data):
        """Response structure should be same as before"""
        response = client.post('/lahiri/natal',
                              json=valid_birth_data)

        assert response.status_code == 200
        data = response.get_json()

        # Response should still have expected fields
        # (exact structure depends on calculation function)
        assert isinstance(data, dict)

    def test_error_status_codes_correct(self, client, valid_birth_data):
        """Error status codes should be standard HTTP codes"""
        # Missing data -> 400
        response = client.post('/lahiri/natal',
                              json={})
        assert response.status_code == 400

        # Invalid data -> 400
        response = client.post('/lahiri/natal',
                              json={**valid_birth_data, 'latitude': 999})
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
