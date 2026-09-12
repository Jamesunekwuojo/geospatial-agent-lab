"""Question input component for GeoScout."""

import streamlit as st

EXAMPLE_QUESTIONS = [
    "How many cells experienced significant vegetation degradation?",
    "What is the mean NDVI change across the study region?",
    "What is the minimum NDVI change?",
    "How many cells are in the study region?",
    "What is the CRS of the study region?",
]


def render_question_input(
    is_running: bool | None = None, **kwargs
) -> tuple[str, bool]:
    """Render the research question input area and run trigger."""
    if is_running is None:
        is_running = st.session_state.get("is_running", False)

    st.markdown(
        "<h3 style='font-size: 1.2rem; margin-bottom: 6px;'>Research Question</h3>",
        unsafe_allow_html=True,
    )

    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    def _sync_example_question() -> None:
        selected = st.session_state.get("example_select_widget")
        if selected and selected != "Select a research question...":
            st.session_state.question_input = selected

    question = st.text_area(
        "Ask GeoScout a geospatial research question",
        placeholder="Example: How many cells experienced significant vegetation degradation?",
        height=90,
        label_visibility="collapsed",
        key="question_input",
        disabled=is_running,
    )

    col_select, col_btn = st.columns([3, 2])

    with col_select:
        st.selectbox(
            "Example questions",
            ["Select a research question..."] + EXAMPLE_QUESTIONS,
            key="example_select_widget",
            on_change=_sync_example_question,
            label_visibility="collapsed",
            disabled=is_running,
        )

    with col_btn:
        run_clicked = st.button(
            "Run Geospatial Analysis",
            type="primary",
            use_container_width=True,
            disabled=is_running,
        )

    return question.strip(), run_clicked


def render_empty_state() -> None:
    """Render a clean empty state when no analysis is currently displayed."""
    empty_html = (
        "<div style='background-color: #0D1B2A; border: 1px dashed #1E3348; border-radius: 8px; "
        "padding: 2.5rem 1.5rem; text-align: center; margin-top: 1rem;'>"
        "<div style='font-size: 2.2rem; margin-bottom: 0.5rem;'>🛰️</div>"
        "<h3 style='font-size: 1.25rem; margin-bottom: 0.5rem; color: #F5F7FA;'>"
        "Ready for Geospatial Analysis</h3>"
        "<p style='color: #8FA3B8; max-width: 580px; margin: 0 auto 1.25rem auto; "
        "font-size: 0.95rem; line-height: 1.5;'>"
        "Enter an environmental inquiry above or pick an example question to observe the agent "
        "select deterministic GIS tools, collect structured evidence, and render spatial hotspot "
        "visualizations."
        "</p>"
        "<div style='display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;'>"
        "<div style='background: #102235; border: 1px solid #1E3348; border-radius: 6px; "
        "padding: 8px 14px; font-size: 0.82rem;'>"
        "<strong style='color: #35D07F;'>1. Plan</strong> · Multi-turn tool calling"
        "</div>"
        "<div style='background: #102235; border: 1px solid #1E3348; border-radius: 6px; "
        "padding: 8px 14px; font-size: 0.82rem;'>"
        "<strong style='color: #35D07F;'>2. Execute</strong> · Deterministic GIS"
        "</div>"
        "<div style='background: #102235; border: 1px solid #1E3348; border-radius: 6px; "
        "padding: 8px 14px; font-size: 0.82rem;'>"
        "<strong style='color: #35D07F;'>3. Ground</strong> · Verifiable Evidence"
        "</div>"
        "</div>"
        "</div>"
    )
    st.markdown(empty_html, unsafe_allow_html=True)
