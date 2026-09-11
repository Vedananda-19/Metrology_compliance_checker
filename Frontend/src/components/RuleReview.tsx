import { useState } from "react";
import type { ApplicableRule } from "../types/inspection";
import StatusBadge from "./StatusBadge";

type Props = {
    rules: ApplicableRule[];
    editable: boolean;
    onDecide: (decisions: { rule_id: string; rule_version: number; officer_decision: string }[]) => void;
    onContinue: () => void;
    busy?: boolean;
};

const MODE_LABEL: Record<string, string> = {
    LABEL_AUTOMATED: "From label text",
    VISION_AUTOMATED: "From image analysis",
    MEASUREMENT_REQUIRED: "Physical measurement",
    MANUAL_INSPECTION: "Manual inspection",
    MANUAL_INPUT: "Officer input",
    EXTERNAL_LOOKUP: "Registry lookup",
};

const RuleReview = ({ rules, editable, onDecide, onContinue, busy }: Props) => {
    const [filter, setFilter] = useState<"all" | "checkable" | "manual">("all");

    const visible = rules.filter((rule) => {
        if (filter === "checkable") return rule.machine_checkable;
        if (filter === "manual") return !rule.machine_checkable;
        return true;
    });

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Applicable requirements</h2>
                    <p className="muted">
                        These provisions were selected by the rule engine from the scope and exemption conditions in the
                        2011 Rules. Normal cases need no action here.
                    </p>
                </div>
                <div className="filterRow">
                    {(["all", "checkable", "manual"] as const).map((value) => (
                        <button
                            key={value}
                            className={`chip ${filter === value ? "chipActive" : ""}`}
                            onClick={() => setFilter(value)}
                        >
                            {value === "all" ? "All" : value === "checkable" ? "Machine checkable" : "Needs a person"}
                        </button>
                    ))}
                </div>
            </div>

            <div className="ruleList">
                {visible.map((rule) => (
                    <article key={`${rule.rule_id}-${rule.rule_version}`} className="panel ruleCard">
                        <div className="ruleCardHead">
                            <div>
                                <span className="pill small">Rule {rule.provision}</span>
                                <h4>{rule.title}</h4>
                            </div>
                            <div className="ruleCardBadges">
                                <StatusBadge value={rule.status} size="small" />
                                <span className="muted small">{rule.severity}</span>
                            </div>
                        </div>

                        <dl className="ruleMeta">
                            <div>
                                <dt>Why it applies</dt>
                                <dd>{rule.why_it_applies}</dd>
                            </div>
                            <div>
                                <dt>How it is checked</dt>
                                <dd>{MODE_LABEL[rule.verification_mode ?? ""] ?? rule.verification_mode}</dd>
                            </div>
                            {rule.reason && (
                                <div>
                                    <dt>Engine note</dt>
                                    <dd>{rule.reason}</dd>
                                </div>
                            )}
                            {rule.threshold_source === "ENGINEERING_POLICY" && (
                                <div>
                                    <dt>Threshold</dt>
                                    <dd className="warnText">
                                        Depends on an implementation threshold, not a figure stated in the Rules
                                    </dd>
                                </div>
                            )}
                        </dl>

                        {editable && (
                            <div className="ruleActions">
                                {(["ACCEPTED", "UNCERTAIN", "REMOVED"] as const).map((decision) => (
                                    <button
                                        key={decision}
                                        className={`ghostButton tiny ${rule.officer_decision === decision ? "active" : ""}`}
                                        onClick={() =>
                                            onDecide([
                                                {
                                                    rule_id: rule.rule_id,
                                                    rule_version: rule.rule_version,
                                                    officer_decision: decision,
                                                },
                                            ])
                                        }
                                    >
                                        {decision === "ACCEPTED"
                                            ? "Accept"
                                            : decision === "UNCERTAIN"
                                              ? "Uncertain"
                                              : "Not applicable"}
                                    </button>
                                ))}
                            </div>
                        )}
                    </article>
                ))}
            </div>

            {editable && (
                <div className="actionBar">
                    <button className="primaryButton" onClick={onContinue} disabled={busy}>
                        Continue to findings
                    </button>
                </div>
            )}
        </div>
    );
};

export default RuleReview;
