import { PROCESSING_STEPS, STEP_LABELS, type ProcessingEvent } from "../types/inspection";

type Props = {
    events: ProcessingEvent[];
    error?: string;
};

const ProcessingStatus = ({ events, error }: Props) => {
    const latest = new Map<string, ProcessingEvent>();
    for (const event of events) latest.set(event.step, event);

    const reached = PROCESSING_STEPS.findIndex((step) => !latest.has(step));
    const activeIndex = reached === -1 ? PROCESSING_STEPS.length : reached;

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Processing</h2>
                    <p className="muted">
                        Images are prepared, read with PaddleOCR, converted into declarations and judged against the
                        rules in force. This page updates as each step finishes.
                    </p>
                </div>
            </div>

            <ol className="processList">
                {PROCESSING_STEPS.map((step, index) => {
                    const event = latest.get(step);
                    const state =
                        event?.status === "failed"
                            ? "failed"
                            : event?.status === "completed"
                              ? "done"
                              : index === activeIndex || event?.status === "processing"
                                ? "active"
                                : "todo";
                    return (
                        <li key={step} className={`panel processItem process-${state}`}>
                            <span className="processIcon" />
                            <div className="processBody">
                                <strong>{STEP_LABELS[step]}</strong>
                                <span className="muted small">{event?.message ?? "Waiting"}</span>
                            </div>
                            {event?.at && (
                                <span className="muted small">
                                    {new Date(event.at).toLocaleTimeString(undefined, {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                        second: "2-digit",
                                    })}
                                </span>
                            )}
                        </li>
                    );
                })}
            </ol>

            {error && <p className="errorMessage">{error}</p>}
        </div>
    );
};

export default ProcessingStatus;
