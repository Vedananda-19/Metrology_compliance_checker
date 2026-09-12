import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ImageUploader from "../components/ImageUploader";
import { useCreateInspection, useUploadImages } from "../hooks/useInspection";
import { errorMessage } from "../apis/api";

function Scan() {
    const [title, setTitle] = useState("");
    const [inspectionId, setInspectionId] = useState<string | null>(null);
    const [reference, setReference] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const createInspection = useCreateInspection();
    const uploadImages = useUploadImages(inspectionId ?? undefined);

    const handleCreate = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            const created = await createInspection.mutateAsync({ title });
            setInspectionId(created.id);
            setReference(created.reference);
            setError("");
        } catch (caught) {
            setError(errorMessage(caught, "Could not create the inspection"));
        }
    };

    const handleUpload = async (files: File[]) => {
        try {
            await uploadImages.mutateAsync(files);
            navigate(`/inspection/${inspectionId}`);
        } catch (caught) {
            setError(errorMessage(caught, "Could not upload the images"));
        }
    };

    return (
        <div className="pageStack narrow">
            <section className="panel">
                <h1>New inspection</h1>
                <p className="muted">
                    Record where the package was drawn from, then photograph every panel that carries a declaration.
                </p>
            </section>

            {!inspectionId ? (
                <section className="panel">
                    <form className="stackForm" onSubmit={handleCreate}>
                        <label className="fieldLabel">
                            Package or product name
                            <input
                                className="inset"
                                value={title}
                                onChange={(event) => setTitle(event.target.value)}
                                placeholder="Aquapure anti-dandruff shampoo 100 ml"
                                autoFocus
                            />
                        </label>
                        <button className="primaryButton" type="submit" disabled={createInspection.isPending}>
                            {createInspection.isPending ? "Creating…" : "Create and add images"}
                        </button>
                        {error && <p className="errorMessage">{error}</p>}
                    </form>
                </section>
            ) : (
                <section className="panel">
                    <div className="panelHeader">
                        <h2>Upload package images</h2>
                        <span className="pill">{reference}</span>
                    </div>
                    <ImageUploader onSubmit={handleUpload} busy={uploadImages.isPending} />
                    {error && <p className="errorMessage">{error}</p>}
                </section>
            )}
        </div>
    );
}

export default Scan;
