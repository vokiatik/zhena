import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api";
import type { ProcessInstance } from "../types/process_instance";

export function useProcessInstances() {
    const { get, post, put } = useApi();

    const fetchProcessInstances = useCallback(async () => {
        const response = await get<ProcessInstance[]>("/process-instances/list");
        return response.data;
    }, [get]);

    const createLinkProcess = useCallback(
        async (link: string) => {
            const response = await post<{ ok: boolean; process_id: string }>(
                "/process-instances/create-link",
                { link }
            );
            refetch();
            return response.data;
        },
        [post]
    );

    const updateProcessInstance = useCallback(
        async (processId: string, data: { status?: string; comment?: string }) => {
            const response = await put<{ ok: boolean }>(
                `/process-instances/update/${processId}`,
                data
            );
            refetch();
            return response.data;
        },
        [put]
    );

    const fetchProcessStatuses = useCallback(async () => {
        const response = await get<string[]>("/process-instances/statuses");
        return response.data;
    }, [get]);

    const {
        data: processInstances,
        isPending,
        error,
        refetch,
    } = useQuery({
        queryKey: ["process_instances"],
        queryFn: fetchProcessInstances,
    });

    const { data: statusOptions } = useQuery({
        queryKey: ["process_statuses"],
        queryFn: fetchProcessStatuses,
    });

    return {
        processInstances,
        isPending,
        error,
        statusOptions: statusOptions ?? [],
        createLinkProcess,
        updateProcessInstance,
        refetch,
    };
}
