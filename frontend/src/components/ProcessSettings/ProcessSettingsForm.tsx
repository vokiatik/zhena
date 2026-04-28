import { useProcessSettings } from "../../hooks/useProcessSettings";
import AttributeSettingsForm from "./AttributeSettingForm";
import "./ProcessSettings.css";
import type { ProcessingItem } from "../../types/processing";
import CustomModal from "../shared/modal/CustomModal";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import { useState } from "react";
import type { ProcessSettingsResult } from "../../types/ProcessSettingsResult";
import { useToast } from "../../contexts/ToastContext";

interface ProcessSettingsFormProps {
    ProcessItem: ProcessingItem | null;
    setShowNewProcessModal: (show: boolean) => void;
    CreateProcess: (process: ProcessingItem) => Promise<ProcessSettingsResult>;
}

export default function ProcessSettingsForm({ ProcessItem, setShowNewProcessModal, CreateProcess }: ProcessSettingsFormProps) {
    const { showToast } = useToast();

    const {
        UpdateProcess,
        availableTypes,
    } = useProcessSettings();

    const [currentProcess, setCurrentProcess] = useState<ProcessingItem>(ProcessItem ||
        {
            id: "",
            title: "",
            description: "",
            type: "",
            created_at: new Date().toISOString(),
            attributes: []
        } as ProcessingItem
    );

    const handleSave = async () => {
        if (currentProcess.type === "") {
            showToast("Please select a process type.", "error");
            return {} as ProcessSettingsResult;
        }
        if (currentProcess.title === "") {
            showToast("Please enter a process title.", "error");
            return {} as ProcessSettingsResult;
        }
        if (currentProcess.description === "") {
            showToast("Please enter a process description.", "error");
            return {} as ProcessSettingsResult;
        }
        let res: ProcessSettingsResult;
        if (ProcessItem) {
            res = await UpdateProcess(currentProcess);
        } else {
            res = await CreateProcess(currentProcess);
        }
        console.log("Process save result:", res);
        if (res.success) {
            showToast(`Process ${ProcessItem ? "updated" : "created"} successfully`, "success");
            setShowNewProcessModal(false);
        } else {
            showToast(`Failed to ${ProcessItem ? "update" : "create"} process: ${res.error}`, "error");
        }
        return res;
    };

    return (
        <CustomModal
            modalTitle={ProcessItem ? "Edit Process" : "Create New Process"}
            SaveButtonName={ProcessItem ? "Update" : "Create"}
            handleSave={handleSave}
            handleClose={() => setShowNewProcessModal(false)}
            children={
                <div className="modal-inputs">
                    <CustomDropdown
                        label="Type"
                        options={availableTypes?.map((t: any) => ({ value: t.id, label: t.process_type_name })) || []}
                        defaultValue={currentProcess.type}
                        onChange={(value) => setCurrentProcess({ ...currentProcess, type: value })}
                    />
                    <input
                        type="text"
                        value={currentProcess?.title || ""}
                        onChange={(e) => setCurrentProcess({ ...currentProcess, title: e.target.value } as ProcessingItem)}
                        placeholder="Process Name"
                        className="modal-input"
                    />
                    <textarea
                        value={currentProcess?.description || ""}
                        onChange={(e) => setCurrentProcess({ ...currentProcess, description: e.target.value } as ProcessingItem)}
                        placeholder="Process Description"
                        className="modal-input"
                    />

                    <AttributeSettingsForm
                        curentProcess={currentProcess}
                        handleSaveNewProcess={handleSave}
                    />
                </div>
            }
        />
    );
}