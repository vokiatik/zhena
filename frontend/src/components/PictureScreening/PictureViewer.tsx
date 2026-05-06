import { useState, useEffect, useCallback } from "react";
import type { PictureItem } from "../../types/picture";
import type { PictureAttribute } from "../../types/picture_attributes";
import PictureFieldList from "./PictureFieldList";
import PresetModal from "./PresetModal";

interface PictureViewerProps {
    picture: PictureItem;
    settings?: PictureAttribute[];
    onVerify: (data: Record<string, string>) => Promise<void>;
}

const HIDDEN_FIELDS = new Set(["id", "verified", "created_at"]);

export default function PictureViewer({ picture, settings, onVerify }: PictureViewerProps) {
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
    const [isSaving, setIsSaving] = useState(false);
    const [invalidFields, setInvalidFields] = useState<Set<string>>(new Set());

    useEffect(() => {
        setFields(getEditableFields(picture));
        setInvalidFields(new Set());
    }, [picture, getEditableFields]);

    const handleFieldChange = (key: string, value: string) => {
        setFields((prev) => ({ ...prev, [key]: value }));
        if (value && value !== "") {
            setInvalidFields((prev) => { const next = new Set(prev); next.delete(key); return next; });
        }
    };

    const validate = (): boolean => {
        const invalid = new Set<string>();
        for (const [key, value] of Object.entries(fields)) {
            const attr = settingsMap.get(key);
            if (attr?.is_editable && !attr.is_nullable) {
                const isEmpty = !value || value === "" || value === "undefined" || value === "null";
                if (isEmpty) invalid.add(key);
            }
        }
        setInvalidFields(invalid);
        return invalid.size === 0;
    };

    const handleSave = async () => {
        if (isSaving) return;
        if (!validate()) return;
        setIsSaving(true);
        try {
            await onVerify(fields);
        } finally {
            setIsSaving(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !isSaving) {
            e.preventDefault();
            handleSave();
        }
    };

    const handleAddNewPresetValue = (_key: string, _newValue: string) => {
        // TODO: implement preset addition
    };

    return (
        <div className="pv-wrapper" onKeyDown={handleKeyDown}>
            <div className="pv-image-container">
                <img src={fields.advertisement_id} alt="screening" className="pv-image" />
            </div>

            <PictureFieldList
                fields={fields}
                settingsMap={settingsMap}
                hasSettings={!!hasSettings}
                onFieldChange={handleFieldChange}
                onShowPreset={setShowPreset}
                invalidFields={invalidFields}
            />

            <div className="pv-buttons">
                <button className="button-primary" onClick={handleSave} disabled={isSaving} type="button">
                    {isSaving ? "Saving…" : "OK"}
                </button>
            </div>

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
