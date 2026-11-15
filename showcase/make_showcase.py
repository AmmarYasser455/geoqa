"""Build the GeoQA showcase: is Natural Earth's Africa country layer clean?

Run from the repository root, offline:

    python showcase/make_showcase.py

Reads ``showcase/data/africa_countries_ne110m.geojson`` (real Natural Earth data),
runs GeoQA's geometry and topology checks on it and writes ``map.geojson``,
``map.png`` and ``index.html`` next to this script.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:  # allow running without installing the package
    sys.path.insert(0, str(ROOT))

import geoqa  # noqa: E402
from geoqa.geometry import GeometryChecker, TopologyChecker  # noqa: E402

DATA_FILE = HERE / "data" / "africa_countries_ne110m.geojson"
TITLE = "Is Natural Earth's Africa country layer ready to publish as GeoJSON?"
CREDIT = "Data: Natural Earth (public domain), 1:110m admin-0 countries"
REPO_URL = "https://github.com/AmmarYasser455/geoqa"
AREA_CRS = "EPSG:6933"  # WGS 84 / NSIDC EASE-Grid 2.0 Global (equal-area, metres)
COORD_DECIMALS = 6  # RFC 7946 recommends 6 decimals (about 0.1 m)


def load_data(path: Path = DATA_FILE) -> gpd.GeoDataFrame:
    """Read the committed Natural Earth extract; the CRS must be EPSG:4326."""
    gdf = gpd.read_file(path, driver="GeoJSON", encoding="utf-8")
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        raise ValueError(f"Expected EPSG:4326 input, got {gdf.crs}")
    return gdf.reset_index(drop=True)


def analyse(gdf: gpd.GeoDataFrame):
    """Run GeoQA on *gdf*. Returns (annotated GeoDataFrame, summary dict)."""
    prof = geoqa.profile(gdf, name="Africa countries (Natural Earth 1:110m)")
    geo = GeometryChecker(gdf).check_all()
    topo = TopologyChecker(gdf).check_all()

    out = gdf[["name", "iso_a3", "pop_est", "geometry"]].copy()
    # Areas in an equal-area projected CRS (metres), never in degrees.
    out["area_km2"] = (gdf.to_crs(AREA_CRS).area / 1e6).round(0).astype(int)
    out["vertices"] = [int(shapely.get_num_coordinates(g)) for g in gdf.geometry]
    bad_ring = set(topo["bad_ring_indices"])
    precise = set(topo["excessive_precision_indices"])
    overlap = {i for pair in topo["self_overlap_pairs"] for i in pair}
    invalid = set(geo["invalid_indices"])
    out["clockwise_exterior_in_source"] = [i in bad_ring for i in range(len(out))]
    out["over_8_decimals_in_source"] = [i in precise for i in range(len(out))]
    out["overlaps_neighbour"] = [i in overlap for i in range(len(out))]
    out["invalid_geometry"] = [i in invalid for i in range(len(out))]

    egypt = out[out["iso_a3"] == "EGY"].iloc[0]
    n = len(out)
    summary = {
        "features": n,
        "quality_score": round(float(prof.quality_score), 1),
        "invalid": geo["invalid_count"],
        "empty": geo["empty_count"],
        "duplicates": geo["duplicate_count"],
        "overlapping_pairs": topo["self_overlap_count"],
        "slivers": topo["sliver_count"],
        "clockwise_exterior": topo["bad_ring_count"],
        "over_8_decimals": topo["excessive_precision_count"],
        "total_vertices": geo["total_vertices"],
        "egypt_area_km2": int(egypt["area_km2"]),
        "egypt_vertices": int(egypt["vertices"]),
        "geometry_types": geo["geometry_types"],
        "crs": str(gdf.crs),
        "area_crs": AREA_CRS,
    }
    return out, summary


def _round_coords(geom):
    return shapely.transform(geom, lambda c: np.round(c, COORD_DECIMALS))


def _rewind(geom):
    """Exterior rings counter-clockwise, holes clockwise (RFC 7946 section 3.1.6)."""
    if isinstance(geom, Polygon):
        return orient(geom, sign=1.0)
    if isinstance(geom, MultiPolygon):
        return MultiPolygon([orient(p, sign=1.0) for p in geom.geoms])
    return geom


def to_rfc7946(result: gpd.GeoDataFrame) -> dict:
    """Return a RFC 7946 FeatureCollection (lon/lat, CCW exteriors, 6 decimals)."""
    result = result.to_crs("EPSG:4326")
    features = []
    for _, row in result.iterrows():
        geom = _rewind(_round_coords(row.geometry))
        props = {
            k: (v.item() if hasattr(v, "item") else v) for k, v in row.drop("geometry").items()
        }
        features.append(
            {"type": "Feature", "properties": props, "geometry": shapely.geometry.mapping(geom)}
        )
    return {"type": "FeatureCollection", "features": features}


def write_geojson(result: gpd.GeoDataFrame, path: Path) -> None:
    text = json.dumps(to_rfc7946(result), indent=1, ensure_ascii=False, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def write_png(result: gpd.GeoDataFrame, summary: dict, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    fig, ax = plt.subplots(figsize=(9, 9), dpi=150)
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
    plot = result.assign(area_plot=result["area_km2"].clip(lower=1))
    plot.plot(
        column="area_plot",
        ax=ax,
        cmap="YlGnBu",
        norm=LogNorm(vmin=1e3, vmax=3e6),
        edgecolor="#333333",
        linewidth=0.5,
        legend=True,
        legend_kwds={"label": "Area (km², equal-area EPSG:6933, log scale)", "shrink": 0.6},
    )
    egy = result[result["iso_a3"] == "EGY"]
    egy.boundary.plot(ax=ax, color="#d62728", linewidth=2.0)
    c = egy.geometry.iloc[0].representative_point()
    ax.annotate(
        f"Egypt\n{summary['egypt_area_km2']:,} km²",
        (c.x, c.y),
        ha="center",
        fontsize=9,
        color="#d62728",
        weight="bold",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none", "pad": 1.5},
    )
    ax.set_title(
        f"Africa: {summary['features']} countries, "
        f"{summary['overlapping_pairs']} overlaps, {summary['invalid']} invalid geometries",
        fontsize=13,
    )
    fig.suptitle(TITLE, fontsize=11, y=0.975)
    ax.set_xlabel("Longitude (°E), EPSG:4326, north up")
    ax.set_ylabel("Latitude (°N)")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.text(
        0.01,
        0.01,
        f"{summary['clockwise_exterior']}/{summary['features']} exterior rings are "
        "clockwise in the source\n(rewound to counter-clockwise for GeoJSON)",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )
    fig.text(0.99, 0.01, CREDIT, ha="right", va="bottom", fontsize=7, color="#444444")
    fig.savefig(path, dpi=150)
    plt.close(fig)


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  body { margin: 0; font-family: system-ui, sans-serif; }
  header { padding: 8px 14px; background: #f6f8fa; border-bottom: 1px solid #d0d7de; }
  h1 { font-size: 1.1rem; margin: 0 0 4px; }
  p { margin: 0; font-size: 0.85rem; line-height: 1.35; }
  #map { height: calc(100vh - 92px); }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <p>GeoQA checked the 51 African countries of the Natural Earth 1:110m layer: validity, duplicates, overlaps, ring order and coordinate precision.</p>
  <p>Click a country for its check results. Served by <a href="__REPO__">GeoQA</a>. Open this page through a web server (python -m http.server) so the GeoJSON can load.</p>
</header>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var map = L.map('map');
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Data: Natural Earth (public domain)'
  }).addTo(map);
  function color(a) {
    return a > 1000000 ? '#08306b' : a > 500000 ? '#2171b5' : a > 200000 ? '#6baed6'
         : a > 50000 ? '#c6dbef' : '#f7fbff';
  }
  function popup(p) {
    var rows = ['name', 'iso_a3', 'pop_est', 'area_km2', 'vertices',
                'clockwise_exterior_in_source', 'over_8_decimals_in_source',
                'overlaps_neighbour', 'invalid_geometry'];
    return '<table>' + rows.map(function (k) {
      return '<tr><td><b>' + k + '</b></td><td>' + p[k] + '</td></tr>';
    }).join('') + '</table>';
  }
  fetch('map.geojson').then(function (r) { return r.json(); }).then(function (data) {
    var layer = L.geoJSON(data, {
      style: function (f) {
        var egy = f.properties.iso_a3 === 'EGY';
        return { color: egy ? '#d62728' : '#333', weight: egy ? 3 : 1,
                 fillColor: color(f.properties.area_km2), fillOpacity: 0.7 };
      },
      onEachFeature: function (f, l) { l.bindPopup(popup(f.properties)); }
    }).addTo(map);
    map.fitBounds(layer.getBounds());
  });
</script>
</body>
</html>
"""


def write_html(path: Path) -> None:
    html = HTML.replace("__TITLE__", TITLE).replace("__REPO__", REPO_URL)
    path.write_text(html, encoding="utf-8")


def main(out_dir: Optional[Path] = None, data_path: Path = DATA_FILE, png: bool = True) -> dict:
    """Build all outputs into *out_dir* (default: this directory).

    ``png=False`` skips the matplotlib rendering of map.png.
    """
    out_dir = Path(out_dir) if out_dir is not None else HERE
    out_dir.mkdir(parents=True, exist_ok=True)
    gdf = load_data(data_path)
    result, summary = analyse(gdf)
    write_geojson(result, out_dir / "map.geojson")
    if png:
        write_png(result, summary, out_dir / "map.png")
    write_html(out_dir / "index.html")
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
