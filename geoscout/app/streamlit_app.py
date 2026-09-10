import sys
from pathlib import Path

# Ensure src/ is on sys.path regardless of execution directory
_SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if _SRC_PATH.exists() and str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

import folium  # noqa: E402
import geopandas as gpd  # noqa: E402
import streamlit as st  # noqa: E402
from streamlit_folium import st_folium  # noqa: E402

from geoscout.agent.groq_planner import GroqAgentRunner  # noqa: E402

st.set_page_config(
    page_title="GeoScout — Geospatial Research Agent",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


EXAMPLE_QUESTIONS = [
    "How many cells experienced significant vegetation degradation?",
    "What is the mean NDVI change across the study region?",
    "What is the minimum NDVI change?",
    "How many cells are in the study region?",
    "What is the CRS of the study region?",
]


def run_agent(question: str):
    """Run GeoScout using the existing agent implementation."""
    runner = GroqAgentRunner(max_steps=10)
    return runner.run(question)


def find_supporting_evidence(state, claim_field):
    """Find evidence specifically supporting one claim field."""
    evidence = []

    for observation_index, observation in enumerate(
        state.observations,
        start=1,
    ):
        if isinstance(observation, dict):
            tool_name = observation.get(
                "tool",
                observation.get("name", observation.get("tool_name", "Unknown tool")),
            )
            output = observation.get(
                "output",
                observation.get("result", {}),
            )
        else:
            tool_name = getattr(observation, "tool_name", "Unknown tool")
            output = getattr(observation, "result", {})

        if not isinstance(output, dict):
            continue

        if claim_field not in output:
            continue

        evidence.append(
            {
                "observation_index": observation_index,
                "tool": tool_name,
                "field": claim_field,
                "value": output[claim_field],
            }
        )

    return evidence


def identify_claim_field(state):
    """Identify the primary evidence field associated with the user question."""
    question = state.question.lower()

    claim_patterns = [
        (
            "mean_ndvi_change",
            [
                "mean ndvi change among hotspots",
                "average ndvi change among hotspots",
                "mean hotspot change",
            ],
        ),
        (
            "degraded_cells",
            [
                "how many cells experienced",
                "how many cells were degraded",
                "number of degraded cells",
                "degraded cells",
                "vegetation degradation",
            ],
        ),
        (
            "hotspot_count",
            [
                "how many hotspots",
                "number of hotspots",
                "hotspot count",
                "degradation hotspots",
            ],
        ),
        (
            "mean_change",
            [
                "mean ndvi change",
                "average ndvi change",
                "mean change",
                "average change",
            ],
        ),
        (
            "minimum_change",
            [
                "minimum ndvi change",
                "minimum change",
                "lowest ndvi change",
                "lowest change",
            ],
        ),
        (
            "maximum_change",
            [
                "maximum ndvi change",
                "maximum change",
                "highest ndvi change",
                "highest change",
            ],
        ),
        (
            "cell_count",
            [
                "how many cells are in",
                "number of cells",
                "cell count",
                "study region contains",
            ],
        ),
        (
            "crs",
            [
                "what is the crs",
                "which crs",
                "coordinate reference system",
                "spatial reference system",
            ],
        ),
    ]

    # More specific patterns should be checked first.
    for field, patterns in claim_patterns:
        if any(pattern in question for pattern in patterns):
            return field

    return None


def display_agent_workflow(state) -> None:
    """Display the actual agent execution workflow."""
    st.subheader("Agent Workflow")

    st.caption(
        "Trace of the agent's execution from question intake "
        "through tool selection, GIS execution, evidence collection, "
        "and answer generation."
    )

    # ---------------------------------------------------------
    # 1. Question received
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown("### ✓ 1. Question Received")

        st.markdown(
            f"**User question:**  \n"
            f"{state.question}"
        )

    # ---------------------------------------------------------
    # 2. Tool selection
    # ---------------------------------------------------------
    with st.container(border=True):
        if state.tool_calls:
            st.markdown("### ✓ 2. Tool Selection")

            st.markdown(
                "The agent selected the following deterministic GIS tool(s):"
            )

            for index, tool_call in enumerate(state.tool_calls, start=1):
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get(
                        "name",
                        tool_call.get("tool", tool_call.get("tool_name", "Unknown tool")),
                    )

                    arguments = tool_call.get(
                        "arguments",
                        tool_call.get("args", {}),
                    )
                else:
                    tool_name = getattr(tool_call, "tool_name", str(tool_call))
                    arguments = getattr(tool_call, "arguments", {})

                st.markdown(
                    f"**Tool {index}:** `{tool_name}`"
                )

                if arguments:
                    st.code(
                        str(arguments),
                        language="json",
                    )
        else:
            st.markdown("### ○ 2. Tool Selection")

            st.warning(
                "No tool calls were recorded for this run."
            )

    # ---------------------------------------------------------
    # 3. GIS execution
    # ---------------------------------------------------------
    with st.container(border=True):
        if state.tool_executions:
            st.markdown("### ✓ 3. GIS Computation")

            st.markdown(
                "The selected GIS operation(s) were executed "
                "against the study dataset."
            )

            for index, execution in enumerate(
                state.tool_executions,
                start=1,
            ):
                if isinstance(execution, dict):
                    tool_name = execution.get(
                        "tool",
                        execution.get("name", execution.get("tool_name", "Unknown tool")),
                    )

                    success = execution.get(
                        "success",
                        True,
                    )

                    latency = execution.get(
                        "latency_ms"
                    )
                else:
                    tool_name = getattr(execution, "tool_name", "Unknown tool")
                    success = getattr(execution, "success", True)
                    latency = getattr(execution, "latency_ms", None)

                status = "Success" if success else "Failed"

                st.markdown(
                    f"**Execution {index}:** `{tool_name}`"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Status",
                        status,
                    )

                with col2:
                    if latency is not None:
                        st.metric(
                            "Latency",
                            f"{latency:.1f} ms",
                        )
                    else:
                        st.metric(
                            "Latency",
                            "N/A",
                        )
        else:
            st.markdown("### ○ 3. GIS Computation")

            st.warning(
                "No GIS tool execution was recorded."
            )

    # ---------------------------------------------------------
    # 4. Evidence collection
    # ---------------------------------------------------------
    with st.container(border=True):
        if state.observations:
            st.markdown("### ✓ 4. Evidence Collected")

            st.markdown(
                "The agent received structured observations from "
                "the executed GIS tools."
            )

            evidence_count = 0

            for observation in state.observations:
                if isinstance(observation, dict):
                    tool_name = observation.get(
                        "tool",
                        observation.get("name", observation.get("tool_name", "Unknown tool")),
                    )
                    output = observation.get(
                        "output",
                        observation.get("result", {}),
                    )
                else:
                    tool_name = getattr(observation, "tool_name", "Unknown tool")
                    output = getattr(observation, "result", {})

                if not isinstance(output, dict):
                    continue

                for field, value in output.items():
                    evidence_count += 1

                    if isinstance(value, float):
                        display_value = f"{value:.4f}"
                    else:
                        display_value = str(value)

                    st.markdown(
                        f"- `{field}` = `{display_value}` "
                        f"from `{tool_name}`"
                    )

            if evidence_count == 0:
                st.info(
                    "Tool observations were recorded, "
                    "but no structured fields were available."
                )
        else:
            st.markdown("### ○ 4. Evidence Collected")

            st.warning(
                "No tool observations were recorded."
            )

    # ---------------------------------------------------------
    # 5. Final answer + supporting evidence
    # ---------------------------------------------------------
    with st.container(border=True):
        if state.final_answer:
            st.markdown("### ✓ 5. Final Answer")

            st.markdown(
                "The agent generated a response using the "
                "available execution results."
            )

            st.markdown(
                f"> {state.final_answer}"
            )

            claim_field = identify_claim_field(state)

            if claim_field:
                supporting_evidence = find_supporting_evidence(
                    state,
                    claim_field,
                )
            else:
                supporting_evidence = []

            if supporting_evidence and claim_field:
                with st.expander(
                    "🔎 View supporting evidence",
                    expanded=False,
                ):
                    st.markdown(
                        "### Claim → Evidence → Tool"
                    )

                    st.caption(
                        "The evidence below was produced by "
                        "deterministic GIS tools executed during "
                        "this run."
                    )

                    st.markdown(
                        f"**Claim field:** `{claim_field}`"
                    )

                    for item in supporting_evidence:
                        value = item["value"]

                        if isinstance(value, float):
                            formatted_value = f"{value:.4f}"
                        else:
                            formatted_value = str(value)

                        st.markdown(
                            "**Evidence field**"
                        )

                        st.code(
                            item["field"],
                            language="text",
                        )

                        st.markdown(
                            "**Observed value**"
                        )

                        st.code(
                            formatted_value,
                            language="text",
                        )

                        st.markdown(
                            "**Source tool**"
                        )

                        st.code(
                            item["tool"],
                            language="text",
                        )

                        st.caption(
                            f"Observation #{item['observation_index']}"
                        )

                        st.success(
                            "✓ Evidence-supported"
                        )

                        st.divider()

        else:
            st.markdown("### ○ 5. Final Answer")

            st.warning(
                "No final answer was generated."
            )

    # ---------------------------------------------------------
    # Workflow completion
    # ---------------------------------------------------------
    completed = 1

    if state.tool_calls:
        completed += 1

    if state.tool_executions:
        completed += 1

    if state.observations:
        completed += 1

    if state.final_answer:
        completed += 1

    st.progress(
        completed / 5,
        text=(
            f"{completed}/5 workflow stages completed"
        ),
    )


def display_summary(state) -> None:
    """Display runtime summary metrics."""
    st.subheader("Run Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Steps", state.steps)

    with col2:
        st.metric("LLM Calls", len(state.llm_calls))

    with col3:
        st.metric("Tool Calls", len(state.tool_calls))

    with col4:
        st.metric(
            "Latency",
            f"{state.total_latency_ms / 1000:.2f} s",
        )

    total_tokens = sum(
        call.total_tokens or 0
        for call in state.llm_calls
    )

    if total_tokens:
        st.caption(f"Total tokens: {total_tokens:,}")


def display_evidence(state) -> None:
    """Display evidence returned by deterministic GIS tools."""
    st.subheader("Evidence")

    if not state.observations:
        st.info("No tool observations were returned.")
        return

    for observation in state.observations:
        result = observation.result

        if not isinstance(result, dict):
            with st.expander(
                f"Evidence from `{observation.tool_name}`",
                expanded=True,
            ):
                st.write(result)
            continue

        st.markdown(f"**Source:** `{observation.tool_name}`")

        preferred_fields = [
            ("cell_count", "Study Cells"),
            ("degraded_cells", "Degraded Cells"),
            ("hotspot_count", "Hotspot Cells"),
            ("mean_change", "Mean NDVI Change"),
            ("mean_ndvi_change", "Mean Hotspot NDVI Change"),
            ("minimum_change", "Minimum NDVI Change"),
            ("maximum_change", "Maximum NDVI Change"),
            ("crs", "CRS"),
        ]

        available_fields = [
            (field, label)
            for field, label in preferred_fields
            if field in result and result[field] is not None
        ]

        if available_fields:
            columns = st.columns(min(len(available_fields), 4))

            for index, (field, label) in enumerate(available_fields):
                with columns[index % len(columns)]:
                    value = result[field]

                    if isinstance(value, float):
                        value = f"{value:.4f}"

                    st.metric(label, value)

        with st.expander("View raw tool output", expanded=False):
            st.json(result)

        st.caption("✓ Evidence produced by deterministic GIS execution.")

def display_spatial_result(state) -> None:
    """Display a spatial visualization derived from the agent result."""
    st.subheader("Spatial Result")

    try:
        base_dir = Path(__file__).resolve().parent.parent
        candidates = [
            Path("data/synthetic/vegetation_grid.geojson"),
            Path("geoscout/data/synthetic/vegetation_grid.geojson"),
            base_dir / "data" / "synthetic" / "vegetation_grid.geojson",
        ]
        default_path = Path("data/synthetic/vegetation_grid.geojson")
        dataset_path = next((c for c in candidates if c.exists()), default_path)
        dataset = gpd.read_file(dataset_path)
    except Exception as exc:
        st.warning(
            f"Could not load the spatial dataset: {exc}"
        )
        return

    if dataset.empty:
        st.info(
            "The spatial dataset contains no features."
        )
        return

    dataset = dataset.copy()

    # ---------------------------------------------------------
    # Calculate NDVI change if it is not already present.
    # ---------------------------------------------------------
    if "ndvi_change" not in dataset.columns:
        dataset["ndvi_change"] = (
            dataset["current_ndvi"]
            - dataset["baseline_ndvi"]
        )

    threshold = -0.10

    dataset["is_hotspot"] = (
        dataset["ndvi_change"] <= threshold
    )

    # ---------------------------------------------------------
    # Identify the type of result requested by the user.
    # ---------------------------------------------------------
    claim_field = identify_claim_field(state)

    # ---------------------------------------------------------
    # Determine which cells should receive emphasis.
    # ---------------------------------------------------------
    dataset["is_result_cell"] = False

    result_label = "Study region"

    if claim_field in {
        "degraded_cells",
        "hotspot_count",
        "mean_ndvi_change",
    }:
        dataset["is_result_cell"] = (
            dataset["is_hotspot"]
        )

        result_label = (
            "Detected degradation hotspots"
        )

    elif claim_field == "minimum_change":
        minimum_value = dataset[
            "ndvi_change"
        ].min()

        dataset["is_result_cell"] = (
            dataset["ndvi_change"]
            == minimum_value
        )

        result_label = (
            "Minimum NDVI change"
        )

    elif claim_field == "maximum_change":
        maximum_value = dataset[
            "ndvi_change"
        ].max()

        dataset["is_result_cell"] = (
            dataset["ndvi_change"]
            == maximum_value
        )

        result_label = (
            "Maximum NDVI change"
        )

    elif claim_field == "mean_change":
        # The mean is a regional statistic, so there is
        # no single polygon that represents the result.
        result_label = (
            "Regional mean NDVI change"
        )

    elif claim_field == "cell_count":
        result_label = (
            "Study region"
        )

    elif claim_field == "crs":
        result_label = (
            "Study region / CRS"
        )

    # ---------------------------------------------------------
    # Create the map.
    # ---------------------------------------------------------
    min_x, min_y, max_x, max_y = (
        dataset.total_bounds
    )

    center_lat = (
        min_y + max_y
    ) / 2

    center_lon = (
        min_x + max_x
    ) / 2

    spatial_map = folium.Map(
        location=[
            center_lat,
            center_lon,
        ],
        zoom_start=13,
        tiles="OpenStreetMap",
    )

    # ---------------------------------------------------------
    # Add polygons.
    # ---------------------------------------------------------
    for _, row in dataset.iterrows():
        is_hotspot = bool(
            row["is_hotspot"]
        )

        is_result_cell = bool(
            row["is_result_cell"]
        )

        ndvi_change = float(
            row["ndvi_change"]
        )

        # Result cells receive stronger visual emphasis.
        if is_result_cell:
            fill_color = "#d62728"
            fill_opacity = 0.80
            line_weight = 3
        elif is_hotspot:
            fill_color = "#f5b7b1"
            fill_opacity = 0.45
            line_weight = 1
        else:
            fill_color = "#9ecae1"
            fill_opacity = 0.25
            line_weight = 1

        status = (
            "Detected hotspot"
            if is_hotspot
            else "No significant degradation"
        )

        popup_html = f"""
        <b>Cell:</b> {row["cell_id"]}<br>
        <b>Status:</b> {status}<br>
        <b>NDVI change:</b> {ndvi_change:.4f}<br>
        <b>Baseline NDVI:</b>
        {row["baseline_ndvi"]:.4f}<br>
        <b>Current NDVI:</b>
        {row["current_ndvi"]:.4f}
        """

        tooltip = (
            f'{row["cell_id"]} · '
            f'NDVI change: {ndvi_change:.4f}'
        )

        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=(
                lambda feature,
                color=fill_color,
                opacity=fill_opacity,
                weight=line_weight: {
                    "fillColor": color,
                    "color": "#333333",
                    "weight": weight,
                    "fillOpacity": opacity,
                }
            ),
            tooltip=tooltip,
            popup=folium.Popup(
                popup_html,
                max_width=300,
            ),
        ).add_to(spatial_map)

    # ---------------------------------------------------------
    # Render map.
    # ---------------------------------------------------------
    st_folium(
        spatial_map,
        width=None,
        height=500,
        returned_objects=[],
    )

    # ---------------------------------------------------------
    # Result interpretation.
    # ---------------------------------------------------------
    hotspot_count = int(
        dataset["is_hotspot"].sum()
    )

    result_count = int(
        dataset["is_result_cell"].sum()
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Study Cells",
            len(dataset),
        )

    with col2:
        if claim_field in {
            "degraded_cells",
            "hotspot_count",
            "mean_ndvi_change",
            "minimum_change",
            "maximum_change",
        }:
            st.metric(
                "Highlighted Cells",
                result_count,
            )
        else:
            st.metric(
                "Detected Hotspots",
                hotspot_count,
            )

    with col3:
        st.metric(
            "Threshold",
            f"≤ {threshold:.2f}",
        )

    st.caption(
        f"Map emphasis: {result_label}. "
        f"CRS: {dataset.crs}."
    )


