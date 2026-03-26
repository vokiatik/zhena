import { useState } from "react";
import type { PictureAttributes } from "../../types/picture_attributes";
import CustomSwitch from "../shared/switch/CustomSwitch";
import "./PictureScreeningSettings.css";

interface AttributeViewProps {
    attribute: PictureAttributes;
    referenceList: string[] | undefined;
    UpdateProcessAttribute: (processId: string, attribute: PictureAttributes) => Promise<void>;
    CreateNewAttributeReferenceType: (referenceType: string) => Promise<void>;
}

export default function AttributeView({ attribute, referenceList, UpdateProcessAttribute, CreateNewAttributeReferenceType }: AttributeViewProps) {

    const [presettingType, setPresettingType] = useState(attribute.reference_value_presetting_type || null);
    const [showNewPresettingInput, setShowNewPresettingInput] = useState(false);
    const [newPresettingValue, setNewPresettingValue] = useState("");

    const handleToggleShown = (checked: boolean) => {
        const updatedAttribute = { ...attribute, is_shown: checked };
        UpdateProcessAttribute(attribute.process_id, updatedAttribute);
    };

    const handleToggleEditable = (checked: boolean) => {
        const updatedAttribute = { ...attribute, is_editable: checked };
        UpdateProcessAttribute(attribute.process_id, updatedAttribute);
    };

    const handleSaveReferenceValuePresettingType = (newType: string) => {
        const updatedAttribute = { ...attribute, reference_value_presetting_type: newType };
        UpdateProcessAttribute(attribute.process_id, updatedAttribute);
    }


    const ReferenceValuePresettingDropdown = () => {
        return (
            <div className="reference-value-presetting-dropdown">
                <label className="reference-value-presetting-label">Reference Value Presetting Type:</label>
                <div className="select-container">
                    <select
                        value={attribute.reference_value_presetting_type || ""}
                        onChange={(e) => setPresettingType(e.target.value)}
                        className="dropdown"
                    >
                        <option className="dropdown-option" value="">None</option>
                        {referenceList?.map((ref) => (
                            <option key={ref} value={ref} className="dropdown-option">{ref}</option>
                        ))}
                    </select>
                    <button onClick={() => setShowNewPresettingInput(!showNewPresettingInput)} className="refresh-button">{showNewPresettingInput ? "Cancel" : "Add New"}</button>
                </div>
                {showNewPresettingInput && (
                    <div className="new-presetting-input">
                        <input
                            type="text"
                            value={newPresettingValue}
                            onChange={(e) => setNewPresettingValue(e.target.value)}
                            className="new-presetting-input-field"
                        />
                        <button
                            onClick={() => {
                                if (newPresettingValue.trim()) {
                                    CreateNewAttributeReferenceType(newPresettingValue);
                                    setNewPresettingValue("");
                                    setShowNewPresettingInput(false);
                                }
                            }}
                            className="save-button"
                        >
                            Save
                        </button>
                    </div>
                )}
                <button onClick={() => handleSaveReferenceValuePresettingType(presettingType || "")} className="save-button">Save</button>
            </div>
        );
    };

    return (
        <div className="attribute-view">
            <h2 className="attribute-view-header">{attribute.title}</h2>
            <CustomSwitch
                label="Shown"
                checked={attribute.is_shown}
                onChange={handleToggleShown} />
            <CustomSwitch
                label="Editable"
                checked={attribute.is_editable}
                onChange={handleToggleEditable}
            />
            <ReferenceValuePresettingDropdown />
        </div>
    );
}
