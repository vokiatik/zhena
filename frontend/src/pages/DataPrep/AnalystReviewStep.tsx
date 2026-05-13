import { useState } from "react";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";
import { PictureScreening } from "../../components/PictureScreening";

interface AnalystReviewStepProps {
    processId: string;
    canAct: boolean;
    onDone: () => void;
}

export default function AnalystReviewStep({ processId, canAct, onDone }: AnalystReviewStepProps) {
    const { analystConfirm } = useProcessInstances();
    const { showToast } = useToast();
    const [confirming, setConfirming] = useState(false);

    const handleConfirm = async () => {
        setConfirming(true);
        try {
            const result = await analystConfirm(processId);
            if (result.ok) {
                showToast("Analyst review completed", "success");
                onDone();
            } else {
                showToast("Failed to confirm review", "error");
            }
        } catch {
            showToast("Failed to confirm review", "error");
        } finally {
            setConfirming(false);
        }
    };

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
                <PictureScreening role="analyst" processId={processId} />
            </div>
            <div className="dp-step-footer">
                <button
                    className="button-primary dp-submit-btn"
                    onClick={handleConfirm}
                    disabled={confirming}
                >
                    {confirming ? "Completing…" : "Complete Review"}
                </button>
            </div>
        </div>
    );
}
