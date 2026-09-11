"""Workflow trace component for visualizing agent execution progression."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_workflow_trace(state: AgentState) -> None:
    """Render the 5-stage research workflow execution trace."""
    st.markdown(
        "<h3 style='font-size: 1.2rem; margin-bottom: 4px;'>Agent Workflow Trace</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Observable execution path from natural-language query to deterministic GIS evidence."
    )

    tools_summary = (
        f"Selected `{len(state.tool_calls)}` GIS tool(s): "
        + ", ".join(f"`{tc.tool_name}`" for tc in state.tool_calls)
        if state.tool_calls
        else "No tools selected."
    )
    exec_summary = (
        f"Executed `{len(state.tool_executions)}` deterministic tool operations."
        if state.tool_executions
        else "No executions recorded."
    )
    obs_summary = (
        f"Collected `{len(state.observations)}` structured tool observation(s)."
        if state.observations
        else "No observations recorded."
    )
    ans_summary = (
        "Synthesized final response grounded in observable tool evidence."
        if state.final_answer
        else "No final response generated."
    )

    stages = [
        ("1. Question Received", True, f"**Query:** {state.question}"),
        ("2. Tool Selection", bool(state.tool_calls), tools_summary),
        ("3. GIS Computation", bool(state.tool_executions), exec_summary),
        ("4. Evidence Collected", bool(state.observations), obs_summary),
        ("5. Final Grounded Answer", bool(state.final_answer), ans_summary),
    ]

    completed_count = sum(1 for _, ok, _ in stages if ok)
    st.progress(
        completed_count / len(stages),
        text=f"Workflow Progress: {completed_count}/{len(stages)} stages completed",
    )

    cols = st.columns(len(stages))
    for i, (title, is_complete, detail) in enumerate(stages):
        with cols[i]:
            status_symbol = "✓" if is_complete else "○"
            border_color = "#35D07F" if is_complete else "#1E3348"
            bg_color = "rgba(53, 208, 127, 0.05)" if is_complete else "#0D1B2A"
            text_color = "#35D07F" if is_complete else "#8FA3B8"

            card_html = (
                f"<div style='background: {bg_color}; border: 1px solid {border_color}; "
                "border-radius: 6px; padding: 10px 8px; min-height: 120px;'>"
                f"<div style='font-size: 0.8rem; font-weight: 700; color: {text_color}; "
                "margin-bottom: 4px;'>"
                f"{status_symbol} {title}"
                "</div>"
                f"<div style='font-size: 0.76rem; color: #8FA3B8; line-height: 1.3;'>"
                f"{detail}"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
