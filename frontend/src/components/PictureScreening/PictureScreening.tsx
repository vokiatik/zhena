import { useState, useEffect } from "react";
import { toDirectImageUrl } from "./imageUtils";
import { usePictureScreening } from "../../hooks/usePictureScreening";
import { usePictureScreeningSettings } from "../../hooks/usePictureScreeningSettings";
import { useAdvertisementScreening } from "../../hooks/useAdvertisementScreening";
import { useApi } from "../../api";
import type { PictureItem } from "../../types/picture";
import type { AdvertisementItem } from "../../types/advertisement";
import PictureViewer from "./PictureViewer";
import AdvertisementViewer from "./AdvertisementViewer";
import VerifiedPictureModal from "./VerifiedPictureModal";
import DeclinedPictureModal from "./DeclinedPictureModal";
import "./PictureScreening.css";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";

interface PictureScreeningProps {
    processId?: string;
    onDone?: () => void;
}

export default function PictureScreening({ processId, onDone }: PictureScreeningProps) {
    const { get } = useApi();
    const [activeTab, setActiveTab] = useState<"unverified" | "verified" | "declined">("unverified");
    const [selectedPicture, setSelectedPicture] = useState<PictureItem | null>(null);
    const [selectedDeclined, setSelectedDeclined] = useState<PictureItem | null>(null);
    const [selectedVerifiedAd, setSelectedVerifiedAd] = useState<AdvertisementItem | null>(null);
    const [selectedDeclinedAd, setSelectedDeclinedAd] = useState<AdvertisementItem | null>(null);
    const [processTypeName, setProcessTypeName] = useState<string | null>(null);
    const [typeLoading, setTypeLoading] = useState(!!processId);

    const { analystConfirm } = useProcessInstances();
    const { showToast } = useToast();
    const [confirming, setConfirming] = useState(false);

    const handleConfirm = async () => {
        if (!processId) return;
        setConfirming(true);
        try {
            const result = await analystConfirm(processId);
            if (result.ok) {
                showToast("Analyst review completed", "success");
                onDone?.();
            } else {
                showToast("Failed to confirm review", "error");
            }
        } catch {
            showToast("Failed to confirm review", "error");
        } finally {
            setConfirming(false);
        }
    };

    // Determine process type when processId is provided
    useEffect(() => {
        if (!processId) return;
        setTypeLoading(true);
        get<{ type_name: string }>(`/process-instances/${processId}`)
            .then((res) => setProcessTypeName(res.data.type_name))
            .catch(() => setProcessTypeName(null))
            .finally(() => setTypeLoading(false));
    }, [processId, get]);

    const isDataPrep = processTypeName === "data_prep";

    // ── Advertisement screening (data_prep process) ──────────────
    const adScreening = useAdvertisementScreening(processId ?? "__none__");

    // ── Legacy picture screening ─────────────────────────────────
    const legacyScreening = usePictureScreening(processId, isDataPrep !== false);
    const { settings, isLoading: settingsLoading } = usePictureScreeningSettings(isDataPrep === false ? processId : undefined);

    if (typeLoading || (isDataPrep ? adScreening.isLoading : legacyScreening.isLoading || settingsLoading)) {
        return <div className="ps-container"><p className="ps-loading">Loading…</p></div>;
    }

    const err = isDataPrep ? adScreening.error : legacyScreening.error;
    if (err) {
        return <div className="ps-container"><p className="ps-error">{err}</p></div>;
    }

    // ── Data-prep advertisement view ─────────────────────────────
    if (isDataPrep) {
        const { currentAdvertisement, unverified, verified, declined, options, total, verifyAndNext, declineAndNext } = adScreening;

        return (
            <div className="ps-container">
                <div className="ps-header">
                    <h2>Total is {total} advertisements</h2>
                </div>

                <div className="ps-tabs">
                    <button className={`ps-tab${activeTab === "unverified" ? " ps-tab--active" : ""}`} onClick={() => setActiveTab("unverified")} type="button">
                        Unverified ({unverified.length})
                    </button>
                    <button className={`ps-tab${activeTab === "verified" ? " ps-tab--active" : ""}`} onClick={() => setActiveTab("verified")} type="button">
                        Verified ({verified.length})
                    </button>
                    <button className={`ps-tab${activeTab === "declined" ? " ps-tab--active" : ""}`} onClick={() => setActiveTab("declined")} type="button">
                        Declined ({declined.length})
                    </button>
                </div>

                {activeTab === "unverified" && (
                    <>
                        {!currentAdvertisement ? (
                            <p className="ps-done">All advertisements have been reviewed!</p>
                        ) : (
                            <AdvertisementViewer
                                advertisement={currentAdvertisement}
                                options={options}
                                onVerify={verifyAndNext}
                                onDecline={declineAndNext}
                            />
                        )}
                    </>
                )}

                {activeTab === "verified" && (
                    <div className="ps-verified-list">
                        {verified.length === 0 ? (
                            <p className="ps-done">No verified advertisements yet.</p>
                        ) : (
                            verified.map((ad) => (
                                <button key={ad.id} className="ps-verified-item" onClick={() => setSelectedVerifiedAd(ad)} type="button">
                                    <img src={toDirectImageUrl(ad.links?.find(l => !l.is_incorrect)?.url ?? ad.url ?? "")} alt="verified ad" className="ps-verified-img" />
                                </button>
                            ))
                        )}
                    </div>
                )}

                {activeTab === "declined" && (
                    <div className="ps-declined-list">
                        {declined.length === 0 ? (
                            <p className="ps-done">No declined advertisements yet.</p>
                        ) : (
                            declined.map((ad) => (
                                <button key={ad.id} className="ps-declined-item" onClick={() => setSelectedDeclinedAd(ad)} type="button">
                                    <img src={toDirectImageUrl(ad.links?.find(l => !l.is_incorrect)?.url ?? ad.url ?? "")} alt="declined ad" className="ps-declined-img" />
                                </button>
                            ))
                        )}
                    </div>
                )}

                {selectedVerifiedAd && (
                    <div className="ps-modal-overlay" onClick={() => setSelectedVerifiedAd(null)}>
                        <div className="ps-modal" onClick={(e) => e.stopPropagation()}>
                            <h3>Verified Advertisement Details</h3>
                            <AdvertisementViewer
                                advertisement={selectedVerifiedAd}
                                options={options}
                                onVerify={async (payload) => {
                                    await adScreening.updateVerified(selectedVerifiedAd.id, payload);
                                    setSelectedVerifiedAd(null);
                                }}
                            />
                            <button className="button-secondary" onClick={() => setSelectedVerifiedAd(null)} type="button">Close</button>
                        </div>
                    </div>
                )}

                {selectedDeclinedAd && (
                    <div className="ps-modal-overlay" onClick={() => setSelectedDeclinedAd(null)}>
                        <div className="ps-modal" onClick={(e) => e.stopPropagation()}>
                            <h3>Declined Advertisement Details</h3>
                            <AdvertisementViewer
                                advertisement={selectedDeclinedAd}
                                options={options}
                                onVerify={async (payload) => {
                                    await adScreening.updateDeclined(selectedDeclinedAd.id, payload, false);
                                    setSelectedDeclinedAd(null);
                                }}
                                onDecline={async () => setSelectedDeclinedAd(null)}
                            />
                            <button className="button-secondary" onClick={() => setSelectedDeclinedAd(null)} type="button">Close</button>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    // ── Legacy picture view ──────────────────────────────────────
    const {
        currentPicture,
        unverifiedPictures,
        verifiedPictures,
        declinedPictures,
        total,
        verifyAndNext: legacyVerifyAndNext,
        updateVerified,
        declineAndNext: legacyDeclineAndNext,
        updateDeclined,
    } = legacyScreening;

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
                    Unverified ({unverifiedPictures?.length})
                </button>
                <button
                    className={`ps-tab${activeTab === "verified" ? " ps-tab--active" : ""}`}
                    onClick={() => setActiveTab("verified")}
                    type="button"
                >
                    Verified ({verifiedPictures?.length})
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
                        <button
                            className="button-primary dp-submit-btn"
                            onClick={handleConfirm}
                            disabled={confirming}
                        >
                            {confirming ? "Completing…" : "Complete Review"}
                        </button>

                    ) : (
                        <PictureViewer
                            picture={currentPicture}
                            settings={settings}
                            onVerify={legacyVerifyAndNext}
                            onDecline={processId ? legacyDeclineAndNext : undefined}
                        />
                    )}
                </>
            )}

            {activeTab === "verified" && (
                <div className="ps-verified-list">
                    {verifiedPictures?.length === 0 ? (
                        <p className="ps-done">No verified pictures yet.</p>
                    ) : (
                        verifiedPictures?.map((pic) => (
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
