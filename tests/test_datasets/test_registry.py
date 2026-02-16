"""Tests for dataset registry."""

import pytest

from cartopy_backgrounds.datasets.base import Dataset
from cartopy_backgrounds.datasets.bluemarble import BlueMarbleDataset
from cartopy_backgrounds.datasets.bluemarble_tb import BlueMarbleTBDataset
from cartopy_backgrounds.datasets.registry import DatasetRegistry
from cartopy_backgrounds.models.common import Month, Resolution
from cartopy_backgrounds.utils.errors import DatasetError


class TestDatasetRegistry:
    """Tests for DatasetRegistry."""

    def test_get_bluemarble(self):
        """Test getting BlueMarble dataset from registry."""
        dataset = DatasetRegistry.get("bluemarble")
        assert isinstance(dataset, BlueMarbleDataset)
        assert dataset.name == "bluemarble"

    def test_get_bluemarble_tb(self):
        """Test getting BlueMarble-TB dataset from registry."""
        dataset = DatasetRegistry.get("bluemarble-tb")
        assert isinstance(dataset, BlueMarbleTBDataset)
        assert dataset.name == "bluemarble-tb"

    def test_get_unknown_dataset(self):
        """Test that getting unknown dataset raises error."""
        with pytest.raises(DatasetError, match="Unknown dataset"):
            DatasetRegistry.get("nonexistent")

    def test_get_names(self):
        """Test getting all registered dataset names."""
        names = DatasetRegistry.get_names()
        assert "bluemarble" in names
        assert "bluemarble-tb" in names
        assert len(names) >= 2

    def test_list_all(self):
        """Test listing all registered datasets."""
        datasets = DatasetRegistry.list_all()
        assert len(datasets) >= 2

        # Check that all are Dataset instances
        for dataset in datasets:
            assert isinstance(dataset, Dataset)

    def test_is_registered(self):
        """Test checking if dataset is registered."""
        assert DatasetRegistry.is_registered("bluemarble") is True
        assert DatasetRegistry.is_registered("bluemarble-tb") is True
        assert DatasetRegistry.is_registered("nonexistent") is False
