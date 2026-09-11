export type InspectionStatus =
    | "DRAFT"
    | "IMAGES_UPLOADED"
    | "IMAGE_REVIEW"
    | "PROCESSING"
    | "EXTRACTION_REVIEW"
    | "CLASSIFICATION_REVIEW"
    | "RULE_REVIEW"
    | "COMPLIANCE_REVIEW"
    | "VIOLATION_REVIEW"
    | "FINAL_REVIEW"
    | "FINALIZED";

export type ComplianceStatus =
    | "COMPLIANT"
    | "NON_COMPLIANT"
    | "REQUIRES_VERIFICATION"
    | "REQUIRES_REVIEW"
    | "NOT_APPLICABLE"
    | "EXEMPT"
    | "OBSERVATION";

export type Usability = "PENDING" | "USABLE" | "RETAKE" | "REMOVED";

export interface User {
    id: string;
    username: string;
    full_name: string | null;
    designation: string | null;
    office: string | null;
}

export interface InspectionImage {
    id: string;
    panel: string | null;
    display_order: number;
    usability: Usability;
    review_note: string | null;
    width_px: number | null;
    height_px: number | null;
    ocr_status: string;
    mean_ocr_confidence: number | null;
    original_filename: string | null;
    url: string | null;
}

export interface OcrRegion {
    id: string;
    image_id: string;
    text: string;
    confidence: number;
    polygon: number[][];
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface ImageOcr {
    image: InspectionImage;
    regions: OcrRegion[];
}

export interface Product {
    id: string;
    brand: string | null;
    common_name: string | null;
    category: string | null;
    tags: string[];
    physical_state: string | null;
    classification_confidence: number | null;
    classification_source: string | null;
    human_override_tags: string[] | null;
}

export interface Declaration {
    fact_path: string;
    label: string;
    ai_value: unknown;
    ai_confidence: number | null;
    human_value: unknown;
    effective_value: unknown;
    verification_status: "UNVERIFIED" | "VERIFIED" | "REJECTED";
    extractor: string | null;
    image_id: string | null;
    region_id: string | null;
    bbox: number[] | null;
    verified_at: string | null;
}

export interface ApplicableRule {
    rule_id: string;
    rule_version: number;
    title: string;
    provision: string | null;
    severity: string | null;
    verification_mode: string | null;
    threshold_source: string | null;
    status: ComplianceStatus;
    queue: string | null;
    reason: string | null;
    exemption_ref: string | null;
    machine_checkable: boolean;
    why_it_applies: string | null;
    officer_decision: string | null;
}

export interface EvidenceItem {
    id: string;
    image_id: string | null;
    region_id: string | null;
    fact_path: string | null;
    observed_text: string | null;
    kind: string;
    note: string | null;
    x1: number | null;
    y1: number | null;
    x2: number | null;
    y2: number | null;
    polygon: number[][] | null;
}

export interface Finding {
    id: string;
    kind: "VIOLATION" | "RESULT";
    rule_id: string;
    rule_version: number;
    title: string;
    provision: string | null;
    severity: string | null;
    confidence: number | null;
    status: ComplianceStatus;
    queue: string | null;
    reason: string | null;
    observed_value: unknown;
    expected: string | null;
    legal_requirement: string | null;
    source_reference: string | null;
    llm_explanation: string | null;
    llm_suggested_status: string | null;
    llm_reason: string | null;
    llm_confidence: number | null;
    officer_decision: string | null;
    officer_reason: string | null;
    evidence: EvidenceItem[];
    missing_facts: string[];
    threshold_source: string | null;
    verification_mode: string | null;
}

export interface CategoryBreakdown {
    category: string;
    passed: number;
    failed: number;
    review: number;
    exempt: number;
}

export interface ComplianceSummary {
    automated_verdict: string | null;
    final_verdict: string | null;
    counts: Record<string, number>;
    by_category: CategoryBreakdown[];
    open_manual_checklist: number;
    rules_evaluated: number;
}

export interface Inspection {
    id: string;
    reference: string;
    title: string | null;
    location: string | null;
    status: InspectionStatus;
    rule_set_version: string | null;
    judged_as_of: string | null;
    automated_verdict: string | null;
    final_verdict: string | null;
    development_mode: boolean;
    degraded_mode: boolean;
    processing_error: string | null;
    inspector_observations: string | null;
    finalized_at: string | null;
    created_at: string | null;
    updated_at: string | null;
    inspector_name: string | null;
    image_count: number;
    violation_count: number;
}

export interface InspectionDetail extends Inspection {
    images: InspectionImage[];
    product: Product | null;
    summary: ComplianceSummary | null;
    processing_log: ProcessingEvent[];
}

export interface ProcessingEvent {
    step: string;
    status: "processing" | "completed" | "failed";
    message: string;
    at: string;
    done?: boolean;
    [key: string]: unknown;
}

export interface AuditEntry {
    id: string;
    action: string;
    target: string | null;
    old_value: unknown;
    new_value: unknown;
    source: string;
    created_at: string;
    username: string | null;
}

export interface ReportPayload {
    inspection: InspectionDetail;
    declarations: Declaration[];
    rules: ApplicableRule[];
    findings: Finding[];
    audit_logs: AuditEntry[];
    rule_set_title: string | null;
    generated_at: string | null;
}

export const STEP_LABELS: Record<string, string> = {
    IMAGE_RECEIVED: "Images received",
    PREPROCESSING: "Preprocessing",
    OCR: "Text extraction",
    DECLARATION_EXTRACTION: "Declarations extracted",
    PRODUCT_CLASSIFICATION: "Product classified",
    RULE_IDENTIFICATION: "Applicable rules identified",
    COMPLIANCE_ANALYSIS: "Compliance evaluated",
    EVIDENCE_GENERATION: "Evidence linked",
    REPORT_GENERATION: "Report prepared",
};

export const PROCESSING_STEPS = Object.keys(STEP_LABELS);

export const STATUS_STEPS: { status: InspectionStatus; label: string }[] = [
    { status: "DRAFT", label: "Create" },
    { status: "IMAGE_REVIEW", label: "Verify images" },
    { status: "PROCESSING", label: "Process" },
    { status: "EXTRACTION_REVIEW", label: "Declarations" },
    { status: "RULE_REVIEW", label: "Rules" },
    { status: "VIOLATION_REVIEW", label: "Findings" },
    { status: "FINAL_REVIEW", label: "Approve" },
    { status: "FINALIZED", label: "Report" },
];
