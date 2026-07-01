import csv
import json
import re
from pathlib import Path
import os
from pypdf.errors import EmptyFileError

from pypdf import PdfReader
from docx import Document


def extract_csv(file_path):
    records = []

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            records.append({
                "source": "csv",
                "full_name": row.get("full_name"),
                "email": row.get("email"),
                "phone": row.get("phone"),
                "company": row.get("company"),
                "title": row.get("title"),
                "city": row.get("city"),
                "country": row.get("country"),
                "skills": []
            })

    return records


def extract_json(file_path):

    """
    Extract candidate information from an ATS JSON export.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    experience = data.get("experience", {})

    location = data.get("location", {})

    return [{

        "source": "json",

        "candidate_id": data.get("candidate_id"),

        "full_name": data.get("full_name"),

        "email": data.get("email"),

        "phone": data.get("phone"),

        "company": experience.get("company"),

        "title": experience.get("title"),

        "city": location.get("city"),

        "country": location.get("country"),

        "skills": data.get("skills", [])

    }]


# --------------------------------------------------
# Shared Resume Parser
# --------------------------------------------------

def extract_resume_text(text, source_name):

    # ---------------------------------------------
    # Basic Information
    # ---------------------------------------------

    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)

    phone_match = re.search(r'(\+?\d[\d\s\-]{8,}\d)', text)

    email = email_match.group() if email_match else None
    phone = phone_match.group() if phone_match else None

    # ---------------------------------------------
    # Clean lines
    # ---------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    full_name = lines[0] if lines else None

    company = None
    title = None
    city = None
    country = None
    skills = []

    # ---------------------------------------------
    # Location
    # ---------------------------------------------

    for line in lines:

        if line.lower().startswith("location"):

            location = line.split(":", 1)[-1].strip()

            parts = [x.strip() for x in location.split(",")]

            if len(parts) >= 1:
                city = parts[0]

            if len(parts) >= 2:
                country = parts[1]

            break

    # ---------------------------------------------
    # Skills Section
    # ---------------------------------------------

    if "Skills" in lines:

        start = lines.index("Skills") + 1

        end = len(lines)

        section_headers = {
            "Experience",
            "Education",
            "Projects",
            "Certifications",
            "Professional Summary",
            "Summary"
        }

        for i in range(start, len(lines)):

            if lines[i] in section_headers:

                end = i
                break

        skills = lines[start:end]

    # ---------------------------------------------
    # Experience Section
    # ---------------------------------------------

    experience_headers = [
        "Experience",
        "Work Experience",
        "Professional Experience"
    ]

    experience_index = None

    for header in experience_headers:

        if header in lines:

            experience_index = lines.index(header)
            break

    if experience_index is not None:

        experience_lines = lines[experience_index + 1:]

        # Remove dates

        experience_lines = [

            line

            for line in experience_lines

            if not re.search(
                r'\b(19|20)\d{2}\b',
                line
            )
        ]

        if len(experience_lines) >= 1:
            company = experience_lines[0]

        if len(experience_lines) >= 2:
            title = experience_lines[1]

    # ---------------------------------------------
    # Return Candidate Record
    # ---------------------------------------------

    return [{

        "source": source_name,

        "candidate_id": None,

        "full_name": full_name,

        "email": email,

        "phone": phone,

        "company": company,

        "title": title,

        "city": city,

        "country": country,

        "skills": skills

    }]

# --------------------------------------------------
# TXT
# --------------------------------------------------

def extract_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return extract_resume_text(text, "txt")


# --------------------------------------------------
# PDF
# --------------------------------------------------

def extract_pdf(file_path):

    try:
        # File exists?
        if not os.path.exists(file_path):
            print(f"[WARNING] PDF not found: {file_path}")
            return []

        # Empty file?
        if os.path.getsize(file_path) == 0:
            print(f"[WARNING] PDF is empty: {file_path}")
            return []

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Valid PDF but no extractable text
        if not text.strip():
            print(f"[WARNING] No text found in PDF: {file_path}")
            return []

        return extract_resume_text(text, "pdf")

    except EmptyFileError:
        print(f"[WARNING] Cannot read empty PDF: {file_path}")
        return []

    except Exception as e:
        print(f"[WARNING] Failed to read PDF ({file_path}): {e}")
        return []


# --------------------------------------------------
# DOCX
# --------------------------------------------------

def extract_docx(file_path):

    document = Document(file_path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    return extract_resume_text(text, "docx")