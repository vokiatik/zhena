import { useEffect, useRef, useState } from "react";
import "./CustomDropdown.css";

interface DropdownOption {
    value: string;
    label: string;
}

interface CustomDropdownProps {
    label?: string;
    defaultValue?: string;
    value?: string;
    options?: DropdownOption[];
    onChange?: (value: string) => void;
    searchable?: boolean;
    placeholder?: string;
}

export default function CustomDropdown({
    label,
    defaultValue,
    value,
    options = [],
    onChange,
    searchable = false,
    placeholder = "Select an option",
}: CustomDropdownProps) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const [selected, setSelected] = useState<DropdownOption | null>(
        options.find((o) => o.value === (value ?? defaultValue)) ?? null
    );
    const containerRef = useRef<HTMLDivElement>(null);

    // Sync when controlled value changes externally
    useEffect(() => {
        if (value !== undefined) {
            setSelected(value ? (options.find((o) => o.value === value) ?? null) : null);
        }
    }, [value, options]);

    // Close on outside click
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

    const filtered = search
        ? options.filter((o) => o.label.toLowerCase().includes(search.toLowerCase()))
        : options;

    function handleSelect(option: DropdownOption | null) {
        setSelected(option);
        setOpen(false);
        setSearch("");
        onChange?.(option?.value ?? "");
    }

    return (
        <div className="dropdown-container" ref={containerRef}>
            {label && <label className="dropdown-label">{label}</label>}
            <button
                type="button"
                className={`dropdown-trigger${open ? " open" : ""}`}
                onClick={() => setOpen((v) => !v)}
                aria-haspopup="listbox"
                aria-expanded={open}
            >
                <span className={selected ? "" : "dropdown-placeholder"}>
                    {selected ? selected.label : placeholder}
                </span>
                <span className="dropdown-chevron" aria-hidden="true">
                    {open ? "▲" : "▼"}
                </span>
            </button>

            {open && (
                <div className="dropdown-menu" role="listbox">
                    {searchable && (
                        <div className="dropdown-search-wrapper">
                            <input
                                autoFocus
                                type="text"
                                className="dropdown-search"
                                placeholder="Search…"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                onClick={(e) => e.stopPropagation()}
                            />
                        </div>
                    )}
                    <ul className="dropdown-list">
                        <li
                            className={`dropdown-item${!selected ? " selected" : ""}`}
                            role="option"
                            aria-selected={!selected}
                            onClick={() => handleSelect(null)}
                        >
                            None
                        </li>
                        {filtered.length > 0 ? (
                            filtered.map((option) => (
                                <li
                                    key={option.value}
                                    className={`dropdown-item${selected?.value === option.value ? " selected" : ""
                                        }`}
                                    role="option"
                                    aria-selected={selected?.value === option.value}
                                    onClick={() => handleSelect(option)}
                                >
                                    {option.label}
                                </li>
                            ))
                        ) : (
                            <li className="dropdown-item dropdown-no-results">No results</li>
                        )}
                    </ul>
                </div>
            )}
        </div>
    );
}