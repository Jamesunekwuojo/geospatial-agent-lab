import json
from pathlib import Path
from typing import Any

from geoscout.agent.groq_planner import GroqAgentRunner
from geoscout.evaluation.claims import (
    evaluate_semantic_claims,
)
from geoscout.evaluation.evidence import (
    evaluate_semantic_evidence,
)
from geoscout.evaluation.failure_analysis import (
    analyze_result,
    summarize_failures,
)
from geoscout.evaluation.performance import (
    summarize_performance,
)

BENCHMARK_PATH = Path(
    "evaluation/benchmarks/"
    "geoscout_evidence_v2.json"
)

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


def extract_expected_tools(
    task: dict[str, Any],
) -> list[str]:
    """
    Extract one representative tool from the semantic
    evidence rules for trajectory analysis.

    This metric is diagnostic only. It does not determine
    whether the evidence path is valid.
    """

    from geoscout.evaluation.evidence_requirements import (
        SEMANTIC_EVIDENCE_RULES,
    )

    tools = []

    for requirement in task.get(
        "required_evidence",
        [],
    ):
        concept = requirement["concept"]

        rules = SEMANTIC_EVIDENCE_RULES.get(
            concept,
            [],
        )

        for rule in rules:
            tool = rule["tool"]

            if tool not in tools:
                tools.append(tool)

    return tools


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
        print(
            f"[{model}] "
            f"Running {task['id']}..."
        )

        state = agent.run(
            task["question"]
        )

        observations = [
            {
                "tool_name": observation.tool_name,
                "result": observation.result,
            }
            for observation in state.observations
        ]

        # --------------------------------------------------
        # 1. Semantic evidence evaluation
        # --------------------------------------------------

        evidence_evaluation = (
            evaluate_semantic_evidence(
                observations=observations,
                requirements=task[
                    "required_evidence"
                ],
            )
        )

        # --------------------------------------------------
        # 2. Semantic claim evaluation
        # --------------------------------------------------

        claim_evaluation = (
            evaluate_semantic_claims(
                claims=task.get(
                    "expected_claims",
                    [],
                ),
                observations=observations,
            )
        )

        # --------------------------------------------------
        # 3. Numerical answer correctness
        # --------------------------------------------------

        answer_correct = (
            evaluate_answer_correctness(
                state.final_answer,
                task,
            )
        )

        # --------------------------------------------------
        # 4. Grounded correctness
        # --------------------------------------------------

        grounded_correct = (
            evidence_evaluation["grounded"]
            and claim_evaluation["grounded"]
            and answer_correct
        )

        performance = summarize_performance(
            state
        )

        expected_tools = (
            extract_expected_tools(task)
        )

        actual_tools = [
            call.tool_name
            for call in state.tool_calls
        ]

        result = {
            "model": model,
            "task_id": task["id"],
            "category": task["category"],
            "difficulty": task["difficulty"],
            "question": task["question"],

            "status": state.status,
            "final_answer": state.final_answer,

            "expected_tools": expected_tools,
            "actual_tools": actual_tools,

            "tool_call_arguments": [
                {
                    "tool_name": call.tool_name,
                    "arguments": call.arguments,
                }
                for call in state.tool_calls
            ],

            "tool_execution_errors": (
                state.tool_execution_errors
            ),

            "evidence_evaluation": (
                evidence_evaluation
            ),

            "claim_evaluation": (
                claim_evaluation
            ),

            "evidence_supported": (
                evidence_evaluation[
                    "grounded"
                ]
            ),

            "answer_correct": (
                answer_correct
            ),

            "grounded_correct": (
                grounded_correct
            ),

            "performance": performance,
        }

        # Diagnostic failure analysis
        analyzed = analyze_result(
            result
        )

        result.update(
            {
                "primary_failure": (
                    analyzed[
                        "primary_failure"
                    ]
                ),
                "trajectory_analysis": (
                    analyzed[
                        "trajectory_analysis"
                    ]
                ),
            }
        )

        results.append(result)

        status = (
            "PASS"
            if grounded_correct
            else "FAIL"
        )

        print(
            f"  {status} | "
            f"evidence="
            f"{evidence_evaluation['grounded']} | "
            f"claims="
            f"{claim_evaluation['grounded']} | "
            f"answer="
            f"{answer_correct} | "
            f"latency="
            f"{performance['total_latency_ms']:.1f}ms"
        )

    return results


