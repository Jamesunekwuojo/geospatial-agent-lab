from geoscout.evaluation.evidence import (
    evaluate_evidence,
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
