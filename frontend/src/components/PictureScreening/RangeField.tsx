import type { RangeValueRef, SimpleValueRef } from "../../types/advertisement";
import CustomDropdown from "../shared/dropdown/CustomDropdown";

interface RangeFieldProps {
    label: string;
    values: RangeValueRef[];
    options: SimpleValueRef[];
    onAdd: (id: string) => void;
    onRemove: (rowId: string) => void;
}

export default function RangeField({ label, values, options, onAdd, onRemove }: RangeFieldProps) {
    const selectedIds = new Set(values.map((v) => v.id));
    const availableOptions = options.filter((o) => !selectedIds.has(o.id));

    return (
        <div className="pv-range-field">
            <span className="pv-field-label">{label}</span>
            <div className="pv-range-tags">
                {values.map((v) => (
                    <span key={v.row_id} className="pv-range-tag">
                        {v.value}
                        <button
                            type="button"
                            className="pv-range-remove"
                            onClick={() => onRemove(v.row_id)}
                            aria-label={`Remove ${v.value}`}
                        >
                            ×
                        </button>
                    </span>
                ))}
            </div>
            {availableOptions.length > 0 && (
                <div className="pv-range-add">
                    <CustomDropdown
                        options={availableOptions.map((o) => ({ label: o.value, value: o.id }))}
                        value={null}
                        onChange={(val) => { if (val) onAdd(val); }}
                        searchable
                        placeholder="Add value…"
                    />
                </div>
            )}
        </div>
    );
}
