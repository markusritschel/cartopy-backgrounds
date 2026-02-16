# Justfile for cartopy-backgrounds project
# Run with: just <recipe>

# Default recipe - show available commands
default:
    @just --list

# Install project dependencies
install:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --group dev

# Run all tests
test *ARGS:
    uv run pytest {{ARGS}}

# Run tests with coverage report
test-coverage:
    uv run pytest --cov=cartopy_backgrounds --cov-report=term-missing

# Run tests and generate HTML coverage report
test-coverage-html:
    uv run pytest --cov=cartopy_backgrounds --cov-report=html
    @echo "Coverage report generated in htmlcov/index.html"

# Lint code with ruff
lint *ARGS:
    uv run ruff check src/ {{ARGS}}

# Format code with ruff
format:
    uv run ruff format src/

# Type check with mypy
typecheck:
    uv run mypy src/

# Run all quality checks (lint + typecheck + test)
check: lint typecheck test
    @echo "✓ All checks passed!"

# Download minimal test dataset (January only, low resolution)
download-test:
    uv run cartopy-bg download --profile minimal -m Jan --generate-json
    @echo "✓ Test download complete: data/bluemarble/BlueMarble_January_720x360.png"

# Download development dataset (all months, low+mid resolution)
download-dev:
    uv run cartopy-bg download --profile dev --generate-json
    @echo "✓ Development dataset downloaded"

# Download production dataset (all months, low+mid+high resolution)
download-prod:
    uv run cartopy-bg download --profile prod --generate-json
    @echo "✓ Production dataset downloaded"

# Download all datasets with dev profile
download-all-dev:
    uv run cartopy-bg download -d all --profile dev --generate-json
    @echo "✓ All datasets downloaded (dev profile)"

# List available datasets
list-datasets:
    uv run cartopy-bg list-datasets

# Generate images.json from existing downloads
generate-json:
    uv run cartopy-bg generate
    @echo "✓ Generated images.json"

# Verify dataset IDs against NASA website
verify-ids:
    uv run python scripts/verify_dataset_ids.py

# Clean downloaded data files
clean-data:
    rm -rf data/*
    rm -f images.json
    @echo "✓ Cleaned downloaded data"

# Clean build artifacts and cache
clean-build:
    rm -rf build/ dist/ .eggs/ *.egg-info
    rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/
    rm -rf htmlcov/ .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "✓ Cleaned build artifacts"

# Clean everything (data + build artifacts)
clean: clean-data clean-build
    @echo "✓ Cleaned all generated files"

# Show CLI help
help:
    uv run cartopy-bg --help

# Run a quick validation workflow
validate: install-dev test download-test
    @echo "✓ Validation complete!"
    @echo "  - Dependencies installed"
    @echo "  - All tests passing"
    @echo "  - Test download successful"

# Full validation including all quality checks
validate-full: install-dev check download-all-dev
    @echo "✓ Full validation complete!"
    @echo "  - Code quality checks passed"
    @echo "  - All datasets downloaded"

# Show project status
status:
    @echo "=== Cartopy Backgrounds Project Status ==="
    @echo ""
    @echo "Git branch:"
    @git branch --show-current
    @echo ""
    @echo "Git status:"
    @git status --short
    @echo ""
    @echo "Downloaded datasets:"
    @ls -lh data/ 2>/dev/null || echo "  No data downloaded yet"
    @echo ""
    @echo "Test results:"
    @uv run pytest --quiet --tb=no 2>/dev/null && echo "  ✓ All tests passing" || echo "  ✗ Some tests failing"


# Install example dependencies
install-examples:
    uv sync --extra examples

# Run Jupyter notebook with Cartopy examples
example-notebook:
    @echo "Starting Jupyter notebook with Cartopy examples..."
    uv run --extra examples jupyter notebook examples/cartopy_usage_examples.ipynb

# Run JupyterLab with Cartopy examples
example-lab:
    @echo "Starting JupyterLab with Cartopy examples..."
    uv run --extra examples --with jupyterlab jupyter lab

# Generate example images using Python script
example-images:
    @echo "Generating example images..."
    uv run --extra examples python examples/cartopy_usage_example.py
    @echo "✓ Examples generated in examples/output/"
