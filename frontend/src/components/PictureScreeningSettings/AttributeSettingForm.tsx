import { useState } from "react";
import type { PictureAttributes } from "../../types/picture_attributes";
import AttributeView from "./AttributeView";
import { useAttributesSettings } from "../../hooks/useAttributesSettings";
import "./PictureScreeningSettings.css";

interface AttributeSettingsFormProps {
    processId: string | null;
    attributeList: PictureAttributes[] | null;
}
export default function AttributeSettingsForm(
    {
        processId,
        attributeList
    }: AttributeSettingsFormProps) {

    const {
        referenceList,
        AddNewProcessAttribute,
        DeleteProcessAttribute,
        UpdateProcessAttribute,
        CreateNewAttributeReferenceType
    } = useAttributesSettings();

    const [newAttribute, setNewAttribute] = useState<PictureAttributes>({
        id: "",
        process_id: "",
        title: "",
        is_shown: true,
        is_editable: true,
        reference_value_presetting_type: undefined,
        created_at: new Date().toISOString(),
    });

    const handleUpdateNewAttribute = async (processId: string, attribute: PictureAttributes) => {
        console.log("Updating new attribute:", processId, attribute);
        setNewAttribute(attribute);
    }

    return (
        <div className="attribute-settings-form">
            <h2 className="attribute-settings-header">Attribute Settings</h2>
            <div className="attribute-item">
                <AttributeView
                    attribute={newAttribute}
                    referenceList={referenceList}
                    CreateNewAttributeReferenceType={CreateNewAttributeReferenceType}
                    UpdateProcessAttribute={handleUpdateNewAttribute}
                />
                <button
                    onClick={
                        () => AddNewProcessAttribute(processId!, newAttribute)
                    }
                    className="attribute-add-btn"
                >
                    Add Attribute
                </button>
            </div>
            {attributeList?.map((attribute) => (
                <div key={attribute.id} className="attribute-item">
                    <AttributeView
                        attribute={attribute}
                        referenceList={referenceList}
                        CreateNewAttributeReferenceType={CreateNewAttributeReferenceType}
                        UpdateProcessAttribute={UpdateProcessAttribute}
                    />
                    <button
                        onClick={
                            () => DeleteProcessAttribute(attribute.process_id, attribute.id)
                        }
                        className="attribute-delete-btn"
                    >
                        Delete Attribute
                    </button>
                </div>
            ))}
        </div>
    );
}