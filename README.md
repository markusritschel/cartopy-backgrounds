# Cartopy Backgrounds

A modern CLI tool to download NASA satellite imagery backgrounds for use with [Cartopy](https://scitools.org.uk/cartopy/).

## Features

- 🌍 **Multiple NASA Datasets**: BlueMarble, BlueMarble + Topography/Bathymetry
- 🚀 **Fast Async Downloads**: Concurrent downloads with retry logic
- 🎨 **Beautiful CLI**: Rich progress bars and colored output
- 📦 **Flexible Resolution Selection**: Choose low, mid, high resolutions
- ⚙️ **Profile Presets**: Quick workflows for development and production
- 🔧 **Extensible Architecture**: Easy to add new datasets
- 📊 **Automatic JSON Generation**: Creates Cartopy-compatible configuration
- ✅ **Comprehensive Tests**: 28+ unit tests covering core functionality

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cartopy-backgrounds.git
cd cartopy-backgrounds

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Basic Usage

```bash
# Download BlueMarble with development profile (low + mid resolution)
uv run cartopy-bg download --profile dev --generate-json

# Download multiple datasets
uv run cartopy-bg download -d bluemarble -d bluemarble-tb --profile prod

# Download specific months only
uv run cartopy-bg download -m Jan -m Jul --profile minimal

# List available datasets
uv run cartopy-bg list-datasets
```

## CLI Commands

### Download Images

```bash
cartopy-bg download [OPTIONS]
```

**Options:**
- `--dataset, -d`: Dataset(s) to download (bluemarble, bluemarble-tb, or `all`)
- `--resolution, -r`: Specific resolutions (low, mid, high)
- `--month, -m`: Specific months (Jan, Feb, etc. or 1-12)
- `--profile`: Preset profile (minimal, dev, prod)
- `--output-dir, -o`: Base output directory (default: `./data`)
- `--force, -f`: Overwrite existing files
- `--generate-json`: Auto-generate images.json after download
- `--max-retries`: Maximum retry attempts (default: 3)
- `--timeout`: Download timeout in seconds (default: 30)

**Profiles:**
- `minimal`: Low resolution only (720x360) - ~5 MB/month
- `dev`: Low + mid resolution (up to 1440x720) - ~15 MB/month
- `prod`: Low + mid + high (up to 3600x1800) - ~50 MB/month

**Examples:**

```bash
# Development workflow - download low/mid resolutions only
cartopy-bg download --profile dev --generate-json

# Production - download all standard resolutions
cartopy-bg download --profile prod

# Custom - specific months and resolutions
cartopy-bg download -r low -r high -m Jan -m Feb -m Mar

# Download multiple datasets
cartopy-bg download -d bluemarble -d bluemarble-tb --profile dev
```

### List Available Datasets

```bash
cartopy-bg list-datasets
```

Shows all registered datasets with their descriptions and supported resolutions.

### Generate images.json

```bash
cartopy-bg generate [OPTIONS]
```

Creates a Cartopy-compatible JSON configuration from downloaded images.

**Options:**
- `--dataset, -d`: Dataset(s) to include (default: all found)
- `--data-dir`: Directory containing images (default: `./data`)
- `--output, -o`: Output file path (default: `./images.json`)
- `--pretty`: Pretty-print JSON (default: true)

## Usage with Cartopy

After downloading images and generating `images.json`:

```python
import cartopy.crs as ccrs
import cartopy.mpl.geoaxes as geoaxes
import matplotlib.pyplot as plt

# Load custom backgrounds
geoaxes.read_user_background_images('images.json')

# Create a map with Blue Marble background
fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Use the downloaded background
ax.background_img(name='Blue Marble January', resolution='mid')
ax.coastlines()

plt.show()
```

## Architecture

The project follows an **MVC architecture** with **Strategy Pattern** for extensibility:

```
├── View Layer (cli.py)
│   └── Typer CLI interface

├── Controller Layer (controller.py)
│   └── Download workflow orchestration

├── Model Layer
│   ├── models/     - Data structures (Month, Resolution enums)
│   └── datasets/   - Dataset implementations (Strategy Pattern)
│       ├── base.py          - Abstract Dataset interface
│       ├── registry.py      - Dataset registry
│       ├── bluemarble.py    - BlueMarble implementation
│       └── bluemarble_tb.py - BlueMarble+TB implementation

└── Services
    ├── downloader.py  - Async HTTP downloader
    ├── generator.py   - JSON configuration generator
    └── scraper.py     - NASA dataset ID scraper
```

### Adding New Datasets

To add a new dataset, create a class implementing the `Dataset` interface:

```python
from cartopy_backgrounds.datasets.base import Dataset
from cartopy_backgrounds.datasets.registry import DatasetRegistry

class MyDataset(Dataset):
    @property
    def name(self) -> str:
        return "my-dataset"

    # Implement other abstract methods...

# Register the dataset
DatasetRegistry.register(MyDataset)
```

## Available Datasets

### Blue Marble (bluemarble)
NASA Blue Marble Next Generation - True color Earth satellite imagery from 2004.

**Source**: https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG
**Resolutions**: low (720x360), mid (1440x720), high (3600x1800)

### Blue Marble + Topography/Bathymetry (bluemarble-tb)
Blue Marble with added topographic and bathymetric shading.

**Source**: https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG-TB
**Resolutions**: low, mid, high

## About NASA's Blue Marble

> Next Generation images show Earth in true color. The images show how the surface would look to a human in space if our world had no clouds and no atmosphere. NASA's Terra satellite collected these images. There is one Blue Marble image for each month of the year 2004. These images allow us to explore changes on Earth's lands over time. Notice how the patterns of green (trees and plants), brown (exposed land surface), and white (snow) change from winter through spring, summer, and fall.
>
> – [NASA Earth Observatory](https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG)

## Development

### Project Structure

```
cartopy-backgrounds/
├── src/cartopy_backgrounds/    # Source code
│   ├── cli.py                  # CLI interface
│   ├── controller.py           # Download orchestration
│   ├── downloader.py           # HTTP download service
│   ├── generator.py            # JSON generator
│   ├── scraper.py              # Dataset ID scraper
│   ├── models/                 # Data models
│   ├── datasets/               # Dataset implementations
│   └── utils/                  # Utilities and helpers
├── tests/                      # Test suite (28+ tests)
├── scripts/                    # Utility scripts
├── data/                       # Downloaded images (git-ignored)
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

### Running Tests

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=cartopy_backgrounds

# Run with verbose output
uv run pytest -v
```

All 28+ tests should pass:
```
============================== 28 passed in 0.17s ===============================
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check with mypy
uv run mypy src/
```

### Verifying Dataset IDs

To verify that dataset IDs are correct:

```bash
uv run python scripts/verify_dataset_ids.py
```

This scrapes the current IDs from NASA's website and compares them with hardcoded values.

## Technical Details

### NASA API

Images are downloaded from NASA's RenderData servlet:

```
https://neo.gsfc.nasa.gov/servlet/RenderData
  ?si={DATASET_ID}&cs=rgb&format=PNG
  &width={WIDTH}&height={HEIGHT}
```

### Supported Resolutions

- **Low**: 720×360 pixels (~250 KB/image)
- **Mid**: 1440×720 pixels (~1 MB/image)
- **High**: 3600×1800 pixels (~5 MB/image)

### File Naming Convention

```
{Dataset}_{Month}_{Width}x{Height}.png

Examples:
- BlueMarble_January_720x360.png
- BlueMarbleTB_July_1440x720.png
```

### Download Features

- **Async I/O**: Concurrent downloads using httpx
- **Retry Logic**: Exponential backoff (2s, 4s, 8s delays)
- **Progress Tracking**: Rich progress bars with speed/ETA
- **Skip Existing**: Avoid re-downloading (unless `--force`)
- **Streaming**: Memory-efficient chunk-based downloads

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes with atomic commits
4. Run tests and linting: `uv run pytest && uv run ruff check src/`
5. Push and create a pull request
6. Use rebase for clean history

### Commit Message Convention

Follow conventional commits style:
- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Adding tests
- `docs:` - Documentation updates
- `refactor:` - Code refactoring

## License

This project is open source. NASA imagery is in the public domain.

## Resources

- [Cartopy Documentation](https://scitools.org.uk/cartopy/)
- [NASA Earth Observatory](https://neo.gsfc.nasa.gov)
- [NASA Visible Earth](https://visibleearth.nasa.gov)
- [Blue Marble Collection](https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG)
- [NASA NEO Topography/Bathymetry](https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG-TB)
