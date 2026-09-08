import json
from pathlib import Path

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.evidence import (
    evaluate_grounded_correctness,
    observations_from_state,
)
from geoscout.evaluation.performance import (
    summarize_benchmark_performance,
    summarize_performance,
)

BENCHMARK_PATH = Path("evaluation/benchmarks/geoscout_evidence_ground_truth.json")


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

        observations = observations_from_state(state)

        evaluation = evaluate_grounded_correctness(
            answer=state.final_answer,
            observations=observations,
            requirements=task["required_evidence"],
        )
        performance = summarize_performance(state)

        result = {
            "task_id": task["id"],
            "question": task["question"],
            "status": state.status,
            "final_answer": state.final_answer,
            **evaluation,
            "performance": performance,
        }

        results.append(result)

        if evaluation["grounded_correct"]:
            status = "PASS"
        elif evaluation["answer_correct"]:
            status = "ANSWER_ONLY"
        elif evaluation["evidence_supported"]:
            status = "EVIDENCE_ONLY"
        else:
            status = "FAIL"

        print(f"  Status: {status}")

        print(f"  Evidence supported: {evaluation['evidence_supported']}")

        print(f"  Answer correct: {evaluation['answer_correct']}")

        print(f"  Grounded correct: {evaluation['grounded_correct']}")

        print(f"  Tools: {[call.tool_name for call in state.tool_calls]}")

        print(f"  Answer: {state.final_answer}")

        print()

    total = len(results)

    evidence_supported = sum(result["evidence_supported"] for result in results)

    answer_correct = sum(result["answer_correct"] for result in results)

    grounded_correct = sum(result["grounded_correct"] for result in results)
    performance_summary = summarize_benchmark_performance(
        [result["performance"] for result in results]
    )

    print("=" * 60)
    print("GeoScout Grounded Correctness Benchmark")
    print("=" * 60)

    print(f"Tasks: {total}")

    print(f"Evidence support rate: {evidence_supported / total:.2%}")

    print(f"Answer correctness: {answer_correct / total:.2%}")

    print(f"Grounded correctness: {grounded_correct / total:.2%}")

    print()
    print("Performance:")
    print(f"  Total latency: {performance_summary['total_latency_ms']:.2f} ms")
    print(f"  Mean task latency: {performance_summary['mean_task_latency_ms']:.2f} ms")
    print(f"  LLM calls: {performance_summary['llm_call_count']}")
    print(f"  Tool calls: {performance_summary['tool_call_count']}")
    print(f"  Tokens: {performance_summary['total_tokens']}")


if __name__ == "__main__":
    main()
