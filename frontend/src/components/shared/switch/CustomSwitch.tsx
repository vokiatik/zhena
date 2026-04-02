import "./customSwitch.css"

interface CustomSwitchProps {
    label?: string;
    checked: boolean;
    disabled?: boolean;
    onChange: (checked: boolean) => void;
}

export default function CustomSwitch({ label, checked, disabled, onChange }: CustomSwitchProps) {
    return (
        <div className="custom-switch-container">
            {label && <span className="switch-label">{label}</span>}
            <label className="switch">
                <input type="checkbox" checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
                <span className="slider round"></span>
            </label>
        </div>
    );
}