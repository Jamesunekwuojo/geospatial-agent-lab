"""Custom styling and theme injection for GeoScout."""

import streamlit as st

THEME_CSS = """
<style>
/* -------------------------------------------------------------
   GeoScout Dark Geospatial Research Palette
   Background: #07111F | Surface: #0D1B2A | Accent: #35D07F
------------------------------------------------------------- */
:root {
    --gs-bg: #07111F;
    --gs-surface: #0D1B2A;
    --gs-surface-2: #102235;
    --gs-border: #1E3348;
    --gs-accent: #35D07F;
    --gs-text-primary: #F5F7FA;
    --gs-text-secondary: #8FA3B8;
    --gs-danger: #E63946;
    --gs-warning: #F4A261;
}

/* Global App Container */
.stApp {
    background-color: var(--gs-bg);
    color: var(--gs-text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--gs-text-primary) !important;
    font-weight: 600;
    letter-spacing: -0.02em;
}

p, span, label {
    color: var(--gs-text-primary);
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: var(--gs-surface) !important;
    border-right: 1px solid var(--gs-border) !important;
}

[data-testid="stSidebar"] hr {
    border-color: var(--gs-border) !important;
}

/* Container / Card styling */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--gs-surface);
    border: 1px solid var(--gs-border) !important;
    border-radius: 8px;
    padding: 0.5rem;
}

/* Buttons */
button[kind="primary"] {
    background-color: var(--gs-accent) !important;
    color: #07111F !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 6px !important;
    transition: all 0.2s ease-in-out !important;
}

button[kind="primary"]:hover {
    background-color: #2ebc71 !important;
    box-shadow: 0 4px 12px rgba(53, 208, 127, 0.25) !important;
}

/* Text Inputs & Selectboxes */
.stTextArea textarea, .stSelectbox select, div[data-baseweb="select"] {
    background-color: var(--gs-surface-2) !important;
    border: 1px solid var(--gs-border) !important;
    color: var(--gs-text-primary) !important;
    border-radius: 6px !important;
}

.stTextArea textarea:focus {
    border-color: var(--gs-accent) !important;
    box-shadow: 0 0 0 1px var(--gs-accent) !important;
}

/* Metrics Cards */
div[data-testid="stMetric"] {
    background-color: var(--gs-surface-2);
    border: 1px solid var(--gs-border);
    border-radius: 6px;
    padding: 10px 14px;
}

div[data-testid="stMetricLabel"] p {
    color: var(--gs-text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

div[data-testid="stMetricValue"] div {
    color: var(--gs-text-primary) !important;
    font-weight: 700;
    font-size: 1.4rem !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: var(--gs-surface-2) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: 6px !important;
    color: var(--gs-text-primary) !important;
    font-weight: 500;
}

/* Custom Research Badges */
.gs-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    background-color: rgba(53, 208, 127, 0.12);
    color: var(--gs-accent);
    border: 1px solid rgba(53, 208, 127, 0.3);
}

.gs-badge-muted {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    background-color: rgba(143, 163, 184, 0.12);
    color: var(--gs-text-secondary);
    border: 1px solid rgba(143, 163, 184, 0.3);
}

.gs-key-finding {
    background: linear-gradient(135deg, rgba(13, 27, 42, 0.95), rgba(16, 34, 53, 0.95));
    border-left: 4px solid var(--gs-accent);
    border-top: 1px solid var(--gs-border);
    border-right: 1px solid var(--gs-border);
    border-bottom: 1px solid var(--gs-border);
    border-radius: 0 8px 8px 0;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}

.gs-evidence-card {
    background-color: var(--gs-surface);
    border: 1px solid var(--gs-border);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}
</style>
"""


def apply_theme() -> None:
    """Inject the dark geospatial stylesheet into the Streamlit application."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)
