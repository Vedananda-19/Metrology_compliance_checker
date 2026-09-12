import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useInspections } from "../hooks/useInspection";
import type { Inspection } from "../types/inspection";
import CaseCard from "../components/CaseCard";
import StatusBadge from "../components/StatusBadge";
import StatCard from "../components/StatCard";
import DonutChart from "../components/DonutChart";
import BarChart from "../components/BarChart";
import Icon from "../components/Icon";

const ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 };
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short" }) : "—";

/** Percentage change of this calendar month against the previous one. */
const monthOverMonth = (items: Inspection[], predicate: (item: Inspection) => boolean) => {
    const now = new Date();
    const key = (date: Date) => date.getFullYear() * 12 + date.getMonth();
    const thisMonth = key(now);

    let current = 0;
    let previous = 0;
    for (const item of items) {
        if (!item.created_at || !predicate(item)) continue;
        const bucket = key(new Date(item.created_at));
        if (bucket === thisMonth) current += 1;
        else if (bucket === thisMonth - 1) previous += 1;
    }

    if (!previous) return null;
    return Math.round(((current - previous) / previous) * 100);
};

function OfficerDashboard() {
    const { data: cases, isLoading } = useInspections();
    const all = useMemo(() => cases ?? [], [cases]);

    const open = useMemo(
        () => all.filter((item) => item.stage !== "RESOLVED").sort((a, b) => ORDER[a.priority] - ORDER[b.priority]),
        [all],
    );
    const resolved = useMemo(() => all.filter((item) => item.stage === "RESOLVED"), [all]);
    const actionRequired = useMemo(() => all.filter((item) => item.stage === "ACTION_REQUIRED"), [all]);
    const highPriority = useMemo(() => all.filter((item) => item.priority === "HIGH"), [all]);

    const stageSegments = useMemo(
        () => [
            { label: "Assigned", value: all.filter((i) => i.stage === "ASSIGNED").length, color: "var(--chart-1)" },
            { label: "In progress", value: all.filter((i) => i.stage === "IN_PROGRESS").length, color: "var(--chart-2)" },
            { label: "Action required", value: actionRequired.length, color: "var(--chart-4)" },
            { label: "Resolved", value: resolved.length, color: "var(--chart-3)" },
        ],
        [all, actionRequired.length, resolved.length],
    );

    const prioritySegments = useMemo(
        () => [
            { label: "High", value: highPriority.length, color: "var(--chart-4)" },
            { label: "Medium", value: all.filter((i) => i.priority === "MEDIUM").length, color: "var(--chart-2)" },
            { label: "Low", value: all.filter((i) => i.priority === "LOW").length, color: "var(--chart-3)" },
        ],
        [all, highPriority.length],
    );

    // Trailing 12 months of intake, oldest first.
    const bars = useMemo(() => {
        const now = new Date();
        const buckets = Array.from({ length: 12 }, (_, index) => {
            const date = new Date(now.getFullYear(), now.getMonth() - (11 - index), 1);
            return { key: `${date.getFullYear()}-${date.getMonth()}`, label: MONTHS[date.getMonth()], value: 0 };
        });
        const index = new Map(buckets.map((bucket) => [bucket.key, bucket]));

        for (const item of all) {
            if (!item.created_at) continue;
            const date = new Date(item.created_at);
            const bucket = index.get(`${date.getFullYear()}-${date.getMonth()}`);
            if (bucket) bucket.value += 1;
        }
        return buckets.map(({ label, value }) => ({ label, value }));
    }, [all]);

    const recent = useMemo(
        () =>
            [...all]
                .sort((a, b) => (b.created_at ?? "").localeCompare(a.created_at ?? ""))
                .slice(0, 6),
        [all],
    );

    const since = "vs last month";

    return (
        <div className="pageStack">
            <section className="panel heroPanel">
                <div>
                    <h2>Your cases</h2>
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

            {isLoading ? (
                <div className="statCardRow">
                    {[0, 1, 2, 3].map((key) => (
                        <div key={key} className="skeleton skeletonCard" />
                    ))}
                </div>
            ) : (
                <div className="statCardRow">
                    <StatCard
                        label="Total cases"
                        value={all.length}
                        icon="stack"
                        tone="brand"
                        delta={monthOverMonth(all, () => true)}
                        deltaNote={since}
                    />
                    <StatCard
                        label="Open"
                        value={open.length}
                        icon="clock"
                        tone="warn"
                        delta={monthOverMonth(all, (item) => item.stage !== "RESOLVED")}
                        deltaNote={since}
                        invertDelta
                    />
                    <StatCard
                        label="Action required"
                        value={actionRequired.length}
                        icon="flag"
                        tone="bad"
                        delta={monthOverMonth(all, (item) => item.stage === "ACTION_REQUIRED")}
                        deltaNote={since}
                        invertDelta
                    />
                    <StatCard
                        label="Resolved"
                        value={resolved.length}
                        icon="check"
                        tone="good"
                        delta={monthOverMonth(all, (item) => item.stage === "RESOLVED")}
                        deltaNote={since}
                    />
                </div>
            )}

            <div className="chartRow">
                <section className="panel">
                    <div className="sectionHead">
                        <h2>Inspection intake</h2>
                        <span className="pill">Last 12 months</span>
                    </div>
                    <BarChart bars={bars} />
                </section>

                <section className="panel">
                    <div className="sectionHead">
                        <h2>By stage</h2>
                    </div>
                    <DonutChart segments={stageSegments} centerLabel={String(all.length)} caption="cases" />
                </section>

                <section className="panel">
                    <div className="sectionHead">
                        <h2>By priority</h2>
                    </div>
                    <DonutChart
                        segments={prioritySegments}
                        centerLabel={String(highPriority.length)}
                        caption="high priority"
                    />
                </section>
            </div>

            <section className="panel">
                <div className="sectionHead">
                    <h2>Recent activity</h2>
                    <Link className="textLink" to="/history">
                        View all
                    </Link>
                </div>

                {!recent.length ? (
                    <div className="emptyState">
                        <span className="emptyIcon">
                            <Icon name="aperture" size={20} />
                        </span>
                        <strong>No inspections yet</strong>
                        <p>Capture a package label to run it against the 2011 rules.</p>
                        <Link className="primaryButton small" to="/officer/capture">
                            Start an inspection
                        </Link>
                    </div>
                ) : (
                    <div className="tableScroll">
                        <table className="dataTable">
                            <thead>
                                <tr>
                                    <th>Reference</th>
                                    <th>Package</th>
                                    <th>Assignee</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recent.map((item) => (
                                    <tr key={item.id}>
                                        <td>
                                            <Link to={`/inspection/${item.id}`} className="cellRef">
                                                {item.reference}
                                            </Link>
                                        </td>
                                        <td>{item.title || "Untitled package"}</td>
                                        <td className="muted">{item.assignee_name || "Unassigned"}</td>
                                        <td>
                                            <span className={`priorityPill priority-${item.priority.toLowerCase()}`}>
                                                {item.priority}
                                            </span>
                                        </td>
                                        <td>
                                            <StatusBadge value={item.status} size="small" />
                                        </td>
                                        <td className="muted">{formatDate(item.created_at)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            <div className="dashboardSplit">
                <section className="panel">
                    <div className="sectionHead">
                        <h2>Needs your attention</h2>
                        <span className="pill">{open.length}</span>
                    </div>

                    {isLoading && <div className="skeleton skeletonRow" />}
                    {!isLoading && !open.length && (
                        <div className="emptyState">
                            <span className="emptyIcon">
                                <Icon name="check" size={20} />
                            </span>
                            <strong>Nothing outstanding</strong>
                            <p>Every case assigned to you has been resolved.</p>
                        </div>
                    )}

                    <div className="cardColumn">
                        {open.slice(0, 6).map((item) => (
                            <CaseCard key={item.id} item={item} readOnly />
                        ))}
                    </div>
                </section>

                <section className="panel">
                    <div className="sectionHead">
                        <h2>Recently resolved</h2>
                        <span className="pill">{resolved.length}</span>
                    </div>

                    {!resolved.length && (
                        <div className="emptyState">
                            <span className="emptyIcon">
                                <Icon name="clock" size={20} />
                            </span>
                            <strong>No resolved cases yet</strong>
                            <p>Cases move here once an inspector marks them resolved.</p>
                        </div>
                    )}

                    <div className="cardColumn">
                        {resolved.slice(0, 8).map((item) => (
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
