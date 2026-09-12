import { useState } from "react";
import { useParams } from "react-router-dom";
import { useDeleteImage, useInspection, useProcess, useUploadImages } from "../hooks/useInspection";
import useImageUrls from "../hooks/useImageUrls";
import { errorMessage } from "../apis/api";
import ImageUploader from "../components/ImageUploader";
import OcrTextView from "../components/OcrTextView";
import DeclarationList from "../components/DeclarationList";
import EvaluationView from "../components/EvaluationView";
import StatusBadge from "../components/StatusBadge";

function Inspection() {
    const { id } = useParams();
    const [error, setError] = useState("");

    const { data: inspection, isLoading } = useInspection(id);
    const imageUrls = useImageUrls(id, inspection?.images);
    const uploadImages = useUploadImages(id);
    const deleteImage = useDeleteImage(id);
    const process = useProcess(id);

    if (isLoading) return <div className="routeState"><h5>Loading inspection…</h5></div>;
    if (!inspection) return <div className="routeState"><h5>Inspection not found</h5></div>;

    const run = async (action: () => Promise<unknown>, fallback: string) => {
        try {
            setError("");
            await action();
        } catch (caught) {
            setError(errorMessage(caught, fallback));
        }
    };

    return (
        <div className="pageStack">
            <section className="panel inspectionHeader">
                <div>
                    <div className="inspectionTitleRow">
                        <h1>{inspection.reference}</h1>
                        <StatusBadge value={inspection.status} />
                        {inspection.evaluation && <StatusBadge value={inspection.evaluation.verdict} />}
                    </div>
                    <p className="muted">{inspection.title || "Untitled package"}</p>
                </div>
                <button
                    className="primaryButton"
                    onClick={() => run(() => process.mutateAsync(), "Processing failed")}
                    disabled={process.isPending || !inspection.images.length}
                >
                    {process.isPending ? "Processing…" : inspection.evaluation ? "Run again" : "Process inspection"}
                </button>
            </section>

            {(error || inspection.error) && <p className="errorMessage">{error || inspection.error}</p>}

            <section className="panel">
                <h2>Package images</h2>
                {inspection.images.length > 0 && (
                    <div className="thumbGrid">
                        {inspection.images.map((image) => (
                            <figure key={image.id} className="panel thumb">
                                {imageUrls[image.id] ? (
                                    <img src={imageUrls[image.id]} alt={image.original_filename ?? "panel"} />
                                ) : (
                                    <div className="imagePlaceholder">Loading…</div>
                                )}
                                <figcaption>
                                    <span className="thumbName">{image.original_filename}</span>
                                </figcaption>
                                <button
                                    className="ghostButton tiny danger"
                                    onClick={() => run(() => deleteImage.mutateAsync(image.id), "Could not remove")}
                                >
                                    Remove
                                </button>
                            </figure>
                        ))}
                    </div>
                )}
                <ImageUploader
                    onSubmit={(files) => run(() => uploadImages.mutateAsync(files), "Could not upload")}
                    busy={uploadImages.isPending}
                    submitLabel="Add images"
                />
            </section>

            {process.isPending && (
                <section className="panel">
                    <p className="muted">
                        Reading the panels with OCR, extracting declarations, retrieving rule passages and asking the
                        model to evaluate them. This takes a moment.
                    </p>
                </section>
            )}

            {inspection.ocr_texts.length > 0 && (
                <section className="panel">
                    <OcrTextView ocrTexts={inspection.ocr_texts} images={inspection.images} />
                </section>
            )}

            {inspection.declarations.length > 0 && (
                <section className="panel">
                    <DeclarationList declarations={inspection.declarations} />
                </section>
            )}

            {inspection.evaluation && (
                <section className="panel">
                    <EvaluationView evaluation={inspection.evaluation} />
                </section>
            )}
        </div>
    );
}

export default Inspection;
