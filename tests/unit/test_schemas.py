"""
Unit Tests for Pydantic Validation Schemas
Phase 2, Module 2.1: Schema Models Testing

Tests comprehensive input validation for all schema models including:
- BirthDataSchema validation
- Field-level validators
- Edge case handling
- Error messages
- Warning generation
- Data sanitization
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from astro_engine.schemas.birth_data import BirthDataSchema


class TestBirthDataSchemaValidData:
    """Test BirthDataSchema with valid inputs"""

    def test_valid_birth_data_accepts(self):
        """Test that valid birth data is accepted"""
        data = {
            'user_name': 'John Doe',
            'birth_date': '1990-05-15',
            'birth_time': '14:30:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5
        }

        schema = BirthDataSchema(**data)

        assert schema.user_name == 'John Doe'
        assert schema.birth_date == '1990-05-15'
        assert schema.birth_time == '14:30:00'
        assert schema.latitude == 28.6139
        assert schema.longitude == 77.209  # Rounded to 6 decimals
        assert schema.timezone_offset == 5.5

    def test_to_dict_method(self):
        """Test that to_dict() returns proper dictionary"""
        data = {
            'user_name': 'Test',
            'birth_date': '1990-05-15',
            'birth_time': '14:30:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5
        }

        schema = BirthDataSchema(**data)
        result = schema.to_dict()

        assert isinstance(result, dict)
        assert 'user_name' in result
        assert 'birth_date' in result
        assert result['latitude'] == schema.latitude

    def test_optional_ayanamsa_field(self):
        """Test that ayanamsa field is optional with default"""
        data = {
            'user_name': 'Test',
            'birth_date': '1990-05-15',
            'birth_time': '14:30:00',
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone_offset': 5.5
        }

        schema = BirthDataSchema(**data)

        # Should default to 'lahiri'
        assert schema.ayanamsa == 'lahiri'


class TestLatitudeValidation:
    """Test latitude field validation"""

    def test_latitude_valid_range(self):
        """Test latitudes within valid range"""
        valid_latitudes = [0, 28.6139, -33.8688, 90, -90, 45.5, -45.5]

        for lat in valid_latitudes:
            data = self._get_base_data(latitude=lat)
            schema = BirthDataSchema(**data)
            assert -90 <= schema.latitude <= 90

    def test_latitude_too_high_rejected(self):
        """Test latitude > 90 is rejected"""
        data = self._get_base_data(latitude=91)

        with pytest.raises(ValidationError) as exc_info:
            BirthDataSchema(**data)

        assert 'latitude' in str(exc_info.value).lower()

    def test_latitude_too_low_rejected(self):
        """Test latitude < -90 is rejected"""
        data = self._get_base_data(latitude=-91)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_latitude_string_rejected(self):
        """Test latitude as string is rejected"""
        data = self._get_base_data(latitude="not a number")

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_latitude_precision_rounded(self):
        """Test latitude is rounded to 6 decimal places"""
        data = self._get_base_data(latitude=28.123456789)

        schema = BirthDataSchema(**data)

        # Should be rounded to 6 decimals
        assert schema.latitude == 28.123457

    @staticmethod
    def _get_base_data(**overrides):
        """Helper to get base valid data with overrides"""
        base = {
            'user_name': 'Test',
            'birth_date': '1990-05-15',
            'birth_time': '14:30:00',
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone_offset': 5.5
        }
        base.update(overrides)
        return base


class TestLongitudeValidation:
    """Test longitude field validation"""

    def test_longitude_valid_range(self):
        """Test longitudes within valid range"""
        valid_longitudes = [0, 77.2090, -122.4194, 180, -180, 151.2093]

        for lon in valid_longitudes:
            data = TestLatitudeValidation._get_base_data(longitude=lon)
            schema = BirthDataSchema(**data)
            assert -180 <= schema.longitude <= 180

    def test_longitude_too_high_rejected(self):
        """Test longitude > 180 is rejected"""
        data = TestLatitudeValidation._get_base_data(longitude=181)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_longitude_too_low_rejected(self):
        """Test longitude < -180 is rejected"""
        data = TestLatitudeValidation._get_base_data(longitude=-181)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_longitude_precision_rounded(self):
        """Test longitude rounded to 6 decimals"""
        data = TestLatitudeValidation._get_base_data(longitude=77.123456789)

        schema = BirthDataSchema(**data)

        assert schema.longitude == 77.123457


class TestBirthDateValidation:
    """Test birth_date field validation"""

    def test_valid_date_format(self):
        """Test valid date format YYYY-MM-DD"""
        valid_dates = ['1990-05-15', '2000-01-01', '1985-12-31', '1950-06-15']

        for date in valid_dates:
            data = TestLatitudeValidation._get_base_data(birth_date=date)
            schema = BirthDataSchema(**data)
            assert schema.birth_date == date

    def test_invalid_date_format_rejected(self):
        """Test invalid date formats are rejected"""
        invalid_dates = [
            '15-05-1990',  # DD-MM-YYYY
            '05/15/1990',  # MM/DD/YYYY
            '1990.05.15',  # Dots
            '15 May 1990', # Text
            '1990-5-5',    # Missing leading zeros
        ]

        for date in invalid_dates:
            data = TestLatitudeValidation._get_base_data(birth_date=date)
            with pytest.raises(ValidationError):
                BirthDataSchema(**data)

    def test_invalid_calendar_date_rejected(self):
        """Test invalid calendar dates are rejected"""
        invalid_dates = [
            '1990-13-01',  # Month 13
            '1990-02-30',  # Feb 30
            '1990-04-31',  # April 31
            '1990-00-15',  # Month 0
            '1990-05-00',  # Day 0
        ]

        for date in invalid_dates:
            data = TestLatitudeValidation._get_base_data(birth_date=date)
            with pytest.raises(ValidationError):
                BirthDataSchema(**data)

    def test_leap_year_february_29_accepted(self):
        """Test that Feb 29 is accepted in leap years"""
        data = TestLatitudeValidation._get_base_data(birth_date='2000-02-29')

        schema = BirthDataSchema(**data)

        assert schema.birth_date == '2000-02-29'

    def test_non_leap_year_february_29_rejected(self):
        """Test that Feb 29 is rejected in non-leap years"""
        data = TestLatitudeValidation._get_base_data(birth_date='1900-02-29')

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_year_before_1900_rejected(self):
        """Test years before 1900 are rejected"""
        data = TestLatitudeValidation._get_base_data(birth_date='1850-05-15')

        with pytest.raises(ValidationError) as exc_info:
            BirthDataSchema(**data)

        assert '1900' in str(exc_info.value)

    def test_year_after_2100_rejected(self):
        """Test years after 2100 are rejected"""
        data = TestLatitudeValidation._get_base_data(birth_date='2150-05-15')

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_future_date_rejected(self):
        """Test future dates are rejected"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = TestLatitudeValidation._get_base_data(birth_date=tomorrow)

        with pytest.raises(ValidationError) as exc_info:
            BirthDataSchema(**data)

        assert 'future' in str(exc_info.value).lower()


