import { useState } from "react";
import { useNavigate } from "react-router-dom";
import CameraCapture from "../components/CameraCapture";
import { useCreateInspection, useUploadImages } from "../hooks/useInspection";
import { errorMessage } from "../apis/api";

function OfficerCapture() {
    const [title, setTitle] = useState("");
    const [inspectionId, setInspectionId] = useState<string | null>(null);
    const [reference, setReference] = useState("");
    const [shots, setShots] = useState(0);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const createInspection = useCreateInspection();
    const uploadImages = useUploadImages(inspectionId ?? undefined);

    const start = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            const created = await createInspection.mutateAsync({ title });
            setInspectionId(created.id);
            setReference(created.reference);
            setError("");
        } catch (caught) {
            setError(errorMessage(caught, "Could not start the case"));
        }
    };

    const capture = async (file: File) => {
        try {
            await uploadImages.mutateAsync([file]);
            setShots((count) => count + 1);
            setError("");
        } catch (caught) {
            setError(errorMessage(caught, "Could not upload the photo"));
        }
    };

    return (
        <div className="pageStack narrow">
            <section className="panel">
                <h1>Camera scan</h1>
                <p className="muted">
                    Photograph every panel that carries a declaration. A declaration the camera never saw cannot be
                    assessed.
                </p>
            </section>

            {!inspectionId ? (
                <section className="panel">
                    <form className="stackForm" onSubmit={start}>
                        <label className="fieldLabel">
                            Package or product name
                            <input
                                className="inset"
                                value={title}
                                onChange={(event) => setTitle(event.target.value)}
                                placeholder="Crunchy namkeen 41.5 g"
                                autoFocus
                            />
                        </label>
                        <button className="primaryButton" type="submit" disabled={createInspection.isPending}>
                            {createInspection.isPending ? "Starting…" : "Start scanning"}
                        </button>
                        {error && <p className="errorMessage">{error}</p>}
                    </form>
                </section>
            ) : (
                <section className="panel">
                    <div className="panelHeader">
                        <h2>Capture panels</h2>
                        <span className="pill">
                            {reference} · {shots} captured
                        </span>
                    </div>

                    <CameraCapture onCapture={capture} busy={uploadImages.isPending} />
                    {error && <p className="errorMessage">{error}</p>}

                    <div className="actionBar">
                        <button
                            className="primaryButton"
                            onClick={() => navigate(`/inspection/${inspectionId}`)}
                            disabled={!shots}
                        >
                            Done, open the case
                        </button>
                    </div>
                </section>
            )}
        </div>
    );
}

export default OfficerCapture;
