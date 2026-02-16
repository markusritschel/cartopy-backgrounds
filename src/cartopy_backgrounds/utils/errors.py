"""Custom exception classes for the package."""


class CartopyBackgroundsError(Exception):
    """Base exception for all cartopy-backgrounds errors."""

    pass


class DownloadError(CartopyBackgroundsError):
    """Raised when an image download fails."""

    pass


class ValidationError(CartopyBackgroundsError):
    """Raised when image validation fails."""

    pass


class DatasetError(CartopyBackgroundsError):
    """Raised when there's an issue with a dataset."""

    pass


class ConfigurationError(CartopyBackgroundsError):
    """Raised when there's a configuration error."""

    pass
