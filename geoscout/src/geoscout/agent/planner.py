from dataclasses import dataclass
from typing import Any


@dataclass
class PlannedAction:
    """Represents the next action selected by the agent."""

    action_type: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None


class Planner:
    """Base planner interface."""

    def plan(
        self,
        question: str,
        observations: list[Any],
    ) -> PlannedAction:
        raise NotImplementedError
