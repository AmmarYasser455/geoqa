"""Tests for the geometry checking module."""

import pytest

from geoqa.geometry import GeometryChecker


class TestGeometryChecker:
    """Tests for GeometryChecker."""

    def test_check_all(self, sample_polygons_gdf):
        """Test check_all returns all expected keys."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.check_all()
        assert "valid_count" in results
        assert "invalid_count" in results
        assert "empty_count" in results
        assert "duplicate_count" in results
        assert "mixed_types" in results
        assert "total_features" in results

    def test_valid_geometries(self, sample_polygons_gdf):
        """Test all valid geometries are detected."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.check_validity()
        assert results["valid_count"] == 5
        assert results["invalid_count"] == 0

    def test_invalid_geometries(self, invalid_geometry_gdf):
        """Test invalid geometry detection."""
        checker = GeometryChecker(invalid_geometry_gdf)
        results = checker.check_validity()
        assert results["invalid_count"] >= 1
        assert len(results["invalid_indices"]) >= 1
        assert len(results["invalid_reasons"]) >= 1

    def test_empty_geometries(self, invalid_geometry_gdf):
        """Test empty geometry detection."""
        checker = GeometryChecker(invalid_geometry_gdf)
        results = checker.check_empty()
        assert results["empty_count"] == 1
        assert 2 in results["empty_indices"]  # Third row (index 2) is empty

    def test_no_empty_geometries(self, sample_polygons_gdf):
        """Test no empty geometries in valid data."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.check_empty()
        assert results["empty_count"] == 0

    def test_duplicate_geometries(self, duplicate_geometry_gdf):
        """Test duplicate geometry detection."""
        checker = GeometryChecker(duplicate_geometry_gdf)
        results = checker.check_duplicates()
        assert results["duplicate_count"] >= 1

    def test_no_duplicates(self, sample_polygons_gdf):
        """Test no duplicates in unique data."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.check_duplicates()
        assert results["duplicate_count"] == 0

    def test_geometry_types(self, sample_polygons_gdf):
        """Test geometry type detection."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.check_geometry_types()
        assert results["mixed_types"] is False
        assert "Polygon" in results["geometry_types"]

    def test_complexity(self, sample_polygons_gdf):
        """Test complexity computation."""
        checker = GeometryChecker(sample_polygons_gdf)
        results = checker.compute_complexity()
        assert "avg_vertices" in results
        assert "total_vertices" in results
        assert results["total_vertices"] > 0

    def test_fix_invalid(self, invalid_geometry_gdf):
        """Test geometry repair."""
        checker = GeometryChecker(invalid_geometry_gdf)
        fixed = checker.fix_invalid()
        # After fixing, the bowtie should become valid
        for geom in fixed.geometry:
            if geom is not None and not geom.is_empty:
                assert geom.is_valid
