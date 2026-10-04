from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.core.db import Database
from app.models.schemas import ActivityItem, ApprovePlanRequest, DuplicatesResponse, FileDetail, LoginRequest, LoginResponse, PlanRequest, WorkspaceStats
from app.services.duplicates import DuplicateService, to_workspace_file
from app.services.executor import SandboxExecutor
from app.services.organizer import OrganizationService
from app.services.safety import SafetyError
from app.services.semantic_search import SemanticSearchService
from app.services.util import dump_model


router = APIRouter(prefix="/api")


def get_db() -> Database:
    from app.main import db, ensure_workspace_ready

    ensure_workspace_ready()
    return db


def get_search() -> SemanticSearchService:
    from app.main import ensure_workspace_ready, search_service

    ensure_workspace_ready()
    return search_service


def auth_guard(authorization: str | None = Header(default=None), settings: Settings = Depends(get_settings)) -> None:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing demo token.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token == settings.demo_token:
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo token.")


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> LoginResponse:
    if payload.email.lower() != settings.demo_email.lower() or payload.password != settings.demo_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo credentials.")
    return LoginResponse(token=settings.demo_token, user={"email": settings.demo_email, "name": "NEXORA Reviewer"})


@router.get("/health")
def health() -> dict:
    from app.main import embedding_engine, ensure_workspace_ready

    ensure_workspace_ready()
    return {
        "api": "Online",
        "workspace": "Indexed",
        "semantic_engine": "Active",
        "safety_layer": "Active",
        "embedding_engine": embedding_engine.engine_name,
        "embedding_mode": embedding_engine.status_mode,
    }


@router.get("/workspace/stats", response_model=WorkspaceStats, dependencies=[Depends(auth_guard)])
def workspace_stats(db: Database = Depends(get_db)) -> WorkspaceStats:
    from app.main import embedding_engine

    total = db.fetch_one("SELECT COUNT(*) AS count, COALESCE(SUM(size), 0) AS size FROM workspace_files")
    indexed = db.fetch_one("SELECT COUNT(*) AS count FROM file_embeddings")
    duplicate_service = DuplicateService(db)
    groups = duplicate_service.exact_groups()
    duplicate_files = sum(len(group.files) for group in groups)
    potential_recovery = sum(group.potential_recovery for group in groups)
    category_counts = db.fetch_all("SELECT category, COUNT(*) AS count FROM workspace_files GROUP BY category")
    ai_count = next((row["count"] for row in category_counts if row["category"] == "AI / Research"), 0)
    move_candidates = db.fetch_all("SELECT COUNT(*) AS count FROM workspace_files WHERE location = 'Downloads'")[0]["count"]
    resume_versions = db.fetch_all("SELECT COUNT(*) AS count FROM workspace_files WHERE lower(name) LIKE '%resume%'")[0]["count"]
    recent = db.fetch_all("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 4")
    return WorkspaceStats(
        total_files=total["count"],
        storage_used=total["size"],
        duplicate_files=duplicate_files,
        potential_recovery=potential_recovery,
        indexed_files=indexed["count"],
        insights=[
            f"{len(groups)} exact duplicate group{'s' if len(groups) != 1 else ''} detected",
            f"{ai_count} files appear related to AI research",
            f"{move_candidates} files may be better organized from Downloads",
            f"{resume_versions} resume versions detected",
        ],
        recent_activity=recent,
        status={
            "api": "Online",
            "workspace": "Indexed",
            "semantic_engine": "Active",
            "safety_layer": "Active",
            "embedding_engine": embedding_engine.engine_name,
            "embedding_mode": embedding_engine.status_mode,
        },
    )


@router.get("/files", dependencies=[Depends(auth_guard)])
def list_files(type: str | None = Query(default=None), category: str | None = Query(default=None), db: Database = Depends(get_db)) -> list[dict]:
    rows = db.fetch_all("SELECT * FROM workspace_files ORDER BY location, name")
    files = [dump_model(to_workspace_file(row)) for row in rows]
    if type:
        files = [file for file in files if file["extension"].lower() == type.lower()]
    if category:
        files = [file for file in files if file["category"] == category]
    return files


