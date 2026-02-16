"""NASA Blue Marble + Topography and Bathymetry dataset implementation."""

from typing import Dict, List

from ..models.common import Month, Resolution
from .base import Dataset


class BlueMarbleTBDataset(Dataset):
    """NASA Blue Marble + Topography and Bathymetry dataset.

    This dataset provides Blue Marble imagery with added topographic
    and bathymetric shading, giving a 3D appearance to terrain and
    ocean depths.

    Data source: https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG-TB
    """

    # Dataset IDs for Blue Marble + Topography/Bathymetry
    # Note: These need to be confirmed/scraped from the NASA website
    DATASET_IDS = {
        Month.JANUARY: "526314",
        Month.FEBRUARY: "526315",
        Month.MARCH: "526316",
        Month.APRIL: "526317",
        Month.MAY: "526318",
        Month.JUNE: "526319",
        Month.JULY: "526320",
        Month.AUGUST: "526321",
        Month.SEPTEMBER: "526322",
        Month.OCTOBER: "526323",
        Month.NOVEMBER: "526324",
        Month.DECEMBER: "526325",
    }

    @property
    def name(self) -> str:
        """Dataset identifier: 'bluemarble-tb'."""
        return "bluemarble-tb"

    @property
    def display_name(self) -> str:
        """Human-readable name: 'Blue Marble + Topography/Bathymetry'."""
        return "Blue Marble + Topography/Bathymetry"

    @property
    def description(self) -> str:
        """Dataset description."""
        return "Blue Marble with added topographic and bathymetric shading"

    def get_dataset_ids(self) -> Dict[Month, str]:
        """Get dataset IDs for all months.

        Returns:
            Dictionary mapping Month to dataset ID string
        """
        return self.DATASET_IDS

    def build_download_url(self, dataset_id: str, resolution: Resolution) -> str:
        """Build NASA NEO download URL.

        Args:
            dataset_id: NASA dataset identifier
            resolution: Target resolution

        Returns:
            Complete download URL for the NASA RenderData servlet
        """
        width = resolution.width
        height = resolution.height
        return (
            f"https://neo.gsfc.nasa.gov/servlet/RenderData"
            f"?si={dataset_id}&cs=rgb&format=PNG"
            f"&width={width}&height={height}"
        )

    def get_available_resolutions(self) -> List[Resolution]:
        """Get supported resolutions.

        Returns:
            List of available Resolution enums
        """
        return [Resolution.LOW, Resolution.MID, Resolution.HIGH]

    def build_filename(self, month: Month, resolution: Resolution) -> str:
        """Generate filename for downloaded image.

        Args:
            month: Month of the image
            resolution: Image resolution

        Returns:
            Filename string following pattern: BlueMarbleTB_{Month}_{Width}x{Height}.png
        """
        return f"BlueMarbleTB_{month.value}_{resolution.value}.png"
