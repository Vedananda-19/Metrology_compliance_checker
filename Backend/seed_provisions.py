from database import SessionLocal, Base, engine, enable_pgvector, IS_POSTGRES
from models import LegalProvisions
from pipeline import preprocess, ocr, llm
from config import LEGAL_PDF_PATH
from pathlib import Path
import re

RULE_HEADING = re.compile(r"^\s*(\d{1,2})\s*\.\s+(.{4,})", re.IGNORECASE)
SCALE = 2.2


def page_images(path: Path):
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(path))
    for index in range(len(document)):
        image = document[index].render(scale=SCALE).to_pil()
        yield index + 1, image


def ocr_page(image):
    import io

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    prepared = preprocess.prepare(buffer.getvalue())
    result = ocr.run(prepared)
    if result["status"] != "DONE":
        return ""
    return "\n".join(region["text"] for region in result["regions"])


def split_into_provisions(pages: dict[int, str]):
    provisions = {}
    current_rule = None
    buffer = []
    first_page = None

    for page_number in sorted(pages):
        for line in pages[page_number].splitlines():
            heading = RULE_HEADING.match(line.strip())
            if heading:
                if current_rule and buffer:
                    provisions.setdefault(current_rule, {"page": first_page, "lines": []})["lines"].extend(buffer)
                current_rule = heading.group(1)
                first_page = page_number
                buffer = [line.strip()]
            elif current_rule:
                buffer.append(line.strip())

    if current_rule and buffer:
        provisions.setdefault(current_rule, {"page": first_page, "lines": []})["lines"].extend(buffer)

    return {
        rule: {"page": data["page"], "text": " ".join(data["lines"])[:6000]}
        for rule, data in provisions.items()
        if len(" ".join(data["lines"])) > 60
    }


def write_embeddings(db, records):
    embeddings = llm.get_embeddings()
    if embeddings is None or not IS_POSTGRES:
        return 0

    written = 0
    for record in records:
        if record.embedding is not None or not record.text:
            continue
        try:
            record.embedding = embeddings.embed_query(f"Rule {record.rule_ref}: {record.text[:2000]}")
            written += 1
        except Exception:
            break
    return written


def main():
    path = Path(LEGAL_PDF_PATH)
    if not path.exists():
        print(f"legal source not found at {path}")
        print("citations still work from the rule excerpts seeded by seed_rules.py")
        return

    enable_pgvector()
    Base.metadata.create_all(bind=engine)

    print(f"reading {path} with PaddleOCR (the scan has no text layer)")
    pages = {}
    for page_number, image in page_images(path):
        text = ocr_page(image)
        pages[page_number] = text
        print(f"  page {page_number:>2}: {len(text):>5} characters")

    provisions = split_into_provisions(pages)
    print(f"segmented into {len(provisions)} rule passages")

    db = SessionLocal()
    try:
        enriched = 0
        for rule_number, data in provisions.items():
            matches = (
                db.query(LegalProvisions)
                .filter(LegalProvisions.rule_ref.like(f"{rule_number}(%"))
                .all()
            )
            exact = db.query(LegalProvisions).filter(LegalProvisions.rule_ref == rule_number).first()
            if exact:
                matches.append(exact)

            for record in matches:
                if record.text_source == "pdf_ocr":
                    continue
                record.text = f"{record.text}\n\n[Read from the scanned source, page {data['page']}]\n{data['text']}"
                record.text_source = "pdf_ocr"
                record.pdf_page = record.pdf_page or data["page"]
                enriched += 1

        embedded = write_embeddings(db, db.query(LegalProvisions).all())
        db.commit()
    finally:
        db.close()

    print(f"enriched   : {enriched} provision rows with OCRed source text")
    print(f"embedded   : {embedded} rows" if embedded else "embedded   : skipped (needs Postgres and an LLM API key)")
    print("passages read from a scan are labelled pdf_ocr and shown as supporting context, not as authoritative text")


if __name__ == "__main__":
    main()
