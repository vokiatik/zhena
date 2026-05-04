import React, { useState } from "react";
import { FileUploadDropzone } from "../../components/Dropzone";
import "./FileUploadPage.css";
import { useParams } from "react-router";
import CustomDropdown from "../../components/shared/dropdown/CustomDropdown";

export default function FileUploadPage(): React.ReactElement {
    const { defaultfiletype } = useParams<{ defaultfiletype: string }>();
    const [filetype, setFiletype] = useState("");

    const dropdownOptions = [
        { value: "", label: "Select file type" },
        { value: "retail", label: "Retail Data" },
        { value: "reference", label: "Reference Data" },
        // Future options can be added here
    ];
    return (
        <div className="file-upload-page">
            <div className="file-upload-page__container">
                <h1 className="file-upload-page__title">File Upload</h1>
                <p className="file-upload-page__description">
                    Upload a CSV or Excel file and save it into PostgreSQL.
                </p>

                {!defaultfiletype &&
                    <CustomDropdown
                        label="File Type"
                        options={dropdownOptions}
                        defaultValue={filetype}
                        onChange={(value) => setFiletype(value)}
                    />}
                {(filetype || defaultfiletype) &&
                    <FileUploadDropzone filetype={filetype || defaultfiletype} />}
            </div>
        </div>
    );
};