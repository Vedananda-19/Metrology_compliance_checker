import { useEffect, useRef, useState } from "react";

type Props = {
    onCapture: (file: File) => void;
    busy?: boolean;
};

const CameraCapture = ({ onCapture, busy }: Props) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [error, setError] = useState("");
    const [live, setLive] = useState(false);

    const stop = () => {
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        setLive(false);
    };

    const start = async () => {
        setError("");
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment", width: { ideal: 1600 } },
            });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }
            setLive(true);
        } catch {
            setError("Could not open the camera. Check the browser permission, and note that capture needs localhost or HTTPS.");
        }
    };

    useEffect(() => stop, []);

    const shoot = () => {
        const video = videoRef.current;
        if (!video) return;

        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d")?.drawImage(video, 0, 0);
        canvas.toBlob(async (blob) => {
            if (!blob) return;
            try {
                await onCapture(new File([blob], `capture-${Date.now()}.png`, { type: "image/png" }));
            } catch {
                /* Parent shows why the photo was rejected. */
            }
        }, "image/png");
    };

    return (
        <div className="stack">
            <div className="inset cameraStage">
                <video ref={videoRef} playsInline muted className={live ? "" : "hidden"} />
                {!live && <p className="muted">The camera is off. Start it to photograph a panel.</p>}
            </div>

            {error && <p className="errorMessage">{error}</p>}

            <div className="buttonRow">
                {live ? (
                    <>
                        <button className="primaryButton" onClick={shoot} disabled={busy}>
                            {busy ? "Uploading…" : "Capture panel"}
                        </button>
                        <button className="ghostButton" onClick={stop}>
                            Stop camera
                        </button>
                    </>
                ) : (
                    <button className="primaryButton" onClick={start}>
                        Start camera
                    </button>
                )}
            </div>
        </div>
    );
};

export default CameraCapture;
