"""Tool execution trace component for GeoScout."""

import streamlit as st

from geoscout.agent.state import AgentState


def render_tool_trace(state: AgentState) -> None:
    """Render the detailed tool execution trace and diagnostic telemetry."""
    st.markdown(
        "<h3 style='font-size: 1.2rem; margin-bottom: 4px;'>Deterministic Tool Trace</h3>",
        unsafe_allow_html=True,
    )
    st.caption("Detailed diagnostics for each GIS tool call invocation and execution.")

    if not state.tool_calls:
        st.info("No GIS tools were invoked during this analysis.")
        return

    for index, tool_call in enumerate(state.tool_calls, start=1):
        execution = next(
            (item for item in state.tool_executions if item.tool_call_id == tool_call.tool_call_id),
            None,
        )

        status_text = "SUCCESS" if (execution and execution.success) else "FAILED"
        if execution and execution.latency_ms is not None:
            latency_text = f"{execution.latency_ms:.1f} ms"
        else:
            latency_text = "N/A"

        header_label = f"#{index} `{tool_call.tool_name}` · {status_text} ({latency_text})"

        with st.expander(header_label, expanded=False):
            col_args, col_exec = st.columns(2)

            with col_args:
                st.markdown(
                    "<strong style='font-size: 0.85rem; color: #8FA3B8;'>Tool Arguments</strong>",
                    unsafe_allow_html=True,
                )
                st.json(tool_call.arguments or {})

            with col_exec:
                st.markdown(
                    "<strong style='font-size: 0.85rem; color: #8FA3B8;'>"
                    "Execution Metrics</strong>",
                    unsafe_allow_html=True,
                )
                exec_payload = {
                    "tool": tool_call.tool_name,
                    "status": status_text,
                    "latency_ms": round(execution.latency_ms, 2) if execution else None,
                }
                if execution and execution.error:
                    exec_payload["error"] = execution.error

                st.json(exec_payload)
