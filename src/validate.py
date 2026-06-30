def validate_candidate(candidate):

    required_fields = [
        "full_name",
        "email"
    ]

    for field in required_fields:

        if field not in candidate:
            raise ValueError(f"Missing field : {field}")

        if candidate[field]["value"] is None:
            raise ValueError(f"{field} cannot be empty")

    return True