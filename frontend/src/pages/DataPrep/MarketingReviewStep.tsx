import { useState } from "react";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";
import { PictureScreening } from "../../components/PictureScreening";

interface MarketingReviewStepProps {
    processId: string;
    canAct: boolean;
    onDone: () => void;
}

export default function MarketingReviewStep({ processId, canAct, onDone }: MarketingReviewStepProps) {
    const { marketingConfirm } = useProcessInstances();
    const { showToast } = useToast();
    const [confirming, setConfirming] = useState(false);

    const handleConfirm = async () => {
        setConfirming(true);
        try {
            const result = await marketingConfirm(processId);
            if (result.ok) {
                showToast("Marketing review completed", "success");
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
                    <p>Waiting for marketing analyst to complete picture review…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dp-step-body">
            <p className="dp-step-desc">
                Review the pictures below for final marketing approval. When done,
                click "Complete Review" to finish the process.
            </p>
            <div className="dp-screening-wrapper">
                <PictureScreening processId={processId} />
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
