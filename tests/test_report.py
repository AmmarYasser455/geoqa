"""Tests for the HTML report generation module."""

from pathlib import Path

import pytest

from geoqa.core import GeoProfile
from geoqa.report import ReportGenerator


class TestReportGenerator:
    """Tests for ReportGenerator."""

    def test_generate_report(self, sample_polygons_gdf, tmp_path):
        """Test basic report generation."""
        gp = GeoProfile(sample_polygons_gdf, name="Test Report")
        output = tmp_path / "report.html"
        result = gp.to_html(output)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_report_content(self, sample_polygons_gdf, tmp_path):
        """Test report contains expected content."""
        gp = GeoProfile(sample_polygons_gdf, name="Test Report")
        output = tmp_path / "report.html"
        gp.to_html(output)
        content = output.read_text(encoding="utf-8")
        assert "GeoQA" in content
        assert "Test Report" in content
        assert "Quality" in content
        assert "Polygon" in content

    def test_report_with_nulls(self, nulls_gdf, tmp_path):
        """Test report generation with null data."""
        gp = GeoProfile(nulls_gdf, name="Nulls Test")
        output = tmp_path / "report_nulls.html"
        result = gp.to_html(output)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "Nulls Test" in content

    def test_report_subdirectory(self, sample_polygons_gdf, tmp_path):
        """Test report creation in subdirectory."""
        output = tmp_path / "subdir" / "report.html"
        gp = GeoProfile(sample_polygons_gdf, name="Sub Test")
        result = gp.to_html(output)
        assert result.exists()

    def test_report_line_data(self, sample_lines_gdf, tmp_path):
        """Test report for line geometry data."""
        gp = GeoProfile(sample_lines_gdf, name="Lines")
        output = tmp_path / "lines_report.html"
        result = gp.to_html(output)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "LineString" in content

    def test_report_quality_score_display(self, sample_polygons_gdf, tmp_path):
        """Test quality score is displayed in report."""
        gp = GeoProfile(sample_polygons_gdf, name="Score Test")
        output = tmp_path / "score_report.html"
        gp.to_html(output)
        content = output.read_text(encoding="utf-8")
        assert "/100" in content

    def test_report_xss_prevention(self, sample_polygons_gdf, tmp_path):
        """Test that HTML/script in dataset name is escaped, not injected."""
        xss_name = '<script>alert("xss")</script>'
        gp = GeoProfile(sample_polygons_gdf, name=xss_name)
        output = tmp_path / "xss_report.html"
        gp.to_html(output)
        content = output.read_text(encoding="utf-8")
        # The raw <script> tag must NOT appear in the output
        assert "<script>alert" not in content
        # The escaped version should be present instead
        assert "&lt;script&gt;" in content

    def test_report_special_chars_in_name(self, sample_polygons_gdf, tmp_path):
        """Test that special characters in dataset name don't break the report."""
        gp = GeoProfile(sample_polygons_gdf, name='Test & "Quotes" <Angles>')
        output = tmp_path / "special_report.html"
        result = gp.to_html(output)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        # Ampersand and angle brackets should be escaped
        assert "&amp;" in content
        assert "&lt;Angles&gt;" in content
