"""Methodology and research limitations component for GeoScout."""

import streamlit as st


def render_methodology_and_limitations() -> None:
    """Render the methodology explainer and research limitations expanders."""
    with st.expander(
        "ℹ️ How GeoScout Produced This Result (Architecture & Pipeline)",
        expanded=False,
    ):
        st.markdown(
            """
GeoScout decouples language-model reasoning from deterministic geospatial computation:

1. **Orchestration:** The LLM receives the research question, reasons about required spatial
   metrics, and selects from validated tool schemas.
2. **Computation:** Deterministic GIS functions (`geopandas`, `shapely`) execute numerical
   aggregations against the 100-cell vegetation grid.
3. **Evidence Extraction:** Structured key-value outputs (e.g., `degraded_cells = 9`,
   `mean_change = -0.0617`) are returned into `AgentState`.
4. **Grounded Synthesis:** The LLM produces its final response strictly conditioned on the
   observed GIS evidence.

The interface visualizes this trace so every claim can be audited against executable spatial data.
"""
        )

    with st.expander("⚠️ Research Scope & Limitations", expanded=False):
        st.markdown(
            """
### Current Prototype Limitations
- **Synthetic Dataset:** Analysis is performed on a controlled 100-cell synthetic vegetation grid.
- **Evidence Verification:** Grounding validates the presence of supporting deterministic tool
  observations; it does not independently parse unconstrained free-text rhetoric.
- **Scope:** This demonstration serves as an observability interface on top of the frozen
  GeoScout v3 experimental baseline.
- **Model Comparison Findings:** Findings between models (e.g. 20B vs 120B) reflect specific
  benchmark prompt-following in this controlled test and should not be generalized to mean
  model scale alone caused differences.

For the complete benchmark taxonomy and experimental findings, consult `RESEARCH_REPORT.md`
in the repository.
"""
        )
