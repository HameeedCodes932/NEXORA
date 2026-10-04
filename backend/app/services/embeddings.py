import hashlib
import math
import os
import re
from typing import Iterable

import numpy as np


CONCEPTS: dict[str, list[str]] = {
    "ai": ["ai", "artificial intelligence", "machine learning", "neural", "model", "llm", "agent", "rag"],
    "transformer": ["transformer", "attention", "self attention", "query", "key", "value", "token", "language model"],
    "research": ["research", "paper", "literature", "evaluation", "experiment", "dataset", "metrics", "summary"],
    "vision": ["computer vision", "image", "object detection", "classification", "segmentation", "convolutional"],
    "university": ["university", "fyp", "final year", "capstone", "thesis", "semester", "supervisor", "viva"],
    "career": ["resume", "cv", "cover letter", "internship", "application", "candidate", "interview"],
    "finance": ["invoice", "budget", "receipt", "payment", "expense", "rent", "subscription", "paid"],
    "project": ["project", "requirements", "architecture", "mvp", "roadmap", "milestone", "planner"],
    "safety": ["approval", "sandbox", "rollback", "permission", "safe", "trash", "undo"],
    "workspace": ["workspace", "files", "documents", "folder", "organize", "duplicates", "scanner"],
}


def term_present(text: str, term: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


class EmbeddingEngine:
    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.model_name = "all-MiniLM-L6-v2"
        self.model = None
        self.engine_name = "Lightweight Demo Mode"
        self.status_mode = "fallback"
        if mode != "lightweight":
            self._try_load_sentence_transformer(mode)

    def _try_load_sentence_transformer(self, mode: str) -> None:
        if os.getenv("NEXORA_FORCE_LIGHTWEIGHT_EMBEDDINGS") == "1":
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            kwargs = {"local_files_only": mode == "auto"}
            self.model = SentenceTransformer(self.model_name, **kwargs)
            self.engine_name = self.model_name
            self.status_mode = "sentence-transformers"
        except TypeError:
            if mode == "sentence-transformers":
                try:
                    from sentence_transformers import SentenceTransformer  # type: ignore

                    self.model = SentenceTransformer(self.model_name)
                    self.engine_name = self.model_name
                    self.status_mode = "sentence-transformers"
                except Exception:
                    self.model = None
        except Exception:
            self.model = None

    def embed(self, text: str) -> list[float]:
        if self.model is not None:
            vector = self.model.encode([text], normalize_embeddings=True)[0]
            return [float(value) for value in vector]
        return self._lightweight_vector(text).tolist()

    def _lightweight_vector(self, text: str) -> np.ndarray:
        normalized = normalize_text(expand_query(text))
        tokens = tokenize(normalized)
        vector = np.zeros(192, dtype=np.float32)

        for concept_index, terms in enumerate(CONCEPTS.values()):
            score = 0.0
            for term in terms:
                if term_present(normalized, term):
                    score += 3.0 if " " in term else 1.5
            vector[concept_index] = score

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = 32 + digest[0] % 160
            vector[bucket] += 1.0 + min(len(token), 12) / 20

        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2]


def expand_query(text: str) -> str:
    lower = text.lower()
    additions: list[str] = []
    for terms in CONCEPTS.values():
        if any(term_present(lower, term) for term in terms):
            additions.extend(terms)
    return f"{text} {' '.join(additions)}"


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    vec_a = np.array(list(a), dtype=np.float32)
    vec_b = np.array(list(b), dtype=np.float32)
    denom = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    value = float(np.dot(vec_a, vec_b) / denom)
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, value))
