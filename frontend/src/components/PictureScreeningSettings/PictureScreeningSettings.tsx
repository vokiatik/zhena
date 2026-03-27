import { useProcessSettings } from "../../hooks/useProcessSettings";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./PictureScreeningSettings.css";
import TvLoading from "../shared/loading/TvLoading";
import type { ProcessingItem } from "../../types/processing";
import { useToast } from "../../contexts/ToastContext";

export default function PictureScreeningProcessList() {
    const {
        processList,
        isProcessListPending,
        ProcessListError,
        CreateProcess,
        DeleteProcess,
        refetchProcessList
    } = useProcessSettings();

    const {
        showToast
    } = useToast();

    const [showNewProcessModal, setShowNewProcessModal] = useState(false);

    const navigate = useNavigate();

    if (isProcessListPending) return <TvLoading />;
    if (ProcessListError) return <div>Error loading processs: {ProcessListError.message}</div>;

    const NewProcessModal = () => {
        const [name, setName] = useState("");
        const [description, setDescription] = useState("");

        const handleSave = async () => {
            const res = await CreateProcess({ title: name, description: description });
            if (res.success) {
                showToast(`Process created successfully: ${res.data.id}`, "success");
                refetchProcessList();
                setShowNewProcessModal(false);
            } else {
                showToast(`Failed to create process: ${res.error}`, "error");
            }

        };

        return (
            <div className="modal-overlay">
                <div className="modal">
                    <div className="modal-header">
                        <h2 className="modal-title">Create New Process</h2>
                        <button className="modal-close" onClick={() => setShowNewProcessModal(false)}>X</button>
                    </div>

                    <div className="modal-body">
                        <div className="modal-inputs">
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Process Name"
                            />
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="Process Description"
                            />
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button onClick={handleSave}>Create</button>
                        <button onClick={() => setShowNewProcessModal(false)}>Cancel</button>
                    </div>
                </div>
            </div>
        );
    }

    const handleDeleteProcess = async (processId: string) => {
        const res = await DeleteProcess(processId);
        if (res.success) {
            showToast(`Process deleted successfully`, "success");
        } else {
            showToast(`Failed to delete process: ${res.error}`, "error");
        }
    };
    return (
        <div className="picture-screening-process-list">
            <h1 className="picture-screening-process-list__title">Picture Screening Process List</h1>
            {processList?.map((process: ProcessingItem) => (
                <div key={process.id} className="picture-screening-process-list__item-container">
                    <div
                        className="picture-screening-process-list__item"
                        onMouseDown={() => navigate(`/process/${process.id}`)}
                    >
                        <span
                            className="picture-screening-process-list__item-title"
                        >
                            {process.title}
                        </span>
                    </div>
                    <button
                        onClick={() => handleDeleteProcess(process.id)}
                        className="picture-screening-process-list__delete-btn"
                    >
                        Delete Process
                    </button>
                </div>
            ))}
            <button
                onClick={() => setShowNewProcessModal(true)}
                className="picture-screening-process-list__add-btn"
            >
                Add New Process
            </button>
            {showNewProcessModal && <NewProcessModal />}
        </div>
    );
}