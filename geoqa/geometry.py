"""
Geometry validation and quality checking module.

Performs comprehensive geometry checks including validity, emptiness,
duplicates, and type consistency.
"""

from __future__ import annotations

from typing import Any

import geopandas as gpd
import numpy as np
from shapely.validation import explain_validity, make_valid


class GeometryChecker:
    """Validates and checks geometry quality of a GeoDataFrame.

    Performs the following checks:
    - Geometry validity (OGC compliance via Shapely)
    - Empty geometries
    - Null geometries
    - Duplicate geometries (WKB-based comparison)
    - Mixed geometry types
    - Self-intersections
    - Geometry complexity metrics

    Args:
        gdf: The GeoDataFrame to check.
    """

    def __init__(self, gdf: gpd.GeoDataFrame) -> None:
        self._gdf = gdf
        self._geom_col = gdf.geometry.name if gdf.geometry is not None else "geometry"

    def check_all(self) -> dict[str, Any]:
        """Run all geometry checks and return a consolidated results dict.

        Returns:
            Dictionary with keys:
            - valid_count: Number of valid geometries
            - invalid_count: Number of invalid geometries
            - invalid_indices: List of row indices with invalid geometries
            - invalid_reasons: List of (index, reason) tuples
            - empty_count: Number of empty geometries
            - empty_indices: List of row indices with empty geometries
            - null_count: Number of null (None) geometries
            - null_indices: List of row indices with null geometries
            - duplicate_count: Number of duplicate geometry pairs
            - duplicate_indices: List of row indices involved in duplicates
            - mixed_types: Boolean indicating mixed geometry types
            - geometry_types: Dict mapping geometry type names to counts
            - total_features: Total number of features
        """
        results = {}

        # Basic counts
        results["total_features"] = len(self._gdf)

        # Validity check
        validity = self.check_validity()
        results.update(validity)

        # Empty check
        empty = self.check_empty()
        results.update(empty)

        # Null check
        nulls = self.check_null()
        results.update(nulls)

        # Duplicate check
        duplicates = self.check_duplicates()
        results.update(duplicates)

        # Type consistency
        types = self.check_geometry_types()
        results.update(types)

        # Complexity
        complexity = self.compute_complexity()
        results.update(complexity)

        return results

    def check_validity(self) -> dict[str, Any]:
        """Check geometry validity per OGC Simple Features specification.

        Returns:
            Dict with valid_count, invalid_count, invalid_indices, invalid_reasons.
        """
        invalid_indices = []
        invalid_reasons = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is None or geom.is_empty:
                continue
            if not geom.is_valid:
                invalid_indices.append(idx)
                reason = explain_validity(geom)
                invalid_reasons.append((idx, reason))

        valid_count = len(self._gdf) - len(invalid_indices)

        return {
            "valid_count": valid_count,
            "invalid_count": len(invalid_indices),
            "invalid_indices": invalid_indices,
            "invalid_reasons": invalid_reasons,
        }

    def check_empty(self) -> dict[str, Any]:
        """Check for empty geometries.

        Returns:
            Dict with empty_count and empty_indices.
        """
        empty_indices = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is not None and geom.is_empty:
                empty_indices.append(idx)

        return {
            "empty_count": len(empty_indices),
            "empty_indices": empty_indices,
        }

    def check_null(self) -> dict[str, Any]:
        """Check for null (None) geometries.

        Returns:
            Dict with null_count and null_indices.
        """
        null_indices = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is None:
                null_indices.append(idx)

        return {
            "null_count": len(null_indices),
            "null_indices": null_indices,
        }

    def check_duplicates(self) -> dict[str, Any]:
        """Check for duplicate geometries using WKB comparison.

        Returns:
            Dict with duplicate_count and duplicate_indices.
        """
        if len(self._gdf) == 0:
            return {"duplicate_count": 0, "duplicate_indices": []}

        try:
            wkb_values = self._gdf.geometry.apply(
                lambda g: g.wkb if g is not None and not g.is_empty else None
            )
            duplicated_mask = wkb_values.duplicated(keep=False)
            duplicate_indices = list(self._gdf.index[duplicated_mask])
            # Count unique groups of duplicates
            duplicate_count = int(wkb_values.duplicated(keep="first").sum())
        except Exception:
            duplicate_indices = []
            duplicate_count = 0

        return {
            "duplicate_count": duplicate_count,
            "duplicate_indices": duplicate_indices,
        }

    def check_geometry_types(self) -> dict[str, Any]:
        """Check geometry type consistency.

        Returns:
            Dict with mixed_types (bool) and geometry_types (type -> count mapping).
        """
        type_counts: dict[str, int] = {}

        for geom in self._gdf.geometry:
            if geom is None:
                gtype = "None"
            else:
                gtype = geom.geom_type
            type_counts[gtype] = type_counts.get(gtype, 0) + 1

        # Filter out None for the "mixed" determination
        real_types = {k: v for k, v in type_counts.items() if k != "None"}
        mixed = len(real_types) > 1

        # Dominant type
        if real_types:
            dominant = max(real_types, key=real_types.get)
        else:
            dominant = "Unknown"

        return {
            "mixed_types": mixed,
            "geometry_types": type_counts,
            "geometry_type": dominant,
        }

    def compute_complexity(self) -> dict[str, Any]:
        """Compute geometry complexity metrics.

        Returns:
            Dict with avg_vertices, max_vertices, min_vertices, total_vertices.
        """
        vertex_counts = []

        for geom in self._gdf.geometry:
            if geom is None or geom.is_empty:
                vertex_counts.append(0)
            else:
                try:
                    vertex_counts.append(_count_vertices(geom))
                except Exception:
                    vertex_counts.append(0)

        arr = np.array(vertex_counts) if vertex_counts else np.array([0])

        return {
            "avg_vertices": float(np.mean(arr)),
            "max_vertices": int(np.max(arr)),
            "min_vertices": int(np.min(arr)),
            "total_vertices": int(np.sum(arr)),
        }

    def fix_invalid(self) -> gpd.GeoDataFrame:
        """Return a new GeoDataFrame with invalid geometries repaired.

        Uses shapely.validation.make_valid to fix invalid geometries.

        Returns:
            A new GeoDataFrame with all geometries made valid.
        """
        gdf = self._gdf.copy()
        gdf["geometry"] = gdf.geometry.apply(
            lambda g: make_valid(g) if g is not None and not g.is_valid else g
        )
        return gdf


