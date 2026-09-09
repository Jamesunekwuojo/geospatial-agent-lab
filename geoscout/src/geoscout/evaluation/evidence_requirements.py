from typing import Any

SEMANTIC_EVIDENCE_RULES: dict[
    str,
    list[dict[str, str]],
] = {
    "degraded_cell_count": [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
        },
        {
            "tool": "summarize_hotspots",
            "field": "hotspot_count",
        },
        {
            "tool": "detect_change_hotspots",
            "field": "hotspot_count",
        },
    ],
    "study_cell_count": [
        {
            "tool": "get_region",
            "field": "cell_count",
        },
        {
            "tool": "calculate_statistics",
            "field": "cell_count",
        },
    ],
    "region_crs": [
        {
            "tool": "get_region",
            "field": "crs",
        },
    ],
    "overall_mean_ndvi_change": [
        {
            "tool": "calculate_statistics",
            "field": "mean_change",
        },
    ],
    "minimum_ndvi_change": [
        {
            "tool": "calculate_statistics",
            "field": "minimum_change",
        },
    ],
    "maximum_ndvi_change": [
        {
            "tool": "calculate_statistics",
            "field": "maximum_change",
        },
    ],
    "hotspot_mean_ndvi_change": [
        {
            "tool": "summarize_hotspots",
            "field": "mean_ndvi_change",
        },
    ],
    "hotspot_cells": [
        {
            "tool": "detect_change_hotspots",
            "field": "hotspot_cells",
        },
        {
            "tool": "summarize_hotspots",
            "field": "hotspot_cells",
        },
    ],
}


def get_concept_sources(
    concept: str,
) -> list[dict[str, str]]:
    """Return all tool/field mappings that satisfy a semantic concept."""

    return SEMANTIC_EVIDENCE_RULES.get(
        concept,
        [],
    )


def evaluate_semantic_requirement(
    observations: list[dict[str, Any]],
    requirement: dict[str, Any],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate a single evidence requirement, supporting either
    concept-based or explicit tool/field specifications.
    """

    expected = requirement.get(
        "expected_value"
    )

    if "concept" in requirement:
        concept = requirement["concept"]
        sources = get_concept_sources(concept)
        matches = []

        for source in sources:
            tool_name = source["tool"]
            field = source["field"]

            for observation in observations:
                if observation.get("tool_name") != tool_name:
                    continue

                result = observation.get("result")
                if not isinstance(result, dict):
                    continue

                if field not in result:
                    continue

                actual = result[field]

                from geoscout.evaluation.evidence import (
                    compare_values,
                )

                if compare_values(
                    actual=actual,
                    expected=expected,
                    tolerance=tolerance,
                ):
                    matches.append(
                        {
                            "tool": tool_name,
                            "field": field,
                            "actual_value": actual,
                        }
                    )

        supported = len(matches) > 0

        return {
            "concept": concept,
            "expected_value": expected,
            "supported": supported,
            "supporting_evidence": matches,
        }

    # Fallback to explicit tool and field requirement
    tool_name = requirement.get("tool", "")
    field = requirement.get("field", "")

    from geoscout.evaluation.evidence import (
        compare_values,
        get_tool_field_value,
    )

    actual = get_tool_field_value(
        observations=observations,
        tool_name=tool_name,
        field=field,
    )

    supported = compare_values(
        actual=actual,
        expected=expected,
        tolerance=tolerance,
    )

    return {
        "tool": tool_name,
        "field": field,
        "expected_value": expected,
        "actual_value": actual,
        "supported": supported,
        "supporting_evidence": (
            [{"tool": tool_name, "field": field, "actual_value": actual}]
            if supported
            else []
        ),
    }


def evaluate_semantic_evidence(
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate whether all required semantic concepts or tool-field requirements
    are satisfied by available tool observations.
    """

    results = [
        evaluate_semantic_requirement(
            observations=observations,
            requirement=req,
            tolerance=tolerance,
        )
        for req in requirements
    ]

    supported_count = sum(
        item["supported"]
        for item in results
    )

    grounded = (
        len(results) > 0
        and supported_count == len(results)
    )

    return {
        "grounded": grounded,
        "requirement_count": len(results),
        "supported_count": supported_count,
        "unsupported_count": (
            len(results)
            - supported_count
        ),
        "requirements": results,
    }
