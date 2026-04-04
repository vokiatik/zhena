import { useState } from "react";
import "./ReferenceSettings.css";
import CustomDropdown from "../../../components/shared/dropdown/CustomDropdown";
import { useReferenceSettings } from "../../../hooks/useReferenceSettings";
import TvLoading from "../../../components/shared/loading/TvLoading";
import ReferenceList from "./ReferenceList";
import type { referenceValue } from "../../../types/reference_value";

export default function ReferenceSettings() {
    const [currentReferenceType, setCurrentReferenceType] = useState<{ id: string; name: string } | null>(null);

    const {
        referenceTypes,
        isReferenceTypesPending,
        referenceTypesError,
    } = useReferenceSettings();

    if (isReferenceTypesPending) {
        return <TvLoading />;
    };

    if (referenceTypesError) {
        return <p>Error loading reference types: {referenceTypesError.message}</p>;
    };

    return (
        <div className="reference-settings">
            <CustomDropdown
                label="Select Reference Type"
                options={referenceTypes}
                defaultValue={currentReferenceType?.id || ""}
                onChange={(value) => {
                    const selectedType = referenceTypes.find((ref: referenceValue) => ref.id === value);
                    setCurrentReferenceType(selectedType ? { id: selectedType.id, name: selectedType.reference_type_name } : null);
                }}
            />

            {currentReferenceType &&
                <ReferenceList
                    referenceTypeId={currentReferenceType.id}
                    referenceTypeName={currentReferenceType.name}
                />}
        </div>
    );
}