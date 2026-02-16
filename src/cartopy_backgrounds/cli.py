"""Command-line interface for cartopy-backgrounds (MVC View layer)."""

import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .controller import DownloadController
from .datasets.registry import DatasetRegistry
from .generator import JSONGenerator
from .models.common import Month, Resolution

app = typer.Typer(
    name="cartopy-bg",
    help="Download NASA satellite imagery backgrounds for Cartopy",
    add_completion=False,
)
console = Console()

# Profile presets for common use cases
PROFILES = {
    "minimal": [Resolution.LOW],
    "dev": [Resolution.LOW, Resolution.MID],
    "prod": [Resolution.LOW, Resolution.MID, Resolution.HIGH],
}


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"cartopy-backgrounds version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Cartopy Backgrounds - Download NASA satellite imagery for Cartopy."""
    pass


@app.command()
def download(
    datasets: List[str] = typer.Option(
        ["bluemarble"],
        "--dataset",
        "-d",
        help="Dataset(s) to download. Use 'all' for all available datasets.",
    ),
    resolutions: Optional[List[str]] = typer.Option(
        None,
        "--resolution",
        "-r",
        help="Resolution(s) to download (low, mid, high, ultrahigh)",
    ),
    months: Optional[List[str]] = typer.Option(
        None,
        "--month",
        "-m",
        help="Specific months to download (Jan, Feb, ..., or 1-12). Default: all",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        help=f"Preset profile (minimal, dev, prod). Overrides --resolution.",
    ),
    output_dir: Path = typer.Option(
        Path("data"),
        "--output-dir",
        "-o",
        help="Base output directory for downloaded images",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
    generate_json: bool = typer.Option(
        False,
        "--generate-json",
        help="Auto-generate images.json after download",
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        help="Maximum retry attempts for failed downloads",
    ),
    timeout: int = typer.Option(
        30,
        "--timeout",
        help="Download timeout in seconds",
    ),
) -> None:
    """Download NASA satellite imagery datasets.

    Examples:

      # Download BlueMarble with dev profile (low + mid resolution)
      cartopy-bg download --profile dev

      # Download multiple datasets
      cartopy-bg download -d bluemarble -d bluemarble-tb --profile prod

      # Download specific months and resolutions
      cartopy-bg download -r low -r high -m Jan -m Jul
    """
    # Resolve datasets
    if "all" in datasets:
        dataset_names = DatasetRegistry.get_names()
    else:
        dataset_names = datasets

    # Resolve resolutions
    if profile:
        if profile not in PROFILES:
            console.print(f"[red]Error:[/red] Unknown profile '{profile}'")
            console.print(f"Available profiles: {', '.join(PROFILES.keys())}")
            raise typer.Exit(1)
        resolution_objs = PROFILES[profile]
    elif resolutions:
        # Convert string resolutions to enum
        resolution_objs = []
        for res in resolutions:
            try:
                resolution_objs.append(Resolution[res.upper()])
            except KeyError:
                console.print(f"[red]Error:[/red] Unknown resolution '{res}'")
                console.print(
                    f"Available: {', '.join([r.name.lower() for r in Resolution])}"
                )
                raise typer.Exit(1)
    else:
        # Default to dev profile
        resolution_objs = PROFILES["dev"]

    # Resolve months
    if months:
        month_objs = []
        for m in months:
            try:
                # Try as number first (1-12)
                if m.isdigit():
                    month_objs.append(Month.from_number(int(m)))
                else:
                    # Try as abbreviation (Jan, Feb, etc.)
                    month_objs.append(Month.from_abbr(m))
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
    else:
        # Default to all months
        month_objs = list(Month)

    # Display download plan
    console.print("\n[bold]Download Plan:[/bold]")
    console.print(f"  Datasets: {', '.join(dataset_names)}")
    console.print(
        f"  Resolutions: {', '.join([r.value for r in resolution_objs])}"
    )
    console.print(f"  Months: {len(month_objs)} month(s)")
    console.print(f"  Output directory: {output_dir}")
    console.print()

    # Execute download
    controller = DownloadController(
        output_dir=output_dir,
        force=force,
        max_retries=max_retries,
        timeout=timeout,
    )

    try:
        results = asyncio.run(
            controller.download_datasets(dataset_names, month_objs, resolution_objs)
        )

        # Summary
        total_files = sum(len(files) for files in results.values())
        console.print(f"\n[green bold]✓ Download complete![/green bold]")
        console.print(f"Total files downloaded: {total_files}")

        # Generate JSON if requested
        if generate_json:
            console.print()
            generator = JSONGenerator(output_dir)
            generator.generate(dataset_names)

    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list-datasets")
def list_datasets() -> None:
    """List all available datasets."""
    datasets = DatasetRegistry.list_all()

    if not datasets:
        console.print("[yellow]No datasets registered[/yellow]")
        return

    table = Table(title="Available Datasets", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Description")
    table.add_column("Resolutions", style="yellow")

    for dataset in datasets:
        resolutions = ", ".join([r.name.lower() for r in dataset.get_available_resolutions()])
        table.add_row(
            dataset.name,
            dataset.display_name,
            dataset.description,
            resolutions,
        )

    console.print(table)


@app.command()
def generate(
    datasets: Optional[List[str]] = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Dataset(s) to include (default: all found)",
    ),
    data_dir: Path = typer.Option(
        Path("data"),
        "--data-dir",
        help="Directory containing downloaded images",
    ),
    output: Path = typer.Option(
        Path("images.json"),
        "--output",
        "-o",
        help="Output JSON file path",
    ),
    pretty: bool = typer.Option(
        True,
        "--pretty/--compact",
        help="Pretty-print JSON",
    ),
) -> None:
    """Generate images.json from downloaded images.

    Examples:

      # Generate from all downloaded datasets
      cartopy-bg generate

      # Generate only for specific datasets
      cartopy-bg generate -d bluemarble -d bluemarble-tb
    """
    generator = JSONGenerator(data_dir)

    try:
        generator.generate(
            dataset_names=datasets,
            output_file=output,
            pretty=pretty,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def verify(
    datasets: Optional[List[str]] = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Dataset(s) to verify (default: all)",
    ),
    data_dir: Path = typer.Option(
        Path("data"),
        "--data-dir",
        help="Directory containing downloaded images",
    ),
) -> None:
    """Verify downloaded images.

    Checks that downloaded images exist and are valid.
    """
    # TODO: Implement validation in Phase 9
    console.print("[yellow]Verification not yet implemented[/yellow]")
    console.print("This feature will be added in Phase 9")


if __name__ == "__main__":
    app()
