"""Telemetry and run summary component for GeoScout."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_telemetry(state: AgentState) -> None:
    """Render the operational telemetry and run summary metrics."""
    st.markdown(
        "<h3 style='font-size: 1.2rem; margin-bottom: 4px;'>Run Telemetry</h3>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Steps", state.steps)

    with col2:
        st.metric("LLM Invocations", len(state.llm_calls))

    with col3:
        st.metric("GIS Tool Calls", len(state.tool_calls))

    with col4:
        total_lat = state.total_latency_ms if state.total_latency_ms is not None else 0.0
        st.metric("Total Latency", f"{total_lat / 1000:.2f} s")

    with col5:
        total_tokens = sum(call.total_tokens or 0 for call in state.llm_calls)
        st.metric("Total Tokens", f"{total_tokens:,}" if total_tokens else "N/A")

    if state.llm_calls:
        token_details = [
            f"Call #{c.call_number}: {c.total_tokens or 0:,} tokens ({(c.latency_ms or 0.0):.1f}ms)"
            for c in state.llm_calls
        ]
        st.caption(" **LLM breakdown:** " + " · ".join(token_details))
