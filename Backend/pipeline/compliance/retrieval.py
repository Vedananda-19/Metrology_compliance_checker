from models import RulePassages
from database import IS_POSTGRES
from pipeline import llm
import re


def embed(text: str):
    embeddings = llm.get_embeddings()
    if embeddings is None:
        return None
    try:
        return embeddings.embed_query(text)
    except Exception:
        return None


def keyword_search(db, query: str, limit: int):
    words = re.findall(r"[a-zA-Z]{4,}", query or "")[:12]
    if not words:
        return db.query(RulePassages).limit(limit).all()

    scored = []
    for record in db.query(RulePassages).all():
        haystack = f"{record.rule_ref} {record.text}".lower()
        score = sum(1 for word in words if word.lower() in haystack)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [record for _, record in scored[:limit]]


def search(db, query: str, limit: int = 8):
    vector = embed(query) if IS_POSTGRES else None
    if vector is not None:
        try:
            return (
                db.query(RulePassages)
                .filter(RulePassages.embedding.isnot(None))
                .order_by(RulePassages.embedding.cosine_distance(vector))
                .limit(limit)
                .all()
            )
        except Exception:
            pass
    return keyword_search(db, query, limit)


def as_text(passages) -> str:
    return "\n\n".join(
        f"Rule {p.rule_ref}" + (f" (page {p.pdf_page})" if p.pdf_page else "") + f":\n{p.text}"
        for p in passages
    )
