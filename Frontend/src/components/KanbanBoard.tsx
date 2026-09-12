import { useState } from "react";
import { STAGES, type Inspection, type Stage } from "../types/inspection";
import CaseCard from "./CaseCard";

type Props = {
    cases: Inspection[];
    readOnly?: boolean;
    onMove?: (id: string, stage: Stage) => void;
    onNote?: (id: string, note: string) => void;
};

const KanbanBoard = ({ cases, readOnly, onMove, onNote }: Props) => {
    const [over, setOver] = useState<Stage | null>(null);

    const drop = (event: React.DragEvent, stage: Stage) => {
        const id = event.dataTransfer.getData("text/plain");
        const item = cases.find((entry) => entry.id === id);
        if (item && onMove && item.stage !== stage) onMove(id, stage);
        setOver(null);
    };

    return (
        <div className="kanban">
            {STAGES.map((stage) => {
                const column = cases.filter((item) => item.stage === stage.key);
                return (
                    <section
                        key={stage.key}
                        className={`panel kanbanColumn ${over === stage.key ? "kanbanOver" : ""}`}
                        onDragOver={(event) => {
                            if (readOnly) return;
                            event.preventDefault();
                            setOver(stage.key);
                        }}
                        onDragLeave={() => setOver((current) => (current === stage.key ? null : current))}
                        onDrop={(event) => !readOnly && drop(event, stage.key)}
                    >
                        <div className="kanbanHead">
                            <strong>{stage.label}</strong>
                            <span className="muted small">{column.length}</span>
                        </div>

                        <div className="kanbanCards">
                            {column.map((item) => (
                                <CaseCard
                                    key={item.id}
                                    item={item}
                                    readOnly={readOnly}
                                    draggable={!readOnly}
                                    onDragStart={(event) => event.dataTransfer.setData("text/plain", item.id)}
                                    onNote={(note) => onNote?.(item.id, note)}
                                />
                            ))}
                            {!column.length && <p className="muted tiny">Nothing here</p>}
                        </div>
                    </section>
                );
            })}
        </div>
    );
};

export default KanbanBoard;
