from typing import Any

from geoscout.tools.geospatial import (
    calculate_ndvi_change,
    calculate_statistics,
    detect_change_hotspots,
    get_region,
    summarize_hotspots,
)

TOOL_FUNCTIONS = {
    "get_region": get_region,
    "calculate_ndvi_change": calculate_ndvi_change,
    "detect_change_hotspots": detect_change_hotspots,
    "calculate_statistics": calculate_statistics,
    "summarize_hotspots": summarize_hotspots,
}


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    """
    Execute a registered GeoScout tool.

    Parameters
    ----------
    tool_name:
        Name of the tool to execute.

    arguments:
        Arguments passed to the tool.

    Returns
    -------
    Any
        Tool result.

    Raises
    ------
    ValueError
        If the requested tool does not exist.
    """

    if tool_name not in TOOL_FUNCTIONS:
        available = ", ".join(TOOL_FUNCTIONS.keys())

        raise ValueError(f"Unknown tool '{tool_name}'. Available tools: {available}")

    function = TOOL_FUNCTIONS[tool_name]

    if arguments is None:
        arguments = {}

    return function(**arguments)
