import { useState } from "react";
import type { InspectionImage, OcrText } from "../types/inspection";

type Props = {
    ocrTexts: OcrText[];
    images: InspectionImage[];
};

const OcrTextView = ({ ocrTexts, images }: Props) => {
    const [open, setOpen] = useState(true);

    const nameFor = (item: OcrText) => {
        const image = images.find((candidate) => candidate.id === item.image_id);
        return image?.original_filename ?? `Panel ${item.display_order + 1}`;
    };

    const total = ocrTexts.reduce((sum, item) => sum + item.text.length, 0);

    return (
        <div className="stack">
            <div className="panelHeader">
                <div>
                    <h2>Text read from the images</h2>
                    <p className="muted">
                        The raw OCR output the declarations were extracted from. Useful when a value looks wrong,
                        because it shows whether the reading or the extraction was at fault.
                    </p>
                </div>
                <span className="pill small">{total} characters</span>
                <button className="ghostButton small" onClick={() => setOpen((value) => !value)}>
                    {open ? "Hide" : "Show"}
                </button>
            </div>

            {open && (
                <div className="ocrList">
                    {ocrTexts.map((item) => (
                        <div key={item.id} className="inset ocrPanel">
                            <div className="ocrPanelHead">
                                <strong>{nameFor(item)}</strong>
                                <span className="muted small">{item.text.length} characters</span>
                            </div>
                            {item.text ? (
                                <pre className="ocrText">{item.text}</pre>
                            ) : (
                                <p className="muted small">No text was read from this image.</p>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OcrTextView;
