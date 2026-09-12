import { useState } from "react";
import CameraCapture from "./CameraCapture";
import ImageUploader from "./ImageUploader";

type Mode = "camera" | "upload";

type Props = {
    onCapture: (file: File) => void | Promise<void>;
    onUpload: (files: File[]) => void | Promise<void>;
    busy?: boolean;
    uploadLabel?: string;
};

const ImageIntake = ({ onCapture, onUpload, busy, uploadLabel = "Add images" }: Props) => {
    const [mode, setMode] = useState<Mode>("camera");

    return (
        <div className="stack">
            <div className="sourceTabs" role="tablist" aria-label="How to add package images">
                <button
                    type="button"
                    role="tab"
                    aria-selected={mode === "camera"}
                    className={`chip ${mode === "camera" ? "chipActive" : ""}`}
                    onClick={() => setMode("camera")}
                >
                    Take photos
                </button>
                <button
                    type="button"
                    role="tab"
                    aria-selected={mode === "upload"}
                    className={`chip ${mode === "upload" ? "chipActive" : ""}`}
                    onClick={() => setMode("upload")}
                >
                    Upload images
                </button>
            </div>

            {mode === "camera" ? (
                <>
                    <p className="muted">
                        Photograph every panel that carries a declaration. Blurry photos are rejected — hold the
                        package still and fill the frame.
                    </p>
                    <CameraCapture onCapture={onCapture} busy={busy} />
                </>
            ) : (
                <ImageUploader onSubmit={onUpload} busy={busy} submitLabel={uploadLabel} />
            )}
        </div>
    );
};

export default ImageIntake;
