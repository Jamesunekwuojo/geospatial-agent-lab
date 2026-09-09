from geoscout.evaluation.evidence_requirements import (
    evaluate_semantic_evidence,
    get_concept_sources,
)


def test_semantic_concept_sources() -> None:
    sources = get_concept_sources("degraded_cell_count")
    tools = [s["tool"] for s in sources]
    assert "calculate_statistics" in tools
    assert "summarize_hotspots" in tools
    assert "detect_change_hotspots" in tools


def test_ge_001_concept_with_calculate_statistics() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "cell_count": 100,
                "degraded_cells": 9,
            },
        }
    ]

    requirements = [
        {
            "concept": "degraded_cell_count",
            "expected_value": 9,
        }
    ]

    result = evaluate_semantic_evidence(
        observations=observations,
        requirements=requirements,
    )

    assert result["grounded"]
    assert result["supported_count"] == 1
    assert result["unsupported_count"] == 0


def test_ge_001_concept_with_summarize_hotspots() -> None:
    observations = [
        {
            "tool_name": "summarize_hotspots",
            "result": {
                "threshold": -0.1,
                "hotspot_count": 9,
                "hotspot_cells": ["cell_03_03"],
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

    result = evaluate_semantic_evidence(
        observations=observations,
        requirements=requirements,
    )

    assert result["grounded"]
    assert result["supported_count"] == 1


def test_ge_001_concept_mismatch() -> None:
    observations = [
        {
            "tool_name": "summarize_hotspots",
            "result": {
                "hotspot_count": 5,
            },
        }
    ]

    requirements = [
        {
            "concept": "degraded_cell_count",
            "expected_value": 9,
        }
    ]

    result = evaluate_semantic_evidence(
        observations=observations,
        requirements=requirements,
    )

    assert not result["grounded"]
    assert result["supported_count"] == 0
    assert result["unsupported_count"] == 1
