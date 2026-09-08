from geoscout.agent.planner import Planner
from geoscout.agent.state import (
    AgentState,
    ToolCall,
    ToolObservation,
)
from geoscout.tools import execute_tool


class GeoScoutAgent:
    """Agent responsible for planning and executing GIS workflows."""

    def __init__(
        self,
        planner: Planner,
        max_steps: int = 10,
    ) -> None:
        self.planner = planner
        self.max_steps = max_steps

    def run(self, question: str) -> AgentState:
        state = AgentState(
            question=question,
        )

        for _ in range(self.max_steps):
            action = self.planner.plan(
                question=state.question,
                observations=state.observations,
            )

            if action.action_type == "finish":
                state.status = "completed"
                state.final_answer = self._build_answer(state)
                return state

            if action.action_type != "tool_call":
                state.status = "failed"
                state.final_answer = f"Unknown action type: {action.action_type}"
                return state

            if action.tool_name is None:
                state.status = "failed"
                state.final_answer = "Planner returned a tool action without a tool name."
                return state

            arguments = action.arguments or {}

            state.tool_calls.append(
                ToolCall(
                    tool_name=action.tool_name,
                    arguments=arguments,
                )
            )

            try:
                result = execute_tool(
                    action.tool_name,
                    arguments,
                )

            except Exception as exc:
                state.status = "failed"
                state.final_answer = f"Tool execution failed: {exc}"
                return state

            state.observations.append(
                ToolObservation(
                    tool_name=action.tool_name,
                    result=result,
                )
            )

        state.status = "failed"
        state.final_answer = "Agent reached the maximum number of steps."

        return state

    def _build_answer(
        self,
        state: AgentState,
    ) -> str:
        """Build a basic answer from the final observation."""

        if not state.observations:
            return "No evidence was collected."

        observation = state.observations[-1]

        if observation.tool_name == "detect_change_hotspots":
            result = observation.result

            return f"The analysis identified {len(result)} vegetation change hotspots."

        return "The analysis completed successfully using the available geospatial tools."
