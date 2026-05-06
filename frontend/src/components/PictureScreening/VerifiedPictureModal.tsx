import { useState } from "react";
import type { PictureItem } from "../../types/picture";
import type { PictureAttribute } from "../../types/picture_attributes";
import CustomDropdown from "../shared/dropdown/CustomDropdown";

const HIDDEN_FIELDS = new Set(["id", "verified", "created_at"]);

interface VerifiedPictureModalProps {
    picture: PictureItem;
    settings?: PictureAttribute[];
    onClose: () => void;
    onSave: (pictureId: string, data: Record<string, string>) => Promise<void>;
}

export default function VerifiedPictureModal({ picture, settings, onClose, onSave }: VerifiedPictureModalProps) {
    const rawFields = Object.entries(picture).filter(
        ([key, value]) =>
            !HIDDEN_FIELDS.has(key) &&
            (typeof value === "string" || typeof value === "number")
    ) as [string, string | number][];

    const settingsMap = new Map(settings?.map((s) => [s.title, s]) ?? []);

    const [isEditing, setIsEditing] = useState(false);
    const [editFields, setEditFields] = useState<Record<string, string>>(
        () => Object.fromEntries(rawFields.map(([k, v]) => [k, String(v)]))
    );
    const [isSaving, setIsSaving] = useState(false);
    const [invalidFields, setInvalidFields] = useState<Set<string>>(new Set());

    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) onClose();
    };

    const handleSave = async () => {
        // Validate non-nullable editable fields
        const invalid = new Set<string>();
        for (const [key, value] of Object.entries(editFields)) {
            const attr = settingsMap.get(key);
            if (attr?.is_editable && !attr.is_nullable) {
                const isEmpty = !value || value === "" || value === "undefined" || value === "null";
                if (isEmpty) invalid.add(key);
            }
        }
        if (invalid.size > 0) {
            setInvalidFields(invalid);
            return;
        }
        setIsSaving(true);
        try {
            await onSave(picture.id, editFields);
            setIsEditing(false);
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancelEdit = () => {
        setEditFields(Object.fromEntries(rawFields.map(([k, v]) => [k, String(v)])));
        setInvalidFields(new Set());
        setIsEditing(false);
    };

    const hasEditableFields = rawFields.some(([key]) => {
        const attr = settingsMap.get(key);
        return attr?.is_editable ?? false;
    });

    return (
        <div className="vpm-backdrop" onClick={handleBackdropClick}>
            <div className="vpm-modal">
                <button className="vpm-close" onClick={onClose} type="button" aria-label="Close">
                    ✕
                </button>
                <div className="vpm-image-container">
                    <img
                        src={String(picture.advertisement_id ?? "")}
                        alt="verified"
                        className="vpm-image"
                    />
                </div>
                <div className="vpm-fields">
                    {rawFields.map(([key]) => {
                        const attr = settingsMap.get(key);
                        const isEditable = isEditing && (attr?.is_editable ?? false);
                        const value = editFields[key] ?? "";
                        return (
                            <div key={key} className="vpm-field">
                                <span className="vpm-field-label">{key}</span>
                                {isEditable ? (
                                    attr?.reference_type_id ? (
                                        <CustomDropdown
                                            options={
                                                attr.reference_values?.map((r) => (
                                                    {
                                                        label: r.value,
                                                        value: r.id
                                                    }
                                                )) ?? []
                                            }
                                            defaultValue={attr.reference_values?.find((r) => String(r.value) === value)?.id ?? undefined}
                                            onChange={(val) => {
                                                setEditFields((p) => ({ ...p, [key]: val }));
                                                if (val && val !== "") {
                                                    setInvalidFields((p) => { const n = new Set(p); n.delete(key); return n; });
                                                }
                                            }}
                                            searchable
                                            error={invalidFields.has(key)}
                                        />
                                    ) : (
                                        <input
                                            className="vpm-field-input"
                                            type="text"
                                            value={value}
                                            onChange={(e) => setEditFields((p) => ({ ...p, [key]: e.target.value }))}
                                        />
                                    )
                                ) : (
                                    <span className="vpm-field-value">{value || "—"}</span>
                                )}
                            </div>
                        );
                    })}
                </div>
                <div className="vpm-actions">
                    {!isEditing ? (
                        hasEditableFields && (
                            <button className="button-secondary" onClick={() => setIsEditing(true)} type="button">
                                Edit
                            </button>
                        )
                    ) : (
                        <>
                            <button className="button-primary" onClick={handleSave} disabled={isSaving} type="button">
                                {isSaving ? "Saving…" : "Save"}
                            </button>
                            <button className="button-secondary" onClick={handleCancelEdit} disabled={isSaving} type="button">
                                Cancel
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

