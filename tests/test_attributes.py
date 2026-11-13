"""Tests for the attribute profiling module."""

import pytest

from geoqa.attributes import AttributeProfiler


def test_boolean_column_profiled_as_categorical():
    """Boolean columns (plain and nullable) must not crash profiling."""
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame(
        {
            "flag": [True, False, True],
            "nflag": pd.array([True, None, False], dtype="boolean"),
        },
        geometry=[Point(0, 0), Point(1, 1), Point(2, 2)],
    )
    results = AttributeProfiler(gdf).profile_all()
    assert results["numeric_columns"] == []
    assert set(results["categorical_columns"]) == {"flag", "nflag"}
    assert results["column_stats"]["flag"]["most_common"] == "True"
    assert results["column_stats"]["nflag"]["null_count"] == 1


class TestAttributeProfiler:
    """Tests for AttributeProfiler."""

    def test_profile_all(self, sample_polygons_gdf):
        """Test profile_all returns expected keys."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        results = profiler.profile_all()
        assert "column_stats" in results
        assert "total_nulls" in results
        assert "completeness" in results
        assert "data_types" in results
        assert "numeric_columns" in results
        assert "categorical_columns" in results

    def test_column_stats(self, sample_polygons_gdf):
        """Test column stats are computed for all columns."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        results = profiler.profile_all()
        stats = results["column_stats"]
        assert "name" in stats
        assert "area_sqm" in stats
        assert "type" in stats

    def test_numeric_stats(self, sample_polygons_gdf):
        """Test numeric column statistics."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        results = profiler.profile_all()
        area_stats = results["column_stats"]["area_sqm"]
        assert area_stats["is_numeric"] is True
        assert "mean" in area_stats
        assert "median" in area_stats
        assert "min" in area_stats
        assert "max" in area_stats

    def test_categorical_stats(self, sample_polygons_gdf):
        """Test categorical column statistics."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        results = profiler.profile_all()
        type_stats = results["column_stats"]["type"]
        assert type_stats["is_numeric"] is False
        assert "most_common" in type_stats
        assert "top_values" in type_stats

    def test_null_detection(self, nulls_gdf):
        """Test null value detection."""
        profiler = AttributeProfiler(nulls_gdf)
        results = profiler.profile_all()
        assert results["total_nulls"] > 0
        # 'name' has 1 null, 'value' has 1 null, 'category' has 2 nulls
        assert results["total_nulls"] == 4

    def test_completeness(self, sample_polygons_gdf):
        """Test completeness is 100% for data without nulls."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        results = profiler.profile_all()
        for col, pct in results["completeness"].items():
            assert pct == 100.0

    def test_completeness_with_nulls(self, nulls_gdf):
        """Test completeness reflects null values."""
        profiler = AttributeProfiler(nulls_gdf)
        results = profiler.profile_all()
        # 'category' has 2 nulls out of 3 = 33.3% completeness
        assert results["completeness"]["category"] < 50

    def test_get_column_profile(self, sample_polygons_gdf):
        """Test getting profile for a specific column."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        stats = profiler.get_column_profile("area_sqm")
        assert stats["name"] == "area_sqm"
        assert stats["is_numeric"] is True

    def test_get_column_profile_invalid(self, sample_polygons_gdf):
        """Test error for invalid column name."""
        profiler = AttributeProfiler(sample_polygons_gdf)
        with pytest.raises(ValueError):
            profiler.get_column_profile("nonexistent")

    def test_points_with_nulls(self, sample_points_gdf):
        """Test profiling point data with null values."""
        profiler = AttributeProfiler(sample_points_gdf)
        results = profiler.profile_all()
        assert results["total_nulls"] == 1  # One null in 'value' column
