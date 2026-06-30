# Multi-Source Candidate Data Transformer

## Overview

This project implements a configurable candidate data transformation pipeline that ingests information from multiple heterogeneous sources, reconciles conflicting values, and produces a single canonical candidate profile.

The system demonstrates end-to-end data integration, including extraction, normalization, reconciliation, provenance tracking, confidence scoring, configurable schema projection, and validation.

The design emphasizes explainability, deterministic behavior, and graceful handling of incomplete or conflicting candidate data.

---

# Supported Input Sources

## Structured Sources

- Recruiter CSV
- ATS JSON

## Unstructured Sources

- Resume PDF
- Resume DOCX
- Resume TXT

---

# Canonical Candidate Schema

Every candidate is transformed into a standard canonical representation.

```json
{
  "candidate_id": "...",
  "full_name": {
    "value": "...",
    "confidence": 95.0,
    "provenance": [...]
  },
  "email": {
    "value": "...",
    "confidence": 100.0,
    "provenance": [...]
  },
  "phone": {
    "value": "...",
    "confidence": 90.0,
    "provenance": [...]
  },
  "company": {
    "value": "...",
    "confidence": 82.5,
    "provenance": [...]
  },
  "title": {
    "value": "...",
    "confidence": 80.0,
    "provenance": [...]
  },
  "city": {
    "value": "...",
    "confidence": 88.0,
    "provenance": [...]
  },
  "country": {
    "value": "...",
    "confidence": 88.0,
    "provenance": [...]
  },
  "skills": {
    "value": [
      "..."
    ],
    "confidence": 92.0,
    "provenance": [...]
  },
  "overall_confidence": 89.36
}
```

---

# Pipeline Architecture

```
                  INPUT SOURCES
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
   CSV Parser       JSON Parser      Resume Parser
                                        │
                              TXT / PDF / DOCX
                                        │
                                        ▼
                              Text Extraction
                                        │
                                        ▼
                             Field Extraction
                                        │
                                        ▼
                              Normalization
                                        │
                                        ▼
                           Candidate Grouping
                                        │
                                        ▼
                              Reconciliation
                                        │
                                        ▼
                           Confidence Scoring
                                        │
                                        ▼
                           Schema Projection
                                        │
                                        ▼
                                Validation
                                        │
                                        ▼
                                 output.json
```

---

# Design Decisions

### 1. Email-based Candidate Resolution

Email is used as the primary candidate identifier because it is generally unique across candidate records and remains consistent across different data sources.

---

### 2. Source Trust Hierarchy

Conflicting values are resolved using configurable source trust.

Default trust order:

```
CSV
>
JSON
>
Resume (PDF / DOCX / TXT)
```

Structured recruiter data is considered the most reliable, followed by ATS exports, while resume extraction is treated as less reliable due to free-form text parsing.

---

### 3. Normalize Before Merge

All records are normalized before reconciliation.

Examples include:

- Phone number normalization
- Email normalization
- Skill formatting
- Name cleanup

This reduces false conflicts during merging.

---

### 4. Explainable Decisions

Every selected field retains provenance information including:

- Source
- Original value
- Confidence

This makes every merge decision transparent and auditable.

---

### 5. Configurable Output Schema

Output fields are not hardcoded.

The pipeline projects the canonical candidate into any configured schema through JSON configuration files.

---

# Confidence Scoring

Each field receives a confidence score using three weighted signals.

| Signal | Weight |
|---------|--------|
| Source Trust | 50% |
| Agreement Across Sources | 35% |
| Extraction Reliability | 15% |

Conflicting values receive an additional penalty.

### Formula

```
Confidence =
0.50 × Source Trust
+ 0.35 × Agreement Ratio
+ 0.15 × Extraction Reliability
− Conflict Penalty
```

Overall candidate confidence is calculated as the average of all field confidence scores.

---

# Provenance Tracking

Every field records:

- Selected value
- Contributing source
- Confidence score
- Alternative values from other sources

Example:

```json
"company": {
    "value": "Google",
    "confidence": 92.5,
    "provenance": [
        {
            "source": "csv",
            "value": "Google"
        },
        {
            "source": "json",
            "value": "Google LLC"
        },
        {
            "source": "pdf",
            "value": "Google"
        }
    ]
}
```

---

# Configuration

The pipeline behavior is controlled using JSON configuration files.

Supported options include:

- Source priority
- Required fields
- Missing value handling
- Schema projection
- Output field mappings

No code changes are required to modify these behaviors.

---

# Running the Project

## Install dependencies

```bash
pip install -r requirements.txt
```

## Execute

```bash
python src/main.py
```

---

# Edge Cases Handled

The pipeline gracefully handles several real-world data quality issues.

- Missing source files
- Missing candidate fields
- Empty PDF resumes
- Corrupted PDF documents
- Invalid resume extraction
- Duplicate candidates
- Conflicting field values
- Multiple phone number formats
- Missing required fields
- Empty skills list
- Malformed CSV rows
- Unsupported source values
- No matching candidate identifiers

The pipeline continues processing remaining valid sources whenever possible.

---

# Assumptions

- Email uniquely identifies a candidate.
- Missing values never overwrite valid values.
- Source trust determines conflict resolution.
- PDF and DOCX resumes are converted to plain text before extraction.
- Output always conforms to the configured schema.

---

# Technologies Used

- Python
- Pydantic
- PyPDF
- python-docx
- CSV
- JSON
- Regular Expressions

---

# Output

The pipeline produces:

```
output.json
```

containing:

- Canonical candidate profile
- Provenance
- Confidence scores
- Schema-valid JSON

---