def display_tool_trace(state) -> None:
    """Display detailed tool execution information."""
    st.subheader("Tool Trace")

    if not state.tool_calls:
        st.info("No GIS tools were executed.")
        return

    for index, tool_call in enumerate(state.tool_calls, start=1):
        execution = next(
            (
                item
                for item in state.tool_executions
                if item.tool_call_id == tool_call.tool_call_id
            ),
            None,
        )

        with st.expander(
            f"{index}. `{tool_call.tool_name}`",
            expanded=False,
        ):
            st.write("**Arguments**")
            st.json(tool_call.arguments)

            if execution:
                st.write("**Execution**")

                execution_data = {
                    "success": execution.success,
                    "latency_ms": round(execution.latency_ms, 2),
                }

                if execution.error:
                    execution_data["error"] = execution.error

                st.json(execution_data)


def display_evidence_grounding(state) -> None:
    """Display claims linked to their observed GIS evidence and source tools."""
    st.subheader("Evidence Grounding")

    if not state.observations:
        st.info("No tool evidence was collected during this run.")
        return

    st.caption(
        "Traceability view: each displayed claim is connected to an "
        "observed value returned by an executed deterministic GIS tool."
    )

    claim_templates = {
        "cell_count": (
            "The study region contains {value} cells."
        ),
        "degraded_cells": (
            "{value} cells experienced significant vegetation degradation."
        ),
        "hotspot_count": (
            "{value} cells were detected as degradation hotspots."
        ),
        "mean_change": (
            "The mean NDVI change across the study region was {value}."
        ),
        "mean_ndvi_change": (
            "The mean NDVI change among detected hotspots was {value}."
        ),
        "minimum_change": (
            "The minimum NDVI change observed was {value}."
        ),
        "maximum_change": (
            "The maximum NDVI change observed was {value}."
        ),
        "crs": (
            "The study region uses CRS {value}."
        ),
    }

    evidence_items = []

    for observation_index, observation in enumerate(
        state.observations,
        start=1,
    ):
        if isinstance(observation, dict):
            tool_name = observation.get(
                "tool",
                observation.get("name", observation.get("tool_name", "Unknown tool")),
            )
            output = observation.get(
                "output",
                observation.get("result", {}),
            )
        else:
            tool_name = getattr(observation, "tool_name", "Unknown tool")
            output = getattr(observation, "result", {})

        if not isinstance(output, dict):
            continue

        for field, value in output.items():
            if field not in claim_templates:
                continue

            evidence_items.append(
                {
                    "observation_index": observation_index,
                    "tool": tool_name,
                    "field": field,
                    "value": value,
                }
            )

    if not evidence_items:
        st.info(
            "The executed tools returned observations, but no "
            "supported claim fields were found."
        )
        return

    for index, item in enumerate(evidence_items, start=1):
        field = item["field"]
        value = item["value"]
        tool_name = item["tool"]
        observation_index = item["observation_index"]

        if isinstance(value, float):
            formatted_value = f"{value:.4f}"
        else:
            formatted_value = str(value)

        claim = claim_templates[field].format(
            value=formatted_value
        )

        with st.container(border=True):
            st.markdown(
                f"### Claim {index}"
            )

            st.markdown(
                f"**{claim}**"
            )

            st.markdown("")

            # Claim → Evidence
            st.markdown(
                "#### ↓ Evidence"
            )

            evidence_col1, evidence_col2 = st.columns(2)

            with evidence_col1:
                st.markdown("**Observed field**")
                st.code(
                    field,
                    language="text",
                )

            with evidence_col2:
                st.markdown("**Observed value**")
                st.code(
                    formatted_value,
                    language="text",
                )

            # Evidence → Tool
            st.markdown(
                "#### ↓ Source Tool"
            )

            st.code(
                tool_name,
                language="text",
            )

            st.caption(
                f"Observation #{observation_index}"
            )

            # Grounding status
            st.success(
                "✓ Evidence-supported"
            )

            st.caption(
                "The evidence shown here was returned by the "
                "executed GIS tool during this run."
            )


