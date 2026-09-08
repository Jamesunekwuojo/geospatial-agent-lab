import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from geoscout.agent.state import AgentState

DEFAULT_OUTPUT_DIR = Path("evaluation/results")


def _serialize_value(value: Any) -> Any:
    """Convert common Python objects into JSON-safe values."""

    if value is None:
        return None

    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_serialize_value(item) for item in value]

    if hasattr(value, "to_dict"):
        try:
            return _serialize_value(value.to_dict())
        except Exception:
            return str(value)

    return value


def build_trajectory(
    state: AgentState,
    model: str,
) -> dict[str, Any]:
    """Convert an AgentState into a research trajectory."""

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model,
        "question": state.question,
        "status": state.status,
        "steps": state.steps,
        "tool_calls": [
            {
                "tool_call_id": call.tool_call_id,
                "tool_name": call.tool_name,
                "arguments": _serialize_value(call.arguments),
            }
            for call in state.tool_calls
        ],
        "observations": [
            {
                "tool_call_id": observation.tool_call_id,
                "tool_name": observation.tool_name,
                "result": _serialize_value(observation.result),
            }
            for observation in state.observations
        ],
        "final_answer": state.final_answer,
        "error": state.error,
    }


def save_trajectory(
    state: AgentState,
    model: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Save an agent trajectory to JSON."""

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    output_path = output_dir / f"trajectory_{timestamp}.json"

    trajectory = build_trajectory(
        state=state,
        model=model,
    )

    output_path.write_text(
        json.dumps(
            trajectory,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return output_path
