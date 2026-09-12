import { useState } from "react";
import type { Evaluation, FindingStatus } from "../types/inspection";
import StatusBadge from "./StatusBadge";

const MODE_LABEL: Record<string, string> = {
    LABEL_AUTOMATED: "From label text",
    VISION_AUTOMATED: "From image analysis",
    MEASUREMENT_REQUIRED: "Needs physical measurement",
    MANUAL_INSPECTION: "Needs manual inspection",
    MANUAL_INPUT: "Needs officer input",
    EXTERNAL_LOOKUP: "Needs a registry lookup",
};

const FILTERS: { key: FindingStatus | "ALL"; label: string }[] = [
    { key: "ALL", label: "All" },
    { key: "NON_COMPLIANT", label: "Violations" },
    { key: "NOT_VERIFIABLE", label: "Not verifiable" },
    { key: "COMPLIANT", label: "Passed" },
];

const EvaluationView = ({ evaluation }: { evaluation: Evaluation }) => {
    const [filter, setFilter] = useState<FindingStatus | "ALL">("ALL");

    const findings = evaluation.result.findings ?? [];
    const counts = {
        COMPLIANT: findings.filter((f) => f.status === "COMPLIANT").length,
        NON_COMPLIANT: findings.filter((f) => f.status === "NON_COMPLIANT").length,
        NOT_VERIFIABLE: findings.filter((f) => f.status === "NOT_VERIFIABLE").length,
    };
    const visible = filter === "ALL" ? findings : findings.filter((f) => f.status === filter);

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Compliance evaluation</h2>
                    <p className="muted">{evaluation.result.summary}</p>
                </div>
                <StatusBadge value={evaluation.verdict} />
            </div>

            <div className="statRow compact">
                <div className="panel stat stat-good">
                    <span className="statValue">{counts.COMPLIANT}</span>
                    <span className="statLabel">Compliant</span>
                </div>
                <div className="panel stat stat-bad">
                    <span className="statValue">{counts.NON_COMPLIANT}</span>
                    <span className="statLabel">Non-compliant</span>
                </div>
                <div className="panel stat stat-warn">
                    <span className="statValue">{counts.NOT_VERIFIABLE}</span>
                    <span className="statLabel">Not verifiable</span>
                </div>
                <div className="panel stat">
                    <span className="statValue">{evaluation.result.counts?.NOT_APPLICABLE ?? 0}</span>
                    <span className="statLabel">Not applicable</span>
                </div>
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
                {visible.map((finding) => (
                    <article key={`${finding.rule_id}-${finding.rule_ref}`} className="inset findingCard">
                        <div className="findingHead">
                            <div>
                                <span className="pill small">Rule {finding.rule_ref}</span>
                                <strong>{finding.requirement}</strong>
                            </div>
                            <div className="findingBadges">
                                <span className="muted small">{finding.severity}</span>
                                <StatusBadge value={finding.status} size="small" />
                            </div>
                        </div>
                        {finding.observed && <p className="muted small">Observed: {finding.observed}</p>}
                        <p>{finding.explanation}</p>
                        <span className="muted tiny">
                            {MODE_LABEL[finding.verification_mode] ?? finding.verification_mode}
                            {finding.threshold_source === "ENGINEERING_POLICY" &&
                                " · depends on an implementation threshold, not a figure in the Rules"}
                        </span>
                    </article>
                ))}
            </div>

            <p className="muted small">
                Judged by the deterministic rule engine against{" "}
                {evaluation.result.rules_evaluated ?? 0} rules in force from rule set{" "}
                {evaluation.result.rule_set_version}. A requirement that cannot be established from a photograph is
                reported as not verifiable, never as compliant.
            </p>
        </div>
    );
};

export default EvaluationView;
