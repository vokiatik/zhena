import { useState } from "react";
import { usePictureScreening } from "../../hooks/usePictureScreening";
import { usePictureScreeningSettings } from "../../hooks/usePictureScreeningSettings";
import type { PictureItem } from "../../types/picture";
import PictureViewer from "./PictureViewer";
import VerifiedPictureModal from "./VerifiedPictureModal";
import "./PictureScreening.css";

interface PictureScreeningProps {
    role: string;
    processId?: string;
}

export default function PictureScreening({ role, processId }: PictureScreeningProps) {
    const [activeTab, setActiveTab] = useState<"unverified" | "verified">("unverified");
    const [selectedPicture, setSelectedPicture] = useState<PictureItem | null>(null);

    const {
        currentPicture,
        unverifiedPictures,
        verifiedPictures,
        total,
        isLoading,
        error,
        verifyAndNext,
        updateVerified,
    } = usePictureScreening(role, processId);

    const { settings, isLoading: settingsLoading } = usePictureScreeningSettings(processId);

    if (isLoading || settingsLoading) {
        return <div className="ps-container"><p className="ps-loading">Loading pictures…</p></div>;
    }

    if (error) {
        return <div className="ps-container"><p className="ps-error">{error}</p></div>;
    }

    return (
        <div className="ps-container">
            <div className="ps-header">
                <h2>Total is {total} pictures</h2>
            </div>

            <div className="ps-tabs">
                <button
                    className={`ps-tab${activeTab === "unverified" ? " ps-tab--active" : ""}`}
                    onClick={() => setActiveTab("unverified")}
                    type="button"
                >
                    Unverified ({unverifiedPictures.length})
                </button>
                <button
                    className={`ps-tab${activeTab === "verified" ? " ps-tab--active" : ""}`}
                    onClick={() => setActiveTab("verified")}
                    type="button"
                >
                    Verified ({verifiedPictures.length})
                </button>
            </div>

            {activeTab === "unverified" && (
                <>
                    {!currentPicture ? (
                        <p className="ps-done">All pictures have been verified!</p>
                    ) : (
                        <PictureViewer
                            picture={currentPicture}
                            settings={settings}
                            onVerify={verifyAndNext}
                        />
                    )}
                </>
            )}

            {activeTab === "verified" && (
                <div className="ps-verified-list">
                    {verifiedPictures.length === 0 ? (
                        <p className="ps-done">No verified pictures yet.</p>
                    ) : (
                        verifiedPictures.map((pic) => (
                            <button
                                key={pic.id}
                                className="ps-verified-item"
                                onClick={() => setSelectedPicture(pic)}
                                type="button"
                                aria-label="View picture details"
                            >
                                <img src={String(pic.advertisement_id ?? "")} alt="verified" className="ps-verified-img" />
                            </button>
                        ))
                    )}
                </div>
            )}

            {selectedPicture && (
                <VerifiedPictureModal
                    picture={selectedPicture}
                    settings={settings}
                    onClose={() => setSelectedPicture(null)}
                    onSave={updateVerified}
                />
            )}
        </div>
    );
}
