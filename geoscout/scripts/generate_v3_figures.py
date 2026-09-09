import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_PATH = Path("evaluation/results/model_comparison_v3.json")
OUTPUT_DIR = Path("evaluation/results/figures")


def load_results():
    with RESULTS_PATH.open() as f:
        return json.load(f)


def get_summaries(data):
    return {
        summary["model"]: summary
        for summary in data["summaries"]
    }


def short_model_name(model):
    if model.endswith("120b"):
        return "GPT-OSS 120B"
    if model.endswith("20b"):
        return "GPT-OSS 20B"
    return model


def save_performance_figure(summaries):
    models = list(summaries.keys())
    labels = [short_model_name(model) for model in models]

    grounded = [
        summaries[model]["grounded_correctness"] * 100
        for model in models
    ]
    answer = [
        summaries[model]["answer_correctness"] * 100
        for model in models
    ]
    evidence = [
        summaries[model]["evidence_support_rate"] * 100
        for model in models
    ]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.bar(x - width, grounded, width, label="Grounded correctness")
    ax.bar(x, answer, width, label="Answer correctness")
    ax.bar(x + width, evidence, width, label="Evidence support")

    ax.set_ylabel("Rate (%)")
    ax.set_title("GeoScout v3 — Primary Evaluation Performance")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 110)
    ax.legend()

    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f%%", padding=3)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(
        OUTPUT_DIR / "performance_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_latency_figure(summaries):
    models = list(summaries.keys())
    labels = [short_model_name(model) for model in models]

    latency = [
        summaries[model]["mean_latency_ms"] / 1000
        for model in models
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(labels, latency)

    ax.set_ylabel("Mean latency (seconds)")
    ax.set_title("GeoScout v3 — Mean End-to-End Latency")

    ax.bar_label(bars, fmt="%.2f s", padding=3)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "latency_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_tool_usage_figure(summaries):
    models = list(summaries.keys())
    labels = [short_model_name(model) for model in models]

    tool_calls = [
        summaries[model]["mean_tool_calls"]
        for model in models
    ]

    llm_calls = [
        summaries[model]["mean_llm_calls"]
        for model in models
    ]

    x = np.arange(len(labels))
    width = 0.32

    fig, ax = plt.subplots(figsize=(9, 6))

    tool_bars = ax.bar(
        x - width / 2,
        tool_calls,
        width,
        label="Mean tool calls",
    )

    llm_bars = ax.bar(
        x + width / 2,
        llm_calls,
        width,
        label="Mean LLM calls",
    )

    ax.set_ylabel("Mean number of calls")
    ax.set_title("GeoScout v3 — Mean Agent Calls by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 2.7)
    ax.legend()

    ax.bar_label(tool_bars, fmt="%.2f", padding=3)
    ax.bar_label(llm_bars, fmt="%.2f", padding=3)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "tool_usage_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def save_failure_figure(data):
    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ]

    labels = [
        short_model_name(model)
        for model in models
    ]

    grounded_failures = []
    evidence_failures = []
    answer_failures = []

    for model in models:
        results = [
            result
            for result in data["results"]
            if result["model"] == model
        ]

        grounded_failures.append(
            sum(not result["grounded_correct"] for result in results)
        )

        evidence_failures.append(
            sum(not result["evidence_supported"] for result in results)
        )

        answer_failures.append(
            sum(not result["answer_correct"] for result in results)
        )

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.bar(
        x - width,
        grounded_failures,
        width,
        label="Grounded failures",
    )

    ax.bar(
        x,
        evidence_failures,
        width,
        label="Evidence failures",
    )

    ax.bar(
        x + width,
        answer_failures,
        width,
        label="Answer failures",
    )

    ax.set_ylabel("Number of failed tasks")
    ax.set_title("GeoScout v3 — Failure Profile")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(3, max(grounded_failures) + 1))
    ax.legend()

    for container in ax.containers:
        ax.bar_label(container, padding=3)

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "failure_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_results()
    summaries = get_summaries(data)

    save_performance_figure(summaries)
    save_latency_figure(summaries)
    save_tool_usage_figure(summaries)
    save_failure_figure(data)

    print("Generated v3 figures:")
    for filename in [
        "performance_comparison.png",
        "latency_comparison.png",
        "tool_usage_comparison.png",
        "failure_comparison.png",
    ]:
        print(f"  {OUTPUT_DIR / filename}")


if __name__ == "__main__":
    main()
