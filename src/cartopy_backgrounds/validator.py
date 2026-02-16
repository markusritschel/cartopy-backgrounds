"""Image validation service for verifying downloaded images."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .datasets.base import Dataset
from .datasets.registry import DatasetRegistry
from .models.common import Month, Resolution
from .utils.errors import DatasetError


class ValidationResult:
    """Result of validating a single image."""

    def __init__(
        self,
        dataset_name: str,
        month: Month,
        resolution: Resolution,
        exists: bool,
        valid: bool,
        file_size: Optional[int] = None,
        error: Optional[str] = None,
    ):
        self.dataset_name = dataset_name
        self.month = month
        self.resolution = resolution
        self.exists = exists
        self.valid = valid
        self.file_size = file_size
        self.error = error

    @property
    def is_ok(self) -> bool:
        """Check if image is valid and exists."""
        return self.exists and self.valid

    def __repr__(self) -> str:
        status = "OK" if self.is_ok else "FAILED"
        return f"<ValidationResult {self.dataset_name}/{self.month.value}/{self.resolution.value}: {status}>"


class ImageValidator:
    """Validates downloaded images."""

    # PNG file signature (magic bytes)
    PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

    # Minimum expected file size (in bytes) - helps detect corrupted/incomplete downloads
    MIN_FILE_SIZE = 1024  # 1KB minimum

    def __init__(self, data_dir: Path):
        """Initialize validator.

        Args:
            data_dir: Base directory containing downloaded images
        """
        self.data_dir = data_dir

    def validate_png(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """Validate that a file is a valid PNG.

        Args:
            filepath: Path to the image file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            file_size = filepath.stat().st_size
            if file_size < self.MIN_FILE_SIZE:
                return False, f"File too small ({file_size} bytes, expected > {self.MIN_FILE_SIZE})"

            # Check PNG signature
            with open(filepath, "rb") as f:
                header = f.read(8)
                if header != self.PNG_SIGNATURE:
                    return False, "Invalid PNG signature"

            return True, None

        except Exception as e:
            return False, str(e)

    def validate_image(
        self, dataset: Dataset, month: Month, resolution: Resolution
    ) -> ValidationResult:
        """Validate a single image.

        Args:
            dataset: Dataset instance
            month: Month to validate
            resolution: Resolution to validate

        Returns:
            ValidationResult with validation details
        """
        # Build expected file path
        dataset_dir = self.data_dir / dataset.get_output_subdir()
        filename = dataset.build_filename(month, resolution)
        filepath = dataset_dir / filename

        # Check if file exists
        if not filepath.exists():
            return ValidationResult(
                dataset_name=dataset.name,
                month=month,
                resolution=resolution,
                exists=False,
                valid=False,
                error="File does not exist",
            )

        # Validate file
        file_size = filepath.stat().st_size
        is_valid, error = self.validate_png(filepath)

        return ValidationResult(
            dataset_name=dataset.name,
            month=month,
            resolution=resolution,
            exists=True,
            valid=is_valid,
            file_size=file_size,
            error=error,
        )

    def validate_dataset(
        self,
        dataset: Dataset,
        months: Optional[List[Month]] = None,
        resolutions: Optional[List[Resolution]] = None,
    ) -> List[ValidationResult]:
        """Validate all images for a dataset.

        Args:
            dataset: Dataset to validate
            months: Months to validate (default: all)
            resolutions: Resolutions to validate (default: all available)

        Returns:
            List of ValidationResult objects
        """
        if months is None:
            months = list(Month)

        if resolutions is None:
            resolutions = dataset.get_available_resolutions()

        results = []
        dataset_ids = dataset.get_dataset_ids()

        for month in months:
            # Skip months not available for this dataset
            if month not in dataset_ids:
                continue

            for resolution in resolutions:
                # Skip resolutions not available for this dataset
                if resolution not in dataset.get_available_resolutions():
                    continue

                result = self.validate_image(dataset, month, resolution)
                results.append(result)

        return results

    def validate_datasets(
        self,
        dataset_names: List[str],
        months: Optional[List[Month]] = None,
        resolutions: Optional[List[Resolution]] = None,
    ) -> Dict[str, List[ValidationResult]]:
        """Validate multiple datasets.

        Args:
            dataset_names: List of dataset names to validate
            months: Months to validate (default: all)
            resolutions: Resolutions to validate (default: all available)

        Returns:
            Dictionary mapping dataset names to validation results
        """
        all_results = {}

        for dataset_name in dataset_names:
            try:
                dataset = DatasetRegistry.get(dataset_name)
                results = self.validate_dataset(dataset, months, resolutions)
                all_results[dataset_name] = results
            except DatasetError:
                # Dataset not found - skip
                continue

        return all_results
