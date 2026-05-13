import { useRef, useState } from "react";
import { apiClient } from "../../api";
import CustomModal from "../shared/modal/CustomModal";
import "../../assets/styles/Dropzone.css";

type UploadState = "idle" | "uploading" | "success" | "error";

const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"];

function isAllowedFile(file: File): boolean {
    const lower = file.name.toLowerCase();
    return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

interface Props {
    displayName: string;
    uploadPrefix: string;
    onClose: () => void;
}

export default function TableUploadModal({ displayName, uploadPrefix, onClose }: Props) {
    const inputRef = useRef<HTMLInputElement | null>(null);
    const [dragOver, setDragOver] = useState(false);
    const [uploadState, setUploadState] = useState<UploadState>("idle");
    const [message, setMessage] = useState<string>("");

    const handleFile = async (file: File) => {
        if (!isAllowedFile(file)) {
            setUploadState("error");
            setMessage("Only CSV, XLSX or XLS files are allowed.");
            return;
        }

        try {
            setUploadState("uploading");
            setMessage("Uploading file…");

            const formData = new FormData();
            formData.append("file", file);

            const result = await apiClient.post(
                `/upload/${uploadPrefix}`,
                formData,
                { headers: { "Content-Type": "multipart/form-data" } }
            );

            console.log("Upload result:", result);
            if (result?.data?.ok) {
                setUploadState("success");
                setMessage(`Upload completed. Inserted ${result.data.inserted_rows ?? 0} rows.`);
            } else {
                setUploadState("error");
                setMessage(result?.data?.detail || "Upload failed.");
            }
        } catch (error: any) {
            const msg =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                error?.message ||
                "Upload failed.";
            setUploadState("error");
            setMessage(msg);
        }
    };

    const onDrop = async (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setDragOver(false);
        if (uploadState === "uploading") return;
        const file = e.dataTransfer.files?.[0];
        if (file) await handleFile(file);
    };

    const onInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        await handleFile(file);
        e.target.value = "";
    };

    const dropzoneClass = [
        "file-upload-dropzone__inner",
        dragOver ? "file-upload-dropzone--dragover" : "",
        uploadState === "uploading" ? "file-upload-dropzone--disabled" : "",
    ]
        .filter(Boolean)
        .join(" ");

    const messageClass = [
        "file-upload-message",
        uploadState === "success" ? "file-upload-message--success" : "",
        uploadState === "error" ? "file-upload-message--error" : "",
        uploadState === "idle" || uploadState === "uploading" ? "file-upload-message--neutral" : "",
    ]
        .filter(Boolean)
        .join(" ");

    return (
        <CustomModal
            modalTitle={`Upload to "${displayName}"`}
            SaveButtonName="Close"
            handleSave={onClose}
            handleClose={onClose}
        >
            {uploadPrefix && (
                <p style={{ fontSize: "0.85rem", color: "#9ca3af", marginBottom: 12 }}>
                    Required file name prefix: <code style={{ color: "#3b82f6" }}>{uploadPrefix}</code>
                </p>
            )}
            <div className="file-upload-dropzone" style={{ margin: 0 }}>
                <input
                    ref={inputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    className="file-upload-dropzone__hidden-input"
                    onChange={onInputChange}
                />
                <div
                    className={dropzoneClass}
                    onClick={() => uploadState !== "uploading" && inputRef.current?.click()}
                    onDragOver={(e) => {
                        e.preventDefault();
                        if (uploadState !== "uploading") setDragOver(true);
                    }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={onDrop}
                >
                    <div className="file-upload-dropzone__icon">↑</div>
                    <h3 className="file-upload-dropzone__title">Upload file</h3>
                    <p className="file-upload-dropzone__subtitle">
                        Drag and drop your CSV or Excel file here, or{" "}
                        <span className="file-upload-dropzone__browse">browse</span>
                    </p>
                    <span className="file-upload-dropzone__formats">CSV, XLS, XLSX</span>
                    {uploadState === "uploading" && (
                        <p className="file-upload-dropzone__status">Processing…</p>
                    )}
                </div>
                {message && <div className={messageClass}>{message}</div>}
            </div>
        </CustomModal>
    );
}
