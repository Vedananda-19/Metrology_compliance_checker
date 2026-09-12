import { useState } from "react";
import { Link } from "react-router-dom";
import { useAssign, useInspections, useOfficers } from "../hooks/useInspection";
import StatusBadge from "../components/StatusBadge";
import { errorMessage } from "../apis/api";

const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" }) : "";

function InspectorRepository() {
    const [error, setError] = useState("");
    const { data: cases, isLoading } = useInspections("all");
    const { data: officers } = useOfficers();
    const assign = useAssign();

    const handleAssign = async (id: string, officerId: string) => {
        try {
            setError("");
            await assign.mutateAsync({ id, officer_id: officerId || null });
        } catch (caught) {
            setError(errorMessage(caught, "Could not assign the case"));
        }
    };

    const unassigned = (cases ?? []).filter((item) => !item.assigned_to).length;

    return (
        <div className="pageStack wide">
            <section className="panel heroPanel">
                <div>
                    <h1>Case repository</h1>
                    <p className="muted">
                        Everything scanned by every officer. Assign a case and it lands on that officer's board in the
                        first stage.
                    </p>
                </div>
                <div className="buttonRow">
                    <span className="pill">{unassigned} unassigned</span>
                    <Link className="ghostButton" to="/rules">
                        Rule list
                    </Link>
                </div>
            </section>

            {error && <p className="errorMessage">{error}</p>}

            <section className="panel">
                {isLoading && <p className="muted">Loading…</p>}
                {!isLoading && !cases?.length && <p className="muted">No cases have been scanned yet.</p>}

                <div className="tableScroll">
                    {cases && cases.length > 0 && (
                        <table className="dataTable">
                            <thead>
                                <tr>
                                    <th>Case</th>
                                    <th>Package</th>
                                    <th>Scanned by</th>
                                    <th>Date</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Stage</th>
                                    <th>Assign to</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cases.map((item) => (
                                    <tr key={item.id}>
                                        <td>
                                            <Link className="caseRef" to={`/inspection/${item.id}`}>
                                                {item.reference}
                                            </Link>
                                        </td>
                                        <td>{item.title || "Untitled package"}</td>
                                        <td className="muted small">{item.owner_name}</td>
                                        <td className="muted small">{formatDate(item.created_at)}</td>
                                        <td>
                                            <span className={`priorityPill priority-${item.priority.toLowerCase()}`}>
                                                {item.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <StatusBadge value={item.status} size="small" />
                                        </td>
                                        <td className="muted small">{item.stage.replace(/_/g, " ").toLowerCase()}</td>
                                        <td>
                                            <select
                                                className="inset assignSelect"
                                                value={item.assigned_to ?? ""}
                                                onChange={(event) => handleAssign(item.id, event.target.value)}
                                            >
                                                <option value="">Unassigned</option>
                                                {(officers ?? []).map((officer) => (
                                                    <option key={officer.id} value={officer.id}>
                                                        {officer.full_name || officer.username}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </section>

            <section className="panel">
                <div className="panelHeader">
                    <h2>Officer boards</h2>
                    <p className="muted">Open a board to see what each officer is working on. Read-only.</p>
                </div>
                <div className="buttonRow">
                    {(officers ?? []).map((officer) => (
                        <Link key={officer.id} className="ghostButton" to={`/inspector/board/${officer.id}`}>
                            {officer.full_name || officer.username}
                        </Link>
                    ))}
                    {!officers?.length && <p className="muted">No officers are registered yet.</p>}
                </div>
            </section>
        </div>
    );
}

export default InspectorRepository;
