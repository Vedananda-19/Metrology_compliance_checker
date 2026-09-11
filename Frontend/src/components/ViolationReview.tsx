import { useState } from "react";
import type { ComplianceSummary, Finding, ImageOcr, OcrRegion } from "../types/inspection";
import HighlightViewer from "./HighlightViewer";
import StatusBadge from "./StatusBadge";

type Props = {
    findings: Finding[];
    summary: ComplianceSummary | null;
    panels: ImageOcr[];
    imageUrls: Record<string, string>;
    editable: boolean;
    onDecide: (body: { findingId: string; officer_decision: string; officer_reason?: string }) => void;
    onContinue: () => void;
    busy?: boolean;
};

const asText = (value: unknown) => {
    if (value === null || value === undefined) return "";
    if (typeof value === "object") {
        const entries = Object.entries(value as Record<string, unknown>);
        if (!entries.length) return "";
        return entries.map(([key, item]) => `${key} = ${String(item)}`).join("; ");
    }
    return String(value);
};

const ViolationReview = ({
    findings,
    summary,
    panels,
    imageUrls,
    editable,
    onDecide,
    onContinue,
    busy,
}: Props) => {
    const [selected, setSelected] = useState<string | null>(null);
    const [reason, setReason] = useState("");

    const violations = findings.filter((item) => item.kind === "VIOLATION");
    const open = findings.filter((item) => item.kind === "RESULT");
    const active = findings.find((item) => item.id === selected) ?? violations[0] ?? null;

    const focus: { imageId: string | null; region: Partial<OcrRegion> | null } | null = (() => {
        const evidence = active?.evidence.find((item) => item.x1 !== null && item.image_id);
        if (!evidence) return null;
        return {
            imageId: evidence.image_id,
            region: { x1: evidence.x1!, y1: evidence.y1!, x2: evidence.x2!, y2: evidence.y2! },
        };
    })();

    const counts = summary?.counts ?? {};
    const pending = violations.filter((item) => item.officer_decision === "PENDING").length;

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Findings</h2>
                    <p className="muted">
                        Accept or reject each violation. If a declaration is visible on the package but the system
                        missed it, reject the violation and say so. Your decision is what the report records.
                    </p>
                </div>
                <StatusBadge value={summary?.final_verdict ?? summary?.automated_verdict} />
            </div>

            <div className="statRow compact">
                {[
                    ["Passed", counts.COMPLIANT ?? 0, "good"],
                    ["Failed", counts.NON_COMPLIANT ?? 0, "bad"],
                    ["Requires review", counts.REQUIRES_VERIFICATION ?? 0, "warn"],
                    ["Exempt", counts.EXEMPT ?? 0, "muted"],
                    ["Not applicable", counts.NOT_APPLICABLE ?? 0, "muted"],
                ].map(([label, value, tone]) => (
                    <div key={String(label)} className={`panel stat stat-${tone}`}>
                        <span className="statValue">{String(value)}</span>
                        <span className="statLabel">{String(label)}</span>
                    </div>
                ))}
            </div>

            <div className="splitView">
                <div className="panel splitLeft">
                    <HighlightViewer panels={panels} imageUrls={imageUrls} focus={focus} height={480} />
                    {active && !focus && (
                        <p className="muted small">
                            This finding has no image region. It is recorded because the declaration was not found on
                            any photographed panel.
                        </p>
                    )}
                </div>

                <div className="panel splitRight">
                    <h3>Violations ({violations.length})</h3>
                    {!violations.length && <p className="muted">No violation was raised for this package.</p>}

                    <div className="findingList">
                        {violations.map((finding) => (
                            <article
                                key={finding.id}
                                className={`inset findingCard ${active?.id === finding.id ? "findingActive" : ""}`}
                                onClick={() => {
                                    setSelected(finding.id);
                                    setReason(finding.officer_reason ?? "");
                                }}
                            >
                                <div className="findingHead">
                                    <div>
                                        <span className="pill small">Rule {finding.provision}</span>
                                        <strong>{finding.title}</strong>
                                    </div>
                                    <div className="findingBadges">
                                        <span className={`sevDot sev-${finding.severity?.toLowerCase()}`} />
                                        <span className="muted small">{finding.severity}</span>
                                        <StatusBadge value={finding.officer_decision} size="small" />
                                    </div>
                                </div>

                                <dl className="findingMeta">
                                    {finding.legal_requirement && (
                                        <div>
                                            <dt>Legal basis</dt>
                                            <dd>{finding.legal_requirement}</dd>
                                        </div>
                                    )}
                                    <div>
                                        <dt>Reference</dt>
                                        <dd>{finding.source_reference}</dd>
                                    </div>
                                    <div>
                                        <dt>Observed</dt>
                                        <dd>
                                            {asText(finding.observed_value) ||
                                                (finding.missing_facts.length
                                                    ? `Not declared (${finding.missing_facts.join(", ")})`
                                                    : "Not declared")}
                                        </dd>
                                    </div>
                                    {finding.confidence !== null && (
                                        <div>
                                            <dt>Confidence</dt>
                                            <dd>{Math.round(finding.confidence * 100)}%</dd>
                                        </div>
                                    )}
                                </dl>

                                {editable && active?.id === finding.id && (
                                    <div className="findingActions">
                                        <input
                                            className="inset"
                                            placeholder="Reason for your decision"
                                            value={reason}
                                            onChange={(event) => setReason(event.target.value)}
                                            onClick={(event) => event.stopPropagation()}
                                        />
                                        <div className="buttonRow">
                                            <button
                                                className="dangerButton tiny"
                                                onClick={(event) => {
                                                    event.stopPropagation();
                                                    onDecide({
                                                        findingId: finding.id,
                                                        officer_decision: "CONFIRMED",
                                                        officer_reason: reason,
                                                    });
                                                }}
                                            >
                                                Accept violation
                                            </button>
                                            <button
                                                className="ghostButton tiny"
                                                onClick={(event) => {
                                                    event.stopPropagation();
                                                    onDecide({
                                                        findingId: finding.id,
                                                        officer_decision: "OVERTURNED",
                                                        officer_reason: reason || "Declaration visible on the package",
                                                    });
                                                }}
                                            >
                                                Reject violation
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </article>
                        ))}
                    </div>

                    <h3>Not verifiable from the images ({open.length})</h3>
                    <p className="muted small">
                        These are not treated as compliant. They need measurement, a registry lookup or a physical
                        check.
                    </p>

                    <div className="findingList">
                        {open.map((finding) => (
                            <article
                                key={finding.id}
                                className={`inset findingCard subtle ${active?.id === finding.id ? "findingActive" : ""}`}
                                onClick={() => setSelected(finding.id)}
                            >
                                <div className="findingHead">
                                    <div>
                                        <span className="pill small">Rule {finding.provision}</span>
                                        <strong>{finding.title}</strong>
                                    </div>
                                    <StatusBadge value={finding.status} size="small" />
                                </div>
                                <p className="muted small">{finding.reason}</p>

                                {finding.llm_suggested_status && (
                                    <div className="advisory">
                                        <div className="advisoryHead">
                                            <span className="badge badge-info badgeSmall">Model suggestion</span>
                                            <span className="muted tiny">
                                                advisory only, it sets no status
                                                {finding.llm_confidence !== null &&
                                                    ` · ${Math.round(finding.llm_confidence * 100)}%`}
                                            </span>
                                        </div>
                                        <p>
                                            <strong>{finding.llm_suggested_status}</strong> — {finding.llm_reason}
                                        </p>
                                        {editable && (
                                            <div className="buttonRow">
                                                <button
                                                    className="ghostButton tiny"
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        onDecide({
                                                            findingId: finding.id,
                                                            officer_decision: "CONFIRMED",
                                                            officer_reason: "Accepted the model suggestion",
                                                        });
                                                    }}
                                                >
                                                    Accept suggestion
                                                </button>
                                                <button
                                                    className="ghostButton tiny"
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        onDecide({
                                                            findingId: finding.id,
                                                            officer_decision: "REMOVED",
                                                            officer_reason: "Rejected the model suggestion",
                                                        });
                                                    }}
                                                >
                                                    Reject
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </article>
                        ))}
                    </div>
                </div>
            </div>

            {editable && (
                <div className="actionBar">
                    {pending > 0 && (
                        <span className="muted small">{pending} violation(s) still need a decision</span>
                    )}
                    <button className="primaryButton" onClick={onContinue} disabled={busy || pending > 0}>
                        Continue to final review
                    </button>
                </div>
            )}
        </div>
    );
};

export default ViolationReview;
