"""
Spatial analysis module.

Computes CRS information, spatial extent, area/length statistics,
and geometric measurements for the dataset.

Author: Ammar Yasser Abdalazim
"""

from __future__ import annotations

from typing import Any

import geopandas as gpd
import pandas as pd


class SpatialAnalyzer:
    """Performs spatial analysis on a GeoDataFrame.

    Computes:
    - CRS information (EPSG code, authority, units)
    - Spatial extent/bounds
    - Area statistics (for polygon features)
    - Length statistics (for line features)
    - Centroid information
    - Density metrics

    Args:
        gdf: The GeoDataFrame to analyze.
    """

    def __init__(self, gdf: gpd.GeoDataFrame) -> None:
        self._gdf = gdf

    def analyze(self) -> dict[str, Any]:
        """Run full spatial analysis.

        Returns:
            Dictionary with all spatial analysis results.
        """
        results = {}

        # CRS info
        results.update(self._crs_info())

        # Bounds
        results.update(self._compute_bounds())

        # Geometry type (from geometry checker's perspective)
        results["geometry_type"] = self._dominant_geometry_type()

        # Area/Length statistics
        results.update(self._measurement_stats())

        return results

    def _crs_info(self) -> dict[str, Any]:
        """Extract CRS information."""
        crs = self._gdf.crs

        if crs is None:
            return {
                "crs_defined": False,
                "crs_epsg": None,
                "crs_name": None,
                "crs_units": None,
                "crs_is_geographic": None,
                "crs_is_projected": None,
            }

        epsg = crs.to_epsg()
        name = crs.name if hasattr(crs, "name") else str(crs)

        # Determine units
        try:
            if crs.is_geographic:
                units = "degrees"
            else:
                axis_info = crs.axis_info
                units = axis_info[0].unit_name if axis_info else "unknown"
        except Exception:
            units = "unknown"

        return {
            "crs_defined": True,
            "crs_epsg": epsg,
            "crs_name": name,
            "crs_units": units,
            "crs_is_geographic": crs.is_geographic,
            "crs_is_projected": crs.is_projected,
        }

    def _compute_bounds(self) -> dict[str, Any]:
        """Compute spatial extent."""
        if len(self._gdf) == 0:
            return {"bounds": {}}

        try:
            total_bounds = self._gdf.total_bounds  # minx, miny, maxx, maxy
            return {
                "bounds": {
                    "minx": round(float(total_bounds[0]), 6),
                    "miny": round(float(total_bounds[1]), 6),
                    "maxx": round(float(total_bounds[2]), 6),
                    "maxy": round(float(total_bounds[3]), 6),
                },
                "center_x": round(float((total_bounds[0] + total_bounds[2]) / 2), 6),
                "center_y": round(float((total_bounds[1] + total_bounds[3]) / 2), 6),
            }
        except Exception:
            return {"bounds": {}}

    def _dominant_geometry_type(self) -> str:
        """Determine the dominant geometry type."""
        if len(self._gdf) == 0:
            return "Unknown"

        types: dict[str, int] = {}
        for geom in self._gdf.geometry:
            if geom is not None:
                gtype = geom.geom_type
                types[gtype] = types.get(gtype, 0) + 1

        if not types:
            return "Unknown"

        return max(types, key=types.get)

    def _measurement_stats(self) -> dict[str, Any]:
        """Compute area and length statistics based on geometry type."""
        results: dict[str, Any] = {}

        if len(self._gdf) == 0:
            return results

        dom_type = self._dominant_geometry_type().lower()

        if "polygon" in dom_type:
            areas = self._gdf.geometry.apply(
                lambda g: g.area if g is not None and not g.is_empty else 0
            )
            results["area_stats"] = {
                "mean": round(float(areas.mean()), 4),
                "median": round(float(areas.median()), 4),
                "std": round(float(areas.std()), 4),
                "min": round(float(areas.min()), 4),
                "max": round(float(areas.max()), 4),
                "total": round(float(areas.sum()), 4),
            }

            # Perimeter
            perimeters = self._gdf.geometry.apply(
                lambda g: g.length if g is not None and not g.is_empty else 0
            )
            results["perimeter_stats"] = {
                "mean": round(float(perimeters.mean()), 4),
                "median": round(float(perimeters.median()), 4),
                "total": round(float(perimeters.sum()), 4),
            }

        elif "line" in dom_type:
            lengths = self._gdf.geometry.apply(
                lambda g: g.length if g is not None and not g.is_empty else 0
            )
            results["length_stats"] = {
                "mean": round(float(lengths.mean()), 4),
                "median": round(float(lengths.median()), 4),
                "std": round(float(lengths.std()), 4),
                "min": round(float(lengths.min()), 4),
                "max": round(float(lengths.max()), 4),
                "total": round(float(lengths.sum()), 4),
            }

        elif "point" in dom_type:
            results["point_stats"] = {
                "count": len(self._gdf),
            }

        return results

    def geometry_stats(self) -> pd.DataFrame:
        """Compute per-feature geometry statistics.

        Returns:
            DataFrame with geometry measurements (area, length, centroid, etc.)
        """
        data = []

        for idx, row in self._gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                data.append(
                    {
                        "index": idx,
                        "geom_type": None,
                        "area": 0,
                        "length": 0,
                        "centroid_x": None,
                        "centroid_y": None,
                        "is_valid": False,
                        "is_empty": geom is None or (geom is not None and geom.is_empty),
                    }
                )
            else:
                centroid = geom.centroid
                data.append(
                    {
                        "index": idx,
                        "geom_type": geom.geom_type,
                        "area": round(geom.area, 6),
                        "length": round(geom.length, 6),
                        "centroid_x": round(centroid.x, 6),
                        "centroid_y": round(centroid.y, 6),
                        "is_valid": geom.is_valid,
                        "is_empty": geom.is_empty,
                    }
                )

        return pd.DataFrame(data)
