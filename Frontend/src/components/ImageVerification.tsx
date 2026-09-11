import { useState } from "react";
import type { InspectionImage } from "../types/inspection";
import ImageUploader from "./ImageUploader";
import StatusBadge from "./StatusBadge";

type Props = {
    images: InspectionImage[];
    imageUrls: Record<string, string>;
    editable: boolean;
    onReview: (body: { imageId: string; usability: string; panel?: string; review_note?: string }) => void;
    onDelete: (imageId: string) => void;
    onReorder: (imageIds: string[]) => void;
    onUpload: (files: File[]) => void;
    onConfirm: () => void;
    onProcess: () => void;
    busy?: boolean;
    error?: string;
};

const PANELS = ["front", "back", "side", "top", "bottom", "unspecified"];

const ImageVerification = ({
    images,
    imageUrls,
    editable,
    onReview,
    onDelete,
    onReorder,
    onUpload,
    onConfirm,
    onProcess,
    busy,
    error,
}: Props) => {
    const [adding, setAdding] = useState(false);
    const usable = images.filter((image) => image.usability === "USABLE");

    const move = (index: number, direction: -1 | 1) => {
        const target = index + direction;
        if (target < 0 || target >= images.length) return;
        const order = images.map((image) => image.id);
        [order[index], order[target]] = [order[target], order[index]];
        onReorder(order);
    };

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Verify the images</h2>
                    <p className="muted">
                        Mark each photograph usable before processing. Poor images produce poor readings, and a
                        declaration that was never photographed cannot be assessed.
                    </p>
                </div>
                <span className="pill">{usable.length} of {images.length} usable</span>
            </div>

            <div className="verifyGrid">
                {images.map((image, index) => (
                    <article key={image.id} className="panel verifyCard">
                        <div className="verifyImage inset">
                            <img src={imageUrls[image.id] ?? ""} alt={image.original_filename ?? "panel"} />
                        </div>

                        <div className="verifyMeta">
                            <StatusBadge value={image.usability} size="small" />
                            <span className="muted small">
                                {image.width_px} × {image.height_px}
                            </span>
                        </div>

                        <label className="fieldLabel small">
                            Panel
                            <select
                                className="inset"
                                value={image.panel ?? "unspecified"}
                                disabled={!editable}
                                onChange={(event) =>
                                    onReview({ imageId: image.id, usability: image.usability, panel: event.target.value })
                                }
                            >
                                {PANELS.map((panel) => (
                                    <option key={panel} value={panel}>
                                        {panel}
                                    </option>
                                ))}
                            </select>
                        </label>

                        {editable && (
                            <div className="verifyActions">
                                <button
                                    className={`ghostButton tiny ${image.usability === "USABLE" ? "active" : ""}`}
                                    onClick={() => onReview({ imageId: image.id, usability: "USABLE" })}
                                >
                                    Usable
                                </button>
                                <button
                                    className={`ghostButton tiny ${image.usability === "RETAKE" ? "active" : ""}`}
                                    onClick={() =>
                                        onReview({
                                            imageId: image.id,
                                            usability: "RETAKE",
                                            review_note: "Inspector requested a retake",
                                        })
                                    }
                                >
                                    Retake
                                </button>
                                <button className="ghostButton tiny" onClick={() => move(index, -1)} disabled={index === 0}>
                                    ↑
                                </button>
                                <button
                                    className="ghostButton tiny"
                                    onClick={() => move(index, 1)}
                                    disabled={index === images.length - 1}
                                >
                                    ↓
                                </button>
                                <button className="ghostButton tiny danger" onClick={() => onDelete(image.id)}>
                                    Remove
                                </button>
                            </div>
                        )}
                    </article>
                ))}
            </div>

            {error && <p className="errorMessage">{error}</p>}

            {editable && (
                <div className="panel">
                    {adding ? (
                        <ImageUploader onSubmit={onUpload} busy={busy} submitLabel="Add images" />
                    ) : (
                        <button className="ghostButton" onClick={() => setAdding(true)}>
                            Add more images
                        </button>
                    )}
                </div>
            )}

            <div className="actionBar">
                <button className="ghostButton" onClick={onConfirm} disabled={busy || !usable.length}>
                    Confirm images
                </button>
                <button className="primaryButton" onClick={onProcess} disabled={busy || !usable.length}>
                    {busy ? "Starting…" : "Process inspection"}
                </button>
            </div>
        </div>
    );
};

export default ImageVerification;
