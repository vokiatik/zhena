import { useEffect, useState } from "react";
import type { ColumnDef, TableRow } from "../../hooks/useTableEditor";
import CustomModal from "../shared/modal/CustomModal";
import CustomSwitch from "../shared/switch/CustomSwitch";
import CustomDropdown from "../shared/dropdown/CustomDropdown";

interface Props {
    row: TableRow;
    schema: ColumnDef[];
    onClose: () => void;
    onSave: (updated: TableRow) => Promise<boolean>;
}

type FieldErrors = Record<string, string>;

function isBooleanColumn(col: ColumnDef): boolean {
    return col.type.toUpperCase().includes("BOOLEAN");
}

function isDateColumn(col: ColumnDef): boolean {
    return col.type.toUpperCase().includes("DATE") || col.type.toUpperCase().includes("TIMESTAMP");
}

const BOOL_OPTIONS = [
    { value: "true", label: "True" },
    { value: "false", label: "False" },
];

export default function RowUpdateModal({ row, schema, onClose, onSave }: Props) {
    const [form, setForm] = useState<TableRow>({ ...row });
    const [errors, setErrors] = useState<FieldErrors>({});
    const [saving, setSaving] = useState(false);

    // Editable columns = everything except primary_key columns
    const editableCols = schema.filter((c) => !c.primary_key);

    function setValue(col: ColumnDef, raw: unknown) {
        setForm((prev) => ({ ...prev, [col.name]: raw }));
        if (errors[col.name]) {
            setErrors((prev) => {
                const next = { ...prev };
                delete next[col.name];
                return next;
            });
        }
    }

    function validate(): boolean {
        const newErrors: FieldErrors = {};
        for (const col of editableCols) {
            if (!col.nullable) {
                const val = form[col.name];
                if (val === null || val === undefined || String(val).trim() === "") {
                    newErrors[col.name] = "This field is required";
                }
            }
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }

    async function handleSave() {
        if (!validate()) return;
        setSaving(true);
        const ok = await onSave(form);
        setSaving(false);
        if (ok) onClose();
    }

    return (
        <CustomModal
            modalTitle="Update Row"
            SaveButtonName={saving ? "Saving…" : "Save"}
            handleSave={handleSave}
            handleClose={onClose}
        >
            <div className="row-form">
                {editableCols.map((col) => {
                    const val = form[col.name];
                    const strVal = val === null || val === undefined ? "" : String(val);
                    const hasError = !!errors[col.name];

                    return (
                        <div key={col.name} className="row-form__field">
                            <label className={`row-form__label${!col.nullable ? " required" : ""}`}>
                                {col.name}
                                <span style={{ color: "#6b7280", fontSize: "0.72rem", marginLeft: 4 }}>
                                    ({col.type})
                                </span>
                            </label>

                            {isBooleanColumn(col) ? (
                                <CustomSwitch
                                    checked={val === true || strVal === "true"}
                                    onChange={(checked) => setValue(col, checked)}
                                />
                            ) : isDateColumn(col) ? (
                                <input
                                    type={col.type.toUpperCase().includes("DATE") && !col.type.toUpperCase().includes("TIMESTAMP") ? "date" : "datetime-local"}
                                    className={`row-form__input${hasError ? " error" : ""}`}
                                    value={strVal.substring(0, 19).replace(" ", "T")}
                                    onChange={(e) => setValue(col, e.target.value || null)}
                                />
                            ) : (
                                <input
                                    type="text"
                                    className={`row-form__input${hasError ? " error" : ""}`}
                                    value={strVal}
                                    onChange={(e) => setValue(col, e.target.value)}
                                />
                            )}

                            {hasError && (
                                <span className="row-form__error">{errors[col.name]}</span>
                            )}
                        </div>
                    );
                })}
            </div>
        </CustomModal>
    );
}
