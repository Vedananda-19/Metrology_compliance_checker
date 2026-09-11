from models import LegalProvisions
from database import IS_POSTGRES
from pipeline import llm
import logging
import re

logger = logging.getLogger(__name__)


def normalize_ref(rule_ref: str) -> str:
    return re.sub(r"\s+", " ", rule_ref or "").strip()


def provision_for_rule(db, rule_ref: str):
    target = "LMPC2011:" + normalize_ref(rule_ref)
    record = db.query(LegalProvisions).filter(LegalProvisions.provision_id == target).first()
    if record:
        return record
    head = normalize_ref(rule_ref).split(",")[0].strip()
    return (
        db.query(LegalProvisions)
        .filter(LegalProvisions.rule_ref.like(f"{head}%"))
        .order_by(LegalProvisions.provision_id)
        .first()
    )


def embed(text: str):
    embeddings = llm.get_embeddings()
    if embeddings is None:
        return None
    try:
        return embeddings.embed_query(text)
    except Exception:
        logger.exception("Embedding call failed")
        return None


def search(db, query: str, limit: int = 5):
    vector = embed(query) if IS_POSTGRES else None
    if vector is not None:
        try:
            return (
                db.query(LegalProvisions)
                .filter(LegalProvisions.embedding.isnot(None))
                .order_by(LegalProvisions.embedding.cosine_distance(vector))
                .limit(limit)
                .all()
            )
        except Exception:
            logger.exception("Vector search failed, falling back to keyword match")

    return keyword_search(db, query, limit)


def keyword_search(db, query: str, limit: int = 5):
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", query or "")][:6]
    if not words:
        return db.query(LegalProvisions).limit(limit).all()

    scored = []
    for record in db.query(LegalProvisions).all():
        haystack = f"{record.rule_ref} {record.text}".lower()
        score = sum(1 for word in words if word.lower() in haystack)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [record for _, record in scored[:limit]]


def context_for(db, rule_ref: str, title: str, limit: int = 3):
    direct = provision_for_rule(db, rule_ref)
    passages = search(db, f"{rule_ref} {title}", limit)

    seen = set()
    ordered = []
    for record in ([direct] if direct else []) + list(passages):
        if record is None or record.provision_id in seen:
            continue
        seen.add(record.provision_id)
        ordered.append(
            {
                "provision_id": record.provision_id,
                "rule_ref": record.rule_ref,
                "pdf_page": record.pdf_page,
                "text": record.text,
                "text_source": record.text_source,
            }
        )
    return ordered[: limit + 1]
