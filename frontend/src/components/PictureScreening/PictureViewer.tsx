import { useState, useEffect, useCallback } from "react";
import type { PictureItem } from "../../types/picture";
import type { PictureAttribute } from "../../types/picture_attributes";
import { useSaveTimer } from "./useSaveTimer";
import PictureFieldList from "./PictureFieldList";
import SaveOverlay from "./SaveOverlay";
import PresetModal from "./PresetModal";

interface PictureViewerProps {
    picture: PictureItem;
    previousPicture: PictureItem | null;
    canCancelVerification?: boolean;
    settings?: PictureAttribute[];
    onVerify: (data: Record<string, string>) => Promise<void>;
    onGoBack: () => void;
    onUnverify: (data: Record<string, string>) => Promise<void>;
}

const HIDDEN_FIELDS = new Set(["id", "verified", "created_at"]);

export default function PictureViewer({ picture, previousPicture, canCancelVerification, settings, onVerify, onGoBack, onUnverify }: PictureViewerProps) {
    const settingsMap = new Map(settings?.map((s) => [s.title, s]) ?? []);
    const hasSettings = settings && settings.length > 0;

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
    const [showPreset, setShowPreset] = useState<string | null>(null);

    const { saving, start: startSave, reset: resetSave } = useSaveTimer(
        useCallback(() => onVerify(fields), [fields, onVerify])
    );

    useEffect(() => {
        setFields(getEditableFields(picture));
        resetSave();
    }, [picture, getEditableFields, resetSave]);

    const handleFieldChange = (key: string, value: string) => {
        setFields((prev) => ({ ...prev, [key]: value }));
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !saving) {
            e.preventDefault();
            startSave();
        }
    };

    const handleAddNewPresetValue = (_key: string, _newValue: string) => {
        // TODO: implement preset addition
    };

    return (
        <div className="pv-wrapper" onKeyDown={handleKeyDown}>
            {previousPicture && (
                <button className="button-secondary pv-back-btn" onClick={onGoBack} type="button">
                    ← Get back
                </button>
            )}

            <div className="pv-image-container">
                <img src={fields.advertisement_id} alt="screening" className="pv-image" />
            </div>

            <PictureFieldList
                fields={fields}
                settingsMap={settingsMap}
                hasSettings={!!hasSettings}
                onFieldChange={handleFieldChange}
                onShowPreset={setShowPreset}
            />

            <div className="pv-buttons">
                {canCancelVerification && (
                    <button className="button-danger" onClick={() => onUnverify(fields)} type="button">
                        Cancel verification
                    </button>
                )}
                <button className="button-primary" onClick={startSave} type="button">
                    OK
                </button>
            </div>

            {saving && <SaveOverlay />}

            {showPreset && settings && (
                <PresetModal
                    fieldKey={showPreset}
                    settings={settings}
                    onAdd={handleAddNewPresetValue}
                    onClose={() => setShowPreset(null)}
                />
            )}
        </div>
    );
}
