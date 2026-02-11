<p align="center">
  <img src="https://raw.githubusercontent.com/AmmarYasser455/geoqa/main/docs/geoqa_logo.png" alt="GeoQA Logo" width="200">
</p>

<h1 align="center">GeoQA</h1>

<p align="center">
  <strong>Geospatial Data Quality Assessment & Interactive Profiling</strong>
</p>

<p align="center">
  <em>Profile any geodataset with a single line of code</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/geoqa/"><img src="https://img.shields.io/pypi/v/geoqa.svg?style=flat-square" alt="PyPI"></a>
  <a href="https://pypi.org/project/geoqa/"><img src="https://img.shields.io/pypi/pyversions/geoqa.svg?style=flat-square" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://github.com/AmmarYasser455/geoqa/actions"><img src="https://img.shields.io/github/actions/workflow/status/AmmarYasser455/geoqa/ci.yml?style=flat-square" alt="CI"></a>
</p>

---

## 🌍 What is GeoQA?

**GeoQA** is a Python package for **automated quality assessment and interactive profiling** of geospatial vector data. Think of it as [ydata-profiling](https://github.com/ydataai/ydata-profiling) (formerly pandas-profiling) but purpose-built for geodata.

GeoQA lets you:

- **Profile** any vector dataset (Shapefile, GeoJSON, GeoPackage, etc.) with one line of code
- **Validate** geometry quality (invalid, empty, duplicate, mixed types)
- **Analyze** attribute completeness, statistics, and distributions
- **Visualize** data on interactive maps with quality issue highlighting
- **Generate** self-contained HTML quality reports
- **Automate** QA/QC workflows via CLI or Python API

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **One-liner Profiling** | `geoqa.profile("data.shp")` — instant dataset overview |
| ✅ **Geometry Validation** | OGC-compliant validity checks, empty/null detection, duplicate finding |
| 📊 **Attribute Profiling** | Data types, null analysis, unique values, descriptive statistics |
| 🗺️ **Interactive Maps** | Folium-based maps with issue highlighting and quality coloring |
| 📋 **HTML Reports** | Beautiful, self-contained quality reports with charts and tables |
| ⚡ **CLI Interface** | `geoqa profile data.shp` — terminal access to all features |
| 🔧 **Auto-fix** | Repair invalid geometries with `profile.geometry_results` |
| 📐 **Spatial Analysis** | CRS info, extent, area/length statistics, centroid computation |

## 📦 Installation

### pip

```bash
pip install geoqa
```

### From source (development)

```bash
git clone https://github.com/AmmarYasser455/geoqa.git
cd geoqa
pip install -e ".[dev]"
```

### Dependencies

GeoQA requires Python 3.9+ and depends on:

- **geopandas** — Geospatial data manipulation
- **shapely** — Geometry operations and validation
- **folium** — Interactive map visualization
- **matplotlib** — Static charts
- **pandas / numpy** — Data analysis
- **jinja2** — Report template rendering
- **click** — CLI framework
- **rich** — Terminal formatting

## 🚀 Quick Start

### Python API

```python
import geoqa

# Profile a dataset with one line
profile = geoqa.profile("buildings.shp")

# View summary
profile.summary()
# Output:
# ╭──────────────────────────────────────────╮
# │  GeoQA Profile: buildings                │
# ╰──────────────────────────────────────────╯
# ┌─────────────────┬──────────────┐
# │ Property        │ Value        │
# ├─────────────────┼──────────────┤
# │ Features        │ 12,456       │
# │ Columns         │ 8            │
# │ Geometry Type   │ Polygon      │
# │ CRS             │ EPSG:4326    │
# │ Quality Score   │ 94.2/100     │
# └─────────────────┴──────────────┘

# Interactive map with issue highlighting
profile.show_map()

# Quality check details
checks = profile.quality_checks()
print(checks)

# Generate HTML report
profile.to_html("quality_report.html")

# Attribute statistics
profile.attribute_stats()

# Geometry measurements
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
# Profile a dataset
geoqa profile data.shp

# Generate HTML report
geoqa report data.shp --output report.html

# Run quality checks only
geoqa check data.geojson

# Show interactive map
geoqa show data.gpkg --output map.html
```

## 📊 Quality Score

GeoQA computes an overall quality score (0-100) based on:

| Component | Weight | Description |
|-----------|--------|-------------|
| Geometry Validity | 40% | Percentage of valid geometries (OGC compliance) |
| Attribute Completeness | 30% | Percentage of non-null attribute values |
| CRS Defined | 15% | Whether a coordinate reference system is set |
| No Empty Geometries | 15% | Percentage of non-empty geometries |

## 🗺️ Interactive Visualization

GeoQA creates interactive folium maps with:

- **Auto-reprojection** to WGS84 for web display
- **Quality highlighting** — invalid geometries in red, valid in blue
- **Interactive tooltips** with attribute data
- **Multiple basemaps** — OpenStreetMap, CartoDB Light/Dark
- **Layer controls** for toggling valid/issue features

```python
# Basic map
profile.show_map()

# Quality-colored map
from geoqa.visualization import MapVisualizer
viz = MapVisualizer(profile.gdf, name="My Data")
quality_map = viz.create_quality_map(profile.geometry_results)
```

## 📋 HTML Reports

Generate comprehensive, self-contained HTML reports:

```python
profile.to_html("report.html")
```

Reports include:
- Quality score badge with color coding
- Dataset overview cards (features, columns, geometry type, CRS)
- Quality checks table with pass/fail/warn indicators
- Spatial extent information
- Attribute completeness with visual progress bars
- Numeric column statistics
- Geometry type distribution

## 🧪 Quality Checks

| Check | Severity | Description |
|-------|----------|-------------|
| Geometry Validity | 🔴 High | OGC Simple Features compliance |
| Empty Geometries | 🟡 Medium | Geometries with no coordinates |
| Duplicate Geometries | 🟡 Medium | Identical geometry pairs (WKB comparison) |
| CRS Defined | 🔴 High | Coordinate reference system presence |
| Attribute Completeness | Varies | Null/missing value analysis |
| Mixed Geometry Types | 🟢 Low | Multiple geometry types in one layer |

## 📐 Supported Formats

GeoQA supports all vector formats readable by GeoPandas/Fiona:

- **Shapefile** (`.shp`)
- **GeoJSON** (`.geojson`, `.json`)
- **GeoPackage** (`.gpkg`)
- **KML** (`.kml`)
- **GML** (`.gml`)
- **CSV with geometry** (`.csv`)
- **File Geodatabase** (`.gdb`)
- And many more via GDAL/OGR drivers

## 🏗️ Architecture

```
geoqa/
├── core.py           # GeoProfile class — main entry point
├── geometry.py       # Geometry validation & quality checks
├── attributes.py     # Attribute profiling & statistics
├── spatial.py        # CRS, extent, area/length analysis
├── visualization.py  # Folium-based interactive maps
├── report.py         # HTML report generation (Jinja2)
├── cli.py            # Click-based CLI interface
└── utils.py          # Utility functions
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone the repository
git clone https://github.com/AmmarYasser455/geoqa.git
cd geoqa

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black geoqa/ tests/
isort geoqa/ tests/
```

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

GeoQA is inspired by the development methodology and open-source philosophy of [Dr. Qiusheng Wu](https://github.com/giswqs) and the [opengeos](https://github.com/opengeos) community. Key inspirations include:

- [leafmap](https://github.com/opengeos/leafmap) — One-liner philosophy for geospatial analysis
- [geemap](https://github.com/gee-community/geemap) — Interactive mapping patterns
- [ydata-profiling](https://github.com/ydataai/ydata-profiling) — Data profiling concept

## 📖 Citation

If you find GeoQA useful in your work, please consider citing:

```bibtex
@software{geoqa2026,
  title = {GeoQA: A Python Package for Geospatial Data Quality Assessment},
  year = {2026},
  url = {https://github.com/AmmarYasser455/geoqa},
  license = {MIT}
}
```

---

<p align="center">
  Made with ❤️ for the geospatial community
</p>
