import json
from pathlib import Path
from typing import Any

from groq import Groq

from geoscout.agent.llm import create_groq_client, get_model
from geoscout.agent.serialization import serialize_tool_result
from geoscout.agent.state import (
    AgentState,
    ToolCall,
    ToolObservation,
)
from geoscout.agent.tool_adapter import get_groq_tools
from geoscout.evaluation.trajectory import save_trajectory
from geoscout.tools import execute_tool

SYSTEM_PROMPT = """
You are GeoScout, an environmental geospatial research agent.

Your responsibility is to answer environmental and geospatial
questions by using the available deterministic GIS tools.

IMPORTANT RULES:

1. Do not invent spatial measurements.
2. Do not perform GIS calculations yourself when a GIS tool
   can provide the evidence.
3. Use the available tools to obtain evidence.
4. Tool arguments must be appropriate for the user's question.
5. After receiving tool results, determine whether additional
   tools are necessary.
6. When sufficient evidence has been collected, provide a concise
   evidence-grounded answer.
7. Never claim that a spatial analysis was performed unless the
   corresponding tool was actually executed.
8. Clearly distinguish evidence from interpretation.
"""


class GroqAgentRunner:
    """
    Executes the complete multi-turn Groq tool-calling loop.
    """

    def __init__(
        self,
        client: Groq | None = None,
        model: str | None = None,
        max_steps: int = 10,
    ) -> None:
        self.client = client or create_groq_client()
        self.model = model or get_model()
        self.max_steps = max_steps


    def run(self, question: str) -> AgentState:

        state = AgentState(
            question=question,
        )

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        state.messages = messages

        for step in range(1, self.max_steps + 1):

            state.steps = step

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=get_groq_tools(),
                tool_choice="auto",
                temperature=0,
                max_completion_tokens=2048,
            )

            message = response.choices[0].message

            assistant_message = message.model_dump(
                exclude_none=True
            )

            messages.append(
                assistant_message
            )

            state.messages = messages

            if not message.tool_calls:

                state.status = "completed"

                state.final_answer = (
                    message.content
                    or "The agent returned no final answer."
                )

                return state

            for tool_call in message.tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError as exc:
                    state.status = "failed"
                    state.error = (
                        f"Invalid JSON arguments for "
                        f"{tool_name}: {exc}"
                    )
                    return state
                
                recorded_call = ToolCall(
                    tool_call_id=tool_call.id,
                    tool_name=tool_name,
                    arguments=arguments,

                )

                state.tool_calls.append(
                    recorded_call
                )

                try:
                    result = execute_tool(
                        tool_name,
                        arguments,
                    )

                    serialized_result = (
                        serialize_tool_result(result)
                    )

                except Exception as exc:
                    error_message = (
                        f"Tool '{tool_name}' failed: "
                        f"{exc}"
                    )

                    state.tool_execution_errors.append(
                    error_message
                    )

                    state.status = "failed"
                    state.error = error_message

                    return state

                state.observations.append(
                    ToolObservation(
                        tool_call_id=tool_call.id,
                        tool_name=tool_name,
                        result=result,
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": serialized_result,
                    }
                )

            state.messages = messages

        state.status = "failed"
        state.error = (
            "Agent reached the maximum number of steps."
        )

        return state

    def run_and_save(
        self,
        question: str,
    ) -> tuple[AgentState, Path]:
        """Run the agent and persist its trajectory."""

        state = self.run(question)

        output_path = save_trajectory(
            state=state,
            model=self.model,
        )

        return state, output_path
