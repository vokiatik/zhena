import { useProcessSettings } from "../../hooks/useProcessSettings";
import { useParams } from "react-router-dom";
import AttributeSettingsForm from "./AttributeSettingForm";
import "./PictureScreeningSettings.css";

export default function ProcessSettingsForm() {

    const { processId } = useParams();
    const {
        process,
        isprocessPending,
        processError,
        UpdateProcess
    } = useProcessSettings();

    if (isprocessPending) return <div>Loading...</div>;
    if (processError) return <div>Error loading processs: {processError.message}</div>;

    return (
        <div className="process-settings-form">
            <h2 className="process-settings-header">Process Settings</h2>
            <div className="process-settings-item">
                <label className="process-settings-label">Title:</label>
                <input
                    type="text"
                    value={process?.title || ""}
                    onChange={(e) => UpdateProcess(processId || "", { title: e.target.value, description: process?.description || "" })}
                    className="process-settings-input"
                />
            </div>
            <div className="process-settings-item">
                <label className="process-settings-label">Description:</label>
                <textarea
                    value={process?.description || ""}
                    onChange={(e) => UpdateProcess(processId || "", { title: process?.title || "", description: e.target.value })}
                    className="process-settings-textarea"
                />
            </div>
            <AttributeSettingsForm
                processId={processId || ""}
                attributeList={process?.attributes || []}
            />
        </div>

    );
}