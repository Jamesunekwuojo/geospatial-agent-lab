import json
from pathlib import Path
from typing import Any

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.claims import (
    evaluate_claims,
    evidence_from_observations,
)
from geoscout.evaluation.evidence import (
    evaluate_grounded_correctness,
    observations_from_state,
)
from geoscout.evaluation.failure_analysis import summarize_failures
from geoscout.evaluation.performance import (
    summarize_performance,
)
from geoscout.tools.geospatial import (
    calculate_statistics,
    detect_change_hotspots,
    summarize_hotspots,
)

BENCHMARK_PATH = Path("evaluation/benchmarks/geoscout_evidence_v2.json")

MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]


def load_benchmark(
    path: Path,
) -> list[dict[str, Any]]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def resolve_ground_truth(
    requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve dynamic ground-truth values from deterministic GIS tools."""

    statistics = calculate_statistics()
    hotspot_summary = summarize_hotspots()
    hotspots = detect_change_hotspots()

    resolved = []

    for requirement in requirements:
        item = dict(requirement)

        if item.get("expected_value") is None:
            tool = item["tool"]
            field = item["field"]

            if tool == "calculate_statistics":
                item["expected_value"] = statistics[field]

            elif tool == "summarize_hotspots":
                item["expected_value"] = hotspot_summary[field]

            elif tool == "detect_change_hotspots":
                if field == "hotspot_count":
                    item["expected_value"] = len(hotspots)

                elif field == "hotspot_cells":
                    item["expected_value"] = hotspots["cell_id"].tolist()

        resolved.append(item)

    return resolved


def evaluate_model(
    model: str,
    tasks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    agent = GroqAgentRunner(
        model=model,
        max_steps=6,
    )

    results = []

    for task in tasks:
        print(f"[{model}] Running {task['id']}...")

        state = agent.run(task["question"])

        observations = observations_from_state(state)
        
        evidence = evidence_from_observations(
            observations
        )

        claim_evaluation = evaluate_claims(
            claims=task.get(
            "expected_claims",
            []
            ),
            evidence=evidence,
        )

        requirements = resolve_ground_truth(task["required_evidence"])

        evaluation = evaluate_grounded_correctness(
            answer=state.final_answer,
            observations=observations,
            requirements=requirements,
        )

        performance = summarize_performance(state)

        result = {
            "model": model,
            "task_id": task["id"],
            "question": task["question"],
            "status": state.status,
            "final_answer": state.final_answer,
            "tool_calls": [call.tool_name for call in state.tool_calls],
            "tool_call_arguments": [
                {
                    "tool_name": call.tool_name,
                    "arguments": call.arguments,
                }
                for call in state.tool_calls
            ],
            "expected_tools": list(
                dict.fromkeys(requirement["tool"] for requirement in requirements)
            ),
            "expected_arguments": task.get(
                "expected_arguments",
                {},
            ),
            "claim_evaluation": claim_evaluation,
            "actual_arguments": (state.tool_calls[0].arguments if state.tool_calls else {}),
            "tool_execution_errors": (state.tool_execution_errors),
            **evaluation,
            "performance": performance,
        }

        results.append(result)

        status = "PASS" if evaluation["grounded_correct"] else "FAIL"

        print(
            f"  {status} | "
            f"grounded="
            f"{evaluation['grounded_correct']} | "
            f"latency="
            f"{performance['total_latency_ms']:.1f}ms"
        )

    return results


def summarize_model(
    model: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(results)

    if total == 0:
        return {
            "model": model,
            "task_count": 0,
        }

    grounded_correct = sum(result["grounded_correct"] for result in results)

    answer_correct = sum(result["answer_correct"] for result in results)

    evidence_supported = sum(result["evidence_supported"] for result in results)

    total_latency = sum(result["performance"]["total_latency_ms"] for result in results)

    total_tool_calls = sum(result["performance"]["tool_call_count"] for result in results)

    total_llm_calls = sum(result["performance"]["llm_call_count"] for result in results)

    total_tokens = sum(result["performance"]["total_tokens"] for result in results)
    
    claim_grounded = sum(
    result[
        "claim_evaluation"
    ]["grounded"]
    for result in results
    )

    return {
        "model": model,
        "task_count": total,
        "grounded_correctness": (grounded_correct / total),
        "answer_correctness": (answer_correct / total),
        "evidence_support_rate": (evidence_supported / total),
        "mean_latency_ms": (total_latency / total),
        "mean_tool_calls": (total_tool_calls / total),
        "mean_llm_calls": (total_llm_calls / total),
        "mean_total_tokens": (total_tokens / total),
        "claim_groundedness": (
            claim_grounded / total
        ),
    }


def main() -> None:
    tasks = load_benchmark(BENCHMARK_PATH)

    all_results = []
    summaries = []

    for model in MODELS:
        results = evaluate_model(
            model=model,
            tasks=tasks,
        )

        all_results.extend(results)

        summary = summarize_model(
            model=model,
            results=results,
        )
        summary["failure_analysis"] = summarize_failures(results)
        summaries.append(summary)

        print()

    output_dir = Path("evaluation/results")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / "model_comparison_v1.json"

    output = {
        "experiment": ("GPT-OSS 20B vs GPT-OSS 120B"),
        "benchmark": str(BENCHMARK_PATH),
        "summaries": summaries,
        "results": all_results,
    }

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=" * 70)
    print("GeoScout Model Comparison")
    print("=" * 70)

    for summary in summaries:
        failure_summary = summary["failure_analysis"]

        print()
        print(f"Model: {summary['model']}")

        print(f"Grounded correctness: {summary['grounded_correctness']:.2%}")

        print(f"Answer correctness: {summary['answer_correctness']:.2%}")

        print(f"Evidence support: {summary['evidence_support_rate']:.2%}")

        print(f"Mean latency: {summary['mean_latency_ms']:.2f} ms")

        print(f"Mean tool calls: {summary['mean_tool_calls']:.2f}")

        print(f"Mean LLM calls: {summary['mean_llm_calls']:.2f}")

        print(f"Mean tokens: {summary['mean_total_tokens']:.2f}")

        print()
        print("Failure Analysis")
        print("-" * 40)

        print(f"Success rate: {failure_summary['success_rate']:.2%}")

        print(f"Failure rate: {failure_summary['failure_rate']:.2%}")

        for failure_type, count in sorted(failure_summary["failure_counts"].items()):
            print(f"  {failure_type}: {count}")

    print()
    print(f"Detailed results saved to:\n{output_path}")


if __name__ == "__main__":
    main()
