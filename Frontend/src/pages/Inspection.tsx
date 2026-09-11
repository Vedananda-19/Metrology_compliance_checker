import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
    useConfirmDeclarations,
    useDecideFinding,
    useDecideRules,
    useDeclarations,
    useDeleteImage,
    useEditDeclarations,
    useFinalize,
    useFindings,
    useInspection,
    useOcr,
    useReorderImages,
    useReviewImage,
    useRules,
    useStartProcessing,
    useUploadImages,
    useVerifyImages,
} from "../hooks/useInspection";
import useImageUrls from "../hooks/useImageUrls";
import { streamProcessing } from "../apis/events";
import { errorMessage } from "../apis/api";
import { queryClient } from "../main";
import Stepper from "../components/Stepper";
import StatusBadge from "../components/StatusBadge";
import ImageVerification from "../components/ImageVerification";
import ProcessingStatus from "../components/ProcessingStatus";
import DeclarationReview from "../components/DeclarationReview";
import RuleReview from "../components/RuleReview";
import ViolationReview from "../components/ViolationReview";
import FinalReview from "../components/FinalReview";
import type { ProcessingEvent } from "../types/inspection";

const REVIEW_STAGES = ["EXTRACTION_REVIEW", "CLASSIFICATION_REVIEW", "RULE_REVIEW", "COMPLIANCE_REVIEW", "VIOLATION_REVIEW", "FINAL_REVIEW"];

