import { useState } from "react";
import type { PictureAttribute } from "../../types/picture_attributes";
import CustomModal from "../shared/modal/CustomModal";

interface PresetModalProps {
    fieldKey: string;
    settings: PictureAttribute[];
    onAdd: (key: string, value: string) => void;
    onClose: () => void;
}

export default function PresetModal({ fieldKey, settings, onAdd, onClose }: PresetModalProps) {
    const [value, setValue] = useState("");
    const referenceName = settings.find((s) => s.title === fieldKey)?.reference_type_name;

    return (
        <CustomModal
            modalTitle="Add new preset value"
            handleClose={onClose}
            handleSave={() => {
                onAdd(fieldKey, value);
                onClose();
            }}
        >
            <div className="preset-modal-content">
                <p>Presetting: <strong>{referenceName}</strong></p>
                <input
                    type="text"
                    className="pv-field-input"
                    placeholder="Enter new preset value"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                />
            </div>
        </CustomModal>
    );
}
