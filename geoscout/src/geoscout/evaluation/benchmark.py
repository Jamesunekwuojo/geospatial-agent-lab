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


def classify_failure(
    tool_correct: bool,
    arguments_correct: bool,
    execution_success: bool,
) -> str:

    if not tool_correct:
        return "tool_selection_error"

    if not arguments_correct:
        return "argument_error"

    if not execution_success:
        return "tool_execution_error"

    return "none"


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
            "category": task.get(
                "category",
                "unknown",
            ),
            "difficulty": task.get(
                "difficulty",
                "unknown",
            ),
            "question": task["question"],
            "status": state.status,
            "tool_selected": None,
            "expected_tool": expected_tool,
            "actual_arguments": None,
            "expected_arguments": expected_arguments,
            "tool_correct": False,
            "arguments_correct": False,
            "execution_success": False,
            "success": False,
            "failure_type": "no_tool_call",
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

    execution_success = (
        state.status == "completed"
    )

    success = (
        tool_correct
        and arguments_correct
        and execution_success
    )

    failure_type = classify_failure(
        tool_correct=tool_correct,
        arguments_correct=arguments_correct,
        execution_success=execution_success,
    )

    return {
        "task_id": task["id"],
        "category": task.get(
            "category",
            "unknown",
        ),
        "difficulty": task.get(
            "difficulty",
            "unknown",
        ),
        "question": task["question"],
        "status": state.status,
        "tool_selected": first_call.tool_name,
        "expected_tool": expected_tool,
        "actual_arguments": first_call.arguments,
        "expected_arguments": expected_arguments,
        "tool_correct": tool_correct,
        "arguments_correct": arguments_correct,
        "execution_success": execution_success,
        "success": success,
        "failure_type": failure_type,
        "steps": state.steps,
        "error": state.error,
    }


def summarize_results(
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    if not results:
        return {
            "task_count": 0,
            "tool_selection_accuracy": 0.0,
            "argument_accuracy": 0.0,
            "execution_success_rate": 0.0,
            "task_success_rate": 0.0,
            "failure_counts": {},
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

    execution_success = sum(
        result["execution_success"]
        for result in results
    )

    successful = sum(
        result["success"]
        for result in results
    )

    failure_counts: dict[str, int] = {}

    for result in results:

        failure_type = result[
            "failure_type"
        ]

        if failure_type == "none":
            continue

        failure_counts[failure_type] = (
            failure_counts.get(
                failure_type,
                0,
            )
            + 1
        )

    return {
        "task_count": total,
        "tool_selection_accuracy": (
            tool_correct / total
        ),
        "argument_accuracy": (
            arguments_correct / total
        ),
        "execution_success_rate": (
            execution_success / total
        ),
        "task_success_rate": (
            successful / total
        ),
        "failure_counts": failure_counts,
    }