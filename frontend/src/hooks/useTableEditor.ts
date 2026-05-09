import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import { useToast } from "../contexts/ToastContext";

export interface TableSetting {
    id: string;
    table_name: string;
    display_name: string;
    visible: boolean;
    only_admin: boolean;
    editable: boolean;
    uploadable: boolean;
    upload_prefix: string | null;
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

    const [schema, setSchema] = useState<ColumnDef[]>([]);
    const [rows, setRows] = useState<TableRow[]>([]);
    const [total, setTotal] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    // ── Meta settings ────────────────────────────────────────────────────────

    const getTableSettings = useCallback(async () => {
        const res = await get<{ success: boolean; data: TableSetting[] }>("/admin/table-settings");
        if (res.data.success) {
            return res.data.data;
        } else {
            throw new Error("Failed to load table settings");
        }
    }, [get]);

    const { data: tableSettings, isPending: isTableSettingsPending, error: tableSettingsError, refetch: refetchTableSettings } = useQuery({
        queryKey: ['table_settings'],
        queryFn: getTableSettings,
    });

    const updateTableSetting = useCallback(
        async (id: string, patch: Omit<TableSetting, "id" | "table_name" | "display_name">) => {
            try {
                const res = await put<{ success: boolean; data: TableSetting }>(
                    `/admin/table-settings/${id}`,
                    patch
                );
                if (res.data.success) {
                    refetchTableSettings();
                    showToast("Setting updated", "success");
                    return true;
                }
                return false;
            } catch {
                showToast("Failed to update setting", "error");
                return false;
            }
        },
        [put, showToast, refetchTableSettings]
    );

    // ── Table editor ─────────────────────────────────────────────────────────

    const getVisibleTables = useCallback(async () => {
        const res = await get<{ success: boolean; data: TableSetting[] }>("/admin/table-editor/tables");
        if (res.data.success) {
            return res.data.data;
        } else {
            throw new Error("Failed to load tables");
        }
    }, [get]);

    const { data: visibleTables, isPending: isVisibleTablesPending, error: visibleTablesError, refetch: refetchVisibleTables } = useQuery({
        queryKey: ['visible_tables'],
        queryFn: getVisibleTables,
    });

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
        isTableSettingsPending,
        tableSettingsError,
        refetchTableSettings,
        updateTableSetting,
        // editor
        visibleTables,
        isVisibleTablesPending,
        visibleTablesError,
        refetchVisibleTables,
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
