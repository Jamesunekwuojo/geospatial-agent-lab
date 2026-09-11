import re
from typing import Any


def extract_numbers(text: str) -> list[float]:
    """Extract numeric values from an agent's final answer."""

    matches = re.findall(
        r"[-+]?(?:\d+\.\d+|\d+)",
        text,
    )

    return [float(value) for value in matches]


def value_matches(
    actual: float,
    expected: float,
    tolerance: float = 0.0,
) -> bool:
    """Check whether a numeric value matches ground truth."""

    return abs(actual - expected) <= tolerance


def find_matching_value(
    numbers: list[float],
    expected: float,
    tolerance: float = 0.0,
) -> float | None:
    """Find a number in the answer matching the expected value."""

    for number in numbers:
        if value_matches(
            actual=number,
            expected=expected,
            tolerance=tolerance,
        ):
            return number

    return None


def evaluate_numeric_answer(
    answer: str | None,
    expected_values: dict[str, float],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate whether expected numerical values appear
    correctly in the agent's final answer.
    """

    if not answer:
        return {
            "answer_available": False,
            "correct": False,
            "expected_values": expected_values,
            "matched_values": {},
            "missing_values": list(expected_values.keys()),
        }

    numbers = extract_numbers(answer)

    matched_values: dict[str, float] = {}
    missing_values: list[str] = []

    for name, expected in expected_values.items():
        matched = find_matching_value(
            numbers=numbers,
            expected=float(expected),
            tolerance=tolerance,
        )

        if matched is None:
            missing_values.append(name)
        else:
            matched_values[name] = matched

    correct = len(missing_values) == 0

    return {
        "answer_available": True,
        "correct": correct,
        "expected_values": expected_values,
        "extracted_numbers": numbers,
        "matched_values": matched_values,
        "missing_values": missing_values,
    }
