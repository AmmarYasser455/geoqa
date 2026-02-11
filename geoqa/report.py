"""
HTML report generation module.

Creates comprehensive, self-contained HTML quality reports
with embedded matplotlib charts, maps, and statistics tables.

Author: Ammar Yasser Abdalazim
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union

from jinja2 import Environment, select_autoescape

if TYPE_CHECKING:
    from geoqa.core import GeoProfile

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoQA Report: {{ name }}</title>
    <style>
        :root {
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), #7c3aed);
            color: white;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header .subtitle { opacity: 0.9; font-size: 1.1rem; }
        .header .logo { font-size: 2.5rem; margin-bottom: 0.5rem; }

        .score-badge {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 1rem;
        }
        .score-high { background: var(--success); color: white; }
        .score-medium { background: var(--warning); color: white; }
        .score-low { background: var(--danger); color: white; }

        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .grid-2col { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }
        .card h3 { color: var(--primary); margin-bottom: 0.75rem; font-size: 1rem; }
        .card .value { font-size: 2rem; font-weight: bold; }
        .card .label { color: var(--text-light); font-size: 0.85rem; }

        .section {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }
        .section h2 {
            color: var(--primary);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }
        .chart-container {
            text-align: center;
            padding: 1rem 0;
        }
        .chart-container img { max-width: 100%; height: auto; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: var(--bg);
            font-weight: 600;
            color: var(--text-light);
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }
        tr:hover td { background: #f1f5f9; }

        .status-pass { color: var(--success); font-weight: bold; }
        .status-fail { color: var(--danger); font-weight: bold; }
        .status-warn { color: var(--warning); font-weight: bold; }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .progress-high { background: var(--success); }
        .progress-medium { background: var(--warning); }
        .progress-low { background: var(--danger); }

        .footer {
            text-align: center;
            padding: 1.5rem;
            color: var(--text-light);
            font-size: 0.85rem;
        }

        .topology-pill {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .pill-ok { background: #dcfce7; color: var(--success); }
        .pill-issue { background: #fef2f2; color: var(--danger); }
        .pill-warn { background: #fefce8; color: var(--warning); }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🌍</div>
        <h1>GeoQA Quality Report</h1>
        <div class="subtitle">{{ name }}</div>
        {% if quality_score >= 80 %}
        <div class="score-badge score-high">{{ quality_score }}/100</div>
        {% elif quality_score >= 60 %}
        <div class="score-badge score-medium">{{ quality_score }}/100</div>
        {% else %}
        <div class="score-badge score-low">{{ quality_score }}/100</div>
        {% endif %}
    </div>

    <!-- Overview Cards -->
    <div class="grid">
        <div class="card">
            <h3>📊 Features</h3>
            <div class="value">{{ "{:,}".format(features) }}</div>
            <div class="label">Total features in dataset</div>
        </div>
        <div class="card">
            <h3>📋 Columns</h3>
            <div class="value">{{ columns }}</div>
            <div class="label">Attribute columns</div>
        </div>
        <div class="card">
            <h3>🔷 Geometry</h3>
            <div class="value">{{ geometry_type }}</div>
            <div class="label">Dominant geometry type</div>
        </div>
        <div class="card">
            <h3>🌐 CRS</h3>
            <div class="value" style="font-size:1rem;">{{ crs or 'Not Defined' }}</div>
            <div class="label">Coordinate Reference System</div>
        </div>
    </div>

    <!-- Charts Row: Quality Gauge + Geometry Types -->
    <div class="grid-2col">
        {% if charts.quality_gauge %}
        <div class="card">
            <h3>🎯 Quality Score</h3>
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.quality_gauge }}" alt="Quality gauge" />
            </div>
        </div>
        {% endif %}
        {% if charts.geometry_types %}
        <div class="card">
            <h3>🔷 Geometry Distribution</h3>
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.geometry_types }}" alt="Geometry types" />
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Quality Checks -->
    <div class="section">
        <h2>✅ Quality Checks</h2>
        {% if charts.checks_summary %}
        <div class="chart-container">
            <img src="data:image/png;base64,{{ charts.checks_summary }}" alt="Checks summary" />
        </div>
        {% endif %}
        <table>
            <thead>
                <tr>
                    <th>Check</th>
                    <th>Status</th>
                    <th>Count</th>
                    <th>Severity</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {% for check in quality_checks %}
                <tr>
                    <td><strong>{{ check.Check }}</strong></td>
                    <td>
                        {% if check.Status == 'PASS' %}
                        <span class="status-pass">✅ PASS</span>
                        {% elif check.Status == 'FAIL' %}
                        <span class="status-fail">❌ FAIL</span>
                        {% else %}
                        <span class="status-warn">⚠️ WARN</span>
                        {% endif %}
                    </td>
                    <td>{{ check.Count }}</td>
                    <td>{{ check.Severity }}</td>
                    <td>{{ check.Details }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Topology Checks (if available) -->
    {% if topology %}
    <div class="section">
        <h2>🔗 Topology Checks</h2>
        <table>
            <thead><tr><th>Check</th><th>Result</th><th>Details</th></tr></thead>
            <tbody>
                <tr>
                    <td><strong>Self-Overlapping Polygons</strong></td>
                    <td>
                        {% if topology.self_overlap_count is defined and topology.self_overlap_count == -1 %}
                        <span class="topology-pill pill-warn">SKIPPED</span>
                        {% elif topology.self_overlap_count is defined and topology.self_overlap_count == 0 %}
                        <span class="topology-pill pill-ok">OK</span>
                        {% elif topology.self_overlap_count is defined %}
                        <span class="topology-pill pill-issue">{{ topology.self_overlap_count }} overlaps</span>
                        {% endif %}
                    </td>
                    <td>{% if topology.self_overlap_count == -1 %}Dataset too large for pairwise check{% elif topology.self_overlap_count == 0 %}No overlapping polygons{% else %}{{ topology.self_overlap_count }} pairs of polygons overlap{% endif %}</td>
                </tr>
                <tr>
                    <td><strong>Ring Winding Order</strong></td>
                    <td>
                        {% if topology.bad_ring_count == 0 %}
                        <span class="topology-pill pill-ok">OK</span>
                        {% else %}
                        <span class="topology-pill pill-warn">{{ topology.bad_ring_count }} issues</span>
                        {% endif %}
                    </td>
                    <td>{% if topology.bad_ring_count == 0 %}All rings follow correct winding order{% else %}{{ topology.bad_ring_count }} features with incorrect ring direction{% endif %}</td>
                </tr>
                <tr>
                    <td><strong>Sliver Polygons</strong></td>
                    <td>
                        {% if topology.sliver_count == 0 %}
                        <span class="topology-pill pill-ok">OK</span>
                        {% else %}
                        <span class="topology-pill pill-warn">{{ topology.sliver_count }} slivers</span>
                        {% endif %}
                    </td>
                    <td>{% if topology.sliver_count == 0 %}No sliver polygons detected{% else %}{{ topology.sliver_count }} very thin/elongated polygons{% endif %}</td>
                </tr>
                <tr>
                    <td><strong>Coordinate Precision</strong></td>
                    <td>
                        {% if topology.excessive_precision_count == 0 %}
                        <span class="topology-pill pill-ok">OK</span>
                        {% else %}
                        <span class="topology-pill pill-warn">{{ topology.excessive_precision_count }} features</span>
                        {% endif %}
                    </td>
                    <td>{% if topology.excessive_precision_count == 0 %}Coordinate precision within normal range{% else %}{{ topology.excessive_precision_count }} features with excessive decimal precision{% endif %}</td>
                </tr>
            </tbody>
        </table>
    </div>
    {% endif %}

    <!-- Spatial Information -->
    <div class="section">
        <h2>📍 Spatial Information</h2>
        <table>
            <tbody>
                {% if bounds %}
                <tr><td><strong>Min X (West)</strong></td><td>{{ bounds.get('minx', 'N/A') }}</td></tr>
                <tr><td><strong>Min Y (South)</strong></td><td>{{ bounds.get('miny', 'N/A') }}</td></tr>
                <tr><td><strong>Max X (East)</strong></td><td>{{ bounds.get('maxx', 'N/A') }}</td></tr>
                <tr><td><strong>Max Y (North)</strong></td><td>{{ bounds.get('maxy', 'N/A') }}</td></tr>
                {% endif %}
                {% if crs_info %}
                <tr><td><strong>EPSG Code</strong></td><td>{{ crs_info.get('crs_epsg', 'N/A') }}</td></tr>
                <tr><td><strong>CRS Name</strong></td><td>{{ crs_info.get('crs_name', 'N/A') }}</td></tr>
                <tr><td><strong>Units</strong></td><td>{{ crs_info.get('crs_units', 'N/A') }}</td></tr>
                <tr><td><strong>Is Geographic</strong></td><td>{{ crs_info.get('crs_is_geographic', 'N/A') }}</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>

    <!-- Attribute Completeness -->
    <div class="section">
        <h2>📊 Attribute Completeness</h2>
        {% if charts.attribute_completeness %}
        <div class="chart-container">
            <img src="data:image/png;base64,{{ charts.attribute_completeness }}" alt="Attribute completeness" />
        </div>
        {% endif %}
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Completeness</th>
                    <th>Nulls</th>
                    <th>Unique</th>
                </tr>
            </thead>
            <tbody>
                {% for col_name, stats in column_stats.items() %}
                <tr>
                    <td><strong>{{ col_name }}</strong></td>
                    <td>{{ stats.get('dtype', 'N/A') }}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div class="progress-bar" style="width: 100px;">
                                {% set pct = completeness.get(col_name, 100) %}
                                <div class="progress-fill {% if pct >= 90 %}progress-high{% elif pct >= 70 %}progress-medium{% else %}progress-low{% endif %}"
                                     style="width: {{ pct }}%;"></div>
                            </div>
                            <span>{{ completeness.get(col_name, 100) }}%</span>
                        </div>
                    </td>
                    <td>{{ stats.get('null_count', 0) }}</td>
                    <td>{{ stats.get('unique_count', 0) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Null Heatmap -->
    {% if charts.null_heatmap %}
    <div class="section">
        <h2>🔍 Null Value Analysis</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,{{ charts.null_heatmap }}" alt="Null heatmap" />
        </div>
    </div>
    {% endif %}

    <!-- Numeric Statistics -->
    {% if numeric_stats %}
    <div class="section">
        <h2>🔢 Numeric Column Statistics</h2>
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Mean</th>
                    <th>Median</th>
                    <th>Std Dev</th>
                    <th>Min</th>
                    <th>Max</th>
                </tr>
            </thead>
            <tbody>
                {% for col_name, stats in numeric_stats.items() %}
                <tr>
                    <td><strong>{{ col_name }}</strong></td>
                    <td>{{ stats.get('mean', 'N/A') }}</td>
                    <td>{{ stats.get('median', 'N/A') }}</td>
                    <td>{{ stats.get('std', 'N/A') }}</td>
                    <td>{{ stats.get('min', 'N/A') }}</td>
                    <td>{{ stats.get('max', 'N/A') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <!-- Distribution Charts -->
    {% if charts.area_distribution or charts.length_distribution or charts.perimeter_distribution %}
    <div class="section">
        <h2>📈 Measurement Distributions</h2>
        <div class="grid-2col">
            {% if charts.area_distribution %}
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.area_distribution }}" alt="Area distribution" />
            </div>
            {% endif %}
            {% if charts.perimeter_distribution %}
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.perimeter_distribution }}" alt="Perimeter distribution" />
            </div>
            {% endif %}
            {% if charts.length_distribution %}
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.length_distribution }}" alt="Length distribution" />
            </div>
            {% endif %}
        </div>
    </div>
    {% endif %}

    <!-- Geometry Type Distribution Table -->
    {% if geometry_type_dist %}
    <div class="section">
        <h2>🔷 Geometry Type Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {% for gtype, count in geometry_type_dist.items() %}
                <tr>
                    <td><strong>{{ gtype }}</strong></td>
                    <td>{{ "{:,}".format(count) }}</td>
                    <td>{{ (count / features * 100) | round(1) }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <div class="footer">
        <p>Generated by <strong>GeoQA v{{ version }}</strong> — Geospatial Data Quality Assessment</p>
        <p>Report generated on {{ timestamp }}</p>
    </div>
</body>
</html>
"""


