from collections import Counter
from typing import Any

FAILURE_TYPES = {
    "none",
    "tool_selection_error",
    "argument_error",
    "missing_required_tool",
    "tool_execution_error",
    "ungrounded_answer",
    "answer_factual_error",
    "evidence_and_answer_error",
    "inefficient_trajectory",
    "agent_failure",
}


def classify_tool_selection(
    expected_tools: list[str],
    actual_tools: list[str],
) -> str:
    """
    Determine whether the agent selected the required tools.
    """

    if not actual_tools:
        return "agent_failure"

    if actual_tools == expected_tools:
        return "none"

    if set(expected_tools).issubset(set(actual_tools)):
        return "inefficient_trajectory"

    if not set(actual_tools).intersection(
        set(expected_tools)
    ):
        return "tool_selection_error"

    return "missing_required_tool"


def classify_arguments(
    expected_arguments: dict[str, Any],
    actual_arguments: dict[str, Any],
) -> str:
    """
    Compare expected and actual tool arguments.
    """

    for key, expected in expected_arguments.items():
        actual = actual_arguments.get(key)

        if actual != expected:
            return "argument_error"

    return "none"


def analyze_trajectory(
    expected_tools: list[str],
    actual_tools: list[str],
    expected_arguments: dict[str, Any] | None = None,
    actual_arguments: dict[str, Any] | None = None,
    tool_execution_errors: list[str] | None = None,
) -> dict[str, Any]:
    """
    Analyze an agent trajectory against expected behavior.
    """

    expected_arguments = expected_arguments or {}
    actual_arguments = actual_arguments or {}
    tool_execution_errors = (
        tool_execution_errors or []
    )

    if tool_execution_errors:
        failure_type = "tool_execution_error"

    else:
        failure_type = classify_tool_selection(
            expected_tools=expected_tools,
            actual_tools=actual_tools,
        )

        if failure_type == "none":
            failure_type = classify_arguments(
                expected_arguments=expected_arguments,
                actual_arguments=actual_arguments,
            )

    return {
        "failure_type": failure_type,
        "expected_tools": expected_tools,
        "actual_tools": actual_tools,
        "expected_arguments": expected_arguments,
        "actual_arguments": actual_arguments,
        "tool_execution_errors": tool_execution_errors,
    }


def analyze_tool_path(
    required_concepts: list[str],
    actual_tools: list[str],
) -> dict[str, Any]:
    """
    Diagnose tool usage without treating a prescribed tool
    as the only valid evidence path.
    """

    from geoscout.evaluation.evidence_requirements import (
        SEMANTIC_EVIDENCE_RULES,
    )

    capable_tools = set()

    for concept in required_concepts:
        for rule in SEMANTIC_EVIDENCE_RULES.get(
            concept,
            [],
        ):
            capable_tools.add(
                rule["tool"]
            )

    actual_tool_set = set(
        actual_tools
    )

    capable_used = (
        actual_tool_set
        & capable_tools
    )

    if not actual_tools:
        status = "no_tool_used"

    elif not capable_used:
        status = "no_capable_tool_used"

    else:
        status = "capable_tool_used"

    return {
        "status": status,
        "capable_tools": sorted(
            capable_tools
        ),
        "actual_tools": actual_tools,
        "capable_tools_used": sorted(
            capable_used
        ),
    }


def analyze_result(
    result: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine trajectory, evidence, and answer evaluation
    into a single diagnostic result.
    """

    performance = result.get(
        "performance",
        {},
    )

    actual_tools = result.get(
        "tool_calls",
        [],
    )

    expected_tools = result.get(
        "expected_tools",
        [],
    )

    expected_arguments = result.get(
        "expected_arguments",
        {},
    )

    actual_arguments = result.get(
        "actual_arguments",
        {},
    )

    trajectory = analyze_trajectory(
        expected_tools=expected_tools,
        actual_tools=actual_tools,
        expected_arguments=expected_arguments,
        actual_arguments=actual_arguments,
        tool_execution_errors=result.get(
            "tool_execution_errors",
            [],
        ),
    )

    evidence_supported = result.get(
        "evidence_supported",
        False,
    )
    answer_correct = result.get(
        "answer_correct",
        False,
    )
    tool_errors = result.get(
        "tool_execution_errors",
        [],
    )

    if tool_errors:
        primary_failure = "tool_execution_error"

    elif not evidence_supported and not answer_correct:
        primary_failure = "evidence_and_answer_error"

    elif not evidence_supported:
        primary_failure = "ungrounded_answer"

    elif not answer_correct:
        primary_failure = "answer_factual_error"

    else:
        primary_failure = "none"

    return {
        **result,
        "primary_failure": primary_failure,
        "trajectory_analysis": trajectory,
        "tool_call_count": performance.get(
            "tool_call_count",
            len(actual_tools),
        ),
        "llm_call_count": performance.get(
            "llm_call_count",
            0,
        ),
        "total_latency_ms": performance.get(
            "total_latency_ms",
            0.0,
        ),
        "total_tokens": performance.get(
            "total_tokens",
            0,
        ),
    }



def summarize_failures(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Produce aggregate failure statistics.
    """

    analyzed = [
        analyze_result(result)
        for result in results
    ]

    counts = Counter(
        result["primary_failure"]
        for result in analyzed
    )

    total = len(analyzed)

    failures = total - counts.get(
        "none",
        0,
    )

    return {
        "task_count": total,
        "successful_tasks": counts.get(
            "none",
            0,
        ),
        "failed_tasks": failures,
        "success_rate": (
            counts.get("none", 0) / total
            if total
            else 0.0
        ),
        "failure_rate": (
            failures / total
            if total
            else 0.0
        ),
        "failure_counts": dict(
            counts
        ),
        "analyzed_results": analyzed,
    }
