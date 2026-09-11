import { useRef, useState } from "react";

type Pending = {
    file: File;
    preview: string;
};

type Props = {
    onSubmit: (files: File[]) => void;
    busy?: boolean;
    submitLabel?: string;
};

const ACCEPTED = ["image/jpeg", "image/png", "image/webp", "image/bmp"];

const ImageUploader = ({ onSubmit, busy, submitLabel = "Upload and continue" }: Props) => {
    const [pending, setPending] = useState<Pending[]>([]);
    const [error, setError] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    const addFiles = (files: FileList | null) => {
        if (!files) return;
        const accepted: Pending[] = [];
        for (const file of Array.from(files)) {
            if (!ACCEPTED.includes(file.type)) {
                setError(`${file.name} is not a supported image type`);
                continue;
            }
            accepted.push({ file, preview: URL.createObjectURL(file) });
        }
        if (accepted.length) setError("");
        setPending((previous) => [...previous, ...accepted]);
    };

    const remove = (index: number) => {
        setPending((previous) => {
            URL.revokeObjectURL(previous[index].preview);
            return previous.filter((_, position) => position !== index);
        });
    };

    const move = (index: number, direction: -1 | 1) => {
        setPending((previous) => {
            const target = index + direction;
            if (target < 0 || target >= previous.length) return previous;
            const next = [...previous];
            [next[index], next[target]] = [next[target], next[index]];
            return next;
        });
    };

    const submit = () => {
        if (!pending.length) {
            setError("Add at least one photograph of the package");
            return;
        }
        onSubmit(pending.map((item) => item.file));
    };

    return (
        <div className="uploader">
            <div
                className="inset dropZone"
                onClick={() => inputRef.current?.click()}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                    event.preventDefault();
                    addFiles(event.dataTransfer.files);
                }}
            >
                <strong>Drop package photographs here</strong>
                <p className="muted">
                    Front, back, side, top and bottom. Every panel that carries a declaration should be photographed,
                    because a declaration the camera never saw cannot be assessed.
                </p>
                <span className="ghostButton small">Choose files</span>
                <input
                    ref={inputRef}
                    type="file"
                    multiple
                    accept={ACCEPTED.join(",")}
                    hidden
                    onChange={(event) => {
                        addFiles(event.target.files);
                        event.target.value = "";
                    }}
                />
            </div>

            {error && <p className="errorMessage">{error}</p>}

            {pending.length > 0 && (
                <>
                    <div className="thumbGrid">
                        {pending.map((item, index) => (
                            <figure key={item.preview} className="panel thumb">
                                <img src={item.preview} alt={item.file.name} />
                                <figcaption>
                                    <span className="thumbName">{item.file.name}</span>
                                    <span className="muted small">Panel {index + 1}</span>
                                </figcaption>
                                <div className="thumbActions">
                                    <button className="ghostButton tiny" onClick={() => move(index, -1)} disabled={index === 0}>
                                        ↑
                                    </button>
                                    <button
                                        className="ghostButton tiny"
                                        onClick={() => move(index, 1)}
                                        disabled={index === pending.length - 1}
                                    >
                                        ↓
                                    </button>
                                    <button className="ghostButton tiny danger" onClick={() => remove(index)}>
                                        Remove
                                    </button>
                                </div>
                            </figure>
                        ))}
                    </div>

                    <button className="primaryButton" onClick={submit} disabled={busy}>
                        {busy ? "Uploading…" : `${submitLabel} (${pending.length})`}
                    </button>
                </>
            )}
        </div>
    );
};

export default ImageUploader;
