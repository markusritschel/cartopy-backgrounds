"""Parsing utilities for CLI arguments."""

import re
from typing import List, TypeVar

from ..models.common import Month, Resolution

T = TypeVar('T')


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


def parse_comma_separated(spec: str) -> List[str]:
    """Parse comma-separated values.

    Args:
        spec: Comma-separated specification string

    Returns:
        List of individual values (stripped)

    Examples:
        >>> parse_comma_separated("low,mid,high")
        ["low", "mid", "high"]
        >>> parse_comma_separated("a, b , c")
        ["a", "b", "c"]
    """
    return [item.strip() for item in spec.split(",") if item.strip()]


def parse_resolution_spec(spec: str) -> List[Resolution]:
    """Parse resolution specification supporting comma-separated values.

    Supports:
    - Single values: "low", "mid", "high"
    - Comma-separated: "low,mid", "low,mid,high"

    Args:
        spec: Resolution specification string

    Returns:
        List of Resolution enums

    Raises:
        ValueError: If specification is invalid

    Examples:
        >>> parse_resolution_spec("low,mid")
        [Resolution.LOW, Resolution.MID]
        >>> parse_resolution_spec("low,mid,high")
        [Resolution.LOW, Resolution.MID, Resolution.HIGH]
    """
    resolutions = []
    parts = parse_comma_separated(spec)

    for part in parts:
        try:
            resolutions.append(Resolution[part.upper()])
        except KeyError:
            available = ", ".join([r.name.lower() for r in Resolution])
            raise ValueError(
                f"Unknown resolution '{part}'. Available: {available}"
            )

    # Remove duplicates while preserving order
    seen = set()
    unique_resolutions = []
    for res in resolutions:
        if res not in seen:
            seen.add(res)
            unique_resolutions.append(res)

    return unique_resolutions


def parse_resolution_specs(specs: List[str]) -> List[Resolution]:
    """Parse multiple resolution specifications.

    Args:
        specs: List of resolution specification strings

    Returns:
        List of Resolution enums (deduplicated)

    Examples:
        >>> parse_resolution_specs(["low", "mid,high"])
        [Resolution.LOW, Resolution.MID, Resolution.HIGH]
    """
    all_resolutions = []
    for spec in specs:
        all_resolutions.extend(parse_resolution_spec(spec))

    # Remove duplicates while preserving order
    seen = set()
    unique_resolutions = []
    for res in all_resolutions:
        if res not in seen:
            seen.add(res)
            unique_resolutions.append(res)

    return unique_resolutions


def parse_dataset_specs(specs: List[str]) -> List[str]:
    """Parse dataset specifications supporting comma-separated values.

    Supports:
    - Single values: "bluemarble"
    - Comma-separated: "bluemarble,bluemarble-tb"

    Args:
        specs: List of dataset specification strings

    Returns:
        List of dataset names (deduplicated)

    Examples:
        >>> parse_dataset_specs(["bluemarble,bluemarble-tb"])
        ["bluemarble", "bluemarble-tb"]
    """
    all_datasets = []
    for spec in specs:
        all_datasets.extend(parse_comma_separated(spec))

    # Remove duplicates while preserving order
    seen = set()
    unique_datasets = []
    for dataset in all_datasets:
        if dataset not in seen:
            seen.add(dataset)
            unique_datasets.append(dataset)

    return unique_datasets
