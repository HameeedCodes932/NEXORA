import re
from pathlib import Path


ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MAX_SAFE_NAME_LENGTH = 120


class SafetyError(ValueError):
    pass


def normalize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", filename).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        raise SafetyError("Filename is empty after normalization.")
    if len(cleaned) > MAX_SAFE_NAME_LENGTH:
        stem = Path(cleaned).stem[:90]
        suffix = Path(cleaned).suffix
        cleaned = f"{stem}{suffix}"
    if Path(cleaned).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise SafetyError("Unsupported file extension.")
    return cleaned


def validate_relative_folder(folder: str) -> str:
    folder = folder.replace("\\", "/").strip("/")
    if not folder:
        return ""
    path = Path(folder)
    if path.is_absolute() or ".." in path.parts:
        raise SafetyError("Path traversal is not allowed.")
    if any(part.startswith(".") for part in path.parts):
        raise SafetyError("Hidden sandbox folders are not addressable.")
    return "/".join(path.parts)


def ensure_within_sandbox(root: Path, candidate: Path) -> Path:
    root_resolved = root.resolve()
    candidate_resolved = candidate.resolve()
    if candidate_resolved != root_resolved and root_resolved not in candidate_resolved.parents:
        raise SafetyError("Operation attempted outside the sandbox.")
    return candidate_resolved


def sandbox_path(root: Path, folder: str, filename: str | None = None) -> Path:
    safe_folder = validate_relative_folder(folder)
    base = root / safe_folder if safe_folder else root
    if filename is not None:
        base = base / normalize_filename(filename)
    return ensure_within_sandbox(root, base)


def assert_approved(approved: bool) -> None:
    if not approved:
        raise SafetyError("Mutating workspace actions require explicit user approval.")