@router.get("/files/{file_id}", response_model=FileDetail, dependencies=[Depends(auth_guard)])
def file_detail(file_id: str, db: Database = Depends(get_db), search: SemanticSearchService = Depends(get_search)) -> FileDetail:
    row = db.fetch_one("SELECT * FROM workspace_files WHERE id = ?", (file_id,))
    if not row:
        raise HTTPException(status_code=404, detail="File not found.")
    base = to_workspace_file(row)
    related = [result.file for result in search.search(row["content"][:500], limit=4).results if result.file.id != file_id][:3]
    duplicates = db.fetch_all("SELECT id FROM workspace_files WHERE sha256 = ? AND id != ?", (row["sha256"], file_id))
    status_text = f"{len(duplicates)} exact duplicate{'s' if len(duplicates) != 1 else ''} found" if duplicates else "No exact duplicate"
    return FileDetail(**dump_model(base), related_files=related, duplicate_status=status_text)


@router.post("/search", dependencies=[Depends(auth_guard)])
def search(payload: dict, search_service: SemanticSearchService = Depends(get_search)) -> dict:
    query = str(payload.get("query", "")).strip()
    limit = int(payload.get("limit", 8))
    if len(query) < 2:
        raise HTTPException(status_code=422, detail="Query must contain at least two characters.")
    return dump_model(search_service.search(query, min(max(limit, 1), 20)))


@router.get("/duplicates", response_model=DuplicatesResponse, dependencies=[Depends(auth_guard)])
def duplicates(db: Database = Depends(get_db)) -> DuplicatesResponse:
    service = DuplicateService(db)
    return DuplicatesResponse(exact_groups=service.exact_groups(), related_versions=service.related_versions())


@router.post("/organize/plan", dependencies=[Depends(auth_guard)])
def organize_plan(payload: PlanRequest, db: Database = Depends(get_db)) -> dict:
    return dump_model(OrganizationService(db).create_plan(payload.instruction))


@router.post("/organize/approve", dependencies=[Depends(auth_guard)])
def organize_approve(payload: ApprovePlanRequest, db: Database = Depends(get_db), settings: Settings = Depends(get_settings)) -> dict:
    try:
        executor = SandboxExecutor(db, settings.sandbox_root)
        activities = executor.approve_plan(payload.plan_id, approved_by=settings.demo_email)
        return {"status": "approved", "activity": [dump_model(activity) for activity in activities]}
    except SafetyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/organize/reject", dependencies=[Depends(auth_guard)])
def organize_reject(payload: ApprovePlanRequest, db: Database = Depends(get_db)) -> dict:
    OrganizationService(db).set_status(payload.plan_id, "rejected")
    return {"status": "rejected"}


@router.get("/activity", response_model=list[ActivityItem], dependencies=[Depends(auth_guard)])
def activity(db: Database = Depends(get_db)) -> list[ActivityItem]:
    rows = db.fetch_all("SELECT * FROM activity_log ORDER BY timestamp DESC")
    return [
        ActivityItem(
            id=row["id"],
            timestamp=row["timestamp"],
            action=row["action"],
            file_id=row["file_id"],
            filename=row["filename"],
            source=row["source"],
            destination=row["destination"],
            reason=row["reason"],
            status=row["status"],
            approved_by=row["approved_by"],
        )
        for row in rows
    ]


@router.post("/activity/{activity_id}/undo", dependencies=[Depends(auth_guard)])
def undo(activity_id: str, db: Database = Depends(get_db), settings: Settings = Depends(get_settings)) -> dict:
    try:
        return dump_model(SandboxExecutor(db, settings.sandbox_root).undo(activity_id))
    except SafetyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
