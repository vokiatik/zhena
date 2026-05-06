import type { PictureAttribute } from "../../types/picture_attributes";
import CustomDropdown from "../shared/dropdown/CustomDropdown";

interface PictureFieldListProps {
    fields: Record<string, string>;
    settingsMap: Map<string, PictureAttribute>;
    hasSettings: boolean;
    onFieldChange: (key: string, value: string) => void;
    onShowPreset: (key: string) => void;
    invalidFields?: Set<string>;
}

export default function PictureFieldList({ fields, settingsMap, hasSettings, onFieldChange, onShowPreset, invalidFields = new Set() }: PictureFieldListProps) {
    return (
        <div className="pv-fields">
            {Object.entries(fields)
                .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
                .map(([key, value]) => {
                    const attr = settingsMap.get(key);
                    if (hasSettings && !attr) return null;
                    if (attr && !attr.is_shown) return null;

                    const isDisabled = attr ? !attr.is_editable : false;
                    const hasDropdown = attr?.reference_type_id;

                    return (
                        <label key={key} className="pv-field">
                            <span className="pv-field-label">{key}{invalidFields.has(key) && <span style={{ color: "#f87171", marginLeft: 4 }}>required</span>}</span>
                            {hasDropdown ? (
                                <div className="pv-dropdown-wrapper">
                                    <CustomDropdown
                                        options={
                                            attr.reference_values?.map((r) => (
                                                {
                                                    label: r.value,
                                                    value: r.id
                                                }
                                            )) ?? []
                                        }
                                        value={attr.reference_values?.find((r) => String(r.value) === value || r.id === value)?.id ?? null}
                                        onChange={(val) => onFieldChange(key, val)}
                                        searchable
                                        error={invalidFields.has(key)}
                                    />
                                    <button
                                        className="button-primary"
                                        onClick={() => onShowPreset(key)}
                                        type="button"
                                        style={{ marginInline: "5px" }}
                                    >
                                        Add new value
                                    </button>
                                </div>
                            ) : (
                                <input
                                    type="text"
                                    className="pv-field-input"
                                    value={value}
                                    disabled={isDisabled}
                                    onChange={(e) => onFieldChange(key, e.target.value)}
                                />
                            )}
                        </label>
                    );
                })}
        </div>
    );
}
