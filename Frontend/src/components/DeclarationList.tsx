import { FIELD_LABELS, type Declaration } from "../types/inspection";

const DeclarationList = ({ declarations }: { declarations: Declaration[] }) => {
    const found = new Set(declarations.map((item) => item.field));
    const missing = Object.keys(FIELD_LABELS).filter((field) => !found.has(field));

    return (
        <div className="stack">
            <h2>Declarations read from the package</h2>

            <div className="declarationList">
                {declarations.map((item) => (
                    <div key={item.field} className="inset declarationRow">
                        <div className="declarationHead">
                            <strong>{FIELD_LABELS[item.field] ?? item.field}</strong>
                            {item.confidence !== null && (
                                <span className="muted small">{Math.round(item.confidence * 100)}%</span>
                            )}
                        </div>
                        <span>{item.value}</span>
                    </div>
                ))}
            </div>

            {missing.length > 0 && (
                <p className="muted small">
                    Not found on any uploaded panel: {missing.map((field) => FIELD_LABELS[field]).join(", ")}
                </p>
            )}
        </div>
    );
};

export default DeclarationList;
