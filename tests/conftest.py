"""Shared test fixtures for GeoQA tests."""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import LineString, MultiPolygon, Point, Polygon


@pytest.fixture
def sample_polygons_gdf():
    """Create a sample GeoDataFrame with polygon geometries."""
    polys = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
    ]
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", "B", "C", "D", "E"],
            "area_sqm": [100.0, 200.0, 150.0, 300.0, 250.0],
            "type": ["residential", "commercial", "residential", "industrial", "commercial"],
            "floors": [2, 5, 3, 1, 4],
            "year": [2000, 2010, 2005, 2015, 2020],
        },
        geometry=polys,
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def sample_lines_gdf():
    """Create a sample GeoDataFrame with line geometries."""
    lines = [
        LineString([(0, 0), (1, 1), (2, 0)]),
        LineString([(0, 1), (1, 2), (2, 1)]),
        LineString([(0, 2), (1, 3), (2, 2)]),
    ]
    gdf = gpd.GeoDataFrame(
        {
            "road_name": ["Main St", "Oak Ave", "Park Blvd"],
            "speed_limit": [50, 30, 40],
            "lanes": [4, 2, 3],
        },
        geometry=lines,
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def sample_points_gdf():
    """Create a sample GeoDataFrame with point geometries."""
    points = [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]
    gdf = gpd.GeoDataFrame(
        {
            "label": ["P1", "P2", "P3", "P4"],
            "value": [10.5, 20.3, 30.1, None],
        },
        geometry=points,
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def invalid_geometry_gdf():
    """Create a GeoDataFrame with invalid geometries."""
    # Bowtie polygon (self-intersecting)
    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2)])  # Self-intersecting
    valid_poly = Polygon([(3, 0), (4, 0), (4, 1), (3, 1)])
    empty_poly = Polygon()  # Empty geometry

    gdf = gpd.GeoDataFrame(
        {
            "name": ["Bowtie", "Valid", "Empty"],
            "value": [1, 2, 3],
        },
        geometry=[bowtie, valid_poly, empty_poly],
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def duplicate_geometry_gdf():
    """Create a GeoDataFrame with duplicate geometries."""
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Original", "Duplicate", "Different"],
            "value": [1, 2, 3],
        },
        geometry=[poly, poly, Polygon([(5, 5), (6, 5), (6, 6), (5, 6)])],
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def no_crs_gdf():
    """Create a GeoDataFrame without CRS."""
    points = [Point(0, 0), Point(1, 1)]
    gdf = gpd.GeoDataFrame(
        {"label": ["A", "B"]},
        geometry=points,
    )
    return gdf


@pytest.fixture
def nulls_gdf():
    """Create a GeoDataFrame with null attributes."""
    polys = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
    ]
    gdf = gpd.GeoDataFrame(
        {
            "name": ["A", None, "C"],
            "value": [1.0, 2.0, None],
            "category": [None, "B", None],
        },
        geometry=polys,
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def data_dir():
    """Return path to the test data directory."""
    return Path(__file__).parent.parent.parent / "data"
