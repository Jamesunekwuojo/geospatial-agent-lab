import csv
import json
from pathlib import Path

RESULTS_PATH = Path("evaluation/results/model_comparison_v3.json")
OUTPUT_PATH = Path("evaluation/results/model_comparison_v3_table.csv")


def load_results():
    with RESULTS_PATH.open() as f:
        return json.load(f)


def short_model_name(model):
    if model.endswith("120b"):
        return "GPT-OSS 120B"
    if model.endswith("20b"):
        return "GPT-OSS 20B"
    return model


def main():
    data = load_results()

    summaries = {short_model_name(summary["model"]): summary for summary in data["summaries"]}

    models = [
        "GPT-OSS 20B",
        "GPT-OSS 120B",
    ]

    rows = [
        (
            "Tasks",
            [str(summaries[model]["task_count"]) for model in models],
        ),
        (
            "Grounded correctness",
            [f"{summaries[model]['grounded_correctness']:.0%}" for model in models],
        ),
        (
            "Answer correctness",
            [f"{summaries[model]['answer_correctness']:.0%}" for model in models],
        ),
        (
            "Evidence support",
            [f"{summaries[model]['evidence_support_rate']:.0%}" for model in models],
        ),
        (
            "Mean latency (s)",
            [f"{summaries[model]['mean_latency_ms'] / 1000:.2f}" for model in models],
        ),
        (
            "Mean tool calls",
            [f"{summaries[model]['mean_tool_calls']:.2f}" for model in models],
        ),
        (
            "Mean LLM calls",
            [f"{summaries[model]['mean_llm_calls']:.2f}" for model in models],
        ),
        (
            "Mean total tokens",
            [f"{summaries[model]['mean_total_tokens']:,.2f}" for model in models],
        ),
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", *models])

        for metric, values in rows:
            writer.writerow([metric, *values])

    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
