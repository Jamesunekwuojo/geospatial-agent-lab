from typing import Any


def get_tool_field_value(
    observations: list[dict[str, Any]],
    tool_name: str,
    field: str,
) -> Any:
    """Find a field produced by a specific tool."""

    for observation in observations:
        if observation["tool_name"] != tool_name:
            continue

        result = observation["result"]

        if isinstance(result, dict):
            if field in result:
                return result[field]

    return None


def compare_values(
    actual: Any,
    expected: Any,
    tolerance: float = 0.0,
) -> bool:
    """Compare scalar values with optional numeric tolerance."""

    if actual is None:
        return False

    if expected is None:
        return True

    if isinstance(
        actual,
        (int, float),
    ) and isinstance(
        expected,
        (int, float),
    ):
        return abs(
            float(actual) - float(expected)
        ) <= tolerance

    return actual == expected


def evaluate_evidence(
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Determine whether every required claim is supported
    by an observed tool result.
    """

    evidence_results = []

    for requirement in requirements:
        tool_name = requirement["tool"]
        field = requirement["field"]
        expected = requirement.get(
            "expected_value"
        )

        actual = get_tool_field_value(
            observations=observations,
            tool_name=tool_name,
            field=field,
        )

        supported = compare_values(
            actual=actual,
            expected=expected,
            tolerance=tolerance,
        )

        evidence_results.append(
            {
                "tool": tool_name,
                "field": field,
                "expected_value": expected,
                "actual_value": actual,
                "supported": supported,
            }
        )

    grounded = all(
        item["supported"]
        for item in evidence_results
    )

    return {
        "grounded": grounded,
        "evidence_count": len(
            evidence_results
        ),
        "supported_count": sum(
            item["supported"]
            for item in evidence_results
        ),
        "evidence": evidence_results,
    }


def observations_from_state(
    state: Any,
) -> list[dict[str, Any]]:
    """Convert AgentState observations into evaluator format."""

    return [
        {
            "tool_name": observation.tool_name,
            "result": observation.result,
        }
        for observation in state.observations
    ]


def evaluate_grounded_correctness(
    answer: str | None,
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
    
) -> dict[str, Any]:
    """
    Evaluate whether the final answer is numerically correct
    and supported by the agent's observed evidence.
    """

    from geoscout.evaluation.numerical import (
        evaluate_numeric_answer,
    )

    expected_values: dict[str, float] = {}

    for requirement in requirements:
        expected = requirement.get(
            "expected_value"
        )

        if expected is None:
            continue

        expected_values[
            requirement["field"]
        ] = expected

    evidence_result = evaluate_evidence(
        observations=observations,
        requirements=requirements,
        tolerance=tolerance,
    )

    numerical_result = evaluate_numeric_answer(
        answer=answer,
        expected_values=expected_values,
        tolerance=tolerance,
    )

    evidence_supported = (
        evidence_result["grounded"]
    )

    answer_correct = (
        numerical_result["correct"]
    )

    grounded_correct = (
        evidence_supported
        and answer_correct
    )
    
    failure_type = classify_grounded_failure(
    evidence_supported=evidence_supported,
    answer_correct=answer_correct,
    )

    return {
        "evidence_supported": evidence_supported,
        "answer_correct": answer_correct,
        "grounded_correct": grounded_correct,
        "failure_type": failure_type,
        "evidence": evidence_result,
        "numerical": numerical_result,
    }


def classify_grounded_failure(
    evidence_supported: bool,
    answer_correct: bool,
) -> str:
    """Classify grounded-answer failures."""

    if evidence_supported and answer_correct:
        return "none"

    if not evidence_supported and not answer_correct:
        return "evidence_and_answer_error"

    if not evidence_supported:
        return "ungrounded_answer"

    return "answer_factual_error"

