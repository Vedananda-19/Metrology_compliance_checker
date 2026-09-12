import { Link } from "react-router-dom";
import { useInspections } from "../hooks/useInspection";
import StatusBadge from "../components/StatusBadge";

const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleString(undefined, { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "";

function History() {
    const { data: inspections, isLoading } = useInspections();

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h1>Inspection history</h1>
                    <p className="muted">Reopen an unfinished inspection at the stage it was left, or view a finalised report.</p>
                </div>
                <Link className="primaryButton" to="/scan">
                    New inspection
                </Link>
            </section>

            <section className="panel">
                {isLoading && <p className="muted">Loading…</p>}
                {!isLoading && !inspections?.length && <p className="muted">No inspections recorded yet.</p>}

                <div className="tableScroll">
                    {inspections && inspections.length > 0 && (
                        <table className="dataTable">
                            <thead>
                                <tr>
                                    <th>Inspection ID</th>
                                    <th>Package</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {inspections.map((item) => (
                                    <tr key={item.id}>
                                        <td>
                                            <strong>{item.reference}</strong>
                                        </td>
                                        <td>{item.title || "Untitled package"}</td>
                                        <td className="muted small">{formatDate(item.created_at)}</td>
                                        <td>
                                            <StatusBadge value={item.status} size="small" />
                                        </td>
                                        <td>
                                            <Link className="ghostButton small" to={`/inspection/${item.id}`}>
                                                Open
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </section>
        </div>
    );
}

export default History;
