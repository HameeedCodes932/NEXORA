from app.core.db import Database, from_json
from app.models.schemas import DuplicateGroup, WorkspaceFile
from app.services.embeddings import cosine_similarity
from app.services.util import dump_model


def to_workspace_file(row: dict) -> WorkspaceFile:
    return WorkspaceFile(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        extension=row["extension"],
        file_type=row["file_type"],
        size=row["size"],
        modified_at=row["modified_at"],
        sha256=row["sha256"],
        category=row["category"],
        confidence=row["confidence"],
        reason=row["reason"],
        preview=row["preview"],
        tags=from_json(row["tags"], []),
    )


class DuplicateService:
    def __init__(self, db: Database):
        self.db = db

    def exact_groups(self) -> list[DuplicateGroup]:
        rows = self.db.fetch_all("SELECT * FROM workspace_files ORDER BY sha256, location, name")
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            grouped.setdefault(row["sha256"], []).append(row)
        groups: list[DuplicateGroup] = []
        group_index = 1
        for digest, files in grouped.items():
            if len(files) < 2:
                continue
            keep_size = max(file["size"] for file in files)
            recovery = sum(file["size"] for file in files) - keep_size
            groups.append(
                DuplicateGroup(
                    id=f"duplicate-group-{group_index}",
                    hash=digest,
                    files=[to_workspace_file(file) for file in files],
                    potential_recovery=recovery,
                )
            )
            group_index += 1
        return groups

    def related_versions(self, limit: int = 6) -> list[dict]:
        files = self.db.fetch_all(
            """
            SELECT f.*, e.vector
            FROM workspace_files f
            JOIN file_embeddings e ON e.file_id = f.id
            ORDER BY f.name
            """
        )
        related: list[dict] = []
        for index, left in enumerate(files):
            for right in files[index + 1 :]:
                if left["sha256"] == right["sha256"]:
                    continue
                same_family = _filename_family(left["name"]) == _filename_family(right["name"])
                same_category = left["category"] == right["category"]
                if not (same_family or same_category):
                    continue
                score = cosine_similarity(from_json(left["vector"], []), from_json(right["vector"], []))
                if score >= 0.68 or same_family:
                    related.append(
                        {
                            "left": dump_model(to_workspace_file(left)),
                            "right": dump_model(to_workspace_file(right)),
                            "score": round(score, 2),
                            "reason": "Similar semantic content or filename family, but SHA-256 hashes differ.",
                        }
                    )
        related.sort(key=lambda item: item["score"], reverse=True)
        return related[:limit]


def _filename_family(name: str) -> str:
    stem = name.rsplit(".", 1)[0].lower()
    for token in ["_final", "_copy", "_old", "-final", "-copy", "-old", " final", " copy", " old"]:
        stem = stem.replace(token, "")
    return stem
