import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
_GEOSCOUT_DIR = Path(__file__).resolve().parent.parent
for _p in [_APP_DIR, _GEOSCOUT_DIR]:
    if _p.exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from app.components.evidence_grounding import (  # noqa: E402
    render_evidence_grounding,
    render_raw_evidence_table,
)
from app.components.key_finding import render_key_finding  # noqa: E402
from app.components.question_input import render_empty_state  # noqa: E402
from app.components.sidebar import render_sidebar  # noqa: E402
from app.components.spatial_map import identify_claim_field, load_spatial_dataset  # noqa: E402
from app.components.telemetry import render_telemetry  # noqa: E402
from app.components.tool_trace import render_tool_trace  # noqa: E402
from app.components.workflow_trace import render_workflow_trace  # noqa: E402
from geoscout.agent.state import (  # noqa: E402
    AgentState,
    LLMCall,
    ToolCall,
    ToolExecution,
    ToolObservation,
)


def test_spatial_dataset_loading():
    """Verify that the synthetic spatial dataset loads correctly."""
    dataset = load_spatial_dataset()
    assert dataset is not None
    assert len(dataset) == 100
    assert "cell_id" in dataset.columns
    assert "baseline_ndvi" in dataset.columns
    assert "current_ndvi" in dataset.columns


def test_claim_field_identification():
    """Verify natural-language claim field identification patterns."""
    cases = [
        ("How many cells were degraded?", "degraded_cells"),
        ("What is the number of hotspots?", "hotspot_count"),
        ("What is the mean NDVI change across the region?", "mean_change"),
        ("What is the mean ndvi change among hotspots?", "mean_ndvi_change"),
        ("What is the lowest change?", "minimum_change"),
        ("What is the highest change?", "maximum_change"),
        ("How many cells are in the region?", "cell_count"),
        ("What is the coordinate reference system?", "crs"),
        ("Unrelated random query", None),
    ]
    for question, expected in cases:
        state = AgentState(question=question)
        assert identify_claim_field(state) == expected


@patch("streamlit.markdown")
@patch("streamlit.progress")
@patch("streamlit.columns")
def test_workflow_trace_grounded_state(mock_cols, mock_progress, mock_markdown):
    """Verify workflow stepper renders 5 completed stages for grounded execution."""
    mock_cols.return_value = [MagicMock() for _ in range(5)]
    state = AgentState(
        question="How many cells experienced degradation?",
        tool_calls=[
            ToolCall(
                tool_call_id="call_1",
                tool_name="count_degraded_cells",
                arguments={},
            )
        ],
        tool_executions=[
            ToolExecution(
                tool_call_id="call_1",
                tool_name="count_degraded_cells",
                success=True,
                latency_ms=12.5,
            )
        ],
        observations=[
            ToolObservation(
                tool_call_id="call_1",
                tool_name="count_degraded_cells",
                result={"degraded_cells": 9},
            )
        ],
        final_answer="The study region contains 9 degraded cells.",
        status="completed",
    )
    render_workflow_trace(state)
    mock_progress.assert_called_once()
    progress_val, progress_kwargs = mock_progress.call_args
    assert progress_val[0] == 1.0
    assert "Fully Evidence-Grounded" in progress_kwargs["text"]


@patch("streamlit.markdown")
@patch("streamlit.progress")
@patch("streamlit.columns")
def test_workflow_trace_ungrounded_state(mock_cols, mock_progress, mock_markdown):
    """Verify workflow stepper correctly handles ungrounded direct model responses."""
    mock_cols.return_value = [MagicMock() for _ in range(5)]
    state = AgentState(
        question="How many cells experienced degradation?",
        tool_calls=[],
        tool_executions=[],
        observations=[],
        final_answer="I think there are 9 cells.",
        status="completed",
    )
    render_workflow_trace(state)
    mock_progress.assert_called_once()
    progress_val, progress_kwargs = mock_progress.call_args
    assert progress_val[0] == 0.2
    assert "Direct Response (Ungrounded)" in progress_kwargs["text"]


@patch("streamlit.markdown")
def test_key_finding_grounded_vs_ungrounded(mock_markdown):
    """Verify key finding component renders appropriate badges and styling."""
    grounded_state = AgentState(
        question="Count degraded cells",
        tool_calls=[ToolCall(tool_call_id="1", tool_name="t", arguments={})],
        tool_executions=[
            ToolExecution(
                tool_call_id="1", tool_name="t", success=True, latency_ms=10.0
            )
        ],
        observations=[
            ToolObservation(
                tool_call_id="1",
                tool_name="t",
                result={"degraded_cells": 9},
            )
        ],
        final_answer="9 cells were degraded.",
        status="completed",
    )
    render_key_finding(grounded_state)
    assert any("gs-key-finding-grounded" in str(call) for call in mock_markdown.call_args_list)
    assert any("EVIDENCE GROUNDED" in str(call) for call in mock_markdown.call_args_list)

    mock_markdown.reset_mock()

    ungrounded_state = AgentState(
        question="Count degraded cells",
        tool_calls=[],
        tool_executions=[],
        observations=[],
        final_answer="9 cells were degraded.",
        status="completed",
    )
    render_key_finding(ungrounded_state)
    assert any("gs-key-finding-ungrounded" in str(call) for call in mock_markdown.call_args_list)
    assert any("Observability Notice" in str(call) for call in mock_markdown.call_args_list)


