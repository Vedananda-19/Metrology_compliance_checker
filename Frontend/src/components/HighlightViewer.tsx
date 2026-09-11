import { useEffect, useMemo, useRef, useState } from "react";
import type { ImageOcr, OcrRegion } from "../types/inspection";

type Props = {
    panels: ImageOcr[];
    imageUrls: Record<string, string>;
    focus?: { imageId: string | null; region: Partial<OcrRegion> | null } | null;
    showAllRegions?: boolean;
    height?: number;
};

const HighlightViewer = ({ panels, imageUrls, focus, showAllRegions = true, height = 420 }: Props) => {
    const [activeIndex, setActiveIndex] = useState(0);
    const [zoom, setZoom] = useState(1);
    const containerRef = useRef<HTMLDivElement>(null);

    const focusedIndex = useMemo(() => {
        if (!focus?.imageId) return null;
        const index = panels.findIndex((panel) => panel.image.id === focus.imageId);
        return index >= 0 ? index : null;
    }, [focus, panels]);

    useEffect(() => {
        if (focusedIndex !== null) setActiveIndex(focusedIndex);
    }, [focusedIndex]);

    const panel = panels[activeIndex];

    useEffect(() => {
        if (!focus?.region || focusedIndex === null || !containerRef.current) return;
        const box = focus.region;
        if (box.y1 === undefined || box.y1 === null || !panel?.image.height_px) return;
        const ratio = box.y1 / panel.image.height_px;
        containerRef.current.scrollTo({
            top: Math.max(ratio * containerRef.current.scrollHeight - height / 3, 0),
            behavior: "smooth",
        });
    }, [focus, focusedIndex, panel, height]);

    if (!panels.length) return <p className="muted">No images available for this inspection.</p>;
    if (!panel) return null;

    const width = panel.image.width_px ?? 1000;
    const imageHeight = panel.image.height_px ?? 1400;
    const isFocusedPanel = focusedIndex === activeIndex;

    return (
        <div className="viewer">
            <div className="viewerBar">
                <div className="viewerTabs">
                    {panels.map((item, index) => (
                        <button
                            key={item.image.id}
                            className={`chip ${index === activeIndex ? "chipActive" : ""}`}
                            onClick={() => setActiveIndex(index)}
                        >
                            {item.image.panel && item.image.panel !== "unspecified"
                                ? item.image.panel
                                : `Panel ${index + 1}`}
                        </button>
                    ))}
                </div>
                <div className="viewerZoom">
                    <button className="ghostButton tiny" onClick={() => setZoom((value) => Math.max(value - 0.25, 0.5))}>
                        −
                    </button>
                    <span className="muted small">{Math.round(zoom * 100)}%</span>
                    <button className="ghostButton tiny" onClick={() => setZoom((value) => Math.min(value + 0.25, 3))}>
                        +
                    </button>
                    <button className="ghostButton tiny" onClick={() => setZoom(1)}>
                        Reset
                    </button>
                </div>
            </div>

            <div className="inset viewerStage" style={{ height }} ref={containerRef}>
                <div className="viewerCanvas" style={{ width: `${zoom * 100}%` }}>
                    <img src={imageUrls[panel.image.id] ?? ""} alt={panel.image.original_filename ?? "package panel"} />
                    <svg viewBox={`0 0 ${width} ${imageHeight}`} preserveAspectRatio="none" className="viewerOverlay">
                        {showAllRegions &&
                            panel.regions.map((region) => (
                                <rect
                                    key={region.id}
                                    x={region.x1}
                                    y={region.y1}
                                    width={region.x2 - region.x1}
                                    height={region.y2 - region.y1}
                                    className="regionBox"
                                />
                            ))}
                        {isFocusedPanel && focus?.region?.x1 !== undefined && focus.region.x1 !== null && (
                            <rect
                                x={focus.region.x1}
                                y={focus.region.y1 ?? 0}
                                width={(focus.region.x2 ?? 0) - (focus.region.x1 ?? 0)}
                                height={(focus.region.y2 ?? 0) - (focus.region.y1 ?? 0)}
                                className="regionBox regionFocus"
                            />
                        )}
                    </svg>
                </div>
            </div>

            <div className="viewerFooter">
                <span className="muted small">
                    {panel.regions.length} text region(s) read
                    {panel.image.mean_ocr_confidence !== null &&
                        ` · mean confidence ${(panel.image.mean_ocr_confidence * 100).toFixed(0)}%`}
                </span>
            </div>
        </div>
    );
};

export default HighlightViewer;
