from models import RulePassages
from database import IS_POSTGRES
from pipeline import llm
import logging
import re

logger = logging.getLogger(__name__)


def embed(text: str):
    embeddings = llm.get_embeddings()
    if embeddings is None:
        return None
    try:
        return embeddings.embed_query(text)
    except Exception:
        logger.exception("Embedding failed, retrieval is falling back to keyword search")
        return None


def keyword_search(db, query: str, limit: int):
    words = re.findall(r"[a-zA-Z]{3,}", query or "")[:16]
    records = db.query(RulePassages).all()
    if not words or not records:
        return records[:limit]

    scored = []
    for record in records:
        haystack = f"{record.rule_ref} {record.text}".lower()
        score = sum(1 for word in words if word.lower() in haystack)
        if score:
            scored.append((score, record))

    if not scored:
        return records[:limit]

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [record for _, record in scored[:limit]]


def cosine_search(db, vector, limit: int):
    import numpy as np

    query = np.array(vector, dtype=float)
    norm = np.linalg.norm(query)
    if norm == 0:
        return []

    scored = []
    for record in db.query(RulePassages).filter(RulePassages.embedding.isnot(None)).all():
        stored = np.array(record.embedding, dtype=float)
        if stored.size != query.size:
            continue
        denominator = norm * np.linalg.norm(stored)
        if denominator:
            scored.append((float(query @ stored / denominator), record))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [record for _, record in scored[:limit]]


def search(db, query: str, limit: int = 8):
    vector = embed(query)
    if vector is not None:
        try:
            if IS_POSTGRES:
                return (
                    db.query(RulePassages)
                    .filter(RulePassages.embedding.isnot(None))
                    .order_by(RulePassages.embedding.cosine_distance(vector))
                    .limit(limit)
                    .all()
                )
            matches = cosine_search(db, vector, limit)
            if matches:
                return matches
        except Exception:
            logger.exception("Vector search failed, retrieval is falling back to keyword search")
    return keyword_search(db, query, limit)


def as_text(passages) -> str:
    return "\n\n".join(
        f"Rule {p.rule_ref}" + (f" (page {p.pdf_page})" if p.pdf_page else "") + f":\n{p.text}"
        for p in passages
    )