st.title("🌍 GeoScout")

st.markdown(
    "### An Evidence-Grounded Geospatial Research Agent"
)

st.markdown(
    """
GeoScout is a research prototype for exploring how language-model
agents can orchestrate deterministic geospatial analysis while keeping
the resulting answers traceable to executable GIS evidence.
"""
)

st.info(
    "Research prototype · Synthetic vegetation-change dataset · "
    "Deterministic GIS tools · Evidence-traceable execution"
)

with st.sidebar:
    st.header("About GeoScout")

    st.markdown(
        """
**GeoScout** explores an evidence-grounded architecture for
LLM-assisted geospatial research.

### Core workflow

1. Research question
2. Agent tool selection
3. Deterministic GIS execution
4. Evidence collection
5. Grounded answer
6. Spatial visualization

### Design principle

The language model handles interpretation
and tool orchestration.

Deterministic GIS functions produce
the measurable spatial evidence.
"""
    )

    st.divider()

    st.subheader("Dataset")

    st.markdown(
        """
**Type:** Synthetic

**Domain:** Vegetation change

**Spatial units:** 100 grid cells

**Comparison:** 2020 → 2025

**CRS:** EPSG:4326
"""
    )

    st.divider()

    st.subheader("Research scope")

    st.caption(
        "This interface demonstrates the GeoScout prototype "
        "and should not be interpreted as an independent "
        "scientific validation system."
    )

