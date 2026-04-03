import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { PictureAttribute } from "../types/picture_attributes";
import { useToast } from "../contexts/ToastContext";
import type { referenceListType } from "../types/ref_list";

type AttributeSettingsResult = {
    success: boolean;
    data?: any;
    error?: string;
};

export function useAttributesSettings(tableName?: string, processId?: string) {
    const { get, post, put, del } = useApi();
    const { showToast } = useToast();

    const getTableColumns = useCallback(
        async () => {
            if (!tableName) return [];
            const response = await get<string[]>(`/process/attributes/list?type_id=${tableName}`);
            return response.data;
        }, [get, tableName]);

    const getProcessAttributes = useCallback(
        async () => {
            if (!processId) return [];
            const response = await get<PictureAttribute[]>(`/process/attributes/${processId}`);
            return response.data;
        }, [get, processId]);

    const getProcessAttributesReferenceList = useCallback(
        async () => {
            const response = await get<referenceListType[]>(`/process/attributes/reference/types_list`);
            return response.data;
        }, [get]);

    const AddNewProcessAttribute = useCallback(
        async (attribute: PictureAttribute) => {
            await post(`/process/attributes/create`, attribute);
            refetchProcessAttributes();
        },
        [post]
    );

    const UpdateProcessAttribute = useCallback(
        async (attribute: PictureAttribute) => {
            await put(`/process/attributes/update/${attribute.process_id}`, attribute);
            refetchProcessAttributes();
        },
        [put]
    );

    const DeleteProcessAttribute = useCallback(
        async (processId: string, attributeId: string) => {
            await del(`/process/attributes/delete/${processId}/${attributeId}`);
            refetchProcessAttributes();
        },
        [del]
    );

    const CreateNewAttributeReferenceType = useCallback(
        async (referenceType: string) => {
            const res = await post<AttributeSettingsResult>(`/process/attributes/reference/create_type?reference_type=${referenceType}`);
            if (res.data.success) {
                refetchReferenceList();
            } else {
                showToast(`Failed to create new reference type: ${res.data.error}`);
            }
        },
        [post]
    );

    const { data: tableColumns, isPending: isTableColumnsPending, error: tableColumnsError } = useQuery({
        queryKey: ['table_columns', tableName],
        queryFn: getTableColumns,
        enabled: !!tableName,
    })

    const { data: processAttributes, isPending: isProcessAttributesPending, refetch: refetchProcessAttributes } = useQuery({
        queryKey: ['process_attributes', processId],
        queryFn: getProcessAttributes,
        enabled: !!processId,
    })

    const { data: referenceList, isPending: isReferenceListPending, error: referenceListError, refetch: refetchReferenceList } = useQuery({
        queryKey: ['reference_list'],
        queryFn: getProcessAttributesReferenceList,
    })

    return {
        tableColumns,
        isTableColumnsPending,
        tableColumnsError,
        processAttributes,
        isProcessAttributesPending,
        referenceList,
        isReferenceListPending,
        referenceListError,
        AddNewProcessAttribute,
        UpdateProcessAttribute,
        DeleteProcessAttribute,
        CreateNewAttributeReferenceType
    };
}