class TestBirthTimeValidation:
    """Test birth_time field validation"""

    def test_valid_time_format(self):
        """Test valid time format HH:MM:SS"""
        valid_times = ['00:00:00', '12:30:45', '23:59:59', '14:30:00', '09:15:30']

        for time in valid_times:
            data = TestLatitudeValidation._get_base_data(birth_time=time)
            schema = BirthDataSchema(**data)
            assert schema.birth_time == time

    def test_invalid_time_format_rejected(self):
        """Test invalid time formats are rejected"""
        invalid_times = [
            '14:30',      # Missing seconds
            '2:30:00',    # Missing leading zero
            '14:30:00 PM', # 12-hour format
            '25:00:00',   # Invalid hour
            '14:60:00',   # Invalid minute
            '14:30:60',   # Invalid second
        ]

        for time in invalid_times:
            data = TestLatitudeValidation._get_base_data(birth_time=time)
            with pytest.raises(ValidationError):
                BirthDataSchema(**data)

    def test_hour_24_rejected(self):
        """Test that hour=24 is rejected (use 00:00:00 instead)"""
        data = TestLatitudeValidation._get_base_data(birth_time='24:00:00')

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_midnight_accepted(self):
        """Test midnight (00:00:00) is valid"""
        data = TestLatitudeValidation._get_base_data(birth_time='00:00:00')

        schema = BirthDataSchema(**data)

        assert schema.birth_time == '00:00:00'


