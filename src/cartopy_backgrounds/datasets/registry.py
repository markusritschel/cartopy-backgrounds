"""Central registry for all available datasets."""

from typing import Dict, List, Type

from ..utils.errors import DatasetError
from .base import Dataset


class DatasetRegistry:
    """Central registry for managing dataset types.

    This implements the Registry pattern, allowing datasets to be
    registered centrally and retrieved by name.
    """

    _datasets: Dict[str, Type[Dataset]] = {}

    @classmethod
    def register(cls, dataset_class: Type[Dataset]) -> None:
        """Register a dataset type.

        Args:
            dataset_class: Dataset class to register

        Raises:
            DatasetError: If a dataset with the same name is already registered
        """
        instance = dataset_class()
        if instance.name in cls._datasets:
            raise DatasetError(f"Dataset '{instance.name}' is already registered")
        cls._datasets[instance.name] = dataset_class

    @classmethod
    def get(cls, name: str) -> Dataset:
        """Get dataset instance by name.

        Args:
            name: Dataset identifier

        Returns:
            New instance of the dataset

        Raises:
            DatasetError: If dataset name is not registered
        """
        if name not in cls._datasets:
            available = ", ".join(cls._datasets.keys())
            raise DatasetError(
                f"Unknown dataset: '{name}'. Available datasets: {available}"
            )
        return cls._datasets[name]()

    @classmethod
    def list_all(cls) -> List[Dataset]:
        """Get all registered datasets.

        Returns:
            List of dataset instances
        """
        return [ds_class() for ds_class in cls._datasets.values()]

    @classmethod
    def get_names(cls) -> List[str]:
        """Get all registered dataset names.

        Returns:
            List of dataset identifier strings
        """
        return list(cls._datasets.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a dataset is registered.

        Args:
            name: Dataset identifier

        Returns:
            True if registered, False otherwise
        """
        return name in cls._datasets
