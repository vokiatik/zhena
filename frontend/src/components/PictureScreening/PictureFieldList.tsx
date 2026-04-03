import type { PictureAttribute } from "../../types/picture_attributes";

interface PictureFieldListProps {
    fields: Record<string, string>;
    settingsMap: Map<string, PictureAttribute>;
    hasSettings: boolean;
    onFieldChange: (key: string, value: string) => void;
    onShowPreset: (key: string) => void;
}

export default function PictureFieldList({ fields, settingsMap, hasSettings, onFieldChange, onShowPreset }: PictureFieldListProps) {
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
                            <span className="pv-field-label">{key}</span>
                            {hasDropdown ? (
                                <div className="pv-dropdown-wrapper">
                                    <select
                                        className="pv-field-input"
                                        value={value}
                                        disabled={isDisabled}
                                        onChange={(e) => onFieldChange(key, e.target.value)}
                                        defaultValue={fields[key] ?? ""}
                                    >
                                        <option value="">— select —</option>
                                        {attr!.reference_values!.map((ref) => (
                                            <option key={ref.id} value={ref.value}>
                                                {ref.value}
                                            </option>
                                        ))}
                                    </select>
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
