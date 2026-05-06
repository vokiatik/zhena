import { useState } from "react";
import type { PictureAttribute } from "../../types/picture_attributes";
import type { referenceListType } from "../../types/ref_list";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import CustomSwitch from "../shared/switch/CustomSwitch";

import "./ProcessSettings.css";


interface AttributeViewProps {
    attribute?: PictureAttribute;
    tableColumns?: string[] | null;
    referenceList: referenceListType[] | undefined;
    curentProcessId?: string;
    setEditAttribute?: (attribute: PictureAttribute | undefined) => void;
    AddNewProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    UpdateProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    CreateNewAttributeReferenceType: (referenceType: string) => Promise<void>;
    setShowAttributeView: (show: boolean) => void;
}

export default function AttributeView({
    attribute,
    tableColumns,
    referenceList,
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
        reference_type_id: undefined,
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
        setEditAttribute && setEditAttribute(undefined);
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
                        { value: "dropdown", label: "Dropdown (single)" },
                        { value: "multi_select", label: "Dropdown (multi-select)" },
                    ]}
                    value={newAttribute.input_type ?? "text"}
                    onChange={(value) => setNewAttribute({ ...newAttribute, input_type: value, reference_type_id: ["dropdown", "multi_select"].includes(value) ? newAttribute.reference_type_id : undefined })}
                />
                {(newAttribute.input_type === "dropdown" || newAttribute.input_type === "multi_select") && (
                    <CustomDropdown
                        label="Reference Type (Dropdown Options)"
                        options={referenceList?.map(ref => ({ value: ref.id, label: ref.reference_type_name })) || []}
                        defaultValue={newAttribute.reference_type_id}
                        onChange={(value) => setNewAttribute({ ...newAttribute, reference_type_id: value })}
                    />
                )}
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
