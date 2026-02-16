"""Dataset implementations for various NASA imagery sources."""

from .base import Dataset
from .bluemarble import BlueMarbleDataset
from .bluemarble_tb import BlueMarbleTBDataset
from .registry import DatasetRegistry

# Register all available datasets
DatasetRegistry.register(BlueMarbleDataset)
DatasetRegistry.register(BlueMarbleTBDataset)

__all__ = [
    "Dataset",
    "DatasetRegistry",
    "BlueMarbleDataset",
    "BlueMarbleTBDataset",
]
