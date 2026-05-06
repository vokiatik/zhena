import { useState } from "react";
import { usePictureScreening } from "../../hooks/usePictureScreening";
import { usePictureScreeningSettings } from "../../hooks/usePictureScreeningSettings";
import type { PictureItem } from "../../types/picture";
import PictureViewer from "./PictureViewer";
import VerifiedPictureModal from "./VerifiedPictureModal";
import DeclinedPictureModal from "./DeclinedPictureModal";
import "./PictureScreening.css";

interface PictureScreeningProps {
    role: string;
    processId?: string;
}

export default function PictureScreening({ role, processId }: PictureScreeningProps) {
    const [activeTab, setActiveTab] = useState<"unverified" | "verified" | "declined">("unverified");
    const [selectedPicture, setSelectedPicture] = useState<PictureItem | null>(null);
    const [selectedDeclined, setSelectedDeclined] = useState<PictureItem | null>(null);

    const {
        currentPicture,
        unverifiedPictures,
        verifiedPictures,
        declinedPictures,
        total,
        isLoading,
        error,
        verifyAndNext,
        updateVerified,
        declineAndNext,
        updateDeclined,
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
                <button
                    className={`ps-tab${activeTab === "declined" ? " ps-tab--active" : ""}`}
                    onClick={() => setActiveTab("declined")}
                    type="button"
                >
                    Declined ({declinedPictures.length})
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
                            onDecline={processId ? declineAndNext : undefined}
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

            {activeTab === "declined" && (
                <div className="ps-declined-list">
                    {declinedPictures.length === 0 ? (
                        <p className="ps-done">No declined pictures yet.</p>
                    ) : (
                        declinedPictures.map((pic) => (
                            <button
                                key={pic.id}
                                className="ps-declined-item"
                                onClick={() => setSelectedDeclined(pic)}
                                type="button"
                                aria-label="View declined picture details"
                            >
                                <img src={String(pic.advertisement_id ?? "")} alt="declined" className="ps-declined-img" />
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

            {selectedDeclined && (
                <DeclinedPictureModal
                    picture={selectedDeclined}
                    settings={settings}
                    onClose={() => setSelectedDeclined(null)}
                    onSave={updateDeclined}
                />
            )}
        </div>
    );
}
