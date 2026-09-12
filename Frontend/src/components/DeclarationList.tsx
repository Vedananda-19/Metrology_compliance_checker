import { useState } from "react";
import { FIELD_LABELS, type Declaration } from "../types/inspection";

type Props = {
    declarations: Declaration[];
    busy?: boolean;
    onSave?: (values: Record<string, string | null>) => void;
};

const DeclarationList = ({ declarations, busy, onSave }: Props) => {
    const [edits, setEdits] = useState<Record<string, string>>({});

    const found = new Set(declarations.map((item) => item.field));
    const missing = Object.keys(FIELD_LABELS).filter((field) => !found.has(field));
    const originalOf = (field: string) => declarations.find((item) => item.field === field)?.value ?? "";
    const valueOf = (field: string) => edits[field] ?? originalOf(field);
    const changed = Object.keys(edits).filter((field) => edits[field] !== originalOf(field));

    const save = () => {
        if (!onSave || !changed.length) return;
        onSave(Object.fromEntries(changed.map((field) => [field, edits[field]])));
        setEdits({});
    };

    const row = (field: string, confidence: number | null) => (
        <div key={field} className="inset declarationRow">
            <div className="declarationHead">
                <strong>{FIELD_LABELS[field] ?? field}</strong>
                {confidence !== null && <span className="muted small">{Math.round(confidence * 100)}%</span>}
            </div>
            {onSave ? (
                <input
                    className="inset declarationInput"
                    value={valueOf(field)}
                    placeholder="Not on the label"
                    disabled={busy}
                    onChange={(event) => setEdits({ ...edits, [field]: event.target.value })}
                />
            ) : (
                <span>{valueOf(field) || "—"}</span>
            )}
        </div>
    );

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Declarations read from the package</h2>
                    {onSave && (
                        <p className="muted small">
                            Correct anything the model misread, then re-check. The rule engine judges the corrected
                            values.
                        </p>
                    )}
                </div>
                {onSave && (
                    <button className="primaryButton" disabled={busy || !changed.length} onClick={save}>
                        {busy ? "Re-checking…" : "Save and re-check"}
                    </button>
                )}
            </div>

            <div className="declarationList">
                {declarations.map((item) => row(item.field, item.confidence))}
                {onSave && missing.map((field) => row(field, null))}
            </div>

            {!onSave && missing.length > 0 && (
                <p className="muted small">
                    Not found on any uploaded panel: {missing.map((field) => FIELD_LABELS[field]).join(", ")}
                </p>
            )}
        </div>
    );
};

export default DeclarationList;
