from geoscout.evaluation.claims import (
    claim_matches_evidence,
    evaluate_claims,
    evidence_from_observations,
)


def test_matching_numeric_claim() -> None:
    claim = {
        "tool": "calculate_statistics",
        "field": "degraded_cells",
        "expected_value": 9,
    }

    evidence = {
        "tool": "calculate_statistics",
        "field": "degraded_cells",
        "actual_value": 9,
    }

    assert claim_matches_evidence(
        claim,
        evidence,
    )


def test_wrong_numeric_claim() -> None:
    claim = {
        "tool": "calculate_statistics",
        "field": "degraded_cells",
        "expected_value": 10,
    }

    evidence = {
        "tool": "calculate_statistics",
        "field": "degraded_cells",
        "actual_value": 9,
    }

    assert not claim_matches_evidence(
        claim,
        evidence,
    )


def test_matching_string_claim() -> None:
    claim = {
        "tool": "get_region",
        "field": "crs",
        "expected_value": "EPSG:4326",
    }

    evidence = {
        "tool": "get_region",
        "field": "crs",
        "actual_value": "EPSG:4326",
    }

    assert claim_matches_evidence(
        claim,
        evidence,
    )


def test_claim_evaluation() -> None:
    claims = [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
            "expected_value": 9,
        },
        {
            "tool": "get_region",
            "field": "cell_count",
            "expected_value": 100,
        },
    ]

    evidence = [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
            "actual_value": 9,
        },
        {
            "tool": "get_region",
            "field": "cell_count",
            "actual_value": 100,
        },
    ]

    result = evaluate_claims(
        claims,
        evidence,
    )

    assert result["grounded"]
    assert result["claim_count"] == 2
    assert result["supported_claim_count"] == 2
    assert result["unsupported_claim_count"] == 0


def test_unsupported_claim() -> None:
    claims = [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
            "expected_value": 10,
        }
    ]

    evidence = [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
            "actual_value": 9,
        }
    ]

    result = evaluate_claims(
        claims,
        evidence,
    )

    assert not result["grounded"]
    assert result["supported_claim_count"] == 0
    assert result["unsupported_claim_count"] == 1


def test_evidence_from_observations() -> None:
    observations = [
        {
            "tool_name": "calculate_statistics",
            "result": {
                "cell_count": 100,
                "degraded_cells": 9,
            },
        }
    ]

    evidence = evidence_from_observations(
        observations
    )

    assert len(evidence) == 2

    assert {
        "tool": "calculate_statistics",
        "field": "degraded_cells",
        "actual_value": 9,
    } in evidence
