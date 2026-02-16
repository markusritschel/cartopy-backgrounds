"""Command-line interface for cartopy-backgrounds (MVC View layer)."""

import asyncio
import sys
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
from .utils.parser import parse_dataset_specs, parse_month_specs, parse_resolution_specs
from .validator import ImageValidator

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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
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
    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)


@app.command()
def download(
    datasets: List[str] = typer.Option(
        ["bluemarble"],
        "--dataset",
        "-d",
        help="Dataset(s): single (bluemarble), comma-separated (bluemarble,bluemarble-tb), or 'all'.",
    ),
    resolutions: Optional[List[str]] = typer.Option(
        None,
        "--resolution",
        "-r",
        help="Resolution(s): single (low), comma-separated (low,mid,high).",
    ),
    months: Optional[List[str]] = typer.Option(
        None,
        "--month",
        "-m",
        help="Months: singles (1, Jan), ranges (1-3, Jan-Mar), comma-separated (1,5,8), mixed (1-3,5,7-9). Default: all",
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

      # Download specific months (various formats)
      cartopy-bg download -m 1-3                  # Range: January through March
      cartopy-bg download -m 1,5,8                # Comma-separated: Jan, May, Aug
      cartopy-bg download -m 1-3,5,7-9            # Mixed: Jan-Mar, May, Jul-Sep

      # Comma-separated datasets and resolutions
      cartopy-bg download -d bluemarble,bluemarble-tb -r low,mid
      cartopy-bg download -d all -r low,mid,high
    """
    # Resolve datasets (support comma-separated)
    dataset_names = parse_dataset_specs(datasets)
    if "all" in dataset_names:
        dataset_names = DatasetRegistry.get_names()

    # Resolve resolutions (support comma-separated)
    if profile:
        if profile not in PROFILES:
            console.print(f"[red]Error:[/red] Unknown profile '{profile}'")
            console.print(f"Available profiles: {', '.join(PROFILES.keys())}")
            raise typer.Exit(1)
        resolution_objs = PROFILES[profile]
    elif resolutions:
        try:
            resolution_objs = parse_resolution_specs(resolutions)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
    else:
        # Default to dev profile
        resolution_objs = PROFILES["dev"]

    # Resolve months
    if months:
        try:
            month_objs = parse_month_specs(months)
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

    Checks that downloaded images exist and are valid PNG files.

    Examples:

      # Verify all downloaded datasets
      cartopy-bg verify

      # Verify specific datasets
      cartopy-bg verify -d bluemarble -d bluemarble-tb
    """
    # Parse dataset specifications
    if datasets:
        dataset_names = parse_dataset_specs(datasets)
    else:
        # Default to all registered datasets
        dataset_names = DatasetRegistry.get_names()

    # Check if data directory exists
    if not data_dir.exists():
        console.print(f"[red]Error:[/red] Data directory does not exist: {data_dir}")
        console.print("Run 'cartopy-bg download' first to download images.")
        raise typer.Exit(1)

    console.print(f"\n[bold]Verifying downloaded images...[/bold]")
    console.print(f"Data directory: {data_dir}\n")

    # Initialize validator
    validator = ImageValidator(data_dir)

    # Validate datasets
    all_results = validator.validate_datasets(dataset_names)

    if not all_results:
        console.print("[yellow]No datasets found to verify[/yellow]")
        raise typer.Exit(0)

    # Display results for each dataset
    total_checked = 0
    total_valid = 0
    total_invalid = 0
    total_missing = 0

    for dataset_name, results in all_results.items():
        if not results:
            continue

        console.print(f"[bold cyan]{dataset_name}:[/bold cyan]")

        # Create results table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Month", style="cyan")
        table.add_column("Resolution", style="yellow")
        table.add_column("Status", style="white")
        table.add_column("Size", justify="right", style="dim")
        table.add_column("Error", style="red")

        for result in results:
            total_checked += 1

            if result.is_ok:
                status = "[green]✓ Valid[/green]"
                size = f"{result.file_size // 1024} KB" if result.file_size else ""
                error = ""
                total_valid += 1
            elif result.exists:
                status = "[red]✗ Invalid[/red]"
                size = f"{result.file_size // 1024} KB" if result.file_size else ""
                error = result.error or "Unknown error"
                total_invalid += 1
            else:
                status = "[yellow]⚠ Missing[/yellow]"
                size = ""
                error = "File not found"
                total_missing += 1

            table.add_row(
                result.month.value,
                result.resolution.value,
                status,
                size,
                error,
            )

        console.print(table)
        console.print()

    # Summary
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Total checked: {total_checked}")
    console.print(f"  [green]Valid: {total_valid}[/green]")
    if total_missing > 0:
        console.print(f"  [yellow]Missing: {total_missing}[/yellow]")
    if total_invalid > 0:
        console.print(f"  [red]Invalid: {total_invalid}[/red]")

    # Exit with error code if any issues found
    if total_invalid > 0 or total_missing > 0:
        console.print("\n[yellow]⚠ Validation completed with issues[/yellow]")
        raise typer.Exit(1)
    else:
        console.print("\n[green bold]✓ All images verified successfully![/green bold]")
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
