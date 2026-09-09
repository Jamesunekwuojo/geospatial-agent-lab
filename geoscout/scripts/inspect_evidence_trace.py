import json
from pathlib import Path

RESULT_PATH = Path(
    "evaluation/results/model_comparison_v3.json"
)


def main() -> None:
    with RESULT_PATH.open() as file:
        data = json.load(file)

    results = data["results"]

    print("=" * 70)
    print("Evidence Trace Inspection")
    print("=" * 70)

    trace_count = 0

    for result in results:
        traces = result.get(
            "evidence_trace",
            [],
        )

        trace_count += len(traces)

        if not traces:
            continue

        print()
        print(
            f"{result['model']} | "
            f"{result['task_id']}"
        )

        for trace in traces:
            print(
                f"  Concept: {trace['concept']}"
            )
            print(
                f"  Expected: "
                f"{trace['expected_value']}"
            )
            print(
                f"  Supported: "
                f"{trace['supported']}"
            )

            for evidence in trace[
                "supporting_evidence"
            ]:
                print(
                    "  Evidence: "
                    f"{evidence['tool']}."
                    f"{evidence['field']} = "
                    f"{evidence['actual_value']}"
                )

    print()
    print("=" * 70)
    print(
        f"Total evidence traces: {trace_count}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
