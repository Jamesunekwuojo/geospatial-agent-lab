import json
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS_PATH = Path("evaluation/results/model_comparison_v3_failure_analysis.json")
OUTPUT_PATH = Path("evaluation/results/figures/ge019_case_study.png")


def load_analysis():
    with RESULTS_PATH.open() as f:
        return json.load(f)


def add_evidence_row(
    ax,
    y,
    label,
    left_value,
    right_value,
    left_status,
    right_status,
):
    ax.text(
        0.05,
        y,
        label,
        fontsize=12,
        va="center",
        fontweight="bold",
    )

    ax.text(
        0.40,
        y,
        left_value,
        fontsize=12,
        va="center",
        ha="center",
    )

    ax.text(
        0.75,
        y,
        right_value,
        fontsize=12,
        va="center",
        ha="center",
    )

    ax.text(
        0.50,
        y,
        "",
    )

    ax.text(
        0.40,
        y - 0.035,
        left_status,
        fontsize=10,
        va="top",
        ha="center",
    )

    ax.text(
        0.75,
        y - 0.035,
        right_status,
        fontsize=10,
        va="top",
        ha="center",
    )


def main():
    load_analysis()

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.95,
        "GE-019 — Evidence Acquisition Case Study",
        fontsize=18,
        fontweight="bold",
        ha="center",
        va="center",
    )

    ax.text(
        0.5,
        0.90,
        "Comparison of benchmark-required evidence for grounded evaluation",
        fontsize=12,
        ha="center",
        va="center",
    )

    # Column headers
    ax.text(
        0.40,
        0.82,
        "GPT-OSS 20B",
        fontsize=14,
        fontweight="bold",
        ha="center",
    )

    ax.text(
        0.75,
        0.82,
        "GPT-OSS 120B",
        fontsize=14,
        fontweight="bold",
        ha="center",
    )

    # Horizontal separator
    ax.plot(
        [0.05, 0.95],
        [0.78, 0.78],
        linewidth=1,
    )

    # Required evidence
    ax.text(
        0.05,
        0.72,
        "Study-cell count",
        fontsize=12,
        fontweight="bold",
        va="center",
    )

    ax.text(
        0.40,
        0.72,
        "Missing",
        fontsize=12,
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.72,
        "100",
        fontsize=12,
        ha="center",
        va="center",
    )

    ax.text(
        0.40,
        0.675,
        "NOT SUPPORTED",
        fontsize=10,
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.675,
        "SUPPORTED",
        fontsize=10,
        ha="center",
        va="center",
    )

    # Degraded count
    ax.text(
        0.05,
        0.59,
        "Degraded-cell count",
        fontsize=12,
        fontweight="bold",
        va="center",
    )

    ax.text(
        0.40,
        0.59,
        "9",
        fontsize=12,
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.59,
        "9",
        fontsize=12,
        ha="center",
        va="center",
    )

    ax.text(
        0.40,
        0.545,
        "SUPPORTED",
        fontsize=10,
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.545,
        "SUPPORTED",
        fontsize=10,
        ha="center",
        va="center",
    )

    # Tool paths
    ax.text(
        0.05,
        0.45,
        "Observed tool path",
        fontsize=12,
        fontweight="bold",
        va="center",
    )

    ax.text(
        0.40,
        0.45,
        "summarize_hotspots",
        fontsize=11,
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.45,
        "get_region → summarize_hotspots",
        fontsize=11,
        ha="center",
        va="center",
    )

    # Evaluation
    ax.plot(
        [0.05, 0.95],
        [0.37, 0.37],
        linewidth=1,
    )

    ax.text(
        0.05,
        0.30,
        "Grounded evaluation",
        fontsize=13,
        fontweight="bold",
        va="center",
    )

    ax.text(
        0.40,
        0.30,
        "FAIL",
        fontsize=15,
        fontweight="bold",
        ha="center",
        va="center",
    )

    ax.text(
        0.75,
        0.30,
        "PASS",
        fontsize=15,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # Interpretation
    ax.text(
        0.05,
        0.19,
        "Interpretation",
        fontsize=12,
        fontweight="bold",
        va="top",
    )

    ax.text(
        0.40,
        0.19,
        "Obtained evidence for 9 hotspots,\nbut not the total study-cell count.",
        fontsize=10.5,
        ha="center",
        va="top",
        linespacing=1.4,
    )

    ax.text(
        0.75,
        0.19,
        "Obtained both benchmark-required evidence\ncomponents through an acceptable tool path.",
        fontsize=10.5,
        ha="center",
        va="top",
        linespacing=1.4,
    )

    fig.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
