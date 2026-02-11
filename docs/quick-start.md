# Quick Start

## Profile a Shapefile

```python
import geoqa

# One-liner dataset profiling
profile = geoqa.profile("path/to/data.shp")

# View summary in terminal
profile.summary()
```

## View Quality Score

```python
print(f"Quality Score: {profile.quality_score}/100")
```

## Run Quality Checks

```python
checks = profile.quality_checks()
print(checks)
```

## Interactive Map

```python
# Show map with quality highlighting
m = profile.show_map(highlight_issues=True)
m  # Displays in Jupyter notebook
```

## HTML Report

```python
profile.to_html("report.html")
```

## Attribute Statistics

```python
# All columns
stats = profile.attribute_stats()
print(stats)

# Single column
stats = profile.attribute_stats("building_type")
```

## Geometry Statistics

```python
geom_stats = profile.geometry_stats()
print(geom_stats)
```

## CLI Usage

```bash
# Profile
geoqa profile data.shp

# Report
geoqa report data.shp -o report.html

# Quality checks
geoqa check data.geojson

# Interactive map
geoqa show data.gpkg -o map.html
```

## Using with GeoDataFrame

```python
import geopandas as gpd
import geoqa

gdf = gpd.read_file("data.geojson")
profile = geoqa.profile(gdf, name="My Dataset")
profile.summary()
```
