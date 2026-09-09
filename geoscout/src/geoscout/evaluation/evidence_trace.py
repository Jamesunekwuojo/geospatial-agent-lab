from dataclasses import dataclass
from typing import Any


@dataclass
class EvidenceReference:
    """A reference to a specific value produced by a GIS tool."""

    tool: str
    field: str
    actual_value: Any


@dataclass
class EvidenceTrace:
    """Connect a semantic claim to the evidence supporting it."""

    concept: str
    expected_value: Any
    supported: bool
    supporting_evidence: list[EvidenceReference]

    def to_dict(self) -> dict[str, Any]:
        """Convert the evidence trace into a JSON-serializable dictionary."""

        return {
            "concept": self.concept,
            "expected_value": self.expected_value,
            "supported": self.supported,
            "supporting_evidence": [
                {
                    "tool": evidence.tool,
                    "field": evidence.field,
                    "actual_value": evidence.actual_value,
                }
                for evidence in self.supporting_evidence
            ],
        }


def build_evidence_trace(
    claim_evaluation: dict[str, Any],
) -> list[EvidenceTrace]:
    """
    Convert semantic claim evaluation results into
    structured evidence traces.
    """

    traces: list[EvidenceTrace] = []

    for item in claim_evaluation.get("claims", []):
        claim = item["claim"]

        supporting_evidence = [
            EvidenceReference(
                tool=evidence["tool"],
                field=evidence["field"],
                actual_value=evidence["actual_value"],
            )
            for evidence in item.get(
                "supporting_evidence",
                [],
            )
        ]

        traces.append(
            EvidenceTrace(
                concept=claim["concept"],
                expected_value=claim.get(
                    "expected_value"
                ),
                supported=item["supported"],
                supporting_evidence=supporting_evidence,
            )
        )

    return traces
