import { useState, useRef, useEffect } from "react";
import type { ReferenceValue } from "../../types/picture_attributes";

interface MultiSelectFieldProps {
    referenceValues: ReferenceValue[];
    /** Comma-separated list of selected IDs */
    value: string;
    onChange: (value: string) => void;
    disabled?: boolean;
    error?: boolean;
}

export default function MultiSelectField({
    referenceValues,
    value,
    onChange,
    disabled = false,
    error = false,
}: MultiSelectFieldProps) {
    const selectedIds = value
        ? value.split(",").map((v) => v.trim()).filter(Boolean)
        : [];

    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
                setSearch("");
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const selectedItems = selectedIds
        .map((id) => referenceValues.find((r) => r.id === id))
        .filter(Boolean) as ReferenceValue[];

    const availableOptions = referenceValues.filter(
        (r) => !selectedIds.includes(r.id)
    );

    const filtered = search
        ? availableOptions.filter((r) =>
            r.value.toLowerCase().includes(search.toLowerCase())
        )
        : availableOptions;

    const handleAdd = (id: string) => {
        const next = [...selectedIds, id];
        onChange(next.join(","));
        setSearch("");
    };

    const handleRemove = (id: string) => {
        const next = selectedIds.filter((sid) => sid !== id);
        onChange(next.join(","));
    };

    return (
        <div
            className={`ms-container${error ? " ms-error" : ""}`}
            ref={containerRef}
        >
            <div className="ms-chips">
                {selectedItems.map((item) => (
                    <span key={item.id} className="ms-chip">
                        <span className="ms-chip-label">{item.value}</span>
                        {!disabled && (
                            <button
                                type="button"
                                className="ms-chip-remove"
                                onClick={() => handleRemove(item.id)}
                                aria-label={`Remove ${item.value}`}
                            >
                                ×
                            </button>
                        )}
                    </span>
                ))}
                {!disabled && (
                    <button
                        type="button"
                        className="ms-add-btn"
                        onClick={() => setOpen((v) => !v)}
                        aria-haspopup="listbox"
                        aria-expanded={open}
                    >
                        + Add
                    </button>
                )}
            </div>

            {open && !disabled && (
                <div className="ms-dropdown" role="listbox">
                    <input
                        autoFocus
                        type="text"
                        className="ms-search"
                        placeholder="Search…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                    />
                    <ul className="ms-list">
                        {filtered.length === 0 ? (
                            <li className="ms-item ms-empty">No options</li>
                        ) : (
                            filtered.map((r) => (
                                <li
                                    key={r.id}
                                    className="ms-item"
                                    role="option"
                                    aria-selected={false}
                                    onClick={() => handleAdd(r.id)}
                                >
                                    {r.value}
                                </li>
                            ))
                        )}
                    </ul>
                </div>
            )}
        </div>
    );
}
