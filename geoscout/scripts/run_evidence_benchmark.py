import json
from pathlib import Path

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.evidence import (
    evaluate_evidence,
    observations_from_state,
)

BENCHMARK_PATH = Path(
    "evaluation/benchmarks/"
    "geoscout_evidence_ground_truth.json"
)


def load_benchmark(
    path: Path,
) -> list[dict]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main() -> None:
    tasks = load_benchmark(
        BENCHMARK_PATH
    )

    agent = GroqAgentRunner(
        max_steps=6
    )

    results = []

    for task in tasks:
        print(
            f"Running {task['id']}..."
        )

        state = agent.run(
            task["question"]
        )

        observations = observations_from_state(
            state
        )

        evaluation = evaluate_evidence(
            observations=observations,
            requirements=task[
                "required_evidence"
            ],
        )

        result = {
            "task_id": task["id"],
            "question": task["question"],
            "status": state.status,
            "final_answer": state.final_answer,
            **evaluation,
        }

        results.append(result)

        status = (
            "PASS"
            if evaluation["grounded"]
            else "FAIL"
        )

        print(f"  {status}")

        print(
            f"  Evidence: "
            f"{evaluation['supported_count']}/"
            f"{evaluation['evidence_count']}"
        )

        print(
            f"  Tools: "
            f"{[call.tool_name for call in state.tool_calls]}"
        )

        print(
            f"  Answer: "
            f"{state.final_answer}"
        )

        print()

    total = len(results)

    grounded = sum(
        result["grounded"]
        for result in results
    )

    grounding_rate = (
        grounded / total
        if total
        else 0.0
    )

    print("=" * 60)
    print(
        "GeoScout Evidence Grounding Benchmark"
    )
    print("=" * 60)

    print(
        f"Tasks: {total}"
    )

    print(
        f"Grounded: {grounded}"
    )

    print(
        f"Ungrounded: {total - grounded}"
    )

    print(
        f"Evidence grounding rate: "
        f"{grounding_rate:.2%}"
    )


if __name__ == "__main__":
    main()