st.divider()

st.subheader("Research Question")

if "question_input" not in st.session_state:
    st.session_state.question_input = ""


def set_example_question() -> None:
    selected = st.session_state.get("example_select")
    if selected and selected != "Select an example...":
        st.session_state.question_input = selected


example_questions = [
    "How many cells experienced significant vegetation degradation?",
    "What is the mean NDVI change across the study region?",
    "What is the minimum NDVI change?",
    "How many cells are in the study region?",
    "What is the CRS of the study region?",
]

question = st.text_area(
    "Ask GeoScout a geospatial question",
    placeholder=(
        "Example: How many cells experienced significant "
        "vegetation degradation?"
    ),
    height=100,
    label_visibility="collapsed",
    key="question_input",
)

st.selectbox(
    "Example questions",
    ["Select an example..."] + example_questions,
    key="example_select",
    on_change=set_example_question,
)

run_analysis = st.button(
    "🔎 Run Geospatial Analysis",
    type="primary",
    use_container_width=True,
)

if run_analysis:
    if not question.strip():
        st.warning(
            "Please enter a research question before running the analysis."
        )
        st.stop()

    runner = GroqAgentRunner(
        max_steps=10
    )

    with st.spinner(
        "GeoScout is planning and executing the analysis..."
    ):
        try:
            state = runner.run(question.strip())
        except Exception as exc:
            st.error(f"GeoScout failed to run: {exc}")
            st.stop()

    st.divider()

    if state.status == "completed":
        st.success(
            "Analysis completed successfully."
        )
    elif state.status == "failed":
        st.error(
            "Analysis failed during execution."
        )
    else:
        st.warning(
            f"Analysis finished with status: {state.status}"
        )

    if state.final_answer:
        st.subheader("Answer")
        st.markdown(state.final_answer)

    if state.error:
        st.error(state.error)

    st.divider()

    with st.expander(
        "ℹ️ How GeoScout produced this result",
        expanded=False,
    ):
        st.markdown(
            """
GeoScout separates language-model reasoning from measurable
geospatial computation.

The agent selects from deterministic GIS tools. Those tools
operate on the study dataset and return structured observations.
The interface then exposes the resulting evidence, execution
trace, and spatial representation.

The final response should therefore be interpreted together
with the evidence and tool trace shown below.
"""
        )

    st.divider()

    display_agent_workflow(state)

    st.divider()

    display_evidence(state)

    st.divider()

    display_evidence_grounding(state)

    st.divider()

    display_spatial_result(state)

    st.divider()

    display_tool_trace(state)

    st.divider()

    with st.expander(
        "⚠️ Research limitations",
        expanded=False,
    ):
        st.markdown(
            """
### Current prototype limitations

- The demonstration uses a synthetic vegetation-change dataset.
- Evidence grounding is based on structured tool observations.
- The interface does not independently verify every natural-language
  claim made by the language model.
- Higher-order spatial interpretations are not comprehensively
  evaluated by the current benchmark.
- Some benchmark evidence requirements test evidence presence rather
  than independently verified ground truth.
- Results from the model comparison should not be interpreted as
  establishing that model scale alone caused performance differences.

For the full experimental methodology, benchmark design, results,
and caveats, see the GeoScout research report in the repository.
"""
        )

    st.divider()

    display_summary(state)
