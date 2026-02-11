"""Tests for the TopologyChecker."""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from geoqa.geometry import TopologyChecker


@pytest.fixture
def overlapping_polygons():
    """Two polygons that overlap."""
    p1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    p2 = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])  # overlaps p1
    p3 = Polygon([(5, 5), (6, 5), (6, 6), (5, 6)])  # separate
    return gpd.GeoDataFrame(geometry=[p1, p2, p3], crs="EPSG:4326")


@pytest.fixture
def non_overlapping_polygons():
    """Three non-overlapping polygons."""
    p1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    p2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    p3 = Polygon([(4, 0), (5, 0), (5, 1), (4, 1)])
    return gpd.GeoDataFrame(geometry=[p1, p2, p3], crs="EPSG:4326")


@pytest.fixture
def sliver_polygon():
    """A very thin sliver polygon."""
    sliver = Polygon([(0, 0), (10, 0), (10, 0.001), (0, 0.001)])
    normal = Polygon([(0, 5), (5, 5), (5, 10), (0, 10)])
    return gpd.GeoDataFrame(geometry=[sliver, normal], crs="EPSG:4326")


class TestTopologyChecker:
    def test_check_all_returns_dict(self, sample_polygons_gdf):
        tc = TopologyChecker(sample_polygons_gdf)
        result = tc.check_all()
        assert isinstance(result, dict)
        assert "bad_ring_count" in result
        assert "excessive_precision_count" in result
        assert "sliver_count" in result

    def test_self_overlaps_detected(self, overlapping_polygons):
        tc = TopologyChecker(overlapping_polygons)
        result = tc.check_self_overlaps()
        assert result["self_overlap_count"] > 0
        assert len(result["self_overlap_pairs"]) > 0

    def test_no_overlaps(self, non_overlapping_polygons):
        tc = TopologyChecker(non_overlapping_polygons)
        result = tc.check_self_overlaps()
        assert result["self_overlap_count"] == 0
        assert len(result["self_overlap_pairs"]) == 0

    def test_overlap_skip_on_large_dataset(self, sample_polygons_gdf):
        tc = TopologyChecker(sample_polygons_gdf)
        result = tc.check_all(max_features=2)  # force skip
        assert result["self_overlap_count"] == -1
        assert result["self_overlap_skipped"] is True

    def test_ring_validity(self, sample_polygons_gdf):
        tc = TopologyChecker(sample_polygons_gdf)
        result = tc.check_ring_validity()
        assert "bad_ring_count" in result
        assert "bad_ring_indices" in result
        assert isinstance(result["bad_ring_count"], int)

    def test_coordinate_precision(self, sample_polygons_gdf):
        tc = TopologyChecker(sample_polygons_gdf)
        result = tc.check_coordinate_precision()
        assert "excessive_precision_count" in result
        assert isinstance(result["excessive_precision_count"], int)

    def test_sliver_detection(self, sliver_polygon):
        tc = TopologyChecker(sliver_polygon)
        result = tc.check_slivers()
        assert result["sliver_count"] >= 1
        assert 0 in result["sliver_indices"]  # the sliver is at index 0

    def test_no_slivers_in_normal_data(self, non_overlapping_polygons):
        tc = TopologyChecker(non_overlapping_polygons)
        result = tc.check_slivers()
        assert result["sliver_count"] == 0

    def test_lines_skip_overlap(self, sample_lines_gdf):
        """Overlap detection should skip non-polygon data."""
        tc = TopologyChecker(sample_lines_gdf)
        result = tc.check_self_overlaps()
        assert result["self_overlap_count"] == 0

    def test_precision_with_high_decimal(self):
        """High-precision coordinates should be flagged."""
        p = Polygon(
            [
                (31.123456789012345, 30.123456789012345),
                (31.223456789012345, 30.123456789012345),
                (31.223456789012345, 30.223456789012345),
                (31.123456789012345, 30.223456789012345),
            ]
        )
        gdf = gpd.GeoDataFrame(geometry=[p], crs="EPSG:4326")
        tc = TopologyChecker(gdf)
        result = tc.check_coordinate_precision(max_decimals=6)
        assert result["excessive_precision_count"] == 1
