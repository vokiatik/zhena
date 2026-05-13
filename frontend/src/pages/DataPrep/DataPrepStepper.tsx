import React from "react";

export const DATA_PREP_STEPS = [
    { key: "file_upload", label: "File Upload" },
    { key: "link", label: "Provide Link" },
    { key: "analyst_review", label: "Analyst Review" },
    { key: "marketing_review", label: "Marketing Review" },
    { key: "completed", label: "Complete" },
] as const;

export function getStepIndex(status: string): number {
    switch (status) {
        case "initiated": return 0;
        case "awaiting_link": return 1;
        case "analyst_review": return 2;
        case "marketing_review": return 3;
        case "completed": return 4;
        default: return 0;
    }
}

interface DataPrepStepperProps {
    currentStepIdx: number;
}

export default function DataPrepStepper({ currentStepIdx }: DataPrepStepperProps) {
    return (
        <div className="dp-stepper">
            {DATA_PREP_STEPS.map((step, idx) => {
                const isActive = idx === currentStepIdx;
                const isDone = idx < currentStepIdx;
                return (
                    <React.Fragment key={step.key}>
                        {idx > 0 && (
                            <div
                                className={`dp-stepper-line ${isDone || isActive ? "dp-stepper-line--done" : ""}`}
                            />
                        )}
                        <div
                            className={[
                                "dp-stepper-step",
                                isActive ? "dp-stepper-step--active" : "",
                                isDone ? "dp-stepper-step--done" : "",
                            ]
                                .filter(Boolean)
                                .join(" ")}
                        >
                            <div className="dp-stepper-circle">
                                {isDone ? "✓" : idx + 1}
                            </div>
                            <span className="dp-stepper-label">{step.label}</span>
                        </div>
                    </React.Fragment>
                );
            })}
        </div>
    );
}
