import type { ProcessingEvent } from "../types/inspection";

type StreamArgs = {
    inspectionId: string;
    onEvent: (event: ProcessingEvent) => void;
    signal?: AbortSignal;
};

export async function streamProcessing({ inspectionId, onEvent, signal }: StreamArgs) {
    const token = localStorage.getItem("access_token");
    const response = await fetch(
        `${import.meta.env.VITE_API_URL}/inspections/${inspectionId}/events`,
        {
            headers: { Authorization: `Bearer ${token ?? ""}` },
            signal,
        },
    );

    if (!response.ok) throw new Error("Could not connect to the processing stream");
    if (!response.body) throw new Error("Streaming is not supported in this browser");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split("\n\n");
        buffer = messages.pop() ?? "";

        for (const message of messages) {
            const dataLine = message.split("\n").find((line) => line.startsWith("data:"));
            if (!dataLine) continue;
            try {
                onEvent(JSON.parse(dataLine.replace(/^data:\s*/, "")) as ProcessingEvent);
            } catch {
                console.warn("Could not parse processing event:", dataLine);
            }
        }
    }
}
