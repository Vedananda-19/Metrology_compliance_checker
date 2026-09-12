import type { IconName } from "./Icon";
import Icon from "./Icon";

export type ResultView = "images" | "ocr" | "declarations" | "findings";

export const RESULT_STEPS: {
    key: ResultView;
    label: string;
    hint: string;
    icon: IconName;
}[] = [
    { key: "images", label: "Images", hint: "Panels on the package", icon: "aperture" },
    { key: "ocr", label: "OCR text", hint: "What Vision read", icon: "lines" },
    { key: "declarations", label: "Declarations", hint: "Correct the model", icon: "spark" },
    { key: "findings", label: "Violations", hint: "Review and decide", icon: "flag" },
];

type Props = {
    current: ResultView;
    available: ResultView[];
    counts: Partial<Record<ResultView, string>>;
    onSelect: (view: ResultView) => void;
};

const ResultNav = ({ current, available, counts, onSelect }: Props) => {
    const open = new Set(available);

    return (
        <nav className="resultNav" aria-label="Inspection results">
            {RESULT_STEPS.map((step, index) => {
                const enabled = open.has(step.key);
                return (
                    <button
                        key={step.key}
                        type="button"
                        className={`resultStep ${current === step.key ? "isCurrent" : ""} ${enabled ? "" : "isLocked"}`}
                        disabled={!enabled}
                        onClick={() => enabled && onSelect(step.key)}
                    >
                        <span className="resultStepIndex">{index + 1}</span>
                        <span className="resultStepIcon" aria-hidden="true">
                            <Icon name={step.icon} size={16} />
                        </span>
                        <span className="resultStepCopy">
                            <strong>{step.label}</strong>
                            <small>{counts[step.key] || step.hint}</small>
                        </span>
                    </button>
                );
            })}
        </nav>
    );
};

export default ResultNav;