class TestTimezoneOffsetValidation:
    """Test timezone_offset field validation"""

    def test_valid_timezone_offsets(self):
        """Test common timezone offsets"""
        valid_offsets = [
            0,      # UTC
            5.5,    # IST (India)
            -5.0,   # EST (US East)
            9.0,    # JST (Japan)
            -8.0,   # PST (US West)
            3.5,    # Iran
            -3.5,   # Newfoundland
            12.0,   # New Zealand
            -12.0,  # Baker Island
            14.0,   # Line Islands (easternmost)
        ]

        for offset in valid_offsets:
            data = TestLatitudeValidation._get_base_data(timezone_offset=offset)
            schema = BirthDataSchema(**data)
            assert schema.timezone_offset == offset

    def test_timezone_too_high_rejected(self):
        """Test timezone > 14 is rejected"""
        data = TestLatitudeValidation._get_base_data(timezone_offset=15)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_timezone_too_low_rejected(self):
        """Test timezone < -12 is rejected"""
        data = TestLatitudeValidation._get_base_data(timezone_offset=-13)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_timezone_precision_rounded(self):
        """Test timezone offset rounded to 1 decimal"""
        data = TestLatitudeValidation._get_base_data(timezone_offset=5.123456)

        schema = BirthDataSchema(**data)

        # Should be rounded to 1 decimal
        assert schema.timezone_offset == 5.1


class TestUserNameValidation:
    """Test user_name field validation and sanitization"""

    def test_valid_names_accepted(self):
        """Test various valid names"""
        valid_names = [
            'John Doe',
            'Ramesh Kumar',
            'Maria Garcia',
            'A',  # Single character OK
            'X' * 100,  # Max length OK
        ]

        for name in valid_names:
            data = TestLatitudeValidation._get_base_data(user_name=name)
            schema = BirthDataSchema(**data)
            assert schema.user_name == name.strip()

    def test_empty_name_rejected(self):
        """Test empty user name is rejected"""
        data = TestLatitudeValidation._get_base_data(user_name='')

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_whitespace_only_name_rejected(self):
        """Test name with only whitespace is rejected"""
        data = TestLatitudeValidation._get_base_data(user_name='   ')

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_name_too_long_rejected(self):
        """Test name longer than 100 chars is rejected"""
        data = TestLatitudeValidation._get_base_data(user_name='X' * 101)

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_name_with_leading_trailing_whitespace_stripped(self):
        """Test whitespace is stripped from name"""
        data = TestLatitudeValidation._get_base_data(user_name='  John Doe  ')

        schema = BirthDataSchema(**data)

        assert schema.user_name == 'John Doe'

    def test_control_characters_removed(self):
        """Test control characters are removed from name"""
        data = TestLatitudeValidation._get_base_data(user_name='John\x00Doe\x1F')

        schema = BirthDataSchema(**data)

        # Control characters should be removed
        assert '\x00' not in schema.user_name
        assert '\x1F' not in schema.user_name
        assert schema.user_name == 'JohnDoe'


class TestEdgeCaseWarnings:
    """Test edge case warning generation"""

    def test_polar_region_warning_north(self):
        """Test warning for Arctic region birth"""
        data = TestLatitudeValidation._get_base_data(latitude=75.0)

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert len(warnings) > 0
        assert any(w['code'] == 'POLAR_REGION' for w in warnings)
        assert any('Arctic' in w['message'] for w in warnings)

    def test_polar_region_warning_south(self):
        """Test warning for Antarctic region birth"""
        data = TestLatitudeValidation._get_base_data(latitude=-75.0)

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert any(w['code'] == 'POLAR_REGION' for w in warnings)
        assert any('Antarctic' in w['message'] for w in warnings)

    def test_midnight_birth_warning(self):
        """Test warning for midnight birth"""
        data = TestLatitudeValidation._get_base_data(birth_time='00:00:00')

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert any(w['code'] == 'MIDNIGHT_BIRTH' for w in warnings)

    def test_date_line_proximity_warning(self):
        """Test warning for birth near International Date Line"""
        data = TestLatitudeValidation._get_base_data(longitude=175.0)

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert any(w['code'] == 'DATE_LINE_PROXIMITY' for w in warnings)

    def test_equatorial_region_info(self):
        """Test info for birth near Equator"""
        data = TestLatitudeValidation._get_base_data(latitude=0.5)

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert any(w['code'] == 'EQUATORIAL_REGION' for w in warnings)

    def test_historical_date_warning(self):
        """Test warning for historical dates"""
        data = TestLatitudeValidation._get_base_data(birth_date='1920-05-15')

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        assert any(w['code'] == 'HISTORICAL_DATE' for w in warnings)

    def test_no_warnings_for_normal_data(self):
        """Test that normal data doesn't generate warnings"""
        data = {
            'user_name': 'Test User',
            'birth_date': '1990-05-15',  # Not historical, not current
            'birth_time': '14:30:00',    # Not midnight
            'latitude': 28.6,            # Not polar, not equator
            'longitude': 77.2,           # Not date line
            'timezone_offset': 5.5
        }

        schema = BirthDataSchema(**data)
        warnings = schema.get_warnings()

        # Should have no warnings for completely normal data
        assert len(warnings) == 0


