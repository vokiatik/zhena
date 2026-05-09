import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { PictureAttribute } from "../types/picture_attributes";

export function useAttributesSettings(tableName?: string, processId?: string) {
    const { get, post, put, del } = useApi();

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

    return {
        tableColumns,
        isTableColumnsPending,
        tableColumnsError,
        processAttributes,
        isProcessAttributesPending,
        AddNewProcessAttribute,
        UpdateProcessAttribute,
        DeleteProcessAttribute,
    };
}