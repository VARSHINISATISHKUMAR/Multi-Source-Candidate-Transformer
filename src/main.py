from detect import detect_file_type
from extract import (
    extract_csv,
    extract_json,
    extract_txt,
    extract_pdf,
    extract_docx,
)
from normalize import normalize_phone, normalize_country
from reconcile import group_candidates, merge_candidate
from project import load_config, project_candidate
from validate import validate_candidate
from utils import save_json
from schema import CanonicalCandidate


files = [
    "sample_inputs/candidates.csv",
    "sample_inputs/resume.pdf",
    "sample_inputs/profile.json"
]


all_records = []


for file in files:

    file_type = detect_file_type(file)

    if file_type == "csv":
        data = extract_csv(file)

    elif file_type == "json":
        data = extract_json(file)

    elif file_type == "txt":
        data = extract_txt(file)

    elif file_type == "pdf":
        data = extract_pdf(file)

    elif file_type == "docx":
        data = extract_docx(file)

    else:
        data = []

    for record in data:

        record["phone"] = normalize_phone(record.get("phone"))
        record["country"] = normalize_country(record.get("country"))

        all_records.append(record)


groups = group_candidates(all_records)

print("\n==============================")
print("MERGED CANDIDATE PROFILES")
print("==============================\n")


config = load_config("configs/default_config.json")

print("\nUSING DEFAULT CONFIG\n")

for email, records in groups.items():

    # Merge candidate into canonical dictionary
    candidate = merge_candidate(records)

    # Convert dictionary to Pydantic model
    candidate_model = CanonicalCandidate(**candidate)
    

    # Convert back to dictionary for projection
    projected = project_candidate(
        candidate_model.model_dump(),
        config
    )

    validate_candidate(projected)

    save_json(
        projected,
        "sample_outputs/output.json"
    )

print("Output written successfully.")