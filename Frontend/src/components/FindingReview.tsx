import { useState } from "react";
import { DECISION_LABELS, type Decision, type FindingReview as Review, type FindingStatus } from "../types/inspection";

const CHOICES: Record<
    string,
    { key: Decision; label: string; detail: string; tone: "bad" | "good" | "muted" }[]
> = {
    NON_COMPLIANT: [
        {
            key: "CONFIRMED",
            label: "Confirm violation",
            detail: "This requirement is not met on the package.",
            tone: "bad",
        },
        {
            key: "DISMISSED",
            label: "False reading",
            detail: "The text or extraction was wrong. Dismiss this finding.",
            tone: "muted",
        },
    ],
    NOT_VERIFIABLE: [
        {
            key: "VERIFIED_COMPLIANT",
            label: "Verified compliant",
            detail: "You checked off-image evidence. This requirement is met.",
            tone: "good",
        },
        {
            key: "VERIFIED_NON_COMPLIANT",
            label: "Verified violation",
            detail: "You checked off-image evidence. This is a real failure.",
            tone: "bad",
        },
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
        <div className={`reviewPanel ${review ? `reviewPanel-${review.decision}` : "reviewPanel-pending"}`}>
            <div className="reviewPanelHead">
                <span className="reviewEyebrow">Officer decision</span>
                {review ? (
                    <span className={`reviewStamp reviewStamp-${review.decision}`}>{DECISION_LABELS[review.decision]}</span>
                ) : (
                    <span className="reviewStamp reviewStamp-pending">Awaiting review</span>
                )}
            </div>

            <div className="reviewChoices">
                {choices.map((choice) => (
                    <button
                        key={choice.key}
                        type="button"
                        className={`reviewChoice reviewChoice-${choice.tone} ${review?.decision === choice.key ? "isOn" : ""}`}
                        disabled={busy}
                        onClick={() => onSave(choice.key, note)}
                    >
                        <strong>{choice.label}</strong>
                        <span>{choice.detail}</span>
                    </button>
                ))}
            </div>

            <label className="fieldLabel">
                Note
                <textarea
                    className="inset reviewNote"
                    value={note}
                    rows={2}
                    placeholder="What did you check on the package or in the OCR text?"
                    disabled={busy}
                    onChange={(event) => setNote(event.target.value)}
                    onBlur={() => review && note !== (review.note ?? "") && onSave(review.decision, note)}
                />
            </label>

            {review && (
                <button className="ghostButton small" disabled={busy} onClick={() => onSave(null, "")}>
                    Clear decision
                </button>
            )}
        </div>
    );
};

export default FindingReview;
