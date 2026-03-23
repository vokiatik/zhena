import { useState, useEffect, useCallback, useRef } from "react";
import type { PictureItem } from "../../types/picture";

interface PictureViewerProps {
    picture: PictureItem;
    previousPicture: PictureItem | null;
    canCancelVerification?: boolean;
    onVerify: (data: Record<string, string>) => Promise<void>;
    onGoBack: () => void;
    onUnverify: (data: Record<string, string>) => Promise<void>;
}

const HIDDEN_FIELDS = new Set(["id", "verified", "created_at"]);
const SAVE_DELAY = 3000;

export default function PictureViewer({ picture, previousPicture, canCancelVerification, onVerify, onGoBack, onUnverify }: PictureViewerProps) {
    // Extract editable text fields from the picture object
    const getEditableFields = useCallback((pic: PictureItem): Record<string, string> => {
        const fields: Record<string, string> = {};
        for (const [key, value] of Object.entries(pic)) {
            if (HIDDEN_FIELDS.has(key)) continue;
            if (typeof value === "string" || typeof value === "number") {
                fields[key] = String(value);
            }
        }
        return fields;
    }, []);

    const [fields, setFields] = useState<Record<string, string>>(() => getEditableFields(picture));
    const [saving, setSaving] = useState(false);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Reset fields when picture changes
    useEffect(() => {
        setFields(getEditableFields(picture));
        setSaving(false);
        if (timerRef.current) {
            clearTimeout(timerRef.current);
            timerRef.current = null;
        }
    }, [picture, getEditableFields]);

    const cancelSave = useCallback(() => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        setSaving(false);
    }, []);

    const startSave = useCallback(() => {
        if (saving) return;
        setSaving(true);
        timerRef.current = setTimeout(async () => {
            timerRef.current = null;
            setSaving(false);
            await onVerify(fields);
        }, SAVE_DELAY);
    }, [saving, fields, onVerify]);

    // Listen for any keypress to cancel save banner
    useEffect(() => {
        if (!saving) return;
        const handler = (e: KeyboardEvent) => {
            // Prevent the key from also triggering other actions while cancelling
            e.preventDefault();
            cancelSave();
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, [saving, cancelSave]);

    const handleFieldChange = (key: string, value: string) => {
        setFields((prev) => ({ ...prev, [key]: value }));
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !saving) {
            e.preventDefault();
            startSave();
        }
    };

    return (
        <div className="pv-wrapper" onKeyDown={handleKeyDown}>
            {/* Go-back button */}
            {previousPicture && (
                <button className="pv-back-btn" onClick={onGoBack} type="button">
                    ← Get back
                </button>
            )}

            {/* Picture display */}
            <div className="pv-image-container">
                <img src={fields.advertisement_id} alt="screening" className="pv-image" />
            </div>

            {/* Editable fields */}
            <div className="pv-fields">
                {Object.entries(fields).map(([key, value]) => (
                    <label key={key} className="pv-field">
                        <span className="pv-field-label">{key}</span>
                        <input
                            type="text"
                            className="pv-field-input"
                            value={value}
                            onChange={(e) => handleFieldChange(key, e.target.value)}
                        />
                    </label>
                ))}
            </div>
            <div className="pv-buttons">
                {canCancelVerification && (
                    <button className="pv-warn-btn" onClick={() => onUnverify(fields)} type="button">
                        Cancel verification
                    </button>
                )}
                {/* OK / save button */}
                <button className="pv-ok-btn" onClick={startSave} type="button">
                    OK
                </button>
            </div>

            {/* Full-screen save banner overlay */}
            {saving && (
                <div className="pv-save-overlay">
                    <p className="pv-save-text">Saving in progress. Press any key to cancel.</p>
                </div>
            )}
        </div>
    );
}
