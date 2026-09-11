from geoscout.evaluation.numerical import (
    evaluate_numeric_answer,
    extract_numbers,
    value_matches,
)


def test_extract_numbers() -> None:
    text = "There are 9 degraded cells with a mean change of -0.023."

    numbers = extract_numbers(text)

    assert numbers == [
        9.0,
        -0.023,
    ]


def test_value_matches_exact() -> None:
    assert value_matches(
        actual=9,
        expected=9,
    )


def test_value_matches_tolerance() -> None:
    assert value_matches(
        actual=-0.021,
        expected=-0.023,
        tolerance=0.002,
    )


def test_value_does_not_match() -> None:
    assert not value_matches(
        actual=14,
        expected=9,
    )


def test_correct_numeric_answer() -> None:
    result = evaluate_numeric_answer(
        answer=("There are 9 degraded cells in the study region."),
        expected_values={
            "degraded_cells": 9,
        },
    )

    assert result["correct"] is True


def test_incorrect_numeric_answer() -> None:
    result = evaluate_numeric_answer(
        answer=("There are 14 degraded cells in the study region."),
        expected_values={
            "degraded_cells": 9,
        },
    )

    assert result["correct"] is False


def test_missing_numeric_answer() -> None:
    result = evaluate_numeric_answer(
        answer=("Vegetation degradation was observed across the study region."),
        expected_values={
            "degraded_cells": 9,
        },
    )

    assert result["correct"] is False
    assert "degraded_cells" in result["missing_values"]
