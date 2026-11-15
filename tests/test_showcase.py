"""The committed showcase must match what showcase/make_showcase.py produces."""

import importlib.util
import json
from pathlib import Path

import pytest
from shapely.geometry import shape

SHOWCASE = Path(__file__).resolve().parent.parent / "showcase"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    spec = importlib.util.spec_from_file_location("make_showcase", SHOWCASE / "make_showcase.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = tmp_path_factory.mktemp("showcase")
    try:
        import matplotlib  # noqa: F401

        has_mpl = True
    except ImportError:
        has_mpl = False
    summary = module.main(out, png=has_mpl)
    return out, summary


def test_geojson_matches_committed(built):
    out, _ = built
    fresh = json.loads((out / "map.geojson").read_text(encoding="utf-8"))
    committed = json.loads((SHOWCASE / "map.geojson").read_text(encoding="utf-8"))
    assert fresh == committed


def test_geojson_is_rfc7946_lonlat_ccw(built):
    out, _ = built
    data = json.loads((out / "map.geojson").read_text(encoding="utf-8"))
    assert len(data["features"]) == 51
    by_iso = {f["properties"]["iso_a3"]: f for f in data["features"]}
    egy = shape(by_iso["EGY"]["geometry"])
    # Egypt in lon/lat: a swapped axis would put it far outside these bounds.
    minx, miny, maxx, maxy = egy.bounds
    assert 24 < minx < 26 and 36 < maxx < 37
    assert 21 < miny < 23 and 31 < maxy < 32
    # About one million km2 in an equal-area CRS (degrees would give ~100).
    assert 950_000 < by_iso["EGY"]["properties"]["area_km2"] < 1_050_000
    for f in data["features"]:
        geom = shape(f["geometry"])
        for poly in getattr(geom, "geoms", [geom]):
            assert poly.exterior.is_ccw
            assert all(not ring.is_ccw for ring in poly.interiors)


def test_summary(built):
    _, summary = built
    assert summary["features"] == 51
    assert summary["invalid"] == 0
    assert summary["overlapping_pairs"] == 0
    assert summary["clockwise_exterior"] == 51


def test_png_is_produced(built):
    pytest.importorskip("matplotlib")
    out, _ = built
    png = out / "map.png"
    assert png.exists()
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_html_is_produced(built):
    out, _ = built
    assert "leaflet@1.9.4" in (out / "index.html").read_text(encoding="utf-8")


def test_notebook_executes_with_inline_map():
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("matplotlib")
    pytest.importorskip("ipykernel")
    nb = nbformat.read(SHOWCASE / "showcase.ipynb", as_version=4)
    client = nbclient.NotebookClient(
        nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(SHOWCASE)}}
    )
    client.execute()  # raises CellExecutionError on any error
    found_png = False
    for cell in nb.cells:
        for out in cell.get("outputs", []):
            assert out.get("output_type") != "error"
            if "image/png" in out.get("data", {}):
                found_png = True
    assert found_png
