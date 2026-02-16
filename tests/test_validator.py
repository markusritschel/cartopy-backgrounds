"""Tests for image validator."""

from pathlib import Path

import pytest

from cartopy_backgrounds.datasets.bluemarble import BlueMarbleDataset
from cartopy_backgrounds.models.common import Month, Resolution
from cartopy_backgrounds.validator import ImageValidator, ValidationResult


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_is_ok_true(self):
        """Test is_ok when image exists and is valid."""
        result = ValidationResult(
            dataset_name="bluemarble",
            month=Month.JANUARY,
            resolution=Resolution.LOW,
            exists=True,
            valid=True,
            file_size=1024000,
        )
        assert result.is_ok is True

    def test_is_ok_false_missing(self):
        """Test is_ok when image is missing."""
        result = ValidationResult(
            dataset_name="bluemarble",
            month=Month.JANUARY,
            resolution=Resolution.LOW,
            exists=False,
            valid=False,
        )
        assert result.is_ok is False

    def test_is_ok_false_invalid(self):
        """Test is_ok when image exists but is invalid."""
        result = ValidationResult(
            dataset_name="bluemarble",
            month=Month.JANUARY,
            resolution=Resolution.LOW,
            exists=True,
            valid=False,
            error="Invalid PNG signature",
        )
        assert result.is_ok is False


class TestImageValidator:
    """Tests for ImageValidator class."""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory with sample images."""
        data_dir = tmp_path / "data"
        bluemarble_dir = data_dir / "bluemarble"
        bluemarble_dir.mkdir(parents=True)

        # Create valid PNG file
        valid_png = bluemarble_dir / "BlueMarble_January_720x360.png"
        with open(valid_png, "wb") as f:
            # Write PNG signature + some data
            f.write(b"\x89PNG\r\n\x1a\n")
            f.write(b"IHDR" + b"\x00" * 1024)  # Add some content

        # Create invalid PNG file (wrong signature)
        invalid_png = bluemarble_dir / "BlueMarble_February_720x360.png"
        with open(invalid_png, "wb") as f:
            f.write(b"NOT A PNG FILE")
            f.write(b"\x00" * 1024)

        # Create too-small file
        small_png = bluemarble_dir / "BlueMarble_March_720x360.png"
        with open(small_png, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            # Only header, no content (< 1KB)

        return data_dir

    @pytest.fixture
    def validator(self, temp_data_dir):
        """Create validator instance."""
        return ImageValidator(temp_data_dir)

    def test_validate_png_valid(self, validator, temp_data_dir):
        """Test validating a valid PNG file."""
        filepath = temp_data_dir / "bluemarble" / "BlueMarble_January_720x360.png"
        is_valid, error = validator.validate_png(filepath)
        assert is_valid is True
        assert error is None

    def test_validate_png_invalid_signature(self, validator, temp_data_dir):
        """Test validating file with invalid PNG signature."""
        filepath = temp_data_dir / "bluemarble" / "BlueMarble_February_720x360.png"
        is_valid, error = validator.validate_png(filepath)
        assert is_valid is False
        assert "Invalid PNG signature" in error

    def test_validate_png_too_small(self, validator, temp_data_dir):
        """Test validating file that is too small."""
        filepath = temp_data_dir / "bluemarble" / "BlueMarble_March_720x360.png"
        is_valid, error = validator.validate_png(filepath)
        assert is_valid is False
        assert "too small" in error

    def test_validate_png_not_found(self, validator, temp_data_dir):
        """Test validating file that doesn't exist."""
        filepath = temp_data_dir / "bluemarble" / "nonexistent.png"
        is_valid, error = validator.validate_png(filepath)
        assert is_valid is False
        assert error is not None

    def test_validate_image_valid(self, validator):
        """Test validating a valid image."""
        dataset = BlueMarbleDataset()
        result = validator.validate_image(dataset, Month.JANUARY, Resolution.LOW)

        assert result.dataset_name == "bluemarble"
        assert result.month == Month.JANUARY
        assert result.resolution == Resolution.LOW
        assert result.exists is True
        assert result.valid is True
        assert result.file_size is not None
        assert result.is_ok is True

    def test_validate_image_invalid(self, validator):
        """Test validating an invalid image."""
        dataset = BlueMarbleDataset()
        result = validator.validate_image(dataset, Month.FEBRUARY, Resolution.LOW)

        assert result.dataset_name == "bluemarble"
        assert result.month == Month.FEBRUARY
        assert result.exists is True
        assert result.valid is False
        assert result.error is not None
        assert result.is_ok is False

    def test_validate_image_missing(self, validator):
        """Test validating a missing image."""
        dataset = BlueMarbleDataset()
        result = validator.validate_image(dataset, Month.DECEMBER, Resolution.LOW)

        assert result.dataset_name == "bluemarble"
        assert result.month == Month.DECEMBER
        assert result.exists is False
        assert result.valid is False
        assert result.error == "File does not exist"
        assert result.is_ok is False

    def test_validate_dataset(self, validator):
        """Test validating entire dataset."""
        dataset = BlueMarbleDataset()
        results = validator.validate_dataset(
            dataset,
            months=[Month.JANUARY, Month.FEBRUARY, Month.MARCH],
            resolutions=[Resolution.LOW],
        )

        assert len(results) == 3
        assert results[0].month == Month.JANUARY
        assert results[1].month == Month.FEBRUARY
        assert results[2].month == Month.MARCH

    def test_validate_datasets(self, validator):
        """Test validating multiple datasets."""
        all_results = validator.validate_datasets(
            dataset_names=["bluemarble"],
            months=[Month.JANUARY, Month.FEBRUARY],
            resolutions=[Resolution.LOW],
        )

        assert "bluemarble" in all_results
        assert len(all_results["bluemarble"]) == 2

    def test_validate_datasets_unknown_dataset(self, validator):
        """Test that unknown datasets are skipped."""
        all_results = validator.validate_datasets(
            dataset_names=["unknown-dataset"],
            months=[Month.JANUARY],
            resolutions=[Resolution.LOW],
        )

        # Should not error, just skip unknown dataset
        assert "unknown-dataset" not in all_results
