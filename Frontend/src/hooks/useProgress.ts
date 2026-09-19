import { useEffect, useRef, useState } from "react";

export type ProgressEvent = {
    stage: string;
    status: "running" | "success" | "error";
    detail?: string | null;
};

// Ordered stages, mirrored from backend/pipeline/progress.py so the UI can
// render a checklist even before the first event arrives.
export const PROGRESS_STAGES = [
    { key: "ocr", label: "Reading the label with OCR" },
    { key: "extraction", label: "Extracting declarations" },
    { key: "measurement", label: "Measuring font sizes" },
    { key: "compliance", label: "Running the rule engine" },
] as const;

const wsUrl = (id: string, token: string) => {
    const base = import.meta.env.VITE_API_URL as string;
    const httpUrl = new URL(`/inspections/${id}/progress`, base);
    httpUrl.protocol = httpUrl.protocol === "https:" ? "wss:" : "ws:";
    httpUrl.searchParams.set("token", token);
    return httpUrl.toString();
};

/**
 * Streams pipeline progress over a WebSocket while `active` is true.
 * `current` is the stage key currently running; `done` fires on the terminal
 * event so the caller can toast success/failure.
 */
export function useProgress(
    id: string | undefined,
    active: boolean,
    onDone?: (event: ProgressEvent) => void,
) {
    const [current, setCurrent] = useState<string | null>(null);
    const onDoneRef = useRef(onDone);
    onDoneRef.current = onDone;

    useEffect(() => {
        if (!id || !active) {
            setCurrent(null);
            return;
        }
        const token = localStorage.getItem("access_token");
        if (!token) return;

        let socket: WebSocket;
        try {
            socket = new WebSocket(wsUrl(id, token));
        } catch {
            return;
        }

        socket.onmessage = (message) => {
            const event: ProgressEvent = JSON.parse(message.data);
            if (event.stage === "done") {
                setCurrent(null);
                onDoneRef.current?.(event);
            } else {
                setCurrent(event.stage);
            }
        };

        return () => {
            socket.onmessage = null;
            socket.close();
        };
    }, [id, active]);

    return { current };
}
