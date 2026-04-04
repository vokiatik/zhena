import { useEffect, useState } from "react";

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

    useEffect(() => {
        setReferenceValue(initialValue);
    }, [initialValue]);

    const handleUpdate = () => {
        onUpdate(refId, referenceValue);
        setReferenceValue(referenceValue);
    }

    const handleDelete = () => {
        onDelete(refId);
    }

    return (
        <div key={refId} className="reference-list-input-item">
            <input className="reference-list-input" type="text" value={referenceValue} onChange={(e) => setReferenceValue(e.target.value)} />
            <button
                className="button-secondary"
                onClick={handleUpdate}
                disabled={referenceValue.trim() === "" || referenceValue === initialValue}
            >
                Update
            </button>
            <button className="button-danger" onClick={handleDelete}>Delete</button>
        </div>
    );
}