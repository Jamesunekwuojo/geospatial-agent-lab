import csv
import json
from pathlib import Path

RESULTS_PATH = Path("evaluation/results/model_comparison_v3.json")
OUTPUT_PATH = Path("evaluation/results/model_comparison_v3_task_results.csv")


def load_results():
    with RESULTS_PATH.open() as f:
        return json.load(f)


def main():
    data = load_results()

    results = data["results"]

    task_ids = sorted(
        {result["task_id"] for result in results},
        key=lambda task_id: int(task_id.split("-")[1]),
    )

    by_task_model = {(result["task_id"], result["model"]): result for result in results}

    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ]

    rows = []

    for task_id in task_ids:
        model_results = [by_task_model[(task_id, model)] for model in models]

        base = model_results[0]

        rows.append(
            [
                task_id,
                base["category"],
                base["difficulty"],
                *["PASS" if result["grounded_correct"] else "FAIL" for result in model_results],
                *["PASS" if result["evidence_supported"] else "FAIL" for result in model_results],
                *["PASS" if result["answer_correct"] else "FAIL" for result in model_results],
            ]
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(
            [
                "Task",
                "Category",
                "Difficulty",
                "20B Grounded",
                "120B Grounded",
                "20B Evidence",
                "120B Evidence",
                "20B Answer",
                "120B Answer",
            ]
        )

        writer.writerows(rows)

    print(f"Generated: {OUTPUT_PATH}")
    print(f"Tasks: {len(rows)}")


if __name__ == "__main__":
    main()
