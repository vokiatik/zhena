import { useProcessSettings } from "../../hooks/useProcessSettings";
import ProcessSettingsForm from "./ProcessSettingsForm";


export default function ProcessSettings() {
    const {
        process,
        isprocessPending,
        processError,
        CreateOrUpdateProcess,
        DeleteProcess
    } = useProcessSettings();

    if (isprocessPending) return <div>Loading...</div>;
    if (processError) return <div>Error loading processs: {processError.message}</div>;

    return (
        <div>
            <h1>Process Settings</h1>
            {process?.map(process => (
                <div key={process.id}>
                    <ProcessSettingsForm
                        process={process}
                        onSave={CreateOrUpdateProcess}
                        onDelete={DeleteProcess}
                    />
                </div>
            ))}
        </div>
    );
}