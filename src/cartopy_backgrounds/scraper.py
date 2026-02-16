"""Scraper for NASA NEO dataset IDs."""

import re
from typing import Dict

import httpx
from rich.console import Console

from .models.common import Month
from .utils.errors import DatasetError

console = Console()


async def scrape_dataset_ids(dataset_id_name: str) -> Dict[Month, str]:
    """Scrape dataset IDs from NASA NEO website.

    Args:
        dataset_id_name: Dataset identifier (e.g., "BlueMarbleNG" or "BlueMarbleNG-TB")

    Returns:
        Dictionary mapping Month to dataset ID strings

    Raises:
        DatasetError: If scraping fails or data cannot be parsed
    """
    url = f"https://neo.gsfc.nasa.gov/view.php?datasetId={dataset_id_name}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise DatasetError(f"Failed to fetch dataset page: {e}")

    html = response.text

    # Pattern: onclick="viewDataset('526308','2004-12-01');"
    # We need to extract dataset_id and date, then map date to month
    pattern = r"viewDataset\('(\d+)','(\d{4})-(\d{2})-\d{2}'\)"
    matches = re.findall(pattern, html)

    if not matches:
        raise DatasetError(
            f"Could not find dataset IDs in HTML. "
            f"The webpage structure may have changed."
        )

    # Build dataset ID mapping
    dataset_ids: Dict[Month, str] = {}
    for dataset_id, year, month_str in matches:
        # Only process 2004 data (the standard Blue Marble year)
        if year != "2004":
            continue

        try:
            month_num = int(month_str)
            month = Month.from_number(month_num)
            dataset_ids[month] = dataset_id
        except ValueError:
            console.print(f"[yellow]⚠ Skipping invalid month: {month_str}[/yellow]")
            continue

    if not dataset_ids:
        raise DatasetError("No valid dataset IDs found for 2004")

    console.print(f"[green]✓ Scraped {len(dataset_ids)} dataset IDs[/green]")
    return dataset_ids


async def verify_dataset_ids(
    expected_ids: Dict[Month, str], scraped_ids: Dict[Month, str]
) -> bool:
    """Compare hardcoded dataset IDs with scraped IDs.

    Args:
        expected_ids: Hardcoded dataset IDs
        scraped_ids: Scraped dataset IDs from website

    Returns:
        True if they match, False otherwise
    """
    all_match = True
    for month in Month:
        expected = expected_ids.get(month, "N/A")
        scraped = scraped_ids.get(month, "N/A")

        if expected != scraped:
            console.print(
                f"[yellow]⚠ {month.value:9s}: "
                f"Expected {expected}, Scraped {scraped}[/yellow]"
            )
            all_match = False

    return all_match