function Inspection() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [error, setError] = useState("");
    const [events, setEvents] = useState<ProcessingEvent[]>([]);
    const [stageOverride, setStageOverride] = useState<string | null>(null);
    const streaming = useRef(false);

    const { data: inspection, isLoading } = useInspection(id);
    const status = inspection?.status;
    const dataReady = Boolean(status && (REVIEW_STAGES.includes(status) || status === "FINALIZED"));

    const { data: panels } = useOcr(id, dataReady);
    const { data: declarations } = useDeclarations(id, dataReady);
    const { data: rules } = useRules(id, dataReady);
    const { data: findings } = useFindings(id, dataReady);
    const imageUrls = useImageUrls(id, inspection?.images);

    const uploadImages = useUploadImages(id);
    const deleteImage = useDeleteImage(id);
    const reorderImages = useReorderImages(id);
    const reviewImage = useReviewImage(id);
    const verifyImages = useVerifyImages(id);
    const startProcessing = useStartProcessing(id);
    const editDeclarations = useEditDeclarations(id);
    const confirmDeclarations = useConfirmDeclarations(id);
    const decideRules = useDecideRules(id);
    const decideFinding = useDecideFinding(id);
    const finalize = useFinalize(id);

    useEffect(() => {
        if (inspection?.processing_log?.length && !events.length) {
            setEvents(inspection.processing_log);
        }
    }, [inspection?.processing_log, events.length]);

    useEffect(() => {
        if (!id || status !== "PROCESSING" || streaming.current) return;
        streaming.current = true;
        const controller = new AbortController();

        streamProcessing({
            inspectionId: id,
            signal: controller.signal,
            onEvent: (event) => {
                setEvents((previous) => [...previous, event]);
                if (event.done) {
                    queryClient.invalidateQueries({ queryKey: ["inspection", id] });
                }
            },
        })
            .catch((caught) => setError(errorMessage(caught, "Lost the processing connection")))
            .finally(() => {
                streaming.current = false;
                queryClient.invalidateQueries({ queryKey: ["inspection", id] });
            });

        return () => controller.abort();
    }, [id, status]);

    if (isLoading) return <div className="routeState"><h5>Loading inspection…</h5></div>;
    if (!inspection) return <div className="routeState"><h5>Inspection not found</h5></div>;

    const editable = inspection.status !== "FINALIZED";
    const stage = stageOverride ?? inspection.status;

    const run = async (action: () => Promise<unknown>, fallback: string) => {
        try {
            setError("");
            await action();
        } catch (caught) {
            setError(errorMessage(caught, fallback));
        }
    };

    const renderStage = () => {
        if (["DRAFT", "IMAGES_UPLOADED", "IMAGE_REVIEW"].includes(stage)) {
            return (
                <ImageVerification
                    images={inspection.images}
                    imageUrls={imageUrls}
                    editable={editable}
                    busy={uploadImages.isPending || startProcessing.isPending}
                    error={error}
                    onUpload={(files) => run(() => uploadImages.mutateAsync(files), "Could not upload")}
                    onDelete={(imageId) => run(() => deleteImage.mutateAsync(imageId), "Could not remove the image")}
                    onReorder={(ids) => run(() => reorderImages.mutateAsync(ids), "Could not reorder")}
                    onReview={(body) => run(() => reviewImage.mutateAsync(body), "Could not update the image")}
                    onConfirm={() => run(() => verifyImages.mutateAsync(), "Could not confirm the images")}
                    onProcess={() =>
                        run(async () => {
                            setEvents([]);
                            await verifyImages.mutateAsync();
                            await startProcessing.mutateAsync();
                        }, "Could not start processing")
                    }
                />
            );
        }

        if (stage === "PROCESSING") {
            return <ProcessingStatus events={events} error={error || inspection.processing_error || undefined} />;
        }

        if (stage === "EXTRACTION_REVIEW" || stage === "CLASSIFICATION_REVIEW") {
            return (
                <DeclarationReview
                    declarations={declarations ?? []}
                    panels={panels ?? []}
                    imageUrls={imageUrls}
                    product={inspection.product}
                    editable={editable}
                    developmentMode={inspection.development_mode}
                    busy={editDeclarations.isPending || confirmDeclarations.isPending}
                    onSave={(edits) => run(() => editDeclarations.mutateAsync(edits), "Could not save the corrections")}
                    onConfirm={() => run(() => confirmDeclarations.mutateAsync(), "Could not confirm")}
                />
            );
        }

        if (stage === "RULE_REVIEW" || stage === "COMPLIANCE_REVIEW") {
            return (
                <RuleReview
                    rules={rules ?? []}
                    editable={editable}
                    busy={decideRules.isPending}
                    onDecide={(decisions) => run(() => decideRules.mutateAsync(decisions), "Could not record the decision")}
                    onContinue={() => setStageOverride("VIOLATION_REVIEW")}
                />
            );
        }

        if (stage === "VIOLATION_REVIEW") {
            return (
                <ViolationReview
                    findings={findings ?? []}
                    summary={inspection.summary}
                    panels={panels ?? []}
                    imageUrls={imageUrls}
                    editable={editable}
                    busy={decideFinding.isPending}
                    onDecide={(body) => run(() => decideFinding.mutateAsync(body), "Could not record the decision")}
                    onContinue={() => setStageOverride("FINAL_REVIEW")}
                />
            );
        }

        return (
            <FinalReview
                inspection={inspection}
                declarations={declarations ?? []}
                rules={rules ?? []}
                findings={findings ?? []}
                editable={editable}
                busy={finalize.isPending}
                error={error}
                onBack={() => setStageOverride("VIOLATION_REVIEW")}
                onFinalize={(observations) =>
                    run(async () => {
                        await finalize.mutateAsync({ inspector_observations: observations });
                        navigate(`/report/${inspection.id}`);
                    }, "Could not finalize the inspection")
                }
            />
        );
    };

    return (
        <div className="pageStack">
            <section className="panel inspectionHeader">
                <div>
                    <div className="inspectionTitleRow">
                        <h1>{inspection.reference}</h1>
                        <StatusBadge value={inspection.status} />
                        <StatusBadge value={inspection.final_verdict ?? inspection.automated_verdict} />
                    </div>
                    <p className="muted">
                        {inspection.title || "Untitled package"}
                        {inspection.location ? ` · ${inspection.location}` : ""}
                        {inspection.rule_set_version ? ` · rule set ${inspection.rule_set_version}` : ""}
                    </p>
                </div>
                {inspection.status === "FINALIZED" && (
                    <button className="primaryButton" onClick={() => navigate(`/report/${inspection.id}`)}>
                        View report
                    </button>
                )}
            </section>

            {inspection.degraded_mode && (
                <div className="panel banner bannerDanger">
                    <strong>Deterministic evaluation did not run.</strong> The rule engine failed for this inspection.
                    Every finding is provisional and needs manual verification.
                </div>
            )}
            {inspection.development_mode && (
                <div className="panel banner bannerWarn">
                    <strong>Development extraction mode.</strong> No language model is configured, so declarations came
                    from the built-in pattern matcher. OCR, the rule engine and all findings are genuine.
                </div>
            )}

            <Stepper status={inspection.status} />

            {stageOverride && stageOverride !== inspection.status && (
                <button className="textLink" onClick={() => setStageOverride(null)}>
                    Back to the current stage ({inspection.status})
                </button>
            )}

            <section className="panel stagePanel">{renderStage()}</section>

            {error && !["DRAFT", "IMAGES_UPLOADED", "IMAGE_REVIEW", "PROCESSING"].includes(stage) && (
                <p className="errorMessage">{error}</p>
            )}
        </div>
    );
}

export default Inspection;
