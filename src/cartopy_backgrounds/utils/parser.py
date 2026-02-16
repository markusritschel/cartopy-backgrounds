"""Parsing utilities for CLI arguments."""

import re
from typing import List

from ..models.common import Month


def parse_month_spec(spec: str) -> List[Month]:
    """Parse month specification supporting ranges and comma-separated values.

    Supports:
    - Single values: "1", "Jan", "January"
    - Ranges: "1-3", "Jan-Mar"
    - Comma-separated: "1,5,8", "Jan,Feb,Mar"
    - Mixed: "1-3,5,7-9"

    Args:
        spec: Month specification string

    Returns:
        List of Month enums

    Raises:
        ValueError: If specification is invalid

    Examples:
        >>> parse_month_spec("1-3")
        [Month.JANUARY, Month.FEBRUARY, Month.MARCH]
        >>> parse_month_spec("Jan,Jul,Dec")
        [Month.JANUARY, Month.JULY, Month.DECEMBER]
        >>> parse_month_spec("1-3,5,7-9")
        [Month.JANUARY, ..., Month.SEPTEMBER]
    """
    months = []

    # Split by comma first
    parts = [p.strip() for p in spec.split(",")]

    for part in parts:
        # Check if it's a range (e.g., "1-3" or "Jan-Mar")
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start_str = start_str.strip()
            end_str = end_str.strip()

            # Parse start and end
            if start_str.isdigit() and end_str.isdigit():
                # Numeric range (1-3)
                start = int(start_str)
                end = int(end_str)
                if not (1 <= start <= 12 and 1 <= end <= 12):
                    raise ValueError(f"Month numbers must be between 1 and 12 in '{part}'")
                if start > end:
                    raise ValueError(f"Invalid range '{part}': start > end")
                for num in range(start, end + 1):
                    months.append(Month.from_number(num))
            else:
                # Abbreviation range (Jan-Mar)
                start_month = Month.from_abbr(start_str)
                end_month = Month.from_abbr(end_str)

                # Get numeric values
                start_num = list(Month).index(start_month) + 1
                end_num = list(Month).index(end_month) + 1

                if start_num > end_num:
                    raise ValueError(
                        f"Invalid range '{part}': {start_str} comes after {end_str}"
                    )

                for num in range(start_num, end_num + 1):
                    months.append(Month.from_number(num))
        else:
            # Single value
            if part.isdigit():
                months.append(Month.from_number(int(part)))
            else:
                months.append(Month.from_abbr(part))

    # Remove duplicates while preserving order
    seen = set()
    unique_months = []
    for month in months:
        if month not in seen:
            seen.add(month)
            unique_months.append(month)

    return unique_months


def parse_month_specs(specs: List[str]) -> List[Month]:
    """Parse multiple month specifications.

    Args:
        specs: List of month specification strings

    Returns:
        List of Month enums (deduplicated)

    Examples:
        >>> parse_month_specs(["1-3", "5", "7-9"])
        [Month.JANUARY, ..., Month.SEPTEMBER]
    """
    all_months = []
    for spec in specs:
        all_months.extend(parse_month_spec(spec))

    # Remove duplicates while preserving order
    seen = set()
    unique_months = []
    for month in all_months:
        if month not in seen:
            seen.add(month)
            unique_months.append(month)

    return unique_months
