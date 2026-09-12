import { useState } from "react";
import { useRules } from "../hooks/useInspection";

const MODE_LABEL: Record<string, string> = {
    LABEL_AUTOMATED: "From label text",
    VISION_AUTOMATED: "From image analysis",
    MEASUREMENT_REQUIRED: "Physical measurement",
    MANUAL_INSPECTION: "Manual inspection",
    MANUAL_INPUT: "Officer input",
    EXTERNAL_LOOKUP: "Registry lookup",
};

function Rules() {
    const [search, setSearch] = useState("");
    const { data, isLoading } = useRules();

    const rules = (data?.rules ?? []).filter((rule) => {
        const needle = search.trim().toLowerCase();
        if (!needle) return true;
        return `${rule.provision} ${rule.title} ${rule.text_excerpt ?? ""}`.toLowerCase().includes(needle);
    });

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h1>Rules the system checks</h1>
                    <p className="muted">
                        {data ? `${data.title}, version ${data.rule_set_version}` : "Loading the rule set"}
                    </p>
                </div>
                <input
                    className="inset ruleSearch"
                    placeholder="Search by rule number or wording"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                />
            </section>

            <section className="panel">
                {isLoading && <p className="muted">Loading…</p>}
                <p className="muted small">
                    {rules.length} of {data?.rules.length ?? 0} rules. A rule marked as needing measurement, manual
                    inspection or a registry lookup is never reported as compliant from a photograph alone.
                </p>

                <div className="ruleList">
                    {rules.map((rule) => (
                        <article key={`${rule.rule_id}-${rule.version}`} className="inset ruleRow">
                            <div className="ruleRowHead">
                                <div>
                                    <span className="pill small">Rule {rule.provision}</span>
                                    <strong>{rule.title}</strong>
                                </div>
                                <div className="ruleRowMeta">
                                    <span className="muted tiny">{rule.severity}</span>
                                    {rule.status !== "active" && <span className="badge badge-muted badgeSmall">{rule.status}</span>}
                                </div>
                            </div>
                            {rule.text_excerpt && <p className="muted small">{rule.text_excerpt}</p>}
                            <span className="muted tiny">
                                {MODE_LABEL[rule.verification_mode] ?? rule.verification_mode}
                                {rule.pdf_page && ` · page ${rule.pdf_page}`}
                                {rule.threshold_source === "ENGINEERING_POLICY" && " · uses an implementation threshold"}
                            </span>
                        </article>
                    ))}
                </div>
            </section>
        </div>
    );
}

export default Rules;
