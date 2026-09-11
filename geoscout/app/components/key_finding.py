"""Key finding component for displaying agent conclusions."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_key_finding(state: AgentState) -> None:
    """Render the primary research finding and execution outcome."""
    if state.status == "completed":
        status_badge = "<span class='gs-badge'>✓ COMPLETED</span>"
    elif state.status == "failed":
        status_badge = (
            "<span style='background: rgba(230,57,70,0.15); color: #E63946; "
            "border: 1px solid #E63946; padding: 3px 8px; border-radius: 4px; "
            "font-size: 0.75rem; font-weight: 600;'>✕ FAILED</span>"
        )
    else:
        status_badge = f"<span class='gs-badge-muted'>{state.status.upper()}</span>"

    finding_html = (
        "<div class='gs-key-finding'>"
        "<div style='display: flex; justify-content: space-between; align-items: center; "
        "margin-bottom: 8px;'>"
        "<span style='font-size: 0.8rem; font-weight: 700; color: #35D07F; "
        "letter-spacing: 0.08em; text-transform: uppercase;'>"
        "Key Research Finding"
        "</span>"
        f"{status_badge}"
        "</div>"
        "<div style='font-size: 1.15rem; line-height: 1.6; color: #F5F7FA; font-weight: 500;'>"
        f"{state.final_answer or 'No final answer was synthesized.'}"
        "</div>"
        "</div>"
    )
    st.markdown(finding_html, unsafe_allow_html=True)

    if state.error:
        st.error(f"Execution Error: {state.error}")
