from typing import Any

from geoscout.evaluation.evidence_requirements import (
    SEMANTIC_EVIDENCE_RULES,
)


def get_semantic_evidence_rules(
    concept: str,
) -> list[dict[str, str]]:
    """Return acceptable tool/field combinations for a concept."""

    return SEMANTIC_EVIDENCE_RULES.get(
        concept,
        [],
    )


def evaluate_semantic_evidence(
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate whether each semantic evidence requirement
    is supported by at least one valid observed tool result.
    """

    results = []

    for requirement in requirements:
        concept = requirement["concept"]
        expected = requirement.get(
            "expected_value"
        )

        rules = get_semantic_evidence_rules(
            concept
        )

        matches = []

        for observation in observations:
            tool_name = observation[
                "tool_name"
            ]

            result = observation[
                "result"
            ]

            if not isinstance(
                result,
                dict,
            ):
                continue

            for rule in rules:
                if rule["tool"] != tool_name:
                    continue

                field = rule["field"]

                if field not in result:
                    continue

                actual = result[field]

                if compare_values(
                    actual=actual,
                    expected=expected,
                    tolerance=tolerance,
                ):
                    matches.append(
                        {
                            "tool": tool_name,
                            "field": field,
                            "actual_value": actual,
                        }
                    )

        supported = len(matches) > 0

        results.append(
            {
                "concept": concept,
                "expected_value": expected,
                "supported": supported,
                "supporting_evidence": matches,
            }
        )

    supported_count = sum(
        item["supported"]
        for item in results
    )

    return {
        "requirement_count": len(results),
        "supported_count": supported_count,
        "unsupported_count": (
            len(results)
            - supported_count
        ),
        "grounded": (
            len(results) > 0
            and supported_count == len(results)
        ),
        "requirements": results,
    }


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
        return abs(float(actual) - float(expected)) <= tolerance

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
        expected = requirement.get("expected_value")

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

    grounded = all(item["supported"] for item in evidence_results)

    return {
        "grounded": grounded,
        "evidence_count": len(evidence_results),
        "supported_count": sum(item["supported"] for item in evidence_results),
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


def qualitative_values_appear_in_answer(
    answer: str | None,
    expected_values: list[Any],
) -> bool:
    """Check whether expected text or list values appear in an answer."""

    if not answer:
        return False

    normalized_answer = answer.casefold()

    for expected in expected_values:
        if isinstance(expected, str):
            values = [expected]
        elif isinstance(expected, list):
            values = [str(value) for value in expected]
        else:
            continue

        if not all(value.casefold() in normalized_answer for value in values):
            return False

    return True


def evaluate_grounded_correctness(
    answer: str | None,
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate whether the final answer is correct and supported by evidence.
    """

    from geoscout.evaluation.numerical import (
        evaluate_numeric_answer,
    )

    numeric_expected_values: dict[str, float] = {}
    qualitative_expected_values: list[Any] = []

    for requirement in requirements:
        expected = requirement.get("expected_value")

        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            key = requirement.get("concept") or requirement.get("field", "value")
            numeric_expected_values[key] = float(expected)
        elif expected is not None:
            qualitative_expected_values.append(expected)

    if any("concept" in req for req in requirements):
        evidence_result = evaluate_semantic_evidence(
            observations=observations,
            requirements=requirements,
            tolerance=tolerance,
        )
    else:
        evidence_result = evaluate_evidence(
            observations=observations,
            requirements=requirements,
            tolerance=tolerance,
        )

    numerical_result = evaluate_numeric_answer(
        answer=answer,
        expected_values=numeric_expected_values,
        tolerance=tolerance,
    )

    evidence_supported = evidence_result["grounded"]

    qualitative_answer_correct = qualitative_values_appear_in_answer(
        answer=answer,
        expected_values=qualitative_expected_values,
    )

    answer_correct = numerical_result["correct"] and qualitative_answer_correct

    grounded_correct = evidence_supported and answer_correct

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
        "qualitative_answer_correct": qualitative_answer_correct,
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
