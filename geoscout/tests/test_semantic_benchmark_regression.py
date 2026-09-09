from geoscout.evaluation.claims import (
    evaluate_semantic_claims,
)
from geoscout.evaluation.evidence import (
    evaluate_semantic_evidence,
)


def test_valid_alternative_path_is_grounded() -> None:
    """
    Regression test:

    The benchmark may expect calculate_statistics,
    but summarize_hotspots can validly provide the
    degraded-cell count.
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
                    "cell_04_03",
                    "cell_04_04",
                    "cell_04_05",
                    "cell_05_03",
                    "cell_05_04",
                    "cell_05_05",
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
