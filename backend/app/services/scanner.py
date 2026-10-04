import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.core.db import Database, to_json
from app.services.demo_data import DEMO_DOCUMENTS
from app.services.embeddings import EmbeddingEngine
from app.services.extractor import extract_text, preview_text
from app.services.organizer import classify_document
from app.services.safety import ALLOWED_EXTENSIONS, sandbox_path


class WorkspaceScanner:
    def __init__(self, db: Database, sandbox_root: Path, embeddings: EmbeddingEngine):
        self.db = db
        self.sandbox_root = Path(sandbox_root).resolve()
        self.embeddings = embeddings

    def ensure_seeded(self) -> None:
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        existing = self.db.fetch_one("SELECT COUNT(*) AS count FROM workspace_files")
        if existing and existing["count"] > 0:
            return
        self._write_demo_workspace()
        self.index_workspace()
        self._record_seed_activity()

    def _write_demo_workspace(self) -> None:
        written_paths: dict[str, Path] = {}
        for doc in DEMO_DOCUMENTS:
            path = sandbox_path(self.sandbox_root, doc.location, doc.name)
            path.parent.mkdir(parents=True, exist_ok=True)
            if doc.duplicate_of and doc.duplicate_of in written_paths:
                shutil.copyfile(written_paths[doc.duplicate_of], path)
            else:
                self._write_document(path, doc.content)
            written_paths[doc.name] = path

    def _write_document(self, path: Path, content: str) -> None:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            try:
                import fitz  # type: ignore

                document = fitz.open()
                page = document.new_page()
                page.insert_textbox((54, 54, 540, 760), content, fontsize=11, lineheight=1.2)
                document.save(path)
                document.close()
                return
            except Exception:
                pass
        if suffix == ".docx":
            try:
                from docx import Document  # type: ignore

                document = Document()
                document.add_paragraph(content)
                document.save(path)
                return
            except Exception:
                pass
        path.write_text(content, encoding="utf-8")

    def index_workspace(self) -> None:
        rows = []
        embedding_rows = []
        for path in sorted(self.sandbox_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            rel = path.relative_to(self.sandbox_root).as_posix()
            location = str(Path(rel).parent).replace("\\", "/")
            if location == ".":
                location = ""
            content = extract_text(path)
            stat = path.stat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            classification = classify_document(path.name, location, content)
            file_id = hashlib.sha1(rel.encode("utf-8")).hexdigest()
            rows.append(
                (
                    file_id,
                    path.name,
                    location,
                    path.suffix.lower().lstrip("."),
                    path.suffix.upper().lstrip(".") or "TXT",
                    stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    digest,
                    classification["category"],
                    classification["confidence"],
                    classification["reason"],
                    preview_text(content),
                    content,
                    to_json(classification["tags"]),
                )
            )
            embedding_rows.append((file_id, to_json(self.embeddings.embed(content)), self.embeddings.engine_name))

        self.db.execute("DELETE FROM file_embeddings")
        self.db.execute("DELETE FROM workspace_files")
        self.db.execute_many(
            """
            INSERT INTO workspace_files
            (id, name, location, extension, file_type, size, modified_at, sha256, category, confidence, reason, preview, content, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.db.execute_many("INSERT INTO file_embeddings (file_id, vector, engine) VALUES (?, ?, ?)", embedding_rows)

    def _record_seed_activity(self) -> None:
        self.db.execute(
            """
            INSERT INTO activity_log (id, timestamp, action, file_id, filename, source, destination, reason, status, approved_by, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "seed-workspace",
                datetime.now(timezone.utc).isoformat(),
                "Workspace indexed",
                None,
                "Demo workspace",
                "Seed data",
                "Sandbox",
                "Created and indexed the preloaded NEXORA demo workspace.",
                "complete",
                "system",
                "{}",
            ),
        )
