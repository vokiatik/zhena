import { useEffect, useRef, useState } from "react";
import type { ColumnDef, TableRow } from "../../hooks/useTableEditor";
import RowUpdateModal from "./RowUpdateModal";
import RowAddModal from "./RowAddModal";

interface Props {
    columns: ColumnDef[];
    rows: TableRow[];
    total: number;
    page: number;
    pageSize: number;
    sortColumn: string | null;
    sortDir: "asc" | "desc";
    editable: boolean;
    onPageChange: (page: number) => void;
    onSort: (column: string) => void;
    onDelete: (rowId: string) => void;
    onUpdate: (rowId: string, data: TableRow) => Promise<boolean>;
    onAdd: (data: TableRow) => Promise<boolean>;
}

const MAX_PAGE_BUTTONS = 7;

function formatCell(val: unknown): string {
    if (val === null || val === undefined) return "";
    if (typeof val === "boolean") return val ? "true" : "false";
    return String(val);
}

export default function DataTable({
    columns,
    rows,
    total,
    page,
    pageSize,
    sortColumn,
    sortDir,
    editable,
    onPageChange,
    onSort,
    onDelete,
    onUpdate,
    onAdd,
}: Props) {
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const [editingRow, setEditingRow] = useState<TableRow | null>(null);
    const [addingRow, setAddingRow] = useState(false);

    function pageButtons(): (number | "…")[] {
        if (totalPages <= MAX_PAGE_BUTTONS) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }
        const pages: (number | "…")[] = [1];
        const start = Math.max(2, page - 2);
        const end = Math.min(totalPages - 1, page + 2);
        if (start > 2) pages.push("…");
        for (let p = start; p <= end; p++) pages.push(p);
        if (end < totalPages - 1) pages.push("…");
        pages.push(totalPages);
        return pages;
    }

    return (
        <>
            {editable && (
                <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
                    <button
                        className="button-primary"
                        style={{ padding: "6px 16px", fontSize: "0.85rem" }}
                        onClick={() => setAddingRow(true)}
                    >
                        + Add Row
                    </button>
                </div>
            )}
            <div className="ts-table-wrap">
                <table className="ts-table">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col.name}
                                    className={`sortable${sortColumn === col.name ? " sorted" : ""}`}
                                    onClick={() => onSort(col.name)}
                                    title={`Sort by ${col.name}`}
                                >
                                    {col.name}
                                    <span className="sort-icon">
                                        {sortColumn === col.name
                                            ? sortDir === "asc" ? "▲" : "▼"
                                            : "⇅"}
                                    </span>
                                </th>
                            ))}
                            {editable && <th>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length + (editable ? 1 : 0)}>
                                    <div className="ts-empty">No rows found</div>
                                </td>
                            </tr>
                        ) : (
                            rows.map((row) => {
                                const rowId = String(row.id);
                                return (
                                    <tr key={rowId}>
                                        {columns.map((col) => (
                                            <td key={col.name} title={formatCell(row[col.name])}>
                                                {formatCell(row[col.name])}
                                            </td>
                                        ))}
                                        {editable && (
                                            <td>
                                                <div className="actions-cell">
                                                    <button
                                                        className="button-primary"
                                                        style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                                                        onClick={() => setEditingRow(row)}
                                                    >
                                                        Update
                                                    </button>
                                                    <button
                                                        className="button-danger"
                                                        style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                                                        onClick={() => onDelete(rowId)}
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </td>
                                        )}
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="ts-pagination">
                <span className="ts-pagination__info">
                    {total} total — page {page} of {totalPages}
                </span>
                <div className="ts-pagination__pages">
                    <button
                        className="ts-pagination__page-btn"
                        disabled={page === 1}
                        onClick={() => onPageChange(page - 1)}
                    >
                        ‹
                    </button>
                    {pageButtons().map((p, idx) =>
                        p === "…" ? (
                            <span key={`ellipsis-${idx}`} style={{ padding: "6px 8px", color: "#6b7280" }}>
                                …
                            </span>
                        ) : (
                            <button
                                key={p}
                                className={`ts-pagination__page-btn${page === p ? " active" : ""}`}
                                onClick={() => onPageChange(p as number)}
                            >
                                {p}
                            </button>
                        )
                    )}
                    <button
                        className="ts-pagination__page-btn"
                        disabled={page === totalPages}
                        onClick={() => onPageChange(page + 1)}
                    >
                        ›
                    </button>
                </div>
            </div>

            {/* Update Modal */}
            {editingRow && (
                <RowUpdateModal
                    row={editingRow}
                    schema={columns}
                    onClose={() => setEditingRow(null)}
                    onSave={async (updated) => {
                        const ok = await onUpdate(String(editingRow.id), updated);
                        return ok;
                    }}
                />
            )}

            {/* Add Modal */}
            {addingRow && (
                <RowAddModal
                    schema={columns}
                    onClose={() => setAddingRow(false)}
                    onSave={async (data) => {
                        const ok = await onAdd(data);
                        return ok;
                    }}
                />
            )}
        </>
    );
}
