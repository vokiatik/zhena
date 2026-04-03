import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";
import "./LinkUpload.css";

export default function LinkUpload() {
    const [link, setLink] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { createLinkProcess } = useProcessInstances();
    const { showToast } = useToast();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!link.trim()) {
            showToast("Please enter a link", "error");
            return;
        }
        setIsSubmitting(true);
        try {
            const res = await createLinkProcess(link.trim());
            if (res.ok) {
                showToast("Link process created successfully", "success");
                navigate("/processes");
            } else {
                showToast("Failed to create process", "error");
            }
        } catch {
            showToast("Failed to create process", "error");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="link-upload-page">
            <div className="link-upload-container">
                <h1 className="link-upload-title">Create Link Process</h1>
                <p className="link-upload-description">
                    Enter the cloud folder URL containing pictures to process.
                </p>
                <form onSubmit={handleSubmit} className="link-upload-form">
                    <input
                        type="text"
                        value={link}
                        onChange={(e) => setLink(e.target.value)}
                        placeholder="https://cloud.example.com/folder/pictures"
                        className="link-upload-input"
                        disabled={isSubmitting}
                    />
                    <button
                        type="submit"
                        className="button-primary link-upload-btn"
                        disabled={isSubmitting || !link.trim()}
                    >
                        {isSubmitting ? "Creating…" : "Create Process"}
                    </button>
                </form>
            </div>
        </div>
    );
}
