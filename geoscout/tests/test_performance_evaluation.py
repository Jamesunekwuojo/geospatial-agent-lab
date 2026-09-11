from geoscout.agent.state import (
    AgentState,
    LLMCall,
    ToolCall,
    ToolExecution,
)
from geoscout.evaluation.performance import (
    summarize_performance,
)


def test_performance_summary() -> None:
    state = AgentState(question="Test question")

    state.total_latency_ms = 1500.0

    state.llm_calls = [
        LLMCall(
            call_number=1,
            latency_ms=500.0,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
        LLMCall(
            call_number=2,
            latency_ms=700.0,
            input_tokens=200,
            output_tokens=80,
            total_tokens=280,
        ),
    ]

    state.tool_calls = [
        ToolCall(
            tool_call_id="call_1",
            tool_name="get_region",
            arguments={},
        ),
        ToolCall(
            tool_call_id="call_2",
            tool_name="calculate_statistics",
            arguments={},
        ),
    ]

    state.tool_executions = [
        ToolExecution(
            tool_call_id="call_1",
            tool_name="get_region",
            latency_ms=10.0,
            success=True,
        ),
        ToolExecution(
            tool_call_id="call_2",
            tool_name="calculate_statistics",
            latency_ms=20.0,
            success=True,
        ),
    ]

    summary = summarize_performance(state)

    assert summary["total_latency_ms"] == 1500.0

    assert summary["llm_call_count"] == 2

    assert summary["tool_call_count"] == 2

    assert summary["total_input_tokens"] == 300

    assert summary["total_output_tokens"] == 130

    assert summary["total_tokens"] == 430

    assert summary["mean_llm_latency_ms"] == 600.0

    assert summary["mean_tool_latency_ms"] == 15.0

    assert summary["max_tool_latency_ms"] == 20.0
