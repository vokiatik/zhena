import "./CustomDropdown.css";


interface CustomDropdownProps {
    label?: string;
    defaultValue?: string;
    options?: { value: string; label: string }[];
    onChange?: (value: string) => void;
}

export default function CustomDropdown({
    label,
    defaultValue,
    options,
    onChange,
}: CustomDropdownProps) {
    return (
        <div className="dropdown-container">
            <label className="dropdown-label">{label || "Select an option"}</label>
            <div className="select-container">
                <select
                    defaultValue={defaultValue || ""}
                    onChange={(e) => onChange?.(e.target.value)}
                    className="dropdown"
                >
                    <option className="dropdown-option" value="">None</option>
                    {options?.map((option) => (
                        <option key={option.value} value={option.value} className="dropdown-option">{option.label}</option>
                    ))}
                </select>
            </div>
        </div>
    );
}