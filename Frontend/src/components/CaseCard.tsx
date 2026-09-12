import { useState } from "react";
import { Link } from "react-router-dom";
import type { Inspection } from "../types/inspection";
import StatusBadge from "./StatusBadge";

type Props = {
    item: Inspection;
    readOnly?: boolean;
    draggable?: boolean;
    onNote?: (note: string) => void;
    onDragStart?: (event: React.DragEvent) => void;
};

const CaseCard = ({ item, readOnly, draggable, onNote, onDragStart }: Props) => {
    const [note, setNote] = useState(item.note ?? "");

    const save = () => {
        const trimmed = note.trim();
        if (onNote && trimmed !== (item.note ?? "")) onNote(trimmed);
    };

    return (
        <article
            className="inset caseCard"
            draggable={Boolean(draggable)}
            onDragStart={onDragStart}
        >
            <div className="caseCardHead">
                <Link to={`/inspection/${item.id}`} className="caseRef">
                    {item.reference}
                </Link>
                <span className={`priorityPill priority-${item.priority.toLowerCase()}`}>{item.priority}</span>
            </div>

            <span className="caseTitle">{item.title || "Untitled package"}</span>

            <div className="caseMeta">
                <StatusBadge value={item.status} size="small" />
                {item.assignee_name && <span className="muted tiny">{item.assignee_name}</span>}
            </div>

            {readOnly ? (
                item.note && <p className="muted tiny caseNote">{item.note}</p>
            ) : (
                <input
                    className="inset caseNoteInput"
                    value={note}
                    placeholder="Add a note"
                    onChange={(event) => setNote(event.target.value)}
                    onBlur={save}
                    onKeyDown={(event) => event.key === "Enter" && event.currentTarget.blur()}
                />
            )}
        </article>
    );
};

export default CaseCard;