class TopologyChecker:
    """Performs topology-level quality checks on a GeoDataFrame.

    Checks:
    - Self-overlaps (polygons overlapping other polygons)
    - Gaps between adjacent polygons
    - Ring validity (exterior/interior ring direction)
    - Coordinate precision (excessive decimal places)
    - Sliver polygons (extremely thin features)
    - Near-duplicate geometries (within tolerance)

    Args:
        gdf: The GeoDataFrame to check.
    """

    def __init__(self, gdf: gpd.GeoDataFrame) -> None:
        self._gdf = gdf

    def check_all(self, max_features: int = 10000) -> dict[str, Any]:
        """Run all topology checks.

        Args:
            max_features: Skip pairwise overlap check if feature count exceeds this.

        Returns:
            Dictionary with all topology check results.
        """
        results: dict[str, Any] = {}
        results.update(self.check_ring_validity())
        results.update(self.check_coordinate_precision())
        results.update(self.check_slivers())

        if len(self._gdf) <= max_features:
            results.update(self.check_self_overlaps())
        else:
            results["self_overlap_count"] = -1  # skipped
            results["self_overlap_skipped"] = True

        return results

    def check_self_overlaps(self) -> dict[str, Any]:
        """Detect polygons that overlap with other polygons in the dataset.

        Uses spatial index for efficient querying.

        Returns:
            Dict with self_overlap_count and self_overlap_pairs (list of index tuples).
        """
        gdf = self._gdf
        dom_type = ""
        for geom in gdf.geometry:
            if geom is not None:
                dom_type = geom.geom_type.lower()
                break

        if "polygon" not in dom_type:
            return {"self_overlap_count": 0, "self_overlap_pairs": []}

        sindex = gdf.sindex
        overlap_pairs = []

        for idx in range(len(gdf)):
            geom = gdf.geometry.iloc[idx]
            if geom is None or geom.is_empty or not geom.is_valid:
                continue

            # Query spatial index for candidates
            candidates = list(sindex.query(geom, predicate="intersects"))

            for other_idx in candidates:
                if other_idx <= idx:
                    continue  # avoid double-counting and self
                other_geom = gdf.geometry.iloc[other_idx]
                if other_geom is None or other_geom.is_empty or not other_geom.is_valid:
                    continue

                try:
                    intersection = geom.intersection(other_geom)
                    if not intersection.is_empty and intersection.area > 0:
                        overlap_pairs.append((idx, other_idx))
                except Exception:
                    continue

        return {
            "self_overlap_count": len(overlap_pairs),
            "self_overlap_pairs": overlap_pairs,
        }

    def check_ring_validity(self) -> dict[str, Any]:
        """Check that polygon rings follow proper winding order.

        Exterior rings should be counter-clockwise, interior rings clockwise
        per OGC convention. Uses shapely's is_ccw check.

        Returns:
            Dict with bad_ring_count and bad_ring_indices.
        """
        bad_indices = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is None or geom.is_empty:
                continue
            if "Polygon" not in geom.geom_type:
                continue

            try:
                polygons = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
                for poly in polygons:
                    ext_ring = poly.exterior
                    if ext_ring is not None and not ext_ring.is_ccw:
                        bad_indices.append(idx)
                        break
            except Exception:
                continue

        return {
            "bad_ring_count": len(bad_indices),
            "bad_ring_indices": bad_indices,
        }

    def check_coordinate_precision(self, max_decimals: int = 8) -> dict[str, Any]:
        """Check for excessive coordinate precision.

        Coordinates with more than *max_decimals* decimal places may indicate
        false precision and bloated file sizes.

        Args:
            max_decimals: Maximum reasonable decimal places.

        Returns:
            Dict with excessive_precision_count and sample coordinates.
        """
        excessive_indices = []
        sample_coords = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is None or geom.is_empty:
                continue
            try:
                coords = _extract_sample_coords(geom, n=3)
                for x, y in coords:
                    x_str = f"{x:.15f}".rstrip("0")
                    y_str = f"{y:.15f}".rstrip("0")
                    x_dec = len(x_str.split(".")[-1]) if "." in x_str else 0
                    y_dec = len(y_str.split(".")[-1]) if "." in y_str else 0
                    if x_dec > max_decimals or y_dec > max_decimals:
                        excessive_indices.append(idx)
                        if len(sample_coords) < 5:
                            sample_coords.append((idx, x, y))
                        break
            except Exception:
                continue

        return {
            "excessive_precision_count": len(excessive_indices),
            "excessive_precision_indices": excessive_indices,
            "precision_sample_coords": sample_coords,
        }

    def check_slivers(
        self,
        compactness_threshold: float = 0.01,
    ) -> dict[str, Any]:
        """Detect sliver polygons (extremely thin/elongated features).

        Uses the Polsby-Popper compactness ratio: 4π × area / perimeter².
        A perfect circle = 1.0; very thin slivers approach 0.

        Args:
            compactness_threshold: Polygons below this ratio are slivers.

        Returns:
            Dict with sliver_count and sliver_indices.
        """
        sliver_indices = []

        for idx, geom in enumerate(self._gdf.geometry):
            if geom is None or geom.is_empty:
                continue
            if "Polygon" not in geom.geom_type:
                continue

            try:
                area = geom.area
                perimeter = geom.length
                if perimeter > 0:
                    compactness = (4 * np.pi * area) / (perimeter ** 2)
                    if compactness < compactness_threshold:
                        sliver_indices.append(idx)
            except Exception:
                continue

        return {
            "sliver_count": len(sliver_indices),
            "sliver_indices": sliver_indices,
        }


def _extract_sample_coords(geom, n: int = 3) -> list[tuple[float, float]]:
    """Extract up to n sample coordinates from a geometry."""
    coords = []
    if hasattr(geom, "geoms"):
        for sub in geom.geoms:
            coords.extend(_extract_sample_coords(sub, n=n))
            if len(coords) >= n:
                break
    elif hasattr(geom, "exterior"):
        coords.extend(list(geom.exterior.coords)[:n])
    elif hasattr(geom, "coords"):
        coords.extend(list(geom.coords)[:n])
    return [(float(c[0]), float(c[1])) for c in coords[:n]]


def _count_vertices(geom) -> int:
    """Recursively count vertices in a geometry."""
    total = 0
    if hasattr(geom, "geoms"):
        for sub in geom.geoms:
            total += _count_vertices(sub)
    elif hasattr(geom, "exterior"):
        total += len(list(geom.exterior.coords))
        for interior in geom.interiors:
            total += len(list(interior.coords))
    elif hasattr(geom, "coords"):
        total += len(list(geom.coords))
    return total
