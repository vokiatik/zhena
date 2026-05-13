import React, { useState } from "react";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";

interface ProvideLinkStepProps {
    processId: string;
    onDone: () => void;
}

export default function ProvideLinkStep({ processId, onDone }: ProvideLinkStepProps) {
    const { provideLink } = useProcessInstances();
    const { showToast } = useToast();
    const [link, setLink] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!link.trim()) {
            setError("Please enter a link.");
            return;
        }
        setSubmitting(true);
        setError(null);
        try {
            const result = await provideLink(processId, link.trim());
            if (result.ok) {
                showToast("Link saved", "success");
                onDone();
            } else {
                setError("Failed to save link.");
            }
        } catch (err: any) {
            setError(err?.response?.data?.detail || err?.message || "Failed to save link.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="dp-step-body">
            <p className="dp-step-desc">
                Enter the URL of the cloud folder containing pictures for this batch.
                Picture loading from the link is in preparation — for now the link is
                stored for reference.
            </p>
            <form onSubmit={handleSubmit} className="dp-link-form">
                <input
                    type="url"
                    value={link}
                    onChange={(e) => setLink(e.target.value)}
                    placeholder="https://cloud.example.com/folder/…"
                    className="dp-link-input"
                    disabled={submitting}
                />
                {error && <p className="dp-msg dp-msg--error">{error}</p>}
                <button
                    type="submit"
                    className="button-primary dp-submit-btn"
                    disabled={submitting || !link.trim()}
                >
                    {submitting ? "Saving…" : "Save & Continue"}
                </button>
            </form>
        </div>
    );
}
