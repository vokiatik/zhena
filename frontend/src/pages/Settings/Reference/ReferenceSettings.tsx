import { useState } from "react";
import "./ReferenceSettings.css";
import CustomDropdown from "../../../components/shared/dropdown/CustomDropdown";
import { useReferenceSettings } from "../../../hooks/useReferenceSettings";
import TvLoading from "../../../components/shared/loading/TvLoading";
import ReferenceList from "./ReferenceList";
import type { referenceListType } from "../../../types/ref_list";

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
            <h1>Reference Settings</h1>
            <CustomDropdown
                label="Select Reference Type"
                options={Array.isArray(referenceTypes) ? referenceTypes.map((ref: referenceListType) => ({ value: ref.id, label: ref.reference_type_name })) : []}
                defaultValue={currentReferenceType?.id || ""}
                onChange={(value) => {
                    const selectedType = Array.isArray(referenceTypes) ? referenceTypes.find((ref: referenceListType) => ref.id === value) : null;
                    setCurrentReferenceType(selectedType ? { id: selectedType.id, name: selectedType.reference_type_name } : null);
                }}
                searchable
            />

            {currentReferenceType &&
                <ReferenceList
                    referenceTypeId={currentReferenceType.id}
                    referenceTypeName={currentReferenceType.name}
                />}
        </div>
    );
}