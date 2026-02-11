# Changelog

All notable changes to GeoQA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-11

### Added

- **Core profiling**: `geoqa.profile()` one-liner for dataset analysis
- **GeoProfile class**: Complete dataset profiling with quality scoring
- **Geometry checks**: Validity, empty, null, duplicate, mixed-type detection
- **Attribute profiling**: Data types, null analysis, statistics, top values
- **Spatial analysis**: CRS info, bounds, area/length/perimeter statistics
- **Interactive maps**: Folium-based visualization with quality highlighting
- **HTML reports**: Self-contained quality reports with Jinja2 templates
- **CLI interface**: `geoqa profile`, `geoqa report`, `geoqa check`, `geoqa show`
- **Rich output**: Beautiful terminal output with tables and colors
- **Quality scoring**: Weighted 0-100 score based on multiple criteria
- **Format support**: All Fiona/GDAL-supported vector formats
- **Auto-fix**: `GeometryChecker.fix_invalid()` for geometry repair
- **Comprehensive docs**: README, CONTRIBUTING, API docs, example notebooks
- **Test suite**: pytest-based tests for all modules
