import { PictureScreening } from "../../components/PictureScreening";

interface AnalystReviewStepProps {
    processId: string;
    canAct: boolean;
    onDone: () => void;
}

export default function AnalystReviewStep({ processId, canAct, onDone }: AnalystReviewStepProps) {
    if (!canAct) {
        return (
            <div className="dp-step-body">
                <div className="dp-waiting">
                    <p>Waiting for analyst to complete picture review…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dp-step-body">
            <p className="dp-step-desc">
                Review the pictures below. When you have finished verifying all items,
                click "Complete Review" to advance to marketing review.
            </p>
            <div className="dp-screening-wrapper">
                <PictureScreening processId={processId} onDone={onDone} />
            </div>
        </div>
    );
}