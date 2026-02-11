"""
Attribute profiling module.

Generates statistical profiles for all non-geometry columns including
data types, null counts, unique values, and descriptive statistics.
"""

from __future__ import annotations

from typing import Any

import geopandas as gpd
import pandas as pd


class AttributeProfiler:
    """Profiles attribute (non-geometry) columns of a GeoDataFrame.

    Computes:
    - Data types and type distribution
    - Null/missing value counts per column
    - Unique value counts
    - Descriptive statistics for numeric columns
    - Value frequency for categorical columns
    - Overall completeness metrics

    Args:
        gdf: The GeoDataFrame to profile.
    """

    def __init__(self, gdf: gpd.GeoDataFrame) -> None:
        self._gdf = gdf
        geom_col = gdf.geometry.name if gdf.geometry is not None else "geometry"
        self._attr_cols = [c for c in gdf.columns if c != geom_col]

    def profile_all(self) -> dict[str, Any]:
        """Run all attribute profiling checks.

        Returns:
            Dictionary with:
            - column_stats: Per-column statistics dict
            - total_nulls: Total null count across all columns
            - completeness: Per-column completeness percentages
            - data_types: Per-column data type names
            - numeric_columns: List of numeric column names
            - categorical_columns: List of categorical column names
        """
        results = {}

        column_stats = {}
        total_nulls = 0
        completeness = {}
        data_types = {}
        numeric_cols = []
        categorical_cols = []

        for col in self._attr_cols:
            stats = self._profile_column(col)
            column_stats[col] = stats
            total_nulls += stats.get("null_count", 0)

            nrows = len(self._gdf)
            col_completeness = (
                ((nrows - stats.get("null_count", 0)) / nrows * 100) if nrows > 0 else 100
            )
            completeness[col] = round(col_completeness, 1)
            data_types[col] = stats.get("dtype", "unknown")

            if stats.get("is_numeric", False):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)

        results["column_stats"] = column_stats
        results["total_nulls"] = total_nulls
        results["completeness"] = completeness
        results["data_types"] = data_types
        results["numeric_columns"] = numeric_cols
        results["categorical_columns"] = categorical_cols

        return results

    def _profile_column(self, col: str) -> dict[str, Any]:
        """Profile a single column.

        Args:
            col: Column name to profile.

        Returns:
            Dict with column statistics.
        """
        series = self._gdf[col]
        stats: dict[str, Any] = {
            "name": col,
            "dtype": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "non_null_count": int(series.notnull().sum()),
            "unique_count": int(series.nunique()),
            "is_numeric": pd.api.types.is_numeric_dtype(series),
        }

        nrows = len(series)
        if nrows > 0:
            stats["null_percentage"] = round(stats["null_count"] / nrows * 100, 2)
        else:
            stats["null_percentage"] = 0.0

        if stats["is_numeric"]:
            stats.update(self._numeric_stats(series))
        else:
            stats.update(self._categorical_stats(series))

        return stats

    def _numeric_stats(self, series: pd.Series) -> dict[str, Any]:
        """Compute descriptive statistics for a numeric column."""
        clean = series.dropna()

        if len(clean) == 0:
            return {
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "q25": None,
                "q75": None,
                "zeros": 0,
                "negatives": 0,
            }

        return {
            "mean": round(float(clean.mean()), 4),
            "median": round(float(clean.median()), 4),
            "std": round(float(clean.std()), 4),
            "min": round(float(clean.min()), 4),
            "max": round(float(clean.max()), 4),
            "q25": round(float(clean.quantile(0.25)), 4),
            "q75": round(float(clean.quantile(0.75)), 4),
            "zeros": int((clean == 0).sum()),
            "negatives": int((clean < 0).sum()),
        }

    def _categorical_stats(self, series: pd.Series) -> dict[str, Any]:
        """Compute statistics for a categorical/string column."""
        clean = series.dropna()

        if len(clean) == 0:
            return {
                "most_common": None,
                "most_common_count": 0,
                "least_common": None,
                "least_common_count": 0,
                "avg_length": None,
                "max_length": None,
                "min_length": None,
                "top_values": {},
            }

        value_counts = clean.value_counts()
        top_n = min(5, len(value_counts))
        top_values = value_counts.head(top_n).to_dict()

        # String length stats
        str_series = clean.astype(str)
        lengths = str_series.str.len()

        return {
            "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "most_common_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "least_common": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
            "least_common_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
            "avg_length": round(float(lengths.mean()), 1),
            "max_length": int(lengths.max()),
            "min_length": int(lengths.min()),
            "top_values": {str(k): int(v) for k, v in top_values.items()},
        }

    def get_column_profile(self, col: str) -> dict[str, Any]:
        """Get profile for a specific column.

        Args:
            col: Column name.

        Returns:
            Dict with column statistics.

        Raises:
            ValueError: If column not found.
        """
        if col not in self._attr_cols:
            raise ValueError(f"Column '{col}' not found. Available: {self._attr_cols}")
        return self._profile_column(col)
