import type { PictureAttribute } from "../../types/picture_attributes";
import "./ProcessSettings.css";

interface AttributeViewProps {
    attribute: PictureAttribute;
    setEditAttribute: (attribute: PictureAttribute) => void;
    DeleteProcessAttribute: (processId: string, attributeId: string) => Promise<void>;
    curentProcessId?: string;
}

export default function AttributeViewNoUpdate({
    attribute,
    setEditAttribute,
    DeleteProcessAttribute,
    curentProcessId
}: AttributeViewProps) {

    const handleSetForEdit = () => {
        setEditAttribute(attribute);
    }

    const handleDeleteAttribute = () => {
        if (attribute?.id && curentProcessId) {
            DeleteProcessAttribute(curentProcessId, attribute.id);
        }
    }

    console.log("Rendering AttributeViewNoUpdate with attribute:", attribute);
    return (
        <div className="new-attribute-settings-no-update-container">
            <div className="new-attribute-settings-no-update">
                <div className="label-value-pair">
                    <span className="attribute-label">Attribute title:</span>
                    <span className="attribute-value">{attribute?.title}</span>
                </div>
                <div className="label-value-pair">
                    <span className="attribute-label">Is Shown:</span>
                    <span className="attribute-value">{attribute?.is_shown ? "Yes" : "No"}</span>
                </div>
                <div className="label-value-pair">
                    <span className="attribute-label">Is Editable:</span>
                    <span className="attribute-value">{attribute?.is_editable ? "Yes" : "No"}</span>
                </div>
                <div className="label-value-pair">
                    <span className="attribute-label">Reference Type:</span>
                    <span className="attribute-value">{attribute?.reference_type_name || "None"}</span>
                </div>
            </div>

            <div className="attribute-view-buttons-no-update">
                <button
                    onClick={handleSetForEdit}
                    className="button-primary"
                >
                    Edit Attribute
                </button>
                <button
                    onClick={handleDeleteAttribute}
                    className="button-danger"
                >
                    Delete Attribute
                </button>
            </div>
        </div>
    );
}