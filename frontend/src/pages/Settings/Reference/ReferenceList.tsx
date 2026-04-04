import { useQuery } from "@tanstack/react-query";

import TvLoading from "../../../components/shared/loading/TvLoading";
import ReferenceListInput from "./ReferenceValueInput";
import { useReferenceSettings } from "../../../hooks/useReferenceSettings";

import type { referenceValue } from "../../../types/reference_value";

interface ReferenceListProps {
    referenceTypeId: string;
    referenceTypeName: string;
}

export default function ReferenceList({
    referenceTypeId,
    referenceTypeName
}: ReferenceListProps) {
    const {
        getReferenceListByType,
        updateReferenceValue,
        deleteReferenceValue,
    } = useReferenceSettings();
    const { data: referenceList, isPending: isReferenceListPending, error: referenceListError } = useQuery({
        queryKey: ['reference_list', referenceTypeId],
        queryFn: () => getReferenceListByType(referenceTypeId),
        enabled: !!referenceTypeId,
    })

    return (
        <div>
            <h2>Reference List for Type: {referenceTypeName}</h2>
            {isReferenceListPending && <TvLoading />}
            {referenceListError && <p>Error: {referenceListError.message}</p>}

            {referenceList && (
                <div className="reference-list-inputs-container">
                    {referenceList.map((ref: referenceValue) => (
                        <ReferenceListInput
                            key={ref.id}
                            refId={ref.id}
                            initialValue={ref.reference_value}
                            onUpdate={(id, newValue) => {
                                updateReferenceValue(id, newValue);
                            }}
                            onDelete={(id) => {
                                deleteReferenceValue(id);
                            }}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
