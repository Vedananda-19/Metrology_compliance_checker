import { useState } from "react";
import type { Decision, Evaluation, Finding, FindingReview as Review, FindingStatus } from "../types/inspection";
import StatusBadge from "./StatusBadge";
import FindingReview from "./FindingReview";

const MODE_LABEL: Record<string, string> = {
    LABEL_AUTOMATED: "From label text",
    VISION_AUTOMATED: "From image analysis",
    MEASUREMENT_REQUIRED: "Needs physical measurement",
    MANUAL_INSPECTION: "Needs manual inspection",
    MANUAL_INPUT: "Needs officer input",
    EXTERNAL_LOOKUP: "Needs a registry lookup",
};

type Filter = FindingStatus | "ALL" | "REVIEW";

const FILTERS: { key: Filter; label: string }[] = [
    { key: "REVIEW", label: "Needs review" },
    { key: "NON_COMPLIANT", label: "Violations" },
    { key: "NOT_VERIFIABLE", label: "Not verifiable" },
    { key: "COMPLIANT", label: "Passed" },
    { key: "ALL", label: "All findings" },
];

type Props = {
    evaluation: Evaluation;
    reviews?: Review[];
    busy?: boolean;
    onReview?: (ruleId: string, decision: Decision | null, note: string) => void;
};

const cardTone = (finding: Finding, reviewed: boolean) => {
    if (reviewed) return "settled";
    if (finding.status === "NON_COMPLIANT") return "bad";
    if (finding.status === "NOT_VERIFIABLE") return "warn";
    if (finding.status === "COMPLIANT") return "good";
    return "muted";
};

const EvaluationView = ({ evaluation, reviews = [], busy, onReview }: Props) => {
    const [filter, setFilter] = useState<Filter>("REVIEW");

    const findings = evaluation.result.findings ?? [];
    const reviewOf = new Map(reviews.map((item) => [item.rule_id, item]));
    const needsReview = (finding: Finding) =>
        (finding.status === "NON_COMPLIANT" || finding.status === "NOT_VERIFIABLE") && !reviewOf.has(finding.rule_id);

    const counts = {
        COMPLIANT: findings.filter((f) => f.status === "COMPLIANT").length,
        NON_COMPLIANT: findings.filter((f) => f.status === "NON_COMPLIANT").length,
        NOT_VERIFIABLE: findings.filter((f) => f.status === "NOT_VERIFIABLE").length,
        REVIEW: findings.filter(needsReview).length,
    };

    const visible =
        filter === "ALL"
            ? findings
            : filter === "REVIEW"
              ? findings.filter(needsReview)
              : findings.filter((f) => f.status === filter);

    const actionable = findings.filter((f) => f.status === "NON_COMPLIANT" || f.status === "NOT_VERIFIABLE");
    const reviewedCount = actionable.filter((f) => reviewOf.has(f.rule_id)).length;

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Violations and findings</h2>
                    <p className="muted">{evaluation.result.summary}</p>
                </div>
                <StatusBadge value={evaluation.verdict} />
            </div>

            <div className="reviewProgress" role="status">
                <div className="reviewProgressTrack" aria-hidden="true">
                    <span
                        style={{
                            width: actionable.length ? `${Math.round((reviewedCount / actionable.length) * 100)}%` : "0%",
                        }}
                    />
                </div>
                <p>
                    <strong>
                        {reviewedCount} of {actionable.length}
                    </strong>{" "}
                    findings that need an officer decision have been reviewed.
                </p>
            </div>

            <div className="statRow compact">
                <button type="button" className="panel stat stat-bad" onClick={() => setFilter("NON_COMPLIANT")}>
                    <span className="statValue">{counts.NON_COMPLIANT}</span>
                    <span className="statLabel">Violations</span>
                </button>
                <button type="button" className="panel stat stat-warn" onClick={() => setFilter("NOT_VERIFIABLE")}>
                    <span className="statValue">{counts.NOT_VERIFIABLE}</span>
                    <span className="statLabel">Not verifiable</span>
                </button>
                <button type="button" className="panel stat stat-good" onClick={() => setFilter("COMPLIANT")}>
                    <span className="statValue">{counts.COMPLIANT}</span>
                    <span className="statLabel">Compliant</span>
                </button>
                <button type="button" className="panel stat" onClick={() => setFilter("REVIEW")}>
                    <span className="statValue">{counts.REVIEW}</span>
                    <span className="statLabel">Need review</span>
                </button>
            </div>

            <div className="filterRow">
                {FILTERS.map((item) => (
                    <button
                        key={item.key}
                        className={`chip ${filter === item.key ? "chipActive" : ""}`}
                        onClick={() => setFilter(item.key)}
                    >
                        {item.label}
                    </button>
                ))}
            </div>

            <div className="findingList">
                {visible.length === 0 && (
                    <p className="muted">
                        {filter === "REVIEW"
                            ? "Every finding that needed a decision has been reviewed."
                            : "Nothing in this filter."}
                    </p>
                )}
                {visible.map((finding) => {
                    const review = reviewOf.get(finding.rule_id);
                    return (
                        <article
                            key={`${finding.rule_id}-${finding.rule_ref}`}
                            className={`findingCard findingCard-${cardTone(finding, Boolean(review))}`}
                        >
                            <div className="findingHead">
                                <div>
                                    <span className="pill small">Rule {finding.rule_ref}</span>
                                    <strong>{finding.requirement}</strong>
                                </div>
                                <div className="findingBadges">
                                    <span className={`severityMark severity-${finding.severity.toLowerCase()}`}>
                                        {finding.severity}
                                    </span>
                                    <StatusBadge value={finding.status} size="small" />
                                </div>
                            </div>
                            {finding.observed && (
                                <p className="findingObserved">
                                    <span>Observed on the label</span>
                                    {finding.observed}
                                </p>
                            )}
                            <p className="findingExplain">{finding.explanation}</p>
                            <span className="muted tiny">
                                {MODE_LABEL[finding.verification_mode] ?? finding.verification_mode}
                                {finding.threshold_source === "ENGINEERING_POLICY" &&
                                    " · depends on an implementation threshold, not a figure in the Rules"}
                            </span>
                            {onReview && (
                                <FindingReview
                                    status={finding.status}
                                    review={review}
                                    busy={busy}
                                    onSave={(decision, note) => onReview(finding.rule_id, decision, note)}
                                />
                            )}
                        </article>
                    );
                })}
            </div>

            <p className="muted small">
                Judged by the deterministic rule engine against {evaluation.result.rules_evaluated ?? 0} rules in force
                from rule set {evaluation.result.rule_set_version}. A requirement that cannot be established from a
                photograph is reported as not verifiable, never as compliant.
            </p>
        </div>
    );
};

export default EvaluationView;
