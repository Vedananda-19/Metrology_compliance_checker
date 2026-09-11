import { Link, useNavigate } from "react-router-dom";
import { useInspections } from "../hooks/useInspection";
import StatusBadge from "../components/StatusBadge";

const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" }) : "";

function Dashboard() {
    const { data: inspections, isLoading } = useInspections();
    const navigate = useNavigate();

    const recent = (inspections ?? []).slice(0, 6);
    const open = (inspections ?? []).filter((item) => item.status !== "FINALIZED").length;
    const nonCompliant = (inspections ?? []).filter(
        (item) => (item.final_verdict ?? item.automated_verdict) === "NON_COMPLIANT",
    ).length;

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h1>Inspections</h1>
                    <p className="muted">
                        Upload package photographs and work through review to a finalised report.
                    </p>
                </div>
                <button className="primaryButton large" onClick={() => navigate("/scan")}>
                    New inspection
                </button>
            </section>

            <section className="statRow">
                <div className="panel stat">
                    <span className="statValue">{inspections?.length ?? 0}</span>
                    <span className="statLabel">Total inspections</span>
                </div>
                <div className="panel stat">
                    <span className="statValue">{open}</span>
                    <span className="statLabel">In progress</span>
                </div>
                <div className="panel stat">
                    <span className="statValue">{nonCompliant}</span>
                    <span className="statLabel">Non-compliant</span>
                </div>
            </section>

            <section className="panel">
                <div className="panelHeader">
                    <h2>Recent</h2>
                    <Link className="textLink" to="/history">
                        View all
                    </Link>
                </div>

                {isLoading && <p className="muted">Loading inspections…</p>}
                {!isLoading && recent.length === 0 && (
                    <p className="muted">No inspections yet. Start one to see it here.</p>
                )}

                <div className="inspectionList">
                    {recent.map((item) => (
                        <Link
                            key={item.id}
                            to={item.status === "FINALIZED" ? `/report/${item.id}` : `/inspection/${item.id}`}
                            className="inset inspectionRow"
                        >
                            <div className="inspectionRowMain">
                                <strong>{item.reference}</strong>
                                <span className="muted">{item.title || "Untitled package"}</span>
                            </div>
                            <div className="inspectionRowMeta">
                                <StatusBadge value={item.status} size="small" />
                                <StatusBadge value={item.final_verdict ?? item.automated_verdict} size="small" />
                                <span className="muted small">{formatDate(item.created_at)}</span>
                            </div>
                        </Link>
                    ))}
                </div>
            </section>
        </div>
    );
}

export default Dashboard;
