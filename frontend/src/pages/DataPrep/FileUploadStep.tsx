import React, { useRef, useState } from "react";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";
import NewDictValuesModal from "../../components/Dropzone/NewDictValuesModal";
import type { ConfirmDecision, ValidationRequiredResponse } from "../../types/file_upload_validation";

const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"];

interface FileUploadStepProps {
    processId: string;
    onDone: () => void;
}

export default function FileUploadStep({ processId, onDone }: FileUploadStepProps) {
    const { uploadFile, confirmDict } = useProcessInstances();
    const { showToast } = useToast();
    const inputRef = useRef<HTMLInputElement>(null);
    const pendingFileRef = useRef<File | null>(null);

    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [isError, setIsError] = useState(false);
    const [validation, setValidation] = useState<ValidationRequiredResponse | null>(null);

    const handleFile = async (file: File) => {
        const lower = file.name.toLowerCase();
        if (!ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext))) {
            setMessage("Only CSV, XLSX or XLS files are allowed.");
            setIsError(true);
            return;
        }

        setUploading(true);
        setMessage("Uploading…");
        setIsError(false);

        try {
            const result = await uploadFile(processId, file);
            if (result.status === "needs_validation") {
                pendingFileRef.current = file;
                setValidation(result as ValidationRequiredResponse);
                setMessage(null);
                return;
            }
            if ("ok" in result && result.ok) {
                showToast("File uploaded successfully", "success");
                onDone();
            } else {
                setMessage("Upload failed.");
                setIsError(true);
            }
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || err?.message || "Upload failed.");
            setIsError(true);
        } finally {
            setUploading(false);
        }
    };

    const handleConfirmDict = async (decisions: ConfirmDecision[]) => {
        const file = pendingFileRef.current;
        if (!file) return;
        setValidation(null);
        setUploading(true);
        setMessage("Saving…");
        setIsError(false);
        try {
            const result = await confirmDict(processId, file, decisions);
            if (result.ok) {
                showToast("File saved with dictionary updates", "success");
                onDone();
            } else {
                setMessage("Failed to save with decisions.");
                setIsError(true);
            }
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || err?.message || "Failed to save.");
            setIsError(true);
        } finally {
            setUploading(false);
        }
    };

    const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setDragOver(false);
        if (uploading) return;
        const file = e.dataTransfer.files?.[0];
        if (file) handleFile(file);
    };

    const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
        e.target.value = "";
    };

    console.log("Render FileUploadStep", { dragOver, uploading, message, validation });
    return (
        <>
            <div className="dp-step-body">
                <p className="dp-step-desc">
                    Upload the retail data CSV or Excel file. The file will be validated
                    automatically — if any reference values are missing, you will be asked to
                    resolve them before proceeding.
                </p>

                <div
                    className={[
                        "dp-dropzone",
                        dragOver ? "dp-dropzone--over" : "",
                        uploading ? "dp-dropzone--disabled" : "",
                    ].filter(Boolean).join(" ")}
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={onDrop}
                    onClick={() => !uploading && inputRef.current?.click()}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        accept=".csv,.xlsx,.xls"
                        hidden
                        onChange={onInputChange}
                    />
                    <div className="dp-dropzone-icon">📂</div>
                    <p className="dp-dropzone-text">
                        {uploading
                            ? message ?? "Uploading…"
                            : "Drop a CSV / XLSX file here, or click to browse"}
                    </p>
                    <p className="dp-dropzone-hint">Supported: .csv · .xlsx · .xls</p>
                </div>

                {message && !uploading && (
                    <p className={`dp-msg ${isError ? "dp-msg--error" : "dp-msg--ok"}`}>
                        {message}
                    </p>
                )}
            </div>

            {validation && (
                <NewDictValuesModal
                    validationData={validation}
                    onConfirm={handleConfirmDict}
                />
            )}
        </>
    );
}
