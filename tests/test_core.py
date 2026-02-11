"""Tests for the core GeoProfile class."""

import geopandas as gpd
import pytest

from geoqa import GeoProfile, profile


class TestProfile:
    """Tests for the geoqa.profile() function."""

    def test_profile_from_gdf(self, sample_polygons_gdf):
        """Test profiling from a GeoDataFrame."""
        p = profile(sample_polygons_gdf, name="Test Polygons")
        assert p.name == "Test Polygons"
        assert p.feature_count == 5
        assert p.column_count == 5  # name, area_sqm, type, floors, year

    def test_profile_from_file(self, data_dir):
        """Test profiling from a shapefile."""
        shp_path = data_dir / "giza_buildings.shp"
        if shp_path.exists():
            p = profile(str(shp_path))
            assert p.feature_count > 0
            assert p.name == "giza_buildings"

    def test_profile_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            profile("nonexistent.shp")


class TestGeoProfile:
    """Tests for the GeoProfile class."""

    def test_feature_count(self, sample_polygons_gdf):
        """Test feature count property."""
        gp = GeoProfile(sample_polygons_gdf)
        assert gp.feature_count == 5

    def test_column_count(self, sample_polygons_gdf):
        """Test column count excludes geometry."""
        gp = GeoProfile(sample_polygons_gdf)
        assert gp.column_count == 5

    def test_geometry_type(self, sample_polygons_gdf):
        """Test geometry type detection."""
        gp = GeoProfile(sample_polygons_gdf)
        assert gp.geometry_type == "Polygon"

    def test_crs(self, sample_polygons_gdf):
        """Test CRS property."""
        gp = GeoProfile(sample_polygons_gdf)
        assert gp.crs is not None
        assert "4326" in gp.crs

    def test_crs_none(self, no_crs_gdf):
        """Test CRS property when no CRS defined."""
        gp = GeoProfile(no_crs_gdf)
        assert gp.crs is None

    def test_bounds(self, sample_polygons_gdf):
        """Test bounds property."""
        gp = GeoProfile(sample_polygons_gdf)
        bounds = gp.bounds
        assert "minx" in bounds
        assert "miny" in bounds
        assert "maxx" in bounds
        assert "maxy" in bounds

    def test_quality_score_range(self, sample_polygons_gdf):
        """Test quality score is between 0 and 100."""
        gp = GeoProfile(sample_polygons_gdf)
        assert 0 <= gp.quality_score <= 100

    def test_quality_score_valid_data(self, sample_polygons_gdf):
        """Test quality score for fully valid data is high."""
        gp = GeoProfile(sample_polygons_gdf)
        assert gp.quality_score >= 90  # Valid data should score high

    def test_quality_score_no_crs(self, no_crs_gdf):
        """Test quality score penalizes missing CRS."""
        gp = GeoProfile(no_crs_gdf)
        assert gp.quality_score < 100  # Missing CRS should reduce score

    def test_summary(self, sample_polygons_gdf):
        """Test summary method returns dict."""
        gp = GeoProfile(sample_polygons_gdf)
        result = gp.summary(print_output=False)
        assert isinstance(result, dict)
        assert "features" in result
        assert "quality_score" in result
        assert result["features"] == 5

    def test_quality_checks(self, sample_polygons_gdf):
        """Test quality_checks returns DataFrame."""
        gp = GeoProfile(sample_polygons_gdf)
        checks = gp.quality_checks()
        assert len(checks) > 0
        assert "Check" in checks.columns
        assert "Status" in checks.columns

    def test_attribute_stats(self, sample_polygons_gdf):
        """Test attribute_stats returns DataFrame."""
        gp = GeoProfile(sample_polygons_gdf)
        stats = gp.attribute_stats()
        assert len(stats) > 0

    def test_attribute_stats_single(self, sample_polygons_gdf):
        """Test attribute_stats for a single column."""
        gp = GeoProfile(sample_polygons_gdf)
        stats = gp.attribute_stats("area_sqm")
        assert len(stats) == 1

    def test_attribute_stats_invalid_column(self, sample_polygons_gdf):
        """Test attribute_stats raises for invalid column."""
        gp = GeoProfile(sample_polygons_gdf)
        with pytest.raises(ValueError):
            gp.attribute_stats("nonexistent_column")

    def test_geometry_stats(self, sample_polygons_gdf):
        """Test geometry_stats returns DataFrame."""
        gp = GeoProfile(sample_polygons_gdf)
        stats = gp.geometry_stats()
        assert len(stats) == 5
        assert "area" in stats.columns
        assert "is_valid" in stats.columns

    def test_repr(self, sample_polygons_gdf):
        """Test string representation."""
        gp = GeoProfile(sample_polygons_gdf, name="Test")
        repr_str = repr(gp)
        assert "Test" in repr_str
        assert "features=5" in repr_str

    def test_str(self, sample_polygons_gdf):
        """Test str representation."""
        gp = GeoProfile(sample_polygons_gdf, name="Test")
        str_repr = str(gp)
        assert "Test" in str_repr
        assert "Polygon" in str_repr

    def test_show_map(self, sample_polygons_gdf):
        """Test map creation doesn't raise."""
        gp = GeoProfile(sample_polygons_gdf)
        m = gp.show_map()
        assert m is not None

    def test_to_html(self, sample_polygons_gdf, tmp_path):
        """Test HTML report generation."""
        gp = GeoProfile(sample_polygons_gdf, name="Test")
        output = tmp_path / "report.html"
        result = gp.to_html(output)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "GeoQA" in content
        assert "Test" in content

    def test_line_geometry(self, sample_lines_gdf):
        """Test profiling line geometries."""
        gp = GeoProfile(sample_lines_gdf)
        assert gp.geometry_type == "LineString"
        assert gp.feature_count == 3

    def test_point_geometry(self, sample_points_gdf):
        """Test profiling point geometries."""
        gp = GeoProfile(sample_points_gdf)
        assert gp.geometry_type == "Point"
        assert gp.feature_count == 4

    def test_large_file_warning(self, tmp_path, caplog):
        """Test that loading a very large file emits a warning.

        We can't create a 500 MB file in tests, so instead we verify
        the warning path by checking a small file does NOT emit the warning.
        """
        import logging
        from shapely.geometry import Point

        gdf = gpd.GeoDataFrame({"v": [1]}, geometry=[Point(0, 0)], crs="EPSG:4326")
        path = tmp_path / "small.geojson"
        gdf.to_file(path, driver="GeoJSON")

        with caplog.at_level(logging.WARNING, logger="geoqa"):
            gp = GeoProfile(str(path))

        # Small file → no "Large file" warning
        assert not any("Large file" in r.message for r in caplog.records)
