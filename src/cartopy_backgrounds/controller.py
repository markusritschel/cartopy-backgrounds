"""Download workflow controller (MVC Controller layer)."""

from pathlib import Path
from typing import Dict, List

from rich.console import Console

from .datasets.registry import DatasetRegistry
from .downloader import ImageDownloader
from .models.common import Month, Resolution
from .utils.errors import DatasetError

console = Console()


class DownloadController:
    """Orchestrates download workflows across multiple datasets.

    This is the Controller in the MVC architecture, coordinating between:
    - Dataset implementations (Model)
    - ImageDownloader service
    - CLI interface (View)
    - JSON generator

    The controller handles:
    - Resolving dataset names to implementations
    - Building download task lists
    - Coordinating concurrent downloads
    - Reporting progress and errors
    """

    def __init__(
        self,
        output_dir: Path,
        force: bool = False,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """Initialize the download controller.

        Args:
            output_dir: Base directory for downloaded images
            force: If True, overwrite existing files
            max_retries: Maximum retry attempts for failed downloads
            timeout: Download timeout in seconds
        """
        self.output_dir = Path(output_dir)
        self.force = force
        self.downloader = ImageDownloader(
            max_retries=max_retries,
            timeout=timeout,
            force=force,
        )

    async def download_datasets(
        self,
        dataset_names: List[str],
        months: List[Month],
        resolutions: List[Resolution],
    ) -> Dict[str, List[Path]]:
        """Download images for multiple datasets.

        Args:
            dataset_names: List of dataset identifiers to download
            months: Months to download
            resolutions: Target resolutions

        Returns:
            Dictionary mapping dataset name to list of downloaded file paths

        Raises:
            DatasetError: If a dataset name is not registered
        """
        results: Dict[str, List[Path]] = {}

        for dataset_name in dataset_names:
            console.print(f"\n[bold blue]📥 Downloading {dataset_name}...[/bold blue]")

            # Get dataset implementation from registry
            try:
                dataset = DatasetRegistry.get(dataset_name)
            except DatasetError as e:
                console.print(f"[red]Error:[/red] {e}")
                continue

            # Setup output directory for this dataset
            dataset_dir = self.output_dir / dataset.get_output_subdir()
            dataset_dir.mkdir(parents=True, exist_ok=True)

            # Build download task list
            downloads = []
            dataset_ids = dataset.get_dataset_ids()
            available_resolutions = dataset.get_available_resolutions()

            for month in months:
                if month not in dataset_ids:
                    console.print(
                        f"[yellow]⚠[/yellow] {month.value} not available for {dataset_name}"
                    )
                    continue

                dataset_id = dataset_ids[month]

                for resolution in resolutions:
                    # Skip if resolution not supported by this dataset
                    if resolution not in available_resolutions:
                        console.print(
                            f"[yellow]⚠[/yellow] {resolution.value} not available "
                            f"for {dataset_name}"
                        )
                        continue

                    # Build download URL and filepath
                    url = dataset.build_download_url(dataset_id, resolution)
                    filename = dataset.build_filename(month, resolution)
                    filepath = dataset_dir / filename

                    downloads.append((url, filepath))

            if not downloads:
                console.print(
                    f"[yellow]No downloads needed for {dataset_name}[/yellow]"
                )
                results[dataset_name] = []
                continue

            # Execute downloads
            console.print(f"Downloading {len(downloads)} files...")
            downloaded = await self.downloader.download_batch(downloads)
            results[dataset_name] = downloaded

            # Report results
            success_count = len(downloaded)
            total_count = len(downloads)
            if success_count == total_count:
                console.print(
                    f"[green]✓[/green] {dataset_name} complete "
                    f"({success_count}/{total_count} files)"
                )
            else:
                console.print(
                    f"[yellow]⚠[/yellow] {dataset_name} partial "
                    f"({success_count}/{total_count} files)"
                )

        return results
