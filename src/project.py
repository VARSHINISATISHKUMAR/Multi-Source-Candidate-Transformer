import json


def load_config(config_path):
    """
    Load runtime configuration JSON.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def project_candidate(candidate, config):
    """
    Project the canonical candidate into the output format
    requested by the runtime configuration.
    """

    output = {}

    fields = config.get("fields", [])

    include_confidence = config.get(
        "include_confidence",
        True
    )

    include_provenance = config.get(
        "include_provenance",
        True
    )

    on_missing = config.get(
        "on_missing",
        "null"
    )

    for field in fields:

        # ----------------------------
        # Support both
        #
        # "full_name"
        #
        # and
        #
        # {
        #   "from":"full_name",
        #   "path":"candidate_name"
        # }
        # ----------------------------

        if isinstance(field, str):

            source_field = field
            output_field = field

        else:

            source_field = field.get("from")
            output_field = field.get("path", source_field)

        # ----------------------------
        # Missing field
        # ----------------------------

        if source_field not in candidate:

            if on_missing == "null":

                output[output_field] = None

            elif on_missing == "omit":

                continue

            elif on_missing == "error":

                raise KeyError(
                    f"Missing field: {source_field}"
                )

            continue

        details = candidate[source_field]

        field_output = {
            "value": details["value"]
        }

        if include_confidence:

            field_output["confidence"] = details["confidence"]

        if include_provenance:

            field_output["provenance"] = details["provenance"]

        output[output_field] = field_output

    return output