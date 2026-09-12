import { Link } from "react-router-dom";
import { useInspections } from "../hooks/useInspection";
import CaseCard from "../components/CaseCard";
import StatusBadge from "../components/StatusBadge";

const ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 };

const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short" }) : "";

function OfficerDashboard() {
    const { data: cases, isLoading } = useInspections();

    const all = cases ?? [];
    const open = all
        .filter((item) => item.stage !== "RESOLVED")
        .sort((a, b) => ORDER[a.priority] - ORDER[b.priority]);
    const resolved = all.filter((item) => item.stage === "RESOLVED").slice(0, 8);

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h1>Your cases</h1>
                    <p className="muted">
                        Highest priority first. Priority comes from the worst confirmed violation on each case.
                    </p>
                </div>
                <div className="buttonRow">
                    <Link className="ghostButton" to="/officer/board">
                        Open board
                    </Link>
                    <Link className="primaryButton" to="/officer/capture">
                        New scan
                    </Link>
                </div>
            </section>

            <div className="dashboardSplit">
                <section className="panel">
                    <div className="panelHeader">
                        <h2>Needs your attention</h2>
                        <span className="pill">{open.length}</span>
                    </div>

                    {isLoading && <p className="muted">Loading…</p>}
                    {!isLoading && !open.length && <p className="muted">Nothing outstanding.</p>}

                    <div className="cardColumn">
                        {open.map((item) => (
                            <CaseCard key={item.id} item={item} readOnly />
                        ))}
                    </div>
                </section>

                <section className="panel">
                    <div className="panelHeader">
                        <h2>Recently resolved</h2>
                        <span className="pill">{resolved.length}</span>
                    </div>

                    {!resolved.length && <p className="muted">No resolved cases yet.</p>}

                    <div className="cardColumn">
                        {resolved.map((item) => (
                            <Link key={item.id} to={`/inspection/${item.id}`} className="inset resolvedRow">
                                <div>
                                    <strong>{item.reference}</strong>
                                    <span className="muted small"> {item.title || "Untitled package"}</span>
                                </div>
                                <div className="resolvedMeta">
                                    <StatusBadge value={item.status} size="small" />
                                    <span className="muted tiny">{formatDate(item.created_at)}</span>
                                </div>
                            </Link>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}

export default OfficerDashboard;