class ReportGenerator:
    """Generates comprehensive HTML quality reports with embedded charts.

    Creates self-contained HTML reports with:
    - Quality score gauge chart
    - Dataset summary cards
    - Quality check results (table + chart)
    - Topology check results
    - Spatial information
    - Attribute completeness (table + chart)
    - Null heatmap
    - Numeric statistics
    - Area/length distribution histograms
    - Geometry type distribution

    Args:
        profile: The GeoProfile instance to generate a report for.
    """

    def __init__(self, profile: "GeoProfile") -> None:
        self._profile = profile

    def generate(self, output_path: Union[str, Path] = "geoqa_report.html") -> Path:
        """Generate and save the HTML report.

        Args:
            output_path: Output file path.

        Returns:
            Path to the generated report.
        """
        from datetime import datetime

        import geoqa
        from geoqa.charts import generate_all_charts
        from geoqa.geometry import TopologyChecker

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate charts
        charts = generate_all_charts(self._profile)

        # Run topology checks
        topo_checker = TopologyChecker(self._profile.gdf)
        topology = topo_checker.check_all()

        # Collect data
        quality_checks = self._profile.quality_checks().to_dict("records")
        column_stats = self._profile.attribute_results.get("column_stats", {})
        completeness = self._profile.attribute_results.get("completeness", {})

        # Numeric stats
        numeric_stats = {}
        numeric_cols = self._profile.attribute_results.get("numeric_columns", [])
        for col in numeric_cols:
            if col in column_stats:
                numeric_stats[col] = column_stats[col]

        # Geometry type distribution
        geometry_type_dist = self._profile.geometry_results.get("geometry_types", {})

        # CRS info
        crs_info = {k: v for k, v in self._profile.spatial_results.items() if k.startswith("crs_")}

        # Render template with autoescape enabled to prevent XSS
        env = Environment(
            autoescape=select_autoescape(
                enabled_extensions=("html", "htm", "xml"),
                default_for_string=True,
            ),
        )
        template = env.from_string(REPORT_TEMPLATE)
        html = template.render(
            name=self._profile.name,
            features=self._profile.feature_count,
            columns=self._profile.column_count,
            geometry_type=self._profile.geometry_type,
            crs=self._profile.crs,
            quality_score=round(self._profile.quality_score, 1),
            bounds=self._profile.bounds,
            quality_checks=quality_checks,
            column_stats=column_stats,
            completeness=completeness,
            numeric_stats=numeric_stats,
            geometry_type_dist=geometry_type_dist,
            crs_info=crs_info,
            charts=charts,
            topology=topology,
            version=geoqa.__version__,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        output_path.write_text(html, encoding="utf-8")
        return output_path
