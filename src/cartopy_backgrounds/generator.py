"""Cartopy images.json generator."""

import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from .datasets.base import Dataset
from .datasets.registry import DatasetRegistry
from .models.common import Month, Resolution

console = Console()


class JSONGenerator:
    """Generates Cartopy-compatible images.json configuration.

    The generated JSON file follows the format expected by
    cartopy.mpl.geoaxes.read_user_background_images(), mapping
    image names to file paths at different resolutions.
    """

    def __init__(self, data_dir: Path):
        """Initialize the JSON generator.

        Args:
            data_dir: Base directory containing downloaded images
        """
        self.data_dir = Path(data_dir)

    def _find_image(
        self, dataset: Dataset, month: Month, resolution: Resolution
    ) -> str | None:
        """Find image file for given dataset, month, and resolution.

        Args:
            dataset: Dataset implementation
            month: Month of the image
            resolution: Image resolution

        Returns:
            Relative path to image file, or None if not found
        """
        # Build expected filename
        filename = dataset.build_filename(month, resolution)
        dataset_dir = self.data_dir / dataset.get_output_subdir()
        filepath = dataset_dir / filename

        if filepath.exists():
            # Return relative path from data_dir
            return str(filepath.relative_to(self.data_dir.parent))
        return None

    def _generate_entry(
        self, dataset: Dataset, month: Month
    ) -> Dict[str, Any] | None:
        """Generate JSON entry for a single month of a dataset.

        Args:
            dataset: Dataset implementation
            month: Month of the images

        Returns:
            Dictionary with Cartopy format, or None if no images found
        """
        entry: Dict[str, Any] = {
            "__comment__": f"{dataset.display_name} {month.value}",
            "__source__": "NASA Visible Earth",
            "__projection__": "PlateCarree",
        }

        # Try to find images for all resolutions
        found_any = False
        for resolution in Resolution:
            image_path = self._find_image(dataset, month, resolution)
            if image_path:
                entry[resolution.json_key] = image_path
                found_any = True

        # Return None if no images found for this month
        return entry if found_any else None

    def generate(
        self,
        dataset_names: List[str] | None = None,
        output_file: Path | None = None,
        pretty: bool = True,
    ) -> Path:
        """Generate images.json file for downloaded datasets.

        Args:
            dataset_names: List of dataset names to include (None = all found)
            output_file: Output file path (default: data_dir.parent / 'images.json')
            pretty: If True, pretty-print the JSON

        Returns:
            Path to generated JSON file
        """
        # Default output file
        if output_file is None:
            output_file = self.data_dir.parent / "images.json"
        output_file = Path(output_file)

        # Determine which datasets to process
        if dataset_names is None:
            # Auto-discover from registered datasets
            datasets = DatasetRegistry.list_all()
        else:
            # Use specified datasets
            datasets = [DatasetRegistry.get(name) for name in dataset_names]

        # Build JSON configuration
        config: Dict[str, Any] = {
            "__comment__": (
                "JSON file specifying the images to use for a given type/name "
                "and resolution. Read in by cartopy.mpl.geoaxes.read_user_background_images."
            )
        }

        # Process each dataset
        entries_count = 0
        for dataset in datasets:
            # Check if dataset directory exists
            dataset_dir = self.data_dir / dataset.get_output_subdir()
            if not dataset_dir.exists():
                console.print(
                    f"[yellow]⚠[/yellow] Skipping {dataset.name}: "
                    f"directory not found at {dataset_dir}"
                )
                continue

            # Generate entries for all months
            dataset_entries = 0
            for month in Month:
                entry = self._generate_entry(dataset, month)
                if entry:
                    key = f"{dataset.display_name} {month.value}"
                    config[key] = entry
                    entries_count += 1
                    dataset_entries += 1

            if dataset_entries > 0:
                console.print(
                    f"[green]✓[/green] Added {dataset_entries} entries for {dataset.display_name}"
                )

        # Write JSON file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            if pretty:
                json.dump(config, f, indent=2)
            else:
                json.dump(config, f)

        if entries_count > 0:
            console.print(
                f"\n[green]✓ Generated {output_file}[/green] with {entries_count} entries"
            )
        else:
            console.print(
                "[yellow]⚠ No images found. JSON file created but empty.[/yellow]"
            )

        return output_file
