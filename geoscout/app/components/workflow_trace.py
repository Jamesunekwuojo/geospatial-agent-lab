"""Workflow trace component for visualizing agent execution progression."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_workflow_trace(state: AgentState) -> None:
    """Render the 5-stage research workflow execution trace with true state consistency."""
    st.markdown(
        "<h3 style='font-size: 1.15rem; margin-bottom: 2px;'>Agent Workflow Trace</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Observable execution lifecycle from natural-language query to deterministic GIS evidence."
    )

    # 1. Question Intake
    q_len = len(state.question.strip())
    s1 = {
        "title": "1. Question Intake",
        "status": "completed",
        "icon": "✓",
        "detail": f"Query received and validated ({q_len} chars)",
    }

    # 2. Tool Selection
    if state.tool_calls:
        tool_names = ", ".join(f"`{tc.tool_name}`" for tc in state.tool_calls)
        s2 = {
            "title": "2. Tool Selection",
            "status": "completed",
            "icon": "✓",
            "detail": f"Selected {len(state.tool_calls)} tool(s): {tool_names}",
        }
    else:
        s2 = {
            "title": "2. Tool Selection",
            "status": "skipped",
            "icon": "○",
            "detail": "Bypassed (Direct model response)",
        }

    # 3. GIS Computation
    if state.tool_executions:
        failed_execs = [e for e in state.tool_executions if not e.success]
        if failed_execs:
            s3 = {
                "title": "3. GIS Computation",
                "status": "failed",
                "icon": "✕",
                "detail": f"{len(failed_execs)} execution error(s) encountered",
            }
        else:
            s3 = {
                "title": "3. GIS Computation",
                "status": "completed",
                "icon": "✓",
                "detail": f"Executed {len(state.tool_executions)} deterministic tool operation(s)",
            }
    else:
        s3 = {
            "title": "3. GIS Computation",
            "status": "skipped",
            "icon": "○",
            "detail": "No GIS computation executed",
        }

    # 4. Evidence Collection
    if state.observations:
        s4 = {
            "title": "4. Evidence Collection",
            "status": "completed",
            "icon": "✓",
            "detail": f"Acquired {len(state.observations)} structured observation(s)",
        }
    else:
        s4 = {
            "title": "4. Evidence Collection",
            "status": "skipped",
            "icon": "○",
            "detail": "No tool observations collected",
        }

    # 5. Answer Synthesis & Grounding
    if state.final_answer:
        if state.observations and any(e.success for e in state.tool_executions):
            s5 = {
                "title": "5. Grounded Answer",
                "status": "completed",
                "icon": "✓",
                "detail": "Synthesized response grounded in verified GIS evidence",
            }
        else:
            s5 = {
                "title": "5. Ungrounded Answer",
                "status": "warning",
                "icon": "!",
                "detail": "Direct model answer without supporting GIS evidence",
            }
    else:
        if state.status == "failed" or state.error:
            s5 = {
                "title": "5. Response Synthesis",
                "status": "failed",
                "icon": "✕",
                "detail": "Execution failed before response generation",
            }
        else:
            s5 = {
                "title": "5. Response Synthesis",
                "status": "skipped",
                "icon": "○",
                "detail": "No final answer generated",
            }

    stages = [s1, s2, s3, s4, s5]
    completed_verified = sum(1 for s in stages if s["status"] == "completed")

    if completed_verified == 5:
        progress_text = "5/5 pipeline stages completed · Fully Evidence-Grounded"
    elif s5["status"] == "warning":
        progress_text = (
            f"{completed_verified}/5 verified stages · Direct Response (Ungrounded)"
        )
    elif any(s["status"] == "failed" for s in stages):
        progress_text = f"{completed_verified}/5 stages completed · Execution Failed"
    else:
        progress_text = f"{completed_verified}/5 pipeline stages completed"

    st.progress(
        completed_verified / len(stages),
        text=f"Workflow Status: {progress_text}",
    )

    cols = st.columns(len(stages))
    for i, s in enumerate(stages):
        status = s["status"]
        if status == "completed":
            border_color = "#35D07F"
            bg_color = "rgba(53, 208, 127, 0.06)"
            text_color = "#35D07F"
        elif status == "warning":
            border_color = "#F4A261"
            bg_color = "rgba(244, 162, 97, 0.08)"
            text_color = "#F4A261"
        elif status == "failed":
            border_color = "#E63946"
            bg_color = "rgba(230, 57, 70, 0.08)"
            text_color = "#E63946"
        else:  # skipped
            border_color = "#1E3348"
            bg_color = "#0D1B2A"
            text_color = "#8FA3B8"

        icon_html = f"<span>{s['icon']}</span> " if s.get("icon") else ""
        with cols[i]:
            card_html = (
                f"<div class='gs-step-card' style='background: {bg_color}; "
                f"border: 1px solid {border_color};'>"
                "<div>"
                f"<div style='font-size: 0.78rem; font-weight: 700; color: {text_color}; "
                "margin-bottom: 4px; display: flex; align-items: center; gap: 4px;'>"
                f"{icon_html}<span>{s['title']}</span>"
                "</div>"
                f"<div style='font-size: 0.74rem; color: #8FA3B8; line-height: 1.35;'>"
                f"{s['detail']}"
                "</div>"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
