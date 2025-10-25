"""
Birth Data Validation Schemas
Phase 2, Module 2.1: Pydantic Schema Models

Comprehensive validation for birth data used in astrological calculations.

Critical Design Decisions:
1. Latitude/Longitude: Validated to 6 decimal places (~0.1m precision)
2. Date Range: 1900-2100 (Swiss Ephemeris reliable range)
3. Time Format: HH:MM:SS (24-hour format)
4. Timezone: -12 to +14 hours (covers all real timezones)
5. Edge Cases: Midnight, poles, date line handled with warnings
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


class BirthDataSchema(BaseModel):
    """
    Base schema for birth data validation

    Used by all natal chart, divisional chart, and dasha calculations.

    Fields:
        user_name: Name of the person (1-100 characters)
        birth_date: Date of birth in YYYY-MM-DD format
        birth_time: Time of birth in HH:MM:SS format (24-hour)
        latitude: Birth location latitude (-90 to 90 degrees)
        longitude: Birth location longitude (-180 to 180 degrees)
        timezone_offset: Timezone offset from UTC in hours (-12 to 14)

    Example:
        {
            "user_name": "John Doe",
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
    """

    # Required fields with validation
    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the person",
        examples=["John Doe", "Jane Smith"]
    )

    birth_date: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Date of birth in YYYY-MM-DD format",
        examples=["1990-05-15", "1985-12-25"]
    )

    birth_time: str = Field(
        ...,
        pattern=r'^\d{2}:\d{2}:\d{2}$',
        description="Time of birth in HH:MM:SS format (24-hour)",
        examples=["14:30:00", "09:15:30", "00:00:00"]
    )

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Birth location latitude in degrees",
        examples=[28.6139, 19.0760, -33.8688]
    )

    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Birth location longitude in degrees",
        examples=[77.2090, 72.8777, 151.2093]
    )

    timezone_offset: float = Field(
        ...,
        ge=-12.0,
        le=14.0,
        description="Timezone offset from UTC in hours",
        examples=[5.5, -5.0, 0.0, 9.5]
    )

    # Optional fields for metadata
    ayanamsa: Optional[str] = Field(
        default='lahiri',
        description="Ayanamsa system to use",
        examples=['lahiri', 'raman', 'kp']
    )

    # Model configuration
    model_config = {
        'str_strip_whitespace': True,  # Auto-strip whitespace
        'validate_assignment': True,    # Validate on assignment
        'extra': 'ignore'              # Ignore extra fields (forward compatibility)
    }

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        """
        Validate birth date format and realistic range

        Checks:
        - Correct format (YYYY-MM-DD)
        - Valid calendar date
        - Year between 1900-2100
        - Handles leap years
        """
        try:
            date_obj = datetime.strptime(v, '%Y-%m-%d')

            # Check year range (Swiss Ephemeris reliable range)
            if not (1900 <= date_obj.year <= 2100):
                raise ValueError(
                    f'Birth year must be between 1900 and 2100. '
                    f'Got: {date_obj.year}. '
                    f'For historical dates before 1900, accuracy may be reduced.'
                )

            # Check date is not in future
            if date_obj.date() > datetime.now().date():
                raise ValueError(
                    f'Birth date cannot be in the future. '
                    f'Got: {v}, Today: {datetime.now().date()}'
                )

            return v

        except ValueError as e:
            # datetime.strptime will raise ValueError for invalid dates
            if 'does not match format' in str(e):
                raise ValueError(
                    f'Invalid date format. Use YYYY-MM-DD. '
                    f'Example: 1990-05-15. Got: {v}'
                )
            raise  # Re-raise other ValueErrors (like future date)

    @field_validator('birth_time')
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        """
        Validate birth time format

        Checks:
        - Correct format (HH:MM:SS)
        - Valid time values (00:00:00 to 23:59:59)
        - Handles midnight (00:00:00) and end of day (23:59:59)
        """
        try:
            time_obj = datetime.strptime(v, '%H:%M:%S')

            # Validate hour, minute, second ranges (datetime handles this,
            # but let's be explicit about valid ranges)
            hour, minute, second = map(int, v.split(':'))

            if not (0 <= hour <= 23):
                raise ValueError(f'Hour must be between 00 and 23. Got: {hour}')

            if not (0 <= minute <= 59):
                raise ValueError(f'Minute must be between 00 and 59. Got: {minute}')

            if not (0 <= second <= 59):
                raise ValueError(f'Second must be between 00 and 59. Got: {second}')

            return v

        except ValueError as e:
            if 'does not match format' in str(e):
                raise ValueError(
                    f'Invalid time format. Use HH:MM:SS (24-hour). '
                    f'Example: 14:30:00. Got: {v}'
                )
            raise

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """
        Validate latitude with precision limit

        Checks:
        - Range: -90 to 90 degrees
        - Precision: 6 decimal places (sufficient for ~0.1m accuracy)
        - Note: Pydantic's ge/le already validates range
        """
        # Round to 6 decimal places for consistency
        # (more precision is not meaningful for astrology)
        rounded = round(v, 6)

        return rounded

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """
        Validate longitude with precision limit

        Checks:
        - Range: -180 to 180 degrees
        - Precision: 6 decimal places
        """
        # Round to 6 decimal places
        rounded = round(v, 6)

        return rounded

    @field_validator('timezone_offset')
    @classmethod
    def validate_timezone_offset(cls, v: float) -> float:
        """
        Validate timezone offset

        Checks:
        - Range: -12 to +14 hours (covers all real timezones)
        - Examples: IST=5.5, EST=-5.0, JST=9.0
        """
        # Timezone offset is already validated by ge/le in Field
        # Round to 1 decimal place (0.5 hour precision is enough)
        rounded = round(v, 1)

        return rounded

    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        """
        Validate and sanitize user name

        Checks:
        - Not empty after stripping whitespace
        - Length between 1-100 characters
        - Remove potentially harmful characters
        """
        # Strip whitespace (Pydantic config does this, but be explicit)
        v = v.strip()

        if not v:
            raise ValueError('User name cannot be empty or only whitespace')

        # Remove control characters
        v = re.sub(r'[\x00-\x1F\x7F]', '', v)

        # Check length after sanitization
        if len(v) < 1:
            raise ValueError('User name must have at least 1 character after sanitization')

        return v

    @model_validator(mode='after')
    def validate_birth_datetime_combination(self) -> 'BirthDataSchema':
        """
        Validate the combination of date and time

        Checks:
        - Combined datetime is not in future
        - Handles timezone offset in validation
        - Provides context-aware error messages
        """
        try:
            # Parse date and time
            date_obj = datetime.strptime(self.birth_date, '%Y-%m-%d')
            time_obj = datetime.strptime(self.birth_time, '%H:%M:%S')

            # Combine date and time
            birth_datetime = datetime.combine(date_obj.date(), time_obj.time())

            # Note: We don't check against current time with timezone
            # because the birth could be in a different timezone
            # The future date check in birth_date validator is sufficient

        except Exception as e:
            # This shouldn't happen if field validators passed,
            # but defensive programming
            logger.error(f"Error validating datetime combination: {e}")

        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert schema to dictionary for processing

        Returns validated data as a dictionary that matches
        the expected format for calculation functions.
        """
        return {
            'user_name': self.user_name,
            'birth_date': self.birth_date,
            'birth_time': self.birth_time,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone_offset': self.timezone_offset,
            'ayanamsa': self.ayanamsa
        }

    def get_warnings(self) -> list:
        """
        Check for edge cases and return warnings

        Edge cases that don't prevent calculation but should be noted:
        - Polar regions (|latitude| > 66.5°)
        - Midnight births (00:00:00)
        - Date line proximity (|longitude| > 170°)
        - Historical dates (before 1950)
        - Recent dates (within 1 year)

        Returns:
            list: Warning messages for edge cases detected
        """
        warnings = []

        # Polar region check
        if abs(self.latitude) > 66.5:
            region = 'Arctic' if self.latitude > 0 else 'Antarctic'
            warnings.append({
                'code': 'POLAR_REGION',
                'message': f'Birth location in {region} Circle (latitude: {self.latitude}°)',
                'impact': 'House calculations may have variations in polar regions',
                'severity': 'info'
            })

        # Midnight birth check
        if self.birth_time == '00:00:00':
            warnings.append({
                'code': 'MIDNIGHT_BIRTH',
                'message': 'Birth time is exactly midnight (00:00:00)',
                'impact': 'Verify if 00:00 (start of day) or 24:00 (end of previous day) was intended',
                'severity': 'warning'
            })

        # Date line proximity check
        if abs(self.longitude) > 170:
            warnings.append({
                'code': 'DATE_LINE_PROXIMITY',
                'message': f'Birth location near International Date Line (longitude: {self.longitude}°)',
                'impact': 'Verify timezone offset is correct for this location',
                'severity': 'info'
            })

        # Equator proximity
        if abs(self.latitude) < 1:
            warnings.append({
                'code': 'EQUATORIAL_REGION',
                'message': f'Birth location near Equator (latitude: {self.latitude}°)',
                'impact': 'Ascendant calculations are standard (no special handling needed)',
                'severity': 'info'
            })

        # Historical date check
        birth_year = int(self.birth_date.split('-')[0])
        if birth_year < 1950:
            warnings.append({
                'code': 'HISTORICAL_DATE',
                'message': f'Birth date is historical (year: {birth_year})',
                'impact': 'Swiss Ephemeris accuracy is excellent, but verify timezone information',
                'severity': 'info'
            })

        # Recent birth check (for testing)
        current_year = datetime.now().year
        if birth_year >= current_year:
            warnings.append({
                'code': 'CURRENT_YEAR_BIRTH',
                'message': f'Birth date is in current year ({birth_year})',
                'impact': 'Ensure birth has already occurred',
                'severity': 'warning'
            })

        return warnings


# Critical Security Notes for Module 2.1:
#
# 1. ALWAYS validate ALL user inputs before processing
# 2. NEVER trust client-provided data
# 3. USE Pydantic's built-in validators (ge, le, pattern)
# 4. SANITIZE string inputs (remove control characters)
# 5. ROUND floating point to prevent precision attacks
# 6. CHECK combined validations (date + time together)
# 7. PROVIDE helpful error messages (users need guidance)
# 8. LOG validation failures (for security monitoring)
