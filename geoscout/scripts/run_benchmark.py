import json

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.benchmark import (
    evaluate_task,
    load_benchmark,
    summarize_results,
)


def main() -> None:

    tasks = load_benchmark()

    agent = GroqAgentRunner(
        max_steps=5,
    )

    results = []

    for task in tasks:
        print(f"Running {task['id']} ({task['difficulty']})...")

        result = evaluate_task(
            agent=agent,
            task=task,
        )

        results.append(result)

        status = "PASS" if result["success"] else "FAIL"

        print(
            f"  {status} | "
            f"tool={result['tool_selected']} | "
            f"expected={result['expected_tool']} | "
            f"failure={result['failure_type']}"
        )

    summary = summarize_results(results)

    print()
    print("=" * 60)
    print("GeoScout Benchmark")
    print("=" * 60)

    print(f"Tasks: {summary['task_count']}")

    print(f"Tool selection accuracy: {summary['tool_selection_accuracy']:.2%}")

    print(f"Argument accuracy: {summary['argument_accuracy']:.2%}")

    print(f"Execution success rate: {summary['execution_success_rate']:.2%}")

    print(f"Task success rate: {summary['task_success_rate']:.2%}")

    print()
    print("Failure analysis:")

    if summary["failure_counts"]:
        for failure_type, count in summary["failure_counts"].items():
            print(f"  {failure_type}: {count}")

    else:
        print("  No failures.")

    print()
    print("Summary JSON:")
    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
