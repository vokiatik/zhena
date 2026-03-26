import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";

type ProcessSettingsResult = {
    success: boolean;
    data?: any;
    error?: string;
};

export function useProcessSettings() {
    const { get, post } = useApi();

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

    const CreateProcess = useCallback(
        async (processData: { title: string; description: string }) => {
            try{
            const response = await post<ProcessSettingsResult>(`/process/create`, processData);
            return response.data;
        } catch (error) {
            return { success: false, error: (error as Error).message };
        }
        },
        [post]
    );
    const UpdateProcess = useCallback(
        async (processId: string, processData: { title: string; description: string }) => {
            try {
                const response = await post<ProcessSettingsResult>(`/process/update/${processId}`, processData);
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [post]
    );

    const DeleteProcess = useCallback(
        async (processId: string) => {
            try {
                const response = await post<ProcessSettingsResult>(`/process/delete`, { id: processId });
                return response.data;
            } catch (error) {
                return { success: false, error: (error as Error).message };
            }
        },
        [post]
    );

    const { data: processList, isPending: isProcessListPending, error: ProcessListError, refetch: refetchProcessList } = useQuery({
        queryKey: ['process_list'],
        queryFn: getprocessList,
    })

    const { data: process, isPending: isprocessPending, error: processError } = useQuery({
        queryKey: ['process', processId],
        queryFn: () => getProcess(processId),
    })

  return { 
    processId,
    process,
    isprocessPending,
    processError,
    processList,
    isProcessListPending,
    ProcessListError,
    CreateProcess,
    UpdateProcess,
    DeleteProcess,
    setProcessId,
    refetchProcessList
};
}