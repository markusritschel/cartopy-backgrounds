"""Tests for CLI argument parsing utilities."""

import pytest

from cartopy_backgrounds.models.common import Month
from cartopy_backgrounds.utils.parser import parse_month_spec, parse_month_specs


class TestParseMonthSpec:
    """Tests for parse_month_spec function."""

    def test_single_number(self):
        """Test parsing single month number."""
        result = parse_month_spec("1")
        assert result == [Month.JANUARY]

        result = parse_month_spec("12")
        assert result == [Month.DECEMBER]

    def test_single_abbr(self):
        """Test parsing single month abbreviation."""
        result = parse_month_spec("Jan")
        assert result == [Month.JANUARY]

        result = parse_month_spec("Dec")
        assert result == [Month.DECEMBER]

    def test_numeric_range(self):
        """Test parsing numeric month range."""
        result = parse_month_spec("1-3")
        assert result == [Month.JANUARY, Month.FEBRUARY, Month.MARCH]

        result = parse_month_spec("10-12")
        assert result == [Month.OCTOBER, Month.NOVEMBER, Month.DECEMBER]

    def test_abbr_range(self):
        """Test parsing abbreviation month range."""
        result = parse_month_spec("Jan-Mar")
        assert result == [Month.JANUARY, Month.FEBRUARY, Month.MARCH]

        result = parse_month_spec("Oct-Dec")
        assert result == [Month.OCTOBER, Month.NOVEMBER, Month.DECEMBER]

    def test_comma_separated(self):
        """Test parsing comma-separated months."""
        result = parse_month_spec("1,5,8")
        assert result == [Month.JANUARY, Month.MAY, Month.AUGUST]

        result = parse_month_spec("Jan,May,Aug")
        assert result == [Month.JANUARY, Month.MAY, Month.AUGUST]

    def test_mixed_format(self):
        """Test parsing mixed formats (ranges and singles)."""
        result = parse_month_spec("1-3,5,7-9")
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH,
            Month.MAY,
            Month.JULY, Month.AUGUST, Month.SEPTEMBER
        ]

        result = parse_month_spec("Jan-Mar,May,Jul-Sep")
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH,
            Month.MAY,
            Month.JULY, Month.AUGUST, Month.SEPTEMBER
        ]

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        result = parse_month_spec(" 1 - 3 , 5 , 7 - 9 ")
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH,
            Month.MAY,
            Month.JULY, Month.AUGUST, Month.SEPTEMBER
        ]

    def test_deduplication(self):
        """Test that duplicate months are removed."""
        result = parse_month_spec("1,2,1,3,2")
        assert result == [Month.JANUARY, Month.FEBRUARY, Month.MARCH]

    def test_invalid_range(self):
        """Test that invalid ranges raise ValueError."""
        with pytest.raises(ValueError, match="Invalid range"):
            parse_month_spec("5-3")  # start > end

        with pytest.raises(ValueError, match="Invalid range"):
            parse_month_spec("Dec-Jan")  # December comes after January

    def test_invalid_month_number(self):
        """Test that invalid month numbers raise ValueError."""
        with pytest.raises(ValueError, match="Month number must be between 1 and 12"):
            parse_month_spec("0")

        with pytest.raises(ValueError, match="Month number must be between 1 and 12"):
            parse_month_spec("13")

        with pytest.raises(ValueError, match="Month numbers must be between 1 and 12"):
            parse_month_spec("1-13")

    def test_invalid_month_abbr(self):
        """Test that invalid abbreviations raise ValueError."""
        with pytest.raises(ValueError, match="Invalid month abbreviation"):
            parse_month_spec("Foo")


class TestParseMonthSpecs:
    """Tests for parse_month_specs function."""

    def test_multiple_specs(self):
        """Test parsing multiple month specifications."""
        result = parse_month_specs(["1-3", "5", "7-9"])
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH,
            Month.MAY,
            Month.JULY, Month.AUGUST, Month.SEPTEMBER
        ]

    def test_overlapping_specs(self):
        """Test that overlapping specs are deduplicated."""
        result = parse_month_specs(["1-3", "2-4"])
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH, Month.APRIL
        ]

    def test_single_spec(self):
        """Test parsing single specification."""
        result = parse_month_specs(["1-12"])
        assert len(result) == 12
        assert result == list(Month)

    def test_empty_specs(self):
        """Test parsing empty list."""
        result = parse_month_specs([])
        assert result == []

    def test_mixed_formats_multiple_specs(self):
        """Test multiple specs with different formats."""
        result = parse_month_specs(["Jan", "1-3", "5,7"])
        # Jan appears in both first and second spec
        assert result == [
            Month.JANUARY, Month.FEBRUARY, Month.MARCH,
            Month.MAY, Month.JULY
        ]
