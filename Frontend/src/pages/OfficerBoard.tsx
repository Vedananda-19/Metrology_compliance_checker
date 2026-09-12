import { useInspections, useUpdateCard } from "../hooks/useInspection";
import KanbanBoard from "../components/KanbanBoard";
import type { Stage } from "../types/inspection";

function OfficerBoard() {
    const { data: cases, isLoading } = useInspections();
    const updateCard = useUpdateCard();

    return (
        <div className="pageStack wide">
            <section className="panel heroPanel">
                <div>
                    <h1>Your board</h1>
                    <p className="muted">
                        Drag a case between columns to change its stage. Notes save when you click away.
                    </p>
                </div>
            </section>

            {isLoading ? (
                <p className="muted">Loading…</p>
            ) : (
                <KanbanBoard
                    cases={cases ?? []}
                    onMove={(id, stage: Stage) => updateCard.mutate({ id, stage })}
                    onNote={(id, note) => updateCard.mutate({ id, note })}
                />
            )}
        </div>
    );
}

export default OfficerBoard;
