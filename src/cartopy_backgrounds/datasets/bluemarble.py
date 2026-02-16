"""NASA Blue Marble Next Generation dataset implementation."""

from typing import Dict, List

from ..models.common import Month, Resolution
from .base import Dataset


class BlueMarbleDataset(Dataset):
    """NASA Blue Marble Next Generation dataset.

    This dataset provides true-color satellite imagery of Earth without
    clouds, collected by NASA's Terra satellite. Images are from 2004,
    with one image per month showing seasonal changes.

    Data source: https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG
    """

    # Hardcoded dataset IDs for 2004 Blue Marble imagery
    # These IDs are stable and used to construct download URLs
    # Verified by scraping from NASA NEO website
    DATASET_IDS = {
        Month.JANUARY: "526293",
        Month.FEBRUARY: "526297",
        Month.MARCH: "526303",
        Month.APRIL: "526310",
        Month.MAY: "526301",
        Month.JUNE: "526299",
        Month.JULY: "526302",
        Month.AUGUST: "526300",
        Month.SEPTEMBER: "526313",
        Month.OCTOBER: "526314",
        Month.NOVEMBER: "526292",
        Month.DECEMBER: "526308",
    }

    @property
    def name(self) -> str:
        """Dataset identifier: 'bluemarble'."""
        return "bluemarble"

    @property
    def display_name(self) -> str:
        """Human-readable name: 'Blue Marble'."""
        return "Blue Marble"

    @property
    def description(self) -> str:
        """Dataset description."""
        return "NASA Blue Marble Next Generation - True color Earth satellite imagery"

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

        Blue Marble from NASA NEO supports low, mid, and high resolutions.
        Ultra-high resolution requires a different data source.

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
            Filename string following pattern: BlueMarble_{Month}_{Width}x{Height}.png
        """
        return f"BlueMarble_{month.value}_{resolution.value}.png"
