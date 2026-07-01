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
from pathlib import Path
import argparse


INPUT_FOLDER = Path("sample_inputs")

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".txt",
    ".json",
    ".pdf"
}

files = sorted(
    [
        str(file)
        for file in INPUT_FOLDER.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
)


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

# -----------------------------------------
# Runtime Configuration Arguments
# -----------------------------------------

parser = argparse.ArgumentParser(
    description="Multi-Source Candidate Data Transformer"
)

parser.add_argument(
    "--config",
    default="configs/default_config.json",
    help="Path to runtime configuration JSON"
)

parser.add_argument(
    "--output",
    default="sample_outputs/output.json",
    help="Output JSON file"
)

args = parser.parse_args()

config = load_config(args.config)



groups = group_candidates(all_records)

print("\n==============================")
print("MERGED CANDIDATE PROFILES")
print("==============================\n")

# Stores canonical candidates
canonical_output = []

# Stores runtime projected candidates
runtime_output = []

for email, records in groups.items():

    candidate = merge_candidate(records)

candidate_model = CanonicalCandidate(**candidate)

# -----------------------------
# Store Canonical Candidate
# -----------------------------
canonical_candidate = candidate_model.model_dump()

canonical_output.append(
    canonical_candidate
)

# -----------------------------
# Runtime Projection
# -----------------------------
projected = project_candidate(
    canonical_candidate,
    config
)

validate_candidate(projected)

runtime_output.append(projected)

# Save ALL candidates once
# -----------------------------------
# Save Canonical Profile
# -----------------------------------

save_json(
    canonical_output,
    "sample_outputs/canonical_output.json"
)

# -----------------------------------
# Save Runtime Projection
# -----------------------------------

save_json(
    runtime_output,
    args.output
)


print("\nPipeline completed successfully.")

print(
    "\nCanonical profile saved to : "
    "sample_outputs/canonical_output.json"
)

print(
    f"Runtime output saved to : {args.output}"
)