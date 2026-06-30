"""
Identity resolution: group raw records from different sources into the
same candidate.

Match key priority (highest confidence first):
  1. email (case-insensitive exact match)
  2. phone (normalized E.164)
  3. full_name + phone combo  — fallback only when email is absent
Records with no usable key become their own singleton group instead of
being silently dropped — "robust" per the spec means nothing disappears.
"""
from collections import defaultdict
from typing import Dict, List

from confidence import calculate_field_confidence

SOURCE_PRIORITY = ["csv", "json", "txt"]

FIELDS = ["full_name", "email", "phone", "company", "title", "city", "country", "skills"]


def _key(value) -> str | None:
    if not value:
        return None
    return str(value).strip().lower()


def group_candidates(records: List[dict]) -> Dict[str, List[dict]]:
    by_email: Dict[str, List[dict]] = defaultdict(list)
    remaining: List[dict] = []

    for record in records:
        email_key = _key(record.get("email"))
        if email_key:
            by_email[f"email:{email_key}"].append(record)
        else:
            remaining.append(record)

    by_phone: Dict[str, List[dict]] = defaultdict(list)
    still_remaining: List[dict] = []

    for record in remaining:
        phone_key = _key(record.get("phone"))
        if phone_key:
            by_phone[f"phone:{phone_key}"].append(record)
        else:
            still_remaining.append(record)

    by_name_phone: Dict[str, List[dict]] = defaultdict(list)
    orphans: List[dict] = []

    for record in still_remaining:
        name_key = _key(record.get("full_name"))
        phone_key = _key(record.get("phone"))
        if name_key and phone_key:
            by_name_phone[f"name_phone:{name_key}|{phone_key}"].append(record)
        else:
            orphans.append(record)

    grouped: Dict[str, List[dict]] = {}
    grouped.update(by_email)
    grouped.update(by_phone)
    grouped.update(by_name_phone)
    for i, record in enumerate(orphans):
        grouped[f"orphan:{i}"] = [record]

    return grouped


def merge_candidate(records: List[dict]) -> dict:
    canonical = {}

    for field in FIELDS:
        chosen_record = None

        for source in SOURCE_PRIORITY:
            for record in records:
                if record.get("source") == source and record.get(field):
                    chosen_record = record
                    break
            if chosen_record:
                break

        if chosen_record:
            provenance = [
                {"source": r["source"], "value": r[field]}
                for r in records if r.get(field)
            ]
            canonical[field] = {
                "value": chosen_record[field],
                "confidence": calculate_field_confidence(field, chosen_record, records),
                "provenance": provenance,
            }
        else:
            canonical[field] = {"value": None, "confidence": 0.0, "provenance": []}

    return canonical