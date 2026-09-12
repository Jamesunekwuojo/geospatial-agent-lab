"""Spatial map component for interactive GeoScout visualization."""

from pathlib import Path

import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

from geoscout.agent.state import AgentState


def identify_claim_field(state: AgentState) -> str | None:
    """Identify the primary evidence field associated with the user question."""
    question = state.question.lower()

    claim_patterns = [
        (
            "mean_ndvi_change",
            [
                "mean ndvi change among hotspots",
                "average ndvi change among hotspots",
                "mean hotspot change",
            ],
        ),
        (
            "degraded_cells",
            [
                "how many cells experienced",
                "how many cells were degraded",
                "number of degraded cells",
                "degraded cells",
                "vegetation degradation",
            ],
        ),
        (
            "hotspot_count",
            [
                "how many hotspots",
                "number of hotspots",
                "hotspot count",
                "degradation hotspots",
            ],
        ),
        (
            "mean_change",
            [
                "mean ndvi change",
                "average ndvi change",
                "mean change",
                "average change",
            ],
        ),
        (
            "minimum_change",
            [
                "minimum ndvi change",
                "minimum change",
                "lowest ndvi change",
                "lowest change",
            ],
        ),
        (
            "maximum_change",
            [
                "maximum ndvi change",
                "maximum change",
                "highest ndvi change",
                "highest change",
            ],
        ),
        (
            "cell_count",
            [
                "how many cells are in",
                "number of cells",
                "cell count",
                "study region contains",
            ],
        ),
        (
            "crs",
            [
                "what is the crs",
                "which crs",
                "coordinate reference system",
                "spatial reference system",
            ],
        ),
    ]

    for field, patterns in claim_patterns:
        if any(pattern in question for pattern in patterns):
            return field

    return None


def load_spatial_dataset() -> gpd.GeoDataFrame | None:
    """Load the synthetic vegetation grid GeoJSON with path fallback."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    candidates = [
        Path("data/synthetic/vegetation_grid.geojson"),
        Path("geoscout/data/synthetic/vegetation_grid.geojson"),
        base_dir / "data" / "synthetic" / "vegetation_grid.geojson",
    ]
    dataset_path = next((c for c in candidates if c.exists()), None)
    if not dataset_path:
        return None
    try:
        return gpd.read_file(dataset_path)
    except Exception:
        return None


def render_spatial_result(state: AgentState) -> None:
    """Render the interactive Folium spatial map and analytical metrics."""
    st.markdown(
        "<h3 style='font-size: 1.2rem; margin-bottom: 4px;'>Spatial Result</h3>",
        unsafe_allow_html=True,
    )

    dataset = load_spatial_dataset()
    if dataset is None or dataset.empty:
        st.warning("Spatial dataset could not be loaded for visualization.")
        return

    dataset = dataset.copy()

    if "ndvi_change" not in dataset.columns:
        dataset["ndvi_change"] = dataset["current_ndvi"] - dataset["baseline_ndvi"]

    threshold = -0.10
    dataset["is_hotspot"] = dataset["ndvi_change"] <= threshold
    claim_field = identify_claim_field(state)

    dataset["is_result_cell"] = False
    result_label = "Study region overview"

    if claim_field in {"degraded_cells", "hotspot_count", "mean_ndvi_change"}:
        dataset["is_result_cell"] = dataset["is_hotspot"]
        result_label = "Detected degradation hotspots (ΔNDVI ≤ -0.10)"
    elif claim_field == "minimum_change":
        min_val = dataset["ndvi_change"].min()
        dataset["is_result_cell"] = dataset["ndvi_change"] == min_val
        result_label = f"Minimum NDVI change cell ({min_val:.4f})"
    elif claim_field == "maximum_change":
        max_val = dataset["ndvi_change"].max()
        dataset["is_result_cell"] = dataset["ndvi_change"] == max_val
        result_label = f"Maximum NDVI change cell ({max_val:.4f})"
    elif claim_field == "mean_change":
        result_label = "Regional mean NDVI change distribution"
    elif claim_field == "cell_count":
        result_label = f"Complete study region ({len(dataset)} cells)"
    elif claim_field == "crs":
        result_label = f"Study region CRS ({dataset.crs})"

    min_x, min_y, max_x, max_y = dataset.total_bounds
    center_lat = (min_y + max_y) / 2
    center_lon = (min_x + max_x) / 2

    spatial_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        control_scale=True,
    )

    for _, row in dataset.iterrows():
        is_hotspot = bool(row["is_hotspot"])
        is_result_cell = bool(row["is_result_cell"])
        ndvi_change = float(row["ndvi_change"])

        if is_result_cell:
            fill_color = "#E63946"
            fill_opacity = 0.85
            line_weight = 2.5
            line_color = "#FFFFFF"
        elif is_hotspot:
            fill_color = "#F4A261"
            fill_opacity = 0.50
            line_weight = 1.0
            line_color = "#E63946"
        else:
            fill_color = "#2A9D8F"
            fill_opacity = 0.25
            line_weight = 0.8
            line_color = "#1E3348"

        status_text = "Hotspot (Degraded)" if is_hotspot else "Stable / Regenerating"
        popup_html = (
            "<div style='font-family: sans-serif; font-size: 12px; color: #111;'>"
            f"<strong style='font-size: 13px;'>Cell: {row['cell_id']}</strong><br/>"
            f"<strong>Status:</strong> {status_text}<br/>"
            f"<strong>ΔNDVI:</strong> {ndvi_change:.4f}<br/>"
            f"<strong>Baseline:</strong> {row['baseline_ndvi']:.4f}<br/>"
            f"<strong>Current:</strong> {row['current_ndvi']:.4f}"
            "</div>"
        )
        tooltip = f"{row['cell_id']} · ΔNDVI: {ndvi_change:.4f}"

        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=(
                lambda feature,
                color=fill_color,
                opacity=fill_opacity,
                weight=line_weight,
                stroke=line_color: {
                    "fillColor": color,
                    "color": stroke,
                    "weight": weight,
                    "fillOpacity": opacity,
                }
            ),
            tooltip=tooltip,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(spatial_map)

    st_folium(
        spatial_map,
        width=None,
        height=420,
        returned_objects=[],
    )

    # Spatial summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Study Grid", f"{len(dataset)} Cells")
    with col2:
        highlight_fields = {
            "degraded_cells",
            "hotspot_count",
            "mean_ndvi_change",
            "minimum_change",
            "maximum_change",
        }
        if claim_field in highlight_fields:
            st.metric("Highlighted", int(dataset["is_result_cell"].sum()))
        else:
            st.metric("Degraded Cells", int(dataset["is_hotspot"].sum()))
    with col3:
        st.metric("Threshold", f"≤ {threshold:.2f}")

    st.caption(f"🗺️ **Map focus:** {result_label} · **CRS:** `{dataset.crs}`")
