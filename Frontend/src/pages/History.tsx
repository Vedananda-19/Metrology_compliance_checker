import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useInspections } from "../hooks/useInspection";
import useUser from "../hooks/useUser";
import StatusBadge from "../components/StatusBadge";
import Icon from "../components/Icon";
import type { InspectionStatus } from "../types/inspection";

const formatDate = (value: string | null) =>
    value
        ? new Date(value).toLocaleString(undefined, {
              day: "2-digit",
              month: "short",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
          })
        : "";

const STATUSES: { key: InspectionStatus | "ALL"; label: string }[] = [
    { key: "ALL", label: "All" },
    { key: "COMPLETED", label: "Completed" },
    { key: "DRAFT", label: "Draft" },
    { key: "FAILED", label: "Failed" },
    { key: "PROCESSING", label: "Processing" },
];

function History() {
    const { data: user } = useUser();
    const [query, setQuery] = useState("");
    const [status, setStatus] = useState<InspectionStatus | "ALL">("ALL");
    const scope = user?.role === "INSPECTOR" ? "all" : "mine";
    const { data: inspections, isLoading } = useInspections(scope, undefined, query);

    const visible = useMemo(() => {
        const rows = inspections ?? [];
        const needle = query.trim().toLowerCase();
        return rows.filter((item) => {
            if (status !== "ALL" && item.status !== status) return false;
            if (!needle) return true;
            const haystack = [
                item.reference,
                item.title,
                item.status,
                item.stage,
                item.priority,
                item.owner_name,
                item.assignee_name,
                item.note,
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();
            return haystack.includes(needle);
        });
    }, [inspections, query, status]);

    const createTo = user?.role === "INSPECTOR" ? "/inspector" : "/officer/capture";

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h1>Inspection history</h1>
                    <p className="muted">
                        Search by reference, package name, officer, stage or status, then reopen a case at any result
                        step.
                    </p>
                </div>
                <Link className="primaryButton" to={createTo}>
                    New inspection
                </Link>
            </section>

            <section className="panel">
                <div className="historyTools">
                    <label className="fieldLabel searchField">
                        Search
                        <input
                            className="inset"
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                            placeholder="INS-2026, shampoo, officer name…"
                        />
                    </label>
                    <div className="filterRow">
                        {STATUSES.map((item) => (
                            <button
                                key={item.key}
                                className={`chip ${status === item.key ? "chipActive" : ""}`}
                                onClick={() => setStatus(item.key)}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            <section className="panel">
                {isLoading && <p className="muted">Loading…</p>}
                {!isLoading && !visible.length && (
                    <div className="emptyState">
                        <span className="emptyIcon">
                            <Icon name="search" size={18} />
                        </span>
                        <strong>{query || status !== "ALL" ? "No matching inspections" : "No inspections recorded yet"}</strong>
                        <p>
                            {query
                                ? "Try a different reference, product name, or officer."
                                : "New scans appear here after you create them."}
                        </p>
                    </div>
                )}

                <div className="tableScroll">
                    {visible.length > 0 && (
                        <table className="dataTable">
                            <thead>
                                <tr>
                                    <th>Inspection ID</th>
                                    <th>Package</th>
                                    <th>Officer</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {visible.map((item) => (
                                    <tr key={item.id}>
                                        <td>
                                            <strong>{item.reference}</strong>
                                        </td>
                                        <td>{item.title || "Untitled package"}</td>
                                        <td className="muted small">{item.assignee_name || item.owner_name || "—"}</td>
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
