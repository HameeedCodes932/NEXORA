from app.core.db import Database, from_json
from app.models.schemas import SearchResponse, SearchResult
from app.services.duplicates import to_workspace_file
from app.services.embeddings import CONCEPTS, EmbeddingEngine, cosine_similarity, term_present, tokenize


class SemanticSearchService:
    def __init__(self, db: Database, embeddings: EmbeddingEngine):
        self.db = db
        self.embeddings = embeddings

    def search(self, query: str, limit: int = 8) -> SearchResponse:
        query_vector = self.embeddings.embed(query)
        rows = self.db.fetch_all(
            """
            SELECT f.*, e.vector
            FROM workspace_files f
            JOIN file_embeddings e ON e.file_id = f.id
            """
        )
        scored: list[SearchResult] = []
        for row in rows:
            embedding_score = cosine_similarity(query_vector, from_json(row["vector"], []))
            signal_score = content_signal(query, row)
            score = (embedding_score * 0.62) + (signal_score * 0.38)
            if score <= 0:
                continue
            scored.append(
                SearchResult(
                    file=to_workspace_file(row),
                    score=round(score, 3),
                    excerpt=best_excerpt(row["content"], query),
                    reason=match_reason(row, score),
                )
            )
        scored.sort(key=lambda result: result.score, reverse=True)
        return SearchResponse(query=query, engine=self.embeddings.engine_name, mode=self.embeddings.status_mode, results=scored[:limit])


def best_excerpt(content: str, query: str, limit: int = 280) -> str:
    collapsed = " ".join(content.split())
    if len(collapsed) <= limit:
        return collapsed
    query_terms = set(tokenize(query))
    lower = collapsed.lower()
    positions = [lower.find(term) for term in query_terms if lower.find(term) >= 0]
    start = max(0, min(positions) - 90) if positions else 0
    excerpt = collapsed[start : start + limit]
    if start > 0:
        excerpt = f"...{excerpt}"
    if start + limit < len(collapsed):
        excerpt = f"{excerpt}..."
    return excerpt


def match_reason(row: dict, score: float) -> str:
    tags = from_json(row["tags"], [])
    tag_text = f" Shared concepts: {', '.join(tags[:3])}." if tags else ""
    percent = round(score * 100)
    return f"Semantic similarity score is {percent}%, based on document content and category signals.{tag_text}"


def content_signal(query: str, row: dict) -> float:
    text = f"{row['content']} {row['category']} {' '.join(from_json(row['tags'], []))}".lower()
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0

    direct_hits = sum(1 for token in query_tokens if term_present(text, token))
    concept_terms: set[str] = set()
    for terms in CONCEPTS.values():
        if any(term_present(query.lower(), term) for term in terms):
            concept_terms.update(terms)
    concept_hits = sum(1 for term in concept_terms if term_present(text, term))
    score = (direct_hits / max(len(query_tokens), 1)) * 0.55
    if concept_terms:
        score += min(1.0, concept_hits / max(3, len(concept_terms) * 0.35)) * 0.45
    return max(0.0, min(1.0, score))
