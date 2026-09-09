from typing import Any


def summarize_performance(
    state: Any,
) -> dict[str, Any]:
    """Summarize runtime and efficiency characteristics."""

    tool_latencies = [execution.latency_ms for execution in state.tool_executions]

    llm_latencies = [call.latency_ms for call in state.llm_calls]

    total_input_tokens = sum(call.input_tokens or 0 for call in state.llm_calls)

    total_output_tokens = sum(call.output_tokens or 0 for call in state.llm_calls)

    total_tokens = sum(call.total_tokens or 0 for call in state.llm_calls)

    return {
        "total_latency_ms": (state.total_latency_ms),
        "llm_call_count": len(state.llm_calls),
        "tool_call_count": len(state.tool_calls),
        "tool_execution_error_count": len(state.tool_execution_errors),
        "total_input_tokens": (total_input_tokens),
        "total_output_tokens": (total_output_tokens),
        "total_tokens": total_tokens,
        "mean_llm_latency_ms": (sum(llm_latencies) / len(llm_latencies) if llm_latencies else 0.0),
        "mean_tool_latency_ms": (
            sum(tool_latencies) / len(tool_latencies) if tool_latencies else 0.0
        ),
        "max_tool_latency_ms": (max(tool_latencies) if tool_latencies else 0.0),
    }


def summarize_benchmark_performance(
    performances: list[dict[str, Any]],
) -> dict[str, float | int]:
    """Aggregate performance measurements from benchmark tasks."""

    task_count = len(performances)
    total_latency_ms = sum(performance["total_latency_ms"] for performance in performances)

    return {
        "total_latency_ms": total_latency_ms,
        "mean_task_latency_ms": (total_latency_ms / task_count if task_count else 0.0),
        "llm_call_count": sum(performance["llm_call_count"] for performance in performances),
        "tool_call_count": sum(performance["tool_call_count"] for performance in performances),
        "total_tokens": sum(performance["total_tokens"] for performance in performances),
    }
