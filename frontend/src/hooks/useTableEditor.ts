import { useCallback, useState } from "react";
import { useApi } from "../api";
import { useToast } from "../contexts/ToastContext";

export interface TableSetting {
    id: string;
    table_name: string;
    display_name: string;
    visible: boolean;
    only_admin: boolean;
    editable: boolean;
}

export interface FkOption {
    value: string;
    label: string;
}

export interface ForeignKeyInfo {
    table: string;
    label_column: string;
}

export interface ColumnDef {
    name: string;
    type: string;
    nullable: boolean;
    primary_key: boolean;
    /** True → auto-generated (PK, server default, deleted, created_at, …). Skip in Add form. */
    auto_generated: boolean;
    /** Scalar Python-level default to pre-fill in the form. Null if none or callable. */
    default_value: unknown;
    /** FK reference config, or null if not a foreign key. */
    foreign_key: ForeignKeyInfo | null;
}

export interface TableRow {
    [key: string]: unknown;
}

export interface TableRowsResult {
    rows: TableRow[];
    total: number;
}

export function useTableEditor() {
    const { get, post, put, del } = useApi();
    const { showToast } = useToast();

    const [tableSettings, setTableSettings] = useState<TableSetting[]>([]);
    const [visibleTables, setVisibleTables] = useState<TableSetting[]>([]);
    const [schema, setSchema] = useState<ColumnDef[]>([]);
    const [rows, setRows] = useState<TableRow[]>([]);
    const [total, setTotal] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    // ── Meta settings ────────────────────────────────────────────────────────

    const fetchTableSettings = useCallback(async () => {
        setIsLoading(true);
        try {
            const res = await get<{ success: boolean; data: TableSetting[] }>("/admin/table-settings");
            if (res.data.success) {
                setTableSettings(res.data.data);
            }
        } catch (e) {
            showToast("Failed to load table settings", "error");
        } finally {
            setIsLoading(false);
        }
    }, [get, showToast]);

    const updateTableSetting = useCallback(
        async (id: string, patch: Omit<TableSetting, "id" | "table_name" | "display_name">) => {
            try {
                const res = await put<{ success: boolean; data: TableSetting }>(
                    `/admin/table-settings/${id}`,
                    patch
                );
                if (res.data.success) {
                    setTableSettings((prev) =>
                        prev.map((s) => (s.id === id ? res.data.data : s))
                    );
                    showToast("Setting updated", "success");
                    return true;
                }
                return false;
            } catch {
                showToast("Failed to update setting", "error");
                return false;
            }
        },
        [put, showToast]
    );

    // ── Table editor ─────────────────────────────────────────────────────────

    const fetchVisibleTables = useCallback(async () => {
        try {
            const res = await get<{ success: boolean; data: TableSetting[] }>("/admin/table-editor/tables");
            if (res.data.success) {
                setVisibleTables(res.data.data);
            }
        } catch {
            showToast("Failed to load tables", "error");
        }
    }, [get, showToast]);

    const fetchSchema = useCallback(
        async (tableName: string) => {
            try {
                const res = await get<{ success: boolean; data: ColumnDef[] }>(
                    `/admin/table-editor/${tableName}/schema`
                );
                if (res.data.success) {
                    setSchema(res.data.data);
                    return res.data.data;
                }
                return [];
            } catch {
                showToast("Failed to load schema", "error");
                return [];
            }
        },
        [get, showToast]
    );

    const fetchRows = useCallback(
        async (
            tableName: string,
            page: number,
            pageSize: number,
            sortColumn?: string,
            sortDir?: string
        ) => {
            setIsLoading(true);
            try {
                const params = new URLSearchParams({
                    page: String(page),
                    page_size: String(pageSize),
                    ...(sortColumn ? { sort_column: sortColumn } : {}),
                    ...(sortDir ? { sort_dir: sortDir } : {}),
                });
                const res = await get<{ success: boolean; data: TableRowsResult }>(
                    `/admin/table-editor/${tableName}/rows?${params}`
                );
                if (res.data.success) {
                    setRows(res.data.data.rows);
                    setTotal(res.data.data.total);
                }
            } catch {
                showToast("Failed to load rows", "error");
            } finally {
                setIsLoading(false);
            }
        },
        [get, showToast]
    );

    const deleteRow = useCallback(
        async (tableName: string, rowId: string) => {
            try {
                const res = await del<{ success: boolean }>(`/admin/table-editor/${tableName}/rows/${rowId}`);
                if (res.data.success) {
                    setRows((prev) => prev.filter((r) => String(r.id) !== rowId));
                    setTotal((t) => t - 1);
                    showToast("Row deleted", "success");
                    return true;
                }
                return false;
            } catch {
                showToast("Failed to delete row", "error");
                return false;
            }
        },
        [del, showToast]
    );

    const addRow = useCallback(
        async (tableName: string, data: TableRow): Promise<TableRow | null> => {
            try {
                const res = await post<{ success: boolean; data: TableRow }>(
                    `/admin/table-editor/${tableName}/rows`,
                    { data }
                );
                if (res.data.success) {
                    showToast("Row added", "success");
                    return res.data.data;
                }
                return null;
            } catch {
                showToast("Failed to add row", "error");
                return null;
            }
        },
        [post, showToast]
    );

    const fetchFkOptions = useCallback(
        async (refTable: string, labelColumn: string): Promise<FkOption[]> => {
            try {
                const res = await get<{ success: boolean; data: FkOption[] }>(
                    `/admin/table-editor/fk-options/${refTable}?label_column=${encodeURIComponent(labelColumn)}`
                );
                if (res.data.success) return res.data.data;
                return [];
            } catch {
                return [];
            }
        },
        [get]
    );

    const updateRow = useCallback(
        async (tableName: string, rowId: string, data: TableRow) => {
            try {
                const res = await put<{ success: boolean }>(
                    `/admin/table-editor/${tableName}/rows/${rowId}`,
                    { data }
                );
                if (res.data.success) {
                    showToast("Row updated", "success");
                    return true;
                }
                return false;
            } catch {
                showToast("Failed to update row", "error");
                return false;
            }
        },
        [put, showToast]
    );

    return {
        // meta
        tableSettings,
        fetchTableSettings,
        updateTableSetting,
        // editor
        visibleTables,
        fetchVisibleTables,
        schema,
        fetchSchema,
        rows,
        total,
        isLoading,
        fetchRows,
        deleteRow,
        addRow,
        fetchFkOptions,
        updateRow,
    };
}
