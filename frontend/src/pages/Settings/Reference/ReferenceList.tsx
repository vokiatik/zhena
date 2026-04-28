import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import TvLoading from "../../../components/shared/loading/TvLoading";
import ReferenceListInput from "./ReferenceValueInput";
import { useReferenceSettings } from "../../../hooks/useReferenceSettings";

import type { referenceValue } from "../../../types/reference_value";
import { useToast } from "../../../contexts/ToastContext";

const ITEMS_PER_PAGE = 13;

interface ReferenceListProps {
    referenceTypeId: string;
    referenceTypeName: string;
}

export default function ReferenceList({
    referenceTypeId,
    referenceTypeName
}: ReferenceListProps) {
    const [currentPage, setCurrentPage] = useState(1);

    const {
        getReferenceListByType,
        updateReferenceValue,
        deleteReferenceValue,
    } = useReferenceSettings();

    const { showToast } = useToast();
    const {
        data: referenceList,
        isPending: isReferenceListPending,
        error: referenceListError,
        refetch: refetchReferenceList
    } = useQuery({
        queryKey: ['reference_list', referenceTypeId],
        queryFn: () => getReferenceListByType(referenceTypeId),
        enabled: !!referenceTypeId,
    })

    const sortedList = useMemo(() => {
        if (!referenceList) return [];
        return [...referenceList].sort((a: referenceValue, b: referenceValue) =>
            a.reference_value.localeCompare(b.reference_value)
        );
    }, [referenceList]);

    const totalPages = Math.max(1, Math.ceil(sortedList.length / ITEMS_PER_PAGE));
    const safePage = Math.min(currentPage, totalPages);
    const paginatedList = sortedList.slice(
        (safePage - 1) * ITEMS_PER_PAGE,
        safePage * ITEMS_PER_PAGE
    );

    return (
        <div className="reference-settings-container">
            <h2>Reference List for Type: {referenceTypeName}</h2>
            {isReferenceListPending && <TvLoading />}
            {referenceListError && <p>Error: {referenceListError.message}</p>}

            {referenceList && (
                <>
                    <div className="reference-list-inputs-container">
                        {paginatedList.map((ref: referenceValue) => (
                            <ReferenceListInput
                                key={ref.id}
                                refId={ref.id}
                                initialValue={ref.reference_value}
                                onUpdate={async (id, newValue) => {
                                    await updateReferenceValue(id, newValue);
                                    showToast("Reference value updated successfully", "success");
                                    refetchReferenceList();
                                }}
                                onDelete={async (id) => {
                                    await deleteReferenceValue(id);
                                    showToast("Reference value deleted successfully", "success");
                                    refetchReferenceList();
                                }}
                            />
                        ))}
                    </div>

                    {totalPages > 1 && (
                        <div className="pagination-controls">
                            <button
                                className="button-secondary"
                                onClick={() => setCurrentPage(1)}
                                disabled={safePage === 1}
                            >
                                &laquo;
                            </button>
                            <button
                                className="button-secondary"
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={safePage === 1}
                            >
                                &lsaquo;
                            </button>
                            <span className="pagination-info">
                                {safePage} / {totalPages}
                            </span>
                            <button
                                className="button-secondary"
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={safePage === totalPages}
                            >
                                &rsaquo;
                            </button>
                            <button
                                className="button-secondary"
                                onClick={() => setCurrentPage(totalPages)}
                                disabled={safePage === totalPages}
                            >
                                &raquo;
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
