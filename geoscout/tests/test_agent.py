from geoscout.agent import GeoScoutAgent, MockGeoPlanner


def test_agent_completes_successfully():
    agent = GeoScoutAgent(
        planner=MockGeoPlanner()
    )

    state = agent.run(
        "Which areas experienced significant vegetation deterioration?"
    )

    assert state.status == "completed"


def test_agent_selects_hotspot_tool():
    agent = GeoScoutAgent(
        planner=MockGeoPlanner()
    )

    state = agent.run(
        "Which areas experienced significant vegetation deterioration?"
    )

    assert len(state.tool_calls) == 1
    assert (
        state.tool_calls[0].tool_name
        == "detect_change_hotspots"
    )


def test_agent_uses_expected_threshold():
    agent = GeoScoutAgent(
        planner=MockGeoPlanner()
    )

    state = agent.run(
        "Which areas experienced significant vegetation deterioration?"
    )

    assert (
        state.tool_calls[0].arguments["threshold"]
        == -0.10
    )


def test_agent_finds_nine_hotspots():
    agent = GeoScoutAgent(
        planner=MockGeoPlanner()
    )

    state = agent.run(
        "Which areas experienced significant vegetation deterioration?"
    )

    result = state.observations[0].result

    assert len(result) == 9
