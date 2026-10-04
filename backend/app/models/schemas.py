from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict[str, str]


class SystemStatus(BaseModel):
    api: str
    workspace: str
    semantic_engine: str
    safety_layer: str
    embedding_engine: str
    embedding_mode: str


class WorkspaceStats(BaseModel):
    total_files: int
    storage_used: int
    duplicate_files: int
    potential_recovery: int
    indexed_files: int
    insights: list[str]
    recent_activity: list[dict]
    status: SystemStatus


class WorkspaceFile(BaseModel):
    id: str
    name: str
    location: str
    extension: str
    file_type: str
    size: int
    modified_at: str
    sha256: str
    category: str
    confidence: float
    reason: str
    preview: str
    tags: list[str]
    status: str = "Indexed"


class FileDetail(WorkspaceFile):
    related_files: list[WorkspaceFile] = Field(default_factory=list)
    duplicate_status: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=300)
    limit: int = Field(default=8, ge=1, le=20)


class SearchResult(BaseModel):
    file: WorkspaceFile
    score: float
    excerpt: str
    reason: str


class SearchResponse(BaseModel):
    query: str
    engine: str
    mode: str
    results: list[SearchResult]


class DuplicateGroup(BaseModel):
    id: str
    hash: str
    files: list[WorkspaceFile]
    potential_recovery: int


class DuplicatesResponse(BaseModel):
    exact_groups: list[DuplicateGroup]
    related_versions: list[dict]


class PlanRequest(BaseModel):
    instruction: str = Field(min_length=3, max_length=500)


class ProposedAction(BaseModel):
    id: str
    action_type: str
    file_id: str
    filename: str
    source: str
    destination: str
    reason: str
    confidence: float
    risk: str


class OrganizationPlan(BaseModel):
    id: str
    created_at: str
    query: str
    status: str
    summary: str
    actions: list[ProposedAction]


class ApprovePlanRequest(BaseModel):
    plan_id: str


class ActivityItem(BaseModel):
    id: str
    timestamp: str
    action: str
    file_id: str | None = None
    filename: str
    source: str
    destination: str
    reason: str
    status: str
    approved_by: str
