import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.db import Database, from_json, to_json
from app.models.schemas import ActivityItem
from app.services.organizer import OrganizationService
from app.services.safety import SafetyError, assert_approved, sandbox_path
from app.services.util import dump_model


class SandboxExecutor:
    def __init__(self, db: Database, sandbox_root: Path):
        self.db = db
        self.sandbox_root = Path(sandbox_root)

    def approve_plan(self, plan_id: str, approved_by: str = "reviewer@nexora.ai") -> list[ActivityItem]:
        assert_approved(True)
        organizer = OrganizationService(self.db)
        plan = organizer.get_plan(plan_id)
        if not plan:
            raise SafetyError("Organization plan was not found.")
        if plan.status != "pending":
            raise SafetyError("Only pending plans can be approved.")
        activities: list[ActivityItem] = []
        for action in plan.actions:
            if action.action_type not in {"move", "trash"}:
                continue
            activities.append(self._execute_move_like_action(dump_model(action), approved_by))
        organizer.set_status(plan_id, "approved")
        return activities

    def execute_action(self, action: dict, approved: bool, approved_by: str = "reviewer@nexora.ai") -> ActivityItem:
        assert_approved(approved)
        return self._execute_move_like_action(action, approved_by)

    def _execute_move_like_action(self, action: dict, approved_by: str) -> ActivityItem:
        file = self.db.fetch_one("SELECT * FROM workspace_files WHERE id = ?", (action["file_id"],))
        if not file:
            raise SafetyError("File no longer exists in the sandbox index.")
        source_path = sandbox_path(self.sandbox_root, file["location"], file["name"])
        destination_folder = action["destination"]
        destination_path = sandbox_path(self.sandbox_root, destination_folder, file["name"])
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path = self._avoid_collision(destination_path)
        if not source_path.exists():
            raise SafetyError("Source file is missing from the sandbox.")
        shutil.move(str(source_path), str(destination_path))

        new_location = destination_path.parent.relative_to(self.sandbox_root).as_posix()
        if new_location == ".":
            new_location = ""
        new_name = destination_path.name
        self.db.execute("UPDATE workspace_files SET location = ?, name = ? WHERE id = ?", (new_location, new_name, file["id"]))
        activity = ActivityItem(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            action="Moved to Trash" if action["action_type"] == "trash" else "Moved",
            file_id=file["id"],
            filename=new_name,
            source=file["location"],
            destination=new_location,
            reason=action["reason"],
            status="complete",
            approved_by=approved_by,
        )
        self.db.execute(
            """
            INSERT INTO activity_log (id, timestamp, action, file_id, filename, source, destination, reason, status, approved_by, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                activity.id,
                activity.timestamp,
                activity.action,
                activity.file_id,
                activity.filename,
                activity.source,
                activity.destination,
                activity.reason,
                activity.status,
                activity.approved_by,
                to_json({"old_location": file["location"], "old_name": file["name"], "new_location": new_location, "new_name": new_name}),
            ),
        )
        return activity

    def undo(self, activity_id: str) -> ActivityItem:
        activity = self.db.fetch_one("SELECT * FROM activity_log WHERE id = ?", (activity_id,))
        if not activity:
            raise SafetyError("Activity item was not found.")
        metadata = from_json(activity["metadata"], {})
        required = {"old_location", "old_name", "new_location", "new_name"}
        if not required.issubset(metadata):
            raise SafetyError("This activity cannot be undone.")
        current_path = sandbox_path(self.sandbox_root, metadata["new_location"], metadata["new_name"])
        previous_path = sandbox_path(self.sandbox_root, metadata["old_location"], metadata["old_name"])
        if not current_path.exists():
            raise SafetyError("Current file path is missing; undo cannot be completed safely.")
        previous_path.parent.mkdir(parents=True, exist_ok=True)
        previous_path = self._avoid_collision(previous_path)
        shutil.move(str(current_path), str(previous_path))
        restored_location = previous_path.parent.relative_to(self.sandbox_root).as_posix()
        if restored_location == ".":
            restored_location = ""
        self.db.execute("UPDATE workspace_files SET location = ?, name = ? WHERE id = ?", (restored_location, previous_path.name, activity["file_id"]))
        self.db.execute("UPDATE activity_log SET status = ? WHERE id = ?", ("undone", activity_id))
        undo_item = ActivityItem(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            action="Undo",
            file_id=activity["file_id"],
            filename=previous_path.name,
            source=metadata["new_location"],
            destination=restored_location,
            reason=f"Restored previous sandbox location for {activity['filename']}.",
            status="complete",
            approved_by="reviewer@nexora.ai",
        )
        self.db.execute(
            """
            INSERT INTO activity_log (id, timestamp, action, file_id, filename, source, destination, reason, status, approved_by, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (undo_item.id, undo_item.timestamp, undo_item.action, undo_item.file_id, undo_item.filename, undo_item.source, undo_item.destination, undo_item.reason, undo_item.status, undo_item.approved_by, "{}"),
        )
        return undo_item

    def _avoid_collision(self, path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        for index in range(1, 100):
            candidate = path.with_name(f"{stem}-{index}{suffix}")
            if not candidate.exists():
                return candidate
        raise SafetyError("Could not find a safe destination filename.")
