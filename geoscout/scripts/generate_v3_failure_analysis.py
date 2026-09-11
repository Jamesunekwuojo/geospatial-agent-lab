import json
from pathlib import Path

RESULTS_PATH = Path("evaluation/results/model_comparison_v3.json")
OUTPUT_PATH = Path("evaluation/results/model_comparison_v3_failure_analysis.json")


def load_results():
    with RESULTS_PATH.open() as f:
        return json.load(f)


def main():
    data = load_results()

    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ]

    failure_analysis = {
        "experiment": data["experiment"],
        "source_artifact": str(RESULTS_PATH),
        "evaluation_version": data["evaluation_version"],
        "models": {},
        "comparative_findings": [],
        "methodological_notes": [
            (
                "The answer_correct metric should not be interpreted "
                "independently of the GE-010 evaluator caveat."
            ),
            (
                "Current claim_groundedness is not treated as an "
                "independent metric from semantic evidence support."
            ),
            (
                "Trajectory tool-path diagnostics are exploratory and "
                "are not authoritative task-failure indicators."
            ),
        ],
    }

    for model in models:
        results = [result for result in data["results"] if result["model"] == model]

        grounded_failures = [
            result["task_id"] for result in results if not result["grounded_correct"]
        ]

        evidence_failures = [
            result["task_id"] for result in results if not result["evidence_supported"]
        ]

        answer_failures = [result["task_id"] for result in results if not result["answer_correct"]]

        failure_analysis["models"][model] = {
            "task_count": len(results),
            "grounded_failure_count": len(grounded_failures),
            "grounded_failure_tasks": grounded_failures,
            "evidence_failure_count": len(evidence_failures),
            "evidence_failure_tasks": evidence_failures,
            "answer_failure_count": len(answer_failures),
            "answer_failure_tasks": answer_failures,
        }

    failure_analysis["comparative_findings"] = [
        {
            "finding": "Grounded correctness difference",
            "description": ("GPT-OSS 120B has one fewer grounded failure than GPT-OSS 20B."),
            "20b_grounded_failures": 2,
            "120b_grounded_failures": 1,
        },
        {
            "finding": "GE-019 differentiates the models",
            "description": (
                "GPT-OSS 20B fails GE-019 evidence grounding, while GPT-OSS 120B passes it."
            ),
            "20b": "FAIL",
            "120b": "PASS",
        },
        {
            "finding": "GE-010 is shared",
            "description": ("Both models fail GE-010 under the semantic-v2 grounded evaluation."),
            "20b": "FAIL",
            "120b": "FAIL",
        },
    ]

    failure_analysis["ge019_case_study"] = {
        "20b": {
            "actual_tools": ["summarize_hotspots"],
            "grounded_correct": False,
            "evidence_supported": False,
            "answer_correct": False,
            "supported_concepts": ["degraded_cell_count"],
            "unsupported_concepts": ["study_cell_count"],
            "interpretation": (
                "The model obtained evidence for the number of "
                "degraded/hotspot cells but did not obtain evidence "
                "for the total study-cell count required by the "
                "benchmark."
            ),
        },
        "120b": {
            "actual_tools": [
                "get_region",
                "summarize_hotspots",
            ],
            "grounded_correct": True,
            "evidence_supported": True,
            "answer_correct": True,
            "supported_concepts": [
                "study_cell_count",
                "degraded_cell_count",
            ],
            "unsupported_concepts": [],
            "interpretation": (
                "The model acquired both the study-cell count and "
                "degraded-cell count through an acceptable tool path."
            ),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w") as f:
        json.dump(
            failure_analysis,
            f,
            indent=2,
        )

    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
