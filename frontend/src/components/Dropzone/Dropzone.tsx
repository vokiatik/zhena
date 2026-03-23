import React, { useRef, useState } from "react";
import { apiClient } from "../../api";
import "./Dropzone.css";

type UploadState = "idle" | "uploading" | "success" | "error";

const allowedExtensions = [".csv", ".xlsx", ".xls"];

function isAllowedFile(file: File) {
    const lower = file.name.toLowerCase();
    return allowedExtensions.some((ext) => lower.endsWith(ext));
}

export default function FileUploadDropzone({ filetype }: { filetype?: string }): React.ReactElement {
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
            setMessage("Uploading file...");
            const filedata = new FormData();
            filedata.append("file", file);
            filetype && filedata.append("filetype", filetype);

            const result = await apiClient.post("/upload/retail-file", filedata, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            console.log(result);
            if (result?.data?.ok) {
                setUploadState("success");
                setMessage(
                    result?.data?.message ||
                    `Upload completed successfully. Inserted ${result?.data?.inserted_rows ?? 0} rows.`
                );
            } else {
                setUploadState("error");
                setMessage(result?.data?.message || "Upload failed.");
            }
        } catch (error: any) {
            const backendMessage =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                error?.message ||
                "Upload failed.";

            setUploadState("error");
            setMessage(backendMessage);
        }
    };

    const onInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        await handleFile(file);
        e.target.value = "";
    };

    const onDrop = async (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setDragOver(false);

        if (uploadState === "uploading") return;

        const file = e.dataTransfer.files?.[0];
        if (!file) return;

        await handleFile(file);
    };

    const openFileDialog = () => {
        if (uploadState === "uploading") return;
        inputRef.current?.click();
    };

    const dropzoneClassName = [
        "file-upload-dropzone__inner",
        dragOver ? "file-upload-dropzone--dragover" : "",
        uploadState === "uploading" ? "file-upload-dropzone--disabled" : "",
    ]
        .filter(Boolean)
        .join(" ");

    const messageClassName = [
        "file-upload-message",
        uploadState === "success" ? "file-upload-message--success" : "",
        uploadState === "error" ? "file-upload-message--error" : "",
        uploadState === "idle" || uploadState === "uploading"
            ? "file-upload-message--neutral"
            : "",
    ]
        .filter(Boolean)
        .join(" ");

    // <div className="file-upload">
    //   <input
    //     ref={inputRef}
    //     type="file"
    //     accept=".csv,.xlsx,.xls"
    //     className="file-upload__input"
    //     onChange={onInputChange}
    //   />

    //   <div
    //     className={dropzoneClassName}
    //     onClick={openFileDialog}
    //     onDragOver={(e) => {
    //       e.preventDefault();
    //       if (uploadState !== "uploading") {
    //         setDragOver(true);
    //       }
    //     }}
    //     onDragLeave={() => setDragOver(false)}
    //     onDrop={onDrop}
    //   >
    //     <h3 className="file-upload-dropzone__title">Upload CSV or Excel file</h3>
    //     <p className="file-upload-dropzone__text">
    //       Drag and drop 1 file here, or click to select.
    //     </p>
    //     <p className="file-upload-dropzone__hint">
    //       Allowed formats: .csv, .xlsx, .xls
    //     </p>

    //     {uploadState === "uploading" && (
    //       <p className="file-upload-dropzone__status">Processing...</p>
    //     )}
    //   </div>

    //   {message && <div className={messageClassName}>{message}</div>}
    // </div>
    return (
        <div className="file-upload-dropzone">
            <input
                ref={inputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                className="file-upload-dropzone__hidden-input"
                onChange={onInputChange}
            />
            <div
                className={dropzoneClassName}
                onClick={openFileDialog}
                onDragOver={(e) => {
                    e.preventDefault();
                    if (uploadState !== "uploading") {
                        setDragOver(true);
                    }
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
            >
                <div className="file-upload-dropzone__icon">↑</div>

                <h3 className="file-upload-dropzone__title">Upload file</h3>
                <p className="file-upload-dropzone__subtitle">
                    Drag and drop your CSV or Excel file here, or <span className="file-upload-dropzone__browse">browse</span>
                </p>
                <span className="file-upload-dropzone__formats">CSV, XLS, XLSX</span>

                {uploadState === "uploading" && (
                    <p className="file-upload-dropzone__status">Processing...</p>
                )}
            </div>

            {message && <div className={messageClassName}>{message}</div>}
        </div>
    );
};