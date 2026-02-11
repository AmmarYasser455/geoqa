"""
Interactive map visualization module.

Creates folium-based interactive maps with quality issue highlighting,
custom styling, and data popups.
"""

from __future__ import annotations

from typing import Any, Optional

import geopandas as gpd
import numpy as np

try:
    import folium
    from folium.plugins import MarkerCluster

    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


class MapVisualizer:
    """Creates interactive maps for geospatial data visualization.

    Generates folium maps with:
    - Automatic CRS reprojection to EPSG:4326 for web display
    - Feature styling based on geometry type
    - Quality issue highlighting (invalid/empty geometries in red)
    - Interactive popups with attribute data
    - Layer controls and basemap options

    Args:
        gdf: The GeoDataFrame to visualize.
        name: Display name for the layer.
    """

    def __init__(self, gdf: gpd.GeoDataFrame, name: str = "Data") -> None:
        self._gdf = gdf
        self._name = name

    def create_map(
        self,
        style: Optional[dict] = None,
        issue_indices: Optional[set] = None,
        width: str = "100%",
        height: str = "600px",
        tiles: str = "OpenStreetMap",
    ):
        """Create an interactive folium map.

        Args:
            style: Optional style dict for normal features.
            issue_indices: Set of row indices to highlight as issues.
            width: Map width (CSS).
            height: Map height (CSS).
            tiles: Base tile layer name.

        Returns:
            folium.Map object (displayable in Jupyter).
        """
        if not HAS_FOLIUM:
            raise ImportError(
                "folium is required for map visualization. "
                "Install it with: pip install folium"
            )

        if len(self._gdf) == 0:
            return folium.Map(location=[0, 0], zoom_start=2, width=width, height=height)

        # Reproject to EPSG:4326 for web display
        gdf_web = self._to_wgs84(self._gdf)

        # Compute center and zoom
        center = self._compute_center(gdf_web)
        zoom = self._compute_zoom(gdf_web)

        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            width=width,
            height=height,
            tiles=tiles,
        )

        # Add additional tile layers
        folium.TileLayer("CartoDB positron", name="CartoDB Light").add_to(m)
        folium.TileLayer("CartoDB dark_matter", name="CartoDB Dark").add_to(m)

        if issue_indices is None:
            issue_indices = set()

        # Default styles
        default_style = style or {
            "color": "#3388ff",
            "weight": 2,
            "fillOpacity": 0.4,
            "fillColor": "#3388ff",
        }

        issue_style = {
            "color": "#ff4444",
            "weight": 3,
            "fillOpacity": 0.6,
            "fillColor": "#ff4444",
        }

        # Add features
        normal_gdf = gdf_web.loc[~gdf_web.index.isin(issue_indices)]
        issue_gdf = gdf_web.loc[gdf_web.index.isin(issue_indices)]

        # Add normal features
        if len(normal_gdf) > 0:
            self._add_geojson_layer(
                m,
                normal_gdf,
                name=f"{self._name} (Valid)",
                style=default_style,
            )

        # Add issue features
        if len(issue_gdf) > 0:
            self._add_geojson_layer(
                m,
                issue_gdf,
                name=f"{self._name} (Issues)",
                style=issue_style,
            )

        # Add layer control
        folium.LayerControl().add_to(m)

        return m

    def create_quality_map(self, geometry_results: dict):
        """Create a map color-coded by quality status.

        Args:
            geometry_results: Results from GeometryChecker.check_all().

        Returns:
            folium.Map with quality-based coloring.
        """
        if not HAS_FOLIUM:
            raise ImportError("folium is required for map visualization.")

        if len(self._gdf) == 0:
            return folium.Map(location=[0, 0], zoom_start=2)

        gdf_web = self._to_wgs84(self._gdf)
        center = self._compute_center(gdf_web)
        zoom = self._compute_zoom(gdf_web)

        m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

        invalid_set = set(geometry_results.get("invalid_indices", []))
        empty_set = set(geometry_results.get("empty_indices", []))
        dup_set = set(geometry_results.get("duplicate_indices", []))

        def style_function(feature):
            idx = feature["properties"].get("_geoqa_idx", -1)
            if idx in invalid_set:
                return {"color": "#ff0000", "weight": 3, "fillColor": "#ff0000", "fillOpacity": 0.6}
            elif idx in empty_set:
                return {"color": "#ff8800", "weight": 3, "fillColor": "#ff8800", "fillOpacity": 0.6}
            elif idx in dup_set:
                return {"color": "#ffaa00", "weight": 2, "fillColor": "#ffaa00", "fillOpacity": 0.4}
            else:
                return {"color": "#00aa44", "weight": 2, "fillColor": "#00aa44", "fillOpacity": 0.3}

        # Add index to properties
        gdf_indexed = gdf_web.copy()
        gdf_indexed["_geoqa_idx"] = gdf_indexed.index

        geojson = folium.GeoJson(
            gdf_indexed.__geo_interface__,
            name="Quality Map",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=[c for c in gdf_indexed.columns if c not in ["geometry", "_geoqa_idx"]][:5],
                aliases=[c for c in gdf_indexed.columns if c not in ["geometry", "_geoqa_idx"]][:5],
            ),
        )
        geojson.add_to(m)

        # Add legend
        self._add_quality_legend(m)

        folium.LayerControl().add_to(m)
        return m

    def _add_geojson_layer(
        self,
        m,
        gdf: gpd.GeoDataFrame,
        name: str,
        style: dict,
    ) -> None:
        """Add a GeoJSON layer to the map with popups."""
        # Filter out null/empty geometries
        valid_gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

        if len(valid_gdf) == 0:
            return

        # Build tooltip fields (max 5 attribute columns)
        attr_cols = [c for c in valid_gdf.columns if c != valid_gdf.geometry.name][:5]

        try:
            geojson = folium.GeoJson(
                valid_gdf.__geo_interface__,
                name=name,
                style_function=lambda feature, s=style: s,
                tooltip=folium.GeoJsonTooltip(
                    fields=attr_cols,
                    aliases=attr_cols,
                ) if attr_cols else None,
            )
            geojson.add_to(m)
        except Exception:
            # Fallback: add without tooltip
            try:
                geojson = folium.GeoJson(
                    valid_gdf.__geo_interface__,
                    name=name,
                    style_function=lambda feature, s=style: s,
                )
                geojson.add_to(m)
            except Exception:
                pass

    def _add_quality_legend(self, m) -> None:
        """Add a quality color legend to the map."""
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                    background-color: white; padding: 10px; border-radius: 5px;
                    border: 2px solid grey; font-size: 14px;">
            <b>Quality Legend</b><br>
            <span style="color: #00aa44;">&#9632;</span> Valid<br>
            <span style="color: #ff0000;">&#9632;</span> Invalid Geometry<br>
            <span style="color: #ff8800;">&#9632;</span> Empty Geometry<br>
            <span style="color: #ffaa00;">&#9632;</span> Duplicate Geometry
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

    @staticmethod
    def _to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Reproject to EPSG:4326 if needed."""
        if gdf.crs is None:
            return gdf
        if gdf.crs.to_epsg() == 4326:
            return gdf
        try:
            return gdf.to_crs(epsg=4326)
        except Exception:
            return gdf

    @staticmethod
    def _compute_center(gdf: gpd.GeoDataFrame) -> list[float]:
        """Compute map center from bounds."""
        try:
            bounds = gdf.total_bounds
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2
            return [center_lat, center_lon]
        except Exception:
            return [0, 0]

    @staticmethod
    def _compute_zoom(gdf: gpd.GeoDataFrame) -> int:
        """Estimate appropriate zoom level from bounds."""
        try:
            bounds = gdf.total_bounds
            dx = bounds[2] - bounds[0]
            dy = bounds[3] - bounds[1]
            max_span = max(dx, dy)

            if max_span > 100:
                return 3
            elif max_span > 50:
                return 5
            elif max_span > 10:
                return 7
            elif max_span > 1:
                return 10
            elif max_span > 0.1:
                return 13
            elif max_span > 0.01:
                return 15
            else:
                return 17
        except Exception:
            return 10
