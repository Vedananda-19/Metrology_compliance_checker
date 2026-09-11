import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useReport } from "../hooks/useInspection";
import api, { errorMessage } from "../apis/api";
import StatusBadge from "../components/StatusBadge";

const asText = (value: unknown) => {
    if (value === null || value === undefined) return "";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
};

const formatDate = (value: string | null | undefined) =>
    value ? new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "";

function Report() {
    const { id } = useParams();
    const { data, isLoading } = useReport(id);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");

    const download = async () => {
        setBusy(true);
        try {
            const response = await api.get(`/inspections/${id}/report/pdf`, { responseType: "blob" });
            const url = URL.createObjectURL(response.data);
            const link = document.createElement("a");
            link.href = url;
            link.download = `${data?.inspection.reference ?? "inspection"}.pdf`;
            link.click();
            URL.revokeObjectURL(url);
            setError("");
        } catch (caught) {
            setError(errorMessage(caught, "Could not generate the PDF"));
        } finally {
            setBusy(false);
        }
    };

    if (isLoading) return <div className="routeState"><h5>Loading report…</h5></div>;
    if (!data) return <div className="routeState"><h5>Report not available</h5></div>;

    const { inspection, declarations, findings, audit_logs: auditLogs } = data;
    const violations = findings.filter((item) => item.kind === "VIOLATION");
    const accepted = violations.filter((item) => item.officer_decision !== "OVERTURNED");
    const open = findings.filter((item) => item.kind === "RESULT");
    const counts = inspection.summary?.counts ?? {};

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <div className="inspectionTitleRow">
                        <h1>{inspection.reference}</h1>
                        <StatusBadge value={inspection.final_verdict ?? inspection.automated_verdict} />
                    </div>
                    <p className="muted">
                        {inspection.title || "Untitled package"} · {inspection.inspector_name} ·{" "}
                        {formatDate(inspection.finalized_at ?? inspection.created_at)}
                    </p>
                </div>
                <div className="buttonRow">
                    <Link className="ghostButton" to={`/inspection/${inspection.id}`}>
                        Open record
                    </Link>
                    <button className="primaryButton" onClick={download} disabled={busy}>
                        {busy ? "Preparing…" : "Download PDF"}
                    </button>
                </div>
            </section>

            {error && <p className="errorMessage">{error}</p>}

            {inspection.degraded_mode && (
                <div className="panel banner bannerDanger">
                    <strong>Deterministic evaluation did not run.</strong> This report is not a compliance
                    determination.
                </div>
            )}
            {inspection.development_mode && (
                <div className="panel banner bannerWarn">
                    <strong>Development extraction mode.</strong> Declarations came from the built-in pattern matcher
                    rather than a language model.
                </div>
            )}

            <section className="panel">
                <h2>Legal basis</h2>
                <div className="summaryGrid">
                    <div className="inset summaryCell">
                        <span className="muted small">Rule set</span>
                        <strong>{data.rule_set_title ?? "Legal Metrology (Packaged Commodities) Rules, 2011"}</strong>
                    </div>
                    <div className="inset summaryCell">
                        <span className="muted small">Version</span>
                        <strong>{inspection.rule_set_version}</strong>
                    </div>
                    <div className="inset summaryCell">
                        <span className="muted small">Judged as of</span>
                        <strong>{inspection.judged_as_of}</strong>
                    </div>
                    <div className="inset summaryCell">
                        <span className="muted small">Requirements evaluated</span>
                        <strong>{inspection.summary?.rules_evaluated}</strong>
                    </div>
                </div>
            </section>

            <section className="statRow compact">
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
            </section>

            {inspection.summary?.by_category?.length ? (
                <section className="panel">
                    <h2>By requirement group</h2>
                    <div className="tableScroll">
                        <table className="dataTable">
                            <thead>
                                <tr>
                                    <th>Group</th>
                                    <th>Passed</th>
                                    <th>Failed</th>
                                    <th>Review</th>
                                    <th>Exempt</th>
                                </tr>
                            </thead>
                            <tbody>
                                {inspection.summary.by_category.map((bucket) => (
                                    <tr key={bucket.category}>
                                        <td>{bucket.category}</td>
                                        <td>{bucket.passed}</td>
                                        <td>{bucket.failed}</td>
                                        <td>{bucket.review}</td>
                                        <td>{bucket.exempt}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </section>
            ) : null}

            <section className="panel">
                <h2>Violations ({accepted.length})</h2>
                {!accepted.length && <p className="muted">No violation was confirmed for this package.</p>}
                {accepted.map((item) => (
                    <article key={item.id} className="inset reportViolation">
                        <div className="findingHead">
                            <div>
                                <span className="pill small">Rule {item.provision}</span>
                                <strong>{item.title}</strong>
                            </div>
                            <span className="muted small">{item.severity}</span>
                        </div>
                        <dl className="findingMeta">
                            <div>
                                <dt>Legal basis</dt>
                                <dd>{item.legal_requirement}</dd>
                            </div>
                            <div>
                                <dt>Reference</dt>
                                <dd>{item.source_reference}</dd>
                            </div>
                            <div>
                                <dt>Inspector</dt>
                                <dd>
                                    {item.officer_decision} {item.officer_reason ? `· ${item.officer_reason}` : ""}
                                </dd>
                            </div>
                        </dl>
                    </article>
                ))}
            </section>

            <section className="panel">
                <h2>Not verifiable from the images ({open.length})</h2>
                <p className="muted small">
                    These provisions could not be decided from photographs and are not treated as compliant.
                </p>
                <div className="tableScroll">
                    <table className="dataTable">
                        <thead>
                            <tr>
                                <th>Rule</th>
                                <th>Requirement</th>
                                <th>Why</th>
                                <th>Mode</th>
                            </tr>
                        </thead>
                        <tbody>
                            {open.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.provision}</td>
                                    <td>{item.title}</td>
                                    <td className="muted small">{item.reason}</td>
                                    <td className="muted small">{item.verification_mode}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="panel">
                <h2>Declarations</h2>
                <div className="tableScroll">
                    <table className="dataTable">
                        <thead>
                            <tr>
                                <th>Declaration</th>
                                <th>Machine value</th>
                                <th>Confidence</th>
                                <th>Verified value</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {declarations.map((item) => (
                                <tr key={item.fact_path}>
                                    <td>{item.label}</td>
                                    <td>{asText(item.ai_value)}</td>
                                    <td>{item.ai_confidence !== null ? `${Math.round(item.ai_confidence * 100)}%` : ""}</td>
                                    <td>{asText(item.human_value)}</td>
                                    <td>
                                        <StatusBadge value={item.verification_status} size="small" />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            {inspection.inspector_observations && (
                <section className="panel">
                    <h2>Inspector observations</h2>
                    <p>{inspection.inspector_observations}</p>
                </section>
            )}

            <section className="panel">
                <h2>Audit trail</h2>
                <div className="tableScroll">
                    <table className="dataTable">
                        <thead>
                            <tr>
                                <th>When</th>
                                <th>Who</th>
                                <th>Action</th>
                                <th>Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            {auditLogs.map((entry) => (
                                <tr key={entry.id}>
                                    <td className="muted small">{formatDate(entry.created_at)}</td>
                                    <td>{entry.username}</td>
                                    <td>{entry.action.replace(/_/g, " ")}</td>
                                    <td className="muted small">
                                        {entry.old_value || entry.new_value
                                            ? `${asText(entry.old_value)} → ${asText(entry.new_value)}`
                                            : ""}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    );
}

export default Report;
