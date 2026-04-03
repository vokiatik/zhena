import "./ProcessSettings.css";
import { useState } from "react";

import { useToast } from "../../contexts/ToastContext";
import { useProcessSettings } from "../../hooks/useProcessSettings";
import type { ProcessingItem } from "../../types/processing";

import TvLoading from "../shared/loading/TvLoading";

import ProcessSettingsForm from "./ProcessSettingsForm";

export default function ProcessSettingsList() {
    const {
        processList,
        isProcessListPending,
        ProcessListError,
        CreateProcess,
        DeleteProcess
    } = useProcessSettings();

    const {
        showToast
    } = useToast();

    const [currentProcess, setCurrentProcess] = useState<ProcessingItem | null>(null);
    const [showNewProcessModal, setShowNewProcessModal] = useState(false);

    if (isProcessListPending) return <TvLoading />;
    if (ProcessListError) return <div>Error loading processs: {ProcessListError.message}</div>;

    const handleDeleteProcess = async (processId: string) => {
        const res = await DeleteProcess(processId);
        if (res.success) {
            showToast(`Process deleted successfully`, "success");
        } else {
            showToast(`Failed to delete process: ${res.error}`, "error");
        }
    };
    return (
        <div className="process-settings-list">
            <h1 className="process-settings-list__title">Process Settings List</h1>
            {processList?.map((process: ProcessingItem) => (
                <div key={process.id} className="process-settings-list__item-container">
                    <div
                        className="process-settings-list__item"
                    >
                        <span
                            className="process-settings-list__item-title"
                        >
                            {process.title}
                        </span>
                        <span className="process-settings-list__item-description">
                            {process.description}
                        </span>
                    </div>
                    <div className="process-settings-list__item-actions">
                        <button
                            onClick={() => {
                                setCurrentProcess(process);
                                setShowNewProcessModal(true);
                            }}
                            className="button-primary"
                            style={{ marginInlineStart: "8px" }}
                        >
                            Edit Process
                        </button>
                        <button
                            onClick={() => handleDeleteProcess(process.id)}
                            className="button-danger"
                            style={{ marginInline: "8px" }}
                        >
                            Delete Process
                        </button>
                    </div>
                </div>
            ))}
            <button
                onClick={() => {
                    setCurrentProcess(null);
                    setShowNewProcessModal(true);
                }}
                className="button-secondary"
            >
                Add New Process
            </button>
            {showNewProcessModal &&
                <ProcessSettingsForm
                    ProcessItem={currentProcess}
                    setShowNewProcessModal={setShowNewProcessModal}
                    CreateProcess={CreateProcess}
                />}
        </div>
    );
}