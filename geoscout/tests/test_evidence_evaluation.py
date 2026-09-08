from geoscout.evaluation.evidence import (
    classify_grounded_failure,
    evaluate_evidence,
    evaluate_grounded_correctness,
    get_tool_field_value,
)


def test_get_tool_field_value() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "cell_count": 100,
                "degraded_cells": 9,
            },
        }
    ]

    value = get_tool_field_value(
        observations=observations,
        tool_name="calculate_statistics",
        field="degraded_cells",
    )

    assert value == 9


def test_evidence_is_grounded() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "cell_count": 100,
                "degraded_cells": 9,
            },
        }
    ]

    result = evaluate_evidence(
        observations=observations,
        requirements=[
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            }
        ],
    )

    assert result["grounded"] is True
    assert result["supported_count"] == 1


def test_evidence_is_not_grounded() -> None:
    observations = [
        {
            "tool_name": "get_region",
            "result": {
                "cell_count": 100,
            },
        }
    ]

    result = evaluate_evidence(
        observations=observations,
        requirements=[
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            }
        ],
    )

    assert result["grounded"] is False
    assert result["supported_count"] == 0


def test_multiple_evidence_requirements() -> None:
    observations = [
        {
            "tool_name": "get_region",
            "result": {
                "cell_count": 100,
            },
        },
        {
            "tool_name": "calculate_statistics",
            "result": {
                "degraded_cells": 9,
            },
        },
    ]

    result = evaluate_evidence(
        observations=observations,
        requirements=[
            {
                "tool": "get_region",
                "field": "cell_count",
                "expected_value": 100,
            },
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            },
        ],
    )

    assert result["grounded"] is True
    assert result["supported_count"] == 2
    

def test_grounded_correct_answer() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "degraded_cells": 9,
            },
        }
    ]

    result = evaluate_grounded_correctness(
        answer="There are 9 degraded cells.",
        observations=observations,
        requirements=[
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            }
        ],
    )

    assert result["evidence_supported"] is True
    assert result["answer_correct"] is True
    assert result["grounded_correct"] is True


def test_correct_answer_but_missing_evidence() -> None:
    observations = [
        {
            "tool_name": "get_region",
            "result": {
                "cell_count": 100,
            },
        }
    ]

    result = evaluate_grounded_correctness(
        answer="There are 9 degraded cells.",
        observations=observations,
        requirements=[
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            }
        ],
    )

    assert result["evidence_supported"] is False
    assert result["answer_correct"] is True
    assert result["grounded_correct"] is False


def test_evidence_correct_but_answer_wrong() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "degraded_cells": 9,
            },
        }
    ]

    result = evaluate_grounded_correctness(
        answer="There are 14 degraded cells.",
        observations=observations,
        requirements=[
            {
                "tool": "calculate_statistics",
                "field": "degraded_cells",
                "expected_value": 9,
            }
        ],
    )

    assert result["evidence_supported"] is True
    assert result["answer_correct"] is False
    assert result["grounded_correct"] is False


def test_failure_classification() -> None:
    assert (
        classify_grounded_failure(
            evidence_supported=True,
            answer_correct=True,
        )
        == "none"
    )

    assert (
        classify_grounded_failure(
            evidence_supported=False,
            answer_correct=True,
        )
        == "ungrounded_answer"
    )

    assert (
        classify_grounded_failure(
            evidence_supported=True,
            answer_correct=False,
        )
        == "answer_factual_error"
    )

    assert (
        classify_grounded_failure(
            evidence_supported=False,
            answer_correct=False,
        )
        == "evidence_and_answer_error"
    )