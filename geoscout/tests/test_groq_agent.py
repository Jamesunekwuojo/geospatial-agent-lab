import pytest

from geoscout.agent.groq_planner import GroqAgentRunner


@pytest.mark.integration
def test_groq_agent_runs():

    agent = GroqAgentRunner(
        max_steps=5,
    )

    state = agent.run(
        "Which areas experienced significant vegetation deterioration?"
    )

    assert state.status == "completed"

    assert state.final_answer is not None

    assert len(state.tool_calls) >= 1

    assert any(
        call.tool_name == "detect_change_hotspots"
        for call in state.tool_calls
    )

    assert len(state.observations) >= 1
