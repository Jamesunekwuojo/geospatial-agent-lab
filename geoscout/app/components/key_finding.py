"""Key finding component for displaying agent conclusions."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_key_finding(state: AgentState) -> None:
    """Render the primary research finding and execution outcome with true groundedness."""
    has_evidence = bool(state.observations)
    has_successful_tools = any(e.success for e in state.tool_executions)

    if state.status == "failed" or state.error:
        card_class = "gs-key-finding-failed"
        label_text = "Analysis Failed"
        status_badge = "<span class='gs-badge-error'>✕ FAILED</span>"
    elif has_evidence and has_successful_tools:
        card_class = "gs-key-finding-grounded"
        label_text = "Key Research Finding (Grounded)"
        status_badge = "<span class='gs-badge'>✓ EVIDENCE GROUNDED</span>"
    else:
        card_class = "gs-key-finding-ungrounded"
        label_text = "Direct Language Model Response (Ungrounded)"
        status_badge = (
            "<span class='gs-badge-warning'> NO GIS EVIDENCE</span>"
        )

    finding_html = (
        f"<div class='{card_class}'>"
        "<div style='display: flex; justify-content: space-between; align-items: center; "
        "margin-bottom: 8px;'>"
        f"<span style='font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; "
        f"text-transform: uppercase;'>{label_text}</span>"
        f"{status_badge}"
        "</div>"
        "<div style='font-size: 1.10rem; line-height: 1.55; color: #F5F7FA; font-weight: 500;'>"
        f"{state.final_answer or 'No final answer was synthesized.'}"
        "</div>"
    )

    if not has_evidence and state.final_answer and state.status != "failed":
        finding_html += (
            "<div style='margin-top: 10px; font-size: 0.80rem; color: #F4A261; "
            "border-top: 1px dashed rgba(244, 162, 97, 0.3); padding-top: 6px;'>"
            "<strong>Observability Notice:</strong> The language model produced this answer "
            "directly without executing deterministic GIS tools. The claims are not corroborated "
            "by spatial dataset evidence."
            "</div>"
        )

    finding_html += "</div>"
    st.markdown(finding_html, unsafe_allow_html=True)

    if state.error:
        st.error(f"Execution Diagnostic: {state.error}")
