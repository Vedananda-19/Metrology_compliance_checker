import { useState } from "react";
import { DECISION_LABELS, type Decision, type FindingReview as Review, type FindingStatus } from "../types/inspection";

const CHOICES: Record<string, { key: Decision; label: string }[]> = {
    NON_COMPLIANT: [
        { key: "CONFIRMED", label: "Confirm violation" },
        { key: "DISMISSED", label: "False reading" },
    ],
    NOT_VERIFIABLE: [
        { key: "VERIFIED_COMPLIANT", label: "Verified compliant" },
        { key: "VERIFIED_NON_COMPLIANT", label: "Verified violation" },
    ],
};

type Props = {
    status: FindingStatus;
    review: Review | undefined;
    busy?: boolean;
    onSave: (decision: Decision | null, note: string) => void;
};

const FindingReview = ({ status, review, busy, onSave }: Props) => {
    const [note, setNote] = useState(review?.note ?? "");
    const choices = CHOICES[status];

    if (!choices) return null;

    return (
        <div className="reviewRow">
            {review ? (
                <span className="reviewMark">{DECISION_LABELS[review.decision]}</span>
            ) : (
                <span className="muted tiny">Not yet checked by an officer</span>
            )}

            <div className="reviewActions">
                {choices.map((choice) => (
                    <button
                        key={choice.key}
                        className={`chip ${review?.decision === choice.key ? "chipActive" : ""}`}
                        disabled={busy}
                        onClick={() => onSave(choice.key, note)}
                    >
                        {choice.label}
                    </button>
                ))}
                {review && (
                    <button className="chip" disabled={busy} onClick={() => onSave(null, "")}>
                        Clear
                    </button>
                )}
            </div>

            <input
                className="inset reviewNote"
                value={note}
                placeholder="What did you check?"
                disabled={busy}
                onChange={(event) => setNote(event.target.value)}
                onBlur={() => review && note !== (review.note ?? "") && onSave(review.decision, note)}
            />
        </div>
    );
};

export default FindingReview;
