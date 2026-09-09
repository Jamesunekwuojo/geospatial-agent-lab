from geoscout.evaluation.evidence_trace import (
    EvidenceReference,
    EvidenceTrace,
    build_evidence_trace,
)


def test_evidence_reference_to_trace() -> None:
    evidence = EvidenceReference(
        tool="calculate_statistics",
        field="degraded_cells",
        actual_value=9,
    )

    trace = EvidenceTrace(
        concept="degraded_cell_count",
        expected_value=9,
        supported=True,
        supporting_evidence=[evidence],
    )

    result = trace.to_dict()

    assert result["concept"] == "degraded_cell_count"
    assert result["expected_value"] == 9
    assert result["supported"] is True

    assert result["supporting_evidence"] == [
        {
            "tool": "calculate_statistics",
            "field": "degraded_cells",
            "actual_value": 9,
        }
    ]


def test_build_evidence_trace() -> None:
    claim_evaluation = {
        "claims": [
            {
                "claim": {
                    "concept": "degraded_cell_count",
                    "expected_value": 9,
                },
                "supported": True,
                "supporting_evidence": [
                    {
                        "tool": "calculate_statistics",
                        "field": "degraded_cells",
                        "actual_value": 9,
                    }
                ],
            }
        ]
    }

    traces = build_evidence_trace(
        claim_evaluation
    )

    assert len(traces) == 1

    trace = traces[0]

    assert trace.concept == "degraded_cell_count"
    assert trace.expected_value == 9
    assert trace.supported is True

    assert len(trace.supporting_evidence) == 1

    evidence = trace.supporting_evidence[0]

    assert evidence.tool == "calculate_statistics"
    assert evidence.field == "degraded_cells"
    assert evidence.actual_value == 9


def test_unsupported_claim_has_no_evidence() -> None:
    claim_evaluation = {
        "claims": [
            {
                "claim": {
                    "concept": "degraded_cell_count",
                    "expected_value": 10,
                },
                "supported": False,
                "supporting_evidence": [],
            }
        ]
    }

    traces = build_evidence_trace(
        claim_evaluation
    )

    assert len(traces) == 1
    assert traces[0].supported is False
    assert traces[0].supporting_evidence == []


def test_evidence_trace_is_json_serializable() -> None:
    import json

    claim_evaluation = {
        "claims": [
            {
                "claim": {
                    "concept": "degraded_cell_count",
                    "expected_value": 9,
                },
                "supported": True,
                "supporting_evidence": [
                    {
                        "tool": "calculate_statistics",
                        "field": "degraded_cells",
                        "actual_value": 9,
                    }
                ],
            }
        ]
    }

    traces = build_evidence_trace(
        claim_evaluation
    )

    serialized = [
        trace.to_dict()
        for trace in traces
    ]

    output = json.dumps(serialized)

    assert "degraded_cell_count" in output
    assert "calculate_statistics" in output
    assert "degraded_cells" in output

