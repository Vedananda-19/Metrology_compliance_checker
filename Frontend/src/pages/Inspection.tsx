import { useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import {
    useDeleteImage,
    useInspection,
    useProcess,
    useReviewFinding,
    useReviseDeclarations,
    useUploadImages,
} from "../hooks/useInspection";
import useImageUrls from "../hooks/useImageUrls";
import { errorMessage } from "../apis/api";
import ImageIntake from "../components/ImageIntake";
import OcrTextView from "../components/OcrTextView";
import DeclarationList from "../components/DeclarationList";
import EvaluationView from "../components/EvaluationView";
import StatusBadge from "../components/StatusBadge";
import ResultNav, { RESULT_STEPS, type ResultView } from "../components/ResultNav";
import type { InspectionDetail } from "../types/inspection";

const isView = (value: string | null): value is ResultView =>
    RESULT_STEPS.some((step) => step.key === value);

const availableViews = (inspection: InspectionDetail): ResultView[] => {
    const views: ResultView[] = ["images"];
    if (inspection.ocr_texts.length) views.push("ocr");
    if (inspection.declarations.length) views.push("declarations");
    if (inspection.evaluation) views.push("findings");
    return views;
};

const defaultView = (inspection: InspectionDetail): ResultView => {
    const open = availableViews(inspection);
    if (open.includes("findings")) return "findings";
    if (open.includes("declarations")) return "declarations";
    if (open.includes("ocr")) return "ocr";
    return "images";
};

function Inspection() {
    const { id } = useParams();
    const [params, setParams] = useSearchParams();
    const [error, setError] = useState("");

    const { data: inspection, isLoading } = useInspection(id);
    const imageUrls = useImageUrls(id, inspection?.images);
    const uploadImages = useUploadImages(id);
    const deleteImage = useDeleteImage(id);
    const process = useProcess(id);
    const reviewFinding = useReviewFinding(id);
    const reviseDeclarations = useReviseDeclarations(id);

    if (isLoading) return <div className="routeState"><h5>Loading inspection…</h5></div>;
    if (!inspection) return <div className="routeState"><h5>Inspection not found</h5></div>;

    const open = availableViews(inspection);
    const requested = params.get("view");
    const view: ResultView = isView(requested) && open.includes(requested) ? requested : defaultView(inspection);

    const setView = (next: ResultView) => {
        const copy = new URLSearchParams(params);
        copy.set("view", next);
        setParams(copy, { replace: true });
    };

    const run = async (action: () => Promise<unknown>, fallback: string) => {
        try {
            setError("");
            await action();
        } catch (caught) {
            setError(errorMessage(caught, fallback));
        }
    };

    const addImages = async (files: File[], fallback: string) => {
        try {
            setError("");
            await uploadImages.mutateAsync(files);
        } catch (caught) {
            setError(errorMessage(caught, fallback));
            throw caught;
        }
    };

    const rerun = () =>
        run(async () => {
            await process.mutateAsync();
            setView("findings");
        }, "Processing failed");

    const findings = inspection.evaluation?.result.findings ?? [];
    const pending =
        findings.filter(
            (item) =>
                (item.status === "NON_COMPLIANT" || item.status === "NOT_VERIFIABLE") &&
                !inspection.reviews.some((review) => review.rule_id === item.rule_id),
        ).length;

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
                    onClick={rerun}
                    disabled={process.isPending || !inspection.images.length}
                >
                    {process.isPending ? "Processing…" : inspection.evaluation ? "Rerun from images" : "Process inspection"}
                </button>
            </section>

            {(error || inspection.error) && <p className="errorMessage">{error || inspection.error}</p>}

            {open.length > 1 && (
                <ResultNav
                    current={view}
                    available={open}
                    counts={{
                        images: `${inspection.images.length} panel${inspection.images.length === 1 ? "" : "s"}`,
                        ocr: inspection.ocr_texts.length ? `${inspection.ocr_texts.length} reads` : "",
                        declarations: inspection.declarations.length ? `${inspection.declarations.length} fields` : "",
                        findings: inspection.evaluation
                            ? pending
                                ? `${pending} to review`
                                : "Reviewed"
                            : "",
                    }}
                    onSelect={setView}
                />
            )}

            {process.isPending && (
                <section className="panel">
                    <p className="muted">
                        Reading the panels with OCR, extracting declarations, then running the rule engine. You can
                        move between OCR, declarations and violations once this finishes.
                    </p>
                </section>
            )}

            {view === "images" && (
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
                    <ImageIntake
                        busy={uploadImages.isPending}
                        uploadLabel="Add images"
                        onCapture={(file) => addImages([file], "Could not keep this photo")}
                        onUpload={(files) => addImages(files, "Could not upload")}
                    />
                </section>
            )}

            {view === "ocr" && (
                <section className="panel">
                    <OcrTextView ocrTexts={inspection.ocr_texts} images={inspection.images} />
                    <div className="actionBar">
                        <button className="ghostButton" onClick={() => setView("images")}>
                            Back to images
                        </button>
                        <button className="primaryButton" onClick={rerun} disabled={process.isPending}>
                            Rerun OCR and extraction
                        </button>
                    </div>
                </section>
            )}

            {view === "declarations" && (
                <section className="panel">
                    <DeclarationList
                        declarations={inspection.declarations}
                        busy={reviseDeclarations.isPending}
                        onSave={(values) =>
                            run(async () => {
                                await reviseDeclarations.mutateAsync(values);
                                setView("findings");
                            }, "Could not save the corrections")
                        }
                    />
                    <div className="actionBar">
                        <button className="ghostButton" onClick={() => setView("ocr")}>
                            Check OCR text
                        </button>
                        <button className="ghostButton" onClick={() => setView("findings")} disabled={!inspection.evaluation}>
                            Skip to violations
                        </button>
                    </div>
                </section>
            )}

            {view === "findings" && inspection.evaluation && (
                <section className="panel">
                    <EvaluationView
                        evaluation={inspection.evaluation}
                        reviews={inspection.reviews}
                        busy={reviewFinding.isPending}
                        onReview={(ruleId, decision, note) =>
                            run(() => reviewFinding.mutateAsync({ ruleId, decision, note }), "Could not save the review")
                        }
                    />
                    <div className="actionBar">
                        <button className="ghostButton" onClick={() => setView("declarations")}>
                            Correct declarations and re-check
                        </button>
                        <button className="primaryButton" onClick={rerun} disabled={process.isPending}>
                            Rerun from images
                        </button>
                    </div>
                </section>
            )}
        </div>
    );
}

export default Inspection;
