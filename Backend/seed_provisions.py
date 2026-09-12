from database import SessionLocal, Base, engine, enable_pgvector
from models import RulePassages
from pipeline.preprocessing import images as preprocessing
from pipeline.extraction import ocr
from pipeline import llm
from config import LEGAL_PDF_PATH
from pathlib import Path
import io
import re

RULE_HEADING = re.compile(r"^\s*(\d{1,2})\s*\.\s*([A-Za-z].{3,})")
SCALE = 2.2


def page_texts(path: Path):
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(path))
    for index in range(len(document)):
        rendered = document[index].render(scale=SCALE).to_pil()
        buffer = io.BytesIO()
        rendered.save(buffer, format="PNG")
        text = ocr.read_text(preprocessing.prepare(buffer.getvalue()))
        print(f"  page {index + 1:>2}: {len(text):>5} characters")
        yield index + 1, text


def split_into_passages(pages: dict[int, str]):
    passages = {}
    current = None
    page = None
    buffer = []

    for number in sorted(pages):
        for line in pages[number].splitlines():
            heading = RULE_HEADING.match(line.strip())
            if heading:
                if current and buffer:
                    passages.setdefault(current, {"page": page, "lines": []})["lines"].extend(buffer)
                current, page, buffer = heading.group(1), number, [line.strip()]
            elif current:
                buffer.append(line.strip())

    if current and buffer:
        passages.setdefault(current, {"page": page, "lines": []})["lines"].extend(buffer)

    return {
        rule: {"page": data["page"], "text": " ".join(data["lines"])[:9000]}
        for rule, data in passages.items()
        if len(" ".join(data["lines"])) > 60
    }


def main():
    path = Path(LEGAL_PDF_PATH)
    if not path.exists():
        print(f"legal source not found at {path}")
        return

    enable_pgvector()
    Base.metadata.create_all(bind=engine)

    print(f"reading {path} with PaddleOCR (the scan has no text layer)")
    pages = dict(page_texts(path))
    passages = split_into_passages(pages)
    print(f"segmented into {len(passages)} rule passages")

    embeddings = llm.get_embeddings()
    db = SessionLocal()
    try:
        db.query(RulePassages).delete()
        embedded = 0
        for rule_ref, data in passages.items():
            record = RulePassages(rule_ref=rule_ref, pdf_page=data["page"], text=data["text"])
            if embeddings is not None:
                try:
                    record.embedding = embeddings.embed_query(f"Rule {rule_ref}: {data['text'][:2000]}")
                    embedded += 1
                except Exception:
                    embeddings = None
            db.add(record)
        db.commit()
    finally:
        db.close()

    print(f"stored     : {len(passages)} passages")
    print(f"embedded   : {embedded}" if embedded else "embedded   : skipped (no LLM API key configured)")
    print("passages are read from a scan, so retrieval quality depends on OCR")


if __name__ == "__main__":
    main()
