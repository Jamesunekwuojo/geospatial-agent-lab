import json
from pathlib import Path
from typing import Any

from geoscout.agent.groq_planner import GroqAgentRunner


DEFAULT_BENCHMARK = Path(
    "evaluation/benchmarks/geoscout_v1.json"
)


def load_benchmark(
    path: Path = DEFAULT_BENCHMARK,
) -> list[dict[str, Any]]:
    """Load benchmark tasks from JSON."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def arguments_match(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    """Check whether tool arguments match exactly."""

    return actual == expected


def evaluate_task(
    agent: GroqAgentRunner,
    task: dict[str, Any],
) -> dict[str, Any]:
    """Run and evaluate a single benchmark task."""

    state = agent.run(
        task["question"]
    )

    expected_tool = task["expected_tool"]
    expected_arguments = task.get(
        "expected_arguments",
        {},
    )

    if not state.tool_calls:
        return {
            "task_id": task["id"],
            "question": task["question"],
            "status": state.status,
            "tool_selected": None,
            "expected_tool": expected_tool,
            "tool_correct": False,
            "arguments_correct": False,
            "success": False,
            "steps": state.steps,
            "error": state.error,
        }

    first_call = state.tool_calls[0]

    tool_correct = (
        first_call.tool_name
        == expected_tool
    )

    arguments_correct = arguments_match(
        actual=first_call.arguments,
        expected=expected_arguments,
    )

    success = (
        tool_correct
        and arguments_correct
    )

    return {
        "task_id": task["id"],
        "question": task["question"],
        "status": state.status,
        "tool_selected": first_call.tool_name,
        "expected_tool": expected_tool,
        "actual_arguments": first_call.arguments,
        "expected_arguments": expected_arguments,
        "tool_correct": tool_correct,
        "arguments_correct": arguments_correct,
        "success": success,
        "steps": state.steps,
        "error": state.error,
    }
    

def summarize_results(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate aggregate benchmark metrics."""

    if not results:
        return {
            "task_count": 0,
            "tool_selection_accuracy": 0.0,
            "argument_accuracy": 0.0,
            "task_success_rate": 0.0,
        }

    total = len(results)

    tool_correct = sum(
        result["tool_correct"]
        for result in results
    )

    arguments_correct = sum(
        result["arguments_correct"]
        for result in results
    )

    successful = sum(
        result["success"]
        for result in results
    )

    return {
        "task_count": total,
        "tool_selection_accuracy": (
            tool_correct / total
        ),
        "argument_accuracy": (
            arguments_correct / total
        ),
        "task_success_rate": (
            successful / total
        ),
    }