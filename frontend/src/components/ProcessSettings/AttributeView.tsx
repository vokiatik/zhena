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
    AddNewProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    UpdateProcessAttribute: (attribute: PictureAttribute) => Promise<void>;
    CreateNewAttributeReferenceType: (referenceType: string) => Promise<void>;
    setShowAttributeView: (show: boolean) => void;
    DeleteProcessAttribute: (processId: string, attributeId: string) => Promise<void>;
}

export default function AttributeView({
    attribute,
    tableColumns,
    referenceList,
    curentProcessId,
    AddNewProcessAttribute,
    UpdateProcessAttribute,
    setShowAttributeView,
    DeleteProcessAttribute,
}: AttributeViewProps) {
    const defaultAttribute: PictureAttribute = {
        id: "",
        process_id: curentProcessId || "",
        title: "",
        is_shown: true,
        is_editable: true,
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
                    label="Reference Type (Dropdown Tag)"
                    options={referenceList?.map(ref => ({ value: ref.id, label: ref.reference_type_name })) || []}
                    defaultValue={newAttribute.reference_type_id}
                    onChange={(value) => setNewAttribute({ ...newAttribute, reference_type_id: value })}
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
                <button
                    onClick={
                        () => DeleteProcessAttribute(newAttribute.process_id, newAttribute.id)
                    }
                    className="button-danger"
                >
                    Delete Attribute
                </button>
            </div>
        </div>
    );
}
