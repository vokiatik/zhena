import "./ProcessSettings.css";
import { useState } from "react";
import { useAttributesSettings } from "../../hooks/useAttributesSettings";
import type { ProcessingItem } from "../../types/processing";
import type { ProcessSettingsResult } from "../../types/ProcessSettingsResult";
import AttributeView from "./AttributeView";
import AttributeViewNoUpdate from "./AttributeViewNoUpdate";
import type { PictureAttribute } from "../../types/picture_attributes";

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
    } = useAttributesSettings(curentProcess?.type, curentProcess?.id);

    const [showAttributeView, setShowAttributeView] = useState(false);
    const [editAttribute, setEditAttribute] = useState<PictureAttribute | undefined>(undefined);

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
                    />
                )}
                <button
                    onClick={() => handleAddNewAttribute()}
                    className="button-primary"
                    disabled={!curentProcess?.id}
                >
                    {showAttributeView ? "Cancel" : "Add Attribute"}
                </button>
                <label className="attribute-add-btn-note">*You need to save the process before adding attributes</label>
            </div>
            {processAttributes?.map((attribute) => {
                if (attribute.id === editAttribute?.id) {
                    return (
                        <div key={attribute.id} className="attribute-item">
                            <AttributeView
                                attribute={editAttribute}
                                tableColumns={tableColumns}
                                referenceList={referenceList}
                                curentProcessId={curentProcess?.id}
                                setEditAttribute={setEditAttribute}
                                AddNewProcessAttribute={AddNewProcessAttribute}
                                UpdateProcessAttribute={UpdateProcessAttribute}
                                CreateNewAttributeReferenceType={CreateNewAttributeReferenceType}
                                setShowAttributeView={setShowAttributeView}
                            />
                        </div>
                    );
                }
                return (
                    <div key={attribute.id} className="attribute-item">
                        <AttributeViewNoUpdate
                            attribute={attribute}
                            setEditAttribute={setEditAttribute}
                            DeleteProcessAttribute={DeleteProcessAttribute}
                            curentProcessId={curentProcess?.id}
                        />
                    </div>
                );
            })}
        </div>
    );
}