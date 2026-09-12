"""Evidence grounding component for GeoScout."""

import streamlit as st

from geoscout.agent.state import AgentState

CLAIM_TEMPLATES = {
    "cell_count": "The study region contains {value} cells.",
    "degraded_cells": "{value} cells experienced significant vegetation degradation.",
    "hotspot_count": "{value} cells were detected as degradation hotspots.",
    "mean_change": "The mean NDVI change across the study region was {value}.",
    "mean_ndvi_change": "The mean NDVI change among detected hotspots was {value}.",
    "minimum_change": "The minimum NDVI change observed was {value}.",
    "maximum_change": "The maximum NDVI change observed was {value}.",
    "crs": "The study region uses CRS {value}.",
}


def render_evidence_grounding(state: AgentState) -> None:
    """Render the Claim -> Evidence -> Tool grounding ledger."""
    st.markdown(
        "<h3 style='font-size: 1.15rem; margin-bottom: 2px;'>Evidence Grounding</h3>",
        unsafe_allow_html=True,
    )
    st.caption("Verifiable link between generated claims and deterministic GIS observations.")

    if not state.observations:
        st.markdown(
            "<div style='background: rgba(244, 162, 97, 0.08); border: 1px solid #F4A261; "
            "border-radius: 6px; padding: 12px; margin-top: 6px; "
            "font-size: 0.85rem; color: #F5F7FA;'>"
            "<strong style='color: #F4A261;'> No GIS Evidence Collected</strong><br/>"
            "The agent did not invoke deterministic tools for this query. "
            "No structured spatial observations are available to ground the response."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    evidence_items = []
    for observation_index, observation in enumerate(state.observations, start=1):
        if isinstance(observation, dict):
            tool_name = observation.get(
                "tool",
                observation.get("name", observation.get("tool_name", "Unknown tool")),
            )
            output = observation.get("output", observation.get("result", {}))
        else:
            tool_name = getattr(observation, "tool_name", "Unknown tool")
            output = getattr(observation, "result", {})

        if not isinstance(output, dict):
            continue

        for field, value in output.items():
            if field in CLAIM_TEMPLATES:
                evidence_items.append(
                    {
                        "observation_index": observation_index,
                        "tool": tool_name,
                        "field": field,
                        "value": value,
                    }
                )

    if not evidence_items:
        st.info("Tool executed, but no standardized claim fields matched the template registry.")
        return

    for index, item in enumerate(evidence_items, start=1):
        field = item["field"]
        value = item["value"]
        tool_name = item["tool"]
        obs_idx = item["observation_index"]

        formatted_val = f"{value:.4f}" if isinstance(value, float) else str(value)
        claim_text = CLAIM_TEMPLATES[field].format(value=formatted_val)

        with st.container():
            card_html = (
                "<div class='gs-evidence-card'>"
                "<div style='display: flex; justify-content: space-between; align-items: center; "
                "margin-bottom: 6px;'>"
                f"<span style='font-size: 0.76rem; font-weight: 600; color: #8FA3B8;'>"
                f"CLAIM #{index}</span>"
                "<span class='gs-badge'>✓ EVIDENCE SUPPORTED</span>"
                "</div>"
                "<div style='font-size: 0.95rem; font-weight: 600; color: #F5F7FA; "
                "margin-bottom: 10px;'>"
                f'"{claim_text}"'
                "</div>"
                "<div style='display: grid; grid-template-columns: 1fr 1fr 1.2fr; gap: 8px; "
                "background: #102235; border: 1px solid #1E3348; border-radius: 6px; "
                "padding: 8px 10px;'>"
                "<div>"
                "<div style='font-size: 0.70rem; color: #8FA3B8; text-transform: uppercase;'>"
                "Field</div>"
                f"<div style='font-family: monospace; font-size: 0.82rem; color: #35D07F; "
                f"font-weight: 600;'>{field}</div>"
                "</div>"
                "<div>"
                "<div style='font-size: 0.70rem; color: #8FA3B8; text-transform: uppercase;'>"
                "Value</div>"
                f"<div style='font-family: monospace; font-size: 0.82rem; color: #F5F7FA; "
                f"font-weight: 600;'>{formatted_val}</div>"
                "</div>"
                "<div>"
                "<div style='font-size: 0.70rem; color: #8FA3B8; text-transform: uppercase;'>"
                "Source Tool</div>"
                f"<div style='font-family: monospace; font-size: 0.82rem; color: #8FA3B8;'>"
                f"{tool_name} (#{obs_idx})</div>"
                "</div>"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)


def render_raw_evidence_table(state: AgentState) -> None:
    """Render raw structured observations from executed GIS tools."""
    if not state.observations:
        return

    st.markdown(
        "<h4 style='font-size: 1.0rem; margin-top: 14px; margin-bottom: 4px; color: #8FA3B8;'>"
        "Observed Feature Metrics</h4>",
        unsafe_allow_html=True,
    )

    for obs in state.observations:
        if isinstance(obs, dict):
            tool_name = obs.get(
                "tool",
                obs.get("name", obs.get("tool_name", "Unknown tool")),
            )
            result = obs.get("output", obs.get("result", {}))
        else:
            tool_name = getattr(obs, "tool_name", "Unknown tool")
            result = getattr(obs, "result", {})

        if isinstance(result, dict):
            preferred_fields = [
                ("cell_count", "Total Cells"),
                ("degraded_cells", "Degraded Cells"),
                ("hotspot_count", "Hotspots"),
                ("mean_change", "Mean ΔNDVI"),
                ("mean_ndvi_change", "Hotspot Mean ΔNDVI"),
                ("minimum_change", "Min ΔNDVI"),
                ("maximum_change", "Max ΔNDVI"),
                ("crs", "CRS"),
            ]
            avail = [
                (f, lbl)
                for f, lbl in preferred_fields
                if f in result and result[f] is not None
            ]
            if avail:
                cols = st.columns(min(len(avail), 4))
                for i, (f, lbl) in enumerate(avail):
                    with cols[i % len(cols)]:
                        val = result[f]
                        disp = f"{val:.4f}" if isinstance(val, float) else str(val)
                        st.metric(lbl, disp)

        with st.expander(f"Inspect Raw JSON: `{tool_name}`", expanded=False):
            st.json(result)
