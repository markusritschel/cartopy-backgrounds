"""Tests for data models and enums."""

import pytest

from cartopy_backgrounds.models.common import Month, Resolution


class TestMonth:
    """Tests for Month enum."""

    def test_month_values(self):
        """Test that all months have correct string values."""
        assert Month.JANUARY.value == "January"
        assert Month.FEBRUARY.value == "February"
        assert Month.DECEMBER.value == "December"

    def test_from_number(self):
        """Test converting month numbers to Month enum."""
        assert Month.from_number(1) == Month.JANUARY
        assert Month.from_number(2) == Month.FEBRUARY
        assert Month.from_number(12) == Month.DECEMBER

    def test_from_number_invalid(self):
        """Test that invalid month numbers raise ValueError."""
        with pytest.raises(ValueError, match="Month number must be between 1 and 12"):
            Month.from_number(0)
        with pytest.raises(ValueError, match="Month number must be between 1 and 12"):
            Month.from_number(13)

    def test_from_abbr(self):
        """Test converting month abbreviations to Month enum."""
        assert Month.from_abbr("Jan") == Month.JANUARY
        assert Month.from_abbr("Feb") == Month.FEBRUARY
        assert Month.from_abbr("Dec") == Month.DECEMBER

    def test_from_abbr_invalid(self):
        """Test that invalid abbreviations raise ValueError."""
        with pytest.raises(ValueError, match="Invalid month abbreviation"):
            Month.from_abbr("Foo")
        with pytest.raises(ValueError, match="Invalid month abbreviation"):
            Month.from_abbr("January")

    def test_all_months_present(self):
        """Test that there are exactly 12 months."""
        months = list(Month)
        assert len(months) == 12


class TestResolution:
    """Tests for Resolution enum."""

    def test_resolution_values(self):
        """Test that resolutions have correct dimension values."""
        assert Resolution.LOW.value == "720x360"
        assert Resolution.MID.value == "1440x720"
        assert Resolution.HIGH.value == "3600x1800"
        assert Resolution.ULTRAHIGH.value == "21600x10800"

    def test_width_property(self):
        """Test that width property returns correct pixel width."""
        assert Resolution.LOW.width == 720
        assert Resolution.MID.width == 1440
        assert Resolution.HIGH.width == 3600
        assert Resolution.ULTRAHIGH.width == 21600

    def test_height_property(self):
        """Test that height property returns correct pixel height."""
        assert Resolution.LOW.height == 360
        assert Resolution.MID.height == 720
        assert Resolution.HIGH.height == 1800
        assert Resolution.ULTRAHIGH.height == 10800

    def test_json_key_property(self):
        """Test that json_key property returns correct Cartopy keys."""
        assert Resolution.LOW.json_key == "low"
        assert Resolution.MID.json_key == "mid"
        assert Resolution.HIGH.json_key == "high"
        assert Resolution.ULTRAHIGH.json_key == "ultrahigh"
