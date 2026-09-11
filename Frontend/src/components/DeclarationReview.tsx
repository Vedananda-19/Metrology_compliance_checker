import { useState } from "react";
import type { Declaration, ImageOcr, OcrRegion, Product } from "../types/inspection";
import HighlightViewer from "./HighlightViewer";
import StatusBadge from "./StatusBadge";

type Props = {
    declarations: Declaration[];
    panels: ImageOcr[];
    imageUrls: Record<string, string>;
    product: Product | null;
    editable: boolean;
    developmentMode: boolean;
    onSave: (edits: { fact_path: string; human_value: unknown; verification_status: string }[]) => void;
    onConfirm: () => void;
    busy?: boolean;
};

const asText = (value: unknown) => {
    if (value === null || value === undefined) return "";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
};

const DeclarationReview = ({
    declarations,
    panels,
    imageUrls,
    product,
    editable,
    developmentMode,
    onSave,
    onConfirm,
    busy,
}: Props) => {
    const [drafts, setDrafts] = useState<Record<string, string>>({});
    const [focus, setFocus] = useState<{ imageId: string | null; region: Partial<OcrRegion> | null } | null>(null);

    const focusOn = (declaration: Declaration) => {
        if (!declaration.image_id || !declaration.bbox) {
            setFocus(null);
            return;
        }
        const [x1, y1, x2, y2] = declaration.bbox;
        setFocus({ imageId: declaration.image_id, region: { x1, y1, x2, y2 } });
    };

    const currentValue = (declaration: Declaration) =>
        drafts[declaration.fact_path] ??
        asText(declaration.human_value !== null && declaration.human_value !== undefined
            ? declaration.human_value
            : declaration.ai_value);

    const dirty = Object.keys(drafts).length > 0;

    const save = (status: string) => {
        const edits = Object.entries(drafts).map(([fact_path, value]) => ({
            fact_path,
            human_value: value,
            verification_status: status,
        }));
        if (edits.length) onSave(edits);
        setDrafts({});
    };

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Declarations read from the package</h2>
                    <p className="muted">
                        Correct anything the system misread. The original machine value is kept alongside your
                        correction, and the corrected value is what the rules are applied to.
                    </p>
                </div>
                {developmentMode && <span className="badge badge-warn">Development extraction</span>}
            </div>

            {product && (
                <div className="panel productStrip">
                    <div>
                        <span className="muted small">Commodity</span>
                        <strong>{product.common_name || "Unclassified"}</strong>
                    </div>
                    <div>
                        <span className="muted small">Category</span>
                        <strong>{product.category}</strong>
                    </div>
                    <div>
                        <span className="muted small">Tags</span>
                        <strong>{(product.human_override_tags ?? product.tags).join(", ") || "none"}</strong>
                    </div>
                    <div>
                        <span className="muted small">Confidence</span>
                        <strong>
                            {product.classification_confidence !== null
                                ? `${Math.round(product.classification_confidence * 100)}%`
                                : "n/a"}
                        </strong>
                    </div>
                </div>
            )}

            <div className="splitView">
                <div className="panel splitLeft">
                    <HighlightViewer panels={panels} imageUrls={imageUrls} focus={focus} height={520} />
                </div>

                <div className="panel splitRight">
                    <div className="declarationList">
                        {declarations.map((declaration) => {
                            const changed = drafts[declaration.fact_path] !== undefined;
                            return (
                                <div
                                    key={declaration.fact_path}
                                    className={`inset declarationRow ${changed ? "declarationChanged" : ""}`}
                                    onClick={() => focusOn(declaration)}
                                >
                                    <div className="declarationHead">
                                        <strong>{declaration.label}</strong>
                                        <div className="declarationBadges">
                                            {declaration.ai_confidence !== null && (
                                                <span className="muted small">
                                                    {Math.round(declaration.ai_confidence * 100)}%
                                                </span>
                                            )}
                                            <StatusBadge value={declaration.verification_status} size="small" />
                                        </div>
                                    </div>

                                    <input
                                        className="inset declarationInput"
                                        value={currentValue(declaration)}
                                        disabled={!editable}
                                        onChange={(event) =>
                                            setDrafts((previous) => ({
                                                ...previous,
                                                [declaration.fact_path]: event.target.value,
                                            }))
                                        }
                                    />

                                    {declaration.human_value !== null && declaration.human_value !== undefined && (
                                        <p className="muted small">
                                            Machine read: {asText(declaration.ai_value) || "nothing"}
                                        </p>
                                    )}
                                    {declaration.bbox && <span className="muted tiny">Click to locate on the image</span>}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {editable && (
                <div className="actionBar">
                    <button className="ghostButton" onClick={() => save("VERIFIED")} disabled={!dirty || busy}>
                        Save corrections
                    </button>
                    <button className="ghostButton" onClick={() => setDrafts({})} disabled={!dirty}>
                        Discard changes
                    </button>
                    <button className="primaryButton" onClick={onConfirm} disabled={busy || dirty}>
                        {dirty ? "Save your corrections first" : "Confirm and re-evaluate"}
                    </button>
                </div>
            )}
        </div>
    );
};

export default DeclarationReview;
