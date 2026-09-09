from typing import Any

from geoscout.evaluation.evidence import (
    evaluate_semantic_evidence,
)


def normalize_text(value: str) -> str:
    """Normalize text for lightweight claim matching."""

    return " ".join(
        value.lower().strip().split()
    )


def claim_matches_evidence(
    claim: dict[str, Any],
    evidence: dict[str, Any],
) -> bool:
    """
    Determine whether a claim is supported by a
    specific piece of evidence.
    """

    claim_tool = claim.get("tool")
    claim_field = claim.get("field")

    evidence_tool = evidence.get("tool")
    evidence_field = evidence.get("field")

    if claim_tool != evidence_tool:
        return False

    if claim_field != evidence_field:
        return False

    expected = claim.get(
        "expected_value"
    )

    actual = evidence.get(
        "actual_value"
    )

    if expected is None:
        return actual is not None

    if isinstance(
        expected,
        (int, float),
    ) and isinstance(
        actual,
        (int, float),
    ):
        tolerance = claim.get(
            "tolerance",
            0.0,
        )

        return (
            abs(
                float(actual)
                - float(expected)
            )
            <= tolerance
        )

    # return normalize_text(
    #     str(actual)
    # ) == normalize_text(
    #     str(expected)
    # )
    
    if isinstance(
        expected,
        list,
    ) and isinstance(
        actual,
        list,
    ):
        return set(actual) == set(expected)

    return normalize_text(
        str(actual)
    ) == normalize_text(
    str(expected)
    )


def evaluate_claims(
    claims: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Evaluate whether every declared claim is supported
    by available evidence.
    """

    results = []

    for claim in claims:
        supporting_evidence = [
            item
            for item in evidence
            if claim_matches_evidence(
                claim,
                item,
            )
        ]

        supported = len(
            supporting_evidence
        ) > 0

        results.append(
            {
                "claim": claim,
                "supported": supported,
                "supporting_evidence": (
                    supporting_evidence
                ),
            }
        )

    supported_count = sum(
        item["supported"]
        for item in results
    )

    return {
        "claim_count": len(results),
        "supported_claim_count": (
            supported_count
        ),
        "unsupported_claim_count": (
            len(results)
            - supported_count
        ),
        "grounded": (
            len(results) > 0
            and supported_count == len(results)
        ),
        "claims": results,
    }


def evidence_from_observations(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert tool observations into field-level
    evidence records.
    """

    evidence = []

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

        for field, value in result.items():
            evidence.append(
                {
                    "tool": tool_name,
                    "field": field,
                    "actual_value": value,
                }
            )

    return evidence


def evaluate_semantic_claims(
    claims: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate claims using semantic evidence concepts.
    """

    requirements = [
        {
            "concept": claim["concept"],
            "expected_value": claim.get(
                "expected_value"
            ),
        }
        for claim in claims
    ]

    evidence_result = evaluate_semantic_evidence(
        observations=observations,
        requirements=requirements,
        tolerance=tolerance,
    )

    claim_results = []

    for claim, evidence in zip(
        claims,
        evidence_result["requirements"],
        strict=True,
    ):
        claim_results.append(
            {
                "claim": claim,
                "supported": evidence[
                    "supported"
                ],
                "supporting_evidence": evidence[
                    "supporting_evidence"
                ],
            }
        )

    supported_count = sum(
        item["supported"]
        for item in claim_results
    )

    return {
        "claim_count": len(claim_results),
        "supported_claim_count": (
            supported_count
        ),
        "unsupported_claim_count": (
            len(claim_results)
            - supported_count
        ),
        "grounded": (
            len(claim_results) > 0
            and supported_count
            == len(claim_results)
        ),
        "claims": claim_results,
    }
