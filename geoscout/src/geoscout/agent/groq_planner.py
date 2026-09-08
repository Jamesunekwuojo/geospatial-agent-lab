import json
from typing import Any

from groq import Groq

from geoscout.agent.llm import create_groq_client, get_model
from geoscout.agent.planner import PlannedAction, Planner
from geoscout.agent.tool_adapter import get_groq_tools

SYSTEM_PROMPT = """
You are GeoScout, an environmental geospatial research agent.

Your responsibility is to answer environmental and geospatial
questions by using the available deterministic GIS tools.

IMPORTANT RULES:

1. Do not invent spatial measurements.
2. Do not calculate GIS values yourself when a GIS tool can
   provide the evidence.
3. Use the available tools to obtain evidence.
4. Tool arguments must be appropriate for the user's question.
5. After receiving tool results, determine whether additional
   tools are necessary.
6. When sufficient evidence has been collected, provide a concise
   evidence-grounded answer.
7. Never claim that a spatial analysis was performed unless the
   corresponding tool was actually executed.
"""


class GroqPlanner(Planner):
    """LLM-powered planner using Groq GPT-OSS models."""

    def __init__(
        self,
        client: Groq | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client or create_groq_client()
        self.model = model or get_model()

    def plan(
        self,
        question: str,
        observations: list[Any],
    ) -> PlannedAction:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        if observations:
            observation_text = json.dumps(
                observations,
                default=str,
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Here are the observations already collected "
                        "from previous GIS tool executions:\n\n"
                        f"{observation_text}\n\n"
                        "Determine whether another tool is required. "
                        "If the evidence is sufficient, provide the "
                        "final answer."
                    ),
                }
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=get_groq_tools(),
            tool_choice="auto",
            temperature=0,
            max_completion_tokens=2048,
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]

            return PlannedAction(
                action_type="tool_call",
                tool_name=tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

        return PlannedAction(
            action_type="finish",
        )
