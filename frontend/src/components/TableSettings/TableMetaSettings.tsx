import { useState } from "react";
import type { TableSetting } from "../../hooks/useTableEditor";
import CustomSwitch from "../shared/switch/CustomSwitch";

interface Props {
    settings: TableSetting[];
    onUpdate: (id: string, patch: Omit<TableSetting, "id" | "table_name" | "display_name">) => void;
}

export default function TableMetaSettings({ settings, onUpdate }: Props) {
    const [editingPrefix, setEditingPrefix] = useState<{ [id: string]: string }>({});

    function getPatch(s: TableSetting, overrides: Partial<Omit<TableSetting, "id" | "table_name" | "display_name">>) {
        return {
            visible: s.visible,
            only_admin: s.only_admin,
            editable: s.editable,
            uploadable: s.uploadable,
            upload_prefix: s.upload_prefix,
            ...overrides,
        };
    }

    return (
        <div>
            <h2 className="ts-section-title">Table Visibility Settings</h2>
            <div className="ts-table-wrap">
                <table className="meta-table">
                    <thead>
                        <tr>
                            <th>Table</th>
                            <th>Display Name</th>
                            <th>Visible</th>
                            <th>Admin Only</th>
                            <th>Editable</th>
                            <th>Uploadable</th>
                            <th>Upload Prefix</th>
                        </tr>
                    </thead>
                    <tbody>
                        {settings.map((s) => (
                            <tr key={s.id}>
                                <td style={{ fontFamily: "monospace", fontSize: "0.82rem" }}>{s.table_name}</td>
                                <td>{s.display_name}</td>
                                <td>
                                    <CustomSwitch
                                        checked={s.visible}
                                        onChange={(checked) =>
                                            onUpdate(s.id, getPatch(s, { visible: checked }))
                                        }
                                    />
                                </td>
                                <td>
                                    <CustomSwitch
                                        checked={s.only_admin}
                                        onChange={(checked) =>
                                            onUpdate(s.id, getPatch(s, { only_admin: checked }))
                                        }
                                    />
                                </td>
                                <td>
                                    <CustomSwitch
                                        checked={s.editable}
                                        onChange={(checked) =>
                                            onUpdate(s.id, getPatch(s, { editable: checked }))
                                        }
                                    />
                                </td>
                                <td>
                                    <CustomSwitch
                                        checked={s.uploadable}
                                        onChange={(checked) =>
                                            onUpdate(s.id, getPatch(s, { uploadable: checked }))
                                        }
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        placeholder="e.g. data_"
                                        value={editingPrefix[s.id] ?? (s.upload_prefix ?? "")}
                                        onChange={(e) =>
                                            setEditingPrefix((prev) => ({ ...prev, [s.id]: e.target.value }))
                                        }
                                        onBlur={() => {
                                            const val = editingPrefix[s.id];
                                            if (val === undefined) return;
                                            const trimmed = val.trim() || null;
                                            onUpdate(s.id, getPatch(s, { upload_prefix: trimmed }));
                                            setEditingPrefix((prev) => {
                                                const next = { ...prev };
                                                delete next[s.id];
                                                return next;
                                            });
                                        }}
                                        style={{
                                            fontFamily: "monospace",
                                            fontSize: "0.82rem",
                                            padding: "2px 6px",
                                            border: "1px solid #d1d5db",
                                            borderRadius: 4,
                                            width: 130,
                                        }}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
