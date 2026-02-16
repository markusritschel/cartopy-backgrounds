"""Tests for BlueMarble dataset implementation."""

import pytest

from cartopy_backgrounds.datasets.bluemarble import BlueMarbleDataset
from cartopy_backgrounds.models.common import Month, Resolution


class TestBlueMarbleDataset:
    """Tests for BlueMarbleDataset."""

    @pytest.fixture
    def dataset(self):
        """Create a BlueMarble dataset instance."""
        return BlueMarbleDataset()

    def test_name(self, dataset):
        """Test dataset name property."""
        assert dataset.name == "bluemarble"

    def test_display_name(self, dataset):
        """Test dataset display name."""
        assert dataset.display_name == "Blue Marble"

    def test_description(self, dataset):
        """Test dataset description."""
        assert "True color" in dataset.description
        assert "NASA" in dataset.description

    def test_get_dataset_ids(self, dataset):
        """Test that dataset IDs are returned for all months."""
        dataset_ids = dataset.get_dataset_ids()

        # Should have IDs for all 12 months
        assert len(dataset_ids) == 12

        # Check specific known IDs (verified by scraping)
        assert dataset_ids[Month.JANUARY] == "526293"
        assert dataset_ids[Month.DECEMBER] == "526308"

    def test_build_download_url(self, dataset):
        """Test URL building for downloads."""
        url = dataset.build_download_url("526293", Resolution.LOW)

        assert "https://neo.gsfc.nasa.gov/servlet/RenderData" in url
        assert "si=526293" in url
        assert "format=PNG" in url
        assert "width=720" in url
        assert "height=360" in url

    def test_get_available_resolutions(self, dataset):
        """Test that available resolutions are returned."""
        resolutions = dataset.get_available_resolutions()

        assert Resolution.LOW in resolutions
        assert Resolution.MID in resolutions
        assert Resolution.HIGH in resolutions
        # Ultra-high not available from NASA NEO
        assert Resolution.ULTRAHIGH not in resolutions

    def test_build_filename(self, dataset):
        """Test filename generation."""
        filename = dataset.build_filename(Month.JANUARY, Resolution.MID)
        assert filename == "BlueMarble_January_1440x720.png"

        filename = dataset.build_filename(Month.JULY, Resolution.HIGH)
        assert filename == "BlueMarble_July_3600x1800.png"

    def test_get_output_subdir(self, dataset):
        """Test output subdirectory name."""
        assert dataset.get_output_subdir() == "bluemarble"
