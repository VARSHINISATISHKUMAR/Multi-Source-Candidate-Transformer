import json


def load_config(config_path):

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def project_candidate(candidate, config):

    output = {}

    for field in config["fields"]:

        if field not in candidate:

            if config["on_missing"] == "null":
                output[field] = None

            continue

        details = candidate[field]

        field_output = {
            "value": details["value"]
        }

        if config["include_confidence"]:
            field_output["confidence"] = details["confidence"]

        if config["include_provenance"]:
            field_output["provenance"] = details["provenance"]

        output[field] = field_output

    return output