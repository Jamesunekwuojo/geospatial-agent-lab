from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A single tool invocation made by the agent."""

    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class ToolObservation:
    """The result returned by a tool."""

    tool_call_id: str
    tool_name: str
    result: Any


@dataclass
class AgentState:
    """State maintained throughout an agent trajectory."""

    question: str

    tool_calls: list[ToolCall] = field(default_factory=list)

    observations: list[ToolObservation] = field(default_factory=list)

    messages: list[dict[str, Any]] = field(default_factory=list)

    final_answer: str | None = None

    status: str = "running"

    steps: int = 0
    
    tool_execution_errors: list[str] = field(
    default_factory=list
    )

    error: str | None = None
