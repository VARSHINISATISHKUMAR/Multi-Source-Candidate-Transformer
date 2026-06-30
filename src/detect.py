from pathlib import Path


def detect_file_type(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".csv":
        return "csv"

    elif extension == ".json":
        return "json"

    elif extension == ".txt":
        return "txt"

    elif extension == ".pdf":
        return "pdf"

    elif extension == ".docx":
        return "docx"

    return "unknown"