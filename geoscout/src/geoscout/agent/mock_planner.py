from typing import Any

from geoscout.agent.planner import PlannedAction, Planner


class MockGeoPlanner(Planner):
    """
    Deterministic planner used to validate the agent architecture
    before introducing an LLM.
    """

    def plan(
        self,
        question: str,
        observations: list[Any],
    ) -> PlannedAction:

        question_lower = question.lower()

        if not observations:

            if (
                "vegetation" in question_lower
                or "ndvi" in question_lower
                or "deterioration" in question_lower
                or "degradation" in question_lower
                or "change" in question_lower
            ):
                return PlannedAction(
                    action_type="tool_call",
                    tool_name="detect_change_hotspots",
                    arguments={
                        "threshold": -0.10,
                    },
                )

            return PlannedAction(
                action_type="tool_call",
                tool_name="get_region",
                arguments={},
            )

        return PlannedAction(
            action_type="finish",
        )
