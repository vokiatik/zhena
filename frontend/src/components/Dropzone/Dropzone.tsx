import React, { useRef, useState } from "react";
import { apiClient } from "../../api";
import "./Dropzone.css";

type UploadState = "idle" | "uploading" | "success" | "error";

const allowedExtensions = [".csv", ".xlsx", ".xls"];

function isAllowedFile(file: File) {
  const lower = file.name.toLowerCase();
  return allowedExtensions.some((ext) => lower.endsWith(ext));
}

export default function FileUploadDropzone() {
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
        const result = await apiClient.post("/upload/incoming", file, {
          headers: {
            "Content-Type": file.type,
          },
        });

      setUploadState("success");
      setMessage(
        result?.data ||
          `Upload completed successfully. Inserted ${result?.data?.inserted_rows ?? 0} rows.`
      );
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
    "file-upload-dropzone",
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

  
    return (
    <div className="file-upload">
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        className="file-upload__input"
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
        <h3 className="file-upload-dropzone__title">Upload CSV or Excel file</h3>
        <p className="file-upload-dropzone__text">
          Drag and drop 1 file here, or click to select.
        </p>
        <p className="file-upload-dropzone__hint">
          Allowed formats: .csv, .xlsx, .xls
        </p>

        {uploadState === "uploading" && (
          <p className="file-upload-dropzone__status">Processing...</p>
        )}
      </div>

      {message && <div className={messageClassName}>{message}</div>}
    </div>
  );
};