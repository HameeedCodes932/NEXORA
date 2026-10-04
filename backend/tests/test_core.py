import os
from pathlib import Path

import pytest

os.environ["NEXORA_FORCE_LIGHTWEIGHT_EMBEDDINGS"] = "1"

from app.core.db import Database
from app.services.duplicates import DuplicateService
from app.services.embeddings import EmbeddingEngine
from app.services.executor import SandboxExecutor
from app.services.organizer import OrganizationService
from app.services.safety import SafetyError, sandbox_path
from app.services.scanner import WorkspaceScanner
from app.services.semantic_search import SemanticSearchService


@pytest.fixture()
def workspace(tmp_path: Path):
    db = Database(tmp_path / "nexora.sqlite3")
    db.init()
    embeddings = EmbeddingEngine("lightweight")
    scanner = WorkspaceScanner(db, tmp_path / "sandbox", embeddings)
    scanner.ensure_seeded()
    return db, tmp_path / "sandbox", embeddings


def test_duplicate_hashing_detects_exact_copies(workspace):
    db, _, _ = workspace
    groups = DuplicateService(db).exact_groups()
    names = {file.name for group in groups for file in group.files}
    assert "resume_final.pdf" in names
    assert "resume_final_copy.pdf" in names
    assert any(group.potential_recovery > 0 for group in groups)


def test_semantic_retrieval_finds_transformer_related_notes(workspace):
    db, _, embeddings = workspace
    response = SemanticSearchService(db, embeddings).search("transformer research", limit=5)
    result_names = [result.file.name for result in response.results]
    assert {"attention_mechanism_notes.md", "notes_43.txt", "research_summary.md"} & set(result_names)


def test_sandbox_path_validation_rejects_traversal(workspace):
    _, sandbox_root, _ = workspace
    with pytest.raises(SafetyError):
        sandbox_path(sandbox_root, "../outside", "budget.txt")


def test_mutating_operation_without_approval_fails(workspace):
    db, sandbox_root, _ = workspace
    file = db.fetch_one("SELECT * FROM workspace_files WHERE location = 'Downloads' LIMIT 1")
    action = {"action_type": "move", "file_id": file["id"], "destination": "Documents/Research", "reason": "test"}
    with pytest.raises(SafetyError):
        SandboxExecutor(db, sandbox_root).execute_action(action, approved=False)


def test_plan_approval_moves_file_and_undo_restores(workspace):
    db, sandbox_root, _ = workspace
    plan = OrganizationService(db).create_plan("Clean up my Downloads folder")
    assert plan.status == "pending"
    assert plan.actions
    executor = SandboxExecutor(db, sandbox_root)
    activities = executor.approve_plan(plan.id)
    assert activities
    moved = activities[0]
    changed_file = db.fetch_one("SELECT * FROM workspace_files WHERE id = ?", (moved.file_id,))
    assert changed_file["location"] == moved.destination
    undo = executor.undo(moved.id)
    restored_file = db.fetch_one("SELECT * FROM workspace_files WHERE id = ?", (moved.file_id,))
    assert restored_file["location"] == undo.destination
