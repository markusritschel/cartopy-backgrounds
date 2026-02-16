"""Abstract base class for dataset implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from ..models.common import Month, Resolution


class Dataset(ABC):
    """Abstract base class for all dataset types.

    Each dataset implementation must provide methods for:
    - Retrieving dataset IDs
    - Building download URLs
    - Generating filenames
    - Listing available resolutions
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Dataset identifier (e.g., 'bluemarble').

        This is used in CLI commands and directory names.
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'Blue Marble').

        This is shown to users in help text and progress messages.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Dataset description.

        A brief description of what this dataset contains.
        """
        pass

    @abstractmethod
    def get_dataset_ids(self) -> Dict[Month, str]:
        """Get dataset IDs for all available months.

        Returns:
            Dictionary mapping Month enum to dataset ID strings.
        """
        pass

    @abstractmethod
    def build_download_url(self, dataset_id: str, resolution: Resolution) -> str:
        """Build download URL for given dataset ID and resolution.

        Args:
            dataset_id: The dataset identifier
            resolution: Target resolution

        Returns:
            Complete download URL
        """
        pass

    @abstractmethod
    def get_available_resolutions(self) -> List[Resolution]:
        """Get list of supported resolutions for this dataset.

        Returns:
            List of available Resolution enums
        """
        pass

    @abstractmethod
    def build_filename(self, month: Month, resolution: Resolution) -> str:
        """Generate filename for downloaded image.

        Args:
            month: Month of the image
            resolution: Image resolution

        Returns:
            Filename string (e.g., 'BlueMarble_January_1440x720.png')
        """
        pass

    def get_output_subdir(self) -> str:
        """Get subdirectory name for this dataset.

        By default, uses the dataset name. Can be overridden.

        Returns:
            Subdirectory name (e.g., 'bluemarble')
        """
        return self.name

    def validate_image(self, filepath: Path) -> bool:
        """Validate downloaded image.

        Default implementation checks PNG signature. Can be overridden
        for datasets with different image formats.

        Args:
            filepath: Path to the image file

        Returns:
            True if valid, False otherwise
        """
        if not filepath.exists():
            return False

        try:
            with open(filepath, "rb") as f:
                header = f.read(8)
                return header == b"\x89PNG\r\n\x1a\n"
        except IOError:
            return False
