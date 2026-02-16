"""HTTP download service with retry logic and progress tracking."""

import asyncio
from pathlib import Path
from typing import List, Tuple

import httpx
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from .utils.errors import DownloadError

console = Console()


class ImageDownloader:
    """HTTP downloader with async support, retry logic, and progress tracking.

    Features:
    - Async downloads with httpx
    - Exponential backoff retry logic
    - Rich progress bars showing speed and ETA
    - Streaming downloads for memory efficiency
    - Optional file overwriting control
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 30,
        force: bool = False,
        chunk_size: int = 8192,
    ):
        """Initialize the downloader.

        Args:
            max_retries: Maximum number of retry attempts for failed downloads
            timeout: Request timeout in seconds
            force: If True, overwrite existing files
            chunk_size: Size of chunks for streaming downloads (bytes)
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.force = force
        self.chunk_size = chunk_size

    async def download_file(
        self,
        url: str,
        filepath: Path,
        progress: Progress,
        task_id: TaskID,
    ) -> Path:
        """Download a single file with retry logic.

        Args:
            url: Download URL
            filepath: Destination file path
            progress: Rich progress instance for tracking
            task_id: Task ID for this download in the progress bar

        Returns:
            Path to downloaded file

        Raises:
            DownloadError: If download fails after all retries
        """
        # Skip if file exists and not forcing overwrite
        if filepath.exists() and not self.force:
            progress.update(task_id, description=f"✓ {filepath.name} (skipped)")
            progress.update(task_id, completed=1, total=1)
            return filepath

        # Create parent directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Retry loop with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("GET", url) as response:
                        response.raise_for_status()

                        # Get total file size for progress tracking
                        total = int(response.headers.get("content-length", 0))
                        progress.update(task_id, total=total)

                        # Stream download with progress updates
                        with open(filepath, "wb") as f:
                            downloaded = 0
                            async for chunk in response.aiter_bytes(
                                chunk_size=self.chunk_size
                            ):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task_id, completed=downloaded)

                # Success - update progress and return
                progress.update(task_id, description=f"✓ {filepath.name}")
                return filepath

            except (httpx.HTTPError, IOError) as e:
                # Handle failure
                if attempt < self.max_retries:
                    # Retry with exponential backoff
                    wait_time = 2**attempt
                    progress.update(
                        task_id,
                        description=f"⚠ {filepath.name} (retry {attempt}/{self.max_retries})",
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # All retries exhausted
                    progress.update(task_id, description=f"✗ {filepath.name} (failed)")
                    raise DownloadError(f"Failed to download {url}: {e}")

        # Should never reach here, but satisfy type checker
        raise DownloadError(f"Failed to download {url} after {self.max_retries} attempts")

    async def download_batch(
        self, downloads: List[Tuple[str, Path]]
    ) -> List[Path]:
        """Download multiple files concurrently with progress tracking.

        Args:
            downloads: List of (url, filepath) tuples to download

        Returns:
            List of downloaded file paths

        Note:
            Failed downloads raise DownloadError but don't stop other downloads.
            Check the progress output for individual failures.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            # Create tasks for all downloads
            tasks = []
            for url, filepath in downloads:
                desc = filepath.name
                task_id = progress.add_task(desc, total=None)
                tasks.append(self.download_file(url, filepath, progress, task_id))

            # Execute all downloads concurrently
            # Use return_exceptions=True to continue even if some fail
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return successful paths
        successful = []
        for result in results:
            if isinstance(result, Exception):
                console.print(f"[red]Error:[/red] {result}")
            else:
                successful.append(result)

        return successful
