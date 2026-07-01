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
from confidence import calculate_field_confidence

SOURCE_PRIORITY = [
    "csv",
    "ats_json",
    "pdf",
    "docx",
    "txt"
]


def build_candidate_key(record):
    """
    Build a matching key for identity resolution.

    Priority:
    1. Email
    2. Phone
    3. Full Name + Phone
    """

    email = record.get("email")
    phone = record.get("phone")
    full_name = record.get("full_name")

    if email:
        return ("email", email.lower())

    if phone:
        return ("phone", phone)

    if full_name and phone:
        return (
            "name_phone",
            f"{full_name.strip().lower()}|{phone}"
        )

    return None


def group_candidates(records):

    grouped = {}

    unmatched = []

    for record in records:

        key = build_candidate_key(record)

        if key is None:

            unmatched.append(record)
            continue

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(record)

    # Records that cannot be matched
    for index, record in enumerate(unmatched):

        grouped[("unknown", index)] = [record]

    return grouped


def merge_candidate(records):

    canonical = {}

    fields = [
        "candidate_id",
        "full_name",
        "email",
        "phone",
        "company",
        "title",
        "city",
        "country",
        "skills"
    ]

    for field in fields:

        chosen_record = None

        for source in SOURCE_PRIORITY:

            for record in records:

                if (
                    record.get("source") == source
                    and record.get(field)
                ):
                    chosen_record = record
                    break

            if chosen_record:
                break

        if chosen_record:

            provenance = []

            for record in records:

                if record.get(field):

                    provenance.append({

                        "source": record["source"],

                        "value": record[field]

                    })

            canonical[field] = {

                "value": chosen_record[field],

                "confidence": calculate_field_confidence(
                    field,
                    chosen_record,
                    records
                ),

                "provenance": provenance

            }

        else:

            canonical[field] = {

                "value": None,

                "confidence": 0,

                "provenance": []

            }

    return canonical