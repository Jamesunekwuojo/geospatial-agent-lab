from typing import Any

from geoscout.tools import TOOLS


def get_groq_tools() -> list[dict[str, Any]]:
    """Convert GeoScout tool definitions to Groq tool schemas."""

    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            },
        }
        for tool in TOOLS
    ]
