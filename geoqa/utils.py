"""
Utility functions for GeoQA.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Union

import geopandas as gpd


def load_geodata(
    source: Union[str, Path, gpd.GeoDataFrame],
    encoding: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """Load geospatial data from various sources.

    Supports: Shapefile, GeoJSON, GeoPackage, KML, CSV with geometry, and
    any format supported by Fiona/GDAL.

    Args:
        source: File path or GeoDataFrame.
        encoding: Optional character encoding for the file.

    Returns:
        A GeoDataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported.
    """
    if isinstance(source, gpd.GeoDataFrame):
        return source.copy()

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    kwargs = {}
    if encoding:
        kwargs["encoding"] = encoding

    return gpd.read_file(str(path), **kwargs)


def file_hash(filepath: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file for change detection.

    Args:
        filepath: Path to the file.

    Returns:
        Hex digest of the SHA-256 hash.
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def format_bytes(size: int) -> str:
    """Format byte size to human-readable string.

    Args:
        size: Size in bytes.

    Returns:
        Formatted string (e.g., '1.5 MB').
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def get_file_info(filepath: Union[str, Path]) -> dict:
    """Get file metadata.

    Args:
        filepath: Path to the file.

    Returns:
        Dict with file size, extension, and modification time.
    """
    path = Path(filepath)
    stat = path.stat()
    return {
        "name": path.name,
        "stem": path.stem,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "size_human": format_bytes(stat.st_size),
        "modified": stat.st_mtime,
    }
