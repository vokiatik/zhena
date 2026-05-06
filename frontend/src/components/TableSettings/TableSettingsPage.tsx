import { useEffect, useState } from "react";
import "./TableSettings.css";
import { useTableEditor } from "../../hooks/useTableEditor";
import type { ColumnDef, TableRow, TableSetting } from "../../hooks/useTableEditor";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import DataTable from "./DataTable";
import TableMetaSettings from "./TableMetaSettings";
import TvLoading from "../shared/loading/TvLoading";

const PAGE_SIZE = 20;

type ActiveTab = "editor" | "meta";

export default function TableSettingsPage() {
    const {
        tableSettings,
        fetchTableSettings,
        updateTableSetting,
        visibleTables,
        fetchVisibleTables,
        schema,
        fetchSchema,
        rows,
        total,
        isLoading,
        fetchRows,
        deleteRow,
        updateRow,
    } = useTableEditor();

    const [activeTab, setActiveTab] = useState<ActiveTab>("editor");
    const [selectedTable, setSelectedTable] = useState<TableSetting | null>(null);
    const [page, setPage] = useState(1);
    const [sortColumn, setSortColumn] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

    // Bootstrap
    useEffect(() => {
        fetchTableSettings();
        fetchVisibleTables();
    }, [fetchTableSettings, fetchVisibleTables]);

    // Reload rows whenever the selected table / page / sort changes
    useEffect(() => {
        if (selectedTable) {
            fetchSchema(selectedTable.table_name);
            fetchRows(selectedTable.table_name, page, PAGE_SIZE, sortColumn ?? undefined, sortDir);
        }
    }, [selectedTable, page, sortColumn, sortDir]);

    function handleTableSelect(tableName: string) {
        const tbl = visibleTables.find((t) => t.table_name === tableName) ?? null;
        setSelectedTable(tbl);
        setPage(1);
        setSortColumn(null);
        setSortDir("asc");
    }

    function handleSort(column: string) {
        if (sortColumn === column) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        } else {
            setSortColumn(column);
            setSortDir("asc");
        }
        setPage(1);
    }

    async function handleDelete(rowId: string) {
        if (!selectedTable) return;
        await deleteRow(selectedTable.table_name, rowId);
    }

    async function handleUpdate(rowId: string, data: TableRow): Promise<boolean> {
        if (!selectedTable) return false;
        const ok = await updateRow(selectedTable.table_name, rowId, data);
        if (ok) {
            // Refresh current page
            fetchRows(selectedTable.table_name, page, PAGE_SIZE, sortColumn ?? undefined, sortDir);
        }
        return ok;
    }

    const tableOptions = visibleTables.map((t) => ({
        value: t.table_name,
        label: t.display_name,
    }));

    return (
        <div className="ts-page">
            <h1 className="ts-page__title">Table Settings</h1>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 8 }}>
                <button
                    className={activeTab === "editor" ? "button-primary" : "button-secondary"}
                    onClick={() => setActiveTab("editor")}
                >
                    Table Editor
                </button>
                <button
                    className={activeTab === "meta" ? "button-primary" : "button-secondary"}
                    onClick={() => setActiveTab("meta")}
                >
                    Visibility Settings
                </button>
            </div>

            {activeTab === "meta" && (
                <TableMetaSettings
                    settings={tableSettings}
                    onUpdate={async (id, patch) => {
                        await updateTableSetting(id, patch);
                        // Refresh visible tables list after toggling
                        fetchVisibleTables();
                    }}
                />
            )}

            {activeTab === "editor" && (
                <>
                    {/* Table selector */}
                    <div className="ts-toolbar">
                        <div className="ts-toolbar__dropdown-wrap">
                            <CustomDropdown
                                label="Select table"
                                options={tableOptions}
                                value={selectedTable?.table_name ?? ""}
                                onChange={handleTableSelect}
                                searchable
                                placeholder="Choose a table…"
                            />
                        </div>
                        {selectedTable && (
                            <span style={{ color: "#6b7280", fontSize: "0.85rem" }}>
                                {total} rows
                            </span>
                        )}
                    </div>

                    {/* Table data */}
                    {!selectedTable && (
                        <div className="ts-empty">Select a table from the dropdown to view its data.</div>
                    )}

                    {selectedTable && isLoading && <TvLoading />}

                    {selectedTable && !isLoading && (
                        <DataTable
                            columns={schema}
                            rows={rows}
                            total={total}
                            page={page}
                            pageSize={PAGE_SIZE}
                            sortColumn={sortColumn}
                            sortDir={sortDir}
                            editable={selectedTable.editable}
                            onPageChange={setPage}
                            onSort={handleSort}
                            onDelete={handleDelete}
                            onUpdate={handleUpdate}
                        />
                    )}
                </>
            )}
        </div>
    );
}