def evaluate_answer_correctness(
    answer: str | None,
    task: dict[str, Any],
) -> bool:
    """
    Evaluate whether the answer contains the expected
    factual values.

    This remains intentionally lightweight for now.
    """

    if not answer:
        return False

    expected_claims = task.get(
        "expected_claims",
        [],
    )

    from geoscout.evaluation.numerical import (
        evaluate_numeric_answer,
    )

    expected_values = {}

    for claim in expected_claims:
        expected = claim.get(
            "expected_value"
        )

        if expected is None:
            continue

        concept = claim["concept"]

        expected_values[concept] = expected

    if not expected_values:
        return True

    numerical = evaluate_numeric_answer(
        answer=answer,
        expected_values=expected_values,
    )

    return numerical["correct"]


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

    grounded = sum(
        result["grounded_correct"]
        for result in results
    )

    answer_correct = sum(
        result["answer_correct"]
        for result in results
    )

    evidence_supported = sum(
        result["evidence_supported"]
        for result in results
    )

    claim_grounded = sum(
        result[
            "claim_evaluation"
        ]["grounded"]
        for result in results
    )

    total_latency = sum(
        result["performance"][
            "total_latency_ms"
        ]
        for result in results
    )

    total_tool_calls = sum(
        result["performance"][
            "tool_call_count"
        ]
        for result in results
    )

    total_llm_calls = sum(
        result["performance"][
            "llm_call_count"
        ]
        for result in results
    )

    total_tokens = sum(
        result["performance"][
            "total_tokens"
        ]
        for result in results
    )

    return {
        "model": model,
        "task_count": total,

        "grounded_correctness": (
            grounded / total
        ),

        "answer_correctness": (
            answer_correct / total
        ),

        "evidence_support_rate": (
            evidence_supported / total
        ),

        "claim_groundedness": (
            claim_grounded / total
        ),

        "mean_latency_ms": (
            total_latency / total
        ),

        "mean_tool_calls": (
            total_tool_calls / total
        ),

        "mean_llm_calls": (
            total_llm_calls / total
        ),

        "mean_total_tokens": (
            total_tokens / total
        ),
    }


def main() -> None:

    tasks = load_benchmark(
        BENCHMARK_PATH
    )

    all_results = []
    summaries = []

    for model in MODELS:

        results = evaluate_model(
            model=model,
            tasks=tasks,
        )

        all_results.extend(
            results
        )

        summary = summarize_model(
            model=model,
            results=results,
        )

        summaries.append(
            summary
        )

        failure_summary = (
            summarize_failures(
                results
            )
        )

        print()
        print(
            f"Failure analysis: {model}"
        )

        for failure, count in (
            failure_summary[
                "failure_counts"
            ].items()
        ):
            print(
                f"  {failure}: {count}"
            )

        print()

    output_dir = Path(
        "evaluation/results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "model_comparison_v2.json"
    )

    output = {
        "experiment": (
            "GPT-OSS 20B vs GPT-OSS 120B"
        ),
        "benchmark": str(
            BENCHMARK_PATH
        ),
        "evaluation_version": "semantic-v2",
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
    print(
        "GeoScout Model Comparison v2"
    )
    print("=" * 70)

    for summary in summaries:

        print()

        print(
            f"Model: "
            f"{summary['model']}"
        )

        print(
            f"Grounded correctness: "
            f"{summary['grounded_correctness']:.2%}"
        )

        print(
            f"Answer correctness: "
            f"{summary['answer_correctness']:.2%}"
        )

        print(
            f"Evidence support: "
            f"{summary['evidence_support_rate']:.2%}"
        )

        print(
            f"Claim groundedness: "
            f"{summary['claim_groundedness']:.2%}"
        )

        print(
            f"Mean latency: "
            f"{summary['mean_latency_ms']:.2f} ms"
        )

        print(
            f"Mean tool calls: "
            f"{summary['mean_tool_calls']:.2f}"
        )

        print(
            f"Mean LLM calls: "
            f"{summary['mean_llm_calls']:.2f}"
        )

        print(
            f"Mean tokens: "
            f"{summary['mean_total_tokens']:.2f}"
        )

    print()
    print(
        "Detailed results saved to:"
    )
    print(output_path)


if __name__ == "__main__":
    main()
