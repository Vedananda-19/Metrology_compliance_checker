import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ImageIntake from "../components/ImageIntake";
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

    const addFiles = async (files: File[], fallback: string) => {
        try {
            await uploadImages.mutateAsync(files);
            setShots((count) => count + files.length);
            setError("");
        } catch (caught) {
            setError(errorMessage(caught, fallback));
            throw caught;
        }
    };

    return (
        <div className="pageStack narrow">
            <section className="panel">
                <h1>New inspection</h1>
                <p className="muted">
                    Photograph every panel that carries a declaration, or upload the photos you already took. A
                    declaration the camera never saw cannot be assessed.
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
                            {createInspection.isPending ? "Starting…" : "Start and add images"}
                        </button>
                        {error && <p className="errorMessage">{error}</p>}
                    </form>
                </section>
            ) : (
                <section className="panel">
                    <div className="panelHeader">
                        <h2>Package images</h2>
                        <span className="pill">
                            {reference} · {shots} added
                        </span>
                    </div>

                    <ImageIntake
                        busy={uploadImages.isPending}
                        uploadLabel="Add images"
                        onCapture={(file) => addFiles([file], "Could not keep this photo")}
                        onUpload={(files) => addFiles(files, "Could not upload the images")}
                    />
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
