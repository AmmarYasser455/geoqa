# Installation

## Requirements

- Python 3.9 or later
- pip or conda package manager

## Install from PyPI

```bash
pip install geoqa
```

## Install from source

```bash
git clone https://github.com/geoqa/geoqa.git
cd geoqa
pip install -e .
```

## Development installation

```bash
pip install -e ".[dev]"
```

## Dependencies

GeoQA automatically installs the following dependencies:

| Package | Purpose |
|---------|---------|
| geopandas | Geospatial data manipulation |
| shapely | Geometry operations |
| folium | Interactive maps |
| matplotlib | Static charts |
| pandas | Data analysis |
| numpy | Numeric computation |
| jinja2 | Report templates |
| click | CLI framework |
| rich | Terminal formatting |
| branca | Map coloring |

## Verify Installation

```python
import geoqa
print(geoqa.__version__)
```
