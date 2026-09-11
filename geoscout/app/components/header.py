"""Header component for GeoScout."""

import streamlit as st


def render_header() -> None:
    """Render the compact research header and identity badges."""
    col_title, col_badges = st.columns([3, 2])

    with col_title:
        st.markdown(
            "<h1 style='margin-bottom: 0px; font-size: 2.0rem;'>🌍 GeoScout</h1>"
            "<p style='color: #8FA3B8; margin-top: 4px; font-size: 1.0rem; font-weight: 500;'>"
            "Evidence-Grounded Geospatial Research Agent</p>",
            unsafe_allow_html=True,
        )

    with col_badges:
        st.markdown(
            "<div style='text-align: right; padding-top: 8px;'>"
            "<span class='gs-badge'>RESEARCH PROTOTYPE</span>&nbsp;&nbsp;"
            "<span class='gs-badge-muted'>Baseline: GeoScout v3</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    banner_html = (
        "<div style='background-color: rgba(13, 27, 42, 0.6); border: 1px solid #1E3348; "
        "border-radius: 6px; padding: 10px 14px; margin-top: 8px; margin-bottom: 16px; "
        "font-size: 0.88rem; color: #8FA3B8;'>"
        "<strong style='color: #35D07F;'>Core Architecture:</strong> "
        "LLM Agent Plans & Orchestrates · Deterministic GIS Tools Compute · "
        "Observable Evidence Tracing · Synthetic Environmental Dataset"
        "</div>"
    )
    st.markdown(banner_html, unsafe_allow_html=True)
