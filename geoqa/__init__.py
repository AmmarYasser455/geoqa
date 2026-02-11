"""
GeoQA: A Python package for geospatial data quality assessment and interactive profiling.

GeoQA provides automated quality checks, statistical profiling, and interactive
visualization for geospatial vector data. It follows the "one-liner" philosophy:
profile any geodataset with a single function call.

Example:
    >>> import geoqa
    >>> profile = geoqa.profile("data.shp")
    >>> profile.summary()
    >>> profile.show_map()
    >>> profile.to_html("report.html")
"""

__version__ = "0.1.0"
__author__ = "GeoQA Contributors"

from geoqa.core import GeoProfile, profile
from geoqa.charts import generate_all_charts, quality_gauge
from geoqa.geometry import TopologyChecker

__all__ = [
    "GeoProfile",
    "profile",
    "generate_all_charts",
    "quality_gauge",
    "TopologyChecker",
    "__version__",
]
