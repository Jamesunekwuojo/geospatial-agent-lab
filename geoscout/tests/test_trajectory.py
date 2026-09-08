import json

from geoscout.agent.state import (
    AgentState,
    ToolCall,
    ToolObservation,
)
from geoscout.evaluation.trajectory import (
    build_trajectory,
    save_trajectory,
)


def test_build_trajectory():

    state = AgentState(
        question=("Which areas experienced vegetation deterioration?"),
        status="completed",
        steps=2,
        final_answer=("The analysis identified 9 hotspots."),
    )

    state.tool_calls.append(
        ToolCall(
            tool_call_id="call_1",
            tool_name="detect_change_hotspots",
            arguments={
                "threshold": -0.10,
            },
        )
    )

    state.observations.append(
        ToolObservation(
            tool_call_id="call_1",
            tool_name="detect_change_hotspots",
            result={
                "hotspot_count": 9,
            },
        )
    )

    trajectory = build_trajectory(
        state=state,
        model="openai/gpt-oss-20b",
    )

    assert trajectory["model"] == "openai/gpt-oss-20b"

    assert trajectory["steps"] == 2

    assert trajectory["tool_calls"][0]["tool_name"] == "detect_change_hotspots"

    assert trajectory["observations"][0]["result"]["hotspot_count"] == 9


def test_save_trajectory(tmp_path):

    state = AgentState(
        question="Test question",
        status="completed",
        steps=1,
        final_answer="Test answer",
    )

    output_path = save_trajectory(
        state=state,
        model="openai/gpt-oss-20b",
        output_dir=tmp_path,
    )

    assert output_path.exists()

    data = json.loads(output_path.read_text())

    assert data["question"] == "Test question"

    assert data["final_answer"] == "Test answer"
