import { useState } from "react";

interface ReferenceListInputProps {
    refId: string;
    initialValue: string;
    onUpdate: (refId: string, newValue: string) => void;
    onDelete: (refId: string) => void;
}

export default function ReferenceListInput({
    refId,
    initialValue,
    onUpdate,
    onDelete
}: ReferenceListInputProps) {

    const [referenceValue, setReferenceValue] = useState<string>(initialValue);

    const handleUpdate = () => {
        onUpdate(refId, referenceValue);
    }

    const handleDelete = () => {
        onDelete(refId);
    }

    return (
        <div key={refId} className="reference-list-input-item">
            <input type="text" value={referenceValue} onChange={(e) => setReferenceValue(e.target.value)} />
            <button className="button-secondary" onClick={handleUpdate}>Update</button>
            <button className="button-danger" onClick={handleDelete}>Delete</button>
        </div>
    );
}