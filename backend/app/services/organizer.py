from datetime import datetime, timezone
from uuid import uuid4

from app.core.db import Database, from_json, to_json
from app.models.schemas import OrganizationPlan, ProposedAction
from app.services.util import dump_model
from app.services.embeddings import term_present


CATEGORY_RULES: dict[str, list[str]] = {
    "AI / Research": ["ai", "machine learning", "neural", "attention", "transformer", "embedding", "retrieval", "computer vision", "dataset", "research", "model", "rag"],
    "University": ["university", "fyp", "final year", "capstone", "thesis", "semester", "supervisor", "viva"],
    "Career": ["resume", "cv", "internship", "application", "cover letter", "candidate", "interview"],
    "Finance": ["invoice", "budget", "receipt", "payment", "expense", "rent", "subscription", "paid"],
    "Projects": ["project", "requirements", "architecture", "mvp", "roadmap", "milestone", "deliverable"],
    "Personal": ["travel", "personal", "packing", "hotel", "membership", "contacts"],
}


def classify_document(filename: str, location: str, content: str) -> dict:
    text = f"{filename} {location} {content}".lower()
    scores: dict[str, float] = {}
    matched: dict[str, list[str]] = {}
    for category, terms in CATEGORY_RULES.items():
        hits = [term for term in terms if term_present(text, term)]
        if hits:
            scores[category] = sum(2.5 if " " in term else 1.0 for term in hits)
            matched[category] = hits[:5]
    if not scores:
        return {
            "category": "Other",
            "confidence": 0.54,
            "reason": "No strong semantic category signal was detected, so the file is kept in Other.",
            "tags": ["uncategorized"],
        }
    category = max(scores, key=scores.get)
    raw_score = scores[category]
    confidence = min(0.96, 0.58 + raw_score / 16)
    terms = matched[category]
    return {
        "category": category,
        "confidence": round(confidence, 2),
        "reason": f"Detected {category.lower()} signals: {', '.join(terms[:4])}.",
        "tags": terms[:5],
    }


def target_folder(file_row: dict) -> str:
    category = file_row["category"]
    text = f"{file_row['name']} {file_row['content']}".lower()
    if category == "AI / Research":
        return "Documents/Research"
    if category == "University":
        return "Projects/FYP" if "fyp" in text or "final year" in text or "capstone" in text else "University"
    if category == "Career":
        return "Documents/Career"
    if category == "Finance":
        return "Documents/Finance"
    if category == "Projects":
        return "Projects/NEXORA" if "nexora" in text else "Projects"
    if category == "Personal":
        return "Documents/Personal"
    return file_row["location"]


def _in_scope(file_row: dict, instruction: str) -> bool:
    query = instruction.lower()
    combined = f"{file_row['name']} {file_row['location']} {file_row['category']} {file_row['content']}".lower()
    if "download" in query:
        return file_row["location"].startswith("Downloads")
    if "duplicate" in query:
        return True
    if "ai" in query or "research" in query or "machine learning" in query:
        return file_row["category"] == "AI / Research" or any(term_present(combined, term) for term in ["attention", "retrieval", "computer vision"])
    if "university" in query or "fyp" in query or "final" in query:
        return file_row["category"] == "University" or term_present(combined, "fyp")
    if "finance" in query or "invoice" in query or "budget" in query:
        return file_row["category"] == "Finance"
    if "career" in query or "internship" in query or "resume" in query:
        return file_row["category"] == "Career"
    return True


class OrganizationService:
    def __init__(self, db: Database):
        self.db = db

    def create_plan(self, instruction: str) -> OrganizationPlan:
        files = self.db.fetch_all("SELECT * FROM workspace_files ORDER BY location, name")
        scoped = [file for file in files if _in_scope(file, instruction)]
        actions: list[ProposedAction] = []

        seen_hashes: dict[str, dict] = {}
        for file in scoped:
            if file["sha256"] in seen_hashes:
                keeper = seen_hashes[file["sha256"]]
                actions.append(
                    ProposedAction(
                        id=str(uuid4()),
                        action_type="trash",
                        file_id=file["id"],
                        filename=file["name"],
                        source=file["location"],
                        destination="Trash",
                        reason=f"Exact duplicate of {keeper['name']} based on matching SHA-256 content hash.",
                        confidence=0.99,
                        risk="Low",
                    )
                )
            else:
                seen_hashes[file["sha256"]] = file

        for file in scoped:
            if any(action.file_id == file["id"] for action in actions):
                continue
            destination = target_folder(file)
            if destination != file["location"] and not file["location"].startswith("Trash"):
                actions.append(
                    ProposedAction(
                        id=str(uuid4()),
                        action_type="move",
                        file_id=file["id"],
                        filename=file["name"],
                        source=file["location"],
                        destination=destination,
                        reason=file["reason"],
                        confidence=max(0.62, float(file["confidence"])),
                        risk="Low",
                    )
                )

        actions = actions[:10]
        plan = OrganizationPlan(
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            query=instruction,
            status="pending",
            summary=f"{len(actions)} proposed action{'s' if len(actions) != 1 else ''}. Nothing has been changed yet.",
            actions=actions,
        )
        self.db.execute(
            """
            INSERT INTO organization_plans (id, created_at, query, status, actions, summary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (plan.id, plan.created_at, plan.query, plan.status, to_json([dump_model(a) for a in actions]), plan.summary),
        )
        return plan

    def get_plan(self, plan_id: str) -> OrganizationPlan | None:
        row = self.db.fetch_one("SELECT * FROM organization_plans WHERE id = ?", (plan_id,))
        if not row:
            return None
        actions = [ProposedAction(**action) for action in from_json(row["actions"], [])]
        return OrganizationPlan(id=row["id"], created_at=row["created_at"], query=row["query"], status=row["status"], summary=row["summary"], actions=actions)

    def set_status(self, plan_id: str, status: str) -> None:
        self.db.execute("UPDATE organization_plans SET status = ? WHERE id = ?", (status, plan_id))
