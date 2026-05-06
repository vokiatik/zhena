import { useEffect, useState } from "react";
import type { ColumnDef, FkOption, TableRow } from "../../hooks/useTableEditor";
import CustomModal from "../shared/modal/CustomModal";
import CustomSwitch from "../shared/switch/CustomSwitch";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import { useApi } from "../../api";

interface Props {
    schema: ColumnDef[];
    onClose: () => void;
    onSave: (data: TableRow) => Promise<boolean>;
}

type FieldErrors = Record<string, string>;

function isBooleanColumn(col: ColumnDef): boolean {
    return col.type.toUpperCase().includes("BOOLEAN");
}

function isDateColumn(col: ColumnDef): boolean {
    return col.type.toUpperCase().includes("DATE") || col.type.toUpperCase().includes("TIMESTAMP");
}

function initialValue(col: ColumnDef): unknown {
    if (col.default_value !== null && col.default_value !== undefined) return col.default_value;
    if (isBooleanColumn(col)) return false;
    return "";
}

export default function RowAddModal({ schema, onClose, onSave }: Props) {
    // Skip auto-generated columns (PK, server defaults, created_at, deleted, …)
    const editableCols = schema.filter((c) => !c.auto_generated);

    const [form, setForm] = useState<TableRow>(() =>
        Object.fromEntries(editableCols.map((c) => [c.name, initialValue(c)]))
    );
    const [errors, setErrors] = useState<FieldErrors>({});
    const [saving, setSaving] = useState(false);

    // FK dropdown options: colName → [{value, label}]
    const [fkOptions, setFkOptions] = useState<Record<string, FkOption[]>>({});
    const [fkLoading, setFkLoading] = useState<Record<string, boolean>>({});
    const { get } = useApi();

    // Fetch options for every FK column on mount
    useEffect(() => {
        editableCols
            .filter((c) => c.foreign_key != null)
            .forEach(async (col) => {
                const fk = col.foreign_key!;
                setFkLoading((prev) => ({ ...prev, [col.name]: true }));
                try {
                    const res = await get<{ success: boolean; data: FkOption[] }>(
                        `/admin/table-editor/fk-options/${fk.table}?label_column=${encodeURIComponent(fk.label_column)}`
                    );
                    if (res.data.success) {
                        setFkOptions((prev) => ({ ...prev, [col.name]: res.data.data }));
                    }
                } catch {
                    // leave empty — column falls back to text input
                } finally {
                    setFkLoading((prev) => ({ ...prev, [col.name]: false }));
                }
            });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

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

        // Convert empty-string FK values to null for nullable FK columns
        const submitData: TableRow = {};
        for (const col of editableCols) {
            const val = form[col.name];
            if (val === "" && col.foreign_key && col.nullable) {
                submitData[col.name] = null;
            } else {
                submitData[col.name] = val;
            }
        }

        setSaving(true);
        const ok = await onSave(submitData);
        setSaving(false);
        if (ok) onClose();
    }

    return (
        <CustomModal
            modalTitle="Add Row"
            SaveButtonName={saving ? "Adding…" : "Add"}
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

                            {col.foreign_key ? (
                                /* FK — render a searchable dropdown */
                                <CustomDropdown
                                    options={fkOptions[col.name] ?? []}
                                    value={String(form[col.name] ?? "") || null}
                                    onChange={(v) => setValue(col, v || "")}
                                    searchable
                                    placeholder={
                                        fkLoading[col.name]
                                            ? "Loading…"
                                            : col.nullable
                                                ? "(none)"
                                                : "Select…"
                                    }
                                    error={hasError}
                                />
                            ) : isBooleanColumn(col) ? (
                                <CustomSwitch
                                    checked={val === true || strVal === "true"}
                                    onChange={(checked) => setValue(col, checked)}
                                />
                            ) : isDateColumn(col) ? (
                                <input
                                    type={
                                        col.type.toUpperCase().includes("DATE") &&
                                            !col.type.toUpperCase().includes("TIMESTAMP")
                                            ? "date"
                                            : "datetime-local"
                                    }
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
