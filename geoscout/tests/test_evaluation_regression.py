from geoscout.evaluation.claims import (
    evaluate_semantic_claims,
)
from geoscout.evaluation.evidence import (
    evaluate_semantic_evidence,
)


def test_ge001_regression() -> None:
    """
    Regression test for the original false-negative case.

    The agent uses summarize_hotspots instead of
    calculate_statistics, but obtains valid evidence
    for the degraded-cell count.
    """

    observations = [
        {
            "tool_name": "summarize_hotspots",
            "result": {
                "threshold": -0.1,
                "hotspot_count": 9,
                "hotspot_cells": [
                    "cell_03_03",
                    "cell_03_04",
                    "cell_03_05",
                ],
                "mean_ndvi_change": -0.206,
            },
        }
    ]

    requirements = [
        {
            "concept": "degraded_cell_count",
            "expected_value": 9,
        }
    ]

    claims = [
        {
            "concept": "degraded_cell_count",
            "expected_value": 9,
        }
    ]

    evidence = evaluate_semantic_evidence(
        observations=observations,
        requirements=requirements,
    )

    claims_result = evaluate_semantic_claims(
        claims=claims,
        observations=observations,
    )

    assert evidence["grounded"]
    assert claims_result["grounded"]


def test_qualitative_answer_correctness_epsg() -> None:
    from geoscout.evaluation.evidence import (
        qualitative_values_appear_in_answer,
    )

    expected_values = ["EPSG:4326"]

    assert qualitative_values_appear_in_answer(
        "The coordinate system is EPSG:4326.",
        expected_values,
    )
    assert not qualitative_values_appear_in_answer(
        "The coordinate system is EPSG:3857.",
        expected_values,
    )
