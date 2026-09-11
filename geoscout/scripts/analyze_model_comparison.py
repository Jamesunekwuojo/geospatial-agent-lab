import json
from collections import Counter
from pathlib import Path
from typing import Any

RESULT_PATH = Path("evaluation/results/model_comparison_v2.json")


def load_results() -> dict[str, Any]:
    with RESULT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def analyze_model(
    model: str,
    results: list[dict[str, Any]],
) -> None:
    total = len(results)

    grounded = sum(result["grounded_correct"] for result in results)

    answer_correct = sum(result["answer_correct"] for result in results)

    evidence_supported = sum(result["evidence_supported"] for result in results)

    claim_grounded = sum(result["claim_evaluation"]["grounded"] for result in results)

    failures = Counter()

    for result in results:
        if result["grounded_correct"]:
            failure = "none"
        else:
            failure = result.get(
                "primary_failure",
                "unknown",
            )

        failures[failure] += 1

    mean_latency = sum(result["performance"]["total_latency_ms"] for result in results) / total

    mean_tools = sum(result["performance"]["tool_call_count"] for result in results) / total

    mean_llm_calls = sum(result["performance"]["llm_call_count"] for result in results) / total

    mean_tokens = sum(result["performance"]["total_tokens"] for result in results) / total

    print()
    print("=" * 70)
    print(model)
    print("=" * 70)

    print(f"Tasks:                 {total}")

    print(f"Grounded correctness:  {grounded / total:.2%}")

    print(f"Answer correctness:    {answer_correct / total:.2%}")

    print(f"Evidence support:      {evidence_supported / total:.2%}")

    print(f"Claim groundedness:    {claim_grounded / total:.2%}")

    print(f"Mean latency:          {mean_latency:.2f} ms")

    print(f"Mean tool calls:       {mean_tools:.2f}")

    print(f"Mean LLM calls:        {mean_llm_calls:.2f}")

    print(f"Mean tokens:           {mean_tokens:.2f}")

    print()
    print("Failure breakdown")
    print("-" * 40)

    for failure, count in failures.most_common():
        print(f"{failure:<30} {count}")

    print()
    print("Failed tasks")
    print("-" * 40)

    for result in results:
        if result["grounded_correct"]:
            continue

        print(f"{result['task_id']}: {result['question']}")

        print(f"  Failure: {result.get('primary_failure')}")

        print(f"  Tools: {result.get('tool_calls')}")

        print(f"  Answer: {result.get('final_answer')}")

        print()


def main() -> None:
    data = load_results()

    results = data["results"]

    models = sorted({result["model"] for result in results})

    for model in models:
        model_results = [result for result in results if result["model"] == model]

        analyze_model(
            model=model,
            results=model_results,
        )


if __name__ == "__main__":
    main()
