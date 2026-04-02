import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { ProcessingItem } from "../types/processing";
import type { ProcessSettingsResult } from "../types/ProcessSettingsResult";


export function useProcessSettings() {
    const { get, post, put, del } = useApi();

    const [processId, setProcessId] = useState<string>("");

    const getprocessList = useCallback(
        async () => {
        const response = await get<ProcessSettingsResult>(`/process/list`);
        if (response.data.success) {
            return response.data.data;
        } else {
            throw new Error(response.data.error || "Failed to fetch process list");
        };
    }, [get]);

    const getProcess = useCallback(
        async (processId: string) => {
            if (!processId) {
                return null;
            }
            const response = await get<ProcessSettingsResult>(`/process/${processId}`);
            if (response.data.success) {
                return response.data.data;
            } else {
                throw new Error(response.data.error || "Failed to fetch process");
            };
    }, [get]);

    const getAvailableTables = useCallback(
        async () => {
            const response = await get<string[]>(`/process/tables`);
            return response.data;
        }, [get]);

    const CreateProcess = useCallback(
        async (processData: ProcessingItem) => {
            try{
            const response = await post<ProcessSettingsResult>(`/process/create`, processData);
            refetchProcessList();
            return response.data;
        } catch (error) {
            return { success: false, error: (error as Error).message };
        }
        },
        [post]
    );
    const UpdateProcess = useCallback(
        async (processData: ProcessingItem) => {
            try {
                const response = await put<ProcessSettingsResult>(`/process/update/${processData.id}`, processData);
                refetchProcessList();
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [put]
    );

    const DeleteProcess = useCallback(
        async (processId: string) => {
            try {
                const response = await del<ProcessSettingsResult>(`/process/delete/${processId}`);
                refetchProcessList();
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [del]
    );

    const { data: processList, isPending: isProcessListPending, error: ProcessListError, refetch: refetchProcessList } = useQuery({
        queryKey: ['process_list'],
        queryFn: getprocessList,
    })

    const { data: process, isPending: isprocessPending, error: processError } = useQuery({
        queryKey: ['process', processId],
        queryFn: () => getProcess(processId),
    })

    const { data: availableTables } = useQuery({
        queryKey: ['available_tables'],
        queryFn: getAvailableTables,
    })

  return { 
    processId,
    process,
    isprocessPending,
    processError,
    processList,
    isProcessListPending,
    ProcessListError,
    availableTables,
    CreateProcess,
    UpdateProcess,
    DeleteProcess,
    setProcessId,
    refetchProcessList
};
}