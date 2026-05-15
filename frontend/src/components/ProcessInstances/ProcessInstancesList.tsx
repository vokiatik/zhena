import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useUser } from "../../contexts";
import { useToast } from "../../contexts/ToastContext";
import type { ProcessInstance } from "../../types/process_instance";
import TvLoading from "../shared/loading/TvLoading";
import "./ProcessInstances.css";

export default function ProcessInstancesList() {
    const {
        processInstances,
        isPending,
        error,
        updateProcessInstance,
        deleteProcessInstance,
        createProcess,
        cancelProcess,
        statusOptions,
    } = useProcessInstances();
    const { hasAnyRole } = useUser();
    const { showToast } = useToast();
    const navigate = useNavigate();
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editStatus, setEditStatus] = useState("");
    const [creating, setCreating] = useState(false);

    if (isPending) return <TvLoading />;
    if (error) return <div className="pi-error">Error loading processes: {error.message}</div>;

    const dataPrep = processInstances?.filter((p) => p.type_name === "data_prep") ?? [];

    const canCreate = hasAnyRole("admin", "analyst");
    const canUpdate = hasAnyRole("admin");

    const actionForProcess = (process: ProcessInstance): "continue" | "view" | null => {
        const s = process.status_name;
        if (s === "canceled") return "view";
        if (s === "completed") return "view";
        if (s === "marketing_review") {
            return hasAnyRole("admin", "marketing_specialist") ? "continue" : "view";
        }
        if (hasAnyRole("admin", "analyst")) return "continue";
        return "view";
    };

    const handleCreate = async () => {
        setCreating(true);
        try {
            const result = await createProcess();
            if (result.ok) {
                navigate(`/data-prep/${result.process_id}`);
            } else {
                showToast("Failed to create process", "error");
            }
        } catch {
            showToast("Failed to create process", "error");
        } finally {
            setCreating(false);
        }
    };

    const handleCancel = async (processId: string) => {
        const result = await cancelProcess(processId);
        if (result.ok) {
            showToast("Process canceled", "success");
        } else {
            showToast("Failed to cancel process", "error");
        }
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

    const handleDelete = async (processId: string) => {
        const res = await deleteProcessInstance(processId);
        if (res.ok) {
            showToast("Process deleted", "success");
        } else {
            showToast("Failed to delete process", "error");
        }
    }
    const getStatusClass = (status: string) => {
        switch (status) {
            case "initiated": return "pi-status--initiated";
            case "awaiting_link": return "pi-status--awaiting";
            case "analyst_review": return "pi-status--review";
            case "marketing_review": return "pi-status--review";
            case "completed": return "pi-status--done";
            case "canceled": return "pi-status--canceled";
            default: return "";
        }
    };

    return (
        <div className="pi-container">
            <div className="pi-top-bar">
                <h1 className="pi-title">Data Preparation Processes</h1>
                {canCreate && (
                    <button
                        className="button-primary pi-create-btn"
                        onClick={handleCreate}
                        disabled={creating}
                    >
                        {creating ? "Creating…" : "+ New Process"}
                    </button>
                )}
            </div>

            <div className="pi-list">
                <div className="pi-header-row">
                    <span className="pi-col pi-col--id">ID</span>
                    <span className="pi-col pi-col--status">Status</span>
                    <span className="pi-col pi-col--comment">Comment</span>
                    <span className="pi-col pi-col--items">Items</span>
                    <span className="pi-col pi-col--date">Created</span>
                    <span className="pi-col pi-col--actions">Actions</span>
                </div>

                {dataPrep.map((process: ProcessInstance) => {
                    const action = actionForProcess(process);
                    return (
                        <div key={process.id} className="pi-row">
                            <span className="pi-col pi-col--id pi-id-text">
                                #{process.id.slice(0, 8)}
                            </span>
                            <span className={`pi-col pi-col--status${editingId === process.id ? "--edit" : ""} ${getStatusClass(process.status_name)}`}>
                                {editingId === process.id ? (
                                    <select
                                        value={editStatus}
                                        onChange={(e) => setEditStatus(e.target.value)}
                                        className="pi-status-select"
                                    >
                                        {statusOptions.map((s) => (
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
                                {action === "continue" && (
                                    <button
                                        className="button-primary pi-action-btn"
                                        onClick={() => navigate(`/data-prep/${process.id}`)}
                                    >
                                        Continue
                                    </button>
                                )}
                                {action === "view" && (
                                    <button
                                        className="button-secondary pi-action-btn"
                                        onClick={() => navigate(`/data-prep/${process.id}`)}
                                    >
                                        View
                                    </button>
                                )}
                                {process.status_name !== "canceled" &&
                                    process.status_name !== "completed" &&
                                    hasAnyRole("admin") && (
                                        <button
                                            className="button-danger pi-action-btn"
                                            onClick={() => handleCancel(process.id)}
                                        >
                                            Cancel
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
                                        hasAnyRole("admin") && (
                                            <button
                                                className="button-secondary pi-action-btn"
                                                onClick={() => {
                                                    setEditingId(process.id);
                                                    setEditStatus(process.status_name);
                                                }}
                                            >
                                                Edit
                                            </button>
                                        )
                                    )
                                )}
                                {process.status_name == "canceled" &&
                                    hasAnyRole("admin") && (
                                        <button
                                            className="button-danger pi-action-btn"
                                            onClick={() => handleDelete(process.id)}
                                        >
                                            Delete
                                        </button>
                                    )}

                            </span>
                        </div>
                    )

                })}

                {dataPrep.length === 0 && (
                    <div className="pi-empty">No data preparation processes found.</div>
                )}
            </div>
        </div>
    );
}

