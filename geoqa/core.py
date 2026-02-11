"""
Core module: GeoProfile class — the central entry point for GeoQA.

Provides one-liner geospatial data profiling with quality assessment,
attribute statistics, and interactive visualization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import geopandas as gpd
import pandas as pd

from geoqa.attributes import AttributeProfiler
from geoqa.geometry import GeometryChecker
from geoqa.report import ReportGenerator
from geoqa.spatial import SpatialAnalyzer
from geoqa.visualization import MapVisualizer


def profile(
    data: Union[str, Path, gpd.GeoDataFrame],
    name: Optional[str] = None,
) -> "GeoProfile":
    """Profile a geospatial dataset with a single function call.

    This is the primary entry point for GeoQA. It loads the data, runs all
    quality checks, computes statistics, and returns a GeoProfile object.

    Args:
        data: Path to a vector file (Shapefile, GeoJSON, GeoPackage, etc.)
              or a GeoDataFrame.
        name: Optional display name for the dataset. If None, inferred from filename.

    Returns:
        A GeoProfile instance with all analysis results.

    Example:
        >>> import geoqa
        >>> p = geoqa.profile("buildings.shp")
        >>> p.summary()
        >>> p.show_map()
        >>> p.to_html("report.html")
    """
    return GeoProfile(data, name=name)


class GeoProfile:
    """Comprehensive geospatial data profile with quality assessment.

    GeoProfile loads, validates, analyzes, and visualizes geospatial vector data.
    It provides:
    - Geometry quality checks (validity, emptiness, duplicates)
    - Attribute profiling (types, nulls, unique values, statistics)
    - Spatial analysis (CRS info, extent, area/length stats)
    - Interactive map visualization (folium-based)
    - HTML report generation

    Args:
        data: Path to vector file or a GeoDataFrame.
        name: Optional display name for the dataset.

    Example:
        >>> from geoqa import GeoProfile
        >>> gp = GeoProfile("roads.shp")
        >>> gp.summary()
        >>> gp.quality_score
        92.5
    """

    def __init__(
        self,
        data: Union[str, Path, gpd.GeoDataFrame],
        name: Optional[str] = None,
    ) -> None:
        # Load data
        if isinstance(data, gpd.GeoDataFrame):
            self._gdf = data.copy()
            self._source_path = None
            self._name = name or "GeoDataFrame"
        else:
            self._source_path = Path(data)
            if not self._source_path.exists():
                raise FileNotFoundError(f"File not found: {self._source_path}")
            self._gdf = gpd.read_file(str(self._source_path))
            self._name = name or self._source_path.stem

        # Initialize analyzers
        self._geometry_checker = GeometryChecker(self._gdf)
        self._attribute_profiler = AttributeProfiler(self._gdf)
        self._spatial_analyzer = SpatialAnalyzer(self._gdf)
        self._map_visualizer = MapVisualizer(self._gdf, name=self._name)
        self._report_generator = ReportGenerator(self)

        # Run analysis
        self._geometry_results = self._geometry_checker.check_all()
        self._attribute_results = self._attribute_profiler.profile_all()
        self._spatial_results = self._spatial_analyzer.analyze()

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Dataset display name."""
        return self._name

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """The underlying GeoDataFrame."""
        return self._gdf

    @property
    def feature_count(self) -> int:
        """Number of features (rows) in the dataset."""
        return len(self._gdf)

    @property
    def column_count(self) -> int:
        """Number of attribute columns (excluding geometry)."""
        return len(self._gdf.columns) - 1  # subtract geometry column

    @property
    def geometry_type(self) -> str:
        """Dominant geometry type in the dataset."""
        return self._spatial_results.get("geometry_type", "Unknown")

    @property
    def crs(self) -> Optional[str]:
        """Coordinate Reference System as string."""
        if self._gdf.crs is not None:
            return str(self._gdf.crs)
        return None

    @property
    def bounds(self) -> dict:
        """Dataset spatial extent as dict with minx, miny, maxx, maxy."""
        return self._spatial_results.get("bounds", {})

    @property
    def quality_score(self) -> float:
        """Overall data quality score (0-100).

        Computed from:
        - Geometry validity (40% weight)
        - Attribute completeness (30% weight)
        - CRS presence (15% weight)
        - No empty geometries (15% weight)
        """
        return self._compute_quality_score()

    @property
    def geometry_results(self) -> dict:
        """Detailed geometry check results."""
        return self._geometry_results

    @property
    def attribute_results(self) -> dict:
        """Detailed attribute profiling results."""
        return self._attribute_results

    @property
    def spatial_results(self) -> dict:
        """Detailed spatial analysis results."""
        return self._spatial_results

    # ── Core Methods ────────────────────────────────────────────────────

    def summary(self, print_output: bool = True) -> dict:
        """Generate a concise summary of the dataset profile.

        Args:
            print_output: If True, prints a formatted summary to stdout.

        Returns:
            Dictionary containing the summary data.
        """
        summary_data = {
            "name": self._name,
            "source": str(self._source_path) if self._source_path else "GeoDataFrame",
            "features": self.feature_count,
            "columns": self.column_count,
            "geometry_type": self.geometry_type,
            "crs": self.crs,
            "bounds": self.bounds,
            "quality_score": round(self.quality_score, 1),
            "geometry_checks": {
                "valid": self._geometry_results.get("valid_count", 0),
                "invalid": self._geometry_results.get("invalid_count", 0),
                "empty": self._geometry_results.get("empty_count", 0),
                "duplicates": self._geometry_results.get("duplicate_count", 0),
            },
            "attribute_completeness": self._attribute_results.get("completeness", {}),
        }

        if print_output:
            self._print_summary(summary_data)

        return summary_data

    def show_map(
        self,
        style: Optional[dict] = None,
        highlight_issues: bool = True,
        width: str = "100%",
        height: str = "600px",
    ):
        """Display an interactive folium map of the dataset.

        Args:
            style: Optional style dictionary for features.
            highlight_issues: If True, highlights invalid/empty geometries in red.
            width: Map width (CSS units).
            height: Map height (CSS units).

        Returns:
            A folium.Map object.
        """
        issue_indices = set()
        if highlight_issues:
            issue_indices = set(self._geometry_results.get("invalid_indices", []))
            issue_indices.update(self._geometry_results.get("empty_indices", []))

        return self._map_visualizer.create_map(
            style=style,
            issue_indices=issue_indices,
            width=width,
            height=height,
        )

    def to_html(self, output_path: Union[str, Path] = "geoqa_report.html") -> Path:
        """Generate and save a comprehensive HTML quality report.

        Args:
            output_path: Path for the output HTML file.

        Returns:
            Path to the generated report file.
        """
        return self._report_generator.generate(output_path)

    def quality_checks(self) -> pd.DataFrame:
        """Return a DataFrame summarizing all quality check results.

        Returns:
            DataFrame with columns: Check, Status, Count, Severity, Details.
        """
        checks = []

        # Geometry validity
        invalid = self._geometry_results.get("invalid_count", 0)
        checks.append({
            "Check": "Geometry Validity",
            "Status": "PASS" if invalid == 0 else "FAIL",
            "Count": invalid,
            "Severity": "High" if invalid > 0 else "None",
            "Details": f"{invalid} invalid geometries found"
            if invalid > 0
            else "All geometries valid",
        })

        # Empty geometries
        empty = self._geometry_results.get("empty_count", 0)
        checks.append({
            "Check": "Empty Geometries",
            "Status": "PASS" if empty == 0 else "WARN",
            "Count": empty,
            "Severity": "Medium" if empty > 0 else "None",
            "Details": f"{empty} empty geometries found"
            if empty > 0
            else "No empty geometries",
        })

        # Duplicate geometries
        dups = self._geometry_results.get("duplicate_count", 0)
        checks.append({
            "Check": "Duplicate Geometries",
            "Status": "PASS" if dups == 0 else "WARN",
            "Count": dups,
            "Severity": "Medium" if dups > 0 else "None",
            "Details": f"{dups} duplicate geometries found"
            if dups > 0
            else "No duplicate geometries",
        })

        # CRS defined
        has_crs = self.crs is not None
        checks.append({
            "Check": "CRS Defined",
            "Status": "PASS" if has_crs else "FAIL",
            "Count": 1 if has_crs else 0,
            "Severity": "High" if not has_crs else "None",
            "Details": f"CRS: {self.crs}" if has_crs else "No CRS defined",
        })

        # Null attributes
        nulls = self._attribute_results.get("total_nulls", 0)
        total_cells = self.feature_count * self.column_count if self.column_count > 0 else 1
        null_pct = (nulls / total_cells) * 100 if total_cells > 0 else 0
        severity = "None"
        if null_pct > 20:
            severity = "High"
        elif null_pct > 5:
            severity = "Medium"
        elif null_pct > 0:
            severity = "Low"

        checks.append({
            "Check": "Attribute Completeness",
            "Status": "PASS" if null_pct < 5 else ("WARN" if null_pct < 20 else "FAIL"),
            "Count": nulls,
            "Severity": severity,
            "Details": f"{nulls} null values ({null_pct:.1f}% of all cells)",
        })

        # Mixed geometry types
        mixed = self._geometry_results.get("mixed_types", False)
        checks.append({
            "Check": "Homogeneous Geometry Types",
            "Status": "PASS" if not mixed else "WARN",
            "Count": len(self._geometry_results.get("geometry_types", {})),
            "Severity": "Low" if mixed else "None",
            "Details": "Mixed geometry types detected" if mixed else "Single geometry type",
        })

        return pd.DataFrame(checks)

    def attribute_stats(self, column: Optional[str] = None) -> pd.DataFrame:
        """Get detailed statistics for attribute columns.

        Args:
            column: If specified, return stats for a single column.
                    Otherwise, returns stats for all columns.

        Returns:
            DataFrame with attribute statistics.
        """
        stats = self._attribute_results.get("column_stats", {})

        if column is not None:
            if column in stats:
                return pd.DataFrame([stats[column]])
            raise ValueError(f"Column '{column}' not found. Available: {list(stats.keys())}")

        if not stats:
            return pd.DataFrame()

        return pd.DataFrame(stats).T

    def geometry_stats(self) -> pd.DataFrame:
        """Get geometry-level statistics (area, length, centroid, etc.).

        Returns:
            DataFrame with geometry statistics.
        """
        return self._spatial_analyzer.geometry_stats()

    # ── Private Methods ─────────────────────────────────────────────────

    def _compute_quality_score(self) -> float:
        """Compute overall quality score (0-100)."""
        score = 0.0
        total = self.feature_count if self.feature_count > 0 else 1

        # Geometry validity: 40%
        valid = self._geometry_results.get("valid_count", 0)
        score += (valid / total) * 40

        # Attribute completeness: 30%
        total_cells = self.feature_count * self.column_count if self.column_count > 0 else 1
        nulls = self._attribute_results.get("total_nulls", 0)
        completeness = 1 - (nulls / total_cells) if total_cells > 0 else 1
        score += completeness * 30

        # CRS present: 15%
        if self.crs is not None:
            score += 15

        # No empty geometries: 15%
        empty = self._geometry_results.get("empty_count", 0)
        score += ((total - empty) / total) * 15

        return min(score, 100.0)

    def _print_summary(self, data: dict) -> None:
        """Pretty-print the summary using rich formatting."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()

            # Header panel
            header = f"[bold cyan]GeoQA Profile:[/bold cyan] [bold]{data['name']}[/bold]"
            console.print(Panel(header, expand=False))

            # Overview table
            table = Table(title="Dataset Overview", show_header=True)
            table.add_column("Property", style="bold")
            table.add_column("Value")

            table.add_row("Source", str(data["source"]))
            table.add_row("Features", str(data["features"]))
            table.add_row("Columns", str(data["columns"]))
            table.add_row("Geometry Type", data["geometry_type"])
            table.add_row("CRS", str(data["crs"]))

            bounds = data.get("bounds", {})
            if bounds:
                bounds_str = (
                    f"({bounds.get('minx', 0):.4f}, {bounds.get('miny', 0):.4f}) → "
                    f"({bounds.get('maxx', 0):.4f}, {bounds.get('maxy', 0):.4f})"
                )
                table.add_row("Extent", bounds_str)

            # Quality score with color
            score = data["quality_score"]
            if score >= 80:
                score_style = "[bold green]"
            elif score >= 60:
                score_style = "[bold yellow]"
            else:
                score_style = "[bold red]"
            table.add_row("Quality Score", f"{score_style}{score}/100[/]")

            console.print(table)

            # Quality checks table
            checks = data["geometry_checks"]
            check_table = Table(title="Geometry Checks", show_header=True)
            check_table.add_column("Check", style="bold")
            check_table.add_column("Result", justify="right")

            for check_name, value in checks.items():
                label = check_name.replace("_", " ").title()
                if check_name in ("invalid", "empty", "duplicates") and value > 0:
                    check_table.add_row(label, f"[red]{value}[/red]")
                else:
                    check_table.add_row(label, f"[green]{value}[/green]")

            console.print(check_table)

        except ImportError:
            # Fallback without rich
            print(f"\n{'=' * 60}")
            print(f"  GeoQA Profile: {data['name']}")
            print(f"{'=' * 60}")
            print(f"  Source:         {data['source']}")
            print(f"  Features:       {data['features']}")
            print(f"  Columns:        {data['columns']}")
            print(f"  Geometry Type:  {data['geometry_type']}")
            print(f"  CRS:            {data['crs']}")
            print(f"  Quality Score:  {data['quality_score']}/100")
            print(f"{'=' * 60}")
            checks = data["geometry_checks"]
            for k, v in checks.items():
                print(f"  {k.replace('_', ' ').title()}: {v}")
            print(f"{'=' * 60}\n")

    def __repr__(self) -> str:
        return (
            f"GeoProfile(name='{self._name}', features={self.feature_count}, "
            f"quality={self.quality_score:.1f}/100)"
        )

    def __str__(self) -> str:
        return (
            f"GeoQA Profile: {self._name}\n"
            f"  Features: {self.feature_count}, Columns: {self.column_count}\n"
            f"  Geometry: {self.geometry_type}, CRS: {self.crs}\n"
            f"  Quality Score: {self.quality_score:.1f}/100"
        )
