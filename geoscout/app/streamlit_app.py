"""GeoScout — Evidence-Grounded Geospatial Research Agent.

Main Streamlit Application.
"""

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_GEOSCOUT_DIR = _APP_DIR.parent
_SRC_DIR = _GEOSCOUT_DIR / "src"

for _path in [_GEOSCOUT_DIR, _SRC_DIR, _APP_DIR]:
    if _path.exists() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import streamlit as st  # noqa: E402

try:
    from app.components.evidence_grounding import (  # noqa: E402
        render_evidence_grounding,
        render_raw_evidence_table,
    )
    from app.components.header import render_header  # noqa: E402
    from app.components.key_finding import render_key_finding  # noqa: E402
    from app.components.methodology import (  # noqa: E402
        render_methodology_and_limitations,
    )
    from app.components.question_input import (  # noqa: E402
        render_empty_state,
        render_question_input,
    )
    from app.components.sidebar import render_sidebar  # noqa: E402
    from app.components.spatial_map import render_spatial_result  # noqa: E402
    from app.components.styles import apply_theme  # noqa: E402
    from app.components.telemetry import render_telemetry  # noqa: E402
    from app.components.tool_trace import render_tool_trace  # noqa: E402
    from app.components.workflow_trace import render_workflow_trace  # noqa: E402
except ImportError:
    from components.evidence_grounding import (  # noqa: E402
        render_evidence_grounding,
        render_raw_evidence_table,
    )
    from components.header import render_header  # noqa: E402
    from components.key_finding import render_key_finding  # noqa: E402
    from components.methodology import (  # noqa: E402
        render_methodology_and_limitations,
    )
    from components.question_input import (  # noqa: E402
        render_empty_state,
        render_question_input,
    )
    from components.sidebar import render_sidebar  # noqa: E402
    from components.spatial_map import render_spatial_result  # noqa: E402
    from components.styles import apply_theme  # noqa: E402
    from components.telemetry import render_telemetry  # noqa: E402
    from components.tool_trace import render_tool_trace  # noqa: E402
    from components.workflow_trace import render_workflow_trace  # noqa: E402

from geoscout.agent.groq_planner import GroqAgentRunner  # noqa: E402

st.set_page_config(
    page_title="GeoScout — Geospatial Research Agent",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Execute the main GeoScout application workflow."""
    apply_theme()
    render_sidebar()
    render_header()

    question, run_clicked = render_question_input()

    if run_clicked:
        if not question:
            st.warning("Please enter a research question before running the analysis.")
            return

        with st.spinner("GeoScout is planning and executing the geospatial analysis..."):
            try:
                runner = GroqAgentRunner(max_steps=10)
                state = runner.run(question)
                st.session_state.current_state = state
            except Exception as exc:
                st.error(f"GeoScout execution failed: {exc}")
                return

    current_state = st.session_state.get("current_state")

    if current_state:
        st.divider()
        render_key_finding(current_state)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Primary Analytical Workspace (Desktop: Side-by-side | Mobile: Stacked)
        col_map, col_evidence = st.columns([1.1, 1], gap="large")

        with col_map:
            render_spatial_result(current_state)

        with col_evidence:
            render_evidence_grounding(current_state)
            render_raw_evidence_table(current_state)

        st.divider()
        render_workflow_trace(current_state)

        st.divider()
        render_tool_trace(current_state)

        st.divider()
        render_telemetry(current_state)

        st.divider()
        render_methodology_and_limitations()
    else:
        render_empty_state()
        st.divider()
        render_methodology_and_limitations()


if __name__ == "__main__":
    main()
