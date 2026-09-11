type Props = {
    value: string | null | undefined;
    size?: "small" | "normal";
};

const TONE: Record<string, string> = {
    COMPLIANT: "good",
    NON_COMPLIANT: "bad",
    REQUIRES_VERIFICATION: "warn",
    REQUIRES_REVIEW: "warn",
    NOT_VERIFIABLE: "warn",
    PENDING: "warn",
    UNVERIFIED: "warn",
    EXEMPT: "muted",
    NOT_APPLICABLE: "muted",
    OBSERVATION: "muted",
    VERIFIED: "good",
    CONFIRMED: "bad",
    OVERTURNED: "muted",
    ACCEPTED: "good",
    REMOVED: "muted",
    UNCERTAIN: "warn",
    FINALIZED: "good",
    PROCESSING: "info",
    DRAFT: "muted",
};

const LABELS: Record<string, string> = {
    REQUIRES_VERIFICATION: "Not verifiable",
    NOT_APPLICABLE: "Not applicable",
    NON_COMPLIANT: "Non-compliant",
    REQUIRES_REVIEW: "Requires review",
    IMAGES_UPLOADED: "Images uploaded",
    IMAGE_REVIEW: "Image review",
    EXTRACTION_REVIEW: "Declaration review",
    CLASSIFICATION_REVIEW: "Classification review",
    RULE_REVIEW: "Rule review",
    COMPLIANCE_REVIEW: "Compliance review",
    VIOLATION_REVIEW: "Violation review",
    FINAL_REVIEW: "Final review",
};

export const readable = (value: string | null | undefined) => {
    if (!value) return "Pending";
    return LABELS[value] ?? value.charAt(0) + value.slice(1).toLowerCase().replace(/_/g, " ");
};

const StatusBadge = ({ value, size = "normal" }: Props) => {
    const tone = TONE[value ?? ""] ?? "muted";
    return <span className={`badge badge-${tone} ${size === "small" ? "badgeSmall" : ""}`}>{readable(value)}</span>;
};

export default StatusBadge;
