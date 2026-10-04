from functools import lru_cache
import os
from pathlib import Path
import tempfile

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NEXORA"
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")
    demo_email: str = Field(default="reviewer@nexora.ai", alias="DEMO_EMAIL")
    demo_password: str = Field(default="NexoraDemo2026!", alias="DEMO_PASSWORD")
    demo_token: str = Field(default="nexora-demo-token", alias="DEMO_TOKEN")
    embeddings_mode: str = Field(default="auto", alias="NEXORA_EMBEDDINGS_MODE")
    max_upload_mb: int = Field(default=8, alias="MAX_UPLOAD_MB")

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def sandbox_root(self) -> Path:
        runtime_dir = os.getenv("NEXORA_RUNTIME_DIR")
        if runtime_dir:
            return Path(runtime_dir) / "sandbox"
        if os.getenv("VERCEL"):
            return Path(tempfile.gettempdir()) / "nexora" / "sandbox"
        return self.backend_root / "sandbox"

    @property
    def database_path(self) -> Path:
        return self.sandbox_root / "nexora.sqlite3"

    @property
    def allowed_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    model_config = {
        "env_file": ".env",
        "extra": "allow",
        "populate_by_name": True,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
