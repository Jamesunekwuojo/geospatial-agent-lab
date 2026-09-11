import json
from pathlib import Path

from geoscout.agent.groq_planner import (
    GroqAgentRunner,
)
from geoscout.evaluation.benchmark import (
    evaluate_multistep_task,
    load_benchmark,
    summarize_multistep_results,
)

BENCHMARK_PATH = Path("evaluation/benchmarks/geoscout_v2.json")


def main() -> None:

    tasks = load_benchmark(path=BENCHMARK_PATH)

    agent = GroqAgentRunner(
        max_steps=6,
    )

    results = []

    for task in tasks:
        print(f"Running {task['id']} ({task['difficulty']})...")

        result = evaluate_multistep_task(
            agent=agent,
            task=task,
        )

        results.append(result)

        status = "PASS" if result["success"] else "FAIL"

        print(f"  {status}")

        print(f"  Required: {result['required_tools']}")

        print(f"  Actual:   {result['actual_tools']}")

        print(f"  Failure:  {result['failure_type']}")

        print()

    summary = summarize_multistep_results(results)

    print("=" * 60)
    print("GeoScout Multi-Step Benchmark")
    print("=" * 60)

    print(f"Tasks: {summary['task_count']}")

    print(f"Required tool coverage: {summary['required_tool_coverage']:.2%}")

    print(f"Execution success rate: {summary['execution_success_rate']:.2%}")

    print(f"Task success rate: {summary['task_success_rate']:.2%}")

    print()
    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
