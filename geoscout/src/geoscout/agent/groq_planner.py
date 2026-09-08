import json
from pathlib import Path
from typing import Any

from groq import Groq

from geoscout.agent.llm import create_groq_client, get_model
from geoscout.agent.serialization import serialize_tool_result
from geoscout.agent.state import (
    AgentState,
    LLMCall,
    ToolCall,
    ToolExecution,
    ToolObservation,
)
from geoscout.agent.tool_adapter import get_groq_tools
from geoscout.evaluation.trajectory import save_trajectory
from geoscout.tools import execute_tool
from geoscout.utils.timing import timer

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
9. Supply only arguments explicitly defined in the selected tool's schema.
   Do not invent arguments such as baseline_year or current_year.
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
        state = AgentState(question=question)

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

        with timer() as total_timer:
            for step in range(1, self.max_steps + 1):
                state.steps = step

                with timer() as llm_timer:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=get_groq_tools(),
                        tool_choice="auto",
                        temperature=0,
                        max_completion_tokens=2084,
                    )

                usage = getattr(response, "usage", None)
                input_tokens = getattr(usage, "prompt_tokens", None)
                output_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)

                state.llm_calls.append(
                    LLMCall(
                        call_number=len(state.llm_calls) + 1,
                        latency_ms=llm_timer["elapsed_ms"],
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                    )
                )

                message = response.choices[0].message
                messages.append(message.model_dump(exclude_none=True))
                state.messages = messages

                if not message.tool_calls:
                    state.status = "completed"
                    state.final_answer = message.content or "The agent returned no final answer."
                    break

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name

                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as exc:
                        state.status = "failed"
                        state.error = f"Invalid JSON arguments for {tool_name}: {exc}"
                        break

                    state.tool_calls.append(
                        ToolCall(
                            tool_call_id=tool_call.id,
                            tool_name=tool_name,
                            arguments=arguments,
                        )
                    )

                    with timer() as tool_timer:
                        try:
                            result = execute_tool(tool_name, arguments)
                            serialized_result = serialize_tool_result(result)
                            tool_success = True
                            tool_error = None
                        except Exception as exc:
                            tool_success = False
                            tool_error = str(exc)
                            result = None
                            serialized_result = f"Tool execution failed: {exc}"

                    state.tool_executions.append(
                        ToolExecution(
                            tool_call_id=tool_call.id,
                            tool_name=tool_name,
                            latency_ms=tool_timer["elapsed_ms"],
                            success=tool_success,
                            error=tool_error,
                        )
                    )

                    if not tool_success:
                        state.tool_execution_errors.append(tool_error or "Unknown tool error")
                        state.status = "failed"
                        state.error = tool_error or "Tool execution failed."
                        break

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

                if state.status == "failed":
                    break
            else:
                state.status = "failed"
                state.error = "Agent reached the maximum number of steps."

        state.total_latency_ms = total_timer["elapsed_ms"]
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
