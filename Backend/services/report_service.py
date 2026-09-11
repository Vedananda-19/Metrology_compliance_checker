from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as PdfImage,
    PageBreak,
    KeepTogether,
)
from models import Reports, RuleSets, Users
from services import inspection_service, review_service, storage_service, audit_service
from datetime import datetime, timezone
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

STATUS_COLOURS = {
    "COMPLIANT": colors.HexColor("#1b7f4b"),
    "NON_COMPLIANT": colors.HexColor("#b32020"),
    "REQUIRES_VERIFICATION": colors.HexColor("#a86a00"),
    "REQUIRES_REVIEW": colors.HexColor("#a86a00"),
    "NOT_VERIFIABLE": colors.HexColor("#a86a00"),
    "EXEMPT": colors.HexColor("#4a5568"),
    "NOT_APPLICABLE": colors.HexColor("#6b7280"),
}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("Head", parent=base["Heading1"], fontSize=17, spaceAfter=4, textColor=colors.HexColor("#1a2433")))
    base.add(ParagraphStyle("Sub", parent=base["Normal"], fontSize=9, textColor=colors.HexColor("#5a6577")))
    base.add(ParagraphStyle("Section", parent=base["Heading2"], fontSize=12, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1a2433")))
    base.add(ParagraphStyle("Small", parent=base["Normal"], fontSize=8, leading=10))
    base.add(ParagraphStyle("Cell", parent=base["Normal"], fontSize=8, leading=10))
    base.add(ParagraphStyle("Banner", parent=base["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#8a4b00")))
    return base


def escape(value) -> str:
    text = "" if value is None else str(value)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def observed_text(finding) -> str:
    observed = finding.observed_value
    if isinstance(observed, dict) and observed:
        return "; ".join(f"{key} = {value}" for key, value in observed.items())
    if observed:
        return str(observed)
    absent = [item.fact_path for item in finding.evidence if item.kind == "ABSENT_DECLARATION"]
    if absent:
        return "Not declared on any photographed panel (" + ", ".join(absent) + ")"
    return "Not declared"


def grid(data, widths, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d0da")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8ecf2")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    table.setStyle(TableStyle(style))
    return table


def evidence_crop(db, inspection_id: str, item, max_width=150 * mm):
    if not item.image_id or item.x1 is None:
        return None
    try:
        import cv2
        import numpy as np

        image = inspection_service.get_image(db, inspection_id, item.image_id)
        data = storage_service.download(image.storage_path)
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return None

        height, width = frame.shape[:2]
        pad_x = max(int((item.x2 - item.x1) * 0.35), 40)
        pad_y = max(int((item.y2 - item.y1) * 1.6), 30)
        x1 = max(item.x1 - pad_x, 0)
        y1 = max(item.y1 - pad_y, 0)
        x2 = min(item.x2 + pad_x, width)
        y2 = min(item.y2 + pad_y, height)

        cv2.rectangle(frame, (item.x1, item.y1), (item.x2, item.y2), (0, 0, 220), 3)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None

        ok, buffer = cv2.imencode(".png", crop)
        if not ok:
            return None

        crop_height, crop_width = crop.shape[:2]
        display_width = min(max_width, crop_width * 0.45)
        display_height = display_width * crop_height / crop_width
        return PdfImage(BytesIO(buffer.tobytes()), width=display_width, height=display_height)
    except Exception:
        logger.exception("Evidence crop failed")
        return None


def panel_image(db, inspection_id: str, image, box=60 * mm):
    try:
        data = storage_service.download(image.storage_path)
        import cv2
        import numpy as np

        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return None
        height, width = frame.shape[:2]
        scale = min(box / width, box / height)
        ok, buffer = cv2.imencode(".png", frame)
        if not ok:
            return None
        return PdfImage(BytesIO(buffer.tobytes()), width=width * scale, height=height * scale)
    except Exception:
        logger.exception("Panel image failed")
        return None


def build(db, inspection_id: str, user) -> bytes:
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    product = inspection_service.get_product(db, inspection_id)
    summary = review_service.summary(db, inspection_id, inspection)
    declarations = review_service.declarations(db, inspection_id)
    findings = review_service.findings(db, inspection_id)
    rules = review_service.rules(db, inspection_id)
    logs = audit_service.history(db, inspection_id)
    rule_set = db.query(RuleSets).filter(RuleSets.rule_set_version == inspection.rule_set_version).first()
    inspector = db.query(Users).filter(Users.id == inspection.user_id).first()

    s = styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"Legal Metrology Inspection {inspection.reference}",
    )
    story = []

    verdict = inspection.final_verdict or inspection.automated_verdict or "PENDING"
    story.append(Paragraph("Legal Metrology Inspection Report", s["Head"]))
    story.append(Paragraph("Packaged Commodity Compliance Assessment", s["Sub"]))
    story.append(Spacer(1, 8))

    if inspection.degraded_mode:
        story.append(Paragraph(
            "<b>Deterministic evaluation did not run.</b> The rule engine failed for this inspection, so "
            "every finding below is provisional and requires full manual verification. This document is "
            "not a compliance determination.", s["Banner"]))
        story.append(Spacer(1, 6))
    if inspection.development_mode:
        story.append(Paragraph(
            "<b>Development extraction mode.</b> No language model was configured, so declarations were "
            "extracted by the built-in pattern matcher. OCR, the rule engine and all findings are genuine.",
            s["Banner"]))
        story.append(Spacer(1, 6))

    story.append(grid([
        ["Inspection ID", escape(inspection.reference), "Status", escape(inspection.status)],
        ["Overall result", escape(verdict), "Automated result", escape(inspection.automated_verdict)],
        ["Inspector", escape((inspector.full_name or inspector.username) if inspector else ""), "Designation", escape(inspector.designation if inspector else "")],
        ["Created", inspection.created_at.strftime("%d %b %Y %H:%M") if inspection.created_at else "", "Finalized", inspection.finalized_at.strftime("%d %b %Y %H:%M") if inspection.finalized_at else "Not finalized"],
        ["Location", escape(inspection.location), "Judged as of", str(inspection.judged_as_of or "")],
    ], [30 * mm, 55 * mm, 30 * mm, 55 * mm], header=False))

    story.append(Paragraph("Legal basis", s["Section"]))
    story.append(grid([
        ["Rule set", Paragraph(escape(rule_set.title if rule_set else "Legal Metrology (Packaged Commodities) Rules, 2011"), s["Cell"])],
        ["Version", escape(inspection.rule_set_version)],
        ["Legal basis", escape(rule_set.legal_basis if rule_set else "")],
        ["Content hash", escape((rule_set.content_sha256 or "")[:32] if rule_set else "")],
    ], [35 * mm, 135 * mm], header=False))

    story.append(Paragraph("Product", s["Section"]))
    story.append(grid([
        ["Common name", escape(product.common_name if product else ""), "Brand", escape(product.brand if product else "")],
        ["Category", escape(product.category if product else ""), "Physical state", escape(product.physical_state if product else "")],
        ["Commodity tags", escape(", ".join((product.human_override_tags or product.tags or [])) if product else ""), "Classification", escape(f"{product.classification_source} ({product.classification_confidence})" if product else "")],
    ], [30 * mm, 55 * mm, 30 * mm, 55 * mm], header=False))

    story.append(Paragraph("Compliance summary", s["Section"]))
    counts = summary.counts
    story.append(grid([
        ["Passed", "Failed", "Requires review", "Not applicable", "Exempt", "Manual checklist"],
        [
            str(counts.get("COMPLIANT", 0)),
            str(counts.get("NON_COMPLIANT", 0)),
            str(counts.get("REQUIRES_VERIFICATION", 0)),
            str(counts.get("NOT_APPLICABLE", 0)),
            str(counts.get("EXEMPT", 0)),
            str(summary.open_manual_checklist),
        ],
    ], [28 * mm, 28 * mm, 32 * mm, 30 * mm, 25 * mm, 30 * mm]))

    if summary.by_category:
        story.append(Spacer(1, 8))
        rows = [["Requirement group", "Passed", "Failed", "Review", "Exempt"]]
        for bucket in summary.by_category:
            rows.append([bucket["category"], str(bucket["passed"]), str(bucket["failed"]), str(bucket["review"]), str(bucket["exempt"])])
        story.append(grid(rows, [78 * mm, 23 * mm, 23 * mm, 23 * mm, 23 * mm]))

    story.append(Paragraph("Declarations read from the package", s["Section"]))
    story.append(Paragraph(
        "The model value is what the system extracted. The verified value is what the inspector confirmed "
        "or corrected. Both are retained.", s["Sub"]))
    story.append(Spacer(1, 4))
    rows = [["Declaration", "Model value", "Confidence", "Verified value", "Status"]]
    for item in declarations:
        rows.append([
            Paragraph(escape(item.label), s["Cell"]),
            Paragraph(escape(item.ai_value), s["Cell"]),
            f"{item.ai_confidence:.2f}" if item.ai_confidence is not None else "",
            Paragraph(escape(item.human_value if item.human_value is not None else ""), s["Cell"]),
            item.verification_status,
        ])
    story.append(grid(rows, [38 * mm, 48 * mm, 18 * mm, 42 * mm, 24 * mm]))

    confirmed = [f for f in findings if f.kind == "VIOLATION" and f.officer_decision != "OVERTURNED"]
    overturned = [f for f in findings if f.kind == "VIOLATION" and f.officer_decision == "OVERTURNED"]
    open_items = [f for f in findings if f.kind == "RESULT"]

    story.append(PageBreak())
    story.append(Paragraph(f"Violations ({len(confirmed)})", s["Section"]))
    if not confirmed:
        story.append(Paragraph("No violation was confirmed for this package.", s["Normal"]))

    for finding in sorted(confirmed, key=lambda f: SEVERITY_ORDER.get(f.severity, 9)):
        block = [Paragraph(f"<b>{escape(finding.title)}</b>", s["Normal"])]
        block.append(grid([
            ["Rule", escape(finding.provision), "Severity", escape(finding.severity)],
            ["Legal basis", Paragraph(escape(finding.legal_requirement), s["Cell"]), "Reference", escape(finding.source_reference)],
            ["Observed", Paragraph(escape(observed_text(finding)), s["Cell"]), "Confidence", f"{finding.confidence:.2f}" if finding.confidence is not None else ""],
            ["Inspector", escape(finding.officer_decision), "Reason", Paragraph(escape(finding.officer_reason), s["Cell"])],
        ], [24 * mm, 61 * mm, 24 * mm, 61 * mm], header=False))

        for item in finding.evidence[:2]:
            if item.kind == "ABSENT_DECLARATION":
                block.append(Paragraph(f"Evidence: {escape(item.fact_path)} not found on any usable panel.", s["Small"]))
                continue
            crop = evidence_crop(db, inspection_id, item)
            if crop is not None:
                block.append(Spacer(1, 3))
                block.append(Paragraph(f"Evidence: {escape(item.observed_text)}", s["Small"]))
                block.append(crop)
        block.append(Spacer(1, 10))
        story.append(KeepTogether(block))

    if overturned:
        story.append(Paragraph(f"Violations rejected by the inspector ({len(overturned)})", s["Section"]))
        rows = [["Rule", "Requirement", "Reason given"]]
        for finding in overturned:
            rows.append([
                escape(finding.provision),
                Paragraph(escape(finding.title), s["Cell"]),
                Paragraph(escape(finding.officer_reason), s["Cell"]),
            ])
        story.append(grid(rows, [26 * mm, 70 * mm, 74 * mm]))

    story.append(Paragraph(f"Requirements not verifiable from the images ({len(open_items)})", s["Section"]))
    story.append(Paragraph(
        "These provisions could not be decided from photographs. They are not treated as compliant.", s["Sub"]))
    story.append(Spacer(1, 4))
    rows = [["Rule", "Requirement", "Why", "Mode", "Inspector"]]
    for finding in open_items:
        rows.append([
            Paragraph(escape(finding.provision), s["Cell"]),
            Paragraph(escape(finding.title), s["Cell"]),
            Paragraph(escape(finding.reason), s["Cell"]),
            Paragraph(escape(finding.verification_mode).replace("_", " ").title(), s["Cell"]),
            Paragraph(escape(finding.officer_decision or "Open"), s["Cell"]),
        ])
    story.append(grid(rows, [30 * mm, 48 * mm, 42 * mm, 30 * mm, 20 * mm]))

    advisory = [f for f in open_items if f.llm_suggested_status]
    if advisory:
        story.append(Paragraph("Model suggestions (advisory only)", s["Section"]))
        story.append(Paragraph(
            "These are suggestions from a language model shown to the inspector. They did not set any "
            "status and are not compliance determinations.", s["Sub"]))
        story.append(Spacer(1, 4))
        rows = [["Rule", "Suggested", "Confidence", "Reasoning"]]
        for finding in advisory:
            rows.append([
                escape(finding.provision),
                escape(finding.llm_suggested_status),
                f"{finding.llm_confidence:.2f}" if finding.llm_confidence is not None else "",
                Paragraph(escape(finding.llm_reason), s["Cell"]),
            ])
        story.append(grid(rows, [24 * mm, 30 * mm, 20 * mm, 96 * mm]))

    story.append(PageBreak())
    story.append(Paragraph("Package images", s["Section"]))
    images = inspection_service.list_images(db, inspection_id)
    row = []
    for image in images:
        rendered = panel_image(db, inspection_id, image)
        if rendered is not None:
            row.append([rendered, Paragraph(f"{escape(image.panel)} — {escape(image.usability)}", s["Small"])])
    if row:
        cells = [[entry[0] for entry in row[:3]], [entry[1] for entry in row[:3]]]
        story.append(Table(cells, colWidths=[58 * mm] * len(cells[0])))

    if inspection.inspector_observations:
        story.append(Paragraph("Inspector observations", s["Section"]))
        story.append(Paragraph(escape(inspection.inspector_observations), s["Normal"]))

    story.append(Paragraph("Audit trail", s["Section"]))
    rows = [["When", "Who", "Action", "Detail"]]
    for entry in logs:
        detail = ""
        if entry.old_value or entry.new_value:
            detail = f"{entry.old_value} -> {entry.new_value}"
        rows.append([
            entry.created_at.strftime("%d %b %H:%M") if entry.created_at else "",
            escape((inspector.full_name or inspector.username) if inspector else ""),
            escape(entry.action),
            Paragraph(escape(detail)[:400], s["Cell"]),
        ])
    story.append(grid(rows, [24 * mm, 30 * mm, 40 * mm, 76 * mm]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Generated {datetime.now(timezone.utc).strftime('%d %b %Y %H:%M UTC')} from inspection record "
        f"{escape(inspection.reference)}. Thresholds marked ENGINEERING_POLICY are implementation choices, "
        f"not requirements of the Rules.", s["Sub"]))

    doc.build(story)
    return buffer.getvalue()


def generate_and_store(db, inspection_id: str, user):
    data = build(db, inspection_id, user)
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    storage_path = f"reports/{inspection.id}/{inspection.reference}.pdf"

    try:
        storage_service.upload(storage_path, data, "application/pdf")
    except Exception:
        logger.exception("Report upload failed")
        storage_path = None

    record = db.query(Reports).filter(Reports.inspection_id == inspection_id).first()
    if record is None:
        record = Reports(inspection_id=inspection_id)
        db.add(record)
    record.rule_set_version = inspection.rule_set_version
    record.storage_path = storage_path
    record.summary = review_service.summary(db, inspection_id, inspection).model_dump()
    record.generated_at = datetime.now(timezone.utc)
    db.commit()
    return data
