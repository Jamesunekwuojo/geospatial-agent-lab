from typing import Any

from geoscout.evaluation.evidence import (
    compare_values,
)

EVIDENCE_CAPABILITIES: dict[
    str,
    set[str],
] = {
    "get_region": {
        "cell_count",
        "crs",
        "bounds",
    },
    "calculate_ndvi_change": {
        "cell_id",
        "baseline_ndvi",
        "current_ndvi",
        "ndvi_change",
    },
    "detect_change_hotspots": {
        "cell_id",
        "hotspot_count",
        "hotspot_cells",
        "ndvi_change",
    },
    "calculate_statistics": {
        "cell_count",
        "mean_change",
        "median_change",
        "minimum_change",
        "maximum_change",
        "degraded_cells",
    },
    "summarize_hotspots": {
        "threshold",
        "hotspot_count",
        "hotspot_cells",
        "mean_ndvi_change",
    },
}


def tool_can_provide(
    tool_name: str,
    field: str,
) -> bool:
    """Return whether a tool can provide a particular evidence field."""

    return field in EVIDENCE_CAPABILITIES.get(
        tool_name,
        set(),
    )


def find_capable_tools(
    field: str,
) -> list[str]:
    """Return all tools capable of producing a field."""

    return [
        tool_name
        for tool_name, fields
        in EVIDENCE_CAPABILITIES.items()
        if field in fields
    ]


def validate_capability_registry() -> dict[str, Any]:
    """Return basic information about the capability registry."""

    return {
        "tool_count": len(
            EVIDENCE_CAPABILITIES
        ),
        "field_count": sum(
            len(fields)
            for fields
            in EVIDENCE_CAPABILITIES.values()
        ),
        "tools": {
            tool: sorted(fields)
            for tool, fields
            in EVIDENCE_CAPABILITIES.items()
        },
    }


def evaluate_evidence_path(
    observations: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    tolerance: float = 0.0,
) -> dict[str, Any]:
    """
    Evaluate whether required evidence was obtained through
    any acceptable evidence-producing tool.
    """

    results = []

    for requirement in requirements:
        field = requirement["field"]
        expected = requirement.get(
            "expected_value"
        )

        acceptable_tools = requirement.get(
            "acceptable_tools"
        )

        matches = []

        for observation in observations:
            tool_name = observation[
                "tool_name"
            ]

            if acceptable_tools is not None:
                if tool_name not in acceptable_tools:
                    continue

            elif not tool_can_provide(
                tool_name,
                field,
            ):
                continue

            result = observation[
                "result"
            ]

            if not isinstance(
                result,
                dict,
            ):
                continue

            if field not in result:
                continue

            actual = result[field]

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

        results.append(
            {
                "field": field,
                "expected_value": expected,
                "supported": supported,
                "supporting_evidence": matches,
            }
        )

    supported_count = sum(
        item["supported"]
        for item in results
    )

    return {
        "requirement_count": len(
            results
        ),
        "supported_count": supported_count,
        "unsupported_count": (
            len(results)
            - supported_count
        ),
        "grounded": (
            len(results) > 0
            and supported_count == len(results)
        ),
        "requirements": results,
    }
