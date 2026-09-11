import { useState } from "react";
import type { ApplicableRule, Declaration, Finding, InspectionDetail } from "../types/inspection";
import StatusBadge from "./StatusBadge";

type Props = {
    inspection: InspectionDetail;
    declarations: Declaration[];
    rules: ApplicableRule[];
    findings: Finding[];
    editable: boolean;
    busy?: boolean;
    error?: string;
    onBack: () => void;
    onFinalize: (observations: string) => void;
};

const asText = (value: unknown) => {
    if (value === null || value === undefined) return "";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
};

const FinalReview = ({ inspection, declarations, rules, findings, editable, busy, error, onBack, onFinalize }: Props) => {
    const [observations, setObservations] = useState(inspection.inspector_observations ?? "");

    const accepted = findings.filter((item) => item.kind === "VIOLATION" && item.officer_decision === "CONFIRMED");
    const rejected = findings.filter((item) => item.kind === "VIOLATION" && item.officer_decision === "OVERTURNED");
    const pending = findings.filter((item) => item.kind === "VIOLATION" && item.officer_decision === "PENDING");
    const unresolved = findings.filter((item) => item.kind === "RESULT" && !item.officer_decision);
    const corrected = declarations.filter((item) => item.verification_status === "VERIFIED");

    const expected = accepted.length ? "NON_COMPLIANT" : unresolved.length ? "REQUIRES_REVIEW" : "COMPLIANT";

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Final review</h2>
                    <p className="muted">
                        Check the record before finalising. A finalised inspection cannot be edited afterwards.
                    </p>
                </div>
                <StatusBadge value={expected} />
            </div>

            <div className="summaryGrid">
                <div className="inset summaryCell">
                    <span className="muted small">Package</span>
                    <strong>{inspection.title || "Untitled"}</strong>
                    <span className="muted small">{inspection.product?.common_name}</span>
                </div>
                <div className="inset summaryCell">
                    <span className="muted small">Images</span>
                    <strong>{inspection.images.filter((image) => image.usability === "USABLE").length} usable</strong>
                    <span className="muted small">{inspection.images.length} uploaded</span>
                </div>
                <div className="inset summaryCell">
                    <span className="muted small">Requirements evaluated</span>
                    <strong>{inspection.summary?.rules_evaluated ?? rules.length}</strong>
                    <span className="muted small">rule set {inspection.rule_set_version}</span>
                </div>
                <div className="inset summaryCell">
                    <span className="muted small">Inspector</span>
                    <strong>{inspection.inspector_name}</strong>
                    <span className="muted small">{inspection.location}</span>
                </div>
            </div>

            <div className="reviewColumns">
                <section>
                    <h3>Accepted violations ({accepted.length})</h3>
                    {!accepted.length && <p className="muted small">None.</p>}
                    <ul className="plainList">
                        {accepted.map((item) => (
                            <li key={item.id} className="inset listRow">
                                <span className="pill small">Rule {item.provision}</span>
                                <span>{item.title}</span>
                                <span className="muted small">{item.severity}</span>
                            </li>
                        ))}
                    </ul>

                    <h3>Rejected violations ({rejected.length})</h3>
                    {!rejected.length && <p className="muted small">None.</p>}
                    <ul className="plainList">
                        {rejected.map((item) => (
                            <li key={item.id} className="inset listRow">
                                <span className="pill small">Rule {item.provision}</span>
                                <span>{item.title}</span>
                                <span className="muted small">{item.officer_reason}</span>
                            </li>
                        ))}
                    </ul>
                </section>

                <section>
                    <h3>Corrected declarations ({corrected.length})</h3>
                    {!corrected.length && <p className="muted small">No declaration was corrected.</p>}
                    <ul className="plainList">
                        {corrected.map((item) => (
                            <li key={item.fact_path} className="inset listRow column">
                                <strong>{item.label}</strong>
                                <span className="muted small">Machine read: {asText(item.ai_value) || "nothing"}</span>
                                <span>Verified: {asText(item.human_value)}</span>
                            </li>
                        ))}
                    </ul>

                    <h3>Unresolved requirements ({unresolved.length})</h3>
                    <p className="muted small">
                        These stay on the record as requiring verification. They are not counted as compliant.
                    </p>
                </section>
            </div>

            <label className="fieldLabel">
                Inspector observations
                <textarea
                    className="inset"
                    rows={4}
                    value={observations}
                    disabled={!editable}
                    onChange={(event) => setObservations(event.target.value)}
                    placeholder="Anything the record should carry beyond the automated findings"
                />
            </label>

            {pending.length > 0 && (
                <p className="warnText">{pending.length} violation(s) still need an accept or reject decision.</p>
            )}
            {error && <p className="errorMessage">{error}</p>}

            {editable && (
                <div className="actionBar">
                    <button className="ghostButton" onClick={onBack}>
                        Send back for review
                    </button>
                    <button
                        className="primaryButton"
                        onClick={() => onFinalize(observations)}
                        disabled={busy || pending.length > 0}
                    >
                        {busy ? "Finalising…" : "Approve and finalize"}
                    </button>
                </div>
            )}
        </div>
    );
};

export default FinalReview;
