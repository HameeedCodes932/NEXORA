from pathlib import Path


def _read_plain_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import fitz  # type: ignore

            with fitz.open(path) as doc:
                return "\n".join(page.get_text().strip() for page in doc).strip()
        except Exception:
            return _read_plain_text(path)
    if suffix == ".docx":
        try:
            from docx import Document  # type: ignore

            document = Document(path)
            return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
        except Exception:
            return _read_plain_text(path)
    return _read_plain_text(path)


def preview_text(content: str, limit: int = 260) -> str:
    collapsed = " ".join(content.split())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 3]}..."
