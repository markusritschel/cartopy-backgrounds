"""Common data models and enums used across the package."""

from enum import Enum


class Month(str, Enum):
    """Enum representing months of the year."""

    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"

    @classmethod
    def from_number(cls, num: int) -> "Month":
        """Convert month number (1-12) to Month enum."""
        if not 1 <= num <= 12:
            raise ValueError(f"Month number must be between 1 and 12, got {num}")
        return list(cls)[num - 1]

    @classmethod
    def from_abbr(cls, abbr: str) -> "Month":
        """Convert month abbreviation (Jan, Feb, etc.) to Month enum."""
        abbr_map = {
            "Jan": cls.JANUARY,
            "Feb": cls.FEBRUARY,
            "Mar": cls.MARCH,
            "Apr": cls.APRIL,
            "May": cls.MAY,
            "Jun": cls.JUNE,
            "Jul": cls.JULY,
            "Aug": cls.AUGUST,
            "Sep": cls.SEPTEMBER,
            "Oct": cls.OCTOBER,
            "Nov": cls.NOVEMBER,
            "Dec": cls.DECEMBER,
        }
        if abbr not in abbr_map:
            raise ValueError(f"Invalid month abbreviation: {abbr}")
        return abbr_map[abbr]


class Resolution(str, Enum):
    """Enum representing image resolutions."""

    LOW = "720x360"
    MID = "1440x720"
    HIGH = "3600x1800"
    ULTRAHIGH = "21600x10800"

    @property
    def width(self) -> int:
        """Get image width in pixels."""
        return int(self.value.split("x")[0])

    @property
    def height(self) -> int:
        """Get image height in pixels."""
        return int(self.value.split("x")[1])

    @property
    def json_key(self) -> str:
        """Get the key used in images.json for this resolution."""
        mapping = {
            Resolution.LOW: "low",
            Resolution.MID: "mid",
            Resolution.HIGH: "high",
            Resolution.ULTRAHIGH: "ultrahigh",
        }
        return mapping[self]
