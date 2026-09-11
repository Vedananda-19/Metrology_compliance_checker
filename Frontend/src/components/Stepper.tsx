import { STATUS_STEPS, type InspectionStatus } from "../types/inspection";

const ORDER: InspectionStatus[] = [
    "DRAFT",
    "IMAGES_UPLOADED",
    "IMAGE_REVIEW",
    "PROCESSING",
    "EXTRACTION_REVIEW",
    "CLASSIFICATION_REVIEW",
    "RULE_REVIEW",
    "COMPLIANCE_REVIEW",
    "VIOLATION_REVIEW",
    "FINAL_REVIEW",
    "FINALIZED",
];

const Stepper = ({ status }: { status: InspectionStatus }) => {
    const current = ORDER.indexOf(status);

    return (
        <ol className="stepper">
            {STATUS_STEPS.map((step) => {
                const index = ORDER.indexOf(step.status);
                const state = index < current ? "done" : index === current ? "active" : "todo";
                return (
                    <li key={step.status} className={`stepperItem stepper-${state}`}>
                        <span className="stepperDot" />
                        <span className="stepperLabel">{step.label}</span>
                    </li>
                );
            })}
        </ol>
    );
};

export default Stepper;
