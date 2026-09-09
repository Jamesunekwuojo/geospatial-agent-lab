from geoscout.evaluation.claims import (
    evaluate_semantic_claims,
)


def test_unsupported_per_cell_ndvi_claim() -> None:
    """
    The hotspot summary provides cell IDs but does not
    provide individual NDVI changes.

    Therefore a claim about an individual cell's NDVI
    should not be considered grounded.
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

    claims = [
        {
            "concept": "overall_mean_ndvi_change",
            "expected_value": -0.23,
        }
    ]

    result = evaluate_semantic_claims(
        claims=claims,
        observations=observations,
    )

    assert not result["grounded"]
