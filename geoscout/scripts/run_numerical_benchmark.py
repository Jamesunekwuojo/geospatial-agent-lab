import json
from pathlib import Path

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.numerical import (
    evaluate_numeric_answer,
)

BENCHMARK_PATH = Path("evaluation/benchmarks/geoscout_ground_truth.json")


def load_benchmark(
    path: Path,
) -> list[dict]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main() -> None:
    tasks = load_benchmark(BENCHMARK_PATH)

    agent = GroqAgentRunner(max_steps=6)

    results = []

    for task in tasks:
        print(f"Running {task['id']}...")

        state = agent.run(task["question"])

        evaluation = evaluate_numeric_answer(
            answer=state.final_answer,
            expected_values=task["expected_values"],
            tolerance=task.get(
                "tolerance",
                0.0,
            ),
        )

        result = {
            "task_id": task["id"],
            "question": task["question"],
            "final_answer": state.final_answer,
            "agent_status": state.status,
            **evaluation,
        }

        results.append(result)

        status = "PASS" if evaluation["correct"] else "FAIL"

        print(f"  {status}")
        print(f"  Expected: {evaluation['expected_values']}")
        print(f"  Matched:  {evaluation['matched_values']}")
        print(f"  Missing:  {evaluation['missing_values']}")
        print(f"  Answer:   {state.final_answer}")
        print()

    total = len(results)

    correct = sum(result["correct"] for result in results)

    accuracy = correct / total if total else 0.0

    summary = {
        "task_count": total,
        "correct": correct,
        "incorrect": total - correct,
        "numeric_answer_accuracy": accuracy,
    }

    print("=" * 60)
    print("GeoScout Numerical Ground-Truth Benchmark")
    print("=" * 60)

    print(f"Tasks: {total}")

    print(f"Correct: {correct}")

    print(f"Incorrect: {total - correct}")

    print(f"Numeric answer accuracy: {accuracy:.2%}")

    print()

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
