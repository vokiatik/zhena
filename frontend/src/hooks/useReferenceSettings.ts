import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { ProcessSettingsResult } from "../types/ProcessSettingsResult";


export function useReferenceSettings() {
    const { get, post, put, del } = useApi();

    const getReferenceTypes = useCallback(async () => {
        const response = await get<ProcessSettingsResult>(`/reference/types_list`);
        if (response.data.success) {
            return response.data.data;
        } else {
            throw new Error(response.data.error || "Failed to fetch reference types");
        };
    }, [get]);

    const getReferenceListByType = useCallback(async (typeId: string) => {
        const response = await get<ProcessSettingsResult>(`/reference/${typeId}`);
        if (response.data.success) {
            return response.data.data;
        } else {
            throw new Error(response.data.error || "Failed to fetch reference by type");
        };
    }, [get]);

    const deleteReferenceType = useCallback(
        async (typeId: string) => {
            try {
                const response = await del(`/reference/delete_type/${typeId}`);
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [del]
    );

    const createReferenceType = useCallback(
        async (referenceType: string) => {
            try {
                const response = await post<ProcessSettingsResult>(`/reference/create_type`, { reference_type: referenceType });
                return response.data;
            }
            catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [post]
    );

    const addValueToReference = useCallback(
        async (typeId: string, value: string) => {
            try {
                const response = await post<ProcessSettingsResult>(`/reference/add_value/${typeId}`, { value });
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [post]
    );

    const deleteReferenceValue = useCallback(
        async (valueId: string) => {
            try {
                const response = await del(`/reference/delete_value/${valueId}`);
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [del]
    );

    const updateReferenceValue = useCallback(
        async (valueId: string, newValue: string) => {
            try {
                const response = await put(`/reference/update_value/${valueId}`, { value: newValue });
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }   

        }, [put]
    );

    const { data: referenceTypes, isPending: isReferenceTypesPending, error: referenceTypesError } = useQuery({
        queryKey: ['reference_types'],
        queryFn: getReferenceTypes,
    })

    return { 
        referenceTypes,
        isReferenceTypesPending,
        referenceTypesError,

        getReferenceListByType,
        deleteReferenceType,
        createReferenceType,
        addValueToReference,
        deleteReferenceValue,
        updateReferenceValue
    };
}