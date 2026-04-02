import "./PictureScreeningSettings.css";
import { useState } from "react";
import { useAttributesSettings } from "../../hooks/useAttributesSettings";
import type { ProcessingItem } from "../../types/processing";
import type { ProcessSettingsResult } from "../../types/ProcessSettingsResult";
import AttributeView from "./AttributeView";

interface AttributeSettingsFormProps {
    curentProcess?: ProcessingItem;
    handleSaveNewProcess?: () => Promise<ProcessSettingsResult>;
}
export default function AttributeSettingsForm({
    curentProcess,
    handleSaveNewProcess
}: AttributeSettingsFormProps) {
    const {
        tableColumns,
        referenceList,
        processAttributes,
        AddNewProcessAttribute,
        DeleteProcessAttribute,
        UpdateProcessAttribute,
        CreateNewAttributeReferenceType
    } = useAttributesSettings(curentProcess?.table_name, curentProcess?.id);

    const [showAttributeView, setShowAttributeView] = useState(false);

    const handleAddNewAttribute = async () => {
        if (!curentProcess?.id && handleSaveNewProcess) {
            const res = await handleSaveNewProcess();
            if (res?.success) {
                setShowAttributeView(true);
            }
        } else {
            setShowAttributeView(!showAttributeView);
        }
    }
    return (
        <div className="attribute-settings-form">
            <h2 className="attribute-settings-header">Attribute Settings</h2>
            <div className="attribute-item">
                {showAttributeView && (
                    <AttributeView
                        tableColumns={tableColumns}
                        referenceList={referenceList}
                        curentProcessId={curentProcess?.id}
                        AddNewProcessAttribute={AddNewProcessAttribute}
                        UpdateProcessAttribute={UpdateProcessAttribute}
                        CreateNewAttributeReferenceType={CreateNewAttributeReferenceType}
                        setShowAttributeView={setShowAttributeView}
                        DeleteProcessAttribute={DeleteProcessAttribute}
                    />
                )}
                <button
                    onClick={() => handleAddNewAttribute()}
                    className="button-primary"
                    disabled={!curentProcess}
                >
                    {showAttributeView ? "Cancel" : "Add Attribute"}
                </button>
                <label className="attribute-add-btn-note">*You need to save the process before adding attributes</label>
            </div>
            {processAttributes?.map((attribute) => (
                <div key={attribute.id} className="attribute-item">
                    <AttributeView
                        attribute={attribute}
                        tableColumns={tableColumns}
                        referenceList={referenceList}
                        AddNewProcessAttribute={AddNewProcessAttribute}
                        UpdateProcessAttribute={UpdateProcessAttribute}
                        CreateNewAttributeReferenceType={CreateNewAttributeReferenceType}
                        setShowAttributeView={setShowAttributeView}
                        DeleteProcessAttribute={DeleteProcessAttribute}
                    />
                </div>
            ))}
        </div>
    );
}