import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useUser } from "../../contexts";
import { useToast } from "../../contexts/ToastContext";
import type { ProcessInstance } from "../../types/process_instance";
import TvLoading from "../shared/loading/TvLoading";
import "./ProcessInstances.css";

const STATUS_OPTIONS = ["initiated", "in progress", "done"];

export default function ProcessInstancesList() {
    const { processInstances, isPending, error, updateProcessInstance } = useProcessInstances();
    const { hasAnyRole } = useUser();
    const { showToast } = useToast();
    const navigate = useNavigate();
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editStatus, setEditStatus] = useState("");

    if (isPending) return <TvLoading />;
    if (error) return <div className="pi-error">Error loading processes: {error.message}</div>;

    const canProceed = (process: ProcessInstance) => {
        if (hasAnyRole("admin")) return true;
        if (hasAnyRole("marketing_specialist") && (process.type_name === "file" || process.type_name === "link")) return true;
        if (hasAnyRole("analyst") && process.type_name === "analyst") return true;
        return false;
    };

    const canUpdate = hasAnyRole("admin");

    const handleProceed = (process: ProcessInstance) => {
        navigate(`/screening/process/${process.id}`);
    };

    const handleUpdate = async (processId: string) => {
        if (!editStatus) return;
        const res = await updateProcessInstance(processId, { status: editStatus });
        if (res.ok) {
            showToast("Process updated", "success");
            setEditingId(null);
        } else {
            showToast("Failed to update process", "error");
        }
    };

    const getStatusClass = (status: string) => {
        switch (status) {
            case "initiated": return "pi-status--initiated";
            case "in progress": return "pi-status--progress";
            case "done": return "pi-status--done";
            default: return "";
        }
    };

    return (
        <div className="pi-container">
            <h1 className="pi-title">Processes</h1>
            {hasAnyRole("admin", "marketing_specialist") && (
                <button
                    className="button-primary pi-create-btn"
                    onClick={() => navigate("/link-upload")}
                >
                    Create Link Process
                </button>
            )}
            <div className="pi-list">
                <div className="pi-header-row">
                    <span className="pi-col pi-col--type">Type</span>
                    <span className="pi-col pi-col--status">Status</span>
                    <span className="pi-col pi-col--comment">Comment</span>
                    <span className="pi-col pi-col--items">Items</span>
                    <span className="pi-col pi-col--date">Created</span>
                    <span className="pi-col pi-col--actions">Actions</span>
                </div>
                {processInstances?.map((process: ProcessInstance) => (
                    <div key={process.id} className="pi-row">
                        <span className="pi-col pi-col--type pi-type-badge">
                            {process.type_name}
                        </span>
                        <span className={`pi-col pi-col--status ${getStatusClass(process.status_name)}`}>
                            {editingId === process.id ? (
                                <select
                                    value={editStatus}
                                    onChange={(e) => setEditStatus(e.target.value)}
                                    className="pi-status-select"
                                >
                                    {STATUS_OPTIONS.map((s) => (
                                        <option key={s} value={s}>{s}</option>
                                    ))}
                                </select>
                            ) : (
                                process.status_name
                            )}
                        </span>
                        <span className="pi-col pi-col--comment" title={process.comment || ""}>
                            {process.comment || "—"}
                        </span>
                        <span className="pi-col pi-col--items">
                            {process.total_items ?? "—"}
                        </span>
                        <span className="pi-col pi-col--date">
                            {new Date(process.created_at).toLocaleDateString()}
                        </span>
                        <span className="pi-col pi-col--actions">
                            {canProceed(process) && process.status_name !== "done" && (
                                <button
                                    className="button-primary pi-action-btn"
                                    onClick={() => handleProceed(process)}
                                >
                                    Proceed
                                </button>
                            )}
                            {canUpdate && (
                                editingId === process.id ? (
                                    <>
                                        <button
                                            className="button-primary pi-action-btn"
                                            onClick={() => handleUpdate(process.id)}
                                        >
                                            Save
                                        </button>
                                        <button
                                            className="button-secondary pi-action-btn"
                                            onClick={() => setEditingId(null)}
                                        >
                                            Cancel
                                        </button>
                                    </>
                                ) : (
                                    <button
                                        className="button-secondary pi-action-btn"
                                        onClick={() => {
                                            setEditingId(process.id);
                                            setEditStatus(process.status_name);
                                        }}
                                    >
                                        Update
                                    </button>
                                )
                            )}
                        </span>
                    </div>
                ))}
                {(!processInstances || processInstances.length === 0) && (
                    <div className="pi-empty">No processes found.</div>
                )}
            </div>
        </div>
    );
}
