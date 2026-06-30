"""
Field-level confidence scoring.

Three signals, weighted:
  - source trust      (how much we trust this source type in general)
  - agreement ratio    (of sources that actually HAD this field, how many agreed)
  - extraction reliability (how mechanically reliable parsing from this source is)

Conflicting values are penalized explicitly and separately from missing values,
so an unopposed field doesn't get unfairly punished just because most sources
never reported it.
"""
from typing import Dict, List, Optional

SOURCE_TRUST: Dict[str, float] = {
    "csv": 1.00,   # recruiter-entered, structured, low ambiguity
    "json": 0.85,  # ATS export, structured but field-mapped/inferred
    "txt": 0.55,   # free text, regex/NLP extraction, most error-prone
}

EXTRACTION_RELIABILITY: Dict[str, float] = {
    "csv": 1.00,
    "json": 0.90,
    "txt": 0.60,
}

TRUST_WEIGHT = 0.50
AGREEMENT_WEIGHT = 0.35
EXTRACTION_WEIGHT = 0.15
CONFLICT_PENALTY_MAX = 0.50  # max fraction we can dock for disagreement


def calculate_field_confidence(
    field: str,
    chosen_record: dict,
    all_records: List[dict],
) -> float:
    source = chosen_record.get("source", "txt")
    chosen_value = chosen_record.get(field)

    # Only sources that actually reported a value for this field count
    # toward agreement/conflict. Missing != disagreeing.
    contributing = [
        r for r in all_records
        if r.get(field) not in (None, "", [])
    ]

    if not contributing:
        return 0.0

    agreeing = sum(1 for r in contributing if r.get(field) == chosen_value)
    conflicting = len(contributing) - agreeing

    agreement_ratio = agreeing / len(contributing)
    conflict_ratio = conflicting / len(contributing)

    trust_score = SOURCE_TRUST.get(source, 0.5)
    extraction_score = EXTRACTION_RELIABILITY.get(source, 0.5)

    raw = (
        TRUST_WEIGHT * trust_score
        + AGREEMENT_WEIGHT * agreement_ratio
        + EXTRACTION_WEIGHT * extraction_score
    )

    # Explicit conflict penalty — a field with active disagreement should
    # never look as confident as a field nobody else even spoke to.
    raw -= conflict_ratio * CONFLICT_PENALTY_MAX

    confidence = max(0.0, min(1.0, raw)) * 100
    return round(confidence, 2)




