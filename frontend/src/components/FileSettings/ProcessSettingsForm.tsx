import type { ProcessingItem } from "../../types/processing";
import CustomSwitch from "../shared/switch/CustomSwitch";

interface ProcessSettingsFormProps {
    process: ProcessingItem;
    onSave: (process: ProcessingItem) => Promise<void>;
    onDelete: (processId: string) => Promise<void>;
}

export default function ProcessSettingsForm(
    { process, onSave, onDelete }: ProcessSettingsFormProps
) {

    const initialProcessState = {
        ...process,
        attributes: process.attributes.map(attr => ({
            ...attr,
            reference_table_name: attr.reference_table_name || "",
            reference_column_name: attr.reference_column_name || "",
        }))
    };

    const isEdited = JSON.stringify(process) !== JSON.stringify(initialProcessState);

    const handleSave = () => {
        onSave(process);
    };

    const handleDelete = () => {
        onDelete(process.id);
    };

    return (
        <div>
            <h2>{process.title}</h2>
            <textarea value={process.description} onChange={(e) => onSave({ ...process, description: e.target.value })} />
            {process.attributes.map((attr) => (
                <div key={attr.id}>
                    <h3>{attr.title}</h3>
                    <CustomSwitch
                        checked={attr.is_shown}
                        onChange={(checked) => onSave({
                            ...process,
                            attributes: process.attributes.map(a => a.id === attr.id ? { ...a, is_shown: checked } : a)
                        })}
                    />
                    <CustomSwitch
                        checked={attr.is_editable}
                        onChange={(checked) => onSave({
                            ...process,
                            attributes: process.attributes.map(a => a.id === attr.id ? { ...a, is_editable: checked } : a)
                        })}
                    />
                    <textarea value={attr.reference_table_name || ""} onChange={(e) => onSave({
                        ...process,
                        attributes: process.attributes.map(a => a.id === attr.id ? { ...a, reference_table_name: e.target.value } : a)
                    })} placeholder="Reference Table Name" />
                    <textarea value={attr.reference_column_name || ""} onChange={(e) => onSave({
                        ...process,
                        attributes: process.attributes.map(a => a.id === attr.id ? { ...a, reference_column_name: e.target.value } : a)
                    })} placeholder="Reference Column Name" />
                </div>
            ))}
            <button onClick={handleSave} disabled={!isEdited}>Edit</button>
            <button onClick={handleDelete}>Delete</button>
        </div>
    );
}