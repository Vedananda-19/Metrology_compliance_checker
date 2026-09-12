import type { Evaluation } from "../types/inspection";
import StatusBadge from "./StatusBadge";

const EvaluationView = ({ evaluation }: { evaluation: Evaluation }) => {
    const findings = evaluation.result.findings ?? [];
    const counts = {
        COMPLIANT: findings.filter((f) => f.status === "COMPLIANT").length,
        NON_COMPLIANT: findings.filter((f) => f.status === "NON_COMPLIANT").length,
        NOT_VERIFIABLE: findings.filter((f) => f.status === "NOT_VERIFIABLE").length,
    };

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Evaluation</h2>
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
            </div>

            <div className="findingList">
                {findings.map((finding, index) => (
                    <article key={`${finding.rule_ref}-${index}`} className="inset findingCard">
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
                    </article>
                ))}
            </div>

            <p className="muted small">
                This assessment was produced by a language model against retrieved rule passages. It is a
                prototype output, not a compliance determination.
            </p>
        </div>
    );
};

export default EvaluationView;
