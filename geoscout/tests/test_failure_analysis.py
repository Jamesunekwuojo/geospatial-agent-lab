from geoscout.evaluation.failure_analysis import (
    analyze_trajectory,
    summarize_failures,
)


def test_correct_trajectory() -> None:
    result = analyze_trajectory(
        expected_tools=["calculate_statistics"],
        actual_tools=["calculate_statistics"],
    )

    assert result["failure_type"] == "none"


def test_tool_selection_error() -> None:
    result = analyze_trajectory(
        expected_tools=["calculate_statistics"],
        actual_tools=["get_region"],
    )

    assert result["failure_type"] == "tool_selection_error"


def test_missing_required_tool() -> None:
    result = analyze_trajectory(
        expected_tools=[
            "get_region",
            "calculate_statistics",
        ],
        actual_tools=["get_region"],
    )

    assert result["failure_type"] == "missing_required_tool"


def test_argument_error() -> None:
    result = analyze_trajectory(
        expected_tools=["detect_change_hotspots"],
        actual_tools=["detect_change_hotspots"],
        expected_arguments={"threshold": -0.10},
        actual_arguments={"threshold": -0.20},
    )

    assert result["failure_type"] == "argument_error"


def test_inefficient_trajectory() -> None:
    result = analyze_trajectory(
        expected_tools=["calculate_statistics"],
        actual_tools=[
            "get_region",
            "calculate_statistics",
        ],
    )

    assert result["failure_type"] == "inefficient_trajectory"


def test_failure_summary() -> None:
    results = [
        {
            "evidence_supported": True,
            "answer_correct": True,
            "tool_calls": ["calculate_statistics"],
            "expected_tools": ["calculate_statistics"],
            "performance": {
                "tool_call_count": 1,
                "llm_call_count": 1,
                "total_latency_ms": 100,
                "total_tokens": 100,
            },
        },
        {
            "evidence_supported": False,
            "answer_correct": False,
            "tool_calls": ["get_region"],
            "performance": {
                "tool_call_count": 1,
                "llm_call_count": 1,
                "total_latency_ms": 100,
                "total_tokens": 100,
            },
            "expected_tools": ["calculate_statistics"],
        },
    ]

    summary = summarize_failures(results)

    assert summary["task_count"] == 2
    assert summary["successful_tasks"] == 1
    assert summary["failed_tasks"] == 1
    assert summary["success_rate"] == 0.5


def test_analyze_result_uses_actual_tools():
    from geoscout.evaluation.failure_analysis import analyze_result

    result = {
        "expected_tools": [
            "calculate_statistics",
            "summarize_hotspots",
        ],
        "actual_tools": [
            "calculate_statistics",
        ],
        "expected_arguments": {},
        "actual_arguments": {},
        "tool_execution_errors": [],
        "evidence_supported": True,
        "answer_correct": True,
    }

    analyzed = analyze_result(result)

    trajectory = analyzed["trajectory_analysis"]

    assert trajectory["actual_tools"] == ["calculate_statistics"]

    assert trajectory["failure_type"] != "agent_failure"
