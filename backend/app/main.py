from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.db import Database
from app.services.embeddings import EmbeddingEngine
from app.services.scanner import WorkspaceScanner
from app.services.semantic_search import SemanticSearchService

settings = get_settings()
db = Database(settings.database_path)
embedding_engine = EmbeddingEngine(settings.embeddings_mode)
scanner = WorkspaceScanner(db, settings.sandbox_root, embedding_engine)
search_service = SemanticSearchService(db, embedding_engine)
_workspace_ready = False


def ensure_workspace_ready() -> None:
    global _workspace_ready
    if _workspace_ready and settings.database_path.exists():
        return
    db.init()
    scanner.ensure_seeded()
    _workspace_ready = True


def create_app() -> FastAPI:
    app = FastAPI(title="NEXORA API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.on_event("startup")
    def startup() -> None:
        ensure_workspace_ready()

    return app


app = create_app()
