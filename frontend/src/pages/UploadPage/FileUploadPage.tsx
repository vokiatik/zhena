import React, { useState } from "react";
import { FileUploadDropzone } from "../../components/Dropzone";
import "./FileUploadPage.css";
import { useParams } from "react-router";

export default function FileUploadPage(): React.ReactElement {
    const { defaultfiletype } = useParams<{ defaultfiletype: string }>();
    const [filetype, setFiletype] = useState("");

    const dropdownOptions = [
        { value: "", label: "Select file type" },
        { value: "retail", label: "Retail Data" },
        { value: "reference", label: "Reference Data" },
        // Future options can be added here
    ];

    const handleDropdownChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setFiletype(e.target.value);
    }

    const renderDropdown = () => (
        <div className="file-upload-dropdown">
            <label htmlFor="filetype" className="file-upload-dropdown__label">File Type:</label>
            <select
                id="filetype"
                value={filetype}
                onChange={handleDropdownChange}
                className="file-upload-dropdown__select"
            >
                {dropdownOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );

    return (
        <div className="file-upload-page">
            <div className="file-upload-page__container">
                <h1 className="file-upload-page__title">File Upload</h1>
                <p className="file-upload-page__description">
                    Upload a CSV or Excel file and save it into PostgreSQL.
                </p>

                {!defaultfiletype && renderDropdown()}
                {(filetype || defaultfiletype) &&
                    <FileUploadDropzone filetype={filetype || defaultfiletype} />}
            </div>
        </div>
    );
};