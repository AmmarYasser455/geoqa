# GeoQA Documentation

Welcome to the **GeoQA** documentation — a Python package for geospatial data quality assessment and interactive profiling.

## Overview

GeoQA provides automated quality checks, statistical profiling, and interactive visualization for geospatial vector data. Profile any geodataset with a single function call.

## Features

- **One-liner profiling** — `geoqa.profile("data.shp")`
- **Geometry validation** — OGC-compliant validity checks
- **Attribute profiling** — Complete statistical analysis
- **Interactive maps** — Folium-based visualization
- **HTML reports** — Self-contained quality reports
- **CLI interface** — Terminal access to all features

## Quick Example

```python
import geoqa

profile = geoqa.profile("buildings.shp")
profile.summary()           # Print summary
profile.show_map()          # Interactive map
profile.to_html("report.html")  # HTML report
```

## Getting Started

- [Installation](installation.md)
- [Quick Start Guide](quick-start.md)
- [API Reference](api-reference.md)
