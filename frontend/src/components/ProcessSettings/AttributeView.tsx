import { useState } from "react";
import type { PictureAttribute } from "../../types/picture_attributes";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import CustomSwitch from "../shared/switch/CustomSwitch";

import "./ProcessSettings.css";


interface AttributeViewProps {
    attribute?: PictureAttribute;
    tableColumns?: string[] | null;
    curentProcessId?: string;
    setEditAttribute?: (attribute: PictureAttribute | undefined) => void;
    AddNewProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    UpdateProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    setShowAttributeView: (show: boolean) => void;
}

export default function AttributeView({
    attribute,
    tableColumns,
    curentProcessId,
    setEditAttribute,
    AddNewProcessAttribute,
    UpdateProcessAttribute,
    setShowAttributeView,
}: AttributeViewProps) {
    const defaultAttribute: PictureAttribute = {
        id: "",
        process_id: curentProcessId || "",
        title: "",
        is_shown: true,
        is_editable: true,
        is_nullable: true,
        input_type: "text",
        created_at: new Date().toISOString(),
    }

    const [newAttribute, setNewAttribute] = useState<PictureAttribute>(attribute || defaultAttribute);


    const handleSaveAttribute = () => {
        if (attribute?.id) {
            UpdateProcessAttribute(newAttribute);
        } else {
            AddNewProcessAttribute(newAttribute);
        }
        setShowAttributeView(false);
    };
    const HandleDeleteAttribute = () => {
        if (setEditAttribute) setEditAttribute(undefined);
    };

    return (
        <div className="new-attribute-settings">
            <h2 className="attribute-view-header">{attribute?.title || "New Attribute settings"}</h2>
            <div className="new-attribute-dropdowns">
                {!attribute?.title && <CustomDropdown
                    label="Attribute Title"
                    options={tableColumns?.map(col => ({ value: col, label: col })) || []}
                    defaultValue={newAttribute.title}
                    onChange={(value) => setNewAttribute({ ...newAttribute, title: value })}
                />
                }
                <CustomDropdown
                    label="Input Type"
                    options={[
                        { value: "text", label: "Text" },
                        { value: "number", label: "Number" },
                    ]}
                    value={newAttribute.input_type ?? "text"}
                    onChange={(value) => setNewAttribute({ ...newAttribute, input_type: value })}
                />
            </div>
            <div className="attribute-switches">
                <CustomSwitch
                    label="Shown"
                    checked={newAttribute.is_shown}
                    onChange={(checked) => setNewAttribute({ ...newAttribute, is_shown: checked })} />
                <CustomSwitch
                    label="Editable"
                    checked={newAttribute.is_editable}
                    onChange={(checked) => setNewAttribute({ ...newAttribute, is_editable: checked })}
                />
            </div>

            <div className="attribute-view-buttons">
                <button
                    onClick={() => handleSaveAttribute()}
                    className="button-primary"
                >
                    Save Attribute
                </button>

                {attribute?.id &&
                    <button
                        onClick={HandleDeleteAttribute}
                        className="button-danger"
                    >
                        Cancel editing
                    </button>
                }
            </div>
        </div>
    );
}
