"""Tests for the charts module."""

import base64

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use("Agg")

from geoqa.charts import (
    _fig_to_base64,
    _fig_to_html_img,
    attribute_completeness_bar,
    checks_summary_bar,
    distribution_histogram,
    generate_all_charts,
    geometry_type_pie,
    null_heatmap,
    quality_gauge,
)
from geoqa.core import GeoProfile


class TestQualityGauge:
    def test_returns_figure(self):
        fig = quality_gauge(85.0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_low_score(self):
        fig = quality_gauge(25.0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_perfect_score(self):
        fig = quality_gauge(100.0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_zero_score(self):
        fig = quality_gauge(0.0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestGeometryTypePie:
    def test_single_type(self):
        fig = geometry_type_pie({"Polygon": 100})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_multiple_types(self):
        fig = geometry_type_pie({"Polygon": 50, "MultiPolygon": 30, "Point": 20})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty_dict(self):
        fig = geometry_type_pie({})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestAttributeCompletenessBar:
    def test_full_completeness(self):
        fig = attribute_completeness_bar({"col_a": 100.0, "col_b": 100.0})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_mixed_completeness(self):
        fig = attribute_completeness_bar({"col_a": 100.0, "col_b": 45.0, "col_c": 80.0})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty(self):
        fig = attribute_completeness_bar({})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_long_names(self):
        fig = attribute_completeness_bar({"a_very_long_column_name_that_exceeds_limit": 90.0})
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestDistributionHistogram:
    def test_normal_data(self):
        data = np.random.normal(0, 1, 1000)
        fig = distribution_histogram(data, label="Test")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty_data(self):
        fig = distribution_histogram([], label="Empty")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_with_units(self):
        fig = distribution_histogram([1, 2, 3, 4, 5], label="Area", units="m²")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestNullHeatmap:
    def test_with_nulls(self):
        fig = null_heatmap({"col_a": 10, "col_b": 50}, total_rows=100)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_no_nulls(self):
        fig = null_heatmap({"col_a": 0, "col_b": 0}, total_rows=100)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty(self):
        fig = null_heatmap({}, total_rows=0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestChecksSummaryBar:
    def test_mixed_checks(self):
        checks = [
            {"Check": "Validity", "Status": "PASS", "Count": 0, "Severity": "None", "Details": "All valid"},
            {"Check": "Empty", "Status": "FAIL", "Count": 5, "Severity": "High", "Details": "5 empty"},
            {"Check": "CRS", "Status": "WARN", "Count": 1, "Severity": "Medium", "Details": "Warning"},
        ]
        fig = checks_summary_bar(checks)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty(self):
        fig = checks_summary_bar([])
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestHelpers:
    def test_fig_to_base64(self):
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.plot([1, 2, 3])
        b64 = _fig_to_base64(fig)
        assert isinstance(b64, str)
        assert len(b64) > 100
        # Verify it's valid base64
        base64.b64decode(b64)

    def test_fig_to_html_img(self):
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.plot([1, 2, 3])
        html = _fig_to_html_img(fig)
        assert html.startswith("<img ")
        assert "data:image/png;base64," in html


class TestGenerateAllCharts:
    def test_with_polygon_profile(self, sample_polygons_gdf):
        p = GeoProfile(sample_polygons_gdf, name="Test")
        charts = generate_all_charts(p)
        assert isinstance(charts, dict)
        assert "quality_gauge" in charts
        assert "checks_summary" in charts
        # Should have base64 strings
        for key, val in charts.items():
            assert isinstance(val, str)
            assert len(val) > 50

    def test_with_line_profile(self, sample_lines_gdf):
        p = GeoProfile(sample_lines_gdf, name="Lines")
        charts = generate_all_charts(p)
        assert "quality_gauge" in charts

    def test_with_point_profile(self, sample_points_gdf):
        p = GeoProfile(sample_points_gdf, name="Points")
        charts = generate_all_charts(p)
        assert "quality_gauge" in charts