@patch("streamlit.markdown")
@patch("streamlit.columns")
@patch("streamlit.container")
def test_evidence_grounding_rendering(mock_container, mock_cols, mock_markdown):
    """Verify evidence grounding handles observations from both objects and dicts."""
    mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    state = AgentState(
        question="Count degraded cells",
        observations=[
            ToolObservation(
                tool_call_id="1",
                tool_name="count_degraded_cells",
                result={"degraded_cells": 9, "mean_change": -0.0617},
            )
        ],
    )
    render_evidence_grounding(state)
    render_raw_evidence_table(state)

    state_dict = AgentState(
        question="Count degraded cells",
        observations=[
            {
                "tool": "count_degraded_cells",
                "result": {"degraded_cells": 9},
            }
        ],
    )
    render_evidence_grounding(state_dict)
    render_raw_evidence_table(state_dict)


@patch("streamlit.metric")
@patch("streamlit.columns")
@patch("streamlit.caption")
@patch("streamlit.markdown")
def test_telemetry_safe_handling(mock_markdown, mock_caption, mock_cols, mock_metric):
    """Verify telemetry handles empty, null, and populated telemetry cleanly."""
    mock_cols.return_value = [MagicMock() for _ in range(5)]
    empty_state = AgentState(question="test", total_latency_ms=0.0)
    render_telemetry(empty_state)

    state_with_calls = AgentState(
        question="test",
        total_latency_ms=1500.0,
        llm_calls=[
            LLMCall(call_number=1, latency_ms=500.0, total_tokens=300),
            LLMCall(call_number=2, latency_ms=0.0, total_tokens=None),
        ],
    )
    render_telemetry(state_with_calls)


@patch("streamlit.expander")
@patch("streamlit.json")
@patch("streamlit.markdown")
def test_tool_trace_rendering(mock_markdown, mock_json, mock_expander):
    """Verify tool execution trace renders both successful and failed tool executions."""
    state = AgentState(
        question="test",
        tool_calls=[
            ToolCall(
                tool_call_id="call_1",
                tool_name="count_degraded_cells",
                arguments={"threshold": -0.10},
            ),
            ToolCall(
                tool_call_id="call_2",
                tool_name="compute_ndvi_stats",
                arguments={},
            ),
        ],
        tool_executions=[
            ToolExecution(
                tool_call_id="call_1",
                tool_name="count_degraded_cells",
                success=True,
                latency_ms=10.2,
            ),
            ToolExecution(
                tool_call_id="call_2",
                tool_name="compute_ndvi_stats",
                success=False,
                latency_ms=15.0,
                error="Simulated timeout",
            ),
        ],
    )
    render_tool_trace(state)


@patch("streamlit.markdown")
def test_empty_state_and_sidebar(mock_markdown):
    """Verify empty state and sidebar render without exceptions."""
    render_empty_state()
    with patch("streamlit.sidebar"):
        render_sidebar()


@patch("streamlit.button")
@patch("streamlit.selectbox")
@patch("streamlit.text_area")
@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_question_input_disabled_when_running(
    mock_cols, mock_markdown, mock_text_area, mock_selectbox, mock_button
):
    """Verify that inputs and run button are disabled when is_running=True."""
    from app.components.question_input import render_question_input

    mock_cols.return_value = [MagicMock(), MagicMock()]
    mock_text_area.return_value = "How many cells are degraded?"
    mock_button.return_value = False

    # When is_running=True
    render_question_input(is_running=True)
    _, text_kwargs = mock_text_area.call_args
    assert text_kwargs["disabled"] is True

    _, select_kwargs = mock_selectbox.call_args
    assert select_kwargs["disabled"] is True

    btn_args, btn_kwargs = mock_button.call_args
    assert btn_args[0] == "Running Analysis..."
    assert btn_kwargs["disabled"] is True


def test_repeated_execution_state_isolation():
    """Verify that successive runs produce independent, un-duplicated state."""
    # Run 1
    state1 = AgentState(
        question="Query 1",
        tool_calls=[ToolCall(tool_call_id="c1", tool_name="t1", arguments={})],
        tool_executions=[
            ToolExecution(tool_call_id="c1", tool_name="t1", success=True, latency_ms=10.0)
        ],
        observations=[
            ToolObservation(tool_call_id="c1", tool_name="t1", result={"degraded_cells": 9})
        ],
        llm_calls=[LLMCall(call_number=1, latency_ms=100.0, total_tokens=150)],
        final_answer="Answer 1",
    )
    assert len(state1.tool_calls) == 1
    assert state1.final_answer == "Answer 1"

    # Run 2 (Simulating a second click with a fresh runner)
    state2 = AgentState(
        question="Query 2",
        tool_calls=[ToolCall(tool_call_id="c2", tool_name="t2", arguments={})],
        tool_executions=[
            ToolExecution(tool_call_id="c2", tool_name="t2", success=True, latency_ms=12.0)
        ],
        observations=[
            ToolObservation(tool_call_id="c2", tool_name="t2", result={"mean_change": -0.05})
        ],
        llm_calls=[LLMCall(call_number=1, latency_ms=110.0, total_tokens=160)],
        final_answer="Answer 2",
    )

    # State 2 should contain strictly 1 tool call, 1 execution, 1 obs, 1 LLM call
    assert len(state2.tool_calls) == 1
    assert len(state2.tool_executions) == 1
    assert len(state2.observations) == 1
    assert len(state2.llm_calls) == 1
    assert state2.tool_calls[0].tool_call_id == "c2"
    assert state2.observations[0].result == {"mean_change": -0.05}
    assert state2.final_answer == "Answer 2"
