from geoscout.evaluation.evidence_capabilities import (
    find_capable_tools,
    tool_can_provide,
    validate_capability_registry,
)


def test_statistics_capability() -> None:
    assert tool_can_provide(
        "calculate_statistics",
        "degraded_cells",
    )


def test_hotspot_summary_capability() -> None:
    assert tool_can_provide(
        "summarize_hotspots",
        "hotspot_count",
    )


def test_unknown_field() -> None:
    assert not tool_can_provide(
        "calculate_statistics",
        "area_hectares",
    )


def test_find_capable_tools() -> None:
    tools = find_capable_tools(
        "degraded_cells"
    )

    assert (
        "calculate_statistics"
        in tools
    )


def test_registry_validation() -> None:
    result = validate_capability_registry()

    assert result["tool_count"] == 5
    assert result["field_count"] > 0
