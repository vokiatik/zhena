import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { ProcessingItem } from "../types/processing";

export function useProcessSettings() {
    const { get, post } = useApi();

    const getprocess = useCallback(
        async () => {
        const response = await get<ProcessingItem[]>(`/process/list`);
        return response.data;
    }, [get]);

    const CreateOrUpdateProcess = useCallback(
        async (processData: ProcessingItem) => {
            await post(`/process/create_update`, processData);
        },
        [post]
    );

    const DeleteProcess = useCallback(
        async (processId: string) => {
            await post(`/process/delete`, { id: processId });
        },
        [post]
    );

    const { data: process, isPending: isprocessPending, error: processError } = useQuery({
        queryKey: ['process_list'],
        queryFn: getprocess,
    })

  return { 
    process,
    isprocessPending,
    processError,
    CreateOrUpdateProcess,
    DeleteProcess,
};
}