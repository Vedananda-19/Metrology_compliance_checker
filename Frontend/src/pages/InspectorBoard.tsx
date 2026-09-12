import { Link, useParams } from "react-router-dom";
import { useInspections, useOfficers } from "../hooks/useInspection";
import KanbanBoard from "../components/KanbanBoard";

function InspectorBoard() {
    const { officerId } = useParams();
    const { data: cases, isLoading } = useInspections("mine", officerId);
    const { data: officers } = useOfficers();

    const officer = (officers ?? []).find((entry) => entry.id === officerId);

    return (
        <div className="pageStack wide">
            <section className="panel heroPanel">
                <div>
                    <h1>{officer ? officer.full_name || officer.username : "Officer board"}</h1>
                    <p className="muted">Read-only. Cases can only be moved by the officer they belong to.</p>
                </div>
                <Link className="ghostButton" to="/inspector">
                    Back to repository
                </Link>
            </section>

            {isLoading ? <p className="muted">Loading…</p> : <KanbanBoard cases={cases ?? []} readOnly />}
        </div>
    );
}

export default InspectorBoard;
