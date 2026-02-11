<p align="center">
  <img src="https://raw.githubusercontent.com/AmmarYasser455/geoqa/main/docs/geoqa_logo.png" alt="GeoQA Logo" width="200">
</p>

<h1 align="center">GeoQA</h1>

<p align="center">
  <strong>Geospatial Data Quality Assessment & Interactive Profiling</strong><br>
  <em>Profile any geodataset with a single line of code</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/geoqa/"><img src="https://img.shields.io/pypi/v/geoqa?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/geoqa/"><img src="https://img.shields.io/pypi/pyversions/geoqa?style=flat-square" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
  <a href="https://github.com/AmmarYasser455/geoqa/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/AmmarYasser455/geoqa/ci.yml?style=flat-square&label=CI" alt="CI"></a>
</p>

---

## What is GeoQA?

**GeoQA** is a Python package for **automated quality assessment and interactive profiling** of geospatial vector data. Think of it as [ydata-profiling](https://github.com/ydataai/ydata-profiling) (formerly pandas-profiling) but purpose-built for geodata.

- **Profile** any vector dataset (Shapefile, GeoJSON, GeoPackage, etc.) with one line of code
- **Validate** geometry quality — invalid, empty, duplicate, and mixed-type detection
- **Analyze** attribute completeness, statistics, and distributions
- **Visualize** data on interactive maps with quality-issue highlighting
- **Generate** self-contained HTML quality reports with charts and tables
- **Automate** QA/QC workflows via CLI or Python API

## Key Features

| Feature | Description |
|---|---|
| **One-liner profiling** | `geoqa.profile("data.shp")` — instant dataset overview |
| **Geometry validation** | OGC-compliant validity checks, empty/null detection, duplicate finding |
| **Attribute profiling** | Data types, null analysis, unique values, descriptive statistics |
| **Interactive maps** | Folium-based maps with issue highlighting and quality coloring |
| **HTML reports** | Self-contained quality reports with charts and tables |
| **CLI interface** | `geoqa profile data.shp` — terminal access to all features |
| **Auto-fix** | Repair invalid geometries with `profile.geometry_results` |
| **Spatial analysis** | CRS info, extent, area/length statistics, centroid computation |

## Installation

```bash
pip install geoqa
```

**From source (development):**

```bash
git clone https://github.com/AmmarYasser455/geoqa.git
cd geoqa
pip install -e ".[dev]"
```

**Requirements:** Python 3.9+ — depends on geopandas, shapely, folium, matplotlib, pandas, numpy, jinja2, click, and rich.

## Quick Start

### Python API

```python
import geoqa

# Profile a dataset
profile = geoqa.profile("buildings.shp")

# View summary
profile.summary()

# Interactive map with issue highlighting
profile.show_map()

# Quality check details
profile.quality_checks()

# Generate HTML report
profile.to_html("quality_report.html")

# Attribute and geometry statistics
profile.attribute_stats()
profile.geometry_stats()
```

### From a GeoDataFrame

```python
import geopandas as gpd
import geoqa

gdf = gpd.read_file("roads.geojson")
profile = geoqa.profile(gdf, name="City Roads")
profile.summary()
```

### CLI

```bash
geoqa profile data.shp                        # Profile a dataset
geoqa report data.shp --output report.html     # Generate HTML report
geoqa check data.geojson                       # Run quality checks only
geoqa show data.gpkg --output map.html         # Open interactive map
```

## Quality Score

GeoQA computes an overall quality score (0–100) based on:

| Component | Weight | Description |
|---|---|---|
| Geometry Validity | 40% | Percentage of valid geometries (OGC compliance) |
| Attribute Completeness | 30% | Percentage of non-null attribute values |
| CRS Defined | 15% | Whether a coordinate reference system is set |
| No Empty Geometries | 15% | Percentage of non-empty geometries |

## Quality Checks

| Check | Severity | Description |
|---|---|---|
| Geometry Validity | High | OGC Simple Features compliance |
| Empty Geometries | Medium | Geometries with no coordinates |
| Duplicate Geometries | Medium | Identical geometry pairs (WKB comparison) |
| CRS Defined | High | Coordinate reference system presence |
| Attribute Completeness | Varies | Null/missing value analysis |
| Mixed Geometry Types | Low | Multiple geometry types in one layer |

## Interactive Visualization

GeoQA creates interactive Folium maps with auto-reprojection to WGS84, quality highlighting (invalid in red, valid in blue), interactive tooltips, multiple basemaps, and layer controls.

```python
profile.show_map()

# Or use the visualization API directly
from geoqa.visualization import MapVisualizer
viz = MapVisualizer(profile.gdf, name="My Data")
quality_map = viz.create_quality_map(profile.geometry_results)
```

## HTML Reports

Generate comprehensive, self-contained HTML reports:

```python
profile.to_html("report.html")
```

Reports include quality score badges, dataset overview cards, quality check tables with pass/fail/warn indicators, spatial extent information, attribute completeness bars, numeric column statistics, and geometry type distributions.

## Supported Formats

All vector formats readable by GeoPandas/Fiona: Shapefile, GeoJSON, GeoPackage, KML, GML, CSV with geometry, File Geodatabase, and more via GDAL/OGR drivers.

## Architecture

```
geoqa/
├── core.py           # GeoProfile — main entry point
├── geometry.py       # Geometry validation & quality checks
├── attributes.py     # Attribute profiling & statistics
├── spatial.py        # CRS, extent, area/length analysis
├── visualization.py  # Folium-based interactive maps
├── report.py         # HTML report generation (Jinja2)
├── charts.py         # Matplotlib chart generation
├── cli.py            # Click-based CLI interface
└── utils.py          # Utility functions
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/AmmarYasser455/geoqa.git
cd geoqa
pip install -e ".[dev]"
pytest
black geoqa/ tests/
```

## Author

**Ammar Yasser Abdalazim**

- GitHub: [@AmmarYasser455](https://github.com/AmmarYasser455)

## License

[MIT License](LICENSE)

## Acknowledgments

GeoQA is inspired by the development methodology and open-source philosophy of [Dr. Qiusheng Wu](https://github.com/giswqs) and the [opengeos](https://github.com/opengeos) community. Key inspirations include [leafmap](https://github.com/opengeos/leafmap), [geemap](https://github.com/gee-community/geemap), and [ydata-profiling](https://github.com/ydataai/ydata-profiling).

## Citation

```bibtex
@software{geoqa2026,
  title   = {GeoQA: A Python Package for Geospatial Data Quality Assessment},
  author  = {Ammar Yasser Abdalazim},
  year    = {2026},
  url     = {https://github.com/AmmarYasser455/geoqa},
  license = {MIT}
}
```
