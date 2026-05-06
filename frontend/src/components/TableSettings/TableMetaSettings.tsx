import { useEffect } from "react";
import type { TableSetting } from "../../hooks/useTableEditor";
import CustomSwitch from "../shared/switch/CustomSwitch";

interface Props {
    settings: TableSetting[];
    onUpdate: (id: string, patch: Omit<TableSetting, "id" | "table_name" | "display_name">) => void;
}

export default function TableMetaSettings({ settings, onUpdate }: Props) {
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
                                            onUpdate(s.id, {
                                                visible: checked,
                                                only_admin: s.only_admin,
                                                editable: s.editable,
                                            })
                                        }
                                    />
                                </td>
                                <td>
                                    <CustomSwitch
                                        checked={s.only_admin}
                                        onChange={(checked) =>
                                            onUpdate(s.id, {
                                                visible: s.visible,
                                                only_admin: checked,
                                                editable: s.editable,
                                            })
                                        }
                                    />
                                </td>
                                <td>
                                    <CustomSwitch
                                        checked={s.editable}
                                        onChange={(checked) =>
                                            onUpdate(s.id, {
                                                visible: s.visible,
                                                only_admin: s.only_admin,
                                                editable: checked,
                                            })
                                        }
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
