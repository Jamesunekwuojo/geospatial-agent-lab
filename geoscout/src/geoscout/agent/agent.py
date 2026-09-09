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

        for step in range(1, self.max_steps + 1):
            state.steps = step

            action = self.planner.plan(
                question=state.question,
                observations=[observation.result for observation in state.observations],
            )

            if action.action_type == "finish":
                state.status = "completed"

                state.final_answer = "The agent completed its analysis."

                return state

            if action.action_type != "tool_call":
                state.status = "failed"
                state.error = f"Unknown action type: {action.action_type}"
                return state

            if action.tool_name is None:
                state.status = "failed"
                state.error = "Planner returned a tool action without a tool name."
                return state

            arguments = action.arguments or {}

            tool_call = ToolCall(
                tool_call_id=f"local_call_{step}",
                tool_name=action.tool_name,
                arguments=arguments,
            )

            state.tool_calls.append(tool_call)

            try:
                result = execute_tool(
                    action.tool_name,
                    arguments,
                )

            except Exception as exc:
                state.status = "failed"
                state.error = str(exc)
                return state

            state.observations.append(
                ToolObservation(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=action.tool_name,
                    result=result,
                )
            )

        state.status = "failed"
        state.error = "Agent reached the maximum number of steps."

        return state
