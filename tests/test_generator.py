"""Tests for JSON generator."""

import json
from pathlib import Path

import pytest

from cartopy_backgrounds.datasets.bluemarble import BlueMarbleDataset
from cartopy_backgrounds.generator import JSONGenerator
from cartopy_backgrounds.models.common import Month, Resolution


class TestJSONGenerator:
    """Tests for JSONGenerator."""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory with sample images."""
        data_dir = tmp_path / "data"
        bluemarble_dir = data_dir / "bluemarble"
        bluemarble_dir.mkdir(parents=True)

        # Create sample image files
        (bluemarble_dir / "BlueMarble_January_720x360.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"  # PNG header
        )
        (bluemarble_dir / "BlueMarble_January_1440x720.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"
        )

        return data_dir

    @pytest.fixture
    def generator(self, temp_data_dir):
        """Create JSONGenerator instance."""
        return JSONGenerator(temp_data_dir)

    def test_find_image(self, generator, temp_data_dir):
        """Test finding image files."""
        dataset = BlueMarbleDataset()

        # Should find existing image
        path = generator._find_image(dataset, Month.JANUARY, Resolution.LOW)
        assert path is not None
        assert "BlueMarble_January_720x360.png" in path

        # Should return None for non-existent image
        path = generator._find_image(dataset, Month.FEBRUARY, Resolution.LOW)
        assert path is None

    def test_generate_entry(self, generator):
        """Test generating JSON entry for a single month."""
        dataset = BlueMarbleDataset()

        # Generate entry for January (has images)
        entry = generator._generate_entry(dataset, Month.JANUARY)
        assert entry is not None
        assert entry["__comment__"] == "Blue Marble January"
        assert entry["__source__"] == "NASA Visible Earth"
        assert entry["__projection__"] == "PlateCarree"
        assert "low" in entry
        assert "mid" in entry

        # Generate entry for February (no images)
        entry = generator._generate_entry(dataset, Month.FEBRUARY)
        assert entry is None

    def test_generate(self, generator, temp_data_dir, capsys):
        """Test full JSON generation."""
        output_file = temp_data_dir.parent / "test_images.json"

        # Generate JSON
        result_path = generator.generate(
            dataset_names=["bluemarble"],
            output_file=output_file,
            pretty=True,
        )

        assert result_path == output_file
        assert output_file.exists()

        # Validate JSON content
        with open(output_file) as f:
            config = json.load(f)

        assert "__comment__" in config
        assert "Blue Marble January" in config

        january_entry = config["Blue Marble January"]
        assert january_entry["__projection__"] == "PlateCarree"
        assert "low" in january_entry
        assert "mid" in january_entry

    def test_generate_pretty_vs_compact(self, generator, temp_data_dir):
        """Test pretty vs compact JSON output."""
        pretty_file = temp_data_dir.parent / "pretty.json"
        compact_file = temp_data_dir.parent / "compact.json"

        generator.generate(dataset_names=["bluemarble"], output_file=pretty_file, pretty=True)
        generator.generate(dataset_names=["bluemarble"], output_file=compact_file, pretty=False)

        # Pretty should have more whitespace
        pretty_size = pretty_file.stat().st_size
        compact_size = compact_file.stat().st_size
        assert pretty_size > compact_size

        # Both should be valid JSON
        with open(pretty_file) as f:
            pretty_data = json.load(f)
        with open(compact_file) as f:
            compact_data = json.load(f)

        # Content should be the same
        assert pretty_data.keys() == compact_data.keys()
