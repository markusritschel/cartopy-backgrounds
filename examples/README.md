# Cartopy Usage Examples

This directory contains examples demonstrating how to use the downloaded NASA BlueMarble imagery with Cartopy.

## Quick Start

### Option 1: Jupyter Notebook (Recommended)

Interactive notebook with 5+ examples:

1. **Download BlueMarble images:**
   ```bash
   cartopy-bg download --profile dev
   ```

2. **Generate images.json:**
   ```bash
   cartopy-bg generate
   ```

3. **Run the notebook with uv (no installation needed):**
   ```bash
   uv run --with jupyter --with cartopy --with matplotlib \
     jupyter notebook examples/cartopy_usage_examples.ipynb
   ```

   Or with JupyterLab:
   ```bash
   uv run --with jupyterlab --with cartopy --with matplotlib jupyter lab
   ```

The notebook includes:
- Basic global map with BlueMarble background
- Regional maps (Europe, North America)
- Different map projections comparison
- Seasonal changes visualization
- Resolution comparison (low/mid/high)
- **Interactive widget** to choose month and resolution

### Option 2: Python Script

Run the standalone Python script to generate example images:

```bash
# Using uv (no installation needed)
uv run --with cartopy --with matplotlib \
  python examples/cartopy_usage_example.py

# Or if you have cartopy/matplotlib installed
python examples/cartopy_usage_example.py
```

This generates example maps in `examples/output/`.

## Installation Options

### Quick Run (No Installation)

Use `uv run --with` to run code without installing packages:

```bash
# Run a Python script with dependencies
uv run --with cartopy --with matplotlib python your_script.py

# Run a Jupyter notebook
uv run --with jupyter --with cartopy --with matplotlib jupyter notebook

# Run with ipywidgets for interactive notebooks
uv run --with jupyter --with cartopy --with matplotlib --with ipywidgets jupyter notebook
```

### Permanent Installation

If you prefer to install Cartopy and Matplotlib globally:

```bash
# With pip
pip install cartopy matplotlib

# With uv
uv pip install cartopy matplotlib

# With conda (recommended for cartopy due to complex dependencies)
conda install -c conda-forge cartopy matplotlib
```

## Example Usage in Your Code

### Basic Usage

```python
import cartopy.crs as ccrs
import cartopy.mpl.geoaxes as geoaxes
import matplotlib.pyplot as plt

# Load custom backgrounds from images.json
geoaxes.read_user_background_images('images.json')

# Create map with BlueMarble background
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Add background (use 'low', 'mid', or 'high' resolution)
ax.background_img(name='Blue Marble January', resolution='mid')

# Add map features
ax.coastlines()
ax.gridlines()

plt.show()
```

### Choose Different Months

```python
# Available months: January, February, March, ..., December
ax.background_img(name='Blue Marble July', resolution='mid')
```

### Choose Different Resolutions

```python
# Resolution options depend on what you downloaded:
# 'low': 720x360 (minimal profile)
# 'mid': 1440x720 (dev profile)
# 'high': 3600x1800 (prod profile)

ax.background_img(name='Blue Marble January', resolution='high')
```

### Regional Maps

```python
# Create map focused on specific region
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.background_img(name='Blue Marble April', resolution='mid')

# Set extent: [lon_min, lon_max, lat_min, lat_max]
ax.set_extent([-130, -60, 25, 50], crs=ccrs.PlateCarree())
```

### Different Projections

```python
# Orthographic (globe view)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(0, 45))
ax.background_img(name='Blue Marble July', resolution='mid')

# Mollweide (elliptical)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mollweide())
ax.background_img(name='Blue Marble July', resolution='mid')

# Robinson
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
ax.background_img(name='Blue Marble July', resolution='mid')
```

## Available Datasets

After downloading, you can use:

- **Blue Marble** - Standard NASA BlueMarble imagery
  - `name='Blue Marble {Month}'`

- **Blue Marble + Topography/Bathymetry** (if downloaded)
  - `name='Blue Marble TB {Month}'`

Check what's available:
```bash
cartopy-bg list-datasets
```

## Verifying Images

To verify your downloaded images are valid:

```bash
cartopy-bg verify
```

This checks that:
- All expected image files exist
- Files are valid PNG format
- File sizes are reasonable (not corrupted)

## Troubleshooting

### "Images not found" error

Make sure you've:
1. Downloaded images: `cartopy-bg download --profile dev`
2. Generated images.json: `cartopy-bg generate`
3. The paths in images.json are correct relative to where you're running your script

### Resolution not available

If you get an error about a resolution not being available:
- Check what you downloaded: `cartopy-bg verify`
- Download additional resolutions: `cartopy-bg download -r high`
- Use a lower resolution that you have downloaded

### Images look pixelated

For higher quality maps:
1. Download high-resolution images: `cartopy-bg download --profile prod`
2. Use `resolution='high'` in your code
3. Note: high-resolution images are much larger (~50MB per month)

## Performance Tips

- Use `resolution='low'` for quick testing and development
- Use `resolution='mid'` for most production use cases (good balance)
- Use `resolution='high'` only when you need publication-quality output
- Cache your background images - Cartopy loads them once and reuses them

## More Information

- [Cartopy Documentation](https://scitools.org.uk/cartopy/docs/latest/)
- [NASA Visible Earth](https://visibleearth.nasa.gov/)
- [Project README](../README.md)
