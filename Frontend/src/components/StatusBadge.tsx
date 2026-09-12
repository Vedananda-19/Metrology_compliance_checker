const TONE: Record<string, string> = {
    COMPLIANT: "good",
    NON_COMPLIANT: "bad",
    NOT_VERIFIABLE: "warn",
    REQUIRES_VERIFICATION: "warn",
    EXEMPT: "muted",
    OBSERVATION: "muted",
    NOT_APPLICABLE: "muted",
    REQUIRES_REVIEW: "warn",
    COMPLETED: "good",
    PROCESSING: "info",
    FAILED: "bad",
    DRAFT: "muted",
};

const LABELS: Record<string, string> = {
    NON_COMPLIANT: "Non-compliant",
    REQUIRES_VERIFICATION: "Not verifiable",
    NOT_VERIFIABLE: "Not verifiable",
    REQUIRES_REVIEW: "Requires review",
};

const StatusBadge = ({ value, size = "normal" }: { value: string | null | undefined; size?: "small" | "normal" }) => {
    if (!value) return null;
    const label = LABELS[value] ?? value.charAt(0) + value.slice(1).toLowerCase().replace(/_/g, " ");
    return <span className={`badge badge-${TONE[value] ?? "muted"} ${size === "small" ? "badgeSmall" : ""}`}>{label}</span>;
};

export default StatusBadge;
