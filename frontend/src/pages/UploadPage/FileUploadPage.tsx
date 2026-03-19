import React from "react";
import { FileUploadDropzone } from "../../components/Dropzone";
import "./FileUploadPage.css";

export default function FileUploadPage(): React.ReactElement {
  return (
    <div className="file-upload-page">
      <div className="file-upload-page__container">
        <h1 className="file-upload-page__title">Retail File Upload</h1>
        <p className="file-upload-page__description">
          Upload a CSV or Excel file and save it into PostgreSQL.
        </p>

        <FileUploadDropzone />
      </div>
    </div>
  );
};