#!/usr/bin/env python3
"""Script to verify and display dataset IDs from NASA NEO website."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cartopy_backgrounds.datasets.bluemarble import BlueMarbleDataset
from cartopy_backgrounds.datasets.bluemarble_tb import BlueMarbleTBDataset
from cartopy_backgrounds.scraper import scrape_dataset_ids, verify_dataset_ids
from rich.console import Console
from rich.table import Table

console = Console()


async def main() -> None:
    """Verify dataset IDs by scraping NASA website."""
    console.print("\n[bold]Verifying BlueMarble Dataset IDs[/bold]\n")

    # Scrape BlueMarble IDs
    console.print("Scraping BlueMarble dataset...")
    bluemarble_scraped = await scrape_dataset_ids("BlueMarbleNG")

    # Compare with hardcoded
    bluemarble = BlueMarbleDataset()
    bluemarble_hardcoded = bluemarble.get_dataset_ids()

    table = Table(title="BlueMarble Dataset IDs", show_header=True)
    table.add_column("Month")
    table.add_column("Hardcoded ID")
    table.add_column("Scraped ID")
    table.add_column("Status")

    for month in bluemarble_hardcoded:
        hardcoded = bluemarble_hardcoded[month]
        scraped = bluemarble_scraped.get(month, "N/A")
        match = "✓" if hardcoded == scraped else "✗"
        style = "green" if hardcoded == scraped else "red"
        table.add_row(
            month.value,
            hardcoded,
            scraped,
            f"[{style}]{match}[/{style}]",
        )

    console.print(table)

    # Verify BlueMarble-TB
    console.print("\n[bold]Verifying BlueMarble-TB Dataset IDs[/bold]\n")
    console.print("Scraping BlueMarble-TB dataset...")
    bluemarble_tb_scraped = await scrape_dataset_ids("BlueMarbleNG-TB")

    bluemarble_tb = BlueMarbleTBDataset()
    bluemarble_tb_hardcoded = bluemarble_tb.get_dataset_ids()

    table2 = Table(title="BlueMarble-TB Dataset IDs", show_header=True)
    table2.add_column("Month")
    table2.add_column("Hardcoded ID")
    table2.add_column("Scraped ID")
    table2.add_column("Status")

    for month in bluemarble_tb_hardcoded:
        hardcoded = bluemarble_tb_hardcoded[month]
        scraped = bluemarble_tb_scraped.get(month, "N/A")
        match = "✓" if hardcoded == scraped else "✗"
        style = "green" if hardcoded == scraped else "red"
        table2.add_row(
            month.value,
            hardcoded,
            scraped,
            f"[{style}]{match}[/{style}]",
        )

    console.print(table2)


if __name__ == "__main__":
    asyncio.run(main())
