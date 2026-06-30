import json


def save_json(data, output_path):

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4
        )