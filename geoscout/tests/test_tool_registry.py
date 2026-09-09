import pytest

from geoscout.tools import TOOLS, execute_tool
from geoscout.tools.schemas import DetectChangeHotspotsInput


def test_tool_registry_contains_expected_tools():
    names = {tool.name for tool in TOOLS}

    expected = {
        "get_region",
        "calculate_ndvi_change",
        "detect_change_hotspots",
        "calculate_statistics",
        "summarize_hotspots",
    }

    assert names == expected


def test_detect_hotspots_schema():
    schema = DetectChangeHotspotsInput(threshold=-0.20)

    assert schema.threshold == -0.20


def test_tool_executor():
    result = execute_tool(
        "detect_change_hotspots",
        {"threshold": -0.10},
    )

    assert len(result) == 9


def test_unknown_tool_fails():
    with pytest.raises(ValueError):
        execute_tool("does_not_exist")
