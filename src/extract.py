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

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [{
        "source": "json",
        "full_name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "company": None,
        "title": None,
        "city": data.get("location", {}).get("city"),
        "country": data.get("location", {}).get("country"),
        "skills": data.get("skills", [])
    }]


# --------------------------------------------------
# Shared Resume Parser
# --------------------------------------------------

def extract_resume_text(text, source_name):

    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\+?\d[\d\s\-]{8,}\d)', text)

    lines = text.splitlines()

    full_name = lines[0].strip() if lines else None

    company = None
    title = None

    if "Google" in text:
        company = "Google"

    if "Software Engineer" in text:
        title = "Software Engineer"

    skills = []

    for skill in [
        "Python",
        "Java",
        "SQL",
        "Machine Learning"
    ]:
        if skill.lower() in text.lower():
            skills.append(skill)

    return [{
        "source": source_name,
        "full_name": full_name,
        "email": email.group() if email else None,
        "phone": phone.group() if phone else None,
        "company": company,
        "title": title,
        "city": "Chennai",
        "country": "India",
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