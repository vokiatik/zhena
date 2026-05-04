import React, { useState, useMemo } from "react";
import { createPortal } from "react-dom";
import type { ConfirmDecision, MissingReferenceValue, ValidationRequiredResponse } from "../../types/file_upload_validation";
import "./NewDictValuesModal.css";
import CustomDropdown from "../shared/dropdown/CustomDropdown";

interface Props {
    validationData: ValidationRequiredResponse;
    onConfirm: (decisions: ConfirmDecision[]) => void;
}

const PAGE_SIZE = 20;

// Palette of background colors for different type names
const TYPE_COLORS = [
    "rgba(99,102,241,0.18)",   // indigo
    "rgba(16,185,129,0.18)",   // green
    "rgba(245,158,11,0.18)",   // amber
    "rgba(239,68,68,0.18)",    // red
    "rgba(59,130,246,0.18)",   // blue
    "rgba(168,85,247,0.18)",   // purple
    "rgba(236,72,153,0.18)",   // pink
    "rgba(20,184,166,0.18)",   // teal
];

function buildTypeColorMap(values: MissingReferenceValue[]): Record<string, string> {
    const types = Array.from(new Set(values.map((v) => v.type_name)));
    const map: Record<string, string> = {};
    types.forEach((t, i) => {
        map[t] = TYPE_COLORS[i % TYPE_COLORS.length];
    });
    return map;
}

export default function NewDictValuesModal({ validationData, onConfirm }: Props): React.ReactElement {
    const { missing_values, existing_values_by_type } = validationData;

    const typeColorMap = useMemo(() => buildTypeColorMap(missing_values), [missing_values]);

    // decisions keyed by "type_id|column|value"
    const initialDecisions: Record<string, ConfirmDecision> = useMemo(() => {
        const map: Record<string, ConfirmDecision> = {};
        missing_values.forEach((mv) => {
            const key = `${mv.type_id}|${mv.column}|${mv.value}`;
            map[key] = {
                type_id: mv.type_id,
                column: mv.column,
                original_value: mv.value,
                save: true,
                replace_with: null,
            };
        });
        return map;
    }, [missing_values]);

    const [decisions, setDecisions] = useState<Record<string, ConfirmDecision>>(initialDecisions);
    const [page, setPage] = useState(1);

    const totalPages = Math.ceil(missing_values.length / PAGE_SIZE);
    const paginated = missing_values.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    function getKey(mv: MissingReferenceValue) {
        return `${mv.type_id}|${mv.column}|${mv.value}`;
    }

    function handleCheckboxChange(mv: MissingReferenceValue, checked: boolean) {
        const key = getKey(mv);
        setDecisions((prev) => ({
            ...prev,
            [key]: { ...prev[key], save: checked, replace_with: checked ? null : prev[key].replace_with },
        }));
    }

    function handleDropdownChange(mv: MissingReferenceValue, value: string) {
        const key = getKey(mv);
        const selected = value || null;
        setDecisions((prev) => ({
            ...prev,
            [key]: {
                ...prev[key],
                replace_with: selected,
                save: selected === null,
            },
        }));
    }

    function handleConfirm() {
        onConfirm(Object.values(decisions));
    }

    return createPortal(
        <div className="ndv-overlay">
            <div className="ndv-modal">
                <div className="ndv-header">
                    <h2 className="ndv-title">New Dictionary Values Found</h2>
                    <p className="ndv-subtitle">
                        The uploaded file contains values that are not yet in the reference
                        database. Review each entry: keep the checkbox checked to save it as a
                        new value, or select an existing value to replace it in the file.
                    </p>
                </div>

                <div className="ndv-body">
                    <table className="ndv-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Value</th>
                                <th>Save as new</th>
                                <th>Replace with existing</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginated.map((mv) => {
                                const key = getKey(mv);
                                const decision = decisions[key];
                                const existingOptions = existing_values_by_type[mv.type_id] ?? [];
                                const rowBg = typeColorMap[mv.type_name] ?? "transparent";

                                return (
                                    <tr key={key} style={{ backgroundColor: rowBg }}>
                                        <td className="ndv-cell ndv-cell--type">
                                            <span className="ndv-type-badge">{mv.type_name}</span>
                                        </td>
                                        <td className="ndv-cell ndv-cell--value">{mv.value}</td>
                                        <td className="ndv-cell ndv-cell--checkbox">
                                            <input
                                                type="checkbox"
                                                className="ndv-checkbox"
                                                checked={decision.save}
                                                onChange={(e) => handleCheckboxChange(mv, e.target.checked)}
                                            />
                                        </td>
                                        <td className="ndv-cell ndv-cell--dropdown">
                                            <CustomDropdown
                                                options={[
                                                    ...existingOptions.map((opt) => (
                                                        {
                                                            value: opt, label: opt
                                                        }
                                                    ))
                                                ]}
                                                value={decision.replace_with ?? ""}
                                                onChange={(value) => handleDropdownChange(mv, value)}
                                                searchable
                                            />
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                {totalPages > 1 && (
                    <div className="ndv-pagination">
                        <button
                            className="ndv-page-btn"
                            disabled={page === 1}
                            onClick={() => setPage((p) => p - 1)}
                        >
                            ‹ Prev
                        </button>
                        <span className="ndv-page-info">{page} / {totalPages}</span>
                        <button
                            className="ndv-page-btn"
                            disabled={page === totalPages}
                            onClick={() => setPage((p) => p + 1)}
                        >
                            Next ›
                        </button>
                    </div>
                )}

                <div className="ndv-footer">
                    <button className="ndv-confirm-btn" onClick={handleConfirm}>
                        Save &amp; Proceed
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
}