class TestMissingFields:
    """Test handling of missing required fields"""

    def test_missing_user_name(self):
        """Test missing user_name is rejected"""
        data = {
            'birth_date': '1990-05-15',
            'birth_time': '14:30:00',
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone_offset': 5.5
        }

        with pytest.raises(ValidationError) as exc_info:
            BirthDataSchema(**data)

        assert 'user_name' in str(exc_info.value).lower()

    def test_missing_birth_date(self):
        """Test missing birth_date is rejected"""
        data = {
            'user_name': 'Test',
            'birth_time': '14:30:00',
            'latitude': 28.6,
            'longitude': 77.2,
            'timezone_offset': 5.5
        }

        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_all_fields_missing(self):
        """Test completely empty data is rejected"""
        with pytest.raises(ValidationError):
            BirthDataSchema(**{})


class TestSpecialCases:
    """Test special and boundary cases"""

    def test_leap_year_validation(self):
        """Test leap year Feb 29 handling"""
        # Leap year - should accept
        data = TestLatitudeValidation._get_base_data(birth_date='2000-02-29')
        schema = BirthDataSchema(**data)
        assert schema.birth_date == '2000-02-29'

        # Non-leap year - should reject
        data = TestLatitudeValidation._get_base_data(birth_date='1900-02-29')
        with pytest.raises(ValidationError):
            BirthDataSchema(**data)

    def test_equinox_dates(self):
        """Test births on equinox dates"""
        equinox_dates = ['1990-03-20', '1990-09-23']  # Approximate equinoxes

        for date in equinox_dates:
            data = TestLatitudeValidation._get_base_data(birth_date=date)
            schema = BirthDataSchema(**data)
            assert schema.birth_date == date

    def test_solstice_dates(self):
        """Test births on solstice dates"""
        solstice_dates = ['1990-06-21', '1990-12-21']  # Approximate solstices

        for date in solstice_dates:
            data = TestLatitudeValidation._get_base_data(birth_date=date)
            schema = BirthDataSchema(**data)
            assert schema.birth_date == date

    def test_daylight_saving_time_timezone(self):
        """Test timezone offsets during DST"""
        # US Eastern: -5 (standard) or -4 (DST)
        data = TestLatitudeValidation._get_base_data(timezone_offset=-4.0)
        schema = BirthDataSchema(**data)
        assert schema.timezone_offset == -4.0

    def test_extreme_latitude_boundaries(self):
        """Test exact latitude boundaries"""
        # Test 90 and -90 (North/South poles)
        for lat in [90.0, -90.0]:
            data = TestLatitudeValidation._get_base_data(latitude=lat)
            schema = BirthDataSchema(**data)
            assert schema.latitude == lat

    def test_extreme_longitude_boundaries(self):
        """Test exact longitude boundaries"""
        # Test 180 and -180 (International Date Line)
        for lon in [180.0, -180.0]:
            data = TestLatitudeValidation._get_base_data(longitude=lon)
            schema = BirthDataSchema(**data)
            assert schema.longitude == lon

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored (forward compatibility)"""
        data = TestLatitudeValidation._get_base_data(
            extra_field='should_be_ignored',
            another_field=123
        )

        # Should not raise error (extra='ignore' in config)
        schema = BirthDataSchema(**data)

        # Extra fields should not be in schema
        assert not hasattr(schema, 'extra_field')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
